"""Agent + service discovery layer for NegotiatorGrid.

This package implements the "discover → verify → negotiate" autonomy
chain that powers the Day-3 wow moment (see
``research-plan-docs/1.3-kite-mcp-server-deep-dive.md`` and
``research-plan-docs/4.2-mcp-registries-x402-catalogs-research.md``).

Public surface:

* :class:`MCPClient` — Streamable-HTTP JSON-RPC 2.0 client compatible
  with Kite's live MCP servers (``mcp.prod.gokite.ai`` and
  ``neo.dev.gokite.ai``). Also talks to our in-process mock server.
* :class:`LocalRegistry` — In-process service catalog used as a
  fallback when the live Kite MCP is unreachable (which is the default
  during hackathon development, per ``current_tech_problems.md``).
* :class:`MockMCPServer` — Starlette-mountable handler exposing the
  exact Kite tool surface (`get_service_details`, `call_service`,
  `list_negotiable_services`) so the demo works without a Passport
  invite.
* :class:`DiscoveryService` — The high-level orchestrator used by
  :class:`NegotiationExecutor`. Does capability lookup → ERC-8004
  identity read → reputation gate → negotiation handoff.
"""

from negotiatorgrid.discovery.local_registry import (
    LocalRegistry,
    ServiceRecord,
)
from negotiatorgrid.discovery.mcp_client import (
    MCPClient,
    MCPError,
    MCPTool,
    MCPToolResult,
)
from negotiatorgrid.discovery.service import (
    DiscoveryResult,
    DiscoveryService,
    VerificationResult,
)

__all__ = [
    "MCPClient",
    "MCPError",
    "MCPTool",
    "MCPToolResult",
    "LocalRegistry",
    "ServiceRecord",
    "DiscoveryService",
    "DiscoveryResult",
    "VerificationResult",
]
