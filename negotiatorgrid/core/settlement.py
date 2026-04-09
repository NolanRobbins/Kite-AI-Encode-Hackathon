"""x402 payment settlement for NegotiatorGrid."""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import httpx
from eth_account import Account
from eth_account.messages import encode_typed_data
from web3 import Web3

from negotiatorgrid.config import X402Config, config
from negotiatorgrid.core.types import PaymentRequirements, SettlementResult
from negotiatorgrid.utils.mock_facilitator import MockFacilitator

logger = logging.getLogger(__name__)

# Permanent x402 error codes that should not be retried.
PERMANENT_FAILURES = frozenset({
    "invalid_exact_evm_nonce_already_used",
    "invalid_exact_evm_insufficient_balance",
    "invalid_exact_evm_signature",
})


class X402Settler:
    """Handles x402 payment settlement between negotiating agents.

    In demo mode (facilitator unreachable or not configured), a
    :class:`MockFacilitator` is used transparently.
    """

    def __init__(self, x402_config: X402Config | None = None, private_key: str = "") -> None:
        self._config = x402_config or config.x402
        self._private_key = private_key or config.kite.private_key
        self._mock_facilitator: MockFacilitator | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_payment_requirements(
        self,
        agreed_price: int,
        seller_wallet: str,
        resource_url: str = "",
        deal_hash: str = "",
    ) -> dict[str, Any]:
        """Build a PaymentRequirements dict for a negotiated deal.

        *agreed_price* is in **atomic units** (6 decimals for USDT, so
        1.50 USDT = 1_500_000).
        """
        return {
            "scheme": self._config.scheme,
            "network": self._config.network,
            "maxAmountRequired": str(agreed_price),
            "resource": resource_url,
            "payTo": Web3.to_checksum_address(seller_wallet),
            "asset": config.kite.test_usdt_addr,
            "maxTimeoutSeconds": 300,
            "extra": {
                "name": "USDT",
                "version": "2",
                "facilitator": self._config.facilitator_url,
                **({"deal_hash": deal_hash} if deal_hash else {}),
                "negotiation_protocol": "negotiatorgrid-v1",
            },
        }

    async def settle_payment(
        self,
        payment_requirements: dict[str, Any],
        buyer_private_key: str | None = None,
    ) -> SettlementResult:
        """Execute the x402 payment flow.

        Simplified for the demo: directly calls the facilitator's verify
        and settle endpoints instead of going through the full HTTP 402
        handshake (since we control both buyer and seller).

        Falls back to :class:`MockFacilitator` if the real facilitator
        is unreachable.
        """
        pkey = buyer_private_key or self._private_key
        if not pkey:
            logger.error("No private key available for settlement")
            return SettlementResult(success=False, error_reason="no_private_key")

        account = Account.from_key(pkey)
        pay_to = payment_requirements.get("payTo", "")
        amount = payment_requirements.get("maxAmountRequired", "0")
        asset = payment_requirements.get("asset", config.kite.test_usdt_addr)

        # Build EIP-712 typed-data payload
        nonce = Web3.keccak(text=f"{account.address}{time.time_ns()}").hex()
        valid_before = int(time.time()) + payment_requirements.get("maxTimeoutSeconds", 300)

        authorization = {
            "from": account.address,
            "to": pay_to,
            "value": amount,
            "validAfter": "0",
            "validBefore": str(valid_before),
            "nonce": nonce,
        }

        # Sign the authorization
        typed_data = _build_eip712_typed_data(
            authorization, asset, int(self._config.network.split(":")[-1])
        )
        try:
            signed = account.sign_typed_data(
                typed_data["domain"],
                typed_data["types"],
                typed_data["message"],
            )
            signature = signed.signature.hex()
        except Exception:
            logger.exception("EIP-712 signing failed")
            return SettlementResult(success=False, error_reason="signing_failed")

        payment_payload = {
            "x402Version": 1,
            "scheme": self._config.scheme,
            "network": self._config.network,
            "payload": {
                "signature": f"0x{signature}",
                "authorization": authorization,
            },
        }

        # Try real facilitator first, fall back to mock
        result = await self._call_facilitator(payment_payload, payment_requirements)
        return result

    async def verify_settlement(self, tx_hash: str) -> bool:
        """Check on KiteScan that a settlement tx exists and succeeded."""
        if not tx_hash or tx_hash.startswith("0x" + "f" * 10):
            # Clearly a mock hash
            logger.info("Mock tx hash detected; skipping verification")
            return True

        try:
            w3 = Web3(Web3.HTTPProvider(config.kite.rpc_url))
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            return receipt["status"] == 1
        except Exception:
            logger.exception("Settlement verification failed for %s", tx_hash)
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _call_facilitator(
        self,
        payment_payload: dict[str, Any],
        payment_requirements: dict[str, Any],
    ) -> SettlementResult:
        """Call the facilitator verify+settle endpoints with failover."""
        facilitator_url = self._config.facilitator_url

        # Skip real facilitator if URL is empty
        if not facilitator_url:
            return await self._mock_settle(payment_payload)

        body = {
            "paymentPayload": payment_payload,
            "paymentRequirements": payment_requirements,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Step 1: Verify
                verify_resp = await client.post(
                    f"{facilitator_url}/v2/verify", json=body
                )
                verify_data = verify_resp.json()

                if not verify_data.get("isValid"):
                    reason = verify_data.get("invalidReason", "unknown")
                    if reason in PERMANENT_FAILURES:
                        return SettlementResult(success=False, error_reason=reason)
                    # Transient failure — fall back to mock for demo
                    logger.warning("Facilitator verify rejected: %s; using mock", reason)
                    return await self._mock_settle(payment_payload)

                # Step 2: Settle
                settle_resp = await client.post(
                    f"{facilitator_url}/v2/settle", json=body
                )
                settle_data = settle_resp.json()

                if settle_data.get("success"):
                    return SettlementResult(
                        success=True,
                        tx_hash=settle_data.get("transaction", ""),
                        payer=settle_data.get("payer", ""),
                        network=settle_data.get("network", ""),
                        amount=settle_data.get("amount", ""),
                    )
                else:
                    return SettlementResult(
                        success=False,
                        error_reason=settle_data.get("errorReason", "unknown"),
                    )
        except Exception:
            logger.warning("Facilitator unreachable; falling back to mock settlement")
            return await self._mock_settle(payment_payload)

    async def _mock_settle(self, payment_payload: dict[str, Any]) -> SettlementResult:
        """Use the mock facilitator as a fallback."""
        if self._mock_facilitator is None:
            self._mock_facilitator = MockFacilitator()

        settle_data = await self._mock_facilitator.settle(payment_payload)
        return SettlementResult(
            success=settle_data.get("success", False),
            tx_hash=settle_data.get("transaction", ""),
            payer=settle_data.get("payer", ""),
            network=settle_data.get("network", ""),
            amount=settle_data.get("amount", ""),
        )


# ------------------------------------------------------------------
# EIP-712 helpers
# ------------------------------------------------------------------

def _build_eip712_typed_data(
    authorization: dict[str, Any],
    asset_address: str,
    chain_id: int,
) -> dict[str, Any]:
    """Build EIP-712 typed data for TransferWithAuthorization (EIP-3009)."""
    return {
        "domain": {
            "name": "USDT",
            "version": "2",
            "chainId": chain_id,
            "verifyingContract": asset_address,
        },
        "types": {
            "TransferWithAuthorization": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"},
                {"name": "nonce", "type": "bytes32"},
            ],
        },
        "message": {
            "from": authorization["from"],
            "to": authorization["to"],
            "value": int(authorization["value"]),
            "validAfter": int(authorization["validAfter"]),
            "validBefore": int(authorization["validBefore"]),
            "nonce": authorization["nonce"],
        },
    }
