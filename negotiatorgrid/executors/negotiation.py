"""A2A NegotiationExecutor — bridges NegMAS negotiation rounds to A2A Task lifecycle."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from negotiatorgrid.core.negotiation import NegotiationSession
from negotiatorgrid.core.opponent_model import OpponentModeler
from negotiatorgrid.core.nash_guardrail import NashGuardrail
from negotiatorgrid.core.types import NegotiationConfig as CoreNegConfig
from negotiatorgrid.core.types import NegotiationOffer as CoreOffer
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
# ---------------------------------------------------------------------------

@dataclass
class NegotiationOffer:
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
class NegotiationRound:
    """One complete round: buyer offer + seller counter."""

    round_number: int
    buyer_offer: Optional[NegotiationOffer] = None
    seller_offer: Optional[NegotiationOffer] = None
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
class NegotiationResult:
    """Final outcome of a negotiation session."""

    negotiation_id: str = ""
    success: bool = False
    agreed_price: float = 0.0
    total_rounds: int = 0
    deal_hash: str = ""
    buyer_utility: float = 0.0
    seller_utility: float = 0.0
    duration_seconds: float = 0.0
    rounds: list[NegotiationRound] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    objective_mode: str = "fairness_guardrail"
    passport_status: str = "stubbed"
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "negotiation_id": self.negotiation_id,
            "success": self.success,
            "agreed_price": self.agreed_price,
            "total_rounds": self.total_rounds,
            "deal_hash": self.deal_hash,
            "buyer_utility": self.buyer_utility,
            "seller_utility": self.seller_utility,
            "duration_seconds": self.duration_seconds,
            "rounds": [r.to_dict() for r in self.rounds],
            "metrics": self.metrics,
            "objective_mode": self.objective_mode,
            "passport_status": self.passport_status,
            "reason": self.reason,
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
    "cooperative": "cooperative",
    "submissive": "cooperative",
}


def compute_deal_hash(negotiation_id: str, agreed_price: float, rounds: int) -> str:
    """Compute a keccak-like hash (sha256 stand-in) for the deal."""
    payload = json.dumps(
        {"negotiation_id": negotiation_id, "agreed_price": agreed_price, "rounds": rounds},
        sort_keys=True,
    )
    return "0x" + hashlib.sha256(payload.encode()).hexdigest()


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
    return aliases.get(mode, mode if mode in {
        "fairness_guardrail",
        "buyer_advantage",
        "seller_advantage",
        "pure_nash",
    } else "fairness_guardrail")


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
    return aliases.get(mode, mode if mode in {
        "policy_only",
        "slm",
        "llm",
        "reasoning_llm",
    } else "policy_only")


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
        "llm_tool_access": "none",
        "filesystem_access": "none",
        "network_access": "model_api_only" if model_mode in {"llm", "reasoning_llm"} else "none",
        "secrets_in_prompt": False,
        "typed_fields_authoritative": True,
        "free_text_can_execute_actions": False,
        "mcp_tools_enabled": False,
        "note": (
            "Current demo agents do not receive filesystem, wallet, or MCP tools. "
            "Only typed negotiation state is sent to the language layer, and numeric protocol fields win over prose."
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
    ):
        self.state = NegotiationState.IDLE
        self._negotiations: dict[str, dict[str, Any]] = {}
        self._on_round = on_round
        self._on_result = on_result

    # -- Public API ---------------------------------------------------------

    async def start_negotiation(
        self,
        buyer_config: AgentConfig,
        seller_config: AgentConfig,
        neg_config: NegotiationParams,
    ) -> NegotiationResult:
        """Run a full bilateral negotiation and return the result."""
        negotiation_id = f"neg-{uuid.uuid4().hex[:8]}"
        self.state = NegotiationState.DISCOVERING
        start_time = time.time()
        objective_mode = _normalise_objective_mode(neg_config.objective_mode)
        model_mode = _normalise_model_mode(neg_config.model_mode)

        # Store session metadata
        session: dict[str, Any] = {
            "id": negotiation_id,
            "buyer": buyer_config,
            "seller": seller_config,
            "params": neg_config,
            "rounds": [],
            "start_time": start_time,
        }
        self._negotiations[negotiation_id] = session

        # Transition to negotiation
        self.state = NegotiationState.NEGOTIATING

        # Map UI-facing controls to aspiration exponents.
        buyer_exp = _agent_exponent(buyer_config, objective_mode)
        seller_exp = _agent_exponent(seller_config, objective_mode)

        # Build core NegotiationConfig with price range encompassing both
        # agents' reservation prices plus margin. NegMAS uses discrete integer
        # issue indices, so sub-dollar demo prices are scaled internally.
        price_min = min(buyer_config.initial_price, seller_config.reservation_price) * 0.8
        price_max = max(seller_config.initial_price, buyer_config.reservation_price) * 1.2
        price_scale = 10_000.0 if price_max <= 1.0 else 1.0
        core_price_min = price_min * price_scale
        core_price_max = price_max * price_scale
        # Ensure a sane range (at least 1 unit wide for NegMAS discrete issues)
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

        # Create opponent modelers only for agents running with NegotiatorGrid.
        buyer_om = OpponentModeler(
            is_opponent_seller=True,
            price_min=core_config.price_min,
            price_max=core_config.price_max,
        ) if buyer_config.grid_enabled else None
        seller_om = OpponentModeler(
            is_opponent_seller=False,
            price_min=core_config.price_min,
            price_max=core_config.price_max,
        ) if seller_config.grid_enabled else None

        # Create and run the REAL NegMAS-backed negotiation session
        neg_session = NegotiationSession(
            config=core_config,
            buyer_opponent_modeler=buyer_om,
            seller_opponent_modeler=seller_om,
            buyer_exponent=buyer_exp,
            seller_exponent=seller_exp,
        )
        core_result = neg_session.run()

        # Post-process the transcript: build round-by-round data with
        # opponent model updates, Nash checks, and NL messages
        guardrail = NashGuardrail()
        offer_gen = OfferGenerator(
            model_mode=model_mode,
            provider=neg_config.model_provider,
            model=neg_config.model_name,
            latency_budget_ms=neg_config.model_latency_budget_ms,
        )

        # Group transcript offers into rounds (buyer + seller per round)
        buyer_offers_by_round: dict[int, CoreOffer] = {}
        seller_offers_by_round: dict[int, CoreOffer] = {}
        for offer in core_result.transcript:
            if offer.agent_id == "buyer":
                buyer_offers_by_round[offer.round_number] = offer
            elif offer.agent_id == "seller":
                seller_offers_by_round[offer.round_number] = offer

        all_round_nums = sorted(set(buyer_offers_by_round.keys()) | set(seller_offers_by_round.keys()))

        rounds_data: list[NegotiationRound] = []
        previous_buyer_price: float | None = None
        previous_seller_price: float | None = None
        last_nash_result = None
        for rnd in all_round_nums:
            r_num = rnd + 1  # 0-indexed NegMAS step → 1-indexed round

            b_core = buyer_offers_by_round.get(rnd)
            s_core = seller_offers_by_round.get(rnd)
            buyer_display_price = display_price(b_core.price) if b_core else None
            seller_display_price = display_price(s_core.price) if s_core else None

            # Generate NL messages via OfferGenerator
            buyer_nl = ""
            seller_nl = ""
            if buyer_display_price is not None:
                buyer_nl = offer_gen.generate_buyer_offer(round_num=r_num, price=buyer_display_price)
            if seller_display_price is not None:
                seller_nl = offer_gen.generate_seller_counter(
                    round_num=r_num,
                    price=seller_display_price,
                )

            # Compute aspiration and stance from time
            t = r_num / max(neg_config.max_rounds, 1)

            # Get opponent model snapshot from the buyer's perspective
            opp_model_data = buyer_om.get_model() if buyer_om else None
            opp_model_dict = {
                "estimated_reservation": round(
                    display_price(opp_model_data.estimated_reservation_price)
                    if opp_model_data
                    else 0.0,
                    6,
                ),
                "confidence": round(opp_model_data.confidence if opp_model_data else 0.0, 2),
                "buyer_grid_enabled": buyer_config.grid_enabled,
                "seller_grid_enabled": seller_config.grid_enabled,
            }

            # Nash guardrail check for this round
            nash_status = "N/A"
            nash_price = 0.0
            nash_deviation_pct = 0.0
            if b_core and s_core:
                buyer_price = buyer_display_price or 0.0
                seller_price = seller_display_price or 0.0
                # Simple ZOPA check using the guardrail's logic
                def buyer_ufun(p: float) -> float:
                    return max(0.0, buyer_config.reservation_price - p)

                def seller_ufun(p: float) -> float:
                    return max(0.0, p - seller_config.reservation_price)

                nash_result = guardrail.check_deal(
                    agreed_price=(buyer_price + seller_price) / 2.0,
                    buyer_ufun=buyer_ufun,
                    seller_ufun=seller_ufun,
                    price_min=display_price(core_config.price_min),
                    price_max=display_price(core_config.price_max),
                    grid_size=11,
                )
                last_nash_result = nash_result
                nash_status = "PASS" if nash_result.passed else "WARN"
                nash_price = round(nash_result.nash_price, 6)
                nash_deviation_pct = round(nash_result.deviation_pct, 4)

            buyer_offer = None
            if b_core and buyer_display_price is not None:
                buyer_price = buyer_display_price
                buyer_tendency = _tendency_label(buyer_config)
                buyer_offer = NegotiationOffer(
                    round=r_num,
                    price=buyer_price,
                    scope=neg_config.scope,
                    nl_message=buyer_nl,
                    agent_id=buyer_config.agent_id or "buyer",
                    timestamp=b_core.timestamp,
                    utility=round(1.0 - t * 0.3, 3),
                    aspiration=round(1.0 - t * 0.5, 3),
                    stance=buyer_tendency,
                    reasoning=_reasoning_summary(
                        role="buyer",
                        price=buyer_price,
                        previous_price=previous_buyer_price,
                        objective_mode=objective_mode,
                        grid_enabled=buyer_config.grid_enabled,
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
                seller_tendency = _tendency_label(seller_config)
                seller_model_data = seller_om.get_model() if seller_om else None
                seller_opp_model = {
                    "estimated_reservation": round(
                        display_price(seller_model_data.estimated_reservation_price)
                        if seller_model_data
                        else 0.0,
                        6,
                    ),
                    "confidence": round(seller_model_data.confidence if seller_model_data else 0.0, 2),
                }
                seller_offer = NegotiationOffer(
                    round=r_num,
                    price=seller_price,
                    scope=neg_config.scope,
                    nl_message=seller_nl,
                    agent_id=seller_config.agent_id or "seller",
                    timestamp=s_core.timestamp,
                    utility=round(1.0 - t * 0.25, 3),
                    aspiration=round(1.0 - t * 0.45, 3),
                    stance=seller_tendency,
                    reasoning=_reasoning_summary(
                        role="seller",
                        price=seller_price,
                        previous_price=previous_seller_price,
                        objective_mode=objective_mode,
                        grid_enabled=seller_config.grid_enabled,
                        tendency=seller_tendency,
                        opponent_model=seller_opp_model,
                        nash_status=nash_status,
                        nash_deviation_pct=nash_deviation_pct,
                    ),
                )
                previous_seller_price = seller_price

            neg_round = NegotiationRound(
                round_number=r_num,
                buyer_offer=buyer_offer,
                seller_offer=seller_offer,
                opponent_model=opp_model_dict,
                nash_check=nash_status,
                nash_price=nash_price,
                nash_deviation_pct=nash_deviation_pct,
                runtime=offer_gen.runtime_metrics(),
            )
            rounds_data.append(neg_round)
            session["rounds"].append(neg_round)

            # Broadcast round if callback registered
            if self._on_round:
                try:
                    await self._on_round(negotiation_id, neg_round)
                except Exception:
                    logger.exception("Error in on_round callback")

            # Small delay for visual streaming effect
            await asyncio.sleep(0.1)

        duration = time.time() - start_time
        success = core_result.agreed_price is not None
        agreed_price = display_price(core_result.agreed_price) if core_result.agreed_price else 0.0

        deal_hash = compute_deal_hash(negotiation_id, agreed_price, len(rounds_data)) if success else ""

        # Compute utilities relative to initial/reservation prices
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
        seller_surplus = max(0.0, agreed_price - seller_config.reservation_price) if success else 0.0
        seller_discount = max(0.0, seller_config.initial_price - agreed_price) if success else 0.0
        buyer_movement = max(0.0, agreed_price - buyer_config.initial_price) if success else 0.0
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
            "model_runtime": offer_gen.runtime_metrics(),
            "sandbox": _sandbox_posture(model_mode),
            "edge_case_status": _edge_case_status(
                neg_config.max_rounds,
                neg_config.timeout_seconds,
            ),
        }

        result = NegotiationResult(
            negotiation_id=negotiation_id,
            success=success,
            agreed_price=agreed_price,
            total_rounds=len(rounds_data),
            deal_hash=deal_hash,
            buyer_utility=round(max(0, min(1, buyer_util)), 3),
            seller_utility=round(max(0, min(1, seller_util)), 3),
            duration_seconds=round(duration, 3),
            rounds=rounds_data,
            metrics=metrics,
            objective_mode=objective_mode,
            passport_status=neg_config.passport_status,
            reason=reason,
        )

        self.state = NegotiationState.COMPLETED if success else NegotiationState.FAILED

        if self._on_result:
            try:
                await self._on_result(result)
            except Exception:
                logger.exception("Error in on_result callback")

        return result

    # -- A2A message handling ------------------------------------------------

    def handle_offer(self, message: dict[str, Any]) -> NegotiationOffer:
        """Parse an incoming A2A negotiation-offer message."""
        content = message.get("content", message)
        return NegotiationOffer(
            round=content.get("round", 0),
            price=content.get("price", 0.0),
            scope=content.get("scope", ""),
            nl_message=content.get("nl_message", ""),
            agent_id=content.get("agent_id", ""),
        )

    def handle_accept(self, message: dict[str, Any]) -> NegotiationResult:
        """Parse an incoming A2A negotiation-accept message."""
        content = message.get("content", message)
        return NegotiationResult(
            success=True,
            agreed_price=content.get("agreed_price", 0.0),
            total_rounds=content.get("total_rounds", 0),
            deal_hash=content.get("deal_hash", ""),
        )

    # -- A2A message construction -------------------------------------------

    @staticmethod
    def build_offer_message(offer: NegotiationOffer) -> dict[str, Any]:
        """Build an A2A negotiation-offer metadata payload."""
        return {
            "type": "negotiation-offer",
            "content": offer.to_dict(),
        }

    @staticmethod
    def build_counteroffer_message(offer: NegotiationOffer) -> dict[str, Any]:
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
