"""REST API endpoints for NegotiatorGrid."""

from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from negotiatorgrid.executors.negotiation import (
    AgentConfig,
    NegotiationExecutor,
    NegotiationParams,
    NegotiationResult,
    NegotiationState,
)
from negotiatorgrid.api.websocket import broadcaster

router = APIRouter(prefix="/api")

# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------

_negotiations: dict[str, dict[str, Any]] = {}
_deals: dict[str, dict[str, Any]] = {}
_stats = {
    "total_negotiations": 0,
    "total_deals": 0,
    "total_rounds": 0,
    "total_volume": 0.0,
}

# Shared executor instance
_executor = NegotiationExecutor()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class AgentConfigSchema(BaseModel):
    agent_id: str = ""
    address: str = "0x0000000000000000000000000000000000000000"
    role: str = "buyer"
    reservation_price: float = 0.10
    initial_price: float = 0.05
    strategy: str = "aspiration"
    concession_rate: float = 0.05
    reputation_score: float = 50.0
    grid_enabled: bool = True
    tendency: str = ""


class NegotiationParamsSchema(BaseModel):
    max_rounds: int = Field(default=7, ge=1, le=50)
    timeout_seconds: int = Field(default=30, ge=5, le=300)
    resource_uri: str = "/api/service"
    scope: str = "weather-data"
    objective_mode: str = "fairness_guardrail"
    passport_status: str = "stubbed"
    model_mode: str = "policy_only"
    model_provider: str = "template"
    model_name: str = "template"
    model_latency_budget_ms: int = Field(default=1200, ge=100, le=30000)


class NegotiateRequest(BaseModel):
    buyer_config: AgentConfigSchema = Field(default_factory=AgentConfigSchema)
    seller_config: AgentConfigSchema = Field(default_factory=AgentConfigSchema)
    negotiation_params: NegotiationParamsSchema = Field(default_factory=NegotiationParamsSchema)


class NegotiateResponse(BaseModel):
    negotiation_id: str
    status: str


# ---------------------------------------------------------------------------
# Background task runner
# ---------------------------------------------------------------------------

