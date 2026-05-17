"""NegMAS SAO integration — bilateral price negotiation engine.

Wraps NegMAS ``SAOMechanism`` with custom buyer/seller negotiators
that use aspiration-based (Boulware) concession strategies with
opponent-model feedback.
"""

from __future__ import annotations

import hashlib
import time
from typing import TYPE_CHECKING

from negmas.outcomes import make_issue
from negmas.preferences import LinearAdditiveUtilityFunction
from negmas.preferences.value_fun import AffineFun
from negmas.sao import ResponseType, SAOMechanism, SAONegotiator, SAOState

from negotiatorgrid.core.types import (
    NegotiationConfig,
    NegotiationOffer,
    NegotiationResult,
    OpponentModel as OpponentModelData,
)

if TYPE_CHECKING:
    from negotiatorgrid.core.opponent_model import OpponentModeler


# ---------------------------------------------------------------------------
# Aspiration helpers
# ---------------------------------------------------------------------------

_EXPONENT_MAP: dict[str, float] = {
    "boulware": 4.0,
    "linear": 1.0,
    "conceder": 0.25,
}


def aspiration_value(t: float, exponent: float, max_asp: float = 1.0) -> float:
    """Compute aspiration level at relative time *t* ∈ [0, 1].

    ``u(t) = max_asp * (1 - t^exponent)``
    """
    t = max(0.0, min(1.0, t))
    return max_asp * (1.0 - t ** exponent)


def price_from_aspiration(
    asp: float,
    reservation: float,
    opponent_reservation: float,
    is_buyer: bool,
) -> float:
    """Map an aspiration level (1 = best for me, 0 = worst) to a price.

    For a **buyer** (``reservation`` = max they'd pay, ``opponent_reservation``
    = min the seller would accept):
      asp 1.0 → ``opponent_reservation`` (best for buyer: pay the minimum)
      asp 0.0 → ``reservation`` (worst: pay up to their max)

    For a **seller** (``reservation`` = min they'd accept,
    ``opponent_reservation`` = max the buyer would pay):
      asp 1.0 → ``opponent_reservation`` (best for seller: get the maximum)
      asp 0.0 → ``reservation`` (worst: accept the minimum)
    """
    if is_buyer:
        # asp=1 → opponent_reservation (low, ideal for buyer)
        # asp=0 → reservation (high, buyer's walk-away ceiling)
        return opponent_reservation + (1.0 - asp) * (reservation - opponent_reservation)
    else:
        # asp=1 → opponent_reservation (high, ideal for seller)
        # asp=0 → reservation (low, seller's walk-away floor)
        return opponent_reservation - (1.0 - asp) * (opponent_reservation - reservation)


# ---------------------------------------------------------------------------
# Custom SAO negotiators
# ---------------------------------------------------------------------------


