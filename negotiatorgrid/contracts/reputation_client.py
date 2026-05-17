"""Python wrapper for the ReputationRegistry (ERC-8004) smart contract."""

from __future__ import annotations

import logging
from typing import Any

from eth_account import Account
from web3 import Web3

from negotiatorgrid.utils.web3_helpers import load_abi, send_transaction

logger = logging.getLogger(__name__)

# Inline ABI matching the deployed ReputationRegistry on Kite Testnet (chain 2368).
# ``giveFeedback`` includes a ``valueDecimals`` byte (int128 precision)
# per the ERC-8004 spec.
REPUTATION_REGISTRY_ABI: list[dict[str, Any]] = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "agentId", "type": "uint256"},
            {"internalType": "int128", "name": "value", "type": "int128"},
            {"internalType": "uint8", "name": "valueDecimals", "type": "uint8"},
            {"internalType": "string", "name": "tag1", "type": "string"},
            {"internalType": "string", "name": "tag2", "type": "string"},
            {"internalType": "string", "name": "endpoint", "type": "string"},
            {"internalType": "string", "name": "feedbackURI", "type": "string"},
            {"internalType": "bytes32", "name": "feedbackHash", "type": "bytes32"},
        ],
        "name": "giveFeedback",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "agentId", "type": "uint256"},
            {"internalType": "address[]", "name": "clientAddresses", "type": "address[]"},
            {"internalType": "string", "name": "tag1", "type": "string"},
            {"internalType": "string", "name": "tag2", "type": "string"},
        ],
        "name": "getSummary",
        "outputs": [
            {"internalType": "uint256", "name": "positiveCount", "type": "uint256"},
            {"internalType": "uint256", "name": "negativeCount", "type": "uint256"},
            {"internalType": "uint256", "name": "neutralCount", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "agentId", "type": "uint256"},
            {"internalType": "address", "name": "client", "type": "address"},
            {"internalType": "uint256", "name": "feedbackIndex", "type": "uint256"},
        ],
        "name": "readFeedback",
        "outputs": [
            {"internalType": "int8", "name": "value", "type": "int8"},
            {"internalType": "string", "name": "tag1", "type": "string"},
            {"internalType": "string", "name": "tag2", "type": "string"},
            {"internalType": "string", "name": "feedbackURI", "type": "string"},
            {"internalType": "bytes32", "name": "feedbackHash", "type": "bytes32"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]


class ReputationClient:
    """Client for the ReputationRegistry smart contract.

    Falls back to in-memory storage when *contract_address* is empty.
    """

    def __init__(self, w3: Web3, contract_address: str, private_key: str) -> None:
        self._w3 = w3
        self._private_key = private_key
        self._mock = not contract_address

        if self._mock:
            logger.info("ReputationClient running in mock mode (no contract address)")
            self._feedbacks: dict[int, list[dict[str, Any]]] = {}
            self._contract = None
        else:
            try:
                abi = load_abi("ReputationRegistry")
            except FileNotFoundError:
                logger.warning("ReputationRegistry ABI file not found; using inline ABI")
                abi = REPUTATION_REGISTRY_ABI
            self._contract = w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=abi,
            )

    # ------------------------------------------------------------------
    # Write methods
    # ------------------------------------------------------------------

    async def give_feedback(
        self,
        agent_id: int,
        value: int,
        tag1: str,
        tag2: str,
        endpoint: str,
        feedback_uri: str,
        feedback_hash: bytes,
    ) -> str:
        """Submit feedback for an agent. Returns tx hash."""
        if self._mock:
            entry = {
                "value": value,
                "tag1": tag1,
                "tag2": tag2,
                "endpoint": endpoint,
                "feedback_uri": feedback_uri,
                "feedback_hash": feedback_hash,
            }
            self._feedbacks.setdefault(agent_id, []).append(entry)
            fake_hash = Web3.keccak(
                feedback_hash + agent_id.to_bytes(32, "big")
            ).hex()
            logger.info("Mock giveFeedback: agent=%d value=%d tag1=%s", agent_id, value, tag1)
            return fake_hash

        try:
            sender = Account.from_key(self._private_key).address
            tx = self._contract.functions.giveFeedback(
                agent_id,
                int(value),
                0,  # valueDecimals: pass 0 → ``value`` interpreted as plain integer
                tag1,
                tag2,
                endpoint,
                feedback_uri,
                feedback_hash,
            ).build_transaction({"chainId": self._w3.eth.chain_id, "from": sender})
            return await send_transaction(self._w3, tx, self._private_key)
        except Exception:
            logger.exception("giveFeedback failed")
            raise

    # ------------------------------------------------------------------
    # Read methods
    # ------------------------------------------------------------------

    def get_summary(
        self,
        agent_id: int,
        client_addresses: list[str] | None = None,
        tag1: str = "",
        tag2: str = "",
    ) -> tuple[int, int, int]:
        """Get aggregated feedback counts: (positive, negative, neutral)."""
        if self._mock:
            feedbacks = self._feedbacks.get(agent_id, [])
            # Apply tag filters
            if tag1:
                feedbacks = [f for f in feedbacks if f["tag1"] == tag1]
            if tag2:
                feedbacks = [f for f in feedbacks if f["tag2"] == tag2]
            pos = sum(1 for f in feedbacks if f["value"] > 0)
            neg = sum(1 for f in feedbacks if f["value"] < 0)
            neu = sum(1 for f in feedbacks if f["value"] == 0)
            return (pos, neg, neu)

        try:
            addrs = [
                Web3.to_checksum_address(a) for a in (client_addresses or [])
            ]
            return self._contract.functions.getSummary(
                agent_id, addrs, tag1, tag2
            ).call()
        except Exception:
            logger.exception("getSummary failed")
            return (0, 0, 0)

    def read_feedback(
        self, agent_id: int, client_address: str, feedback_index: int
    ) -> dict[str, Any]:
        """Read a specific feedback entry."""
        if self._mock:
            feedbacks = self._feedbacks.get(agent_id, [])
            if feedback_index < len(feedbacks):
                return feedbacks[feedback_index]
            return {}

        try:
            result = self._contract.functions.readFeedback(
                agent_id,
                Web3.to_checksum_address(client_address),
                feedback_index,
            ).call()
            return {
                "value": result[0],
                "tag1": result[1],
                "tag2": result[2],
                "feedback_uri": result[3],
                "feedback_hash": result[4],
            }
        except Exception:
            logger.exception("readFeedback failed")
            return {}
