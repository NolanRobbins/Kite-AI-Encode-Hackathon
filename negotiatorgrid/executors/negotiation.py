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
        }


@dataclass
class NegotiationRound:
    """One complete round: buyer offer + seller counter."""

    round_number: int
    buyer_offer: Optional[NegotiationOffer] = None
    seller_offer: Optional[NegotiationOffer] = None
    opponent_model: dict[str, Any] = field(default_factory=dict)
    nash_check: str = "N/A"

    def to_dict(self) -> dict[str, Any]:
        return {
            "round": self.round_number,
            "buyer_offer": self.buyer_offer.price if self.buyer_offer else None,
            "seller_offer": self.seller_offer.price if self.seller_offer else None,
            "buyer_nl": self.buyer_offer.nl_message if self.buyer_offer else "",
            "seller_nl": self.seller_offer.nl_message if self.seller_offer else "",
            "opponent_model": self.opponent_model,
            "nash_check": self.nash_check,
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


@dataclass
class NegotiationParams:
    """Parameters controlling the negotiation session."""

    max_rounds: int = 7
    timeout_seconds: int = 30
    resource_uri: str = "/api/service"
    scope: str = "weather-data"


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


def compute_deal_hash(negotiation_id: str, agreed_price: float, rounds: int) -> str:
    """Compute a keccak-like hash (sha256 stand-in) for the deal."""
    payload = json.dumps(
        {"negotiation_id": negotiation_id, "agreed_price": agreed_price, "rounds": rounds},
        sort_keys=True,
    )
    return "0x" + hashlib.sha256(payload.encode()).hexdigest()


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

        # Map strategy names to aspiration exponents
        buyer_exp = _STRATEGY_EXPONENTS.get(buyer_config.strategy, 4.0)
        seller_exp = _STRATEGY_EXPONENTS.get(seller_config.strategy, 4.0)

        # Build core NegotiationConfig with price range encompassing both
        # agents' reservation prices plus margin
        price_min = min(buyer_config.initial_price, seller_config.reservation_price) * 0.8
        price_max = max(seller_config.initial_price, buyer_config.reservation_price) * 1.2
        # Ensure a sane range (at least 1 unit wide for NegMAS discrete issues)
        if price_max - price_min < 1.0:
            price_min = min(buyer_config.initial_price, seller_config.reservation_price) - 1.0
            price_max = max(seller_config.initial_price, buyer_config.reservation_price) + 1.0

        core_config = CoreNegConfig(
            max_rounds=neg_config.max_rounds,
            timeout_seconds=neg_config.timeout_seconds,
            price_min=price_min,
            price_max=price_max,
            buyer_reservation=buyer_config.reservation_price,
            seller_reservation=seller_config.reservation_price,
        )

        # Create opponent modelers
        buyer_om = OpponentModeler(
            is_opponent_seller=True,
            price_min=core_config.price_min,
            price_max=core_config.price_max,
        )
        seller_om = OpponentModeler(
            is_opponent_seller=False,
            price_min=core_config.price_min,
            price_max=core_config.price_max,
        )

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
        offer_gen = OfferGenerator()  # No API key = template mode

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
        for rnd in all_round_nums:
            r_num = rnd + 1  # 0-indexed NegMAS step → 1-indexed round

            b_core = buyer_offers_by_round.get(rnd)
            s_core = seller_offers_by_round.get(rnd)

            # Generate NL messages via OfferGenerator
            buyer_nl = ""
            seller_nl = ""
            if b_core:
                buyer_nl = offer_gen.generate_buyer_offer(round_num=r_num, price=b_core.price)
            if s_core:
                seller_nl = offer_gen.generate_seller_counter(round_num=r_num, price=s_core.price)

            # Compute aspiration and stance from time
            t = r_num / max(neg_config.max_rounds, 1)

            buyer_offer = None
            if b_core:
                buyer_offer = NegotiationOffer(
                    round=r_num,
                    price=b_core.price,
                    scope=neg_config.scope,
                    nl_message=buyer_nl,
                    agent_id=buyer_config.agent_id or "buyer",
                    timestamp=b_core.timestamp,
                    utility=round(1.0 - t * 0.3, 3),
                    aspiration=round(1.0 - t * 0.5, 3),
                    stance="generous" if t > 0.6 else "neutral",
                )

            seller_offer = None
            if s_core:
                seller_offer = NegotiationOffer(
                    round=r_num,
                    price=s_core.price,
                    scope=neg_config.scope,
                    nl_message=seller_nl,
                    agent_id=seller_config.agent_id or "seller",
                    timestamp=s_core.timestamp,
                    utility=round(1.0 - t * 0.25, 3),
                    aspiration=round(1.0 - t * 0.45, 3),
                    stance="generous" if t > 0.6 else "neutral",
                )

            # Get opponent model snapshot from the buyer's perspective
            opp_model_data = buyer_om.get_model()
            opp_model_dict = {
                "estimated_reservation": round(opp_model_data.estimated_reservation_price, 6),
                "confidence": round(opp_model_data.confidence, 2),
            }

            # Nash guardrail check for this round
            nash_status = "N/A"
            if b_core and s_core:
                buyer_price = b_core.price
                seller_price = s_core.price
                # Simple ZOPA check using the guardrail's logic
                def buyer_ufun(p: float) -> float:
                    return max(0.0, buyer_config.reservation_price - p)

                def seller_ufun(p: float) -> float:
                    return max(0.0, p - seller_config.reservation_price)

                nash_result = guardrail.check_deal(
                    agreed_price=(buyer_price + seller_price) / 2.0,
                    buyer_ufun=buyer_ufun,
                    seller_ufun=seller_ufun,
                    price_min=core_config.price_min,
                    price_max=core_config.price_max,
                    grid_size=11,
                )
                nash_status = "PASS" if nash_result.passed else "WARN"

            neg_round = NegotiationRound(
                round_number=r_num,
                buyer_offer=buyer_offer,
                seller_offer=seller_offer,
                opponent_model=opp_model_dict,
                nash_check=nash_status,
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
        agreed_price = core_result.agreed_price or 0.0

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
