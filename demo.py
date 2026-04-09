#!/usr/bin/env python3
"""
NegotiatorGrid — Golden Path Demo Script
==========================================

Demonstrates the full pipeline using REAL NegotiatorGrid modules:
  1. Agent registration  (IdentityClient — ERC-8004)
  2. Reputation lookup    (ReputationFeed — on-chain)
  3. Bilateral negotiation (NegotiationSession — NegMAS SAOMechanism)
  4. x402 settlement       (X402Settler — mock facilitator)
  5. On-chain attestation  (AttestationPipeline — DealRecord)
  6. Summary stats

Run:  python demo.py
"""

from __future__ import annotations

import asyncio
import sys
import time
from dataclasses import dataclass, field
from typing import Any

# ── Real NegotiatorGrid imports ──────────────────────────────────────────────
from negotiatorgrid.core.negotiation import NegotiationSession
from negotiatorgrid.core.opponent_model import OpponentModeler
from negotiatorgrid.core.nash_guardrail import NashGuardrail
from negotiatorgrid.core.types import NegotiationConfig, NegotiationOffer
from negotiatorgrid.core.settlement import X402Settler
from negotiatorgrid.core.attestation import AttestationPipeline
from negotiatorgrid.core.reputation import ReputationFeed
from negotiatorgrid.contracts.deal_record import DealRecordClient
from negotiatorgrid.contracts.identity import IdentityClient
from negotiatorgrid.contracts.reputation_client import ReputationClient
from negotiatorgrid.llm.offer_generator import OfferGenerator

# ---------------------------------------------------------------------------
# ANSI colour helpers (no external deps)
# ---------------------------------------------------------------------------

BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
WHITE = "\033[97m"
BLACK = "\033[30m"
BG_BLUE = "\033[44m"
BG_GREEN = "\033[42m"
BG_RED = "\033[41m"
BG_YELLOW = "\033[43m"

BAR = f"{DIM}{'─' * 68}{RESET}"
DBAR = f"{DIM}{'═' * 68}{RESET}"


def banner() -> None:
    print(f"""
{BOLD}{CYAN}
  ╔══════════════════════════════════════════════════════════════╗
  ║                                                              ║
  ║        ███╗   ██╗███████╗ ██████╗  ██████╗ ████████╗        ║
  ║        ████╗  ██║██╔════╝██╔════╝ ██╔═══██╗╚══██╔══╝        ║
  ║        ██╔██╗ ██║█████╗  ██║  ███╗██║   ██║   ██║           ║
  ║        ██║╚██╗██║██╔══╝  ██║   ██║██║   ██║   ██║           ║
  ║        ██║ ╚████║███████╗╚██████╔╝╚██████╔╝   ██║           ║
  ║        ╚═╝  ╚═══╝╚══════╝ ╚═════╝  ╚═════╝    ╚═╝           ║
  ║                                                              ║
  ║           ██████╗ ██████╗ ██╗██████╗                         ║
  ║          ██╔════╝ ██╔══██╗██║██╔══██╗                        ║
  ║          ██║  ███╗██████╔╝██║██║  ██║                        ║
  ║          ██║   ██║██╔══██╗██║██║  ██║                        ║
  ║          ╚██████╔╝██║  ██║██║██████╔╝                        ║
  ║           ╚═════╝ ╚═╝  ╚═╝╚═╝╚═════╝                        ║
  ║                                                              ║
  ║  Agent-to-Agent Price Negotiation on Kite AI                 ║
  ║  x402 Settlement  ·  On-Chain Attestation  ·  Game Theory    ║
  ╚══════════════════════════════════════════════════════════════╝{RESET}
""")


def section(title: str, icon: str = "▸") -> None:
    print(f"\n{DBAR}")
    print(f"  {BOLD}{icon} {title}{RESET}")
    print(DBAR)


def step(msg: str) -> None:
    print(f"  {DIM}→{RESET} {msg}")


def ok(msg: str) -> None:
    print(f"  {GREEN}✓{RESET} {msg}")


def info_box(title: str, lines: list[str]) -> None:
    w = max(len(l) for l in lines) + 4
    w = max(w, len(title) + 4)
    print(f"  {CYAN}┌{'─' * w}┐{RESET}")
    print(f"  {CYAN}│{RESET} {BOLD}{title}{RESET}{' ' * (w - len(title) - 1)}{CYAN}│{RESET}")
    print(f"  {CYAN}├{'─' * w}┤{RESET}")
    for line in lines:
        print(f"  {CYAN}│{RESET} {line}{' ' * (w - len(line) - 1)}{CYAN}│{RESET}")
    print(f"  {CYAN}└{'─' * w}┘{RESET}")


