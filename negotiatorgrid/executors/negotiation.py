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
# Simple built-in alternating-offers protocol
# ---------------------------------------------------------------------------

def _aspiration_offer(
    initial: float,
    reservation: float,
    t: float,
    concession_exponent: float = 2.0,
) -> float:
    """Time-dependent aspiration strategy.

    t in [0, 1] is the normalised negotiation time.
    concession_exponent > 1 → Boulware (slow concession early, fast late)
    concession_exponent < 1 → Conceder (fast early, slow late)
    concession_exponent == 1 → Linear
    """
    return initial + (reservation - initial) * (t ** concession_exponent)


def _concession_exponent(strategy: str) -> float:
    """Map strategy name to concession exponent."""
    return {
        "aspiration": 1.5,
        "boulware": 3.0,
        "tit-for-tat": 1.0,
        "conceder": 0.5,
    }.get(strategy, 1.5)


def _generate_nl_message(role: str, price: float, round_num: int, total_rounds: int) -> str:
    """Generate a natural-language negotiation message (no LLM required)."""
    t = round_num / max(total_rounds, 1)
    if role == "buyer":
        if t < 0.3:
            return f"I'd like to start at ${price:.4f} per call. I believe this is a fair market rate given current alternatives."
        elif t < 0.7:
            return f"I can move to ${price:.4f}. Let's find middle ground — I value a long-term relationship."
        else:
            return f"My best offer is ${price:.4f}. I'm close to my limit but want to make this work."
    else:
        if t < 0.3:
            return f"My service is worth ${price:.4f} per call — sub-150ms latency with 99.9% uptime."
        elif t < 0.7:
            return f"I can come down to ${price:.4f}. This still covers my operational costs."
        else:
            return f"${price:.4f} is my minimum. I've settled 47 deals at this quality tier."


def _estimate_opponent_reservation(offers: list[float]) -> dict[str, Any]:
    """Simple opponent model: linear extrapolation of concession trend."""
    if len(offers) < 2:
        return {"estimated_reservation": None, "confidence": 0.0}
    deltas = [offers[i] - offers[i - 1] for i in range(1, len(offers))]
    avg_delta = sum(deltas) / len(deltas)
    if abs(avg_delta) < 1e-9:
        est = offers[-1]
    else:
        remaining_steps = max(3, len(offers))
        est = offers[-1] + avg_delta * remaining_steps
    confidence = min(0.9, 0.3 + 0.15 * len(offers))
    return {"estimated_reservation": round(est, 6), "confidence": round(confidence, 2)}


def _nash_check(buyer_price: float, seller_price: float, buyer_res: float, seller_res: float) -> str:
    """Simplified Nash-bargaining check: are both parties inside the ZOPA?"""
    zopa_low = min(buyer_res, seller_res)
    zopa_high = max(buyer_res, seller_res)
    mid = (buyer_price + seller_price) / 2
    if zopa_low <= mid <= zopa_high:
        return "PASS"
    gap = abs(buyer_price - seller_price)
    if gap < 0.02:
        return "PASS"
    return "WARN"


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

    Bridges alternating-offers protocol to A2A Task lifecycle messages.
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

        # Store session
        session: dict[str, Any] = {
            "id": negotiation_id,
            "buyer": buyer_config,
            "seller": seller_config,
            "params": neg_config,
            "rounds": [],
            "buyer_offers": [],
            "seller_offers": [],
            "start_time": start_time,
        }
        self._negotiations[negotiation_id] = session

        # Transition to negotiation
        self.state = NegotiationState.NEGOTIATING

        buyer_exp = _concession_exponent(buyer_config.strategy)
        seller_exp = _concession_exponent(seller_config.strategy)

        agreed_price = 0.0
        success = False
        reason = "max_rounds_reached"

        for r in range(1, neg_config.max_rounds + 1):
            t = r / neg_config.max_rounds

            # Buyer offer
            buyer_price = _aspiration_offer(
                buyer_config.initial_price,
                buyer_config.reservation_price,
                t,
                buyer_exp,
            )
            buyer_price = round(buyer_price, 6)
            buyer_nl = _generate_nl_message("buyer", buyer_price, r, neg_config.max_rounds)
            buyer_offer = NegotiationOffer(
                round=r,
                price=buyer_price,
                scope=neg_config.scope,
                nl_message=buyer_nl,
                agent_id=buyer_config.agent_id,
                utility=round(1.0 - t * 0.3, 3),
                aspiration=round(1.0 - t * 0.5, 3),
                stance="generous" if t > 0.6 else "neutral",
            )
            session["buyer_offers"].append(buyer_price)

            # Seller offer
            seller_price = _aspiration_offer(
                seller_config.initial_price,
                seller_config.reservation_price,
                t,
                seller_exp,
            )
            seller_price = round(seller_price, 6)
            seller_nl = _generate_nl_message("seller", seller_price, r, neg_config.max_rounds)
            seller_offer = NegotiationOffer(
                round=r,
                price=seller_price,
                scope=neg_config.scope,
                nl_message=seller_nl,
                agent_id=seller_config.agent_id,
                utility=round(1.0 - t * 0.25, 3),
                aspiration=round(1.0 - t * 0.45, 3),
                stance="generous" if t > 0.6 else "neutral",
            )
            session["seller_offers"].append(seller_price)

            # Opponent models
            opp_model = _estimate_opponent_reservation(session["seller_offers"])
            nash = _nash_check(
                buyer_price,
                seller_price,
                buyer_config.reservation_price,
                seller_config.reservation_price,
            )

            neg_round = NegotiationRound(
                round_number=r,
                buyer_offer=buyer_offer,
                seller_offer=seller_offer,
                opponent_model=opp_model,
                nash_check=nash,
            )
            session["rounds"].append(neg_round)

            # Broadcast round if callback registered
            if self._on_round:
                try:
                    await self._on_round(negotiation_id, neg_round)
                except Exception:
                    logger.exception("Error in on_round callback")

            # Small delay for realism
            await asyncio.sleep(0.1)

            # Check for acceptance: buyer price >= seller price → deal
            if buyer_price >= seller_price:
                agreed_price = round((buyer_price + seller_price) / 2, 6)
                success = True
                reason = "agreement"
                break

        duration = time.time() - start_time
        deal_hash = compute_deal_hash(negotiation_id, agreed_price, len(session["rounds"])) if success else ""

        # Compute utilities
        if success and buyer_config.reservation_price != buyer_config.initial_price:
            buyer_util = 1.0 - (agreed_price - buyer_config.initial_price) / (
                buyer_config.reservation_price - buyer_config.initial_price
            )
        else:
            buyer_util = 0.0

        if success and seller_config.initial_price != seller_config.reservation_price:
            seller_util = 1.0 - (seller_config.initial_price - agreed_price) / (
                seller_config.initial_price - seller_config.reservation_price
            )
        else:
            seller_util = 0.0

        result = NegotiationResult(
            negotiation_id=negotiation_id,
            success=success,
            agreed_price=agreed_price,
            total_rounds=len(session["rounds"]),
            deal_hash=deal_hash,
            buyer_utility=round(max(0, min(1, buyer_util)), 3),
            seller_utility=round(max(0, min(1, seller_util)), 3),
            duration_seconds=round(duration, 3),
            rounds=session["rounds"],
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
