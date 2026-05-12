"""REST API endpoints for NegotiatorGrid."""

from __future__ import annotations

import time
import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from negotiatorgrid.api.app_state import ledger
from negotiatorgrid.api.websocket import broadcaster
from negotiatorgrid.executors.negotiation import (
    AgentConfig,
    NegotiationExecutor,
    NegotiationParams,
    WireNegotiationResult,
)

router = APIRouter(prefix="/api")


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

    async def on_round(neg_id: str, neg_round: Any) -> None:
        await broadcaster.broadcast_round(neg_round.to_dict())

    async def on_result(result: WireNegotiationResult) -> None:
        await broadcaster.broadcast_result(result.to_dict())

    executor = NegotiationExecutor(on_round=on_round, on_result=on_result)
    ledger.mark_negotiating(negotiation_id)

    try:
        result = await executor.start_negotiation(
            buyer, seller, params, negotiation_id=negotiation_id
        )
        result_dict = result.to_dict()

        deal: dict[str, Any] | None = None
        if result.success:
            deal = {
                "deal_hash": result.deal_hash,
                "negotiation_id": negotiation_id,
                "agreed_price": result.agreed_price,
                "total_rounds": result.total_rounds,
                "buyer_agent": buyer.agent_id,
                "seller_agent": seller.agent_id,
                "buyer_wallet": buyer.address,
                "seller_wallet": seller.address,
                "buyer_utility": result.buyer_utility,
                "seller_utility": result.seller_utility,
                "metrics": result.metrics,
                "objective_mode": result.objective_mode,
                "passport_status": result.passport_status,
                "timestamp": time.time(),
                "settled": False,
                "attestation_tx": "",
            }

        ledger.record_completed_run(
            negotiation_id,
            success=result.success,
            result_dict=result_dict,
            total_rounds=result.total_rounds,
            deal=deal,
        )
    except Exception as exc:
        ledger.record_run_exception(negotiation_id, str(exc))


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
    ledger.create_submitted(
        negotiation_id,
        buyer_config=req.buyer_config.model_dump(),
        seller_config=req.seller_config.model_dump(),
        params=req.negotiation_params.model_dump(),
        created_at=time.time(),
    )

    background_tasks.add_task(_run_negotiation, negotiation_id, req)

    return NegotiateResponse(negotiation_id=negotiation_id, status="submitted")


@router.get("/negotiations")
async def list_negotiations() -> list[dict[str, Any]]:
    """List all negotiations with status."""
    return ledger.list_negotiation_summaries()


@router.get("/negotiations/{negotiation_id}")
async def get_negotiation(negotiation_id: str) -> dict[str, Any]:
    """Get negotiation detail with full transcript."""
    row = ledger.get_negotiation(negotiation_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    return row


@router.get("/deals")
async def list_deals() -> list[dict[str, Any]]:
    """List all completed deals."""
    return ledger.list_deals()


@router.get("/deals/{deal_hash}")
async def get_deal(deal_hash: str) -> dict[str, Any]:
    """Get deal detail by deal hash."""
    row = ledger.get_deal(deal_hash)
    if row is None:
        raise HTTPException(status_code=404, detail="Deal not found")
    return row


@router.get("/agents/{address}/reputation")
async def get_agent_reputation(address: str) -> dict[str, Any]:
    """Get agent reputation summary (mock)."""
    return ledger.reputation_summary(address)


@router.get("/stats")
async def get_stats() -> dict[str, Any]:
    """Dashboard aggregate stats."""
    return ledger.dashboard_stats()
