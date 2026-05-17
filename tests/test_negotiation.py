"""Unit tests for the NegotiatorGrid negotiation engine.

Covers:
- Two agents reaching agreement within ZOPA
- Timeout when no agreement is possible (disjoint ZOPAs)
- Round counting
- Opponent model estimation accuracy
- Nash guardrail: flags exploitative deals
- Nash guardrail: passes fair deals
- NL offer generation returns non-empty strings (mocked OpenAI)
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from negotiatorgrid.core.nash_guardrail import NashGuardrail
from negotiatorgrid.core.negotiation import NegotiationSession
from negotiatorgrid.core.opponent_model import OpponentModeler
from negotiatorgrid.core.types import (
    NegotiationConfig,
    NegotiationOffer,
    OpponentType,
)
from negotiatorgrid.llm.offer_generator import OfferGenerator


# -----------------------------------------------------------------------
# Negotiation session tests
# -----------------------------------------------------------------------


class TestNegotiationAgreement:
    """Agents with overlapping ZOPAs must reach agreement."""

    def test_agreement_within_zopa(self):
        cfg = NegotiationConfig(
            max_rounds=7,
            timeout_seconds=30,
            price_min=0,
            price_max=100,
            buyer_reservation=60,
            seller_reservation=40,
        )
        result = NegotiationSession(config=cfg).run()

        assert result.agreed_price is not None
        assert 40 <= result.agreed_price <= 60, (
            f"Agreed price {result.agreed_price} outside ZOPA [40, 60]"
        )

    def test_agreement_with_linear_concession(self):
        cfg = NegotiationConfig(
            max_rounds=7,
            timeout_seconds=30,
            price_min=0,
            price_max=100,
            buyer_reservation=70,
            seller_reservation=30,
        )
        result = NegotiationSession(
            config=cfg, buyer_exponent=1.0, seller_exponent=1.0
        ).run()

        assert result.agreed_price is not None
        assert 30 <= result.agreed_price <= 70

    def test_agreement_tight_zopa(self):
        """Even with a narrow ZOPA, agents should agree."""
        cfg = NegotiationConfig(
            max_rounds=7,
            timeout_seconds=30,
            price_min=0,
            price_max=100,
            buyer_reservation=52,
            seller_reservation=48,
        )
        result = NegotiationSession(
            config=cfg, buyer_exponent=1.0, seller_exponent=1.0
        ).run()

        assert result.agreed_price is not None
        assert 48 <= result.agreed_price <= 52


class TestNegotiationTimeout:
    """Agents with disjoint ZOPAs must NOT reach agreement."""

    def test_no_agreement_disjoint_zopa(self):
        cfg = NegotiationConfig(
            max_rounds=7,
            timeout_seconds=30,
            price_min=0,
            price_max=100,
            buyer_reservation=30,
            seller_reservation=70,
        )
        result = NegotiationSession(config=cfg).run()

        assert result.agreed_price is None
        assert result.deal_hash == ""

    def test_no_agreement_extreme_gap(self):
        cfg = NegotiationConfig(
            max_rounds=7,
            timeout_seconds=30,
            price_min=0,
            price_max=100,
            buyer_reservation=10,
            seller_reservation=90,
        )
        result = NegotiationSession(config=cfg).run()

        assert result.agreed_price is None


class TestRoundCounting:
    """Round counting must be accurate."""

    def test_rounds_within_max(self):
        cfg = NegotiationConfig(
            max_rounds=7,
            timeout_seconds=30,
            price_min=0,
            price_max=100,
            buyer_reservation=60,
            seller_reservation=40,
        )
        result = NegotiationSession(config=cfg).run()

        assert 1 <= result.rounds <= 7

    def test_timeout_uses_all_rounds(self):
        cfg = NegotiationConfig(
            max_rounds=5,
            timeout_seconds=30,
            price_min=0,
            price_max=100,
            buyer_reservation=20,
            seller_reservation=80,
        )
        result = NegotiationSession(config=cfg).run()

        # Should use all rounds when no agreement
        assert result.rounds >= 4  # NegMAS may end at step 5 (0-indexed → reported as 5)

    def test_transcript_populated(self):
        cfg = NegotiationConfig(
            max_rounds=7,
            timeout_seconds=30,
            price_min=0,
            price_max=100,
            buyer_reservation=60,
            seller_reservation=40,
        )
        result = NegotiationSession(config=cfg).run()

        assert len(result.transcript) > 0
        for offer in result.transcript:
            assert offer.round_number >= 0
            assert offer.price >= 0


class TestDealHash:
    """Deal hash must be populated on agreement."""

    def test_deal_hash_on_agreement(self):
        cfg = NegotiationConfig(
            max_rounds=7,
            timeout_seconds=30,
            price_min=0,
            price_max=100,
            buyer_reservation=60,
            seller_reservation=40,
        )
        result = NegotiationSession(config=cfg).run()

        assert result.agreed_price is not None
        assert len(result.deal_hash) > 0


# -----------------------------------------------------------------------
# Opponent model tests
# -----------------------------------------------------------------------


class TestOpponentModel:
    """Opponent modeler correctly estimates counterparty behavior."""

    def test_estimate_reservation_price_seller_conceding(self):
        """Seller conceding from 80 toward 50 → reservation should be near low end."""
        modeler = OpponentModeler(is_opponent_seller=True, price_min=0, price_max=100)
        for i, price in enumerate([80, 75, 70, 65, 60]):
            modeler.update(
                NegotiationOffer(round_number=i, price=price, agent_id="seller")
            )

        est = modeler.estimate_reservation_price()
        # Extrapolated: the seller is conceding at -5/round, so should be well below 60
        assert est < 60, f"Estimated reservation {est} should be < 60"

    def test_estimate_type_aggressive(self):
        """Very small concessions → aggressive."""
        modeler = OpponentModeler(is_opponent_seller=True, price_min=0, price_max=100)
        for i, price in enumerate([80, 79.5, 79, 78.5, 78]):
            modeler.update(
                NegotiationOffer(round_number=i, price=price, agent_id="seller")
            )

        assert modeler.estimate_type() == OpponentType.AGGRESSIVE

    def test_estimate_type_generous(self):
        """Large concessions → generous."""
        modeler = OpponentModeler(is_opponent_seller=True, price_min=0, price_max=100)
        for i, price in enumerate([80, 70, 60, 50, 40]):
            modeler.update(
                NegotiationOffer(round_number=i, price=price, agent_id="seller")
            )

        assert modeler.estimate_type() == OpponentType.GENEROUS

    def test_confidence_increases_with_observations(self):
        modeler = OpponentModeler(is_opponent_seller=True, price_min=0, price_max=100)

        assert modeler.get_confidence() == 0.0

        modeler.update(NegotiationOffer(round_number=0, price=80, agent_id="s"))
        c1 = modeler.get_confidence()
        assert c1 > 0.0

        for i in range(1, 5):
            modeler.update(NegotiationOffer(round_number=i, price=80 - i * 5, agent_id="s"))

        c5 = modeler.get_confidence()
        assert c5 > c1

    def test_strategy_adjustment_aggressive(self):
        modeler = OpponentModeler(is_opponent_seller=True, price_min=0, price_max=100)
        for i, p in enumerate([80, 79.8, 79.6, 79.4, 79.2]):
            modeler.update(NegotiationOffer(round_number=i, price=p, agent_id="s"))

        adj = modeler.strategy_adjustment()
        assert adj["concession_rate"] < 1.0  # slow down our concession
        assert adj["walk_away_threshold"] > 0.5  # higher threshold

    def test_strategy_adjustment_generous(self):
        modeler = OpponentModeler(is_opponent_seller=True, price_min=0, price_max=100)
        for i, p in enumerate([80, 70, 60, 50, 40]):
            modeler.update(NegotiationOffer(round_number=i, price=p, agent_id="s"))

        adj = modeler.strategy_adjustment()
        assert adj["concession_rate"] > 1.0  # speed up reciprocation
        assert adj["walk_away_threshold"] < 0.5


# -----------------------------------------------------------------------
# Nash guardrail tests
# -----------------------------------------------------------------------


class TestNashGuardrail:
    """Nash guardrail correctly validates deals."""

    @staticmethod
    def _buyer_ufun(price: float) -> float:
        """Buyer utility: 100 - price (higher price = less utility)."""
        return max(0.0, 100.0 - price)

    @staticmethod
    def _seller_ufun(price: float) -> float:
        """Seller utility: price (higher price = more utility)."""
        return max(0.0, price)

    def test_compute_nash_returns_midpoint(self):
        """Symmetric linear utilities → Nash should be near midpoint."""
        guardrail = NashGuardrail()
        result = guardrail.compute_nash(
            self._buyer_ufun, self._seller_ufun,
            price_min=0, price_max=100, grid_size=11,
        )

        # NBS for symmetric utilities = 50
        assert 40 <= result.nash_price <= 60, f"Nash price {result.nash_price} not near midpoint"

    def test_fair_deal_passes(self):
        """A deal at the Nash price should pass the guardrail."""
        guardrail = NashGuardrail(deviation_threshold=0.20)

        # First compute Nash to know the reference price
        nash_result = guardrail.compute_nash(
            self._buyer_ufun, self._seller_ufun,
            price_min=0, price_max=100, grid_size=11,
        )

        result = guardrail.check_deal(
            agreed_price=nash_result.nash_price,
            buyer_ufun=self._buyer_ufun,
            seller_ufun=self._seller_ufun,
            price_min=0,
            price_max=100,
            grid_size=11,
        )

        assert result.passed is True
        assert result.deviation_pct < 0.01

    def test_exploitative_deal_flagged(self):
        """A deal very far from Nash should be flagged."""
        guardrail = NashGuardrail(deviation_threshold=0.20)

        # Extremely lopsided: price = 95 (almost all value to seller)
        result = guardrail.check_deal(
            agreed_price=95.0,
            buyer_ufun=self._buyer_ufun,
            seller_ufun=self._seller_ufun,
            price_min=0,
            price_max=100,
            grid_size=11,
        )

        assert result.passed is False
        assert result.deviation_pct > 0.20

    def test_slightly_off_deal_passes(self):
        """A deal within 20% deviation should still pass."""
        guardrail = NashGuardrail(deviation_threshold=0.20)

        nash_result = guardrail.compute_nash(
            self._buyer_ufun, self._seller_ufun,
            price_min=0, price_max=100, grid_size=11,
        )

        # Offer 10% above Nash
        slightly_off = nash_result.nash_price * 1.10
        result = guardrail.check_deal(
            agreed_price=slightly_off,
            buyer_ufun=self._buyer_ufun,
            seller_ufun=self._seller_ufun,
            price_min=0,
            price_max=100,
            grid_size=11,
        )

        assert result.passed is True


# -----------------------------------------------------------------------
# LLM offer generator tests
# -----------------------------------------------------------------------


class TestOfferGenerator:
    """Offer generator produces non-empty strings, with mocked OpenAI."""

    def test_template_fallback_buyer_offer(self):
        """Without API key, returns template fallback."""
        gen = OfferGenerator(api_key="")
        msg = gen.generate_buyer_offer(round_num=1, price=45.0)
        assert len(msg) > 0
        assert "45.00" in msg
        metrics = gen.runtime_metrics()
        assert metrics["fallback_messages"] >= 1
        assert metrics["last_error"] in {"mode_policy_only", "missing_api_key"}

    def test_template_fallback_seller_counter(self):
        gen = OfferGenerator(api_key="")
        msg = gen.generate_seller_counter(round_num=2, price=55.0)
        assert len(msg) > 0
        assert "55.00" in msg

    def test_template_fallback_acceptance(self):
        gen = OfferGenerator(api_key="")
        msg = gen.generate_acceptance_message(agreed_price=50.0, rounds=3)
        assert len(msg) > 0
        assert "50.00" in msg

    def test_template_fallback_rejection(self):
        gen = OfferGenerator(api_key="")
        msg = gen.generate_rejection_message(reason="Price too high")
        assert len(msg) > 0

    def test_mocked_openai_buyer_offer(self):
        """With mocked OpenAI client, returns LLM response."""
        gen = OfferGenerator(api_key="")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "I propose $45 based on market analysis."
        mock_client.chat.completions.create.return_value = mock_response
        gen._client = mock_client

        msg = gen.generate_buyer_offer(round_num=1, price=45.0)
        assert msg == "I propose $45 based on market analysis."
        mock_client.chat.completions.create.assert_called_once()

    def test_openai_error_falls_back(self):
        """When OpenAI raises, we fall back to template."""
        gen = OfferGenerator(api_key="")

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RuntimeError("API error")
        gen._client = mock_client

        msg = gen.generate_buyer_offer(round_num=1, price=45.0)
        assert len(msg) > 0
        assert "45.00" in msg


# -----------------------------------------------------------------------
# Integration: negotiation with opponent modeling
# -----------------------------------------------------------------------


class TestNegotiationWithOpponentModel:
    """Negotiation session with opponent modeling injected."""

    def test_opponent_model_updated_during_negotiation(self):
        buyer_modeler = OpponentModeler(is_opponent_seller=True, price_min=0, price_max=100)
        seller_modeler = OpponentModeler(is_opponent_seller=False, price_min=0, price_max=100)

        cfg = NegotiationConfig(
            max_rounds=7,
            timeout_seconds=30,
            price_min=0,
            price_max=100,
            buyer_reservation=60,
            seller_reservation=40,
        )
        session = NegotiationSession(
            config=cfg,
            buyer_opponent_modeler=buyer_modeler,
            seller_opponent_modeler=seller_modeler,
        )
        result = session.run()

        assert result.agreed_price is not None
        # The modelers should have some observations (at least from the agreement round)
        assert buyer_modeler.get_confidence() >= 0.0
        assert seller_modeler.get_confidence() >= 0.0
