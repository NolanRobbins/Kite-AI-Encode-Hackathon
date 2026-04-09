"""Mock x402 facilitator for local testing.

Used when KITE_FACILITATOR_URL is not set or unreachable.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

from web3 import Web3

logger = logging.getLogger(__name__)


class MockFacilitator:
    """Simulates the x402 facilitator verify/settle endpoints.

    Every call succeeds — intended for demo and integration testing only.
    """

    async def verify(self, payment_payload: dict[str, Any]) -> dict[str, Any]:
        """Validate a payment payload (always returns valid)."""
        payer = payment_payload.get("payload", {}).get("authorization", {}).get("from", "")
        logger.info("MockFacilitator.verify: payer=%s", payer)
        return {
            "isValid": True,
            "invalidReason": "",
            "payer": payer,
            "extensions": {},
        }

    async def settle(self, payment_payload: dict[str, Any]) -> dict[str, Any]:
        """Simulate an on-chain settlement (returns a deterministic fake tx hash)."""
        raw = (
            payment_payload.get("payload", {})
            .get("authorization", {})
            .get("nonce", str(time.time_ns()))
        )
        fake_tx = Web3.keccak(text=str(raw)).hex()
        logger.info("MockFacilitator.settle: fake_tx=%s", fake_tx)
        return {
            "success": True,
            "errorReason": "",
            "payer": payment_payload.get("payload", {}).get("authorization", {}).get("from", ""),
            "transaction": fake_tx,
            "network": "eip155:2368",
            "amount": payment_payload.get("payload", {}).get("authorization", {}).get("value", "0"),
        }
