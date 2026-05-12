"""Hand-rolled x402 middleware for the Surprise API.

Implements exactly the fields NegotiatorGrid's buyer client produces:

* ``X-Payment`` header: base64(JSON) of the payment payload that
  :class:`negotiatorgrid.core.settlement.X402Settler` emits
  (``{"x402Version": 1, "scheme": "exact", "network": "eip155:2368",
  "payload": {"signature": "0x...", "authorization": {...}}}``).
* 402 response body: x402-compliant ``{"x402Version": 1, "accepts":
  [PaymentRequirements], "error": "..."}``.

Verification is pluggable:

1. If a ``facilitator_url`` is configured AND reachable, we POST the
   payload to ``/v2/verify`` → ``/v2/settle`` on the configured
   facilitator (e.g. Pieverse). This is the production path.
2. Otherwise we **locally verify** the EIP-712 signature (shared
   ``build_transfer_with_authorization_typed_data`` in
   ``negotiatorgrid.core.x402_eip712`` — same bytes32 nonce encoding as
   ``X402Settler``) and enforce replay protection via a nonce cache. This
   makes the demo work offline and in pytest, without ever accepting unsigned
   payments.

The middleware exposes a ``@require_payment("<price_atomic>")``
decorator for route-level pricing. The current pricing is read at
request time from a ``PricingStore`` so the negotiator can inject
dynamic prices produced by ``NegotiationExecutor``.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

import httpx
from eth_account import Account
from eth_account.messages import encode_typed_data
from fastapi import Request
from fastapi.responses import JSONResponse
from web3 import Web3

from negotiatorgrid.core.x402_eip712 import (
    DEFAULT_MAX_TIMEOUT_SECONDS,
    EIP712_DOMAIN_TOKEN_NAME,
    EIP712_DOMAIN_TOKEN_VERSION,
    X402_JSON_VERSION,
    build_transfer_with_authorization_typed_data,
    default_eip155_network,
    default_test_usdt_address,
    default_x402_scheme,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pricing store — shared between middleware + negotiator injection
# ---------------------------------------------------------------------------


@dataclass
class PricingStore:
    """In-memory map: ``route → atomic price (str, micro-USDT)``.

    Shared (by reference) between the FastAPI app and the discovery
    registration. The negotiator can mutate entries to reflect a freshly
    negotiated price before the buyer retries with ``X-Payment``.
    """

    prices: dict[str, str] = field(default_factory=dict)

    def set_price(self, route: str, atomic_price: int) -> None:
        self.prices[route] = str(int(atomic_price))

    def get_price(self, route: str) -> str | None:
        return self.prices.get(route)


# ---------------------------------------------------------------------------
# Nonce cache — replay protection
# ---------------------------------------------------------------------------


@dataclass
class NonceCache:
    """TTL-bounded set of used nonces. Not durable — per-process only.

    The TTL is set to ``validBefore - now`` per payment, so expired
    authorizations drop out naturally.
    """

    _seen: dict[str, float] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def check_and_record(self, nonce: str, expires_at: float) -> bool:
        """Return True if the nonce is fresh and record it; False if replayed."""
        now = time.time()
        async with self._lock:
            # Lazy GC
            stale = [k for k, exp in self._seen.items() if exp < now]
            for k in stale:
                self._seen.pop(k, None)
            if nonce in self._seen:
                return False
            self._seen[nonce] = expires_at
            return True


# ---------------------------------------------------------------------------
# Config + middleware
# ---------------------------------------------------------------------------


@dataclass
class X402MiddlewareConfig:
    """Configuration injected by the app factory."""

    seller_wallet: str
    network: str = field(default_factory=default_eip155_network)
    asset: str = field(default_factory=default_test_usdt_address)
    facilitator_url: str = ""
    service_name: str = "Surprise API"
    # Seconds allowed between sign-time and server receipt.
    max_timeout_seconds: int = DEFAULT_MAX_TIMEOUT_SECONDS

    @property
    def chain_id(self) -> int:
        try:
            return int(self.network.split(":")[-1])
        except (ValueError, AttributeError):
            return 2368


# ---------------------------------------------------------------------------
# Core verification flow
# ---------------------------------------------------------------------------


class X402PaymentError(Exception):
    """Raised when a payment payload is rejected. The ``code`` is
    surfaced in the 402 response ``error`` field."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


@dataclass
class PaymentVerification:
    """Result of verifying a decoded X-Payment payload."""

    payer: str
    amount: int
    tx_hash: str = ""  # populated when facilitator settles on-chain
    facilitator_used: bool = False


