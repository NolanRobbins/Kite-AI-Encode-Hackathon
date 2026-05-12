"""x402 payment settlement for NegotiatorGrid."""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx
from eth_account import Account
from web3 import Web3

from negotiatorgrid.config import X402Config, config
from negotiatorgrid.core.types import PaymentRequirements, SettlementResult
from negotiatorgrid.core.x402_eip712 import (
    DEFAULT_MAX_TIMEOUT_SECONDS,
    EIP712_DOMAIN_TOKEN_NAME,
    EIP712_DOMAIN_TOKEN_VERSION,
    X402_JSON_VERSION,
    build_transfer_with_authorization_typed_data,
    chain_id_from_eip155,
)
from negotiatorgrid.utils.mock_facilitator import MockFacilitator

logger = logging.getLogger(__name__)

# Permanent x402 error codes that should not be retried.
PERMANENT_FAILURES = frozenset({
    "invalid_exact_evm_nonce_already_used",
    "invalid_exact_evm_insufficient_balance",
    "invalid_exact_evm_signature",
})


class DealHashMismatchError(Exception):
    """Raised when payment requirements don't match the negotiated deal."""

    def __init__(
        self,
        message: str,
        field: str = "",
        expected: Any = None,
        actual: Any = None,
        actual_atomic: int | None = None,
    ) -> None:
        super().__init__(message)
        self.field = field
        self.expected = expected
        self.actual = actual
        self.actual_atomic = actual_atomic


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
            "maxTimeoutSeconds": DEFAULT_MAX_TIMEOUT_SECONDS,
            "extra": {
                "name": EIP712_DOMAIN_TOKEN_NAME,
                "version": EIP712_DOMAIN_TOKEN_VERSION,
                "facilitator": self._config.facilitator_url,
                **({"deal_hash": deal_hash} if deal_hash else {}),
                "negotiation_protocol": "negotiatorgrid-v1",
            },
        }

    def verify_payment_requirements(
        self,
        agreed_price_atomic: int,
        deal_hash: str,
        seller_wallet: str,
        resource_url: str,
        payment_requirements: dict[str, Any],
    ) -> None:
        """Verify that payment requirements match the agreed deal terms.

        Raises:
            DealHashMismatchError: If any field doesn't match expected values.
        """
        # Verify amount
        actual_amount = int(payment_requirements.get("maxAmountRequired", "0"))
        if actual_amount != agreed_price_atomic:
            raise DealHashMismatchError(
                f"Payment amount mismatch: expected {agreed_price_atomic}, got {actual_amount}",
                field="maxAmountRequired",
                expected=agreed_price_atomic,
                actual=actual_amount,
                actual_atomic=actual_amount,
            )

        # Verify seller wallet
        actual_payto = payment_requirements.get("payTo", "").lower()
        expected_payto = Web3.to_checksum_address(seller_wallet).lower()
        if actual_payto != expected_payto:
            raise DealHashMismatchError(
                f"Payment recipient mismatch: expected {expected_payto}, got {actual_payto}",
                field="payTo",
                expected=expected_payto,
                actual=actual_payto,
            )

        # Verify resource URL
        actual_resource = payment_requirements.get("resource", "")
        if actual_resource != resource_url:
            raise DealHashMismatchError(
                f"Resource URL mismatch: expected {resource_url}, got {actual_resource}",
                field="resource",
                expected=resource_url,
                actual=actual_resource,
            )

        # Verify deal hash in extra field (if deal_hash is provided)
        if deal_hash:
            extra = payment_requirements.get("extra", {})
            actual_deal_hash = extra.get("deal_hash", "")
            if actual_deal_hash != deal_hash:
                raise DealHashMismatchError(
                    f"Deal hash mismatch: expected {deal_hash}, got {actual_deal_hash}",
                    field="deal_hash",
                    expected=deal_hash,
                    actual=actual_deal_hash,
                )

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
        valid_before = int(time.time()) + payment_requirements.get(
            "maxTimeoutSeconds", DEFAULT_MAX_TIMEOUT_SECONDS
        )

        authorization = {
            "from": account.address,
            "to": pay_to,
            "value": amount,
            "validAfter": "0",
            "validBefore": str(valid_before),
            "nonce": nonce,
        }

        # Sign the authorization
        typed_data = build_transfer_with_authorization_typed_data(
            authorization, asset, chain_id_from_eip155(self._config.network)
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
            "x402Version": X402_JSON_VERSION,
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


# Backwards-compatible name for callers that imported the private helper.
_build_eip712_typed_data = build_transfer_with_authorization_typed_data
