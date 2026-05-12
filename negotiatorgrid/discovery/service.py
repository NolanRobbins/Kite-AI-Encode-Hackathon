"""High-level discovery orchestrator.

The :class:`DiscoveryService` is what ``NegotiationExecutor`` calls
before the ``DISCOVERING → VERIFYING → NEGOTIATING`` transition. It
encapsulates four failure-tolerant steps:

1. **Capability lookup** — try the live Kite MCP via :class:`MCPClient`.
   If unauthenticated/unreachable, transparently fall back to the
   in-process :class:`LocalRegistry` + :class:`MockMCPServer`.
2. **Service details** — fetch the structured ``get_service_details``
   payload so the buyer agent can validate schemas before paying.
3. **Identity verification** — read the seller's wallet from the
   ERC-8004 ``IdentityRegistry``, confirming the MCP-advertised
   address matches what the chain says.
4. **Reputation gate** — query ``ReputationFeed`` and reject sellers
   below the configured threshold.

The service never raises on partial failures — it returns a
:class:`DiscoveryResult` whose ``mode`` field tells callers which path
actually ran (``live``, ``mock``, ``in_process``). This lets the
dashboard render honest "LIVE" vs "MOCK" badges instead of silently
lying.
"""

from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Awaitable, Callable, Optional

from negotiatorgrid.discovery.local_registry import (
    LocalRegistry,
    ServiceRecord,
    default_registry,
)
from negotiatorgrid.discovery.mcp_client import MCPClient, MCPError
from negotiatorgrid.discovery.mock_server import MockMCPServer

logger = logging.getLogger(__name__)

DiscoveryMode = str  # "live" | "in_process" | "mock"


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------


@dataclass
class DiscoveryResult:
    """Result of a capability → service lookup."""

    capability: str
    service_id: str = ""
    name: str = ""
    description: str = ""
    resource_url: str = ""
    seller_address: str = ""
    seller_agent_id: int = 0
    list_price: float = 0.0
    reservation_price: float = 0.0
    reputation: float = 0.0
    tags: list[str] = field(default_factory=list)
    service_details: dict[str, Any] = field(default_factory=dict)
    mode: DiscoveryMode = "in_process"
    mcp_endpoint: str = ""
    duration_ms: float = 0.0
    matched_tools: list[str] = field(default_factory=list)
    error: str = ""  # terminal error: set only when no service was found
    live_path_error: str = ""  # non-fatal: live MCP failed, we fell back

    @property
    def success(self) -> bool:
        return bool(self.service_id)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["success"] = self.success
        return d


@dataclass
class VerificationResult:
    """Result of ERC-8004 identity + reputation verification."""

    agent_id: int
    claimed_address: str
    onchain_address: str = ""
    address_matches: bool = False
    reputation: float = 0.0
    reputation_passed: bool = False
    threshold: float = 0.0
    duration_ms: float = 0.0
    mode: DiscoveryMode = "mock"  # "live" if real chain read, "mock" otherwise
    error: str = ""

    @property
    def passed(self) -> bool:
        return self.address_matches and self.reputation_passed and not self.error

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["passed"] = self.passed
        return d


# ---------------------------------------------------------------------------
# DiscoveryService
# ---------------------------------------------------------------------------


EventCallback = Callable[[str, dict[str, Any]], Awaitable[None]]


