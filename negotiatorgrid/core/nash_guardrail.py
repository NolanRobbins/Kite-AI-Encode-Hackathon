"""Nash equilibrium guardrail — game-theoretic deal validation.

Discretises the price range into a payoff matrix, finds the pure-strategy
Nash equilibrium, and flags agreed prices that deviate too far from it.

Uses ``pygambit`` when available; otherwise falls back to a brute-force
best-response enumeration for pure-strategy NE.
"""

from __future__ import annotations

from typing import Callable

from negotiatorgrid.core.types import NashGuardrailResult

# Try to import pygambit; fall back gracefully.
try:
    import pygambit as gbt

    _HAS_GAMBIT = True
except ImportError:
    _HAS_GAMBIT = False


# Type alias for a utility function: price → float utility
UtilityFn = Callable[[float], float]


class NashGuardrail:
    """Compute Nash equilibria and validate negotiated prices.

    Parameters
    ----------
    deviation_threshold:
        Maximum acceptable fractional deviation from the Nash price.
        Default 0.20 (20%).
    """

    def __init__(self, deviation_threshold: float = 0.20) -> None:
        self.deviation_threshold = deviation_threshold

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute_nash(
        self,
        buyer_ufun: UtilityFn,
        seller_ufun: UtilityFn,
        price_min: float,
        price_max: float,
        grid_size: int = 10,
    ) -> NashGuardrailResult:
        """Find Nash equilibrium price over a discretised price grid.

        Both *buyer_ufun* and *seller_ufun* take a single float price
        argument and return the player's utility for that price.
        """
        prices = self._price_grid(price_min, price_max, grid_size)

        if _HAS_GAMBIT:
            return self._compute_nash_gambit(buyer_ufun, seller_ufun, prices)
        return self._compute_nash_bruteforce(buyer_ufun, seller_ufun, prices)

    def check_deal(
        self,
        agreed_price: float,
        buyer_ufun: UtilityFn,
        seller_ufun: UtilityFn,
        price_min: float = 0.0,
        price_max: float = 100.0,
        grid_size: int = 10,
    ) -> NashGuardrailResult:
        """Check whether *agreed_price* is close to Nash equilibrium.

        Returns a ``NashGuardrailResult`` with ``passed=True`` if the
        deviation is within threshold.
        """
        result = self.compute_nash(buyer_ufun, seller_ufun, price_min, price_max, grid_size)
        if result.nash_price == 0.0:
            result.passed = True
            return result

        deviation = abs(agreed_price - result.nash_price) / max(abs(result.nash_price), 1e-9)
        result.deviation_pct = deviation
        result.passed = deviation <= self.deviation_threshold
        return result

    # ------------------------------------------------------------------
    # Internal: pygambit path
    # ------------------------------------------------------------------

    def _compute_nash_gambit(
        self,
        buyer_ufun: UtilityFn,
        seller_ufun: UtilityFn,
        prices: list[float],
    ) -> NashGuardrailResult:
        """Use pygambit to find Nash equilibria via support enumeration."""
        n = len(prices)
        game = gbt.Game.new_table([n, n])  # type: ignore[union-attr]
        game.players[0].label = "Buyer"
        game.players[1].label = "Seller"

        for i, bp in enumerate(prices):
            for j, sp in enumerate(prices):
                game[i, j][game.players[0]] = gbt.Rational(int(buyer_ufun(bp) * 1000), 1000)  # type: ignore[union-attr]
                game[i, j][game.players[1]] = gbt.Rational(int(seller_ufun(sp) * 1000), 1000)  # type: ignore[union-attr]

        result = gbt.nash.lcp_solve(game)  # type: ignore[union-attr]
        eqs = result.equilibria
        if not eqs:
            return self._fallback_nash(buyer_ufun, seller_ufun, prices)

        # Use the first equilibrium found
        eq = eqs[0]
        buyer_probs = [float(eq[game.players[0].strategies[i]]) for i in range(n)]
        seller_probs = [float(eq[game.players[1].strategies[j]]) for j in range(n)]

        buyer_price = sum(p * pr for p, pr in zip(prices, buyer_probs))
        seller_price = sum(p * pr for p, pr in zip(prices, seller_probs))
        nash_price = (buyer_price + seller_price) / 2.0

        return NashGuardrailResult(
            nash_price=nash_price,
            deviation_pct=0.0,
            passed=True,
            strategy_profile=f"gambit_lcp|buyer_idx={buyer_probs}|seller_idx={seller_probs}",
        )

    # ------------------------------------------------------------------
    # Internal: brute-force pure-strategy NE
    # ------------------------------------------------------------------

    def _compute_nash_bruteforce(
        self,
        buyer_ufun: UtilityFn,
        seller_ufun: UtilityFn,
        prices: list[float],
    ) -> NashGuardrailResult:
        """Find pure-strategy Nash equilibria by best-response enumeration.

        For each pair (i, j) check whether i is a best response for the
        buyer given seller plays j, and j is a best response for the seller
        given buyer plays i.
        """
        n = len(prices)
        if n == 0:
            return NashGuardrailResult()

        # Build payoff matrices
        buyer_payoff = [[buyer_ufun(prices[i]) for j in range(n)] for i in range(n)]
        seller_payoff = [[seller_ufun(prices[j]) for j in range(n)] for i in range(n)]

        # For each column j, find buyer's best row
        buyer_br: dict[int, set[int]] = {}
        for j in range(n):
            max_u = max(buyer_payoff[i][j] for i in range(n))
            buyer_br[j] = {i for i in range(n) if abs(buyer_payoff[i][j] - max_u) < 1e-9}

        # For each row i, find seller's best column
        seller_br: dict[int, set[int]] = {}
        for i in range(n):
            max_u = max(seller_payoff[i][j] for j in range(n))
            seller_br[i] = {j for j in range(n) if abs(seller_payoff[i][j] - max_u) < 1e-9}

        # NE: (i, j) where i ∈ buyer_br[j] and j ∈ seller_br[i]
        ne_pairs: list[tuple[int, int]] = []
        for j in range(n):
            for i in buyer_br[j]:
                if j in seller_br[i]:
                    ne_pairs.append((i, j))

        if not ne_pairs:
            return self._fallback_nash(buyer_ufun, seller_ufun, prices)

        # Average NE price across all equilibria found
        ne_prices = [(prices[i] + prices[j]) / 2.0 for i, j in ne_pairs]
        nash_price = sum(ne_prices) / len(ne_prices)

        return NashGuardrailResult(
            nash_price=nash_price,
            deviation_pct=0.0,
            passed=True,
            strategy_profile=f"bruteforce|ne_count={len(ne_pairs)}|pairs={ne_pairs[:5]}",
        )

    # ------------------------------------------------------------------
    # Fallback: Nash Bargaining Solution (analytical)
    # ------------------------------------------------------------------

    def _fallback_nash(
        self,
        buyer_ufun: UtilityFn,
        seller_ufun: UtilityFn,
        prices: list[float],
    ) -> NashGuardrailResult:
        """When no pure-strategy NE is found, use the Nash Bargaining Solution.

        NBS = argmax_{p} (buyer_ufun(p) * seller_ufun(p)) subject to both
        utilities being non-negative.
        """
        best_price = prices[0]
        best_product = -1.0
        for p in prices:
            bu = buyer_ufun(p)
            su = seller_ufun(p)
            if bu >= 0 and su >= 0:
                product = bu * su
                if product > best_product:
                    best_product = product
                    best_price = p

        return NashGuardrailResult(
            nash_price=best_price,
            deviation_pct=0.0,
            passed=True,
            strategy_profile=f"nbs_fallback|price={best_price}",
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _price_grid(price_min: float, price_max: float, grid_size: int) -> list[float]:
        """Create evenly-spaced price grid."""
        if grid_size <= 1:
            return [(price_min + price_max) / 2.0]
        step = (price_max - price_min) / (grid_size - 1)
        return [price_min + i * step for i in range(grid_size)]
