"""Live Surprise API + Kite pipeline — same stages as ``demo.py`` Act 2 (D–F).

Used by the FastAPI host so the Next.js dashboard receives the same WebSocket
``pipeline_stage`` / settlement events as the CLI demo (hash-mismatch hero,
``/admin/sync-deal``, real x402, ``DealRecord.recordDeal``).
"""

from __future__ import annotations

import base64
import json
import logging
import os
import time
from collections.abc import Awaitable, Callable
from typing import Any

import httpx
from eth_account.signers.local import LocalAccount
from web3 import Web3

from negotiatorgrid.config import config
from negotiatorgrid.core.deal_hash import (
    compute_binding_deal_hash_bytes_from_result,
    compute_binding_deal_hash_hex_from_result,
)
from negotiatorgrid.core.settlement import DealHashMismatchError, X402Settler
from negotiatorgrid.core.types import DealAttestation, SLATerms
from negotiatorgrid.core.x402_eip712 import (
    DEFAULT_MAX_TIMEOUT_SECONDS,
    X402_JSON_VERSION,
    build_transfer_with_authorization_typed_data,
)
from negotiatorgrid.executors.negotiation import AgentConfig, WireNegotiationResult
from negotiatorgrid.post_negotiation import SettlementInfo, build_clients
from negotiatorgrid.post_negotiation import wire_negotiation_result_to_core
from negotiatorgrid.utils.web3_helpers import explorer_tx_url

logger = logging.getLogger(__name__)

NotifyFn = Callable[[str, dict[str, Any]], Awaitable[None]]

NVDA_ROUTE = "/api/nvda"
USDT_DECIMALS = 1_000_000


def surprise_base_url() -> str:
    """Base URL for ``surprise_api`` (no trailing slash)."""
    return os.getenv("SURPRISE_API_URL", "http://127.0.0.1:8001").rstrip("/")


async def fetch_agent_json(client: httpx.AsyncClient, base_url: str) -> dict[str, Any]:
    r = await client.get(f"{base_url}/.well-known/agent.json", timeout=10.0)
    r.raise_for_status()
    return r.json()


async def fetch_402_payment_requirements(
    client: httpx.AsyncClient, base_url: str, route: str
) -> dict[str, Any]:
    r = await client.get(f"{base_url}{route}", timeout=15.0)
    if r.status_code != 402:
        raise RuntimeError(
            f"Expected 402 from {route}, got {r.status_code}: {r.text[:200]}"
        )
    body = r.json()
    accepts = body.get("accepts") or []
    if not accepts:
        raise RuntimeError(f"402 body had no 'accepts' array: {body}")
    return accepts[0]


async def post_sync_deal(
    client: httpx.AsyncClient,
    base_url: str,
    *,
    route: str,
    price_atomic: int,
    deal_hash_hex: str,
    expected_buyer: str,
) -> dict[str, Any]:
    r = await client.post(
        f"{base_url}/admin/sync-deal",
        json={
            "route": route,
            "price_atomic": price_atomic,
            "deal_hash": deal_hash_hex,
            "expected_buyer": expected_buyer,
        },
        timeout=10.0,
    )
    r.raise_for_status()
    return r.json()


def _sign_x_payment_header(
    *,
    buyer: LocalAccount,
    payment_requirements: dict[str, Any],
) -> str:
    asset = payment_requirements.get("asset", config.kite.test_usdt_addr)
    pay_to = payment_requirements["payTo"]
    amount = payment_requirements["maxAmountRequired"]
    network = payment_requirements.get("network", config.x402.network)
    chain_id = int(str(network).split(":")[-1])

    nonce_hex = "0x" + Web3.keccak(text=f"{buyer.address}{time.time_ns()}").hex().lstrip("0x")
    nonce_hex = "0x" + nonce_hex[2:].rjust(64, "0")
    valid_before = int(time.time()) + int(
        payment_requirements.get("maxTimeoutSeconds", DEFAULT_MAX_TIMEOUT_SECONDS)
    )

    authorization = {
        "from": buyer.address,
        "to": pay_to,
        "value": str(amount),
        "validAfter": "0",
        "validBefore": str(valid_before),
        "nonce": nonce_hex,
    }
    typed = build_transfer_with_authorization_typed_data(authorization, asset, chain_id)
    signed = buyer.sign_typed_data(typed["domain"], typed["types"], typed["message"])
    sig_hex = signed.signature.hex()
    if not sig_hex.startswith("0x"):
        sig_hex = "0x" + sig_hex

    payment_payload = {
        "x402Version": X402_JSON_VERSION,
        "scheme": payment_requirements.get("scheme", "exact"),
        "network": network,
        "payload": {
            "signature": sig_hex,
            "authorization": authorization,
        },
    }
    raw = json.dumps(payment_payload).encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


