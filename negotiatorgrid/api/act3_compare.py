"""Act 3 side-by-side compare: high-reputation vs low-reputation buyer scenarios."""

from __future__ import annotations

import threading
import time
import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException

from negotiatorgrid.api.app_state import ledger
from negotiatorgrid.api.routes import (
    AgentConfigSchema,
    NegotiateRequest,
    NegotiationParamsSchema,
    _run_negotiation,
)

router = APIRouter(prefix="/api/act3", tags=["act3"])

# Display stars (demo UX); engine uses separate price parameters below.
HIGH_REP_STARS = 4.8
LOW_REP_STARS = 3.2

_pairs_lock = threading.Lock()
# (high_rep_negotiation_id, low_rep_negotiation_id) as returned from POST /compare
_compare_pairs: set[tuple[str, str]] = set()


def _negotiation_id() -> str:
    return f"neg-{uuid.uuid4().hex[:8]}"


def _shared_params() -> NegotiationParamsSchema:
    return NegotiationParamsSchema(
        max_rounds=7,
        timeout_seconds=30,
        resource_uri="/api/act3/service",
        scope="compare-demo",
        objective_mode="fairness_guardrail",
        passport_status="stubbed",
        model_mode="policy_only",
    )


def _high_rep_scenario() -> NegotiateRequest:
    """Cooperative high-trust buyer; tends to settle at a higher price."""
    return NegotiateRequest(
        buyer_config=AgentConfigSchema(
            agent_id="act3-high-rep-buyer",
            address="0x1000000000000000000000000000000000000001",
            reputation_score=92.0,
            reservation_price=0.20,
            initial_price=0.11,
            strategy="aspiration",
            concession_rate=0.06,
            tendency="cooperative",
            grid_enabled=True,
        ),
        seller_config=AgentConfigSchema(
            agent_id="act3-seller-a",
            address="0x2000000000000000000000000000000000000002",
            reservation_price=0.13,
            initial_price=0.17,
            strategy="boulware",
            concession_rate=0.04,
            tendency="dominant",
            grid_enabled=True,
        ),
        negotiation_params=_shared_params(),
    )


def _low_rep_scenario() -> NegotiateRequest:
    """Cautious low-trust buyer; holds opening low and walks away with a lower price."""
    return NegotiateRequest(
        buyer_config=AgentConfigSchema(
            agent_id="act3-low-rep-buyer",
            address="0x3000000000000000000000000000000000000003",
            reputation_score=28.0,
            reservation_price=0.12,
            initial_price=0.035,
            strategy="boulware",
            concession_rate=0.03,
            tendency="dominant",
            grid_enabled=True,
        ),
        seller_config=AgentConfigSchema(
            agent_id="act3-seller-b",
            address="0x4000000000000000000000000000000000000004",
            reservation_price=0.095,
            initial_price=0.115,
            strategy="aspiration",
            concession_rate=0.05,
            tendency="balanced",
            grid_enabled=True,
        ),
        negotiation_params=_shared_params(),
    )


def _summarize_leg(negotiation_id: str, *, reputation_stars: float | None) -> dict[str, Any]:
    row = ledger.get_negotiation(negotiation_id)
    if row is None:
        return {"negotiation_id": negotiation_id, "status": "unknown"}
    out: dict[str, Any] = {
        "negotiation_id": negotiation_id,
        "status": row.get("status", "unknown"),
    }
    if reputation_stars is not None:
        out["reputation_stars"] = reputation_stars
    if row.get("status") in ("completed", "failed"):
        res = row.get("result") or {}
        out["success"] = bool(res.get("success"))
        out["agreed_price"] = float(res.get("agreed_price") or 0.0)
    return out


@router.post("/compare")
async def start_compare(background_tasks: BackgroundTasks) -> dict[str, Any]:
    """Start two parallel negotiations: high-rep vs low-rep buyer framing."""
    high_id = _negotiation_id()
    low_id = _negotiation_id()
    while low_id == high_id:
        low_id = _negotiation_id()

    req_high = _high_rep_scenario()
    req_low = _low_rep_scenario()

    now = time.time()
    ledger.create_submitted(
        high_id,
        buyer_config=req_high.buyer_config.model_dump(),
        seller_config=req_high.seller_config.model_dump(),
        params=req_high.negotiation_params.model_dump(),
        created_at=now,
    )
    ledger.create_submitted(
        low_id,
        buyer_config=req_low.buyer_config.model_dump(),
        seller_config=req_low.seller_config.model_dump(),
        params=req_low.negotiation_params.model_dump(),
        created_at=now,
    )

    with _pairs_lock:
        _compare_pairs.add((high_id, low_id))

    background_tasks.add_task(_run_negotiation, high_id, req_high)
    background_tasks.add_task(_run_negotiation, low_id, req_low)

    return {
        "high_rep": {
            "negotiation_id": high_id,
            "reputation_stars": HIGH_REP_STARS,
        },
        "low_rep": {
            "negotiation_id": low_id,
            "reputation_stars": LOW_REP_STARS,
        },
    }


@router.get("/compare/{high_id}/{low_id}")
async def compare_status(high_id: str, low_id: str) -> dict[str, Any]:
    """Poll negotiation status for a compare pair started via POST /compare."""
    with _pairs_lock:
        valid = (high_id, low_id) in _compare_pairs
    if not valid:
        raise HTTPException(status_code=404, detail="Unknown compare pair")

    if ledger.get_negotiation(high_id) is None or ledger.get_negotiation(low_id) is None:
        raise HTTPException(status_code=404, detail="Negotiation not found")

    high = _summarize_leg(high_id, reputation_stars=None)
    low = _summarize_leg(low_id, reputation_stars=None)

    both_complete = (
        high.get("status") in ("completed", "failed")
        and low.get("status") in ("completed", "failed")
    )

    body: dict[str, Any] = {
        "both_complete": both_complete,
        "high_rep": high,
        "low_rep": low,
    }

    if both_complete:
        hp = float(high.get("agreed_price") or 0.0)
        lp = float(low.get("agreed_price") or 0.0)
        savings_abs = max(0.0, hp - lp)
        savings_pct = (savings_abs / hp * 100.0) if hp > 0 else 0.0
        body["savings_abs"] = round(savings_abs, 8)
        body["savings_pct"] = round(min(100.0, max(0.0, savings_pct)), 4)

    return body
