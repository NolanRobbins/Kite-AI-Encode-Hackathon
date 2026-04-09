"""Python wrapper for the DealRecord smart contract."""

from __future__ import annotations

import logging
from typing import Any

from web3 import Web3

from negotiatorgrid.core.types import DealAttestation, SLATerms
from negotiatorgrid.utils.web3_helpers import load_abi, send_transaction

logger = logging.getLogger(__name__)

# Inline ABI used when the JSON file is not yet deployed.
DEAL_RECORD_ABI: list[dict[str, Any]] = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "bytes32", "name": "dealHash", "type": "bytes32"},
                    {"internalType": "address", "name": "buyer", "type": "address"},
                    {"internalType": "address", "name": "seller", "type": "address"},
                    {"internalType": "uint256", "name": "buyerAgentId", "type": "uint256"},
                    {"internalType": "uint256", "name": "sellerAgentId", "type": "uint256"},
                    {"internalType": "string", "name": "resourceUri", "type": "string"},
                    {"internalType": "uint256", "name": "openingBuyerPrice", "type": "uint256"},
                    {"internalType": "uint256", "name": "openingSellerPrice", "type": "uint256"},
                    {"internalType": "uint256", "name": "finalPrice", "type": "uint256"},
                    {"internalType": "uint8", "name": "negotiationRounds", "type": "uint8"},
                    {
                        "components": [
                            {"internalType": "uint32", "name": "responseTimeMs", "type": "uint32"},
                            {"internalType": "uint16", "name": "availabilityBps", "type": "uint16"},
                            {"internalType": "uint32", "name": "validityPeriodSecs", "type": "uint32"},
                        ],
                        "internalType": "struct SLATerms",
                        "name": "sla",
                        "type": "tuple",
                    },
                    {"internalType": "bytes32", "name": "x402TxHash", "type": "bytes32"},
                    {"internalType": "uint64", "name": "timestamp", "type": "uint64"},
                    {"internalType": "bool", "name": "settled", "type": "bool"},
                ],
                "internalType": "struct DealAttestation",
                "name": "attestation",
                "type": "tuple",
            }
        ],
        "name": "recordDeal",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "dealHash", "type": "bytes32"},
            {"internalType": "bytes32", "name": "x402TxHash", "type": "bytes32"},
        ],
        "name": "settleDeal",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "dealHash", "type": "bytes32"},
            {"internalType": "uint8", "name": "buyerScore", "type": "uint8"},
            {"internalType": "uint8", "name": "sellerScore", "type": "uint8"},
            {"internalType": "string", "name": "tag", "type": "string"},
        ],
        "name": "updateReputation",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "dealHash", "type": "bytes32"}],
        "name": "getDeal",
        "outputs": [
            {
                "components": [
                    {"internalType": "bytes32", "name": "dealHash", "type": "bytes32"},
                    {"internalType": "address", "name": "buyer", "type": "address"},
                    {"internalType": "address", "name": "seller", "type": "address"},
                    {"internalType": "uint256", "name": "buyerAgentId", "type": "uint256"},
                    {"internalType": "uint256", "name": "sellerAgentId", "type": "uint256"},
                    {"internalType": "string", "name": "resourceUri", "type": "string"},
                    {"internalType": "uint256", "name": "openingBuyerPrice", "type": "uint256"},
                    {"internalType": "uint256", "name": "openingSellerPrice", "type": "uint256"},
                    {"internalType": "uint256", "name": "finalPrice", "type": "uint256"},
                    {"internalType": "uint8", "name": "negotiationRounds", "type": "uint8"},
                    {
                        "components": [
                            {"internalType": "uint32", "name": "responseTimeMs", "type": "uint32"},
                            {"internalType": "uint16", "name": "availabilityBps", "type": "uint16"},
                            {"internalType": "uint32", "name": "validityPeriodSecs", "type": "uint32"},
                        ],
                        "internalType": "struct SLATerms",
                        "name": "sla",
                        "type": "tuple",
                    },
                    {"internalType": "bytes32", "name": "x402TxHash", "type": "bytes32"},
                    {"internalType": "uint64", "name": "timestamp", "type": "uint64"},
                    {"internalType": "bool", "name": "settled", "type": "bool"},
                ],
                "internalType": "struct DealAttestation",
                "name": "",
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "agent", "type": "address"}],
        "name": "getDealsByAgent",
        "outputs": [{"internalType": "bytes32[]", "name": "", "type": "bytes32[]"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "agent", "type": "address"}],
        "name": "getDealCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "agent", "type": "address"}],
        "name": "getTotalVolume",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]


def _attestation_to_tuple(att: DealAttestation) -> tuple:
    """Convert a DealAttestation dataclass to the Solidity struct tuple."""
    return (
        att.deal_hash,
        Web3.to_checksum_address(att.buyer),
        Web3.to_checksum_address(att.seller),
        att.buyer_agent_id,
        att.seller_agent_id,
        att.resource_uri,
        att.opening_buyer_price,
        att.opening_seller_price,
        att.final_price,
        att.negotiation_rounds,
        (att.sla.response_time_ms, att.sla.availability_bps, att.sla.validity_period_secs),
        att.x402_tx_hash,
        att.timestamp,
        att.settled,
    )


