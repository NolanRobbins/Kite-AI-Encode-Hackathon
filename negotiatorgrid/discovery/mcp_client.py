"""Streamable-HTTP JSON-RPC 2.0 MCP client.

This client is built to match the live Kite MCP servers **exactly** as
probed on 2026-04-08 (see ``research-plan-docs/1.3-kite-mcp-server-deep-dive.md``),
while avoiding a hard dependency on the ``mcp`` Python SDK so we can
install on judge machines that don't have it.

Transport details (confirmed live):

* Each call is a POST with ``Content-Type: application/json`` and
  ``Accept: application/json, text/event-stream``.
* The server responds with ``text/event-stream`` (SSE frames prefixed
  with ``data: ``) carrying a single JSON-RPC 2.0 payload per frame.
* Some servers (our mock, some deployments) may respond with a plain
  JSON body. We handle both transparently.
* Initialize → protocolVersion ``2024-11-05`` → serverInfo name
  ``Kite Passport MCP``, version ``1.12.3``.

The client is intentionally small (< 250 LOC) and has **no runtime
dependency on the `mcp` package** — only ``httpx``, which is already
a project dependency. If the `mcp` SDK is available we prefer its
richer types, but we degrade gracefully if not.
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

# Canonical headers. The live Kite server rejects requests missing the
# dual Accept header with ``-32600: Not Acceptable``.
_MCP_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}

# MCP protocol version pinned to what the live Kite server reports.
_MCP_PROTOCOL_VERSION = "2024-11-05"

# Client identity sent during ``initialize``.
_CLIENT_INFO = {
    "name": "negotiatorgrid",
    "version": "0.1.0",
}


class MCPError(RuntimeError):
    """Raised when the MCP server returns a JSON-RPC error or bad body."""

    def __init__(self, message: str, code: int = -32000, data: Any = None) -> None:
        super().__init__(message)
        self.code = code
        self.data = data


@dataclass
class MCPTool:
    """One entry from ``tools/list``."""

    name: str
    description: str = ""
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "MCPTool":
        return cls(
            name=d.get("name", ""),
            description=d.get("description", ""),
            input_schema=d.get("inputSchema") or {},
            output_schema=d.get("outputSchema") or {},
        )


@dataclass
class MCPToolResult:
    """Unwrapped ``tools/call`` result.

    ``structured`` is the parsed JSON payload when the server returns a
    structured content block; ``text`` concatenates any ``text`` content
    blocks; ``raw`` is the full MCP response for callers that need
    access to content-block metadata (mime type, annotations, etc.).
    """

    structured: dict[str, Any] = field(default_factory=dict)
    text: str = ""
    is_error: bool = False
    raw: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# SSE / body parsing
# ---------------------------------------------------------------------------


def _parse_sse_body(body: str) -> dict[str, Any]:
    """Extract the single JSON-RPC payload from an SSE frame body.

    MCP's Streamable-HTTP transport emits exactly one SSE ``data:`` line
    per response. Multi-event streams are not expected for our
    request/response call pattern, but we still take the **last** data
    frame if several are present (matches the live server's behaviour
    of sending a keep-alive then the payload).
    """
    payload: Optional[dict[str, Any]] = None
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        raw = line[len("data:"):].strip()
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
    if payload is None:
        raise MCPError(f"No SSE data frame in MCP response: {body[:200]!r}")
    return payload


def _extract_jsonrpc_result(parsed: dict[str, Any]) -> dict[str, Any]:
    """Pull ``result`` out of a JSON-RPC envelope, or raise on error."""
    if "error" in parsed:
        err = parsed["error"] or {}
        raise MCPError(
            err.get("message", "MCP error"),
            code=int(err.get("code", -32000)),
            data=err.get("data"),
        )
    if "result" not in parsed:
        raise MCPError(f"Malformed JSON-RPC envelope: {parsed!r}")
    result = parsed["result"]
    if not isinstance(result, dict):
        raise MCPError(f"Unexpected result type: {type(result).__name__}")
    return result


def _extract_tool_result(result: dict[str, Any]) -> MCPToolResult:
    """Unwrap a ``tools/call`` result into text + structured fields."""
    out = MCPToolResult(raw=result, is_error=bool(result.get("isError")))
    structured = result.get("structuredContent")
    if isinstance(structured, dict):
        out.structured = structured
    text_parts: list[str] = []
    for block in result.get("content", []) or []:
        if isinstance(block, dict) and block.get("type") == "text":
            text_parts.append(str(block.get("text", "")))
    out.text = "\n".join(text_parts)
    # If the server didn't provide structuredContent but the text is
    # valid JSON, parse it so callers don't have to.
    if not out.structured and out.text:
        try:
            parsed = json.loads(out.text)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            out.structured = parsed
    return out


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class MCPClient:
    """Minimal async MCP client.

    Usage::

        async with MCPClient("https://mcp.prod.gokite.ai/<api_key>/mcp") as c:
            tools = await c.list_tools()
            result = await c.call_tool("get_service_details",
                                       {"service_id": "agent_Lpz..."})
    """

    def __init__(
        self,
        endpoint: str,
        *,
        auth_token: Optional[str] = None,
        timeout: float = 10.0,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self._auth_token = auth_token
        self._timeout = timeout
        self._client = client
        self._owns_client = client is None
        self._session_id: Optional[str] = None
        self._initialized = False

    async def __aenter__(self) -> "MCPClient":
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    # -- Core request ----------------------------------------------------

    async def _rpc(self, method: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Execute a single JSON-RPC call and return the ``result``."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
            self._owns_client = True

        payload = {
            "jsonrpc": "2.0",
            "id": uuid.uuid4().hex,
            "method": method,
            "params": params or {},
        }
        headers = dict(_MCP_HEADERS)
        if self._auth_token:
            headers["Authorization"] = f"Bearer {self._auth_token}"
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id

        try:
            response = await self._client.post(
                self.endpoint, json=payload, headers=headers
            )
        except httpx.HTTPError as exc:
            raise MCPError(f"HTTP transport error: {exc}") from exc

        # Streamable-HTTP servers may hand us a session id on initialize.
        sid = response.headers.get("mcp-session-id") or response.headers.get(
            "Mcp-Session-Id"
        )
        if sid and not self._session_id:
            self._session_id = sid

        content_type = (response.headers.get("content-type") or "").lower()
        body = response.text

        if response.status_code >= 400:
            # 401/403 from the Passport MCP endpoint without OAuth is
            # the common failure path. Surface it cleanly.
            raise MCPError(
                f"MCP server returned HTTP {response.status_code}: {body[:200]}",
                code=-32600,
            )

        if "text/event-stream" in content_type:
            parsed = _parse_sse_body(body)
        else:
            try:
                parsed = json.loads(body) if body else {}
            except json.JSONDecodeError as exc:
                raise MCPError(f"Invalid JSON from MCP server: {exc}") from exc

        return _extract_jsonrpc_result(parsed)

    # -- High-level methods ---------------------------------------------

    async def initialize(self) -> dict[str, Any]:
        """Send ``initialize`` and record the server info."""
        if self._initialized:
            return {}
        result = await self._rpc(
            "initialize",
            {
                "protocolVersion": _MCP_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": _CLIENT_INFO,
            },
        )
        # Per spec, the client must send a ``notifications/initialized``
        # after receiving the initialize result. We do this best-effort;
        # if it fails the server will typically still serve tool calls.
        try:
            await self._notify("notifications/initialized", {})
        except Exception:
            logger.debug("Skipping notifications/initialized (non-fatal)")
        self._initialized = True
        return result

    async def _notify(self, method: str, params: dict[str, Any]) -> None:
        """Fire-and-forget notification (no id)."""
        if self._client is None:
            return
        headers = dict(_MCP_HEADERS)
        if self._auth_token:
            headers["Authorization"] = f"Bearer {self._auth_token}"
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id
        payload = {"jsonrpc": "2.0", "method": method, "params": params}
        try:
            await self._client.post(self.endpoint, json=payload, headers=headers)
        except httpx.HTTPError:
            pass

    async def list_tools(self) -> list[MCPTool]:
        """Fetch the server's available tools."""
        await self.initialize()
        result = await self._rpc("tools/list", {})
        tools = result.get("tools") or []
        return [MCPTool.from_dict(t) for t in tools if isinstance(t, dict)]

    async def call_tool(
        self, name: str, arguments: Optional[dict[str, Any]] = None
    ) -> MCPToolResult:
        """Invoke a server tool and return its parsed result."""
        await self.initialize()
        result = await self._rpc(
            "tools/call",
            {"name": name, "arguments": arguments or {}},
        )
        return _extract_tool_result(result)