def _decode_x_payment(header_value: str) -> dict[str, Any]:
    """Base64-decode the X-Payment header value → JSON payload dict."""
    if not header_value:
        raise X402PaymentError("missing_payment", "X-Payment header required")
    try:
        raw = base64.b64decode(header_value, validate=True).decode("utf-8")
    except Exception as exc:
        raise X402PaymentError("malformed_payment", f"base64 decode failed: {exc}") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise X402PaymentError("malformed_payment", f"json decode failed: {exc}") from exc
    if not isinstance(payload, dict):
        raise X402PaymentError("malformed_payment", "payload must be a JSON object")
    return payload


def _verify_signature_local(
    authorization: dict[str, Any],
    signature_hex: str,
    asset_address: str,
    chain_id: int,
    expected_recipient: str,
    expected_amount: int,
) -> str:
    """Verify EIP-712 signature and business invariants. Returns payer address."""
    # Business invariants first — cheap and defensive.
    try:
        value = int(authorization.get("value", "0"))
    except (TypeError, ValueError) as exc:
        raise X402PaymentError("malformed_payment", f"bad value: {exc}") from exc

    if value < expected_amount:
        raise X402PaymentError(
            "invalid_exact_evm_amount",
            f"paid {value} < required {expected_amount}",
        )

    to_addr = (authorization.get("to") or "").lower()
    if to_addr != expected_recipient.lower():
        raise X402PaymentError(
            "invalid_exact_evm_recipient",
            f"paid to {to_addr} != seller {expected_recipient.lower()}",
        )

    try:
        valid_after = int(authorization.get("validAfter", "0"))
        valid_before = int(authorization.get("validBefore", "0"))
    except (TypeError, ValueError) as exc:
        raise X402PaymentError("malformed_payment", f"bad validity window: {exc}") from exc

    now = int(time.time())
    if valid_before <= now:
        raise X402PaymentError("invalid_exact_evm_expired", "authorization expired")
    if valid_after > now:
        raise X402PaymentError("invalid_exact_evm_not_yet_valid", "authorization not yet valid")

    # Now verify the signature.
    try:
        typed = build_transfer_with_authorization_typed_data(
            authorization, asset_address, chain_id
        )
        signable = encode_typed_data(
            domain_data=typed["domain"],
            message_types=typed["types"],
            message_data=typed["message"],
        )
        recovered = Account.recover_message(signable, signature=signature_hex)
    except Exception as exc:
        raise X402PaymentError(
            "invalid_exact_evm_signature",
            f"signature recovery failed: {exc}",
        ) from exc

    claimed_from = (authorization.get("from") or "").lower()
    if recovered.lower() != claimed_from:
        raise X402PaymentError(
            "invalid_exact_evm_signature",
            f"recovered {recovered} != claimed {claimed_from}",
        )

    return Web3.to_checksum_address(recovered)


async def _facilitator_verify_and_settle(
    facilitator_url: str,
    payment_payload: dict[str, Any],
    payment_requirements: dict[str, Any],
    timeout: float = 10.0,
) -> PaymentVerification | None:
    """Try the real facilitator. Returns ``None`` on failure so callers can fall back."""
    body = {
        "paymentPayload": payment_payload,
        "paymentRequirements": payment_requirements,
    }
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            v = await client.post(f"{facilitator_url}/v2/verify", json=body)
            data = v.json()
            if not data.get("isValid"):
                reason = data.get("invalidReason", "unknown")
                logger.info("Facilitator rejected payment: %s", reason)
                return None
            s = await client.post(f"{facilitator_url}/v2/settle", json=body)
            sdata = s.json()
            if not sdata.get("success"):
                return None
            auth = payment_payload["payload"]["authorization"]
            return PaymentVerification(
                payer=Web3.to_checksum_address(auth["from"]),
                amount=int(auth["value"]),
                tx_hash=sdata.get("transaction", ""),
                facilitator_used=True,
            )
    except Exception as exc:
        logger.info("Facilitator unreachable (%s); falling back to local verify", exc)
        return None


# ---------------------------------------------------------------------------
# The middleware itself
# ---------------------------------------------------------------------------


