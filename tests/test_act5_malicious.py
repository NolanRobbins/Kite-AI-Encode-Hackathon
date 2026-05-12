"""Act 5 — malicious seller x402 inflation and payment refusal."""

from __future__ import annotations

import asyncio

import httpx
import pytest

from negotiatorgrid.api.server import app
from negotiatorgrid.core.settlement import DealHashMismatchError, X402Settler
from negotiatorgrid.executors.malicious_seller import (
    MALICIOUS_INFLATION_FACTOR,
    inflate_payment_requirements,
)


@pytest.fixture
def transport():
    return httpx.ASGITransport(app=app)


def test_inflate_payment_requirements_multiplies_atomic() -> None:
    settler = X402Settler()
    req = settler.create_payment_requirements(
        agreed_price=100_000,
        seller_wallet="0x209693Bc6412A8b3D23E1bF6E1d59EbFf95bC2cE",
        resource_url="/api/weather",
        deal_hash="0xabc",
    )
    bad = inflate_payment_requirements(req)
    assert int(bad["maxAmountRequired"]) == int(100_000 * MALICIOUS_INFLATION_FACTOR)


def test_verify_catches_inflated_requirements() -> None:
    settler = X402Settler()
    seller = "0x209693Bc6412A8b3D23E1bF6E1d59EbFf95bC2cE"
    honest = settler.create_payment_requirements(
        agreed_price=80_000,
        seller_wallet=seller,
        resource_url="/api/weather",
        deal_hash="0xdeadbeef",
    )
    malicious = inflate_payment_requirements(honest)
    with pytest.raises(DealHashMismatchError) as exc:
        settler.verify_payment_requirements(
            agreed_price_atomic=80_000,
            deal_hash="0xdeadbeef",
            seller_wallet=seller,
            resource_url="/api/weather",
            payment_requirements=malicious,
        )
    assert exc.value.actual_atomic == int(80_000 * MALICIOUS_INFLATION_FACTOR)


def test_verify_honest_requirements_ok() -> None:
    settler = X402Settler()
    seller = "0x209693Bc6412A8b3D23E1bF6E1d59EbFf95bC2cE"
    req = settler.create_payment_requirements(
        agreed_price=80_000,
        seller_wallet=seller,
        resource_url="/api/weather",
        deal_hash="0xabc123",
    )
    settler.verify_payment_requirements(
        agreed_price_atomic=80_000,
        deal_hash="0xabc123",
        seller_wallet=seller,
        resource_url="/api/weather",
        payment_requirements=req,
    )


@pytest.mark.asyncio
async def test_act5_endpoint_marks_payment_refused(transport: httpx.ASGITransport) -> None:
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        start = await c.post("/api/act5/malicious")
        assert start.status_code == 200
        neg_id = start.json()["negotiation_id"]

        deadline = 90.0
        while deadline > 0:
            await asyncio.sleep(0.3)
            r = await c.get(f"/api/negotiations/{neg_id}")
            assert r.status_code == 200
            body = r.json()
            if body.get("status") == "payment_refused":
                settle = body.get("settlement") or {}
                assert settle.get("payment_refused") is True
                assert settle.get("rejection_reason") == "price_manipulation"
                break
            deadline -= 0.3
        else:
            pytest.fail("negotiation did not reach payment_refused status")

        stats = await c.get("/api/stats")
        assert stats.json().get("rejected_payments", 0) >= 1