def _tuple_to_attestation(data: tuple) -> DealAttestation:
    """Convert a Solidity struct tuple back to a DealAttestation."""
    sla_tuple = data[10]
    return DealAttestation(
        deal_hash=data[0],
        buyer=data[1],
        seller=data[2],
        buyer_agent_id=data[3],
        seller_agent_id=data[4],
        resource_uri=data[5],
        opening_buyer_price=data[6],
        opening_seller_price=data[7],
        final_price=data[8],
        negotiation_rounds=data[9],
        sla=SLATerms(
            response_time_ms=sla_tuple[0],
            availability_bps=sla_tuple[1],
            validity_period_secs=sla_tuple[2],
        ),
        x402_tx_hash=data[11],
        timestamp=data[12],
        settled=data[13],
    )


class DealRecordClient:
    """Client for the DealRecord smart contract.

    Falls back to in-memory storage when *contract_address* is empty.
    """

    def __init__(self, w3: Web3, contract_address: str, private_key: str) -> None:
        self._w3 = w3
        self._private_key = private_key
        self._mock = not contract_address

        if self._mock:
            logger.info("DealRecordClient running in mock mode (no contract address)")
            self._store: dict[bytes, DealAttestation] = {}
            self._agent_deals: dict[str, list[bytes]] = {}
            self._contract = None
        else:
            try:
                abi = load_abi("DealRecord")
            except FileNotFoundError:
                logger.warning("DealRecord ABI file not found; using inline ABI")
                abi = DEAL_RECORD_ABI
            self._contract = w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=abi,
            )

    # ------------------------------------------------------------------
    # Write methods
    # ------------------------------------------------------------------

    async def record_deal(self, attestation: DealAttestation) -> str:
        """Record a deal attestation on-chain. Returns tx hash."""
        if self._mock:
            self._store[attestation.deal_hash] = attestation
            for addr in (attestation.buyer, attestation.seller):
                self._agent_deals.setdefault(addr.lower(), []).append(attestation.deal_hash)
            fake_hash = Web3.keccak(attestation.deal_hash).hex()
            logger.info("Mock recordDeal: %s", fake_hash)
            return fake_hash

        try:
            tx = self._contract.functions.recordDeal(
                _attestation_to_tuple(attestation)
            ).build_transaction({"chainId": self._w3.eth.chain_id})
            return await send_transaction(self._w3, tx, self._private_key)
        except Exception:
            logger.exception("recordDeal failed")
            raise

    async def settle_deal(self, deal_hash: bytes, x402_tx_hash: bytes) -> str:
        """Mark a deal as settled with the x402 payment tx hash."""
        if self._mock:
            if deal_hash in self._store:
                self._store[deal_hash].x402_tx_hash = x402_tx_hash
                self._store[deal_hash].settled = True
            fake_hash = Web3.keccak(deal_hash + x402_tx_hash).hex()
            logger.info("Mock settleDeal: %s", fake_hash)
            return fake_hash

        try:
            tx = self._contract.functions.settleDeal(
                deal_hash, x402_tx_hash
            ).build_transaction({"chainId": self._w3.eth.chain_id})
            return await send_transaction(self._w3, tx, self._private_key)
        except Exception:
            logger.exception("settleDeal failed")
            raise

    async def update_reputation(
        self,
        deal_hash: bytes,
        buyer_score: int,
        seller_score: int,
        tag: str,
    ) -> str:
        """Submit reputation scores for a completed deal."""
        if self._mock:
            logger.info(
                "Mock updateReputation: deal=%s buyer=%d seller=%d tag=%s",
                deal_hash.hex(),
                buyer_score,
                seller_score,
                tag,
            )
            return Web3.keccak(deal_hash).hex()

        try:
            tx = self._contract.functions.updateReputation(
                deal_hash, buyer_score, seller_score, tag
            ).build_transaction({"chainId": self._w3.eth.chain_id})
            return await send_transaction(self._w3, tx, self._private_key)
        except Exception:
            logger.exception("updateReputation failed")
            raise

    # ------------------------------------------------------------------
    # Read methods
    # ------------------------------------------------------------------

    def get_deal(self, deal_hash: bytes) -> DealAttestation:
        """Retrieve a deal attestation by hash."""
        if self._mock:
            return self._store.get(deal_hash, DealAttestation())

        try:
            result = self._contract.functions.getDeal(deal_hash).call()
            return _tuple_to_attestation(result)
        except Exception:
            logger.exception("getDeal failed")
            return DealAttestation()

    def get_deals_by_agent(self, agent_address: str) -> list[bytes]:
        """List all deal hashes for a given agent address."""
        if self._mock:
            return self._agent_deals.get(agent_address.lower(), [])

        try:
            return self._contract.functions.getDealsByAgent(
                Web3.to_checksum_address(agent_address)
            ).call()
        except Exception:
            logger.exception("getDealsByAgent failed")
            return []

    def get_deal_count(self, agent_address: str) -> int:
        """Return the number of deals an agent has participated in."""
        if self._mock:
            return len(self._agent_deals.get(agent_address.lower(), []))

        try:
            return self._contract.functions.getDealCount(
                Web3.to_checksum_address(agent_address)
            ).call()
        except Exception:
            logger.exception("getDealCount failed")
            return 0

    def get_total_volume(self, agent_address: str) -> int:
        """Return the total trade volume for an agent (in atomic units)."""
        if self._mock:
            return sum(
                self._store[h].final_price
                for h in self._agent_deals.get(agent_address.lower(), [])
                if h in self._store
            )

        try:
            return self._contract.functions.getTotalVolume(
                Web3.to_checksum_address(agent_address)
            ).call()
        except Exception:
            logger.exception("getTotalVolume failed")
            return 0
