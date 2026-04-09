#!/usr/bin/env python3
"""
NegotiatorGrid — Golden Path Demo Script
==========================================

Demonstrates the full pipeline:
  1. Agent registration (mock ERC-8004 identities)
  2. Reputation lookup
  3. 5-round bilateral negotiation with NL dialogue
  4. x402 settlement (mock)
  5. On-chain attestation (mock)
  6. Summary stats

Run:  python demo.py
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import sys
import time
from dataclasses import dataclass, field
from typing import Any

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


def warn(msg: str) -> None:
    print(f"  {YELLOW}⚠{RESET} {msg}")


def fail(msg: str) -> None:
    print(f"  {RED}✗{RESET} {msg}")


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
# Mock agent identities (stand-in for ERC-8004)
# ---------------------------------------------------------------------------

@dataclass
class MockAgent:
    agent_id: str
    name: str
    address: str
    role: str
    reputation_score: float
    total_deals: int
    tags: list[str] = field(default_factory=list)


BUYER_AGENT = MockAgent(
    agent_id="agent-001",
    name="DataBuyer-Alpha",
    address="0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18",
    role="buyer",
    reputation_score=4.8,
    total_deals=47,
    tags=["weather-data", "premium-api", "bulk-consumer"],
)

SELLER_AGENT = MockAgent(
    agent_id="agent-002",
    name="WeatherPro-Service",
    address="0x209693Bc6412A8b3D23E1bF6E1d59EbFf95bC2cE",
    role="seller",
    reputation_score=4.5,
    total_deals=123,
    tags=["weather-api", "geolocation", "high-uptime"],
)


# ---------------------------------------------------------------------------
# Negotiation engine (inline — no external deps required)
# ---------------------------------------------------------------------------

def aspiration_offer(initial: float, reservation: float, t: float, exponent: float = 2.0) -> float:
    return initial + (reservation - initial) * (t ** exponent)


def generate_nl(role: str, price: float, rnd: int, total: int) -> str:
    t = rnd / max(total, 1)
    if role == "buyer":
        if t < 0.3:
            return f"I'd like to start at ${price:.4f}/call. Given current market rates and my volume needs, this seems fair."
        elif t < 0.7:
            return f"I can move to ${price:.4f}. I value reliability — let's find a price that works for both of us."
        else:
            return f"My best offer: ${price:.4f}. I'm near my budget ceiling but genuinely want to close this deal."
    else:
        if t < 0.3:
            return f"My service at ${price:.4f}/call includes sub-150ms latency, 99.9% uptime, and 200 RPS throughput."
        elif t < 0.7:
            return f"I can come down to ${price:.4f}. This covers infrastructure costs while maintaining SLA guarantees."
        else:
            return f"${price:.4f} is where I need to be. I've completed {SELLER_AGENT.total_deals} deals at this quality."


def opponent_model(offers: list[float]) -> dict[str, Any]:
    if len(offers) < 2:
        return {"estimated_reservation": None, "confidence": 0.0}
    deltas = [offers[i] - offers[i - 1] for i in range(1, len(offers))]
    avg_d = sum(deltas) / len(deltas)
    est = offers[-1] + avg_d * max(3, len(offers)) if abs(avg_d) > 1e-9 else offers[-1]
    conf = min(0.9, 0.3 + 0.15 * len(offers))
    return {"estimated_reservation": round(est, 6), "confidence": round(conf, 2)}


def nash_check(bp: float, sp: float, b_res: float, s_res: float) -> str:
    zopa_lo, zopa_hi = min(b_res, s_res), max(b_res, s_res)
    mid = (bp + sp) / 2
    if zopa_lo <= mid <= zopa_hi or abs(bp - sp) < 0.02:
        return "PASS"
    return "WARN"


def deal_hash(neg_id: str, price: float, rounds: int) -> str:
    payload = json.dumps({"negotiation_id": neg_id, "agreed_price": price, "rounds": rounds}, sort_keys=True)
    return "0x" + hashlib.sha256(payload.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Settlement mock (x402)
# ---------------------------------------------------------------------------

def mock_x402_settle(buyer: MockAgent, seller: MockAgent, price: float) -> dict[str, Any]:
    tx_hash = "0x" + hashlib.sha256(f"x402-{buyer.address}-{seller.address}-{price}-{time.time()}".encode()).hexdigest()
    return {
        "success": True,
        "tx_hash": tx_hash,
        "network": "eip155:2368",
        "payer": buyer.address,
        "payee": seller.address,
        "amount_usdt": price,
    }


# ---------------------------------------------------------------------------
# Attestation mock (DealRecord contract)
# ---------------------------------------------------------------------------

def mock_attestation(d_hash: str, buyer: MockAgent, seller: MockAgent, price: float, rounds: int, x402_tx: str) -> dict[str, Any]:
    tx_hash = "0x" + hashlib.sha256(f"attest-{d_hash}-{time.time()}".encode()).hexdigest()
    return {
        "tx_hash": tx_hash,
        "deal_hash": d_hash,
        "buyer_agent_id": buyer.agent_id,
        "seller_agent_id": seller.agent_id,
        "agreed_price": price,
        "negotiation_rounds": rounds,
        "x402_tx_hash": x402_tx,
        "kitescan_url": f"https://testnet.kitescan.ai/tx/{tx_hash}",
    }


# ---------------------------------------------------------------------------
# Main demo
# ---------------------------------------------------------------------------

async def run_demo() -> None:
    banner()
    total_start = time.time()

    # ── Stage 1: Agent Registration ────────────────────────────────────────
    section("STAGE 1: Agent Registration (ERC-8004 Identity)", "🔐")
    step("Registering buyer agent...")
    await asyncio.sleep(0.3)
    info_box(f"Buyer: {BUYER_AGENT.name}", [
        f"Agent ID:    {BUYER_AGENT.agent_id}",
        f"Address:     {BUYER_AGENT.address}",
        f"Role:        {BUYER_AGENT.role}",
        f"Tags:        {', '.join(BUYER_AGENT.tags)}",
    ])
    ok(f"Buyer registered: {BUYER_AGENT.name}")

    await asyncio.sleep(0.2)
    step("Registering seller agent...")
    await asyncio.sleep(0.3)
    info_box(f"Seller: {SELLER_AGENT.name}", [
        f"Agent ID:    {SELLER_AGENT.agent_id}",
        f"Address:     {SELLER_AGENT.address}",
        f"Role:        {SELLER_AGENT.role}",
        f"Tags:        {', '.join(SELLER_AGENT.tags)}",
    ])
    ok(f"Seller registered: {SELLER_AGENT.name}")

    # ── Stage 2: Reputation Lookup ─────────────────────────────────────────
    section("STAGE 2: Reputation Lookup", "⭐")
    await asyncio.sleep(0.2)

    for agent in [BUYER_AGENT, SELLER_AGENT]:
        stars = "★" * int(agent.reputation_score) + "☆" * (5 - int(agent.reputation_score))
        print(f"  {CYAN}{agent.name}{RESET}  {YELLOW}{stars}{RESET}  "
              f"({agent.reputation_score}/5.0)  "
              f"{DIM}{agent.total_deals} completed deals{RESET}")

    ok("Reputation data loaded from on-chain registry")
    step(f"Buyer reputation {YELLOW}{BUYER_AGENT.reputation_score}/5.0{RESET} → strategy: moderate concession")
    step(f"Seller reputation {YELLOW}{SELLER_AGENT.reputation_score}/5.0{RESET} → strategy: aspiration-based")

    # ── Stage 3: Bilateral Negotiation ─────────────────────────────────────
    section("STAGE 3: Bilateral Negotiation (5-Round SAOP)", "🤝")

    neg_id = "neg-demo-001"
    max_rounds = 5
    buyer_initial = 0.06
    buyer_reservation = 0.12
    seller_initial = 0.14
    seller_reservation = 0.08

    buyer_exp = 1.5  # aspiration
    seller_exp = 2.0  # boulware

    buyer_offers: list[float] = []
    seller_offers: list[float] = []
    agreed_price = 0.0
    agreed = False

    for r in range(1, max_rounds + 1):
        t = r / max_rounds
        bp = round(aspiration_offer(buyer_initial, buyer_reservation, t, buyer_exp), 4)
        sp = round(aspiration_offer(seller_initial, seller_reservation, t, seller_exp), 4)
        buyer_offers.append(bp)
        seller_offers.append(sp)

        bnl = generate_nl("buyer", bp, r, max_rounds)
        snl = generate_nl("seller", sp, r, max_rounds)
        opp = opponent_model(seller_offers)
        nc = nash_check(bp, sp, buyer_reservation, seller_reservation)

        print(f"\n  {BOLD}{BG_BLUE}{WHITE} ROUND {r}/{max_rounds} {RESET}")
        print(BAR)

        # Buyer offer
        print(f"  {BLUE}BUYER  →{RESET}  ${bp:.4f}  {DIM}{BUYER_AGENT.name}{RESET}")
        print(f"         {DIM}\"{bnl}\"{RESET}")

        # Seller offer
        print(f"  {MAGENTA}SELLER →{RESET}  ${sp:.4f}  {DIM}{SELLER_AGENT.name}{RESET}")
        print(f"         {DIM}\"{snl}\"{RESET}")

        # Analytics
        opp_str = f"est. reservation: ${opp['estimated_reservation']:.4f}" if opp["estimated_reservation"] else "insufficient data"
        nc_color = GREEN if nc == "PASS" else YELLOW
        print(f"  {DIM}Opponent model:{RESET} {opp_str} (conf: {opp['confidence']:.0%})")
        print(f"  {DIM}Nash check:{RESET}     {nc_color}{nc}{RESET}")

        await asyncio.sleep(0.5)

        if bp >= sp:
            agreed_price = round((bp + sp) / 2, 4)
            agreed = True
            print(f"\n  {BG_GREEN}{BLACK}{BOLD} ✓ DEAL AGREED {RESET}  "
                  f"Price: {GREEN}${agreed_price:.4f}{RESET}  "
                  f"Round: {r}/{max_rounds}")
            break

    if not agreed:
        agreed_price = round((buyer_offers[-1] + seller_offers[-1]) / 2, 4)
        agreed = True
        print(f"\n  {BG_YELLOW}{BOLD} ≈ CONVERGED {RESET}  "
              f"Split price: {GREEN}${agreed_price:.4f}{RESET}")

    total_rounds = len(buyer_offers)
    d_hash = deal_hash(neg_id, agreed_price, total_rounds)

    # Utilities
    b_util = round(1.0 - (agreed_price - buyer_initial) / (buyer_reservation - buyer_initial), 3)
    s_util = round(1.0 - (seller_initial - agreed_price) / (seller_initial - seller_reservation), 3)
    b_util = max(0, min(1, b_util))
    s_util = max(0, min(1, s_util))

    print(f"\n  {DIM}Deal hash:      {RESET}{d_hash[:20]}...")
    print(f"  {DIM}Buyer utility:  {RESET}{b_util:.3f}")
    print(f"  {DIM}Seller utility: {RESET}{s_util:.3f}")

    # ── Stage 4: x402 Settlement ───────────────────────────────────────────
    section("STAGE 4: x402 Payment Settlement", "💰")
    step("Constructing PaymentRequirements from negotiated price...")
    await asyncio.sleep(0.3)

    print(f"  {DIM}scheme:     exact{RESET}")
    print(f"  {DIM}network:    eip155:2368 (Kite Testnet){RESET}")
    print(f"  {DIM}amount:     ${agreed_price:.4f} USDT{RESET}")
    print(f"  {DIM}payTo:      {SELLER_AGENT.address[:20]}...{RESET}")
    print(f"  {DIM}facilitator: 0x12343e649e6b2b...3C78b{RESET}")

    step("Signing payment payload...")
    await asyncio.sleep(0.4)
    step("Submitting to Kite facilitator...")
    await asyncio.sleep(0.5)

    settlement = mock_x402_settle(BUYER_AGENT, SELLER_AGENT, agreed_price)

    if settlement["success"]:
        ok(f"Settlement confirmed!")
        print(f"  {DIM}Tx hash:  {RESET}{settlement['tx_hash'][:30]}...")
        print(f"  {DIM}Network:  {RESET}{settlement['network']}")
        print(f"  {DIM}Amount:   {RESET}${settlement['amount_usdt']:.4f} USDT")
    else:
        fail("Settlement failed!")

    # ── Stage 5: On-Chain Attestation ──────────────────────────────────────
    section("STAGE 5: On-Chain Attestation (DealRecord)", "📜")
    step("Recording deal on Kite blockchain...")
    await asyncio.sleep(0.5)

    attestation = mock_attestation(d_hash, BUYER_AGENT, SELLER_AGENT, agreed_price, total_rounds, settlement["tx_hash"])

    ok("DealRecord written to chain!")
    info_box("Attestation Details", [
        f"Deal hash:        {attestation['deal_hash'][:30]}...",
        f"Buyer agent:      {attestation['buyer_agent_id']}",
        f"Seller agent:     {attestation['seller_agent_id']}",
        f"Agreed price:     ${attestation['agreed_price']:.4f} USDT",
        f"Rounds:           {attestation['negotiation_rounds']}",
        f"x402 tx:          {attestation['x402_tx_hash'][:30]}...",
        f"KiteScan:         {attestation['kitescan_url'][:50]}...",
    ])

    # ── Stage 6: Summary ───────────────────────────────────────────────────
    total_duration = time.time() - total_start
    section("SUMMARY", "📊")

    print(f"""
  {BOLD}Negotiation Results{RESET}
  {BAR}
  Negotiation ID:       {neg_id}
  Total rounds:         {total_rounds}
  Agreed price:         {GREEN}${agreed_price:.4f} USDT{RESET}
  Buyer utility:        {b_util:.3f}
  Seller utility:       {s_util:.3f}
  Global welfare:       {round((b_util + s_util) / 2, 3):.3f}

  {BOLD}Settlement{RESET}
  {BAR}
  x402 tx:              {settlement['tx_hash'][:40]}...
  Attestation tx:       {attestation['tx_hash'][:40]}...
  Network:              Kite Testnet (Chain ID 2368)

  {BOLD}Performance{RESET}
  {BAR}
  Total duration:       {total_duration:.2f}s
  Avg round time:       {total_duration / total_rounds:.2f}s

  {BOLD}Price Convergence{RESET}
  {BAR}""")

    # ASCII price chart
    chart_width = 50
    all_prices = buyer_offers + seller_offers
    p_min = min(all_prices) * 0.95
    p_max = max(all_prices) * 1.05
    p_range = p_max - p_min if p_max > p_min else 0.01

    for r in range(total_rounds):
        bp = buyer_offers[r]
        sp = seller_offers[r]
        bp_pos = int((bp - p_min) / p_range * chart_width)
        sp_pos = int((sp - p_min) / p_range * chart_width)

        line = [" "] * (chart_width + 1)
        line[bp_pos] = f"{BLUE}●{RESET}"
        line[sp_pos] = f"{MAGENTA}●{RESET}"
        bar_str = "".join(line)
        print(f"  R{r + 1}  ${bp:.4f} {BLUE}B{RESET} {'─' * max(0, sp_pos - bp_pos - 1)} {MAGENTA}S{RESET} ${sp:.4f}  {DIM}|{bar_str}|{RESET}")

    if agreed:
        ap_pos = int((agreed_price - p_min) / p_range * chart_width)
        line = [" "] * (chart_width + 1)
        line[ap_pos] = f"{GREEN}◆{RESET}"
        bar_str = "".join(line)
        print(f"  {GREEN}DEAL{RESET} ${agreed_price:.4f}            {DIM}|{bar_str}|{RESET}")

    print(f"""
  {DIM}Legend: {BLUE}● Buyer{RESET}  {MAGENTA}● Seller{RESET}  {GREEN}◆ Agreed{RESET}{DIM}
         Price axis: ${p_min:.4f} ← → ${p_max:.4f}{RESET}
""")

    print(f"  {BOLD}{GREEN}Demo complete!{RESET} Full pipeline executed in {total_duration:.2f}s")
    print(f"  {DIM}NegotiatorGrid v0.1.0 — Kite AI × Encode Club Hackathon{RESET}")
    print()


# Support missing ANSI code (BLACK not defined above)
BLACK = "\033[30m"


def main() -> None:
    """Entry point for the demo script."""
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Demo interrupted.{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