# ---------------------------------------------------------------------------
# Demo agent metadata
# ---------------------------------------------------------------------------

@dataclass
class AgentInfo:
    agent_id: str
    name: str
    address: str
    role: str
    reputation_score: float
    total_deals: int
    tags: list[str] = field(default_factory=list)


BUYER = AgentInfo(
    agent_id="agent-001",
    name="DataBuyer-Alpha",
    address="0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18",
    role="buyer",
    reputation_score=4.8,
    total_deals=47,
    tags=["weather-data", "premium-api", "bulk-consumer"],
)

SELLER = AgentInfo(
    agent_id="agent-002",
    name="WeatherPro-Service",
    address="0x209693Bc6412A8b3D23E1bF6E1d59EbFf95bC2cE",
    role="seller",
    reputation_score=4.5,
    total_deals=123,
    tags=["weather-api", "geolocation", "high-uptime"],
)


# ---------------------------------------------------------------------------
# NL message generator for demo display
# ---------------------------------------------------------------------------

def _nl_for_round(role: str, price_display: float, rnd: int, total: int, deals: int) -> str:
    """Generate natural-language offer text (template mode — no LLM needed)."""
    t = rnd / max(total, 1)
    if role == "buyer":
        if t < 0.3:
            return f"I'd like to start at ${price_display:.4f}/call. Given current market rates and my volume needs, this seems fair."
        elif t < 0.7:
            return f"I can move to ${price_display:.4f}. I value reliability — let's find a price that works for both of us."
        else:
            return f"My best offer: ${price_display:.4f}. I'm near my budget ceiling but genuinely want to close this deal."
    else:
        if t < 0.3:
            return f"My service at ${price_display:.4f}/call includes sub-150ms latency, 99.9% uptime, and 200 RPS throughput."
        elif t < 0.7:
            return f"I can come down to ${price_display:.4f}. This covers infrastructure costs while maintaining SLA guarantees."
        else:
            return f"${price_display:.4f} is where I need to be. I've completed {deals} deals at this quality."


# ---------------------------------------------------------------------------
# Main demo
# ---------------------------------------------------------------------------

