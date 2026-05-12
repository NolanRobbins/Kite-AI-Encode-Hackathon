"""Post-negotiation pipeline: x402 settlement + on-chain attestation.

This module is the glue between the ``NegotiationExecutor`` (which produces
a :class:`negotiatorgrid.executors.negotiation.WireNegotiationResult`) and the on-chain layer (``X402Settler``
+ ``AttestationPipeline``).

Design goals
------------
* Safe by default: if any env is missing (no private key, no facilitator,
  no contract addresses), the pipeline transparently runs on the
  ``MockFacilitator`` + mock contract clients.  Demos never crash.
* Best-effort: settlement and attestation failures never raise upward.
  The deal record is always returned with ``pipeline_error`` populated
  so the API and dashboard can surface partial success.
* Streaming: emits ``settlement_started``, ``settlement_completed``,
  ``attestation_started`` and ``attestation_completed`` events via the
  shared WebSocket broadcaster so the dashboard can animate each stage.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

from web3 import Web3

from negotiatorgrid.api.websocket import broadcaster
from negotiatorgrid.config import config
from negotiatorgrid.contracts.deal_record import DealRecordClient
from negotiatorgrid.contracts.identity import IdentityClient
from negotiatorgrid.contracts.reputation_client import ReputationClient
from negotiatorgrid.core.attestation import AttestationPipeline
from negotiatorgrid.core.settlement import DealHashMismatchError, X402Settler
from negotiatorgrid.core.types import (
    NegotiationOffer as CoreOffer,
)
from negotiatorgrid.core.types import (
    NegotiationResult as CoreNegotiationResult,
)
from negotiatorgrid.executors.malicious_seller import inflate_payment_requirements
from negotiatorgrid.executors.negotiation import (
    AgentConfig,
    WireNegotiationResult,
)
from negotiatorgrid.utils.web3_helpers import explorer_tx_url, get_web3

logger = logging.getLogger(__name__)


_FALLBACK_SELLER_ADDRESS = "0x000000000000000000000000000000000000dEaD"


# ---------------------------------------------------------------------------
# Result bundle
# ---------------------------------------------------------------------------


@dataclass
class SettlementInfo:
    """Bundle of outputs from the settle + attest pipeline."""

    settled: bool = False
    x402_tx_hash: str = ""
    x402_network: str = ""
    attestation_tx: str = ""
    attestation_deal_hash: str = ""
    kitescan_tx_url: str = ""
    kitescan_attestation_url: str = ""
    pipeline_error: str = ""
    mock_mode: bool = True
    duration_seconds: float = 0.0
    # Act 5 — payment refused before signing (hash / amount mismatch).
    payment_refused: bool = False
    rejection_reason: str = ""
    expected_atomic: int = 0
    requested_atomic: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "settled": self.settled,
            "x402_tx_hash": self.x402_tx_hash,
            "x402_network": self.x402_network,
            "attestation_tx": self.attestation_tx,
            "attestation_deal_hash": self.attestation_deal_hash,
            "kitescan_tx_url": self.kitescan_tx_url,
            "kitescan_attestation_url": self.kitescan_attestation_url,
            "pipeline_error": self.pipeline_error,
            "mock_mode": self.mock_mode,
            "duration_seconds": round(self.duration_seconds, 3),
            "payment_refused": self.payment_refused,
            "rejection_reason": self.rejection_reason,
            "expected_atomic": self.expected_atomic,
            "requested_atomic": self.requested_atomic,
        }


# ---------------------------------------------------------------------------
# Client factory
# ---------------------------------------------------------------------------


@dataclass
class OnChainClients:
    """Bundle of on-chain clients. Any field may be in mock mode."""

    deal_record: DealRecordClient
    identity: IdentityClient
    reputation: ReputationClient
    any_mock: bool = True


def build_clients() -> OnChainClients:
    """Construct the three on-chain clients with graceful mock fallback.

    If either the RPC is unreachable, the private key is missing, or the
    contract address env var is empty, that client runs in mock mode.
    We never raise from here — the pipeline must always return *some*
    client bundle so the demo keeps running.
    """
    w3: Web3 | None = None
    pkey = config.kite.private_key

    try:
        w3 = get_web3()
        if not w3.is_connected():
            logger.info("RPC not connected; forcing mock clients")
            w3 = None
    except Exception:
        logger.exception("Web3 init failed; forcing mock clients")
        w3 = None

    # An empty contract address triggers mock mode in each client.
    deal_addr = config.contracts.deal_record if w3 and pkey else ""
    ident_addr = config.contracts.identity_registry if w3 and pkey else ""
    rep_addr = config.contracts.reputation_registry if w3 and pkey else ""

    deal_record = DealRecordClient(w3, deal_addr, pkey)
    identity = IdentityClient(w3, ident_addr, pkey)
    reputation = ReputationClient(w3, rep_addr, pkey)

    any_mock = not (deal_addr and ident_addr and rep_addr and pkey and w3)
    return OnChainClients(
        deal_record=deal_record,
        identity=identity,
        reputation=reputation,
        any_mock=any_mock,
    )


# ---------------------------------------------------------------------------
# Exec → Pydantic result bridge
# ---------------------------------------------------------------------------


def _exec_to_core_result(
    exec_result: WireNegotiationResult,
    buyer_config: AgentConfig,
    seller_config: AgentConfig,
) -> CoreNegotiationResult:
    """Adapt the executor wire result into the Pydantic core result.

    The AttestationPipeline reads ``buyer_id``, ``seller_id``,
    ``agreed_price``, ``rounds``, ``transcript`` and ``deal_hash``.  The
    executor's ``rounds`` is a list of :class:`WireNegotiationRound` objects with
    ``buyer_offer`` / ``seller_offer`` fields — we flatten them into a
    Pydantic :class:`negotiatorgrid.core.types.NegotiationOffer` transcript keyed on ``agent_id``.
    """
    buyer_id = buyer_config.agent_id or buyer_config.address or "buyer"
    seller_id = seller_config.agent_id or seller_config.address or "seller"

    transcript: list[CoreOffer] = []
    for nr in exec_result.rounds:
        if nr.buyer_offer is not None:
            transcript.append(
                CoreOffer(
                    round_number=nr.round_number,
                    price=nr.buyer_offer.price,
                    scope=nr.buyer_offer.scope,
                    nl_message=nr.buyer_offer.nl_message,
                    timestamp=nr.buyer_offer.timestamp,
                    agent_id=buyer_id,
                )
            )
        if nr.seller_offer is not None:
            transcript.append(
                CoreOffer(
                    round_number=nr.round_number,
                    price=nr.seller_offer.price,
                    scope=nr.seller_offer.scope,
                    nl_message=nr.seller_offer.nl_message,
                    timestamp=nr.seller_offer.timestamp,
                    agent_id=seller_id,
                )
            )

    return CoreNegotiationResult(
        agreed_price=exec_result.agreed_price or None,
        rounds=exec_result.total_rounds,
        transcript=transcript,
        buyer_id=buyer_id,
        seller_id=seller_id,
        duration_ms=exec_result.duration_seconds * 1000.0,
        deal_hash=exec_result.deal_hash,
    )


# ---------------------------------------------------------------------------
# Address normalisation
# ---------------------------------------------------------------------------


def _normalise_address(addr: str) -> str:
    """Return a checksummed ETH address, or a deterministic fallback.

    The x402 payload requires a valid checksummed ``payTo`` address.
    Agent configs often default to the zero address, which would succeed
    but leaves a confusing on-chain trail, so we swap in a dead address
    sentinel instead.
    """
    if not addr or addr == "0x0000000000000000000000000000000000000000":
        return Web3.to_checksum_address(_FALLBACK_SELLER_ADDRESS)
    try:
        return Web3.to_checksum_address(addr)
    except Exception:
        return Web3.to_checksum_address(_FALLBACK_SELLER_ADDRESS)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def settle_and_attest(
    exec_result: WireNegotiationResult,
    buyer_config: AgentConfig,
    seller_config: AgentConfig,
    resource_uri: str = "",
) -> SettlementInfo:
    """Run the post-negotiation settle → attest pipeline.

    *exec_result* is the :class:`WireNegotiationResult` produced by the
    ``NegotiationExecutor`` (see ``executors/negotiation.py``).

    Broadcasts four WebSocket events along the way:
    ``settlement_started``, ``settlement_completed``,
    ``attestation_started``, ``attestation_completed``.

    Never raises; failures land in ``SettlementInfo.pipeline_error``.
    """
    start = time.time()
    info = SettlementInfo()

    if not exec_result.success or exec_result.agreed_price <= 0:
        info.pipeline_error = "negotiation_failed_or_zero_price"
        info.duration_seconds = time.time() - start
        return info

    # -----------------------------------------------------------------
    # 1. x402 settlement
    # -----------------------------------------------------------------
    seller_wallet = _normalise_address(seller_config.address)
    # agreed_price is in display USDT (float, e.g. 0.10); convert to 6-dec atomic
    atomic_amount = int(round(exec_result.agreed_price * 1_000_000))

    await broadcaster.broadcast_event(
        "settlement_started",
        {
            "negotiation_id": exec_result.negotiation_id,
            "agreed_price": exec_result.agreed_price,
            "atomic_amount": atomic_amount,
            "seller_wallet": seller_wallet,
        },
    )

    settler = X402Settler()
    try:
        payment_req = settler.create_payment_requirements(
            agreed_price=atomic_amount,
            seller_wallet=seller_wallet,
            resource_url=resource_uri,
            deal_hash=exec_result.deal_hash,
        )
        if seller_config.malicious_seller:
            payment_req = inflate_payment_requirements(payment_req)

        settler.verify_payment_requirements(
            agreed_price_atomic=atomic_amount,
            deal_hash=exec_result.deal_hash,
            seller_wallet=seller_wallet,
            resource_url=resource_uri,
            payment_requirements=payment_req,
        )
    except DealHashMismatchError as exc:
        # Act 5 — refuse to sign; penalise seller reputation; no on-chain
        # deal record (Solidity has no REJECTED status — we record off-chain).
        info.payment_refused = True
        info.rejection_reason = "price_manipulation"
        info.expected_atomic = exc.expected_atomic
        info.requested_atomic = exc.actual_atomic
        info.pipeline_error = "deal_hash_mismatch"
        info.duration_seconds = time.time() - start

        clients = build_clients()
        info.mock_mode = clients.any_mock

        agent_id = seller_config.seller_agent_id or 99
        fb_hash = Web3.keccak(text=exec_result.deal_hash or "no-hash")
        try:
            await clients.reputation.give_feedback(
                agent_id=agent_id,
                value=-1,
                tag1="price_manipulation",
                tag2=(exec_result.deal_hash or "")[:32],
                endpoint="",
                feedback_uri="",
                feedback_hash=fb_hash,
            )
        except Exception:
            logger.exception("Negative reputation feedback failed (non-blocking)")

        await broadcaster.broadcast_event(
            "settlement_completed",
            {
                "success": False,
                "tx_hash": "",
                "network": config.x402.network,
                "error": "deal_hash_mismatch",
            },
        )
        await broadcaster.broadcast_event(
            "payment_refused",
            {
                "negotiation_id": exec_result.negotiation_id,
                "deal_hash": exec_result.deal_hash,
                "message": (
                    "PAYMENT REFUSED — x402 payment terms do not match "
                    "the negotiated deal (hash mismatch)."
                ),
                "seller_agent_id": agent_id,
                "expected_atomic": info.expected_atomic,
                "requested_atomic": info.requested_atomic,
                "rejection_reason": info.rejection_reason,
            },
        )
        await broadcaster.broadcast_event(
            "attestation_completed",
            {
                "deal_hash": exec_result.deal_hash,
                "attestation_tx": "",
                "kitescan_url": "",
                "mock_mode": info.mock_mode,
                "duration_seconds": info.duration_seconds,
                "error": "rejected_price_manipulation",
                "status": "rejected",
                "rejection_reason": "price_manipulation",
            },
        )
        return info
    except Exception as exc:
        logger.exception("X402 settlement crashed")
        info.pipeline_error = f"x402_crash: {exc}"
        info.duration_seconds = time.time() - start
        await broadcaster.broadcast_event(
            "settlement_completed",
            {"success": False, "error": info.pipeline_error},
        )
        return info

    # Rebuild honest requirements for settlement (never sign inflated terms).
    payment_req = settler.create_payment_requirements(
        agreed_price=atomic_amount,
        seller_wallet=seller_wallet,
        resource_url=resource_uri,
        deal_hash=exec_result.deal_hash,
    )
    settlement = await settler.settle_payment(payment_req)

    info.x402_tx_hash = settlement.tx_hash or ""
    info.x402_network = settlement.network or config.x402.network
    info.settled = bool(settlement.success)

    await broadcaster.broadcast_event(
        "settlement_completed",
        {
            "success": info.settled,
            "tx_hash": info.x402_tx_hash,
            "network": info.x402_network,
            "error": "" if info.settled else (settlement.error_reason or "unknown"),
        },
    )

    if not info.settled:
        info.pipeline_error = f"x402_failed: {settlement.error_reason or 'unknown'}"
        # Still proceed to attestation with a zero tx hash so the deal is
        # recorded as unsettled — judges care about the attestation trail
        # even when the demo settler fails.

    # -----------------------------------------------------------------
    # 2. On-chain attestation
    # -----------------------------------------------------------------
    clients = build_clients()
    info.mock_mode = clients.any_mock

    await broadcaster.broadcast_event(
        "attestation_started",
        {
            "negotiation_id": exec_result.negotiation_id,
            "deal_hash": exec_result.deal_hash,
            "mock_mode": info.mock_mode,
        },
    )

    try:
        core_result = _exec_to_core_result(exec_result, buyer_config, seller_config)
        attestation = AttestationPipeline(
            deal_record=clients.deal_record,
            reputation=clients.reputation,
            identity=clients.identity,
        )
        attestation_hash = await attestation.attest_deal(
            core_result, info.x402_tx_hash
        )
        info.attestation_deal_hash = attestation_hash
        info.attestation_tx = (
            attestation_hash if attestation_hash.startswith("0x")
            else f"0x{attestation_hash}"
        )
    except Exception as exc:
        logger.exception("Attestation crashed")
        info.pipeline_error = (
            info.pipeline_error or ""
        ) + f" attestation_crash: {exc}"

    # -----------------------------------------------------------------
    # 3. Explorer URLs (only meaningful in non-mock mode)
    # -----------------------------------------------------------------
    if info.x402_tx_hash and not info.mock_mode:
        info.kitescan_tx_url = explorer_tx_url(info.x402_tx_hash)
    if info.attestation_tx and not info.mock_mode:
        info.kitescan_attestation_url = explorer_tx_url(info.attestation_tx)

    info.duration_seconds = time.time() - start

    await broadcaster.broadcast_event(
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

    return info
