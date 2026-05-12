"""Integration tests for the Day-4 Surprise API + x402 buyer client.

Everything runs in-process via ``httpx.ASGITransport`` — no network
required, no facilitator required. This guarantees CI + demo-day
reliability even with zero external connectivity.
"""

from __future__ import annotations

import asyncio
import base64
import json

import httpx
import pytest
from eth_account import Account

from negotiatorgrid.core.x402_buyer import X402BuyerClient, X402FetchResult
from negotiatorgrid.discovery.local_registry import LocalRegistry
from surprise_api.app import SURPRISE_API_SERVICE_RECORD, SurpriseAPISettings, build_app
from surprise_api.x402_middleware import NonceCache, _decode_x_payment

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def seller_key() -> str:
    # Deterministic throwaway key; checksum wallet fed into settings.
    return "0x" + "1" * 64


@pytest.fixture
def buyer_key() -> str:
    return "0x" + "2" * 64


@pytest.fixture
def settings(seller_key: str) -> SurpriseAPISettings:
    wallet = Account.from_key(seller_key).address
    return SurpriseAPISettings(
        seller_wallet=wallet,
        facilitator_url="",  # Force local verify path.
        default_weather_price_atomic=25_000,
        default_nvda_price_atomic=30_000,
        # Point open-meteo at a dead host so fallback data is used —
        # keeps tests network-free & deterministic.
        open_meteo_base="http://127.0.0.1:1/forecast",
    )


@pytest.fixture
def registry() -> LocalRegistry:
    return LocalRegistry(services=[])


@pytest.fixture
def app(settings: SurpriseAPISettings, registry: LocalRegistry):
    return build_app(settings=settings, registry=registry, register_service=True)


@pytest.fixture
def transport(app):
    return httpx.ASGITransport(app=app)


