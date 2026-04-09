"""Python wrapper for the IdentityRegistry (ERC-8004) smart contract."""

from __future__ import annotations

import logging
from typing import Any

from web3 import Web3

from negotiatorgrid.utils.web3_helpers import load_abi, send_transaction

logger = logging.getLogger(__name__)

# Inline ABI for when the JSON file is not yet available.
IDENTITY_REGISTRY_ABI: list[dict[str, Any]] = [
    {
        "inputs": [
            {"internalType": "string", "name": "agentURI", "type": "string"},
            {"internalType": "bytes", "name": "metadata", "type": "bytes"},
        ],
        "name": "register",
        "outputs": [{"internalType": "uint256", "name": "agentId", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "agentId", "type": "uint256"},
            {"internalType": "address", "name": "wallet", "type": "address"},
        ],
        "name": "setAgentWallet",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "agentId", "type": "uint256"}],
        "name": "getAgentWallet",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "agentId", "type": "uint256"},
            {"internalType": "string", "name": "key", "type": "string"},
        ],
        "name": "getMetadata",
        "outputs": [{"internalType": "bytes", "name": "", "type": "bytes"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "agentId", "type": "uint256"},
            {"internalType": "string", "name": "key", "type": "string"},
            {"internalType": "bytes", "name": "value", "type": "bytes"},
        ],
        "name": "setMetadata",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]


class IdentityClient:
    """Client for the ERC-8004 IdentityRegistry contract.

    Falls back to in-memory storage when *contract_address* is empty.
    """

    def __init__(self, w3: Web3, contract_address: str, private_key: str) -> None:
        self._w3 = w3
        self._private_key = private_key
        self._mock = not contract_address

        if self._mock:
            logger.info("IdentityClient running in mock mode (no contract address)")
            self._next_id = 1
            self._agents: dict[int, dict[str, Any]] = {}
            self._wallets: dict[int, str] = {}
            self._metadata: dict[int, dict[str, bytes]] = {}
            self._contract = None
        else:
            try:
                abi = load_abi("IdentityRegistry")
            except FileNotFoundError:
                logger.warning("IdentityRegistry ABI file not found; using inline ABI")
                abi = IDENTITY_REGISTRY_ABI
            self._contract = w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=abi,
            )

    # ------------------------------------------------------------------
    # Write methods
    # ------------------------------------------------------------------

    async def register_agent(
        self, agent_uri: str, metadata: dict[str, Any] | None = None
    ) -> int:
        """Register a new agent and return its on-chain agentId."""
        import json as _json

        metadata_bytes = _json.dumps(metadata or {}).encode()

        if self._mock:
            agent_id = self._next_id
            self._next_id += 1
            self._agents[agent_id] = {"uri": agent_uri, "metadata": metadata or {}}
            logger.info("Mock registerAgent: id=%d uri=%s", agent_id, agent_uri)
            return agent_id

        try:
            tx = self._contract.functions.register(
                agent_uri, metadata_bytes
            ).build_transaction({"chainId": self._w3.eth.chain_id})
            tx_hash = await send_transaction(self._w3, tx, self._private_key)
            # Parse the agentId from the transaction receipt logs
            receipt = self._w3.eth.get_transaction_receipt(tx_hash)
            # Attempt to decode the return value; fall back to receipt log parsing
            try:
                logs = self._contract.events.get("AgentRegistered", lambda: None)
                if logs:
                    parsed = logs().process_receipt(receipt)
                    if parsed:
                        return parsed[0]["args"]["agentId"]
            except Exception:
                pass
            logger.warning("Could not parse agentId from receipt; returning 0")
            return 0
        except Exception:
            logger.exception("register_agent failed")
            raise

    async def set_agent_wallet(self, agent_id: int, wallet_address: str) -> None:
        """Bind a wallet address to an agent."""
        if self._mock:
            self._wallets[agent_id] = wallet_address
            logger.info("Mock setAgentWallet: id=%d wallet=%s", agent_id, wallet_address)
            return

        try:
            tx = self._contract.functions.setAgentWallet(
                agent_id, Web3.to_checksum_address(wallet_address)
            ).build_transaction({"chainId": self._w3.eth.chain_id})
            await send_transaction(self._w3, tx, self._private_key)
        except Exception:
            logger.exception("set_agent_wallet failed")
            raise

    # ------------------------------------------------------------------
    # Read methods
    # ------------------------------------------------------------------

    def get_agent_wallet(self, agent_id: int) -> str:
        """Retrieve the wallet address for an agent."""
        if self._mock:
            return self._wallets.get(agent_id, "")

        try:
            return self._contract.functions.getAgentWallet(agent_id).call()
        except Exception:
            logger.exception("get_agent_wallet failed")
            return ""

    def get_metadata(self, agent_id: int, key: str) -> bytes:
        """Read a metadata value for an agent."""
        if self._mock:
            return self._metadata.get(agent_id, {}).get(key, b"")

        try:
            return self._contract.functions.getMetadata(agent_id, key).call()
        except Exception:
            logger.exception("get_metadata failed")
            return b""
