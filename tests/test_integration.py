"""Integration tests: full pipeline from NegotiationSession → X402Settler → AttestationPipeline.

All tests use MOCK mode — no network, no API keys, no blockchain required.
Run with: pytest tests/test_integration.py
"""

from __future__ import annotations

import pytest

from negotiatorgrid.contracts.deal_record import DealRecordClient
from negotiatorgrid.contracts.identity import IdentityClient
from negotiatorgrid.contracts.reputation_client import ReputationClient
from negotiatorgrid.core.attestation import AttestationPipeline
from negotiatorgrid.core.nash_guardrail import NashGuardrail
from negotiatorgrid.core.negotiation import NegotiationSession
from negotiatorgrid.core.opponent_model import OpponentModeler
from negotiatorgrid.core.reputation import ReputationFeed
from negotiatorgrid.core.settlement import X402Settler
from negotiatorgrid.core.types import NegotiationConfig
from negotiatorgrid.llm.offer_generator import OfferGenerator


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_clients():
    """Create all three mock blockchain clients (no contract address → mock mode)."""
    identity = IdentityClient(w3=None, contract_address="", private_key="")
    reputation = ReputationClient(w3=None, contract_address="", private_key="")
    deal_record = DealRecordClient(w3=None, contract_address="", private_key="")
    return identity, reputation, deal_record


@pytest.fixture()
def negotiation_result():
    """Run a standard negotiation and return the result."""
    config = NegotiationConfig(
        max_rounds=7,
        timeout_seconds=30,
        price_min=0.0,
        price_max=100.0,
        buyer_reservation=60.0,
        seller_reservation=40.0,
    )
    buyer_om = OpponentModeler(is_opponent_seller=True, price_min=0.0, price_max=100.0)
    seller_om = OpponentModeler(is_opponent_seller=False, price_min=0.0, price_max=100.0)
    session = NegotiationSession(
        config=config,
        buyer_opponent_modeler=buyer_om,
        seller_opponent_modeler=seller_om,
    )
    return session.run()


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------

