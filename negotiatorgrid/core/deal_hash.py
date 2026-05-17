"""Deal hash helpers — bind the off-chain negotiation to the on-chain attestation.

Two flavours are provided. They serve different layers and intentionally do
**not** need to be byte-equal:

* **Off-chain "binding" hash** (:func:`compute_binding_deal_hash_bytes`,
  :func:`binding_deal_hash_hex`) — a short fingerprint over
  ``(buyer_id, seller_id, agreed_price, bound_at)``. Computed inside
  :mod:`negotiatorgrid.core.negotiation` the moment the SAO mechanism
  agrees, then echoed back in the x402 ``extra.deal_hash`` field. Its
  job is to let the buyer reject any mutated 402 response — see
  :class:`negotiatorgrid.core.settlement.DealHashMismatchError`.

* **On-chain "canonical" hash**
  (:func:`compute_onchain_deal_hash_bytes`,
  :func:`compute_binding_deal_hash_bytes_from_result`) — a
  byte-for-byte reproduction of what the Solidity
  ``DealRecord.recordDeal`` function computes::

      keccak256(abi.encodePacked(buyer, seller, finalPrice, resourceUri,
                                  timestamp, negotiationRounds))

  Used by :class:`negotiatorgrid.core.attestation.AttestationPipeline`
  so the buyer can independently verify the ``dealHash`` emitted in the
  ``DealRecorded`` event.

Both functions are total: opaque agent ids (``"buyer"``/``"seller-low-rep"``)
collapse to ``address(0)`` in the on-chain variant so the call never
raises mid-attestation.
"""

from __future__ import annotations

from web3 import Web3

from negotiatorgrid.core.types import NegotiationResult

ZERO_ADDRESS: str = "0x" + "00" * 20


# ---------------------------------------------------------------------------
# Off-chain binding fingerprint (used by negotiation.py / x402 layer)
# ---------------------------------------------------------------------------


def compute_binding_deal_hash_bytes(
    buyer_id: str,
    seller_id: str,
    agreed_price: float,
    bound_at: int,
) -> bytes:
    """Short, deterministic fingerprint for x402 ``extra.deal_hash``.

    Computed as ``keccak256(utf8(f"{buyer_id}:{seller_id}:{price}:{bound_at}"))``.
    Cheap, no abi encoding, no chain dependency — perfect for embedding
    inside the 402 response and for the buyer's pre-payment check.
    """
    raw = f"{buyer_id}:{seller_id}:{float(agreed_price):.8f}:{int(bound_at)}"
    return Web3.keccak(text=raw)


def binding_deal_hash_hex(digest: bytes) -> str:
    """Format a binding hash as a ``"0x..."`` hex string."""
    return "0x" + digest.hex()


# ---------------------------------------------------------------------------
# On-chain canonical hash (matches DealRecord.recordDeal exactly)
# ---------------------------------------------------------------------------


def _coerce_address(agent_id: str | None) -> str:
    """Best-effort cast of an opaque agent id to an EIP-55 address."""
    if not agent_id:
        return ZERO_ADDRESS
    if agent_id.startswith("0x") and len(agent_id) == 42:
        try:
            return Web3.to_checksum_address(agent_id)
        except ValueError:
            return ZERO_ADDRESS
    return ZERO_ADDRESS


def compute_onchain_deal_hash_bytes(
    *,
    buyer_address: str,
    seller_address: str,
    final_price_atomic: int,
    resource_uri: str,
    bound_at: int,
    negotiation_rounds: int,
) -> bytes:
    """Reproduce ``DealRecord.recordDeal``'s ``keccak256(abi.encodePacked(...))``.

    ``final_price_atomic`` is in 6-decimal USDT atomic units (the same
    integer the contract stores). Argument order, types, and packing
    match the Solidity contract verbatim.
    """
    return Web3.solidity_keccak(
        ["address", "address", "uint256", "string", "uint64", "uint8"],
        [
            _coerce_address(buyer_address),
            _coerce_address(seller_address),
            int(final_price_atomic),
            resource_uri or "",
            int(bound_at),
            int(negotiation_rounds) & 0xFF,
        ],
    )


def compute_binding_deal_hash_bytes_from_result(
    result: NegotiationResult,
    *,
    bound_at: int,
    resource_uri: str = "",
) -> bytes:
    """Solidity-compatible hash derived from a :class:`NegotiationResult`.

    This is the function :class:`AttestationPipeline` calls right before
    writing to the DealRecord contract. Off-chain Python and on-chain
    Solidity therefore agree on the canonical ``dealHash`` byte-for-byte
    when buyer/seller ids are real addresses.
    """
    final_price_atomic = int((result.agreed_price or 0) * 1_000_000)
    return compute_onchain_deal_hash_bytes(
        buyer_address=result.buyer_id,
        seller_address=result.seller_id,
        final_price_atomic=final_price_atomic,
        resource_uri=resource_uri,
        bound_at=bound_at,
        negotiation_rounds=int(result.rounds or 0),
    )


def compute_binding_deal_hash_hex_from_result(
    result: NegotiationResult,
    *,
    bound_at: int,
    resource_uri: str = "",
) -> str:
    """Hex-string variant of :func:`compute_binding_deal_hash_bytes_from_result`."""
    return binding_deal_hash_hex(
        compute_binding_deal_hash_bytes_from_result(
            result, bound_at=bound_at, resource_uri=resource_uri
        )
    )


__all__ = [
    "ZERO_ADDRESS",
    "binding_deal_hash_hex",
    "compute_binding_deal_hash_bytes",
    "compute_binding_deal_hash_bytes_from_result",
    "compute_binding_deal_hash_hex_from_result",
    "compute_onchain_deal_hash_bytes",
]
