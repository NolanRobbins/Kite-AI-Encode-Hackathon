"""Unit tests for Passport runtime mode/status derivation."""

from __future__ import annotations

from types import SimpleNamespace

from negotiatorgrid import passport


def _cfg(
    *,
    mode: str = "mock",
    endpoint: str = "https://neo.dev.gokite.ai/v1/mcp",
    token: str = "",
    agent_id: str = "",
    session_id: str = "",
) -> SimpleNamespace:
    return SimpleNamespace(
        mcp=SimpleNamespace(endpoint=endpoint, auth_token=token),
        passport=SimpleNamespace(mode=mode, agent_id=agent_id, session_id=session_id),
    )


def test_mock_mode_resolves_stubbed(monkeypatch) -> None:
    monkeypatch.setattr(passport, "config", _cfg(mode="mock"))
    runtime = passport.resolve_passport_runtime()
    assert runtime.requested_mode == "mock"
    assert runtime.passport_status == "stubbed"


def test_live_mode_without_token_resolves_disabled(monkeypatch) -> None:
    monkeypatch.setattr(passport, "config", _cfg(mode="live", token=""))
    runtime = passport.resolve_passport_runtime()
    assert runtime.requested_mode == "live"
    assert runtime.passport_status == "disabled"
    assert "KITE_MCP_AUTH_TOKEN" in runtime.missing_requirements


def test_live_mode_with_token_resolves_ready(monkeypatch) -> None:
    monkeypatch.setattr(
        passport,
        "config",
        _cfg(mode="live", token="bearer-abc123"),
    )
    runtime = passport.resolve_passport_runtime()
    assert runtime.requested_mode == "live"
    assert runtime.passport_status == "ready"
    assert runtime.mcp_auth_configured is True


def test_live_mode_with_auth_embedded_in_endpoint_resolves_ready(monkeypatch) -> None:
    monkeypatch.setattr(
        passport,
        "config",
        _cfg(
            mode="live",
            endpoint="https://mcp.prod.gokite.ai/api_key_demo123/mcp",
            token="",
        ),
    )
    runtime = passport.resolve_passport_runtime()
    assert runtime.requested_mode == "live"
    assert runtime.passport_status == "ready"
    assert runtime.mcp_auth_configured is True


def test_explicit_non_stub_status_override_wins(monkeypatch) -> None:
    monkeypatch.setattr(passport, "config", _cfg(mode="mock"))
    assert passport.resolve_effective_passport_status("ready") == "ready"
    assert passport.resolve_effective_passport_status("disabled") == "disabled"
    assert passport.resolve_effective_passport_status("stubbed") == "stubbed"
