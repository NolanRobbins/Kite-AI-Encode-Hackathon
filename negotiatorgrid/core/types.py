"""Shared data types for NegotiatorGrid."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Legacy dataclass types (kept for backward compatibility with existing code)
# ---------------------------------------------------------------------------


@dataclass
class SLATerms:
    """Service-level agreement terms embedded in a deal."""

    response_time_ms: int = 1000
    availability_bps: int = 9950  # 99.5%
    validity_period_secs: int = 3600


@dataclass
class DealAttestation:
    """On-chain attestation of a completed negotiation."""

    deal_hash: bytes = b""
    buyer: str = ""
    seller: str = ""
    buyer_agent_id: int = 0
    seller_agent_id: int = 0
    resource_uri: str = ""
    opening_buyer_price: int = 0
    opening_seller_price: int = 0
    final_price: int = 0
    negotiation_rounds: int = 0
    sla: SLATerms = field(default_factory=SLATerms)
    x402_tx_hash: bytes = b""
    timestamp: int = 0
    settled: bool = False


@dataclass
class PaymentRequirements:
    """x402 payment requirements returned in a 402 response."""

    scheme: str = "exact"
    network: str = "eip155:2368"
    max_amount_required: str = "0"
    resource: str = ""
    pay_to: str = ""
    asset: str = ""
    max_timeout_seconds: int = 300
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class SettlementResult:
    """Result of an x402 settlement attempt."""

    success: bool = False
    tx_hash: str = ""
    error_reason: str = ""
    payer: str = ""
    network: str = ""
    amount: str = ""


# ---------------------------------------------------------------------------
# Pydantic models for the negotiation engine
# ---------------------------------------------------------------------------


class NegotiationOffer(BaseModel):
    """A single offer in a negotiation round."""

    round_number: int
    price: float
    scope: str = ""
    nl_message: str = ""
    timestamp: float = 0.0
    agent_id: str = ""


class NegotiationResult(BaseModel):
    """Output of a completed negotiation session."""

    agreed_price: float | None = None
    rounds: int = 0
    transcript: list[NegotiationOffer] = Field(default_factory=list)
    buyer_id: str = ""
    seller_id: str = ""
    duration_ms: float = 0.0
    nash_check_passed: bool | None = None
    deal_hash: str = ""
    #: Unix second frozen at agreement; drives binding hash + on-chain timestamp.
    deal_bound_at: int = 0


# Executor / API wire shapes with the same *names* would collide with the
# models above; see ``WireNegotiationOffer``, ``WireNegotiationRound``, and
# ``WireNegotiationResult`` in ``negotiatorgrid.executors.negotiation``.


class NegotiationConfig(BaseModel):
    """Parameters controlling a negotiation session."""

    max_rounds: int = 7
    timeout_seconds: float = 30.0
    price_min: float = 0.0
    price_max: float = 100.0
    buyer_reservation: float = 60.0
    seller_reservation: float = 40.0


class AgentProfile(BaseModel):
    """Profile for an agent participating in negotiations."""

    agent_id: str = ""
    wallet_address: str = ""
    reputation_score: float = 0.5
    deal_count: int = 0
    avg_rounds: float = 0.0
    strategy_params: dict[str, Any] = Field(default_factory=dict)


class OpponentType(str, Enum):
    AGGRESSIVE = "aggressive"
    MODERATE = "moderate"
    GENEROUS = "generous"


class OpponentModel(BaseModel):
    """Estimated model of an opponent's behavior."""

    estimated_reservation_price: float = 0.0
    concession_rate: float = 0.0
    estimated_type: OpponentType = OpponentType.MODERATE
    confidence: float = 0.0


class NashGuardrailResult(BaseModel):
    """Result of Nash equilibrium guardrail check."""

    nash_price: float = 0.0
    deviation_pct: float = 0.0
    passed: bool = True
    strategy_profile: str = ""
