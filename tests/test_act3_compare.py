"""Tests for the Act 3 side-by-side compare endpoint."""

from __future__ import annotations

import asyncio

import httpx
import pytest

from negotiatorgrid.api.server import app


@pytest.fixture
def transport():
    return httpx.ASGITransport(app=app)


@pytest.mark.asyncio
async def test_act3_compare_starts_two_negotiations(transport) -> None:
    async with httpx.AsyncClient(
        transport=transport, base_url="http://test"
    ) as c:
        resp = await c.post("/api/act3/compare", json={})

    assert resp.status_code == 200
    body = resp.json()
    assert "high_rep" in body and "low_rep" in body
    high_id = body["high_rep"]["negotiation_id"]
    low_id = body["low_rep"]["negotiation_id"]
    assert high_id != low_id
    assert body["high_rep"]["reputation_stars"] == 4.8
    assert body["low_rep"]["reputation_stars"] == 3.2


@pytest.mark.asyncio
async def test_act3_status_endpoint_returns_deltas_when_complete(transport) -> None:
    async with httpx.AsyncClient(
        transport=transport, base_url="http://test"
    ) as c:
        start = await c.post("/api/act3/compare", json={})
        assert start.status_code == 200
        high_id = start.json()["high_rep"]["negotiation_id"]
        low_id = start.json()["low_rep"]["negotiation_id"]

        # Poll the compare status up to ~15s for both to complete.
        deadline = 15.0
        status: dict = {}
        for _ in range(60):
            await asyncio.sleep(0.25)
            s = await c.get(f"/api/act3/compare/{high_id}/{low_id}")
            assert s.status_code == 200
            status = s.json()
            if status.get("both_complete"):
                break
            deadline -= 0.25

        assert status.get("both_complete") is True, (
            f"Expected both complete, got {status}"
        )
        assert status["high_rep"]["success"] is True
        assert status["low_rep"]["success"] is True
        # Low-rep buyer starts lower and concedes slower, so its agreed
        # price should be <= the high-rep agreed price.
        assert status["low_rep"]["agreed_price"] <= status["high_rep"]["agreed_price"]
        assert status["savings_abs"] >= 0.0
        assert 0.0 <= status["savings_pct"] <= 100.0


@pytest.mark.asyncio
async def test_act3_status_404_for_unknown_ids(transport) -> None:
    async with httpx.AsyncClient(
        transport=transport, base_url="http://test"
    ) as c:
        resp = await c.get("/api/act3/compare/neg-deadbeef/neg-cafebabe")
    assert resp.status_code == 404