async def _run_negotiation(negotiation_id: str, req: NegotiateRequest) -> None:
    """Run the negotiation engine in the background."""
    buyer = AgentConfig(
        agent_id=req.buyer_config.agent_id or f"buyer-{uuid.uuid4().hex[:6]}",
        address=req.buyer_config.address,
        role="buyer",
        reservation_price=req.buyer_config.reservation_price,
        initial_price=req.buyer_config.initial_price,
        strategy=req.buyer_config.strategy,
        concession_rate=req.buyer_config.concession_rate,
        reputation_score=req.buyer_config.reputation_score,
        grid_enabled=req.buyer_config.grid_enabled,
        tendency=req.buyer_config.tendency,
    )
    seller = AgentConfig(
        agent_id=req.seller_config.agent_id or f"seller-{uuid.uuid4().hex[:6]}",
        address=req.seller_config.address,
        role="seller",
        reservation_price=req.seller_config.reservation_price,
        initial_price=req.seller_config.initial_price,
        strategy=req.seller_config.strategy,
        concession_rate=req.seller_config.concession_rate,
        reputation_score=req.seller_config.reputation_score,
        grid_enabled=req.seller_config.grid_enabled,
        tendency=req.seller_config.tendency,
    )
    params = NegotiationParams(
        max_rounds=req.negotiation_params.max_rounds,
        timeout_seconds=req.negotiation_params.timeout_seconds,
        resource_uri=req.negotiation_params.resource_uri,
        scope=req.negotiation_params.scope,
        objective_mode=req.negotiation_params.objective_mode,
        passport_status=req.negotiation_params.passport_status,
        model_mode=req.negotiation_params.model_mode,
        model_provider=req.negotiation_params.model_provider,
        model_name=req.negotiation_params.model_name,
        model_latency_budget_ms=req.negotiation_params.model_latency_budget_ms,
    )

    # Wire up broadcaster callbacks
    async def on_round(neg_id: str, neg_round: Any) -> None:
        await broadcaster.broadcast_round(neg_round.to_dict())

    async def on_result(result: NegotiationResult) -> None:
        await broadcaster.broadcast_result(result.to_dict())

    executor = NegotiationExecutor(on_round=on_round, on_result=on_result)
    _negotiations[negotiation_id]["status"] = "negotiating"

    try:
        result = await executor.start_negotiation(buyer, seller, params)
        result_dict = result.to_dict()
        result_dict["negotiation_id"] = negotiation_id
        _negotiations[negotiation_id].update({
            "status": "completed" if result.success else "failed",
            "result": result_dict,
        })
        _stats["total_rounds"] += result.total_rounds

        if result.success:
            deal = {
                "deal_hash": result.deal_hash,
                "negotiation_id": negotiation_id,
                "agreed_price": result.agreed_price,
                "total_rounds": result.total_rounds,
                "buyer_agent": buyer.agent_id,
                "seller_agent": seller.agent_id,
                "buyer_utility": result.buyer_utility,
                "seller_utility": result.seller_utility,
                "metrics": result.metrics,
                "objective_mode": result.objective_mode,
                "passport_status": result.passport_status,
                "timestamp": time.time(),
                "settled": False,
                "attestation_tx": "",
            }
            _deals[result.deal_hash] = deal
            _stats["total_deals"] += 1
            _stats["total_volume"] += result.agreed_price
    except Exception as exc:
        _negotiations[negotiation_id]["status"] = "failed"
        _negotiations[negotiation_id]["error"] = str(exc)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check."""
    return {
        "status": "ok",
        "service": "NegotiatorGrid",
        "version": "0.1.0",
        "ws_clients": broadcaster.client_count,
    }


@router.post("/negotiate", response_model=NegotiateResponse)
async def start_negotiation(req: NegotiateRequest, background_tasks: BackgroundTasks) -> NegotiateResponse:
    """Trigger a new bilateral negotiation."""
    negotiation_id = f"neg-{uuid.uuid4().hex[:8]}"
    _negotiations[negotiation_id] = {
        "negotiation_id": negotiation_id,
        "status": "submitted",
        "buyer_config": req.buyer_config.model_dump(),
        "seller_config": req.seller_config.model_dump(),
        "params": req.negotiation_params.model_dump(),
        "created_at": time.time(),
        "result": None,
    }
    _stats["total_negotiations"] += 1

    background_tasks.add_task(_run_negotiation, negotiation_id, req)

    return NegotiateResponse(negotiation_id=negotiation_id, status="submitted")


@router.get("/negotiations")
async def list_negotiations() -> list[dict[str, Any]]:
    """List all negotiations with status."""
    return [
        {
            "negotiation_id": nid,
            "status": data["status"],
            "created_at": data.get("created_at"),
        }
        for nid, data in _negotiations.items()
    ]


@router.get("/negotiations/{negotiation_id}")
async def get_negotiation(negotiation_id: str) -> dict[str, Any]:
    """Get negotiation detail with full transcript."""
    if negotiation_id not in _negotiations:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    return _negotiations[negotiation_id]


@router.get("/deals")
async def list_deals() -> list[dict[str, Any]]:
    """List all completed deals."""
    return list(_deals.values())


@router.get("/deals/{deal_hash}")
async def get_deal(deal_hash: str) -> dict[str, Any]:
    """Get deal detail by deal hash."""
    if deal_hash not in _deals:
        raise HTTPException(status_code=404, detail="Deal not found")
    return _deals[deal_hash]


@router.get("/agents/{address}/reputation")
async def get_agent_reputation(address: str) -> dict[str, Any]:
    """Get agent reputation summary (mock)."""
    agent_deals = [d for d in _deals.values() if address in (d.get("buyer_agent", ""), d.get("seller_agent", ""))]
    total = len(agent_deals)
    avg_price = sum(d["agreed_price"] for d in agent_deals) / total if total else 0
    return {
        "address": address,
        "total_deals": total,
        "average_price": round(avg_price, 6),
        "reputation_score": min(100, 50 + total * 5),
        "positive_feedback": total,
        "negative_feedback": 0,
    }


@router.get("/stats")
async def get_stats() -> dict[str, Any]:
    """Dashboard aggregate stats."""
    avg_rounds = _stats["total_rounds"] / max(_stats["total_negotiations"], 1)
    return {
        "total_negotiations": _stats["total_negotiations"],
        "total_deals": _stats["total_deals"],
        "avg_rounds": round(avg_rounds, 1),
        "total_volume": round(_stats["total_volume"], 6),
        "passport_status": "stubbed",
    }
