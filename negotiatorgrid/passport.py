"""Passport runtime helpers (mock/live mode + status derivation)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from urllib.parse import parse_qs, urlparse

from negotiatorgrid.config import config


def _norm(value: str) -> str:
    return (value or "").strip().lower()


def _endpoint_contains_embedded_auth(endpoint: str) -> bool:
    """Best-effort detection of auth embedded directly in MCP URL."""
    raw = (endpoint or "").strip()
    if not raw:
        return False
    low = raw.lower()
    if "api_key_" in low or "token=" in low or "auth=" in low:
        return True
    try:
        parsed = urlparse(raw)
    except Exception:
        return False
    if "@" in parsed.netloc:
        return True
    qs = parse_qs(parsed.query or "", keep_blank_values=True)
    auth_keys = {"token", "auth", "apikey", "api_key", "access_token", "key"}
    for key in auth_keys:
        vals = qs.get(key)
        if vals and any((v or "").strip() for v in vals):
            return True
    return False


@dataclass(frozen=True)
class PassportRuntime:
    """Derived runtime posture for Kite Agent Passport."""

    requested_mode: str = "mock"
    passport_status: str = "stubbed"
    mcp_endpoint: str = ""
    mcp_auth_configured: bool = False
    agent_id: str = ""
    session_id: str = ""
    missing_requirements: list[str] = field(default_factory=list)
    reason: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def resolve_passport_runtime() -> PassportRuntime:
    """Resolve Passport runtime mode from env-backed app config."""
    requested = _norm(config.passport.mode)
    if requested not in {"live", "mock"}:
        requested = "mock"

    endpoint = (config.mcp.endpoint or "").strip()
    token = (config.mcp.auth_token or "").strip()
    embedded_auth = _endpoint_contains_embedded_auth(endpoint)
    agent_id = (config.passport.agent_id or "").strip()
    session_id = (config.passport.session_id or "").strip()

    if requested == "mock":
        return PassportRuntime(
            requested_mode="mock",
            passport_status="stubbed",
            mcp_endpoint=endpoint,
            mcp_auth_configured=bool(token),
            agent_id=agent_id,
            session_id=session_id,
            reason="KITE_PASSPORT_MODE=mock (Passport-compatible demo mode).",
        )

    missing: list[str] = []
    if not endpoint:
        missing.append("KITE_MCP_ENDPOINT")
    if not token and not embedded_auth:
        missing.append("KITE_MCP_AUTH_TOKEN")

    if missing:
        return PassportRuntime(
            requested_mode="live",
            passport_status="disabled",
            mcp_endpoint=endpoint,
            mcp_auth_configured=bool(token or embedded_auth),
            agent_id=agent_id,
            session_id=session_id,
            missing_requirements=missing,
            reason=(
                "Live Passport requested but missing required settings: "
                + ", ".join(missing)
            ),
        )

    notes: list[str] = []
    if not agent_id:
        notes.append("KITE_PASSPORT_AGENT_ID not set")
    if not session_id:
        notes.append("KITE_PASSPORT_SESSION_ID not set")

    reason = "Live Passport configured (MCP endpoint + auth token present)."
    if embedded_auth and not token:
        reason = "Live Passport configured (auth appears embedded in MCP endpoint URL)."
    if notes:
        reason += " " + "; ".join(notes) + "."

    return PassportRuntime(
        requested_mode="live",
        passport_status="ready",
        mcp_endpoint=endpoint,
        mcp_auth_configured=bool(token or embedded_auth),
        agent_id=agent_id,
        session_id=session_id,
        reason=reason,
    )


def resolve_effective_passport_status(requested_status: str = "") -> str:
    """Compute final wire status while honoring explicit non-stub overrides."""
    explicit = _norm(requested_status)
    if explicit in {"ready", "disabled"}:
        return explicit
    runtime = resolve_passport_runtime()
    return runtime.passport_status
