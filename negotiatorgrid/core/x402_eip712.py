"""Shared x402 / EIP-712 constants and typed-data builder.

``X402Settler`` (``settlement.py``), ``surprise_api.x402_middleware``, and
``x402_buyer`` must agree on scheme/network defaults and on the exact
``TransferWithAuthorization`` message shape so signatures round-trip through
local verification.
"""

from __future__ import annotations

from typing import Any

from web3 import Web3

from negotiatorgrid.config import config

# JSON envelope (X-Payment payload and 402 body)
X402_JSON_VERSION: int = 1

# EIP-712 domain for USDT-style EIP-3009 TransferWithAuthorization on Kite demo
EIP712_DOMAIN_TOKEN_NAME: str = "USDT"
EIP712_DOMAIN_TOKEN_VERSION: str = "2"

# Default timeout echoed in PaymentRequirements (seconds)
DEFAULT_MAX_TIMEOUT_SECONDS: int = 300

# Typed-data primary type (must match USDT contract expectations)
TRANSFER_WITH_AUTHORIZATION_TYPES: dict[str, list[dict[str, str]]] = {
    "TransferWithAuthorization": [
        {"name": "from", "type": "address"},
        {"name": "to", "type": "address"},
        {"name": "value", "type": "uint256"},
        {"name": "validAfter", "type": "uint256"},
        {"name": "validBefore", "type": "uint256"},
        {"name": "nonce", "type": "bytes32"},
    ],
}


def default_x402_scheme() -> str:
    """x402 ``scheme`` field (e.g. ``exact``)."""
    return config.x402.scheme


def default_eip155_network() -> str:
    """Default CAIP-2 style network id (e.g. ``eip155:2368``)."""
    return config.x402.network


def default_test_usdt_address() -> str:
    """USDT (or test USDT) contract used as EIP-712 verifying contract."""
    return config.kite.test_usdt_addr


def chain_id_from_eip155(network: str) -> int:
    """Parse ``eip155:<id>`` → integer chain id."""
    return int(network.split(":")[-1])


def _nonce_to_bytes32(nonce: str | bytes) -> bytes:
    """Normalise wire-format nonce to 32 bytes for EIP-712 ``bytes32``."""
    if isinstance(nonce, bytes):
        if len(nonce) != 32:
            raise ValueError("nonce as bytes must be length 32")
        return nonce
    raw = (nonce or "").strip().removeprefix("0x").removeprefix("0X")
    if len(raw) != 64 or any(c not in "0123456789abcdefABCDEF" for c in raw):
        raise ValueError("nonce must be 32-byte hex (64 hex chars), with or without 0x")
    return bytes.fromhex(raw)


def build_transfer_with_authorization_typed_data(
    authorization: dict[str, Any],
    asset_address: str,
    chain_id: int,
) -> dict[str, Any]:
    """Build EIP-712 typed data for ``TransferWithAuthorization`` (EIP-3009).

    The ``nonce`` field in *authorization* may be a hex string (with or
    without ``0x``) or 32 raw bytes; the in-memory ``message`` always uses
    ``bytes`` so ``eth_account`` signing and recovery agree with
    ``encode_typed_data`` in middleware verification.
    """
    verifying = Web3.to_checksum_address(asset_address)
    nonce_bytes = _nonce_to_bytes32(authorization["nonce"])
    return {
        "domain": {
            "name": EIP712_DOMAIN_TOKEN_NAME,
            "version": EIP712_DOMAIN_TOKEN_VERSION,
            "chainId": chain_id,
            "verifyingContract": verifying,
        },
        "types": TRANSFER_WITH_AUTHORIZATION_TYPES,
        "message": {
            "from": authorization["from"],
            "to": authorization["to"],
            "value": int(authorization["value"]),
            "validAfter": int(authorization["validAfter"]),
            "validBefore": int(authorization["validBefore"]),
            "nonce": nonce_bytes,
        },
    }