class X402PaymentMiddleware:
    """FastAPI middleware that gates protected routes behind x402 payment.

    Usage::

        config = X402MiddlewareConfig(seller_wallet="0x...")
        pricing = PricingStore()
        pricing.set_price("/api/weather", 25_000)  # 0.025 USDT
        middleware = X402PaymentMiddleware(config, pricing, {"/api/weather"})
        app.middleware("http")(middleware)
    """

    def __init__(
        self,
        config: X402MiddlewareConfig,
        pricing: PricingStore,
        protected_routes: set[str],
        nonce_cache: NonceCache | None = None,
    ) -> None:
        self.config = config
        self.pricing = pricing
        self.protected_routes = set(protected_routes)
        self.nonce_cache = nonce_cache or NonceCache()
        # Public, read-only for tests + dashboard introspection.
        self.receipts: list[dict[str, Any]] = []

    # -- Public protocol --------------------------------------------------

    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Any]],
    ) -> Any:
        path = request.url.path
        if path not in self.protected_routes:
            return await call_next(request)

        price_str = self.pricing.get_price(path)
        if price_str is None:
            # No price configured → gate is locked with a placeholder.
            price_str = "1"
        try:
            price_atomic = int(price_str)
        except ValueError:
            price_atomic = 1

        x_payment = request.headers.get("x-payment") or request.headers.get("X-Payment")

        if not x_payment:
            return self._build_402_response(
                path, price_atomic, error="payment_required"
            )

        try:
            verification = await self._verify_payment(path, price_atomic, x_payment)
        except X402PaymentError as exc:
            return self._build_402_response(
                path, price_atomic, error=exc.code
            )
        except Exception:
            logger.exception("Unexpected x402 verification error")
            return self._build_402_response(
                path, price_atomic, error="internal_error"
            )

        # Attach verification metadata for handlers / tests.
        request.state.x402_payment = {
            "payer": verification.payer,
            "amount": verification.amount,
            "tx_hash": verification.tx_hash,
            "facilitator_used": verification.facilitator_used,
        }
        # Record a receipt (bounded).
        self.receipts.append(
            {
                "route": path,
                "payer": verification.payer,
                "amount": verification.amount,
                "tx_hash": verification.tx_hash,
                "facilitator_used": verification.facilitator_used,
                "timestamp": time.time(),
            }
        )
        if len(self.receipts) > 200:
            self.receipts = self.receipts[-200:]

        return await call_next(request)

    # -- PaymentRequirements construction --------------------------------

    def build_payment_requirements(
        self, route: str, price_atomic: int
    ) -> dict[str, Any]:
        """Build x402 PaymentRequirements advertised in the 402 body."""
        return {
            "scheme": default_x402_scheme(),
            "network": self.config.network,
            "maxAmountRequired": str(price_atomic),
            "resource": route,
            "payTo": Web3.to_checksum_address(self.config.seller_wallet),
            "asset": self.config.asset,
            "maxTimeoutSeconds": self.config.max_timeout_seconds,
            "extra": {
                "name": EIP712_DOMAIN_TOKEN_NAME,
                "version": EIP712_DOMAIN_TOKEN_VERSION,
                "facilitator": self.config.facilitator_url,
                "service": self.config.service_name,
                "negotiation_protocol": "negotiatorgrid-v1",
            },
        }

    # -- Internals --------------------------------------------------------

    def _build_402_response(
        self, route: str, price_atomic: int, *, error: str
    ) -> JSONResponse:
        body = {
            "x402Version": X402_JSON_VERSION,
            "error": error,
            "accepts": [self.build_payment_requirements(route, price_atomic)],
        }
        return JSONResponse(status_code=402, content=body)

    async def _verify_payment(
        self, route: str, price_atomic: int, header_value: str
    ) -> PaymentVerification:
        payload = _decode_x_payment(header_value)

        if payload.get("x402Version") != X402_JSON_VERSION:
            raise X402PaymentError("unsupported_x402_version")
        if payload.get("scheme") != default_x402_scheme():
            raise X402PaymentError("unsupported_scheme")
        if payload.get("network") != self.config.network:
            raise X402PaymentError("wrong_network")

        inner = payload.get("payload") or {}
        authorization = inner.get("authorization") or {}
        signature_hex = inner.get("signature") or ""
        nonce = authorization.get("nonce") or ""

        if not authorization or not signature_hex or not nonce:
            raise X402PaymentError("malformed_payment", "missing auth/signature/nonce")

        # Replay protection BEFORE expensive signature ops.
        try:
            valid_before = int(authorization.get("validBefore", "0"))
        except (TypeError, ValueError):
            valid_before = int(time.time()) + 60
        fresh = await self.nonce_cache.check_and_record(nonce, float(valid_before))
        if not fresh:
            raise X402PaymentError("invalid_exact_evm_nonce_already_used", "replay detected")

        # Try facilitator first if configured.
        if self.config.facilitator_url:
            requirements = self.build_payment_requirements(route, price_atomic)
            via_facilitator = await _facilitator_verify_and_settle(
                self.config.facilitator_url, payload, requirements
            )
            if via_facilitator is not None:
                return via_facilitator

        # Local verify fallback (same crypto the buyer signed against).
        payer = _verify_signature_local(
            authorization=authorization,
            signature_hex=signature_hex,
            asset_address=self.config.asset,
            chain_id=self.config.chain_id,
            expected_recipient=self.config.seller_wallet,
            expected_amount=price_atomic,
        )
        return PaymentVerification(
            payer=payer,
            amount=int(authorization["value"]),
            tx_hash="",
            facilitator_used=False,
        )
