"""Opponent modeling — estimate counterparty behaviour from observed offers.

Tracks incoming offers, uses linear regression on concession patterns to
estimate the opponent's reservation price, classifies their type as
aggressive / moderate / generous, and recommends strategy adjustments.
"""

from __future__ import annotations

import math

from negotiatorgrid.core.types import (
    NegotiationOffer,
    OpponentModel,
    OpponentType,
)


class OpponentModeler:
    """Stateful opponent model that updates incrementally with each observed offer.

    Usage::

        modeler = OpponentModeler(is_opponent_seller=True, price_min=0, price_max=100)
        modeler.update(offer)          # call for each counterparty offer
        model = modeler.get_model()    # OpponentModel snapshot
        adj = modeler.strategy_adjustment()
    """

    def __init__(
        self,
        *,
        is_opponent_seller: bool = True,
        price_min: float = 0.0,
        price_max: float = 100.0,
    ) -> None:
        self.is_opponent_seller = is_opponent_seller
        self.price_min = price_min
        self.price_max = price_max
        self._offers: list[NegotiationOffer] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, offer: NegotiationOffer) -> None:
        """Record a new offer from the counterparty."""
        self._offers.append(offer)

    def estimate_reservation_price(self) -> float:
        """Estimate the opponent's reservation price via linear extrapolation.

        Fits a simple linear regression on (round, price) pairs and
        extrapolates to where the opponent would converge (t → 1.0).
        """
        if len(self._offers) < 2:
            # Not enough data — return a neutral mid-point guess
            return (self.price_min + self.price_max) / 2.0

        xs = [float(o.round_number) for o in self._offers]
        ys = [o.price for o in self._offers]
        slope, intercept = self._linear_regression(xs, ys)

        # Extrapolate to a high round number as proxy for "deadline"
        max_round = max(xs) + 5
        projected = slope * max_round + intercept
        return max(self.price_min, min(self.price_max, projected))

    def estimate_type(self) -> OpponentType:
        """Classify opponent based on concession speed.

        Concession rate = average per-round change in price toward a deal.
        For a seller, concession means prices going *down*.
        For a buyer, concession means prices going *up*.
        """
        rate = self._concession_rate()
        if rate is None:
            return OpponentType.MODERATE

        # Thresholds tuned for a [0, 100] price range over ~7 rounds
        price_range = self.price_max - self.price_min
        normalised = abs(rate) / max(price_range, 1.0) * 7.0  # per-negotiation %

        if normalised < 0.10:
            return OpponentType.AGGRESSIVE  # barely conceding
        elif normalised > 0.30:
            return OpponentType.GENEROUS  # conceding fast
        return OpponentType.MODERATE

    def get_confidence(self) -> float:
        """Confidence in the model — rises with # observations.

        Returns a value in [0, 1].  Reaches 0.8 at ~5 observations.
        """
        n = len(self._offers)
        if n == 0:
            return 0.0
        return min(1.0, 1.0 - math.exp(-0.35 * n))

    def get_model(self) -> OpponentModel:
        """Return a snapshot of the current opponent model."""
        return OpponentModel(
            estimated_reservation_price=self.estimate_reservation_price(),
            concession_rate=self._concession_rate() or 0.0,
            estimated_type=self.estimate_type(),
            confidence=self.get_confidence(),
        )

    def strategy_adjustment(self) -> dict[str, float]:
        """Recommend strategy parameter tweaks based on opponent type.

        Returns
        -------
        dict with ``concession_rate`` and ``walk_away_threshold`` modifiers.
        """
        otype = self.estimate_type()
        if otype == OpponentType.AGGRESSIVE:
            return {"concession_rate": 0.5, "walk_away_threshold": 0.7}
        elif otype == OpponentType.GENEROUS:
            return {"concession_rate": 1.5, "walk_away_threshold": 0.3}
        return {"concession_rate": 1.0, "walk_away_threshold": 0.5}

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _concession_rate(self) -> float | None:
        """Average per-round price change (signed).

        Positive means prices are increasing; negative means decreasing.
        """
        if len(self._offers) < 2:
            return None
        deltas: list[float] = []
        for i in range(1, len(self._offers)):
            deltas.append(self._offers[i].price - self._offers[i - 1].price)
        return sum(deltas) / len(deltas)

    @staticmethod
    def _linear_regression(xs: list[float], ys: list[float]) -> tuple[float, float]:
        """Simple OLS linear regression returning (slope, intercept)."""
        n = len(xs)
        if n == 0:
            return 0.0, 0.0
        sum_x = sum(xs)
        sum_y = sum(ys)
        sum_xy = sum(x * y for x, y in zip(xs, ys))
        sum_x2 = sum(x * x for x in xs)
        denom = n * sum_x2 - sum_x * sum_x
        if abs(denom) < 1e-12:
            return 0.0, sum_y / n
        slope = (n * sum_xy - sum_x * sum_y) / denom
        intercept = (sum_y - slope * sum_x) / n
        return slope, intercept