class BuyerNegotiator(SAONegotiator):
    """Buyer-side negotiator using aspiration-based concession.

    Starts near *buyer_reservation* (low price) and concedes **up** toward
    the seller's reservation over time.  Uses a Boulware curve by default
    (exponent = 4.0 → slow concession, large jumps near deadline).
    """

    def __init__(
        self,
        buyer_reservation: float,
        seller_reservation: float,
        price_min: float,
        price_max: float,
        exponent: float = 4.0,
        opponent_modeler: OpponentModeler | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.buyer_reservation = buyer_reservation
        self.seller_reservation = seller_reservation
        self.price_min = price_min
        self.price_max = price_max
        self.base_exponent = exponent
        self.opponent_modeler = opponent_modeler
        self._offers: list[NegotiationOffer] = []

    @property
    def _exponent(self) -> float:
        if self.opponent_modeler is None:
            return self.base_exponent
        om = self.opponent_modeler.get_model()
        if om.estimated_type.value == "aggressive":
            return max(self.base_exponent, 4.0)  # hold firm
        elif om.estimated_type.value == "generous":
            return min(self.base_exponent, 0.5)  # reciprocate
        return self.base_exponent

    def _price_to_outcome_index(self, price: float) -> int:
        """Convert a float price to the nearest discrete outcome index."""
        n = int(self.price_max - self.price_min)
        idx = int(round(price - self.price_min))
        return max(0, min(n - 1, idx))

    def propose(self, state: SAOState, dest: str | None = None):
        t = state.relative_time
        asp = aspiration_value(t, self._exponent)
        price = price_from_aspiration(
            asp, self.buyer_reservation, self.seller_reservation, is_buyer=True
        )
        # Hard-clamp: buyer never offers above their reservation price
        price = max(self.price_min, min(self.buyer_reservation, price))
        idx = self._price_to_outcome_index(price)
        offer = NegotiationOffer(
            round_number=state.step,
            price=self.price_min + idx,
            agent_id=self.name or "buyer",
            timestamp=time.time(),
        )
        self._offers.append(offer)
        return (idx,)

    def respond(self, state: SAOState, source: str | None = None) -> ResponseType:
        offer = state.current_offer
        if offer is None:
            return ResponseType.REJECT_OFFER

        offered_price = self.price_min + offer[0]

        # Feed opponent modeler
        if self.opponent_modeler is not None:
            self.opponent_modeler.update(
                NegotiationOffer(
                    round_number=state.step,
                    price=offered_price,
                    agent_id=source or "seller",
                    timestamp=time.time(),
                )
            )

        # Hard limit: never accept above buyer's reservation
        if offered_price > self.buyer_reservation:
            return ResponseType.REJECT_OFFER

        t = state.relative_time
        asp = aspiration_value(t, self._exponent)
        threshold_price = price_from_aspiration(
            asp, self.buyer_reservation, self.seller_reservation, is_buyer=True
        )
        # Clamp threshold to reservation
        threshold_price = min(threshold_price, self.buyer_reservation)

        if offered_price <= threshold_price:
            self._offers.append(
                NegotiationOffer(
                    round_number=state.step,
                    price=offered_price,
                    agent_id=source or "seller",
                    timestamp=time.time(),
                )
            )
            return ResponseType.ACCEPT_OFFER
        return ResponseType.REJECT_OFFER


class SellerNegotiator(SAONegotiator):
    """Seller-side negotiator using time-dependent aspiration.

    Starts near *seller_reservation* (high price) and concedes **down**
    toward the buyer's reservation.
    """

    def __init__(
        self,
        buyer_reservation: float,
        seller_reservation: float,
        price_min: float,
        price_max: float,
        exponent: float = 4.0,
        opponent_modeler: OpponentModeler | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.buyer_reservation = buyer_reservation
        self.seller_reservation = seller_reservation
        self.price_min = price_min
        self.price_max = price_max
        self.base_exponent = exponent
        self.opponent_modeler = opponent_modeler
        self._offers: list[NegotiationOffer] = []

    @property
    def _exponent(self) -> float:
        if self.opponent_modeler is None:
            return self.base_exponent
        om = self.opponent_modeler.get_model()
        if om.estimated_type.value == "aggressive":
            return max(self.base_exponent, 4.0)
        elif om.estimated_type.value == "generous":
            return min(self.base_exponent, 0.5)
        return self.base_exponent

    def _price_to_outcome_index(self, price: float) -> int:
        n = int(self.price_max - self.price_min)
        idx = int(round(price - self.price_min))
        return max(0, min(n - 1, idx))

    def propose(self, state: SAOState, dest: str | None = None):
        t = state.relative_time
        asp = aspiration_value(t, self._exponent)
        price = price_from_aspiration(
            asp, self.seller_reservation, self.buyer_reservation, is_buyer=False
        )
        # Hard-clamp: seller never offers below their reservation price
        price = max(self.seller_reservation, min(self.price_max, price))
        idx = self._price_to_outcome_index(price)
        offer = NegotiationOffer(
            round_number=state.step,
            price=self.price_min + idx,
            agent_id=self.name or "seller",
            timestamp=time.time(),
        )
        self._offers.append(offer)
        return (idx,)

    def respond(self, state: SAOState, source: str | None = None) -> ResponseType:
        offer = state.current_offer
        if offer is None:
            return ResponseType.REJECT_OFFER

        offered_price = self.price_min + offer[0]

        if self.opponent_modeler is not None:
            self.opponent_modeler.update(
                NegotiationOffer(
                    round_number=state.step,
                    price=offered_price,
                    agent_id=source or "buyer",
                    timestamp=time.time(),
                )
            )

        # Hard limit: never accept below seller's reservation
        if offered_price < self.seller_reservation:
            return ResponseType.REJECT_OFFER

        t = state.relative_time
        asp = aspiration_value(t, self._exponent)
        threshold_price = price_from_aspiration(
            asp, self.seller_reservation, self.buyer_reservation, is_buyer=False
        )
        # Clamp threshold to reservation
        threshold_price = max(threshold_price, self.seller_reservation)

        if offered_price >= threshold_price:
            self._offers.append(
                NegotiationOffer(
                    round_number=state.step,
                    price=offered_price,
                    agent_id=source or "buyer",
                    timestamp=time.time(),
                )
            )
            return ResponseType.ACCEPT_OFFER
        return ResponseType.REJECT_OFFER


# ---------------------------------------------------------------------------
# NegotiationSession — orchestrates the mechanism
# ---------------------------------------------------------------------------


class NegotiationSession:
    """Wraps a NegMAS ``SAOMechanism`` for bilateral price negotiation.

    Parameters
    ----------
    config:
        Negotiation parameters (max rounds, timeout, price range, reservations).
    buyer_profile / seller_profile:
        Optional ``AgentProfile`` instances for reputation-aware strategy.
    buyer_opponent_modeler / seller_opponent_modeler:
        Optional ``OpponentModeler`` instances injected into the negotiators.
    buyer_exponent / seller_exponent:
        Aspiration-curve exponents (default 4.0 = Boulware).
    """

    def __init__(
        self,
        config: NegotiationConfig | None = None,
        *,
        buyer_opponent_modeler: OpponentModeler | None = None,
        seller_opponent_modeler: OpponentModeler | None = None,
        buyer_exponent: float = 4.0,
        seller_exponent: float = 4.0,
    ) -> None:
        self.config = config or NegotiationConfig()
        self.buyer_opponent_modeler = buyer_opponent_modeler
        self.seller_opponent_modeler = seller_opponent_modeler
        self.buyer_exponent = buyer_exponent
        self.seller_exponent = seller_exponent

    def run(self) -> NegotiationResult:
        """Execute the negotiation and return the result."""
        cfg = self.config
        n_values = max(2, int(cfg.price_max - cfg.price_min))

        issues = [make_issue(values=n_values, name="price")]
        mechanism = SAOMechanism(
            issues=issues,
            n_steps=cfg.max_rounds,
            time_limit=cfg.timeout_seconds,
        )

        # Utility: buyer prefers low index (low price), seller prefers high
        buyer_ufun = LinearAdditiveUtilityFunction(
            values={"price": AffineFun(slope=-1, bias=float(n_values - 1))},
            outcome_space=mechanism.outcome_space,
        )
        seller_ufun = LinearAdditiveUtilityFunction(
            values={"price": AffineFun(slope=1, bias=0.0)},
            outcome_space=mechanism.outcome_space,
        )

        buyer = BuyerNegotiator(
            buyer_reservation=cfg.buyer_reservation,
            seller_reservation=cfg.seller_reservation,
            price_min=cfg.price_min,
            price_max=cfg.price_max,
            exponent=self.buyer_exponent,
            opponent_modeler=self.buyer_opponent_modeler,
            name="buyer",
        )
        seller = SellerNegotiator(
            buyer_reservation=cfg.buyer_reservation,
            seller_reservation=cfg.seller_reservation,
            price_min=cfg.price_min,
            price_max=cfg.price_max,
            exponent=self.seller_exponent,
            opponent_modeler=self.seller_opponent_modeler,
            name="seller",
        )

        mechanism.add(buyer, ufun=buyer_ufun)
        mechanism.add(seller, ufun=seller_ufun)

        start = time.time()
        state = mechanism.run()
        elapsed_ms = (time.time() - start) * 1000.0

        # Build transcript from both negotiators' recorded offers
        transcript = sorted(
            buyer._offers + seller._offers,
            key=lambda o: (o.round_number, o.timestamp),
        )

        agreed_price: float | None = None
        if state.agreement is not None:
            agreed_price = cfg.price_min + state.agreement[0]

        deal_hash = ""
        deal_bound_at = 0
        if agreed_price is not None:
            deal_bound_at = int(time.time())
            raw = f"buyer:seller:{agreed_price}:{state.step}:{deal_bound_at}"
            deal_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]

        return NegotiationResult(
            agreed_price=agreed_price,
            rounds=state.step,
            transcript=transcript,
            buyer_id="buyer",
            seller_id="seller",
            duration_ms=elapsed_ms,
            deal_hash=deal_hash,
            deal_bound_at=deal_bound_at,
        )