async def pay_nvda_route(
    client: httpx.AsyncClient,
    base_url: str,
    *,
    route: str,
    payment_requirements: dict[str, Any],
    buyer: LocalAccount,
) -> dict[str, Any]:
    header = _sign_x_payment_header(
        buyer=buyer, payment_requirements=payment_requirements
    )
    r = await client.get(
        f"{base_url}{route}",
        headers={"X-Payment": header},
        timeout=20.0,
    )
    r.raise_for_status()
    return r.json()


async def execute_nvda_post_negotiation(
    *,
    http_client: httpx.AsyncClient,
    exec_result: WireNegotiationResult,
    buyer_cfg: AgentConfig,
    seller_cfg: AgentConfig,
    seller_wallet: str,
    onchain_seller_agent_id: int,
    buyer_account: LocalAccount,
    notify: NotifyFn,
    resource_uri: str = NVDA_ROUTE,
) -> SettlementInfo:
    """Hash-mismatch demo, policy sync, x402 pay, ``DealRecord`` — mirrors ``demo.py``."""
    start = time.time()
    info = SettlementInfo()
    base = surprise_base_url()
    settler = X402Settler()

    if not exec_result.success or exec_result.agreed_price <= 0:
        info.pipeline_error = "negotiation_failed_or_zero_price"
        info.duration_seconds = time.time() - start
        return info

    core_nr = wire_negotiation_result_to_core(exec_result, buyer_cfg, seller_cfg)
    core_nr.buyer_id = buyer_account.address
    core_nr.seller_id = Web3.to_checksum_address(seller_wallet)
    bound_at = int(exec_result.deal_bound_at or int(time.time()))
    core_nr.deal_bound_at = bound_at

    deal_hash_hex = compute_binding_deal_hash_hex_from_result(
        core_nr, bound_at=bound_at, resource_uri=resource_uri
    )
    agreed_atomic = int(round(float(exec_result.agreed_price) * USDT_DECIMALS))

    await notify(
        "pipeline_stage",
        {
            "phase": "hash_mismatch",
            "title": "Stale 402 vs negotiated deal",
            "detail": "Buyer fetches list-price 402 before seller sync.",
        },
    )
    await notify(
        "settlement_started",
        {
            "negotiation_id": exec_result.negotiation_id,
            "agreed_price": exec_result.agreed_price,
            "atomic_amount": agreed_atomic,
            "seller_wallet": seller_wallet,
            "mode": "surprise_live",
        },
    )

    try:
        stale_pr = await fetch_402_payment_requirements(
            http_client, base, resource_uri
        )
        settler.verify_payment_requirements(
            agreed_price_atomic=agreed_atomic,
            deal_hash=deal_hash_hex,
            seller_wallet=seller_wallet,
            resource_url=resource_uri,
            payment_requirements=stale_pr,
        )
        await notify(
            "pipeline_stage",
            {
                "phase": "hash_mismatch",
                "title": "Unexpected pass",
                "detail": "Stale 402 matched — reset surprise_api /admin/reset.",
            },
        )
    except DealHashMismatchError as exc:
        await notify(
            "pipeline_stage",
            {
                "phase": "hash_mismatch",
                "title": "Payment blocked (stale or tampered 402)",
                "field": exc.field,
                "expected": str(exc.expected)[:66],
                "actual": str(exc.actual)[:66],
            },
        )

    tampered = dict(await fetch_402_payment_requirements(http_client, base, resource_uri))
    tampered["maxAmountRequired"] = str(agreed_atomic)
    tampered["extra"] = {**tampered.get("extra", {}), "deal_hash": "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"}
    try:
        settler.verify_payment_requirements(
            agreed_price_atomic=agreed_atomic,
            deal_hash=deal_hash_hex,
            seller_wallet=seller_wallet,
            resource_url=resource_uri,
            payment_requirements=tampered,
        )
        await notify(
            "pipeline_stage",
            {
                "phase": "tampered_hash",
                "title": "Tamper check did not reject",
                "detail": "Verify deal_hash binding logic.",
            },
        )
    except DealHashMismatchError:
        await notify(
            "pipeline_stage",
            {
                "phase": "tampered_hash",
                "title": "Tampered deal_hash rejected",
                "detail": "Same price, mutated extra.deal_hash — blocked.",
            },
        )

    await notify(
        "pipeline_stage",
        {
            "phase": "policy_sync",
            "title": "Policy sync → Surprise API",
            "detail": f"POST /admin/sync-deal ({resource_uri})",
        },
    )
    await post_sync_deal(
        http_client,
        base,
        route=resource_uri,
        price_atomic=agreed_atomic,
        deal_hash_hex=deal_hash_hex,
        expected_buyer=buyer_account.address,
    )

    fresh_pr = await fetch_402_payment_requirements(http_client, base, resource_uri)
    settler.verify_payment_requirements(
        agreed_price_atomic=agreed_atomic,
        deal_hash=deal_hash_hex,
        seller_wallet=seller_wallet,
        resource_url=resource_uri,
        payment_requirements=fresh_pr,
    )
    await notify(
        "pipeline_stage",
        {
            "phase": "x402_settle",
            "title": "x402 settlement",
            "detail": "EIP-712 TransferWithAuthorization → X-Payment",
        },
    )

    paid = await pay_nvda_route(
        http_client,
        base,
        route=resource_uri,
        payment_requirements=fresh_pr,
        buyer=buyer_account,
    )
    x402_tx = str(paid.get("tx_hash") or "")
    info.settled = True
    info.x402_tx_hash = x402_tx
    info.x402_network = config.x402.network
    await notify(
        "settlement_completed",
        {
            "success": True,
            "tx_hash": x402_tx,
            "network": info.x402_network,
            "paid_atomic": paid.get("paid_amount_atomic", 0),
            "facilitator_used": paid.get("facilitator_used"),
        },
    )

    clients = build_clients()
    info.mock_mode = clients.any_mock

    await notify(
        "attestation_started",
        {
            "negotiation_id": exec_result.negotiation_id,
            "deal_hash": deal_hash_hex,
            "mock_mode": info.mock_mode,
        },
    )

    opening_buyer = 0
    opening_seller = 0
    for offer in core_nr.transcript:
        if offer.agent_id == core_nr.buyer_id and opening_buyer == 0:
            opening_buyer = int(float(offer.price) * USDT_DECIMALS)
        elif offer.agent_id == core_nr.seller_id and opening_seller == 0:
            opening_seller = int(float(offer.price) * USDT_DECIMALS)

    x402_bytes = (
        bytes.fromhex(x402_tx.removeprefix("0x"))
        if x402_tx and len(x402_tx) >= 66
        else b"\x00" * 32
    )
    attestation = DealAttestation(
        deal_hash=compute_binding_deal_hash_bytes_from_result(
            core_nr, bound_at=bound_at, resource_uri=resource_uri
        ),
        buyer=Web3.to_checksum_address(buyer_account.address),
        seller=Web3.to_checksum_address(seller_wallet),
        buyer_agent_id=0,
        seller_agent_id=int(onchain_seller_agent_id),
        resource_uri=resource_uri,
        opening_buyer_price=opening_buyer,
        opening_seller_price=opening_seller,
        final_price=agreed_atomic,
        negotiation_rounds=int(exec_result.total_rounds or 0),
        sla=SLATerms(),
        x402_tx_hash=x402_bytes,
        timestamp=bound_at,
        settled=bool(x402_tx),
    )
    try:
        record_tx = await clients.deal_record.record_deal(attestation)
        info.attestation_tx = record_tx
        info.attestation_deal_hash = deal_hash_hex
    except Exception as exc:
        logger.exception("DealRecord.record_deal failed")
        info.pipeline_error = f"attestation: {exc}"

    if info.x402_tx_hash and not info.mock_mode:
        info.kitescan_tx_url = explorer_tx_url(info.x402_tx_hash)
    if info.attestation_tx and not info.mock_mode:
        info.kitescan_attestation_url = explorer_tx_url(info.attestation_tx)

    info.duration_seconds = time.time() - start
    await notify(
        "attestation_completed",
        {
            "deal_hash": info.attestation_deal_hash,
            "attestation_tx": info.attestation_tx,
            "kitescan_url": info.kitescan_attestation_url,
            "mock_mode": info.mock_mode,
            "duration_seconds": info.duration_seconds,
            "error": info.pipeline_error,
        },
    )
    await notify(
        "pipeline_stage",
        {
            "phase": "complete",
            "title": "Pipeline complete",
            "x402_tx": x402_tx[:22] if x402_tx else "",
            "dealrecord_tx": (info.attestation_tx or "")[:22],
        },
    )
    return info


__all__ = [
    "NVDA_ROUTE",
    "execute_nvda_post_negotiation",
    "fetch_agent_json",
    "surprise_base_url",
]
