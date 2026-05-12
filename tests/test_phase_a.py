"""Phase A hardening: deal_hash in extras, reputation by wallet, CORS."""

from __future__ import annotations

import httpx
import pytest

from negotiatorgrid.api.server import app
from negotiatorgrid.core.settlement import DealHashMismatchError, X402Settler


@pytest.fixture
def transport():
    return httpx.ASGITransport(app=app)


def test_verify_requires_deal_hash_in_extra_when_negotiation_has_hash() -> None:
    settler = X402Settler()
    seller = "0x209693Bc6412A8b3D23E1bF6E1d59EbFf95bC2cE"
    req = settler.create_payment_requirements(
        agreed_price=80_000,
        seller_wallet=seller,
        resource_url="/api/weather",
        deal_hash="0xabc123",
    )
    extra = dict(req.get("extra") or {})
    extra.pop("deal_hash", None)
    bad = {**req, "extra": extra}
    with pytest.raises(DealHashMismatchError) as exc:
        settler.verify_payment_requirements(
            agreed_price_atomic=80_000,
            deal_hash="0xabc123",
            seller_wallet=seller,
            resource_url="/api/weather",
            payment_requirements=bad,
        )
    assert exc.value.field == "deal_hash"


def test_verify_skips_deal_hash_requirement_when_negotiation_hash_empty() -> None:
    settler = X402Settler()
    seller = "0x209693Bc6412A8b3D23E1bF6E1d59EbFf95bC2cE"
    req = settler.create_payment_requirements(
        agreed_price=80_000,
        seller_wallet=seller,
        resource_url="/api/weather",
        deal_hash="",
    )
    settler.verify_payment_requirements(
        agreed_price_atomic=80_000,
        deal_hash="",
        seller_wallet=seller,
        resource_url="/api/weather",
        payment_requirements=req,
    )


@pytest.mark.asyncio
async def test_reputation_matches_buyer_wallet(
    transport: httpx.ASGITransport, monkeypatch: pytest.MonkeyPatch
) -> None:
    from negotiatorgrid.api import routes

    wallet = "0x742d35Cc6634C0532925a3b844Bc9e7595bD1811"
    monkeypatch.setattr(
        routes.ledger,
        "_deals",
        {
            "0xdeals1": {
                "deal_hash": "0xdeals1",
                "buyer_wallet": wallet,
                "seller_wallet": "0x2096c34E1F3B4aA7C5f8dE90b6cA42Ef1d2cE4A2",
                "buyer_agent": "buyer-test",
                "seller_agent": "seller-test",
                "agreed_price": 0.12,
            }
        },
    )
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.get(f"/api/agents/{wallet.lower()}/reputation")
        assert r.status_code == 200
        body = r.json()
        assert body["total_deals"] == 1
        assert body["average_price"] == 0.12


@pytest.mark.asyncio
async def test_reputation_still_matches_agent_id(
    transport: httpx.ASGITransport, monkeypatch: pytest.MonkeyPatch
) -> None:
    from negotiatorgrid.api import routes

    monkeypatch.setattr(
        routes.ledger,
        "_deals",
        {
            "0xdeals2": {
                "deal_hash": "0xdeals2",
                "buyer_wallet": "0x1111111111111111111111111111111111111111",
                "seller_wallet": "0x2222222222222222222222222222222222222222",
                "buyer_agent": "unique-buyer-agent-id",
                "seller_agent": "unique-seller",
                "agreed_price": 0.05,
            }
        },
    )
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.get("/api/agents/unique-buyer-agent-id/reputation")
        assert r.status_code == 200
        assert r.json()["total_deals"] == 1