class DiscoveryService:
    """Discovers negotiable services and verifies counterparty identity.

    Parameters
    ----------
    registry:
        Local fallback catalog. Defaults to the built-in fixture.
    mcp_endpoint:
        Optional live Kite MCP endpoint. If set, we try the network
        path first and only fall back to ``registry`` on failure.
    mcp_auth_token:
        OAuth bearer for ``neo.dev.gokite.ai``. If unset, the Passport
        MCP will reject us and we'll fall back cleanly.
    identity_client:
        Optional :class:`IdentityClient` for real ERC-8004 lookups.
        Passing a client that's in mock mode is fine — the service
        will note ``mode="mock"`` in its verification result.
    reputation_feed:
        Optional :class:`ReputationFeed` for on-chain reputation. If
        omitted we trust the ``reputation`` value on the service record.
    reputation_threshold:
        Minimum score (0.0 - 1.0) required to pass verification.
    event_callback:
        Optional async callable ``(event_type, data)`` used to stream
        discovery/verification events over WebSocket. Failures in the
        callback are swallowed — the core flow must never break because
        the UI is offline.
    """

    def __init__(
        self,
        registry: Optional[LocalRegistry] = None,
        *,
        mcp_endpoint: str = "",
        mcp_auth_token: str = "",
        identity_client: Any = None,
        reputation_feed: Any = None,
        reputation_threshold: float = 0.5,
        event_callback: Optional[EventCallback] = None,
    ) -> None:
        self._registry = registry or default_registry()
        self._mcp_endpoint = mcp_endpoint
        self._mcp_auth_token = mcp_auth_token
        self._identity_client = identity_client
        self._reputation_feed = reputation_feed
        self._threshold = reputation_threshold
        self._event_cb = event_callback
        # An in-process MockMCPServer gives us parity with the live
        # server for demos: even the "in_process" fallback path walks
        # the exact JSON-RPC shapes.
        self._mock_server = MockMCPServer(self._registry)

    # -- Public API ------------------------------------------------------

    async def discover_tool(
        self,
        capability: str,
        *,
        negotiation_id: str = "",
    ) -> DiscoveryResult:
        """Resolve a capability string to a concrete service record."""
        started = time.monotonic()
        await self._emit(
            "discovery_started",
            {
                "negotiation_id": negotiation_id,
                "capability": capability,
                "mcp_endpoint": self._mcp_endpoint or "local://mock",
            },
        )

        record: ServiceRecord | None = None
        mode: DiscoveryMode = "in_process"
        matched_tools: list[str] = []
        live_path_error = ""

        if self._mcp_endpoint:
            try:
                record, matched_tools = await self._discover_live(capability)
                if record is not None:
                    mode = "live"
            except MCPError as exc:
                logger.info(
                    "Live MCP discovery failed (%s). Falling back to local registry.",
                    exc,
                )
                live_path_error = f"live_failed: {exc}"
            except Exception as exc:
                logger.warning("Unexpected live MCP failure: %s", exc)
                live_path_error = f"live_failed: {exc}"

        if record is None:
            record, matched_tools = await self._discover_mock(capability)
            # mark as "mock" if a live attempt was made, else "in_process"
            mode = "mock" if (live_path_error or self._mcp_endpoint) else "in_process"

        duration_ms = round((time.monotonic() - started) * 1000.0, 2)

        if record is None:
            result = DiscoveryResult(
                capability=capability,
                mode=mode,
                mcp_endpoint=self._mcp_endpoint,
                matched_tools=matched_tools,
                duration_ms=duration_ms,
                error=f"no_service_for_capability: {capability}",
                live_path_error=live_path_error,
            )
        else:
            details = await self._fetch_service_details(record, mode)
            result = DiscoveryResult(
                capability=capability,
                service_id=record.service_id,
                name=record.name,
                description=record.description,
                resource_url=record.resource_url,
                seller_address=record.seller_address,
                seller_agent_id=record.seller_agent_id,
                list_price=record.list_price,
                reservation_price=record.reservation_price,
                reputation=record.reputation,
                tags=list(record.tags),
                service_details=details,
                mode=mode,
                mcp_endpoint=self._mcp_endpoint,
                matched_tools=matched_tools,
                duration_ms=duration_ms,
                live_path_error=live_path_error,
            )

        await self._emit(
            "discovery_completed",
            {"negotiation_id": negotiation_id, **result.to_dict()},
        )
        return result

    async def verify_discovered_agent(
        self,
        discovery: DiscoveryResult,
        *,
        negotiation_id: str = "",
    ) -> VerificationResult:
        """Run ERC-8004 + reputation checks against a discovered agent."""
        started = time.monotonic()
        await self._emit(
            "verification_started",
            {
                "negotiation_id": negotiation_id,
                "agent_id": discovery.seller_agent_id,
                "claimed_address": discovery.seller_address,
            },
        )

        onchain_address = ""
        mode: DiscoveryMode = "mock"
        error = ""

        if self._identity_client is not None and discovery.seller_agent_id:
            try:
                onchain_address = self._identity_client.get_agent_wallet(
                    discovery.seller_agent_id
                )
                # IdentityClient reports mock mode via its own attribute.
                is_mock = getattr(self._identity_client, "_mock", True)
                mode = "mock" if is_mock else "live"
            except Exception as exc:
                logger.info("Identity lookup failed: %s", exc)
                error = f"identity_lookup_failed: {exc}"

        # If no identity client is wired, or we're in mock mode, trust
        # the claim (same behaviour the legacy demo used).
        if not onchain_address:
            onchain_address = discovery.seller_address

        address_matches = bool(onchain_address) and (
            onchain_address.lower() == discovery.seller_address.lower()
        )

        # Reputation: prefer live feed if available, else service record.
        reputation = discovery.reputation
        if self._reputation_feed is not None and discovery.seller_address:
            try:
                profile = self._reputation_feed.get_agent_reputation(
                    discovery.seller_address
                )
                reputation = float(getattr(profile, "reputation_score", reputation))
            except Exception as exc:
                logger.debug("Reputation lookup fell back to record value: %s", exc)

        reputation_passed = reputation >= self._threshold
        duration_ms = round((time.monotonic() - started) * 1000.0, 2)

        result = VerificationResult(
            agent_id=discovery.seller_agent_id,
            claimed_address=discovery.seller_address,
            onchain_address=onchain_address,
            address_matches=address_matches,
            reputation=reputation,
            reputation_passed=reputation_passed,
            threshold=self._threshold,
            duration_ms=duration_ms,
            mode=mode,
            error=error,
        )

        await self._emit(
            "verification_completed",
            {"negotiation_id": negotiation_id, **result.to_dict()},
        )
        return result

    async def register_discovered_tool(self, record: ServiceRecord) -> None:
        """Register a locally-spun-up service so future lookups find it."""
        self._registry.register(record)

    # -- Live discovery via MCP ----------------------------------------

    async def _discover_live(
        self, capability: str
    ) -> tuple[ServiceRecord | None, list[str]]:
        """Attempt discovery via the configured live MCP endpoint."""
        matched_tools: list[str] = []
        async with MCPClient(
            self._mcp_endpoint, auth_token=self._mcp_auth_token or None
        ) as client:
            tools = await client.list_tools()
            matched_tools = [t.name for t in tools]

            # Preferred path: NegotiatorGrid extension tool.
            if any(t.name == "list_negotiable_services" for t in tools):
                result = await client.call_tool(
                    "list_negotiable_services", {"capability": capability}
                )
                services = result.structured.get("services") or []
                for entry in services:
                    if entry.get("capability") == capability:
                        return self._entry_to_record(entry), matched_tools

            # Fallback: Kite's native get_service_details if we can find
            # a service id that matches the capability (tag-based match).
            for t in tools:
                if t.name == "get_service_details":
                    # Without a directory endpoint on the live server,
                    # we can't browse by capability. Signal "not found"
                    # so the caller falls back to the local registry.
                    break
        return None, matched_tools

    # -- In-process / mock discovery -----------------------------------

    async def _discover_mock(
        self, capability: str
    ) -> tuple[ServiceRecord | None, list[str]]:
        """Discovery via the in-process MockMCPServer (parity mode)."""
        envelope = await self._mock_server.handle_jsonrpc(
            {
                "jsonrpc": "2.0",
                "id": "discovery",
                "method": "tools/call",
                "params": {
                    "name": "list_negotiable_services",
                    "arguments": {"capability": capability},
                },
            }
        )
        matched_tools = ["list_negotiable_services", "get_service_details", "call_service"]
        if not envelope or "result" not in envelope:
            return None, matched_tools
        services = (
            (envelope["result"].get("structuredContent") or {}).get("services") or []
        )
        for entry in services:
            if entry.get("capability") == capability:
                record = self._registry.get(entry["service_id"])
                if record:
                    return record, matched_tools
        return None, matched_tools

    async def _fetch_service_details(
        self, record: ServiceRecord, mode: DiscoveryMode
    ) -> dict[str, Any]:
        """Invoke ``get_service_details`` for the chosen service."""
        if mode == "live":
            try:
                async with MCPClient(
                    self._mcp_endpoint, auth_token=self._mcp_auth_token or None
                ) as client:
                    r = await client.call_tool(
                        "get_service_details", {"service_id": record.service_id}
                    )
                    if r.structured:
                        return r.structured
            except MCPError as exc:
                logger.debug("Live get_service_details failed: %s", exc)
        # In-process fallback always works.
        envelope = await self._mock_server.handle_jsonrpc(
            {
                "jsonrpc": "2.0",
                "id": "details",
                "method": "tools/call",
                "params": {
                    "name": "get_service_details",
                    "arguments": {"service_id": record.service_id},
                },
            }
        )
        if envelope and "result" in envelope:
            return envelope["result"].get("structuredContent") or {}
        return record.to_service_details()

    # -- Helpers --------------------------------------------------------

    @staticmethod
    def _entry_to_record(entry: dict[str, Any]) -> ServiceRecord:
        """Convert a live-server search entry into a local ``ServiceRecord``."""
        return ServiceRecord(
            service_id=str(entry.get("service_id", "")),
            name=str(entry.get("name", "")),
            description=str(entry.get("description", "")),
            capability=str(entry.get("capability", "")),
            seller_address=str(entry.get("seller_address", "")),
            seller_agent_id=int(entry.get("seller_agent_id") or 0),
            reservation_price=float(entry.get("reservation_price") or 0.0),
            list_price=float(entry.get("list_price") or 0.0),
            resource_url=str(entry.get("resource_url", "")),
            tags=list(entry.get("tags") or []),
            reputation=float(entry.get("reputation") or 0.0),
            negotiable=bool(entry.get("negotiable", True)),
        )

    async def _emit(self, event_type: str, data: dict[str, Any]) -> None:
        if self._event_cb is None:
            return
        try:
            await self._event_cb(event_type, data)
        except Exception:
            logger.debug("Discovery event callback failed (non-fatal)", exc_info=True)
