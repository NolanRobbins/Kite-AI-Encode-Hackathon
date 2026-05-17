"""FastAPI application factory for the Surprise API seller.

Endpoints:

* ``GET /healthz`` — unauthenticated liveness probe (Railway/Vercel health check).
* ``GET /.well-known/agent.json`` — ERC-8004 / A2A agent card so buyers
  can fetch identity metadata without paying.
* ``GET /api/weather?city=...`` — x402-gated weather endpoint. Falls
  back to deterministic demo data if open-meteo is unreachable.
* ``GET /api/nvda`` — x402-gated NVDA quote endpoint. Deterministic
  demo payload (no external key).
* ``GET /api/receipts`` — unauthenticated read-only view of recent
  accepted payments (for the dashboard "payment log" widget).

The app is deliberately self-contained: starting it also registers a
matching :class:`ServiceRecord` in the shared in-process registry so
``DiscoveryService`` surfaces it to the buyer agent as a real,
MCP-discoverable capability.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from negotiatorgrid.discovery.local_registry import LocalRegistry, ServiceRecord
from surprise_api.x402_middleware import (
    NonceCache,
    PricingStore,
    X402MiddlewareConfig,
    X402PaymentMiddleware,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Canonical service record — the buyer resolves to this via MCP
# ---------------------------------------------------------------------------


SURPRISE_API_SERVICE_RECORD = ServiceRecord(
    service_id="agent_SurpriseAPI_Day4",
    name="Surprise API",
    description=(
        "Independent x402-gated seller introduced on Day 4 of the hackathon. "
        "Serves live weather and NVDA data at negotiable prices."
    ),
    capability="surprise-data",
    seller_address="0xa7C52Bd9E51E6c49aB2F0aB30c57Bb24aB1B91B7",
    seller_agent_id=7,
    reservation_price=15_000.0,  # 0.015 USDT floor
    list_price=40_000.0,  # 0.040 USDT opening ask
    resource_url="/api/weather",
    endpoints=["/api/weather", "/api/nvda"],
    input_fields={"city": "string", "symbol": "string"},
    response_fields={"temp_c": "number", "price_usd": "number"},
    tags=["weather-api", "market-data", "surprise-api", "day-4"],
    reputation=0.82,
)


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------


@dataclass
class SurpriseAPISettings:
    seller_wallet: str = SURPRISE_API_SERVICE_RECORD.seller_address
    network: str = "eip155:2368"
    asset: str = "0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63"
    facilitator_url: str = ""
    default_weather_price_atomic: int = 25_000  # 0.025 USDT
    default_nvda_price_atomic: int = 30_000  # 0.030 USDT
    cors_origins: tuple[str, ...] = ("*",)
    open_meteo_base: str = "https://api.open-meteo.com/v1/forecast"

    @classmethod
    def from_env(cls) -> "SurpriseAPISettings":
        return cls(
            seller_wallet=os.getenv(
                "SURPRISE_API_SELLER_WALLET", cls.seller_wallet
            ),
            network=os.getenv("KITE_NETWORK", cls.network),
            asset=os.getenv("TEST_USDT_ADDRESS", cls.asset),
            facilitator_url=os.getenv("X402_FACILITATOR_URL", ""),
            cors_origins=tuple(
                (os.getenv("CORS_ORIGINS") or "*").split(",")
            ),
        )


# ---------------------------------------------------------------------------
# Fallback data (offline-safe)
# ---------------------------------------------------------------------------


_FALLBACK_WEATHER = {
    "source": "surprise-api-fallback",
    "city": "New York",
    "temp_c": 22.0,
    "temp_f": 71.6,
    "conditions": "Partly cloudy",
    "humidity_pct": 58,
    "wind_kmh": 12.4,
}

_FALLBACK_NVDA = {
    "source": "surprise-api-fallback",
    "symbol": "NVDA",
    "price_usd": 951.23,
    "change_pct": 1.42,
    "volume": 24_137_890,
    "market_cap_b": 2347.6,
}

# Minimal lookup table so tests + demos don't depend on open-meteo geocoding.
_CITY_COORDS: dict[str, tuple[float, float]] = {
    "new york": (40.7128, -74.0060),
    "london": (51.5074, -0.1278),
    "tokyo": (35.6762, 139.6503),
    "san francisco": (37.7749, -122.4194),
    "singapore": (1.3521, 103.8198),
    "berlin": (52.52, 13.405),
    "paris": (48.8566, 2.3522),
}


async def _fetch_live_weather(city: str, base_url: str) -> dict[str, Any] | None:
    coords = _CITY_COORDS.get(city.strip().lower())
    if coords is None:
        return None
    lat, lon = coords
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                base_url,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                },
            )
            if resp.status_code != 200:
                return None
            data = resp.json().get("current") or {}
            temp_c = float(data.get("temperature_2m", 0.0))
            return {
                "source": "open-meteo",
                "city": city,
                "temp_c": temp_c,
                "temp_f": round(temp_c * 9 / 5 + 32, 2),
                "conditions": _weather_code_to_text(int(data.get("weather_code", 0))),
                "humidity_pct": data.get("relative_humidity_2m"),
                "wind_kmh": data.get("wind_speed_10m"),
            }
    except Exception as exc:
        logger.info("open-meteo fetch failed: %s", exc)
        return None


def _weather_code_to_text(code: int) -> str:
    # Open-Meteo WMO weather codes — compressed mapping (no silent default).
    table = {
        0: "Clear",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Rime fog",
        51: "Light drizzle",
        61: "Light rain",
        63: "Moderate rain",
        71: "Snow",
        80: "Rain showers",
        95: "Thunderstorm",
    }
    return table.get(code, f"Code {code}")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def build_app(
    settings: SurpriseAPISettings | None = None,
    *,
    registry: LocalRegistry | None = None,
    register_service: bool = True,
) -> FastAPI:
    """Construct the Surprise API FastAPI application.

    Args:
        settings: Optional overrides; otherwise loaded from env.
        registry: If provided, the ``SURPRISE_API_SERVICE_RECORD`` is
            registered here so the buyer agent discovers it via the
            normal ``DiscoveryService`` flow.
        register_service: Set False to skip registry registration (used
            when the caller wants to own registration explicitly).

    Returns:
        A fully wired FastAPI app with x402 middleware installed.
    """
    settings = settings or SurpriseAPISettings.from_env()
    pricing = PricingStore()
    pricing.set_price("/api/weather", settings.default_weather_price_atomic)
    pricing.set_price("/api/nvda", settings.default_nvda_price_atomic)

    middleware_cfg = X402MiddlewareConfig(
        seller_wallet=settings.seller_wallet,
        network=settings.network,
        asset=settings.asset,
        facilitator_url=settings.facilitator_url,
        service_name=SURPRISE_API_SERVICE_RECORD.name,
    )
    x402 = X402PaymentMiddleware(
        config=middleware_cfg,
        pricing=pricing,
        protected_routes={"/api/weather", "/api/nvda"},
        nonce_cache=NonceCache(),
    )

    app = FastAPI(
        title="Surprise API",
        description=(
            "Standalone x402-gated seller service for NegotiatorGrid "
            "Day-4 demo. Independent process, real 402 handshake."
        ),
        version="0.1.0",
    )

    # Stash for tests / dashboard introspection.
    app.state.settings = settings
    app.state.pricing = pricing
    app.state.x402 = x402
    app.state.service_record = SURPRISE_API_SERVICE_RECORD

    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(settings.cors_origins),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*", "X-Payment"],
            expose_headers=["X-Payment-Response"],
        )

    # The x402 gate runs BEFORE handlers but AFTER CORS.
    app.middleware("http")(x402)

    # -- Routes -----------------------------------------------------------

    @app.get("/")
    async def root() -> dict[str, Any]:
        """Browser-friendly index — this service has no HTML shell."""
        return {
            "service": "surprise-api",
            "message": "Use JSON endpoints below (GET / is not an HTML app).",
            "try": {
                "health": "/healthz",
                "agent_card": "/.well-known/agent.json",
                "nvda_x402": "/api/nvda",
                "weather_x402": "/api/weather",
            },
        }

    @app.get("/healthz")
    async def healthz() -> dict[str, Any]:
        return {
            "status": "ok",
            "service": "surprise-api",
            "version": "0.1.0",
            "network": settings.network,
            "facilitator": bool(settings.facilitator_url),
        }

    @app.get("/.well-known/agent.json")
    async def agent_card() -> dict[str, Any]:
        record = app.state.service_record
        return {
            "protocolVersion": "0.2.9",
            "name": record.name,
            "description": record.description,
            "url": f"https://surprise.negotiatorgrid.dev{record.resource_url}",
            "version": "0.1.0",
            "registrations": [
                {
                    "agentId": record.seller_agent_id,
                    "agentAddress": record.seller_address,
                    "signature": "0x",  # Filled in during chain registration
                }
            ],
            "capabilities": {
                "x402": True,
                "streaming": False,
            },
            "skills": [
                {
                    "id": "weather",
                    "name": "Current weather",
                    "description": "x402-paid current weather by city.",
                    "tags": ["weather", "x402"],
                    "endpoint": "/api/weather",
                },
                {
                    "id": "nvda-quote",
                    "name": "NVDA quote",
                    "description": "x402-paid NVDA stock quote.",
                    "tags": ["market-data", "x402"],
                    "endpoint": "/api/nvda",
                },
            ],
        }

    @app.get("/api/weather")
    async def weather(request: Request, city: str = "New York") -> dict[str, Any]:
        live = await _fetch_live_weather(city, settings.open_meteo_base)
        payload = live or {**_FALLBACK_WEATHER, "city": city}
        payment = getattr(request.state, "x402_payment", {})
        return {
            "data": payload,
            "paid_by": payment.get("payer"),
            "paid_amount_atomic": payment.get("amount"),
            "tx_hash": payment.get("tx_hash", ""),
            "facilitator_used": payment.get("facilitator_used", False),
        }

    @app.get("/api/nvda")
    async def nvda(request: Request) -> dict[str, Any]:
        payment = getattr(request.state, "x402_payment", {})
        return {
            "data": dict(_FALLBACK_NVDA),
            "paid_by": payment.get("payer"),
            "paid_amount_atomic": payment.get("amount"),
            "tx_hash": payment.get("tx_hash", ""),
            "facilitator_used": payment.get("facilitator_used", False),
        }

    @app.get("/api/receipts")
    async def receipts() -> JSONResponse:
        return JSONResponse(content={"receipts": list(x402.receipts)})

    # ------------------------------------------------------------------
    # Demo-only admin surface: lets the NegotiatorGrid policy layer push
    # a negotiated price + deal hash into the seller's PricingStore *and*
    # into the ``extra`` block echoed in 402 responses. Without this hop,
    # the buyer's pre-payment ``verify_payment_requirements`` correctly
    # rejects the seller for advertising a stale list price — that IS the
    # hash-mismatch hero shot. After the sync, the same buyer accepts and
    # pays. Authentication is intentionally absent for demo simplicity
    # (testnet only); do not expose this in production.
    # ------------------------------------------------------------------
    @app.post("/admin/sync-deal")
    async def sync_deal(payload: dict[str, Any]) -> dict[str, Any]:
        route = payload.get("route") or "/api/nvda"
        price_atomic = int(payload.get("price_atomic") or 0)
        deal_hash = str(payload.get("deal_hash") or "")
        expected_buyer = str(payload.get("expected_buyer") or "")
        if price_atomic <= 0:
            return {"ok": False, "error": "price_atomic_required"}

        pricing.set_price(route, price_atomic)

        # Stash deal-binding hints so build_payment_requirements echoes them.
        app.state.deal_bindings = getattr(app.state, "deal_bindings", {})
        app.state.deal_bindings[route] = {
            "deal_hash": deal_hash,
            "expected_buyer": expected_buyer,
        }

        # Patch the middleware's PR builder ONCE so future 402s carry the
        # negotiated extra fields. Repeated /admin/sync-deal calls update
        # ``app.state.deal_bindings`` only — never re-wrap the builder.
        if not getattr(x402, "_binding_patched", False):
            original_builder = x402.build_payment_requirements

            def _build_with_binding(r: str, atomic: int) -> dict[str, Any]:
                requirements = original_builder(r, atomic)
                binding = (app.state.deal_bindings or {}).get(r) or {}
                if binding.get("deal_hash"):
                    requirements.setdefault("extra", {})["deal_hash"] = binding["deal_hash"]
                if binding.get("expected_buyer"):
                    requirements["extra"]["expected_buyer"] = binding["expected_buyer"]
                return requirements

            x402.build_payment_requirements = _build_with_binding  # type: ignore[assignment]
            x402._binding_patched = True  # type: ignore[attr-defined]

        return {
            "ok": True,
            "route": route,
            "price_atomic": price_atomic,
            "deal_hash": deal_hash,
            "expected_buyer": expected_buyer,
        }

    @app.post("/admin/reset")
    async def reset_pricing() -> dict[str, Any]:
        pricing.set_price("/api/weather", settings.default_weather_price_atomic)
        pricing.set_price("/api/nvda", settings.default_nvda_price_atomic)
        app.state.deal_bindings = {}
        return {"ok": True, "weather": settings.default_weather_price_atomic,
                "nvda": settings.default_nvda_price_atomic}

    if register_service and registry is not None:
        registry.register(SURPRISE_API_SERVICE_RECORD)

    return app


# ---------------------------------------------------------------------------
# Module-level app (uvicorn entry point)
# ---------------------------------------------------------------------------


def _module_app() -> FastAPI:
    """Used by ``uvicorn surprise_api.app:app``."""
    return build_app(register_service=False)


app = _module_app()
