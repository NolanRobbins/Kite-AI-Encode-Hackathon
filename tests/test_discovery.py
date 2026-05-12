"""Tests for the Day-3 discovery layer.

Covers:

* :class:`LocalRegistry` — filtering, mutation, default fixture.
* :class:`MockMCPServer` — JSON-RPC dispatch, error envelopes,
  structured + text content, notifications ACK.
* :class:`MCPClient` — SSE parsing, plain-JSON fallback, live HTTP
  round-trip against the mock server via ``httpx.ASGITransport``.
* :class:`DiscoveryService` — capability → record, verification
  (identity + reputation), graceful live-MCP fallback, events.
* Executor integration — ``DISCOVERING → VERIFYING → NEGOTIATING``
  state flow with discovery metadata attached to results.
"""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from negotiatorgrid.discovery.local_registry import (
    LocalRegistry,
    ServiceRecord,
    default_registry,
)
from negotiatorgrid.discovery.mcp_client import (
    MCPClient,
    MCPError,
    MCPTool,
    _parse_sse_body,
)
from negotiatorgrid.discovery.mock_server import MockMCPServer, build_starlette_app
from negotiatorgrid.discovery.service import DiscoveryService
from negotiatorgrid.executors.negotiation import (
    AgentConfig,
    NegotiationExecutor,
    NegotiationParams,
    NegotiationState,
)

# ---------------------------------------------------------------------------
# LocalRegistry
# ---------------------------------------------------------------------------


def test_default_registry_has_negotiable_services() -> None:
    reg = default_registry()
    services = reg.all()
    assert len(services) >= 3
    caps = {s.capability for s in services}
    assert "weather-data" in caps


def test_registry_filters_by_capability_tag_and_reputation() -> None:
    reg = default_registry()

    # Exact capability match
    weather = reg.list_services(capability="weather-data")
    assert len(weather) == 1
    assert weather[0].name == "WeatherPro-Service"

    # Tag filter
    with_geo = reg.list_services(tag="geolocation")
    assert any(s.service_id.startswith("agent_Lpz") for s in with_geo)

    # Reputation threshold excludes lower-reputation services
    high_rep = reg.list_services(min_reputation=0.85)
    assert all(s.reputation >= 0.85 for s in high_rep)
    assert reg.list_services(min_reputation=1.1) == []


def test_registry_register_and_unregister_are_isolated() -> None:
    reg = LocalRegistry(services=[])
    assert reg.all() == []

    record = ServiceRecord(
        service_id="svc_custom",
        name="Custom",
        description="",
        capability="custom-cap",
        seller_address="0x" + "a" * 40,
        seller_agent_id=99,
        reservation_price=1.0,
        list_price=5.0,
        resource_url="/api/custom",
    )
    reg.register(record)
    assert reg.get("svc_custom") is record or reg.get("svc_custom").service_id == "svc_custom"
    assert reg.unregister("svc_custom") is True
    assert reg.get("svc_custom") is None
    assert reg.unregister("svc_custom") is False  # idempotent


def test_service_record_to_service_details_matches_kite_shape() -> None:
    record = default_registry().get("agent_LpzYVzWGzjGiZBI3HTm4ZCKj")
    assert record is not None
    payload = record.to_service_details()
    # Kite's get_service_details returns exactly these four keys.
    assert set(payload.keys()) == {
        "description",
        "input_fields",
        "response_fields",
        "service_info",
    }


# ---------------------------------------------------------------------------
# MockMCPServer
# ---------------------------------------------------------------------------


@pytest.fixture()
def server() -> MockMCPServer:
    return MockMCPServer(default_registry())


async def test_server_initialize_reports_kite_identity(server: MockMCPServer) -> None:
    envelope = await server.handle_jsonrpc(
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    )
    assert envelope is not None
    result = envelope["result"]
    assert result["protocolVersion"] == "2024-11-05"
    # Matches the live server string (parity requirement).
    assert result["serverInfo"]["name"] == "Kite Passport MCP"


async def test_server_lists_three_tools_including_extension(server: MockMCPServer) -> None:
    envelope = await server.handle_jsonrpc(
        {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    )
    assert envelope is not None
    names = {t["name"] for t in envelope["result"]["tools"]}
    assert names == {
        "get_service_details",
        "call_service",
        "list_negotiable_services",
    }


async def test_server_get_service_details_returns_structured_payload(
    server: MockMCPServer,
) -> None:
    envelope = await server.handle_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_service_details",
                "arguments": {"service_id": "agent_LpzYVzWGzjGiZBI3HTm4ZCKj"},
            },
        }
    )
    assert envelope is not None
    result = envelope["result"]
    assert result["isError"] is False
    assert "description" in result["structuredContent"]
    # Text content is JSON-encoded and round-trips to the structured payload.
    text_block = result["content"][0]["text"]
    assert json.loads(text_block) == result["structuredContent"]