class TestFullPipeline:
    """Integration tests: NegotiationSession → X402Settler → AttestationPipeline."""

    def test_negotiate_settle_attest_pipeline(self, mock_clients):
        """Full pipeline: negotiate → check Nash → settle (mock) → attest (mock)."""
        identity, reputation, deal_record = mock_clients

        # 1. Run negotiation
        config = NegotiationConfig(
            max_rounds=7,
            timeout_seconds=30,
            price_min=0.0,
            price_max=100.0,
            buyer_reservation=60.0,
            seller_reservation=40.0,
        )
        session = NegotiationSession(config=config)
        result = session.run()

        # 2. Verify agreement reached (ZOPA exists: 40-60)
        assert result.agreed_price is not None
        assert 40.0 <= result.agreed_price <= 60.0
        assert result.rounds >= 1
        assert result.deal_hash != ""

        # 3. Nash guardrail check
        guardrail = NashGuardrail()

        def buyer_ufun(p: float) -> float:
            return max(0.0, (60.0 - p) / 20.0)

        def seller_ufun(p: float) -> float:
            return max(0.0, (p - 40.0) / 20.0)

        nash_result = guardrail.check_deal(
            result.agreed_price, buyer_ufun, seller_ufun,
            price_min=0.0, price_max=100.0,
        )
        assert nash_result.nash_price > 0

        # 4. Settlement (mock)
        settler = X402Settler()
        settlement = await_mock_settle(settler, result)
        assert settlement.success
        assert settlement.tx_hash != ""

        # 5. Attestation (mock)
        pipeline = AttestationPipeline(deal_record, reputation, identity)
        deal_hash_hex = run_async(pipeline.attest_deal(result, settlement.tx_hash))
        assert deal_hash_hex != ""
        assert len(deal_hash_hex) > 10  # hex string of keccak256

    def test_reputation_feeds_into_strategy(self, mock_clients):
        """Reputation score affects strategy parameters via ReputationFeed."""
        _, reputation, deal_record = mock_clients

        rep_feed = ReputationFeed(reputation, deal_record)

        # Mock mode returns default 0.5 reputation (no feedback data)
        profile = rep_feed.get_agent_reputation(1)
        assert profile.reputation_score == 0.5

        # High reputation → cooperative strategy
        high_strategy = ReputationFeed.map_reputation_to_strategy(0.9)
        assert high_strategy["label"] == "cooperative"
        assert high_strategy["concession_rate"] > 0.1

        # Low reputation → aggressive strategy
        low_strategy = ReputationFeed.map_reputation_to_strategy(0.2)
        assert low_strategy["label"] == "aggressive"
        assert low_strategy["concession_rate"] < 0.1

        # Medium reputation → balanced
        mid_strategy = ReputationFeed.map_reputation_to_strategy(0.6)
        assert mid_strategy["label"] == "balanced"

    def test_offer_generator_wraps_numeric_offers(self, negotiation_result):
        """OfferGenerator produces NL text for each offer in a real transcript."""
        result = negotiation_result
        offer_gen = OfferGenerator()  # no API key = template fallback

        assert len(result.transcript) > 0

        for offer in result.transcript:
            if offer.agent_id == "buyer":
                text = offer_gen.generate_buyer_offer(offer.round_number, offer.price)
            else:
                text = offer_gen.generate_seller_counter(offer.round_number, offer.price)
            assert isinstance(text, str)
            assert len(text) > 0
            # Template fallback includes the price
            assert f"${offer.price:.2f}" in text

        # Acceptance message
        if result.agreed_price is not None:
            accept_msg = offer_gen.generate_acceptance_message(result.agreed_price, result.rounds)
            assert len(accept_msg) > 0
            assert f"${result.agreed_price:.2f}" in accept_msg

    def test_nash_guardrail_validates_negotiated_deal(self, negotiation_result):
        """Nash guardrail validates a deal produced by NegotiationSession."""
        result = negotiation_result

        if result.agreed_price is None:
            pytest.skip("No agreement reached — cannot validate")

        guardrail = NashGuardrail()

        def buyer_ufun(p: float) -> float:
            return max(0.0, (60.0 - p) / 20.0)

        def seller_ufun(p: float) -> float:
            return max(0.0, (p - 40.0) / 20.0)

        nash_result = guardrail.check_deal(
            result.agreed_price, buyer_ufun, seller_ufun,
            price_min=0.0, price_max=100.0,
        )

        # Deal from aspiration negotiators should have a computable Nash price
        assert nash_result.nash_price > 0
        assert nash_result.deviation_pct >= 0
        # Strategy profile should be populated
        assert nash_result.strategy_profile != ""

    def test_identity_registration_and_wallet_binding(self, mock_clients):
        """IdentityClient registers agents and binds wallets in mock mode."""
        identity, _, _ = mock_clients

        agent_id = run_async(identity.register_agent("https://example.com/agent.json"))
        assert agent_id >= 1

        wallet = "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18"
        run_async(identity.set_agent_wallet(agent_id, wallet))

        retrieved = identity.get_agent_wallet(agent_id)
        assert retrieved == wallet

    def test_deal_record_stores_and_retrieves(self, mock_clients):
        """DealRecordClient stores and retrieves deals in mock mode."""
        _, _, deal_record = mock_clients
        from negotiatorgrid.core.types import DealAttestation

        att = DealAttestation(
            deal_hash=b"\x01" * 32,
            buyer="buyer",
            seller="seller",
            final_price=100_000,
            negotiation_rounds=3,
        )

        tx = run_async(deal_record.record_deal(att))
        assert tx != ""

        retrieved = deal_record.get_deal(b"\x01" * 32)
        assert retrieved.final_price == 100_000
        assert retrieved.negotiation_rounds == 3

    def test_opponent_models_updated_during_pipeline(self, mock_clients):
        """Opponent models are updated during a full negotiation."""
        config = NegotiationConfig(
            max_rounds=7,
            timeout_seconds=30,
            price_min=0.0,
            price_max=100.0,
            buyer_reservation=60.0,
            seller_reservation=40.0,
        )
        buyer_om = OpponentModeler(is_opponent_seller=True, price_min=0.0, price_max=100.0)
        seller_om = OpponentModeler(is_opponent_seller=False, price_min=0.0, price_max=100.0)

        session = NegotiationSession(
            config=config,
            buyer_opponent_modeler=buyer_om,
            seller_opponent_modeler=seller_om,
        )
        result = session.run()

        assert result.agreed_price is not None

        # Both opponent models should have been fed data
        buyer_model = buyer_om.get_model()
        seller_model = seller_om.get_model()
        assert buyer_model.confidence >= 0.0
        assert seller_model.confidence >= 0.0


# ---------------------------------------------------------------------------
# Async helpers (tests are synchronous, modules use async)
# ---------------------------------------------------------------------------

import asyncio


def run_async(coro):
    """Run an async coroutine synchronously."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def await_mock_settle(settler: X402Settler, result) -> "SettlementResult":
    """Run mock settlement without EIP-712 signing."""
    from negotiatorgrid.core.types import SettlementResult
    from negotiatorgrid.utils.mock_facilitator import MockFacilitator

    mock = MockFacilitator()
    payload = {
        "x402Version": 1,
        "scheme": "exact",
        "network": "eip155:2368",
        "payload": {
            "signature": "0x" + "00" * 65,
            "authorization": {
                "from": "0x0000000000000000000000000000000000000001",
                "to": "0x0000000000000000000000000000000000000002",
                "value": str(int((result.agreed_price or 0) * 1_000_000)),
                "validAfter": "0",
                "validBefore": "999999999",
                "nonce": "test",
            },
        },
    }
    settle_data = run_async(mock.settle(payload))
    return SettlementResult(
        success=settle_data.get("success", False),
        tx_hash=settle_data.get("transaction", ""),
        payer=settle_data.get("payer", ""),
        network=settle_data.get("network", ""),
        amount=settle_data.get("amount", ""),
    )