# ---------------------------------------------------------------------------
# Infrastructure checks
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_endpoint_is_open(transport: httpx.ASGITransport) -> None:
    async with httpx.AsyncClient(transport=transport, base_url="http://surprise") as c:
        resp = await c.get("/healthz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["service"] == "surprise-api"
    assert body["network"] == "eip155:2368"


@pytest.mark.asyncio
async def test_agent_card_is_open(transport: httpx.ASGITransport) -> None:
    async with httpx.AsyncClient(transport=transport, base_url="http://surprise") as c:
        resp = await c.get("/.well-known/agent.json")
    assert resp.status_code == 200
    card = resp.json()
    assert card["name"] == "Surprise API"
    assert card["capabilities"]["x402"] is True
    assert {s["id"] for s in card["skills"]} == {"weather", "nvda-quote"}


def test_app_registers_service_in_registry(registry: LocalRegistry, app) -> None:
    record = registry.get(SURPRISE_API_SERVICE_RECORD.service_id)
    assert record is not None
    assert record.capability == "surprise-data"
    assert record.resource_url == "/api/weather"


# ---------------------------------------------------------------------------
# 402 gating
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_weather_without_payment_returns_402(
    transport: httpx.ASGITransport,
) -> None:
    async with httpx.AsyncClient(transport=transport, base_url="http://surprise") as c:
        resp = await c.get("/api/weather")
    assert resp.status_code == 402
    body = resp.json()
    assert body["x402Version"] == 1
    assert body["error"] == "payment_required"
    accepts = body["accepts"]
    assert len(accepts) == 1
    req = accepts[0]
    assert req["scheme"] == "exact"
    assert req["network"] == "eip155:2368"
    assert int(req["maxAmountRequired"]) == 25_000
    assert req["resource"] == "/api/weather"


@pytest.mark.asyncio
async def test_nvda_without_payment_returns_402(
    transport: httpx.ASGITransport,
) -> None:
    async with httpx.AsyncClient(transport=transport, base_url="http://surprise") as c:
        resp = await c.get("/api/nvda")
    assert resp.status_code == 402
    body = resp.json()
    assert int(body["accepts"][0]["maxAmountRequired"]) == 30_000


@pytest.mark.asyncio
async def test_bad_base64_x_payment_rejected(
    transport: httpx.ASGITransport,
) -> None:
    async with httpx.AsyncClient(transport=transport, base_url="http://surprise") as c:
        resp = await c.get(
            "/api/weather", headers={"X-Payment": "not-base64!!!"}
        )
    assert resp.status_code == 402
    assert resp.json()["error"] == "malformed_payment"


@pytest.mark.asyncio
async def test_forged_signature_rejected(
    transport: httpx.ASGITransport, seller_key: str
) -> None:
    # Build a structurally-valid but unsigned payload.
    seller_wallet = Account.from_key(seller_key).address
    authorization = {
        "from": "0x0000000000000000000000000000000000000001",
        "to": seller_wallet,
        "value": "25000",
        "validAfter": "0",
        "validBefore": str(2**32),
        "nonce": "0x" + "ab" * 32,
    }
    payload = {
        "x402Version": 1,
        "scheme": "exact",
        "network": "eip155:2368",
        "payload": {
            "signature": "0x" + "cd" * 65,
            "authorization": authorization,
        },
    }
    header = base64.b64encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")
    async with httpx.AsyncClient(transport=transport, base_url="http://surprise") as c:
        resp = await c.get("/api/weather", headers={"X-Payment": header})
    assert resp.status_code == 402
    assert resp.json()["error"] == "invalid_exact_evm_signature"


# ---------------------------------------------------------------------------
# Happy path via the real buyer client
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_buyer_completes_402_handshake(
    transport: httpx.ASGITransport, buyer_key: str
) -> None:
    buyer = X402BuyerClient(private_key=buyer_key, transport=transport)
    result = await buyer.fetch_with_payment(
        "http://surprise/api/weather", params={"city": "New York"}
    )
    assert isinstance(result, X402FetchResult)
    assert result.success, f"expected success, got status={result.status_code} err={result.error}"
    assert result.payment_amount == 25_000
    assert result.payer_address == Account.from_key(buyer_key).address
    assert result.data["paid_by"] == result.payer_address
    # Fallback weather is served because open-meteo base is unreachable.
    assert result.data["data"]["city"] == "New York"
    assert "temp_c" in result.data["data"]


@pytest.mark.asyncio
async def test_buyer_over_budget_does_not_pay(
    transport: httpx.ASGITransport, buyer_key: str
) -> None:
    buyer = X402BuyerClient(private_key=buyer_key, transport=transport)
    result = await buyer.fetch_with_payment(
        "http://surprise/api/nvda",
        max_price_atomic=1,  # less than 30_000 asking.
    )
    assert not result.success
    assert result.error == "over_budget"
    assert result.payment_amount == 30_000


# ---------------------------------------------------------------------------
# Replay protection
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_replay_of_payment_rejected(
    transport: httpx.ASGITransport, buyer_key: str, app
) -> None:
    buyer = X402BuyerClient(private_key=buyer_key, transport=transport)

    # First request: perform real 402 handshake so we capture the header.
    async with httpx.AsyncClient(
        transport=transport, base_url="http://surprise"
    ) as c:
        first = await c.get("/api/weather")
        assert first.status_code == 402
        requirements = first.json()["accepts"][0]
        header = buyer._build_payment_header(requirements)
        ok = await c.get("/api/weather", headers={"X-Payment": header})
        assert ok.status_code == 200

        # Same header again → replay.
        replay = await c.get("/api/weather", headers={"X-Payment": header})
        assert replay.status_code == 402
        assert replay.json()["error"] == "invalid_exact_evm_nonce_already_used"


# ---------------------------------------------------------------------------
# Receipts log
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_receipts_are_recorded_after_successful_payment(
    transport: httpx.ASGITransport, buyer_key: str, app
) -> None:
    buyer = X402BuyerClient(private_key=buyer_key, transport=transport)
    result = await buyer.fetch_with_payment("http://surprise/api/weather")
    assert result.success

    async with httpx.AsyncClient(
        transport=transport, base_url="http://surprise"
    ) as c:
        resp = await c.get("/api/receipts")
    receipts = resp.json()["receipts"]
    assert len(receipts) == 1
    r = receipts[0]
    assert r["route"] == "/api/weather"
    assert r["payer"] == Account.from_key(buyer_key).address
    assert r["amount"] == 25_000
    assert r["facilitator_used"] is False


# ---------------------------------------------------------------------------
# Unit-level sanity
# ---------------------------------------------------------------------------


def test_decode_x_payment_roundtrip() -> None:
    payload = {"x402Version": 1, "scheme": "exact", "network": "eip155:2368"}
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    assert _decode_x_payment(encoded) == payload


@pytest.mark.asyncio
async def test_nonce_cache_detects_replay() -> None:
    cache = NonceCache()
    exp = 9_999_999_999.0
    assert await cache.check_and_record("abc", exp) is True
    assert await cache.check_and_record("abc", exp) is False
    assert await cache.check_and_record("def", exp) is True


@pytest.mark.asyncio
async def test_nonce_cache_evicts_expired() -> None:
    cache = NonceCache()
    # Expired nonce
    assert await cache.check_and_record("old", 1.0) is True
    # Force at least one second forward in logical time by sleeping.
    await asyncio.sleep(0.01)
    # A new nonce triggers GC; the expired one should be forgotten.
    assert await cache.check_and_record("new", 9_999_999_999.0) is True
    # Re-using "old" should succeed because it was GC'd.
    assert await cache.check_and_record("old", 9_999_999_999.0) is True