async def test_server_unknown_service_returns_json_rpc_error(server: MockMCPServer) -> None:
    envelope = await server.handle_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_service_details",
                "arguments": {"service_id": "missing"},
            },
        }
    )
    assert envelope is not None
    assert "error" in envelope
    assert envelope["error"]["code"] == -32602


async def test_server_unknown_method_returns_method_not_found(server: MockMCPServer) -> None:
    envelope = await server.handle_jsonrpc(
        {"jsonrpc": "2.0", "id": 4, "method": "resources/list", "params": {}}
    )
    assert envelope is not None
    assert envelope["error"]["code"] == -32601


async def test_server_notifications_are_silently_acked(server: MockMCPServer) -> None:
    envelope = await server.handle_jsonrpc(
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
    )
    assert envelope is None


async def test_server_list_negotiable_services_respects_min_reputation(
    server: MockMCPServer,
) -> None:
    envelope = await server.handle_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "list_negotiable_services",
                "arguments": {"min_reputation": 0.85},
            },
        }
    )
    assert envelope is not None
    services = envelope["result"]["structuredContent"]["services"]
    assert all(s["reputation"] >= 0.85 for s in services)


# ---------------------------------------------------------------------------
# MCP client — parser unit tests
# ---------------------------------------------------------------------------


def test_parse_sse_body_extracts_last_data_frame() -> None:
    body = "event: ping\n\ndata: {\"jsonrpc\":\"2.0\",\"id\":1,\"result\":{\"ok\":true}}\n\n"
    parsed = _parse_sse_body(body)
    assert parsed == {"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}


def test_parse_sse_body_raises_when_no_data_frame() -> None:
    with pytest.raises(MCPError):
        _parse_sse_body("event: keepalive\n\n")


def test_mcp_tool_from_dict_handles_missing_schemas() -> None:
    tool = MCPTool.from_dict({"name": "foo", "description": "bar"})
    assert tool.name == "foo"
    assert tool.input_schema == {}
    assert tool.output_schema == {}


# ---------------------------------------------------------------------------
# MCP client ↔ mock server round-trip (via ASGI transport)
# ---------------------------------------------------------------------------


@pytest.fixture()
async def mcp_http_client() -> httpx.AsyncClient:
    app = build_starlette_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://mcp") as c:
        yield c


async def test_client_list_tools_against_mock_server(
    mcp_http_client: httpx.AsyncClient,
) -> None:
    async with MCPClient("http://mcp/mcp", client=mcp_http_client) as c:
        tools = await c.list_tools()
    names = {t.name for t in tools}
    assert "list_negotiable_services" in names
    assert "get_service_details" in names


async def test_client_call_tool_returns_structured_payload(
    mcp_http_client: httpx.AsyncClient,
) -> None:
    async with MCPClient("http://mcp/mcp", client=mcp_http_client) as c:
        result = await c.call_tool(
            "list_negotiable_services", {"capability": "weather-data"}
        )
    services = result.structured.get("services") or []
    assert len(services) == 1
    assert services[0]["capability"] == "weather-data"
    assert result.is_error is False


async def test_client_raises_mcp_error_on_bad_accept_header() -> None:
    app = build_starlette_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://mcp") as hc:
        resp = await hc.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
            headers={"Accept": "application/json"},  # missing text/event-stream
        )
    assert resp.status_code == 406
    body = resp.json()
    assert body["error"]["code"] == -32600


# ---------------------------------------------------------------------------
# DiscoveryService
# ---------------------------------------------------------------------------


async def test_discovery_service_finds_service_in_process() -> None:
    svc = DiscoveryService()
    result = await svc.discover_tool("weather-data")
    assert result.success
    assert result.service_id == "agent_LpzYVzWGzjGiZBI3HTm4ZCKj"
    assert result.mode == "in_process"
    assert "list_negotiable_services" in result.matched_tools


async def test_discovery_service_falls_back_when_live_mcp_unreachable() -> None:
    # Point at a non-existent endpoint — client will raise MCPError and
    # the service must quietly fall back to the mock path.
    svc = DiscoveryService(
        mcp_endpoint="http://127.0.0.1:1/mcp",
        mcp_auth_token="fake",
    )
    result = await svc.discover_tool("weather-data")
    assert result.success
    assert result.mode == "mock"
    assert result.live_path_error.startswith("live_failed")
    assert not result.error


