"""x402 buyer client — full HTTP 402 → sign → retry handshake.

The rest of NegotiatorGrid's settlement path (``X402Settler``) speaks
directly to the facilitator for the demo loop. That's fine when we
control both sides. But the Day-4 "Surprise API" seller is a distinct
process that only speaks the real 402 protocol, so we need a proper
client to talk to it.

This module is intentionally minimal and reuses the same EIP-712
typing as ``negotiatorgrid.core.x402_eip712`` / ``X402Settler``,
guaranteeing round-trip compatibility with the hand-rolled seller
middleware in ``surprise_api/x402_middleware.py``.
"""

from __future__ import annotations

import base64
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

import httpx
from eth_account import Account
from web3 import Web3

from negotiatorgrid.core.x402_eip712 import (
    X402_JSON_VERSION,
    build_transfer_with_authorization_typed_data,
    default_eip155_network,
    default_test_usdt_address,
    default_x402_scheme,
)

logger = logging.getLogger(__name__)


class X402BuyerError(Exception):
    """Raised when the buyer cannot complete a paid fetch."""


@dataclass
class X402FetchResult:
    """Outcome of a ``fetch_with_payment`` call."""

    status_code: int
    data: Any = None
    payment_amount: int = 0
    payer_address: str = ""
    resource_url: str = ""
    error: str = ""
    raw_accepts: list[dict[str, Any]] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.status_code == 200 and not self.error


class X402BuyerClient:
    """Minimal x402 buyer client that follows the 402 handshake.

    Example::

        buyer = X402BuyerClient(private_key="0x...")
        result = await buyer.fetch_with_payment(
            "http://localhost:8801/api/weather",
            max_price_atomic=30_000,
        )
        if result.success:
            print(result.data)
    """

    def __init__(
        self,
        *,
        private_key: str,
        max_retries: int = 1,
        http_client: httpx.AsyncClient | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not private_key:
            raise X402BuyerError("private_key is required")
        self._account = Account.from_key(private_key)
        self._max_retries = max_retries
        self._external_client = http_client
        # ``transport`` lets tests wire this straight to an ASGI app.
        self._transport = transport

    @property
    def address(self) -> str:
        return self._account.address

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def fetch_with_payment(
        self,
        url: str,
        *,
        method: str = "GET",
        params: dict[str, Any] | None = None,
        max_price_atomic: int | None = None,
    ) -> X402FetchResult:
        """Fetch a URL, paying an x402 toll if the server demands one.

        If ``max_price_atomic`` is set and the advertised price exceeds
        it, the call returns an ``X402FetchResult`` with an error code
        instead of paying — this is the spending-cap the negotiator
        enforces post-agreement.
        """
        client_cm = self._client()
        async with client_cm as client:
            resp = await client.request(method, url, params=params)

            if resp.status_code != 402:
                # Either the server didn't gate the route, or we got an
                # error before the gate. Return raw.
                return X402FetchResult(
                    status_code=resp.status_code,
                    data=self._decode_body(resp),
                    resource_url=url,
                )

            try:
                body = resp.json()
            except ValueError:
                return X402FetchResult(
                    status_code=402,
                    resource_url=url,
                    error="malformed_402_response",
                )

            accepts = body.get("accepts") or []
            if not accepts:
                return X402FetchResult(
                    status_code=402,
                    resource_url=url,
                    error=body.get("error", "no_accepts_in_402"),
                )

            # Prefer "exact" scheme on the chain we expect.
            requirements = self._select_requirements(accepts)
            price = int(requirements.get("maxAmountRequired", "0"))

            if max_price_atomic is not None and price > max_price_atomic:
                return X402FetchResult(
                    status_code=402,
                    resource_url=url,
                    error="over_budget",
                    raw_accepts=accepts,
                    payment_amount=price,
                )

            payment_header = self._build_payment_header(requirements)

            # Retry with the payment header.
            paid_resp = await client.request(
                method, url, params=params, headers={"X-Payment": payment_header}
            )
            return X402FetchResult(
                status_code=paid_resp.status_code,
                data=self._decode_body(paid_resp),
                payment_amount=price,
                payer_address=self._account.address,
                resource_url=url,
                error="" if paid_resp.status_code == 200 else "payment_rejected",
                raw_accepts=accepts if paid_resp.status_code != 200 else [],
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _client(self) -> httpx.AsyncClient:
        if self._external_client is not None:
            # Caller owns lifecycle; wrap in a no-op async context.
            return _ProvidedClient(self._external_client)  # type: ignore[return-value]
        kwargs: dict[str, Any] = {"timeout": 15.0}
        if self._transport is not None:
            kwargs["transport"] = self._transport
        return httpx.AsyncClient(**kwargs)

    @staticmethod
    def _decode_body(resp: httpx.Response) -> Any:
        ctype = resp.headers.get("content-type", "")
        if "application/json" in ctype:
            try:
                return resp.json()
            except ValueError:
                return resp.text
        return resp.text

    @staticmethod
    def _select_requirements(accepts: list[dict[str, Any]]) -> dict[str, Any]:
        # Preference order: exact + eip155:2368, then exact any, else first.
        for req in accepts:
            if req.get("scheme") == default_x402_scheme() and req.get("network") == default_eip155_network():
                return req
        for req in accepts:
            if req.get("scheme") == default_x402_scheme():
                return req
        return accepts[0]

    def _build_payment_header(self, requirements: dict[str, Any]) -> str:
        network = requirements.get("network", default_eip155_network())
        try:
            chain_id = int(network.split(":")[-1])
        except ValueError:
            chain_id = 2368
        asset = requirements.get("asset", default_test_usdt_address())
        pay_to = Web3.to_checksum_address(requirements["payTo"])
        value = str(int(requirements.get("maxAmountRequired", "0")))
        timeout = int(requirements.get("maxTimeoutSeconds", 300))

        nonce_bytes = bytes(
            Web3.keccak(text=f"{self._account.address}{time.time_ns()}")
        )
        nonce_hex = "0x" + nonce_bytes.hex()

        authorization = {
            "from": self._account.address,
            "to": pay_to,
            "value": value,
            "validAfter": "0",
            "validBefore": str(int(time.time()) + timeout),
            "nonce": nonce_hex,
        }

        typed = build_transfer_with_authorization_typed_data(authorization, asset, chain_id)
        signed = self._account.sign_typed_data(
            typed["domain"], typed["types"], typed["message"]
        )
        signature_hex = signed.signature.hex()
        if not signature_hex.startswith("0x"):
            signature_hex = "0x" + signature_hex

        payment_payload = {
            "x402Version": X402_JSON_VERSION,
            "scheme": requirements.get("scheme", default_x402_scheme()),
            "network": network,
            "payload": {
                "signature": signature_hex,
                "authorization": authorization,
            },
        }
        return base64.b64encode(
            json.dumps(payment_payload, separators=(",", ":")).encode("utf-8")
        ).decode("ascii")


class _ProvidedClient:
    """Trivial async context that yields a caller-owned client."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def __aenter__(self) -> httpx.AsyncClient:
        return self._client

    async def __aexit__(self, *exc_info: Any) -> None:
        return None
