"""REST API endpoints for NegotiatorGrid."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Any

import httpx
from eth_account import Account
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from negotiatorgrid.api.app_state import ledger
from negotiatorgrid.api.websocket import broadcaster
from negotiatorgrid.config import config as kite_config
from negotiatorgrid.core.reputation import ReputationFeed
from negotiatorgrid.discovery.service import DiscoveryService
from negotiatorgrid.executors.negotiation import (
    AgentConfig,
    NegotiationExecutor,
    NegotiationParams,
    WireNegotiationResult,
)
from negotiatorgrid.passport import (
    resolve_effective_passport_status,
    resolve_passport_runtime,
)
from negotiatorgrid.post_negotiation import SettlementInfo, build_clients, complete_deal_after_negotiation
from negotiatorgrid.surprise_live_settlement import (
    NVDA_ROUTE,
    execute_nvda_post_negotiation,
    fetch_agent_json,
    surprise_base_url,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

_ACT5_BUYER_ADDRESS = "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18"
_ACT5_SELLER_ADDRESS = "0x209693Bc6412A8b3D23E1bF6E1d59EbFf95bC2cE"


def _discovery_stage_payload(event_type: str, data: dict[str, Any]) -> dict[str, Any] | None:
    if event_type == "discovery_started":
        endpoint = data.get("mcp_endpoint") or "local://mock"
        return {
            "phase": "discover",
            "title": "Passport MCP discovery",
            "detail": f"Capability={data.get('capability', '')} via {endpoint}",
        }
    if event_type == "discovery_completed":
        if data.get("success"):
            return {
                "phase": "discover",
                "title": "Service discovered",
                "detail": (
                    f"mode={data.get('mode')} service={data.get('service_id')} "
                    f"seller={data.get('seller_address')}"
                ),
            }
        return {
            "phase": "discover",
            "title": "Discovery fallback",
            "detail": str(data.get("error") or data.get("live_path_error") or "no service"),
        }
    if event_type == "verification_started":
        return {
            "phase": "verify",
            "title": "ERC-8004 + reputation checks",
            "detail": f"agent_id={data.get('agent_id')} wallet={data.get('claimed_address')}",
        }
    if event_type == "verification_completed":
        return {
            "phase": "verify",
            "title": "Verification result",
            "detail": (
                f"passed={data.get('passed')} rep={data.get('reputation')} "
                f"mode={data.get('mode')}"
            ),
        }
    return None


def _build_discovery_service() -> DiscoveryService:
    runtime = resolve_passport_runtime()
    live_enabled = runtime.passport_status == "ready"
    clients = build_clients()
    feed = ReputationFeed(clients.reputation, clients.deal_record)

    async def _event_callback(event_type: str, data: dict[str, Any]) -> None:
        payload = _discovery_stage_payload(event_type, data)
        if payload is None:
            return
        await broadcaster.broadcast_event("pipeline_stage", payload)

    return DiscoveryService(
        mcp_endpoint=runtime.mcp_endpoint if live_enabled else "",
        mcp_auth_token=(kite_config.mcp.auth_token or "").strip() if live_enabled else "",
        identity_client=clients.identity,
        reputation_feed=feed,
        event_callback=_event_callback,
    )


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class AgentConfigSchema(BaseModel):
    agent_id: str = ""
    address: str = "0x0000000000000000000000000000000000000000"
    role: str = "buyer"
    reservation_price: float = 0.10  # Will be adjusted based on role if not explicitly set
    initial_price: float = 0.05
    strategy: str = "aspiration"
    concession_rate: float = 0.05
    reputation_score: float = 50.0
    grid_enabled: bool = True
    tendency: str = ""
    malicious_seller: bool = False
    seller_agent_id: int = 0

    def model_post_init(self, __context: Any) -> None:
        """Adjust defaults based on role if not explicitly set."""
        # If using placeholder address, derive from config private key for buyer
        if self.address == "0x0000000000000000000000000000000000000000":
            if self.role == "buyer" and kite_config.kite.private_key:
                from eth_account import Account
                self.address = Account.from_key(kite_config.kite.private_key).address
            elif self.role == "seller":
                # Use a deterministic seller placeholder (not 0x000... to avoid validation errors)
                self.address = "0xa7C52Bd9E51E6c49aB2F0aB30c57Bb24aB1B91B7"  # Surprise API seller

        # If using default 0.10, apply role-aware defaults
        # Buyer reservation: max willing to pay (higher)
        # Seller reservation: min willing to accept (lower)
        if self.reservation_price == 0.10:
            if self.role == "buyer":
                self.reservation_price = 0.030  # Buyer's walk-away ceiling
            elif self.role == "seller":
                self.reservation_price = 0.022  # Seller's walk-away floor

        # Similarly adjust initial_price if at default
        if self.initial_price == 0.05:
            if self.role == "buyer":
                self.initial_price = 0.020  # Buyer opens low
            elif self.role == "seller":
                self.initial_price = 0.030  # Seller opens high (at list price)


class NegotiationParamsSchema(BaseModel):
    max_rounds: int = Field(default=12, ge=1, le=50)  # Increased from 7 to 12 for better mode/grid visibility
    timeout_seconds: int = Field(default=30, ge=5, le=300)
    resource_uri: str = "/api/service"
    scope: str = "weather-data"
    objective_mode: str = "fairness_guardrail"
    passport_status: str = "stubbed"
    model_mode: str = "policy_only"
    model_provider: str = "template"
    model_name: str = "template"
    model_latency_budget_ms: int = Field(default=1200, ge=100, le=30000)
    #: ``nvda_surprise_live`` — same pipeline as ``demo.py`` (Surprise API + Kite).
    scenario: str = ""
    #: ``legacy`` (text fingerprint) or ``canonical_eip712`` (DealRecord-aligned).
    deal_binding_mode: str = "legacy"


class NegotiateRequest(BaseModel):
    buyer_config: AgentConfigSchema = Field(default_factory=AgentConfigSchema)
    seller_config: AgentConfigSchema = Field(default_factory=AgentConfigSchema)
    negotiation_params: NegotiationParamsSchema = Field(default_factory=NegotiationParamsSchema)


class NegotiateResponse(BaseModel):
    negotiation_id: str
    status: str


# ---------------------------------------------------------------------------
# Post-negotiation (async settlement)
# ---------------------------------------------------------------------------


async def _merge_settlement_into_ledger(
    negotiation_id: str,
    result: WireNegotiationResult,
    info: SettlementInfo,
) -> None:
    """Attach settlement / attestation fields to the ledger deal row."""
    if not result.deal_hash:
        return
    if info.payment_refused:
        settlement_status = "refused"
    elif info.pipeline_error:
        settlement_status = "error"
    else:
        settlement_status = "completed"
    ledger.record_settlement(
        negotiation_id,
        result.deal_hash,
        {
            "settled": info.settled,
            "attestation_tx": info.attestation_tx,
            "attestation_deal_hash": info.attestation_deal_hash,
            "x402_tx_hash": info.x402_tx_hash,
            "x402_network": info.x402_network,
            "pipeline_error": info.pipeline_error,
            "mock_mode": info.mock_mode,
            "kitescan_tx_url": info.kitescan_tx_url,
            "kitescan_attestation_url": info.kitescan_attestation_url,
            "payment_refused": info.payment_refused,
            "rejection_reason": info.rejection_reason,
            "settlement_status": settlement_status,
            "settlement_completed_at": time.time(),
        },
    )


async def _run_post_negotiation_and_merge_deal(
    negotiation_id: str,
    result: WireNegotiationResult,
    buyer: AgentConfig,
    seller: AgentConfig,
    resource_uri: str,
) -> None:
    """Background: x402 + attestation, then merge into ledger deal row."""
    try:
        info = await complete_deal_after_negotiation(
            result,
            buyer,
            seller,
            notify=broadcaster.broadcast_event,
            resource_uri=resource_uri,
        )
    except Exception:
        logger.exception(
            "post-negotiation settlement failed negotiation_id=%s", negotiation_id
        )
        return
    await _merge_settlement_into_ledger(negotiation_id, result, info)


# ---------------------------------------------------------------------------
# NVDA + Surprise API — same orchestration as ``demo.py`` for the dashboard
# ---------------------------------------------------------------------------


async def _run_nvda_surprise_live_dashboard(negotiation_id: str, req: NegotiateRequest) -> None:
    """Discover → reputation snapshot → NegMAS → Surprise x402 + DealRecord."""
    ledger.mark_negotiating(negotiation_id)

    async def notify(event: str, payload: dict[str, Any]) -> None:
        event_payload = dict(payload)
        event_payload.setdefault("negotiation_id", negotiation_id)
        await broadcaster.broadcast_event(event, event_payload)

    if not kite_config.kite.private_key:
        await notify("error", {"message": "PRIVATE_KEY required for live NVDA + Surprise demo"})
        ledger.record_run_exception(negotiation_id, "missing_private_key")
        return

    buyer_wallet = Account.from_key(kite_config.kite.private_key).address
    base = surprise_base_url()

    try:
        async with httpx.AsyncClient() as http_client:
            try:
                await http_client.post(f"{base}/admin/reset", timeout=5.0)
            except Exception:
                logger.debug("surprise_api /admin/reset failed (non-fatal)", exc_info=True)

            await notify(
                "pipeline_stage",
                {
                    "phase": "discover",
                    "title": "A2A discovery",
                    "detail": f"GET {base}/.well-known/agent.json",
                },
            )
            card = await fetch_agent_json(http_client, base)
            reg0 = card.get("registrations") or [{}]
            reg = reg0[0] if isinstance(reg0, list) else {}
            advertised_seller = str(reg.get("agentAddress") or "")
            advertised_id = int(reg.get("agentId") or 0)

            await notify(
                "pipeline_stage",
                {
                    "phase": "identity",
                    "title": "ERC-8004 seller registration",
                    "wallet": advertised_seller,
                    "advertised_agent_id": advertised_id,
                },
            )

            clients = build_clients()
            identity = clients.identity
            onchain_seller_id = await identity.register_agent(
                f"https://surprise.negotiatorgrid.dev/agents/{advertised_id}.json",
                metadata={"role": "seller", "service": "surprise-api"},
            )
            if onchain_seller_id <= 0:
                onchain_seller_id = advertised_id or 1
            await identity.set_agent_wallet(onchain_seller_id, advertised_seller)

            feed = ReputationFeed(clients.reputation, clients.deal_record)
            profile = feed.get_agent_reputation(advertised_seller)
            rep_score = float(getattr(profile, "reputation_score", 0.85))
            await notify(
                "pipeline_stage",
                {
                    "phase": "reputation",
                    "title": "ReputationRegistry",
                    "score": rep_score,
                },
            )

            buyer = AgentConfig(
                agent_id=buyer_wallet,
                address=buyer_wallet,
                role="buyer",
                reservation_price=0.03,
                initial_price=0.01,
                strategy="aspiration",
                concession_rate=0.05,
                reputation_score=50.0,
                grid_enabled=True,
                tendency="balanced",
            )
            seller = AgentConfig(
                agent_id=str(onchain_seller_id),
                address=advertised_seller,
                role="seller",
                reservation_price=0.022,
                initial_price=0.03,
                strategy="aspiration",
                concession_rate=0.05,
                reputation_score=78.0,
                grid_enabled=True,
                tendency="balanced",
                malicious_seller=False,
                seller_agent_id=onchain_seller_id,
            )
            passport_status = resolve_effective_passport_status(
                req.negotiation_params.passport_status
            )
            params = NegotiationParams(
                max_rounds=req.negotiation_params.max_rounds,
                timeout_seconds=req.negotiation_params.timeout_seconds,
                resource_uri=NVDA_ROUTE,
                scope="nvda-market-data",
                objective_mode=req.negotiation_params.objective_mode,
                passport_status=passport_status,
                model_mode=req.negotiation_params.model_mode,
                model_provider=req.negotiation_params.model_provider,
                model_name=req.negotiation_params.model_name,
                model_latency_budget_ms=req.negotiation_params.model_latency_budget_ms,
                deal_binding_mode="canonical_eip712",
            )

            async def on_round(neg_id: str, neg_round: Any) -> None:
                payload = neg_round.to_dict()
                payload["negotiation_id"] = neg_id
                await broadcaster.broadcast_round(payload)

            async def on_result(result: WireNegotiationResult) -> None:
                await broadcaster.broadcast_result(result.to_dict())

            executor = NegotiationExecutor(on_round=on_round, on_result=on_result)
            await notify(
                "pipeline_stage",
                {
                    "phase": "negotiate",
                    "title": "Bilateral negotiation (NegMAS)",
                    "detail": "NVDA micro-payment price barter",
                },
            )
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
                    "settlement_status": "pending",
                }

            ledger.record_completed_run(
                negotiation_id,
                success=result.success,
                result_dict=result_dict,
                total_rounds=result.total_rounds,
                deal=deal,
            )

            if result.success and deal is not None:
                account = Account.from_key(kite_config.kite.private_key)
                info = await execute_nvda_post_negotiation(
                    http_client=http_client,
                    exec_result=result,
                    buyer_cfg=buyer,
                    seller_cfg=seller,
                    seller_wallet=advertised_seller,
                    onchain_seller_agent_id=onchain_seller_id,
                    buyer_account=account,
                    notify=notify,
                    resource_uri=NVDA_ROUTE,
                )
                await _merge_settlement_into_ledger(negotiation_id, result, info)
    except Exception as exc:
        logger.exception("nvda_surprise_live dashboard failed")
        ledger.record_run_exception(negotiation_id, str(exc))
        await notify("error", {"message": str(exc)})


async def _run_negotiation(negotiation_id: str, req: NegotiateRequest) -> None:
    """Run the negotiation engine in the background."""
    scenario = (req.negotiation_params.scenario or "").strip()
    if scenario == "nvda_surprise_live":
        await _run_nvda_surprise_live_dashboard(negotiation_id, req)
        return

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
        malicious_seller=req.seller_config.malicious_seller,
        seller_agent_id=req.seller_config.seller_agent_id,
    )
    passport_status = resolve_effective_passport_status(
        req.negotiation_params.passport_status
    )
    params = NegotiationParams(
        max_rounds=req.negotiation_params.max_rounds,
        timeout_seconds=req.negotiation_params.timeout_seconds,
        resource_uri=req.negotiation_params.resource_uri,
        scope=req.negotiation_params.scope,
        objective_mode=req.negotiation_params.objective_mode,
        passport_status=passport_status,
        model_mode=req.negotiation_params.model_mode,
        model_provider=req.negotiation_params.model_provider,
        model_name=req.negotiation_params.model_name,
        model_latency_budget_ms=req.negotiation_params.model_latency_budget_ms,
        deal_binding_mode=req.negotiation_params.deal_binding_mode or "legacy",
    )

    async def on_round(neg_id: str, neg_round: Any) -> None:
        payload = neg_round.to_dict()
        payload["negotiation_id"] = neg_id
        await broadcaster.broadcast_round(payload)

    async def on_result(result: WireNegotiationResult) -> None:
        await broadcaster.broadcast_result(result.to_dict())

    executor = NegotiationExecutor(
        on_round=on_round,
        on_result=on_result,
        discovery_service=_build_discovery_service(),
        discovery_capability=req.negotiation_params.scope,
    )
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
                "settlement_status": "pending",
            }

        ledger.record_completed_run(
            negotiation_id,
            success=result.success,
            result_dict=result_dict,
            total_rounds=result.total_rounds,
            deal=deal,
        )
        if result.success and deal is not None:
            asyncio.create_task(
                _run_post_negotiation_and_merge_deal(
                    negotiation_id,
                    result,
                    buyer,
                    seller,
                    req.negotiation_params.resource_uri,
                )
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
async def start_negotiation(
    req: NegotiateRequest,
    background_tasks: BackgroundTasks,
) -> NegotiateResponse:
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


@router.post("/act5/malicious", response_model=NegotiateResponse)
async def start_malicious_seller_demo(
    background_tasks: BackgroundTasks,
) -> NegotiateResponse:
    """Trigger the optional malicious-seller payment-refusal demo."""
    req = NegotiateRequest(
        buyer_config=AgentConfigSchema(
            agent_id="act5-buyer",
            address=_ACT5_BUYER_ADDRESS,
            role="buyer",
            initial_price=0.05,
            reservation_price=0.12,
            tendency="balanced",
            grid_enabled=True,
        ),
        seller_config=AgentConfigSchema(
            agent_id="act5-malicious-seller",
            address=_ACT5_SELLER_ADDRESS,
            role="seller",
            initial_price=0.16,
            reservation_price=0.04,
            tendency="dominant",
            malicious_seller=True,
            seller_agent_id=99,
            grid_enabled=True,
        ),
        negotiation_params=NegotiationParamsSchema(
            max_rounds=7,
            resource_uri="/api/weather",
            scope="weather-data",
            objective_mode="fairness_guardrail",
            passport_status="stubbed",
            model_mode="policy_only",
        ),
    )
    return await start_negotiation(req, background_tasks)


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


@router.get("/negotiations/{negotiation_id}/trace")
async def get_negotiation_trace(negotiation_id: str) -> dict[str, Any]:
    """Get the auto-saved JSON trace payload for one negotiation."""
    trace = ledger.get_trace(negotiation_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    return trace


@router.get("/traces")
async def list_negotiation_traces() -> list[dict[str, Any]]:
    """List trace files for all negotiations seen by this API process."""
    return ledger.list_traces()


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
    return ledger.dashboard_stats(
        passport_status=resolve_effective_passport_status()
    )


@router.get("/passport/status")
async def get_passport_status() -> dict[str, Any]:
    """Expose current Passport runtime posture for demo diagnostics."""
    runtime = resolve_passport_runtime()
    return runtime.to_dict()