async def test_discovery_service_returns_error_for_unknown_capability() -> None:
    svc = DiscoveryService()
    result = await svc.discover_tool("there-is-no-such-capability")
    assert not result.success
    assert "no_service_for_capability" in result.error


async def test_discovery_service_emits_events() -> None:
    events: list[tuple[str, dict[str, Any]]] = []

    async def cb(event_type: str, data: dict[str, Any]) -> None:
        events.append((event_type, data))

    svc = DiscoveryService(event_callback=cb)
    discovery = await svc.discover_tool("weather-data")
    await svc.verify_discovered_agent(discovery)

    event_types = [e[0] for e in events]
    assert event_types == [
        "discovery_started",
        "discovery_completed",
        "verification_started",
        "verification_completed",
    ]


async def test_verification_passes_for_high_reputation_service() -> None:
    svc = DiscoveryService(reputation_threshold=0.5)
    discovery = await svc.discover_tool("weather-data")
    verification = await svc.verify_discovered_agent(discovery)
    assert verification.passed
    assert verification.address_matches
    assert verification.reputation >= 0.5


async def test_verification_fails_when_threshold_exceeds_reputation() -> None:
    svc = DiscoveryService(reputation_threshold=0.99)
    discovery = await svc.discover_tool("news-feed")  # rep=0.72 < 0.99
    verification = await svc.verify_discovered_agent(discovery)
    assert not verification.reputation_passed
    assert not verification.passed


async def test_register_discovered_tool_persists_across_lookups() -> None:
    svc = DiscoveryService()
    await svc.register_discovered_tool(
        ServiceRecord(
            service_id="svc_freshly_registered",
            name="FreshService",
            description="",
            capability="freshly-registered",
            seller_address="0x" + "b" * 40,
            seller_agent_id=77,
            reservation_price=10.0,
            list_price=50.0,
            resource_url="/api/fresh",
            reputation=0.8,
        )
    )
    result = await svc.discover_tool("freshly-registered")
    assert result.success
    assert result.service_id == "svc_freshly_registered"


# ---------------------------------------------------------------------------
# Executor integration
# ---------------------------------------------------------------------------


async def test_executor_records_discovery_and_verification_metadata() -> None:
    discovery_service = DiscoveryService()

    buyer = AgentConfig(
        agent_id="b",
        address="0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18",
        role="buyer",
        initial_price=500.0,
        reservation_price=1200.0,
    )
    seller = AgentConfig(
        agent_id="s",
        address="0x209693Bc6412A8b3D23E1bF6E1d59EbFf95bC2cE",
        role="seller",
        initial_price=1500.0,
        reservation_price=800.0,
    )
    params = NegotiationParams(max_rounds=7, scope="weather-data")

    executor = NegotiationExecutor(
        discovery_service=discovery_service,
        discovery_capability="weather-data",
    )
    result = await executor.start_negotiation(buyer, seller, params)

    assert result.discovery is not None
    assert result.discovery["service_id"] == "agent_LpzYVzWGzjGiZBI3HTm4ZCKj"
    assert result.discovery["mode"] in {"in_process", "mock", "live"}
    assert result.verification is not None
    assert result.verification["passed"] is True
    # Executor ended in a terminal state.
    assert executor.state in {NegotiationState.COMPLETED, NegotiationState.FAILED}


async def test_executor_short_circuits_on_enforced_verification_failure() -> None:
    # Force verification to fail by setting threshold above all records.
    svc = DiscoveryService(reputation_threshold=0.99)
    executor = NegotiationExecutor(
        discovery_service=svc,
        discovery_capability="news-feed",
        enforce_verification=True,
    )
    buyer = AgentConfig(
        agent_id="b",
        address="0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18",
        role="buyer",
        initial_price=100.0,
        reservation_price=500.0,
    )
    seller = AgentConfig(
        agent_id="s",
        address="0x4e3Ab8d8e2c6e9c7D7b1aE4c4a0c3cEe67aA1122",
        role="seller",
        initial_price=800.0,
        reservation_price=200.0,
    )
    params = NegotiationParams(max_rounds=7, scope="news-feed")

    result = await executor.start_negotiation(buyer, seller, params)

    assert result.success is False
    assert result.reason == "verification_failed"
    assert result.total_rounds == 0
    assert result.verification is not None
    assert result.verification["passed"] is False
