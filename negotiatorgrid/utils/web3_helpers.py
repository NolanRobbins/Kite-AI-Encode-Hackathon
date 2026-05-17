"""Web3 helpers for Kite testnet interaction."""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

from eth_account import Account
from web3 import Web3
from web3.contract import Contract
from web3.middleware import ExtraDataToPOAMiddleware

from negotiatorgrid.config import config

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_web3() -> Web3:
    """Get a Web3 instance connected to Kite testnet."""
    w3 = Web3(Web3.HTTPProvider(config.kite.rpc_url))
    # Kite is a PoA chain — inject the middleware
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    if not w3.is_connected():
        logger.warning("Web3 not connected to %s", config.kite.rpc_url)
    return w3


def get_account() -> Account:
    """Get the signing account from the configured private key."""
    if not config.kite.private_key:
        raise ValueError("PRIVATE_KEY not set in environment")
    return Account.from_key(config.kite.private_key)


def load_abi(contract_name: str) -> list[dict[str, Any]]:
    """Load a contract ABI from the contracts/abi directory."""
    abi_dir = Path(__file__).resolve().parent.parent / "contracts" / "abi"
    abi_path = abi_dir / f"{contract_name}.json"
    if not abi_path.exists():
        raise FileNotFoundError(f"ABI not found: {abi_path}")
    with open(abi_path) as f:
        return json.load(f)


def get_contract(contract_name: str, address: str) -> Contract:
    """Get a Web3 contract instance by name and address."""
    w3 = get_web3()
    abi = load_abi(contract_name)
    return w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)


async def send_transaction(
    w3: Web3,
    tx: dict[str, Any],
    private_key: str,
    max_retries: int = 3,
) -> str:
    """Sign and send a transaction with retries and exponential backoff."""
    import asyncio

    account = Account.from_key(private_key)
    tx["from"] = account.address

    for attempt in range(max_retries):
        try:
            tx["nonce"] = w3.eth.get_transaction_count(account.address)
            tx["gas"] = w3.eth.estimate_gas(tx)
            # If ``build_transaction`` already supplied EIP-1559 fields, do
            # not stomp them with a legacy ``gasPrice`` — Kite's RPC rejects
            # transactions that carry both with ``code -32000``.
            if "maxFeePerGas" not in tx and "maxPriorityFeePerGas" not in tx:
                tx["gasPrice"] = w3.eth.gas_price

            signed = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

            if receipt["status"] == 1:
                logger.info("Transaction confirmed: %s", tx_hash.hex())
                return tx_hash.hex()
            else:
                logger.error("Transaction reverted: %s", tx_hash.hex())
                raise RuntimeError(f"Transaction reverted: {tx_hash.hex()}")

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** (attempt + 1)
                logger.warning(
                    "Transaction attempt %d failed: %s. Retrying in %ds...",
                    attempt + 1,
                    e,
                    wait_time,
                )
                await asyncio.sleep(wait_time)
            else:
                raise


def explorer_tx_url(tx_hash: str) -> str:
    """Build a KiteScan URL for a transaction hash."""
    return f"{config.kite.explorer_url}tx/{tx_hash}"


def explorer_address_url(address: str) -> str:
    """Build a KiteScan URL for an address."""
    return f"{config.kite.explorer_url}address/{address}"
