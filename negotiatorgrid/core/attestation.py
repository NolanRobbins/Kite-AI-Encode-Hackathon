"""Deal attestation pipeline — binds negotiation outcomes to on-chain records."""

from __future__ import annotations

import logging
import time

from web3 import Web3

from negotiatorgrid.contracts.deal_record import DealRecordClient
from negotiatorgrid.contracts.identity import IdentityClient
from negotiatorgrid.contracts.reputation_client import ReputationClient
from negotiatorgrid.core.types import (
    DealAttestation,
    NegotiationResult,
    SLATerms,
)

logger = logging.getLogger(__name__)

# The Pydantic NegotiationResult uses different field names than the
# on-chain DealAttestation.  These helpers bridge the two.


class AttestationPipeline:
    """Orchestrates the full post-negotiation attestation flow:

    1. Compute deal hash
    2. Record deal on-chain (DealRecord)
    3. Settle deal with x402 tx proof
    4. Submit reputation feedback for both agents
    """

    def __init__(
        self,
        deal_record: DealRecordClient,
        reputation: ReputationClient,
        identity: IdentityClient,
    ) -> None:
        self._deal_record = deal_record
        self._reputation = reputation
        self._identity = identity

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def attest_deal(
        self,
        negotiation_result: NegotiationResult,
        x402_tx_hash: str,
    ) -> str:
        """Run the full attestation pipeline. Returns the deal hash hex string.

        Accepts the Pydantic *NegotiationResult* (``agreed_price``,
        ``buyer_id``/``seller_id``) and bridges to the on-chain
        *DealAttestation* dataclass.

        Failures in reputation feedback are logged but do not block the
        caller — the payment has already settled.
        """
        # 1. Compute deterministic deal hash
        deal_hash = _compute_deal_hash(negotiation_result)
        ts = int(time.time())

        # Convert agreed_price (float, e.g. 0.15 USDT) to atomic units (6 decimals)
        final_price_atomic = int((negotiation_result.agreed_price or 0) * 1_000_000)

        # Extract opening prices from transcript if available
        opening_buyer = 0
        opening_seller = 0
        if negotiation_result.transcript:
            for offer in negotiation_result.transcript:
                if offer.agent_id == negotiation_result.buyer_id and opening_buyer == 0:
                    opening_buyer = int(offer.price * 1_000_000)
                elif offer.agent_id == negotiation_result.seller_id and opening_seller == 0:
                    opening_seller = int(offer.price * 1_000_000)

        attestation = DealAttestation(
            deal_hash=deal_hash,
            buyer=negotiation_result.buyer_id,
            seller=negotiation_result.seller_id,
            buyer_agent_id=0,
            seller_agent_id=0,
            resource_uri="",
            opening_buyer_price=opening_buyer,
            opening_seller_price=opening_seller,
            final_price=final_price_atomic,
            negotiation_rounds=negotiation_result.rounds,
            sla=SLATerms(),
            x402_tx_hash=bytes.fromhex(x402_tx_hash.removeprefix("0x")) if x402_tx_hash else b"\x00" * 32,
            timestamp=ts,
            settled=False,
        )

        # 2. Record deal on-chain
        try:
            record_tx = await self._deal_record.record_deal(attestation)
            logger.info("Deal recorded: deal_hash=%s tx=%s", deal_hash.hex(), record_tx)
        except Exception:
            logger.exception("recordDeal failed for %s", deal_hash.hex())
            raise

        # 3. Settle deal with x402 tx proof
        x402_bytes = attestation.x402_tx_hash
        try:
            settle_tx = await self._deal_record.settle_deal(deal_hash, x402_bytes)
            logger.info("Deal settled: deal_hash=%s tx=%s", deal_hash.hex(), settle_tx)
        except Exception:
            logger.exception("settleDeal failed for %s", deal_hash.hex())
            # Don't raise — the deal is recorded even if settlement marking fails

        # 4. Reputation feedback for both agents (best-effort)
        # Agent IDs default to 0 when we only have wallet addresses.
        await self._submit_reputation(
            agent_id=0,
            value=1,  # positive: deal completed
            tag1="deal_completion",
            tag2="success",
            deal_hash=deal_hash,
        )
        await self._submit_reputation(
            agent_id=0,
            value=1,
            tag1="deal_completion",
            tag2="success",
            deal_hash=deal_hash,
        )

        return deal_hash.hex()

    def get_deal_history(self, agent_address: str) -> list[DealAttestation]:
        """Retrieve all deal attestations for an agent."""
        deal_hashes = self._deal_record.get_deals_by_agent(agent_address)
        deals: list[DealAttestation] = []
        for dh in deal_hashes:
            deal = self._deal_record.get_deal(dh)
            if deal.deal_hash:
                deals.append(deal)
        return deals

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _submit_reputation(
        self,
        agent_id: int,
        value: int,
        tag1: str,
        tag2: str,
        deal_hash: bytes,
    ) -> None:
        """Best-effort reputation feedback — never raises."""
        try:
            await self._reputation.give_feedback(
                agent_id=agent_id,
                value=value,
                tag1=tag1,
                tag2=tag2,
                endpoint="",
                feedback_uri="",
                feedback_hash=deal_hash,
            )
        except Exception:
            logger.exception(
                "Reputation feedback failed for agent %d (non-blocking)", agent_id
            )


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _compute_deal_hash(result: NegotiationResult) -> bytes:
    """Compute keccak256(buyer, seller, price, timestamp, nonce).

    Uses abi.encodePacked-style concatenation matching the Solidity contract.
    Handles both address-style IDs (0x…) and opaque string IDs.
    """
    ts = int(time.time())
    final_price_atomic = int((result.agreed_price or 0) * 1_000_000)

    # Use a combination of fields as the nonce to ensure uniqueness
    nonce = Web3.keccak(
        text=f"{result.buyer_id}{result.seller_id}{final_price_atomic}{ts}"
    )

    # Buyer/seller IDs might be wallet addresses (0x…) or opaque strings.
    def _to_bytes(val: str) -> bytes:
        if val.startswith("0x") and len(val) >= 42:
            return bytes.fromhex(val.removeprefix("0x").lower().zfill(40))
        return val.encode()

    packed = b"".join([
        _to_bytes(result.buyer_id),
        _to_bytes(result.seller_id),
        final_price_atomic.to_bytes(32, "big"),
        ts.to_bytes(8, "big"),
        nonce,
    ])

    return Web3.keccak(packed)
