"""In-process service catalog used as the discovery fallback.

Rationale (from ``current_tech_problems.md``): Passport invites are
the single biggest bottleneck for hackathon builders. When the live
Kite MCP is unreachable (no API key, no invite) we MUST still be able
to demo a full discover → verify → negotiate chain.

This module holds a handful of synthetic "negotiable services" that
mirror the exact Kite tool shape (matching
``get_service_details`` output fields from
``research-plan-docs/1.3-kite-mcp-server-deep-dive.md``). Keep the
data here intentionally small and human-readable so judges can diff
it against the live server's payloads at demo time.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ServiceRecord:
    """One negotiable service entry.

    Matches the shape of Kite's ``get_service_details`` response plus
    the NegotiatorGrid-specific extension fields documented in
    ``research-plan-docs/4.2-mcp-registries-x402-catalogs-research.md``.
    """

    service_id: str
    name: str
    description: str
    capability: str  # free-text tag used for capability lookup
    seller_address: str
    seller_agent_id: int
    reservation_price: float  # seller floor (micro-USDT)
    list_price: float  # seller opening ask (micro-USDT)
    resource_url: str
    endpoints: list[str] = field(default_factory=list)
    input_fields: dict[str, str] = field(default_factory=dict)
    response_fields: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    reputation: float = 0.75  # 0.0 - 1.0 score (pre-loaded)
    negotiable: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_service_details(self) -> dict[str, Any]:
        """Return the exact payload Kite's ``get_service_details`` emits."""
        return {
            "description": self.description,
            "input_fields": dict(self.input_fields),
            "response_fields": dict(self.response_fields),
            "service_info": (
                f"{self.name} — endpoints: "
                + ", ".join(self.endpoints or [self.resource_url])
            ),
        }

    def to_search_entry(self) -> dict[str, Any]:
        """Return the public entry used by ``list_negotiable_services``."""
        return {
            "service_id": self.service_id,
            "name": self.name,
            "capability": self.capability,
            "resource_url": self.resource_url,
            "seller_address": self.seller_address,
            "seller_agent_id": self.seller_agent_id,
            "list_price": self.list_price,
            "reservation_price": self.reservation_price,
            "tags": list(self.tags),
            "reputation": self.reputation,
            "negotiable": self.negotiable,
        }


# ---------------------------------------------------------------------------
# Default fixture — used by the mock server and by DiscoveryService when
# the live MCP is offline.
# ---------------------------------------------------------------------------

_DEFAULT_SERVICES: list[ServiceRecord] = [
    ServiceRecord(
        service_id="agent_LpzYVzWGzjGiZBI3HTm4ZCKj",
        name="WeatherPro-Service",
        description=(
            "High-uptime weather API. 200 RPS, sub-150ms p95 latency, "
            "99.9% SLA. Pay-per-call via x402."
        ),
        capability="weather-data",
        seller_address="0x209693Bc6412A8b3D23E1bF6E1d59EbFf95bC2cE",
        seller_agent_id=2,
        reservation_price=800.0,
        list_price=1500.0,
        resource_url="/api/weather",
        endpoints=["https://api.weatherpro.demo/v1/current"],
        input_fields={"city": "string", "units": "string"},
        response_fields={"temp_c": "number", "conditions": "string"},
        tags=["weather-api", "geolocation", "high-uptime"],
        reputation=0.90,
    ),
    ServiceRecord(
        service_id="agent_NewsProto_17",
        name="NewsProto-Service",
        description=(
            "Real-time news ticker: headlines, summaries, and sentiment. "
            "Negotiable-pricing endpoint."
        ),
        capability="news-feed",
        seller_address="0x4e3Ab8d8e2c6e9c7D7b1aE4c4a0c3cEe67aA1122",
        seller_agent_id=3,
        reservation_price=1000.0,
        list_price=1800.0,
        resource_url="/api/news",
        endpoints=["https://api.newsproto.demo/v1/headlines"],
        input_fields={"topic": "string", "limit": "number"},
        response_fields={"headlines": "array", "sentiment": "number"},
        tags=["news", "nlp", "sentiment"],
        reputation=0.72,
    ),
    ServiceRecord(
        service_id="agent_SatImagery_42",
        name="SatImagery-Service",
        description=(
            "Satellite imagery for agri/logistics use cases. Per-tile "
            "pricing; premium option for 15-minute refresh."
        ),
        capability="satellite-imagery",
        seller_address="0x9e1F5aA36Bf9f74c5Bd82e61a3E7f44B5C22Dd11",
        seller_agent_id=4,
        reservation_price=6000.0,
        list_price=12000.0,
        resource_url="/api/satellite",
        endpoints=["https://api.satimagery.demo/v1/tile"],
        input_fields={"bbox": "string", "date": "string"},
        response_fields={"tile_url": "string", "resolution_m": "number"},
        tags=["imagery", "geospatial", "remote-sensing"],
        reputation=0.84,
    ),
]


class LocalRegistry:
    """Thread-safe (single-threaded async) service catalog.

    The registry exposes the minimum Kite-compatible surface we need
    for discovery:

    * ``list_services(capability=...)`` — used by the mock
      ``list_negotiable_services`` tool.
    * ``get(service_id)`` — used by the mock ``get_service_details``
      tool.
    * ``register(record)`` / ``unregister(service_id)`` — used by
      tests and by the `DiscoveryService.register_discovered_tool`
      stub so locally-spun-up services can be re-discovered in the
      same process.
    """

    def __init__(self, services: list[ServiceRecord] | None = None) -> None:
        src = services if services is not None else _DEFAULT_SERVICES
        # Deep-copy so mutating a record doesn't leak across instances.
        self._services: dict[str, ServiceRecord] = {
            s.service_id: copy.deepcopy(s) for s in src
        }

    # -- Queries --------------------------------------------------------

    def list_services(
        self,
        capability: str | None = None,
        *,
        tag: str | None = None,
        min_reputation: float = 0.0,
    ) -> list[ServiceRecord]:
        """Return services matching the given filters."""
        out: list[ServiceRecord] = []
        for svc in self._services.values():
            if capability and svc.capability != capability:
                continue
            if tag and tag not in svc.tags:
                continue
            if svc.reputation < min_reputation:
                continue
            out.append(svc)
        # Stable order: highest reputation first, then by id.
        out.sort(key=lambda s: (-s.reputation, s.service_id))
        return out

    def get(self, service_id: str) -> ServiceRecord | None:
        return self._services.get(service_id)

    def all(self) -> list[ServiceRecord]:
        return list(self._services.values())

    # -- Mutations ------------------------------------------------------

    def register(self, record: ServiceRecord) -> None:
        self._services[record.service_id] = record

    def unregister(self, service_id: str) -> bool:
        return self._services.pop(service_id, None) is not None


def default_registry() -> LocalRegistry:
    """Return a fresh registry populated with the default fixture."""
    return LocalRegistry()