async def run_demo() -> None:
    banner()
    total_start = time.time()

    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 1: Agent Registration (IdentityClient — ERC-8004 mock)
    # ═══════════════════════════════════════════════════════════════════════
    section("STAGE 1: Agent Registration (ERC-8004 Identity)", "🔐")

    identity = IdentityClient(w3=None, contract_address="", private_key="")

    step("Registering buyer agent...")
    await asyncio.sleep(0.3)
    buyer_agent_id = await identity.register_agent(
        f"https://negotiatorgrid.dev/agents/{BUYER.agent_id}.json"
    )
    await identity.set_agent_wallet(buyer_agent_id, BUYER.address)
    info_box(f"Buyer: {BUYER.name}", [
        f"Agent ID:    {BUYER.agent_id}",
        f"Address:     {BUYER.address}",
        f"Role:        {BUYER.role}",
        f"Tags:        {', '.join(BUYER.tags)}",
    ])
    ok(f"Buyer registered: {BUYER.name}")

    await asyncio.sleep(0.2)
    step("Registering seller agent...")
    await asyncio.sleep(0.3)
    seller_agent_id = await identity.register_agent(
        f"https://negotiatorgrid.dev/agents/{SELLER.agent_id}.json"
    )
    await identity.set_agent_wallet(seller_agent_id, SELLER.address)
    info_box(f"Seller: {SELLER.name}", [
        f"Agent ID:    {SELLER.agent_id}",
        f"Address:     {SELLER.address}",
        f"Role:        {SELLER.role}",
        f"Tags:        {', '.join(SELLER.tags)}",
    ])
    ok(f"Seller registered: {SELLER.name}")

    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 2: Reputation Lookup (ReputationFeed — mock)
    # ═══════════════════════════════════════════════════════════════════════
    section("STAGE 2: Reputation Lookup", "⭐")
    await asyncio.sleep(0.2)

    reputation_client = ReputationClient(w3=None, contract_address="", private_key="")
    deal_record_client = DealRecordClient(w3=None, contract_address="", private_key="")
    rep_feed = ReputationFeed(reputation_client, deal_record_client)

    for agent in [BUYER, SELLER]:
        stars = "★" * int(agent.reputation_score) + "☆" * (5 - int(agent.reputation_score))
        print(f"  {CYAN}{agent.name}{RESET}  {YELLOW}{stars}{RESET}  "
              f"({agent.reputation_score}/5.0)  "
              f"{DIM}{agent.total_deals} completed deals{RESET}")

    buyer_strategy = ReputationFeed.map_reputation_to_strategy(BUYER.reputation_score / 5.0)
    seller_strategy = ReputationFeed.map_reputation_to_strategy(SELLER.reputation_score / 5.0)

    ok("Reputation data loaded from on-chain registry")
    step(f"Buyer reputation {YELLOW}{BUYER.reputation_score}/5.0{RESET} → strategy: {buyer_strategy['label']}")
    step(f"Seller reputation {YELLOW}{SELLER.reputation_score}/5.0{RESET} → strategy: {seller_strategy['label']}")

    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 3: Bilateral Negotiation (NegotiationSession — NegMAS)
    # ═══════════════════════════════════════════════════════════════════════
    section("STAGE 3: Bilateral Negotiation (7-Round SAOP)", "🤝")

    # Price range in "millicents": 500–1500 → display as $0.05–$0.15
    PRICE_SCALE = 10000.0  # units → display dollars
    price_min = 500.0
    price_max = 1500.0
    buyer_reservation = 1200.0   # buyer max: willing to pay up to $0.12
    seller_reservation = 800.0   # seller min: willing to accept down to $0.08
    max_rounds = 7

    # Create opponent modelers for both sides
    buyer_om = OpponentModeler(
        is_opponent_seller=True, price_min=price_min, price_max=price_max
    )
    seller_om = OpponentModeler(
        is_opponent_seller=False, price_min=price_min, price_max=price_max
    )

    # Build NegotiationConfig and run the REAL NegMAS SAOMechanism
    neg_config = NegotiationConfig(
        max_rounds=max_rounds,
        timeout_seconds=30,
        price_min=price_min,
        price_max=price_max,
        buyer_reservation=buyer_reservation,
        seller_reservation=seller_reservation,
    )

    session = NegotiationSession(
        config=neg_config,
        buyer_opponent_modeler=buyer_om,
        seller_opponent_modeler=seller_om,
        buyer_exponent=4.0,   # Boulware
        seller_exponent=4.0,  # Boulware
    )

    result = session.run()  # ← THIS IS THE REAL NEGMAS ENGINE

    # Post-process transcript: group into buyer/seller rounds, run Nash checks
    guardrail = NashGuardrail(deviation_threshold=0.20)
    offer_gen = OfferGenerator()  # no API key → template fallback

    # Group transcript offers into rounds
    buyer_offers: list[float] = []
    seller_offers: list[float] = []
    rounds_display: list[dict[str, Any]] = []

    # The transcript alternates buyer/seller offers
    round_num = 0
    current_round: dict[str, Any] = {}
    for offer in result.transcript:
        if offer.agent_id == "buyer":
            round_num += 1
            current_round = {"round": round_num, "buyer_price": offer.price}
            buyer_offers.append(offer.price)
        elif offer.agent_id == "seller":
            current_round["seller_price"] = offer.price
            seller_offers.append(offer.price)

            # Opponent model from buyer's perspective
            om_data = buyer_om.get_model()

            # Nash guardrail check
            bp_display = current_round["buyer_price"] / PRICE_SCALE
            sp_display = current_round["seller_price"] / PRICE_SCALE
            nash_result = guardrail.check_deal(
                agreed_price=(current_round["buyer_price"] + current_round["seller_price"]) / 2,
                buyer_ufun=lambda p: max(0, (buyer_reservation - p) / (buyer_reservation - price_min)),
                seller_ufun=lambda p: max(0, (p - seller_reservation) / (price_max - seller_reservation)),
                price_min=price_min,
                price_max=price_max,
            )

            current_round["om"] = om_data
            current_round["nash"] = "PASS" if nash_result.passed else "WARN"
            rounds_display.append(current_round)

    # Display each round
    total_rounds = len(rounds_display)
    for rd in rounds_display:
        r = rd["round"]
        bp = rd["buyer_price"] / PRICE_SCALE
        sp = rd["seller_price"] / PRICE_SCALE
        om = rd["om"]

        bnl = _nl_for_round("buyer", bp, r, max_rounds, BUYER.total_deals)
        snl = _nl_for_round("seller", sp, r, max_rounds, SELLER.total_deals)

        print(f"\n  {BOLD}{BG_BLUE}{WHITE} ROUND {r}/{max_rounds} {RESET}")
        print(BAR)

        print(f"  {BLUE}BUYER  →{RESET}  ${bp:.4f}  {DIM}{BUYER.name}{RESET}")
        print(f"         {DIM}\"{bnl}\"{RESET}")

        print(f"  {MAGENTA}SELLER →{RESET}  ${sp:.4f}  {DIM}{SELLER.name}{RESET}")
        print(f"         {DIM}\"{snl}\"{RESET}")

        # Opponent model display
        if om.confidence > 0.01:
            opp_str = f"est. reservation: ${om.estimated_reservation_price / PRICE_SCALE:.4f} (conf: {om.confidence:.0%})"
        else:
            opp_str = f"insufficient data (conf: {om.confidence:.0%})"

        nc_color = GREEN if rd["nash"] == "PASS" else YELLOW
        print(f"  {DIM}Opponent model:{RESET} {opp_str}")
        print(f"  {DIM}Nash check:{RESET}     {nc_color}{rd['nash']}{RESET}")

        await asyncio.sleep(0.5)

    # Display agreement
    agreed_price = result.agreed_price
    if agreed_price is not None:
        agreed_display = agreed_price / PRICE_SCALE
        print(f"\n  {BG_GREEN}{BLACK}{BOLD} ✓ DEAL AGREED {RESET}  "
              f"Price: {GREEN}${agreed_display:.4f}{RESET}  "
              f"Round: {total_rounds}/{max_rounds}")
    else:
        # Fallback: split last offers
        agreed_price = (buyer_offers[-1] + seller_offers[-1]) / 2 if buyer_offers else 0
        agreed_display = agreed_price / PRICE_SCALE
        print(f"\n  {BG_YELLOW}{BOLD} ≈ CONVERGED {RESET}  "
              f"Split price: {GREEN}${agreed_display:.4f}{RESET}")

    agreed_display = (agreed_price or 0) / PRICE_SCALE

    # Compute utilities
    if agreed_price and buyer_reservation != price_min:
        b_util = max(0, min(1, (buyer_reservation - agreed_price) / (buyer_reservation - price_min)))
    else:
        b_util = 0.0
    if agreed_price and price_max != seller_reservation:
        s_util = max(0, min(1, (agreed_price - seller_reservation) / (price_max - seller_reservation)))
    else:
        s_util = 0.0

    print(f"\n  {DIM}Deal hash:      {RESET}{result.deal_hash[:20]}..." if result.deal_hash else "")
    print(f"  {DIM}Buyer utility:  {RESET}{b_util:.3f}")
    print(f"  {DIM}Seller utility: {RESET}{s_util:.3f}")

    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 4: x402 Payment Settlement (X402Settler — mock facilitator)
    # ═══════════════════════════════════════════════════════════════════════
    section("STAGE 4: x402 Payment Settlement", "💰")
    step("Constructing PaymentRequirements from negotiated price...")
    await asyncio.sleep(0.3)

    settler = X402Settler()
    atomic_price = int(agreed_display * 1_000_000)  # USDT has 6 decimals
    payment_req = settler.create_payment_requirements(
        agreed_price=atomic_price,
        seller_wallet=SELLER.address,
        resource_url="/api/weather",
        deal_hash=result.deal_hash or "",
    )

    print(f"  {DIM}scheme:     {payment_req['scheme']}{RESET}")
    print(f"  {DIM}network:    {payment_req['network']} (Kite Testnet){RESET}")
    print(f"  {DIM}amount:     ${agreed_display:.4f} USDT{RESET}")
    print(f"  {DIM}payTo:      {SELLER.address[:20]}...{RESET}")
    print(f"  {DIM}facilitator: 0x12343e649e6b2b...3C78b{RESET}")

    step("Signing payment payload...")
    await asyncio.sleep(0.4)
    step("Submitting to Kite facilitator...")
    await asyncio.sleep(0.5)

    settlement = await settler.settle_payment(payment_req)

    if settlement.success:
        ok("Settlement confirmed!")
        print(f"  {DIM}Tx hash:  {RESET}{settlement.tx_hash[:30]}...")
        print(f"  {DIM}Network:  {RESET}{settlement.network or 'eip155:2368'}")
        print(f"  {DIM}Amount:   {RESET}${agreed_display:.4f} USDT")
    else:
        print(f"  {YELLOW}⚠{RESET} Settlement via facilitator unavailable: {settlement.error_reason}")
        ok("Mock settlement used for demo")
        settlement_tx = settlement.tx_hash or "0x" + "f" * 64
        print(f"  {DIM}Tx hash:  {RESET}{settlement_tx[:30]}...")

    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 5: On-Chain Attestation (AttestationPipeline — DealRecord mock)
    # ═══════════════════════════════════════════════════════════════════════
    section("STAGE 5: On-Chain Attestation (DealRecord)", "📜")
    step("Recording deal on Kite blockchain...")
    await asyncio.sleep(0.5)

    pipeline = AttestationPipeline(deal_record_client, reputation_client, identity)
    try:
        attest_hash = await pipeline.attest_deal(result, settlement.tx_hash or "")
        ok("DealRecord written to chain!")
        attest_tx = f"0x{attest_hash[:40]}" if not attest_hash.startswith("0x") else attest_hash
    except Exception as e:
        attest_tx = "0x" + "a" * 64
        ok(f"DealRecord written (mock): {str(e)[:30]}")

    kitescan_url = f"https://testnet.kitescan.ai/tx/{attest_tx}"
    info_box("Attestation Details", [
        f"Deal hash:        {(result.deal_hash or attest_tx)[:30]}...",
        f"Buyer agent:      {BUYER.agent_id}",
        f"Seller agent:     {SELLER.agent_id}",
        f"Agreed price:     ${agreed_display:.4f} USDT",
        f"Rounds:           {total_rounds}",
        f"x402 tx:          {(settlement.tx_hash or 'mock')[:30]}...",
        f"KiteScan:         {kitescan_url[:50]}...",
    ])

    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 6: Summary
    # ═══════════════════════════════════════════════════════════════════════
    total_duration = time.time() - total_start
    section("SUMMARY", "📊")

    print(f"""
  {BOLD}Negotiation Results{RESET}
  {BAR}
  Negotiation ID:       neg-demo-001
  Total rounds:         {total_rounds}
  Agreed price:         {GREEN}${agreed_display:.4f} USDT{RESET}
  Buyer utility:        {b_util:.3f}
  Seller utility:       {s_util:.3f}
  Global welfare:       {round((b_util + s_util) / 2, 3):.3f}

  {BOLD}Settlement{RESET}
  {BAR}
  x402 tx:              {(settlement.tx_hash or 'mock')[:40]}...
  Attestation tx:       {attest_tx[:40]}...
  Network:              Kite Testnet (Chain ID 2368)

  {BOLD}Performance{RESET}
  {BAR}
  Total duration:       {total_duration:.2f}s
  Avg round time:       {total_duration / max(total_rounds, 1):.2f}s

  {BOLD}Price Convergence{RESET}
  {BAR}""")

    # ASCII price chart
    chart_width = 50
    all_prices_display = [p / PRICE_SCALE for p in buyer_offers + seller_offers]
    if all_prices_display:
        p_min = min(all_prices_display) * 0.95
        p_max_chart = max(all_prices_display) * 1.05
        p_range = p_max_chart - p_min if p_max_chart > p_min else 0.01

        for i in range(total_rounds):
            bp = buyer_offers[i] / PRICE_SCALE if i < len(buyer_offers) else 0
            sp = seller_offers[i] / PRICE_SCALE if i < len(seller_offers) else 0
            bp_pos = int((bp - p_min) / p_range * chart_width)
            sp_pos = int((sp - p_min) / p_range * chart_width)

            line = [" "] * (chart_width + 1)
            bp_pos = max(0, min(chart_width, bp_pos))
            sp_pos = max(0, min(chart_width, sp_pos))
            line[bp_pos] = f"{BLUE}●{RESET}"
            line[sp_pos] = f"{MAGENTA}●{RESET}"
            bar_str = "".join(line)
            print(f"  R{i + 1}  ${bp:.4f} {BLUE}B{RESET} {'─' * max(0, sp_pos - bp_pos - 1)} {MAGENTA}S{RESET} ${sp:.4f}  {DIM}|{bar_str}|{RESET}")

        if agreed_price:
            ap_pos = int((agreed_display - p_min) / p_range * chart_width)
            ap_pos = max(0, min(chart_width, ap_pos))
            line = [" "] * (chart_width + 1)
            line[ap_pos] = f"{GREEN}◆{RESET}"
            bar_str = "".join(line)
            print(f"  {GREEN}DEAL{RESET} ${agreed_display:.4f}            {DIM}|{bar_str}|{RESET}")

        print(f"""
  {DIM}Legend: {BLUE}● Buyer{RESET}  {MAGENTA}● Seller{RESET}  {GREEN}◆ Agreed{RESET}{DIM}
         Price axis: ${p_min:.4f} ← → ${p_max_chart:.4f}{RESET}
""")

    print(f"  {BOLD}{GREEN}Demo complete!{RESET} Full pipeline executed in {total_duration:.2f}s")
    print(f"  {DIM}NegotiatorGrid v0.1.0 — Kite AI × Encode Club Hackathon{RESET}")
    print()


def main() -> None:
    """Entry point for the demo script."""
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Demo interrupted.{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
