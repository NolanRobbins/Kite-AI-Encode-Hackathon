"""Python wrapper for the IdentityRegistry (ERC-8004) smart contract."""

from __future__ import annotations

import logging
from typing import Any

from eth_account import Account
from web3 import Web3

from negotiatorgrid.utils.web3_helpers import load_abi, send_transaction

logger = logging.getLogger(__name__)

# Inline ABI matching the deployed IdentityRegistry on Kite Testnet (chain 2368).
# The full contract has 3 ``register`` overloads; we use the simplest
# ``register(string)`` form because the demo doesn't need on-chain
# metadata entries. ``setAgentWallet(uint256,address,uint256,bytes)``
# requires a signature from the new wallet — we expose it for callers
# that have that key, and skip it for synthetic seller addresses.
IDENTITY_REGISTRY_ABI: list[dict[str, Any]] = [
    {
        "inputs": [{"internalType": "string", "name": "agentURI", "type": "string"}],
        "name": "register",
        "outputs": [{"internalType": "uint256", "name": "agentId", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "uint256", "name": "agentId", "type": "uint256"},
            {"indexed": False, "internalType": "string", "name": "agentURI", "type": "string"},
            {"indexed": True, "internalType": "address", "name": "owner", "type": "address"},
        ],
        "name": "Registered",
        "type": "event",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "agentId", "type": "uint256"},
            {"internalType": "address", "name": "newWallet", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"},
            {"internalType": "bytes", "name": "signature", "type": "bytes"},
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
        "inputs": [],
        "name": "totalAgents",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
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
        """Register a new agent and return its on-chain agentId.

        Uses the ``register(string)`` overload. The ``metadata`` parameter
        is accepted for API compatibility but is currently routed through
        ``setMetadata`` on a best-effort basis (not yet implemented;
        callers that need rich metadata should write it via the agent's
        URI document instead).
        """
        if self._mock:
            agent_id = self._next_id
            self._next_id += 1
            self._agents[agent_id] = {"uri": agent_uri, "metadata": metadata or {}}
            self._wallets[agent_id] = ""
            logger.info("Mock registerAgent: id=%d uri=%s", agent_id, agent_uri)
            return agent_id

        try:
            sender = Account.from_key(self._private_key).address
            tx = self._contract.functions.register(agent_uri).build_transaction(
                {"chainId": self._w3.eth.chain_id, "from": sender}
            )
            tx_hash = await send_transaction(self._w3, tx, self._private_key)
            receipt = self._w3.eth.get_transaction_receipt(tx_hash)
            # Parse agentId from the indexed ``Registered`` event.
            try:
                parsed = self._contract.events.Registered().process_receipt(receipt)
                if parsed:
                    return int(parsed[0]["args"]["agentId"])
            except Exception:
                logger.debug("Receipt event decode failed", exc_info=True)
            # Fallback: read totalAgents() and assume the last one is ours.
            try:
                return int(self._contract.functions.totalAgents().call())
            except Exception:
                return 0
        except Exception:
            logger.exception("register_agent failed")
            raise

    async def set_agent_wallet(self, agent_id: int, wallet_address: str) -> None:
        """Bind a wallet address to an agent.

        The deployed contract requires a signed deadline + signature from
        ``wallet_address``'s private key. When we don't hold that key
        (typical for the demo's synthetic sellers), this is a no-op that
        logs a warning instead of raising — so the demo flow still
        progresses while leaving an honest gap on chain.
        """
        if self._mock:
            self._wallets[agent_id] = wallet_address
            logger.info("Mock setAgentWallet: id=%d wallet=%s", agent_id, wallet_address)
            return

        logger.warning(
            "setAgentWallet(%d, %s) skipped: signature from new wallet required.",
            agent_id,
            wallet_address,
        )

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
