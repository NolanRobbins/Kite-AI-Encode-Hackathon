"""A2A NegotiationExecutor — bridges NegMAS negotiation rounds to A2A Task lifecycle."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any, Callable, Optional

from negotiatorgrid.config import config
from negotiatorgrid.core.deal_hash import (
    binding_deal_hash_hex,
    compute_binding_deal_hash_bytes,
    compute_binding_deal_hash_hex_from_result,
)
from negotiatorgrid.core.nash_guardrail import NashGuardrail
from negotiatorgrid.core.negotiation import NegotiationSession
from negotiatorgrid.core.opponent_model import OpponentModeler
from negotiatorgrid.core.types import NegotiationConfig as CoreNegConfig
from negotiatorgrid.core.types import NegotiationOffer as CoreOffer
from negotiatorgrid.core.types import NegotiationResult as CoreSessionResult
from negotiatorgrid.llm.offer_generator import OfferGenerator

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State Machine
# ---------------------------------------------------------------------------


class NegotiationState(str, Enum):
    """State machine for a bilateral negotiation session."""

    IDLE = "idle"
    DISCOVERING = "discovering"
    NEGOTIATING = "negotiating"
    SETTLING = "settling"
    ATTESTING = "attesting"
    COMPLETED = "completed"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Wire-format data structures (A2A message metadata payloads)
#
# Names are ``Wire*`` to avoid colliding with :class:`negotiatorgrid.core.types.NegotiationOffer`
# / ``NegotiationResult`` (Pydantic transcript output from NegMAS ``NegotiationSession``).
# ---------------------------------------------------------------------------


@dataclass
class WireNegotiationOffer:
    """A single offer / counter-offer in the negotiation."""

    round: int
    price: float
    scope: str = ""
    nl_message: str = ""
    agent_id: str = ""
    timestamp: float = field(default_factory=time.time)
    utility: float = 0.0
    aspiration: float = 0.0
    stance: str = "neutral"
    reasoning: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "round": self.round,
            "price": self.price,
            "scope": self.scope,
            "nl_message": self.nl_message,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp,
            "utility": self.utility,
            "aspiration": self.aspiration,
            "stance": self.stance,
            "reasoning": self.reasoning,
        }


@dataclass
class WireNegotiationRound:
    """One complete round: buyer offer + seller counter."""

    round_number: int
    buyer_offer: Optional[WireNegotiationOffer] = None
    seller_offer: Optional[WireNegotiationOffer] = None
    opponent_model: dict[str, Any] = field(default_factory=dict)
    nash_check: str = "N/A"
    nash_price: float = 0.0
    nash_deviation_pct: float = 0.0
    runtime: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "round": self.round_number,
            "buyer_offer": self.buyer_offer.price if self.buyer_offer else None,
            "seller_offer": self.seller_offer.price if self.seller_offer else None,
            "buyer_nl": self.buyer_offer.nl_message if self.buyer_offer else "",
            "seller_nl": self.seller_offer.nl_message if self.seller_offer else "",
            "buyer_stance": self.buyer_offer.stance if self.buyer_offer else "",
            "seller_stance": self.seller_offer.stance if self.seller_offer else "",
            "buyer_reasoning": self.buyer_offer.reasoning if self.buyer_offer else {},
            "seller_reasoning": self.seller_offer.reasoning if self.seller_offer else {},
            "opponent_model": self.opponent_model,
            "nash_check": self.nash_check,
            "nash_price": self.nash_price,
            "nash_deviation_pct": self.nash_deviation_pct,
            "runtime": self.runtime,
        }


@dataclass
class WireNegotiationResult:
    """Final outcome of a negotiation session (executor / API wire shape)."""

    negotiation_id: str = ""
    success: bool = False
    agreed_price: float = 0.0
    total_rounds: int = 0
    deal_hash: str = ""
    #: Unix second frozen at agreement; must match attestation binding hash.
    deal_bound_at: int = 0
    buyer_utility: float = 0.0
    seller_utility: float = 0.0
    duration_seconds: float = 0.0
    rounds: list[WireNegotiationRound] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    objective_mode: str = "fairness_guardrail"
    passport_status: str = "stubbed"
    reason: str = ""
    discovery: dict[str, Any] | None = None
    verification: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "negotiation_id": self.negotiation_id,
            "success": self.success,
            "agreed_price": self.agreed_price,
            "total_rounds": self.total_rounds,
            "deal_hash": self.deal_hash,
            "deal_bound_at": self.deal_bound_at,
            "buyer_utility": self.buyer_utility,
            "seller_utility": self.seller_utility,
            "duration_seconds": self.duration_seconds,
            "rounds": [r.to_dict() for r in self.rounds],
            "metrics": self.metrics,
            "objective_mode": self.objective_mode,
            "passport_status": self.passport_status,
            "reason": self.reason,
            "discovery": self.discovery,
            "verification": self.verification,
        }


# ---------------------------------------------------------------------------
# Agent config for a negotiation participant
# ---------------------------------------------------------------------------


@dataclass
class AgentConfig:
    """Configuration for one side of a negotiation."""

    agent_id: str = ""
    address: str = ""
    role: str = "buyer"  # "buyer" or "seller"
    reservation_price: float = 0.0
    initial_price: float = 0.0
    strategy: str = "aspiration"  # "aspiration", "tit-for-tat", "boulware"
    concession_rate: float = 0.05
    reputation_score: float = 50.0
    grid_enabled: bool = True
    tendency: str = ""
    malicious_seller: bool = False
    seller_agent_id: int = 0


@dataclass
class NegotiationParams:
    """Parameters controlling the negotiation session."""

    max_rounds: int = 7
    timeout_seconds: int = 30
    resource_uri: str = "/api/service"
    scope: str = "weather-data"
    objective_mode: str = "fairness_guardrail"
    passport_status: str = "stubbed"
    model_mode: str = "policy_only"
    model_provider: str = "template"
    model_name: str = "template"
    model_latency_budget_ms: int = 1200
    #: ``legacy`` = short text fingerprint; ``canonical_eip712`` = same hash as
    #: ``DealRecord`` / ``demo.py`` / ``surprise_api`` admin sync (keccak ABI).
    deal_binding_mode: str = "legacy"


# ---------------------------------------------------------------------------
# Strategy name → aspiration exponent mapping
# ---------------------------------------------------------------------------

_STRATEGY_EXPONENTS: dict[str, float] = {
    "aspiration": 4.0,
    "boulware": 4.0,
    "tit-for-tat": 1.0,
    "conceder": 0.25,
    "linear": 1.0,
}

_TENDENCY_EXPONENTS: dict[str, float] = {
    "dominant": 4.0,
    "aggressive": 4.0,
    "balanced": 1.0,
    "cooperative": 0.35,
    "submissive": 0.25,
}

_TENDENCY_LABELS: dict[str, str] = {
    "dominant": "dominant",
    "aggressive": "dominant",
    "balanced": "balanced",
    "cooperative": "submissive",
    "submissive": "submissive",
}


def _normalise_objective_mode(value: str) -> str:
    mode = (value or "fairness_guardrail").strip().lower().replace("-", "_")
    aliases = {
        "fair": "fairness_guardrail",
        "fairness": "fairness_guardrail",
        "buyer": "buyer_advantage",
        "buyer_surplus": "buyer_advantage",
        "seller": "seller_advantage",
        "seller_margin": "seller_advantage",
        "nash": "pure_nash",
        "pure_nash_benchmark": "pure_nash",
    }
    return aliases.get(
        mode,
        mode
        if mode
        in {
            "fairness_guardrail",
            "buyer_advantage",
            "seller_advantage",
            "pure_nash",
        }
        else "fairness_guardrail",
    )


def _normalise_model_mode(value: str) -> str:
    mode = (value or "policy_only").strip().lower().replace("-", "_")
    aliases = {
        "none": "policy_only",
        "template": "policy_only",
        "small": "slm",
        "small_language_model": "slm",
        "large": "llm",
        "large_language_model": "llm",
        "reasoning": "reasoning_llm",
    }
    return aliases.get(
        mode,
        mode if mode in {"policy_only", "slm", "llm", "reasoning_llm"} else "policy_only",
    )


def _agent_exponent(config: AgentConfig, objective_mode: str) -> float:
    """Translate demo controls into the aspiration exponent used by NegMAS."""
    tendency = (config.tendency or "").strip().lower()
    exponent = _TENDENCY_EXPONENTS.get(
        tendency,
        _STRATEGY_EXPONENTS.get(config.strategy, 4.0),
    )

    if not config.grid_enabled:
        # A plain baseline agent still negotiates, but without adaptive grid help.
        exponent = min(exponent, 1.0)

    if objective_mode == "pure_nash":
        return min(exponent, 0.75)
    if objective_mode == "buyer_advantage":
        return max(exponent, 4.0) if config.role == "buyer" else min(exponent, 0.35)
    if objective_mode == "seller_advantage":
        return min(exponent, 0.35) if config.role == "buyer" else max(exponent, 4.0)
    return exponent


def _tendency_label(config: AgentConfig) -> str:
    tendency = (config.tendency or "").strip().lower()
    if tendency:
        return _TENDENCY_LABELS.get(tendency, tendency)
    if config.strategy in {"boulware", "aspiration"}:
        return "dominant"
    if config.strategy == "conceder":
        return "cooperative"
    return "balanced"


def _social_risk_label(deviation_pct: float, objective_mode: str) -> str:
    if objective_mode == "pure_nash":
        return "benchmark"
    if deviation_pct <= 0.10:
        return "low"
    if deviation_pct <= 0.20:
        return "watch"
    return "high"


def _sandbox_posture(model_mode: str) -> dict[str, Any]:
    return {
        "buyer_agent_isolated": True,
        "seller_agent_isolated": True,
        "shared_private_state": False,
        "transport": "typed_offer_bus",
        "llm_tool_access": "none",
        "filesystem_access": "none",
        "network_access": "model_api_only" if model_mode in {"llm", "reasoning_llm"} else "none",
        "secrets_in_prompt": False,
        "typed_fields_authoritative": True,
        "free_text_can_execute_actions": False,
        "mcp_tools_enabled": False,
        "note": (
            "Buyer and seller run as separate negotiation policies with "
            "separate reservation bounds. They do not receive filesystem, "
            "wallet, or MCP tools. Only typed negotiation state is sent "
            "to the language layer, and numeric protocol fields win over prose."
        ),
    }


def _edge_case_status(max_rounds: int, timeout_seconds: int) -> dict[str, Any]:
    return {
        "round_cap": max_rounds,
        "timeout_seconds": timeout_seconds,
        "deadlock_policy": "walk_away_no_payment",
        "price_mismatch_policy": "abort_payment_on_deal_hash_or_amount_mismatch",
        "streaming_policy": "round_updates_only_no_mid_round_price_mutation",
        "payment_failure_policy": "mock_or_retry_later_until_kite_passport_ready",
        "mcp_policy": "disabled_until_trust_gate_and_sandbox_are_configured",
    }


def _combine_runtime_metrics(
    model_mode: str,
    buyer_runtime: dict[str, Any],
    seller_runtime: dict[str, Any],
) -> dict[str, Any]:
    buyer_calls = int(buyer_runtime.get("model_calls") or 0)
    seller_calls = int(seller_runtime.get("model_calls") or 0)
    total_calls = buyer_calls + seller_calls

    buyer_fallbacks = int(buyer_runtime.get("fallback_messages") or 0)
    seller_fallbacks = int(seller_runtime.get("fallback_messages") or 0)
    total_fallbacks = buyer_fallbacks + seller_fallbacks

    buyer_total_latency = float(buyer_runtime.get("total_model_latency_ms") or 0.0)
    seller_total_latency = float(seller_runtime.get("total_model_latency_ms") or 0.0)
    total_latency = buyer_total_latency + seller_total_latency
    avg_latency = total_latency / total_calls if total_calls else 0.0

    buyer_provider = str(buyer_runtime.get("provider") or "buyer")
    seller_provider = str(seller_runtime.get("provider") or "seller")
    buyer_model = str(buyer_runtime.get("model") or "template")
    seller_model = str(seller_runtime.get("model") or "template")

    if model_mode in {"llm", "reasoning_llm"}:
        runtime_note = (
            "Buyer and seller use independent model sandboxes. "
            "Typed protocol fields remain authoritative."
        )
    elif model_mode == "slm":
        runtime_note = (
            "SLM mode uses lightweight language generation with deterministic core policy."
        )
    else:
        runtime_note = "Policy-only mode uses deterministic negotiation state and template language."

    return {
        "model_mode": model_mode,
        "provider": f"{buyer_provider}|{seller_provider}",
        "model": f"{buyer_model}|{seller_model}",
        "model_calls": total_calls,
        "fallback_messages": total_fallbacks,
        "avg_model_latency_ms": round(avg_latency, 2),
        "total_model_latency_ms": round(total_latency, 2),
        "latency_budget_ms": max(
            int(buyer_runtime.get("latency_budget_ms") or 0),
            int(seller_runtime.get("latency_budget_ms") or 0),
        ),
        "runtime_note": runtime_note,
        "buyer_runtime": buyer_runtime,
        "seller_runtime": seller_runtime,
    }


def _reasoning_summary(
    *,
    role: str,
    price: float,
    previous_price: float | None,
    objective_mode: str,
    grid_enabled: bool,
    tendency: str,
    opponent_model: dict[str, Any],
    nash_status: str,
    nash_deviation_pct: float,
) -> dict[str, str]:
    side = "buyer" if role == "buyer" else "seller"
    objective_text = {
        "fairness_guardrail": "optimize own surplus while staying close to a fair Nash band",
        "buyer_advantage": "maximize buyer surplus and track fairness drift",
        "seller_advantage": "maximize seller margin and track fairness drift",
        "pure_nash": "converge toward the Nash benchmark for comparison",
    }[objective_mode]

    if previous_price is None:
        movement = "opened with a calibrated anchor"
    else:
        delta = price - previous_price
        if abs(delta) < 0.000001:
            movement = "held position to test opponent resolve"
        elif (side == "buyer" and delta > 0) or (side == "seller" and delta < 0):
            movement = "conceded to keep the zone of agreement alive"
        else:
            movement = "pressed advantage after reading the counterparty signal"

    confidence = opponent_model.get("confidence", 0.0)
    estimated = opponent_model.get("estimated_reservation", 0.0)
    signal = (
        f"opponent reservation estimate ${estimated:.4f} at {confidence:.0%} confidence"
        if grid_enabled
        else "baseline mode: no opponent-model adjustment"
    )
    risk = (
        f"{nash_status}: {nash_deviation_pct:.1%} away from Nash benchmark"
        if nash_status != "N/A"
        else "waiting for both offers before Nash drift check"
    )

    return {
        "goal": objective_text,
        "signal": signal,
        "action": f"{tendency} stance: {movement} at ${price:.4f}",
        "risk": risk,
    }


# ---------------------------------------------------------------------------
# NegotiationExecutor internals (session assembly + transcript enrichment)
# ---------------------------------------------------------------------------


@dataclass
class _TranscriptEnrichmentContext:
    """Inputs for turning a NegMAS transcript into wire rounds."""

    negotiation_id: str
    session: dict[str, Any]
    core_result: CoreSessionResult
    display_price: Callable[[float], float]
    buyer_config: AgentConfig
    seller_config: AgentConfig
    neg_config: NegotiationParams
    objective_mode: str
    buyer_om: Optional[OpponentModeler]
    seller_om: Optional[OpponentModeler]
    buyer_offer_gen: OfferGenerator
    seller_offer_gen: OfferGenerator
    guardrail: NashGuardrail
    core_config: CoreNegConfig


@dataclass
class _TranscriptEnrichmentOutcome:
    """Outputs from async transcript enrichment."""

    rounds: list[WireNegotiationRound]
    last_nash_result: Any
    buyer_offer_gen: OfferGenerator
    seller_offer_gen: OfferGenerator


# ---------------------------------------------------------------------------
# NegotiationExecutor — the main class
# ---------------------------------------------------------------------------


class NegotiationExecutor:
    """Manages an A2A bilateral negotiation session.

    Delegates the actual negotiation to the NegMAS-backed
    ``NegotiationSession`` from ``core.negotiation``, then post-processes
    the transcript with opponent modelling, Nash guardrail checks, and
    NL message generation.
    """

    def __init__(
        self,
        on_round: Optional[Callable] = None,
        on_result: Optional[Callable] = None,
        discovery_service: Any = None,
        discovery_capability: str = "",
        enforce_verification: bool = False,
    ):
        self.state = NegotiationState.IDLE
        self._negotiations: dict[str, dict[str, Any]] = {}
        self._on_round = on_round
        self._on_result = on_result
        self._discovery_service = discovery_service
        self._discovery_capability = discovery_capability
        self._enforce_verification = enforce_verification

    @staticmethod
    def _metadata_to_dict(value: Any) -> dict[str, Any]:
        if value is None:
            return {}
        if hasattr(value, "to_dict"):
            return dict(value.to_dict())
        if hasattr(value, "model_dump"):
            return dict(value.model_dump())
        if is_dataclass(value):
            return asdict(value)
        if isinstance(value, dict):
            return dict(value)
        return {"value": value}

    @staticmethod
    def _resolve_negotiation_id(negotiation_id: str | None) -> str:
        external = (negotiation_id or "").strip()
        if external:
            return external
        return f"neg-{uuid.uuid4().hex[:8]}"

    @staticmethod
    def _build_scaled_core_config(
        buyer_config: AgentConfig,
        seller_config: AgentConfig,
        neg_config: NegotiationParams,
    ) -> tuple[CoreNegConfig, Callable[[float], float]]:
        """Map UI prices into NegMAS integer issue space and return ``display_price`` scaler."""
        price_min = min(buyer_config.initial_price, seller_config.reservation_price) * 0.8
        price_max = max(seller_config.initial_price, buyer_config.reservation_price) * 1.2
        price_scale = 10_000.0 if price_max <= 1.0 else 1.0
        core_price_min = price_min * price_scale
        core_price_max = price_max * price_scale
        if core_price_max - core_price_min < 1.0:
            core_price_min = min(
                buyer_config.initial_price,
                seller_config.reservation_price,
            ) * price_scale - 1.0
            core_price_max = max(
                seller_config.initial_price,
                buyer_config.reservation_price,
            ) * price_scale + 1.0

        def display_price(value: float) -> float:
            return value / price_scale

        core_config = CoreNegConfig(
            max_rounds=neg_config.max_rounds,
            timeout_seconds=neg_config.timeout_seconds,
            price_min=core_price_min,
            price_max=core_price_max,
            buyer_reservation=buyer_config.reservation_price * price_scale,
            seller_reservation=seller_config.reservation_price * price_scale,
        )
        return core_config, display_price

    @staticmethod
    def _make_grid_modelers(
        buyer_config: AgentConfig,
        seller_config: AgentConfig,
        core_config: CoreNegConfig,
    ) -> tuple[Optional[OpponentModeler], Optional[OpponentModeler]]:
        buyer_om = (
            OpponentModeler(
                is_opponent_seller=True,
                price_min=core_config.price_min,
                price_max=core_config.price_max,
            )
            if buyer_config.grid_enabled
            else None
        )
        seller_om = (
            OpponentModeler(
                is_opponent_seller=False,
                price_min=core_config.price_min,
                price_max=core_config.price_max,
            )
            if seller_config.grid_enabled
            else None
        )
        return buyer_om, seller_om

    @staticmethod
    def _run_negmas_core(
        core_config: CoreNegConfig,
        buyer_exp: float,
        seller_exp: float,
        buyer_om: Optional[OpponentModeler],
        seller_om: Optional[OpponentModeler],
    ) -> CoreSessionResult:
        neg_session = NegotiationSession(
            config=core_config,
            buyer_opponent_modeler=buyer_om,
            seller_opponent_modeler=seller_om,
            buyer_exponent=buyer_exp,
            seller_exponent=seller_exp,
        )
        return neg_session.run()

    @staticmethod
    def _build_offer_generators(
        neg_config: NegotiationParams,
        model_mode: str,
    ) -> tuple[OfferGenerator, OfferGenerator]:
        buyer_model = (config.llm.model or "gpt-4o-mini").strip() or "gpt-4o-mini"
        seller_model = (config.llm.xai_model or "grok-4").strip() or "grok-4"
        seller_base_url = (config.llm.xai_base_url or "https://api.x.ai/v1").strip()

        if model_mode == "llm":
            buyer = OfferGenerator(
                api_key=config.llm.api_key,
                model=buyer_model,
                model_mode=model_mode,
                provider="openai",
                latency_budget_ms=neg_config.model_latency_budget_ms,
            )
            seller = OfferGenerator(
                api_key=config.llm.xai_api_key,
                model=seller_model,
                model_mode=model_mode,
                provider="xai",
                latency_budget_ms=neg_config.model_latency_budget_ms,
                base_url=seller_base_url,
            )
            return buyer, seller

        if model_mode == "reasoning_llm":
            buyer = OfferGenerator(
                api_key=config.llm.api_key,
                model=buyer_model,
                model_mode=model_mode,
                provider="openai",
                latency_budget_ms=neg_config.model_latency_budget_ms,
            )
            seller = OfferGenerator(
                api_key=config.llm.xai_api_key,
                model=seller_model,
                model_mode=model_mode,
                provider="xai",
                latency_budget_ms=neg_config.model_latency_budget_ms,
                base_url=seller_base_url,
            )
            return buyer, seller

        if model_mode == "slm":
            return (
                OfferGenerator(
                    api_key="",
                    model="local-small-buyer",
                    model_mode=model_mode,
                    provider="slm-buyer",
                    latency_budget_ms=neg_config.model_latency_budget_ms,
                ),
                OfferGenerator(
                    api_key="",
                    model="local-small-seller",
                    model_mode=model_mode,
                    provider="slm-seller",
                    latency_budget_ms=neg_config.model_latency_budget_ms,
                ),
            )

        return (
            OfferGenerator(
                api_key="",
                model=buyer_model,
                model_mode=model_mode,
                provider="template-buyer",
                latency_budget_ms=neg_config.model_latency_budget_ms,
            ),
            OfferGenerator(
                api_key="",
                model=seller_model,
                model_mode=model_mode,
                provider="template-seller",
                latency_budget_ms=neg_config.model_latency_budget_ms,
            ),
        )

    @staticmethod
    def _group_core_offers_by_round(
        transcript: list[CoreOffer],
    ) -> tuple[dict[int, CoreOffer], dict[int, CoreOffer]]:
        buyer_offers_by_round: dict[int, CoreOffer] = {}
        seller_offers_by_round: dict[int, CoreOffer] = {}
        for offer in transcript:
            if offer.agent_id == "buyer":
                buyer_offers_by_round[offer.round_number] = offer
            elif offer.agent_id == "seller":
                seller_offers_by_round[offer.round_number] = offer
        return buyer_offers_by_round, seller_offers_by_round

    async def _enrich_and_broadcast_rounds(
        self,
        ctx: _TranscriptEnrichmentContext,
    ) -> _TranscriptEnrichmentOutcome:
        buyer_offers_by_round, seller_offers_by_round = self._group_core_offers_by_round(
            ctx.core_result.transcript
        )
        all_round_nums = sorted(
            set(buyer_offers_by_round.keys()) | set(seller_offers_by_round.keys())
        )

        rounds_data: list[WireNegotiationRound] = []
        previous_buyer_price: float | None = None
        previous_seller_price: float | None = None
        last_nash_result = None
        model_mode = ctx.buyer_offer_gen.model_mode
        if model_mode == "reasoning_llm":
            stream_delay = 0.45
        elif model_mode == "llm":
            stream_delay = 0.35
        elif model_mode == "slm":
            stream_delay = 0.2
        else:
            stream_delay = 0.12

        for rnd in all_round_nums:
            r_num = rnd + 1
            b_core = buyer_offers_by_round.get(rnd)
            s_core = seller_offers_by_round.get(rnd)
            buyer_display_price = ctx.display_price(b_core.price) if b_core else None
            seller_display_price = ctx.display_price(s_core.price) if s_core else None

            buyer_nl = ""
            seller_nl = ""
            if buyer_display_price is not None:
                buyer_nl = ctx.buyer_offer_gen.generate_buyer_offer(
                    round_num=r_num, price=buyer_display_price
                )
            if seller_display_price is not None:
                seller_nl = ctx.seller_offer_gen.generate_seller_counter(
                    round_num=r_num,
                    price=seller_display_price,
                )

            t = r_num / max(ctx.neg_config.max_rounds, 1)

            opp_model_data = ctx.buyer_om.get_model() if ctx.buyer_om else None
            opp_model_dict = {
                "estimated_reservation": round(
                    ctx.display_price(opp_model_data.estimated_reservation_price)
                    if opp_model_data
                    else 0.0,
                    6,
                ),
                "confidence": round(opp_model_data.confidence if opp_model_data else 0.0, 2),
                "buyer_grid_enabled": ctx.buyer_config.grid_enabled,
                "seller_grid_enabled": ctx.seller_config.grid_enabled,
            }

            nash_status = "N/A"
            nash_price = 0.0
            nash_deviation_pct = 0.0
            if b_core and s_core:
                buyer_price = buyer_display_price or 0.0
                seller_price = seller_display_price or 0.0

                def buyer_ufun(p: float) -> float:
                    return max(0.0, ctx.buyer_config.reservation_price - p)

                def seller_ufun(p: float) -> float:
                    return max(0.0, p - ctx.seller_config.reservation_price)

                nash_result = ctx.guardrail.check_deal(
                    agreed_price=(buyer_price + seller_price) / 2.0,
                    buyer_ufun=buyer_ufun,
                    seller_ufun=seller_ufun,
                    price_min=ctx.display_price(ctx.core_config.price_min),
                    price_max=ctx.display_price(ctx.core_config.price_max),
                    grid_size=11,
                )
                last_nash_result = nash_result
                nash_status = "PASS" if nash_result.passed else "WARN"
                nash_price = round(nash_result.nash_price, 6)
                nash_deviation_pct = round(nash_result.deviation_pct, 4)

            buyer_offer = None
            if b_core and buyer_display_price is not None:
                buyer_price = buyer_display_price
                buyer_tendency = _tendency_label(ctx.buyer_config)
                buyer_offer = WireNegotiationOffer(
                    round=r_num,
                    price=buyer_price,
                    scope=ctx.neg_config.scope,
                    nl_message=buyer_nl,
                    agent_id=ctx.buyer_config.agent_id or "buyer",
                    timestamp=b_core.timestamp,
                    utility=round(1.0 - t * 0.3, 3),
                    aspiration=round(1.0 - t * 0.5, 3),
                    stance=buyer_tendency,
                    reasoning=_reasoning_summary(
                        role="buyer",
                        price=buyer_price,
                        previous_price=previous_buyer_price,
                        objective_mode=ctx.objective_mode,
                        grid_enabled=ctx.buyer_config.grid_enabled,
                        tendency=buyer_tendency,
                        opponent_model=opp_model_dict,
                        nash_status=nash_status,
                        nash_deviation_pct=nash_deviation_pct,
                    ),
                )
                previous_buyer_price = buyer_price

            seller_offer = None
            if s_core and seller_display_price is not None:
                seller_price = seller_display_price
                seller_tendency = _tendency_label(ctx.seller_config)
                seller_model_data = ctx.seller_om.get_model() if ctx.seller_om else None
                seller_opp_model = {
                    "estimated_reservation": round(
                        ctx.display_price(seller_model_data.estimated_reservation_price)
                        if seller_model_data
                        else 0.0,
                        6,
                    ),
                    "confidence": round(
                        seller_model_data.confidence if seller_model_data else 0.0, 2
                    ),
                }
                seller_offer = WireNegotiationOffer(
                    round=r_num,
                    price=seller_price,
                    scope=ctx.neg_config.scope,
                    nl_message=seller_nl,
                    agent_id=ctx.seller_config.agent_id or "seller",
                    timestamp=s_core.timestamp,
                    utility=round(1.0 - t * 0.25, 3),
                    aspiration=round(1.0 - t * 0.45, 3),
                    stance=seller_tendency,
                    reasoning=_reasoning_summary(
                        role="seller",
                        price=seller_price,
                        previous_price=previous_seller_price,
                        objective_mode=ctx.objective_mode,
                        grid_enabled=ctx.seller_config.grid_enabled,
                        tendency=seller_tendency,
                        opponent_model=seller_opp_model,
                        nash_status=nash_status,
                        nash_deviation_pct=nash_deviation_pct,
                    ),
                )
                previous_seller_price = seller_price

            round_runtime = _combine_runtime_metrics(
                ctx.buyer_offer_gen.model_mode,
                ctx.buyer_offer_gen.runtime_metrics(),
                ctx.seller_offer_gen.runtime_metrics(),
            )

            neg_round = WireNegotiationRound(
                round_number=r_num,
                buyer_offer=buyer_offer,
                seller_offer=seller_offer,
                opponent_model=opp_model_dict,
                nash_check=nash_status,
                nash_price=nash_price,
                nash_deviation_pct=nash_deviation_pct,
                runtime=round_runtime,
            )
            rounds_data.append(neg_round)
            ctx.session["rounds"].append(neg_round)

            if self._on_round:
                try:
                    await self._on_round(ctx.negotiation_id, neg_round)
                except Exception:
                    logger.exception("Error in on_round callback")

            await asyncio.sleep(stream_delay)

        return _TranscriptEnrichmentOutcome(
            rounds=rounds_data,
            last_nash_result=last_nash_result,
            buyer_offer_gen=ctx.buyer_offer_gen,
            seller_offer_gen=ctx.seller_offer_gen,
        )

    async def _emit_final_result(self, result: WireNegotiationResult, success: bool) -> None:
        self.state = NegotiationState.COMPLETED if success else NegotiationState.FAILED
        if self._on_result:
            try:
                await self._on_result(result)
            except Exception:
                logger.exception("Error in on_result callback")

    # -- Public API ---------------------------------------------------------

    async def start_negotiation(
        self,
        buyer_config: AgentConfig,
        seller_config: AgentConfig,
        neg_config: NegotiationParams,
        *,
        negotiation_id: str | None = None,
    ) -> WireNegotiationResult:
        """Run a full bilateral negotiation and return the result.

        Args:
            negotiation_id: Correlation id from the host (e.g. REST path). When
                omitted or blank, a new ``neg-…`` id is minted for standalone runs.
        """
        negotiation_id = self._resolve_negotiation_id(negotiation_id)
        self.state = NegotiationState.DISCOVERING
        start_time = time.time()
        objective_mode = _normalise_objective_mode(neg_config.objective_mode)
        model_mode = _normalise_model_mode(neg_config.model_mode)

        session: dict[str, Any] = {
            "id": negotiation_id,
            "buyer": buyer_config,
            "seller": seller_config,
            "params": neg_config,
            "rounds": [],
            "start_time": start_time,
        }
        self._negotiations[negotiation_id] = session

        discovery_data: dict[str, Any] | None = None
        verification_data: dict[str, Any] | None = None
        if self._discovery_service is not None:
            capability = self._discovery_capability or neg_config.scope
            discovery = await self._discovery_service.discover_tool(
                capability,
                negotiation_id=negotiation_id,
            )
            discovery_data = self._metadata_to_dict(discovery)

            if discovery_data.get("success", bool(discovery_data.get("service_id"))):
                verification = await self._discovery_service.verify_discovered_agent(
                    discovery,
                    negotiation_id=negotiation_id,
                )
                verification_data = self._metadata_to_dict(verification)
            elif self._enforce_verification:
                verification_data = {
                    "passed": False,
                    "error": discovery_data.get("error", "discovery_failed"),
                }

            if self._enforce_verification and not (
                verification_data and verification_data.get("passed")
            ):
                result = WireNegotiationResult(
                    negotiation_id=negotiation_id,
                    success=False,
                    total_rounds=0,
                    duration_seconds=round(time.time() - start_time, 3),
                    objective_mode=objective_mode,
                    passport_status=neg_config.passport_status,
                    reason="verification_failed",
                    discovery=discovery_data,
                    verification=verification_data,
                )
                await self._emit_final_result(result, False)
                return result

        self.state = NegotiationState.NEGOTIATING

        buyer_exp = _agent_exponent(buyer_config, objective_mode)
        seller_exp = _agent_exponent(seller_config, objective_mode)

        core_config, display_price = self._build_scaled_core_config(
            buyer_config, seller_config, neg_config
        )
        buyer_om, seller_om = self._make_grid_modelers(
            buyer_config, seller_config, core_config
        )
        core_result = self._run_negmas_core(
            core_config, buyer_exp, seller_exp, buyer_om, seller_om
        )

        guardrail = NashGuardrail()
        buyer_offer_gen, seller_offer_gen = self._build_offer_generators(
            neg_config,
            model_mode,
        )

        ctx = _TranscriptEnrichmentContext(
            negotiation_id=negotiation_id,
            session=session,
            core_result=core_result,
            display_price=display_price,
            buyer_config=buyer_config,
            seller_config=seller_config,
            neg_config=neg_config,
            objective_mode=objective_mode,
            buyer_om=buyer_om,
            seller_om=seller_om,
            buyer_offer_gen=buyer_offer_gen,
            seller_offer_gen=seller_offer_gen,
            guardrail=guardrail,
            core_config=core_config,
        )
        enriched = await self._enrich_and_broadcast_rounds(ctx)
        rounds_data = enriched.rounds
        last_nash_result = enriched.last_nash_result
        buyer_offer_gen = enriched.buyer_offer_gen
        seller_offer_gen = enriched.seller_offer_gen

        duration = time.time() - start_time
        success = core_result.agreed_price is not None
        agreed_price = (
            display_price(core_result.agreed_price) if core_result.agreed_price else 0.0
        )
        buyer_id = buyer_config.agent_id or buyer_config.address or "buyer"
        seller_id = seller_config.agent_id or seller_config.address or "seller"
        deal_bound_at = int(time.time()) if success else 0
        deal_hash = ""
        if success:
            if neg_config.deal_binding_mode == "canonical_eip712":
                tmp_nr = CoreSessionResult(
                    agreed_price=agreed_price,
                    rounds=len(rounds_data),
                    transcript=[],
                    buyer_id=buyer_id,
                    seller_id=seller_id,
                    deal_bound_at=deal_bound_at,
                )
                deal_hash = compute_binding_deal_hash_hex_from_result(
                    tmp_nr,
                    bound_at=deal_bound_at,
                    resource_uri=neg_config.resource_uri or "",
                )
            else:
                digest = compute_binding_deal_hash_bytes(
                    buyer_id, seller_id, agreed_price, deal_bound_at
                )
                deal_hash = binding_deal_hash_hex(digest)

        buyer_util = 0.0
        seller_util = 0.0
        if success:
            if buyer_config.reservation_price != buyer_config.initial_price:
                buyer_util = 1.0 - (agreed_price - buyer_config.initial_price) / (
                    buyer_config.reservation_price - buyer_config.initial_price
                )
            if seller_config.initial_price != seller_config.reservation_price:
                seller_util = 1.0 - (seller_config.initial_price - agreed_price) / (
                    seller_config.initial_price - seller_config.reservation_price
                )

        reason = "agreement" if success else "max_rounds_reached"
        nash_price = round(last_nash_result.nash_price, 6) if last_nash_result else 0.0
        nash_deviation_pct = round(last_nash_result.deviation_pct, 4) if last_nash_result else 0.0
        buyer_surplus = max(0.0, buyer_config.reservation_price - agreed_price) if success else 0.0
        seller_surplus = (
            max(0.0, agreed_price - seller_config.reservation_price)
            if success
            else 0.0
        )
        seller_discount = max(0.0, seller_config.initial_price - agreed_price) if success else 0.0
        buyer_movement = max(0.0, agreed_price - buyer_config.initial_price) if success else 0.0
        model_runtime = _combine_runtime_metrics(
            model_mode,
            buyer_offer_gen.runtime_metrics(),
            seller_offer_gen.runtime_metrics(),
        )

        metrics = {
            "buyer_surplus": round(buyer_surplus, 6),
            "seller_surplus": round(seller_surplus, 6),
            "seller_discount": round(seller_discount, 6),
            "buyer_movement": round(buyer_movement, 6),
            "nash_price": nash_price,
            "nash_deviation_pct": nash_deviation_pct,
            "objective_mode": objective_mode,
            "social_risk": _social_risk_label(nash_deviation_pct, objective_mode),
            "buyer_grid_enabled": buyer_config.grid_enabled,
            "seller_grid_enabled": seller_config.grid_enabled,
            "buyer_tendency": _tendency_label(buyer_config),
            "seller_tendency": _tendency_label(seller_config),
            "passport_status": neg_config.passport_status,
            "model_runtime": model_runtime,
            "sandbox": _sandbox_posture(model_mode),
            "edge_case_status": _edge_case_status(
                neg_config.max_rounds,
                neg_config.timeout_seconds,
            ),
        }

        result = WireNegotiationResult(
            negotiation_id=negotiation_id,
            success=success,
            agreed_price=agreed_price,
            total_rounds=len(rounds_data),
            deal_hash=deal_hash,
            deal_bound_at=deal_bound_at,
            buyer_utility=round(max(0, min(1, buyer_util)), 3),
            seller_utility=round(max(0, min(1, seller_util)), 3),
            duration_seconds=round(duration, 3),
            rounds=rounds_data,
            metrics=metrics,
            objective_mode=objective_mode,
            passport_status=neg_config.passport_status,
            reason=reason,
            discovery=discovery_data,
            verification=verification_data,
        )

        await self._emit_final_result(result, success)
        return result

    # -- A2A message handling ------------------------------------------------

    def handle_offer(self, message: dict[str, Any]) -> WireNegotiationOffer:
        """Parse an incoming A2A negotiation-offer message."""
        content = message.get("content", message)
        return WireNegotiationOffer(
            round=content.get("round", 0),
            price=content.get("price", 0.0),
            scope=content.get("scope", ""),
            nl_message=content.get("nl_message", ""),
            agent_id=content.get("agent_id", ""),
        )

    def handle_accept(self, message: dict[str, Any]) -> WireNegotiationResult:
        """Parse an incoming A2A negotiation-accept message."""
        content = message.get("content", message)
        return WireNegotiationResult(
            success=True,
            agreed_price=content.get("agreed_price", 0.0),
            total_rounds=content.get("total_rounds", 0),
            deal_hash=content.get("deal_hash", ""),
        )

    # -- A2A message construction -------------------------------------------

    @staticmethod
    def build_offer_message(offer: WireNegotiationOffer) -> dict[str, Any]:
        """Build an A2A negotiation-offer metadata payload."""
        return {
            "type": "negotiation-offer",
            "content": offer.to_dict(),
        }

    @staticmethod
    def build_counteroffer_message(offer: WireNegotiationOffer) -> dict[str, Any]:
        """Build an A2A negotiation-counteroffer metadata payload."""
        return {
            "type": "negotiation-counteroffer",
            "content": offer.to_dict(),
        }

    @staticmethod
    def build_accept_message(
        agreed_price: float, total_rounds: int, deal_hash: str
    ) -> dict[str, Any]:
        """Build an A2A negotiation-accept metadata payload."""
        return {
            "type": "negotiation-accept",
            "content": {
                "agreed_price": agreed_price,
                "total_rounds": total_rounds,
                "deal_hash": deal_hash,
            },
        }

    @staticmethod
    def build_reject_message(reason: str, final_round: int) -> dict[str, Any]:
        """Build an A2A negotiation-reject metadata payload."""
        return {
            "type": "negotiation-reject",
            "content": {
                "reason": reason,
                "final_round": final_round,
            },
        }

    # -- Accessors ----------------------------------------------------------

    def get_negotiation(self, negotiation_id: str) -> Optional[dict[str, Any]]:
        return self._negotiations.get(negotiation_id)

    def list_negotiations(self) -> list[dict[str, Any]]:
        results = []
        for nid, session in self._negotiations.items():
            results.append({
                "negotiation_id": nid,
                "state": self.state.value,
                "rounds_completed": len(session["rounds"]),
                "buyer_agent": session["buyer"].agent_id,
                "seller_agent": session["seller"].agent_id,
            })
        return results
