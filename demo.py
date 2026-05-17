#!/usr/bin/env python3
"""NegotiatorGrid — end-to-end demo on live Kite Testnet (Chain 2368).

Three acts:

* **Act 1 — Without NegotiatorGrid.** A naive buyer hits the Surprise
  API directly, gets a 402 with the list price, and pays it. One round
  trip. No negotiation. No attestation.
* **Act 2 — With NegotiatorGrid (happy path).** MCP-style discovery,
  ERC-8004 identity check, on-chain reputation lookup, 7-round NegMAS
  SAOP negotiation, **hash-mismatch rejection** of the stale 402,
  policy-driven re-sync, real x402 settlement against the Surprise
  API, and a real ``DealRecord`` write on Kite Testnet.
* **Act 3 — Reputation-conditioned strategy.** A second seller is
  registered on ``IdentityRegistry``, given a piece of negative
  feedback on ``ReputationRegistry``, and the same buyer re-runs the
  bargain. The Boulware → Conceder shift in the buyer's aspiration
  curve is what makes the second negotiation finish in fewer rounds
  at a worse-for-the-seller price.

Pre-flight:

* ``contracts/scripts/write_env_files.js`` must have produced the
  repo-root ``.env`` with deployed contract addresses + a funded
  ``PRIVATE_KEY``.
* The Surprise API must be running on ``http://localhost:8001``::

      uv pip install -r requirements.txt    # one-time
      .venv-demo\\Scripts\\python -m uvicorn surprise_api.app:app --port 8001

* On Windows, the demo sets ``PYTHONIOENCODING=utf-8`` for box-drawing
  characters; or just run with ``$env:PYTHONIOENCODING="utf-8"``.

Run::

    .venv-demo\\Scripts\\python demo.py
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Any

import httpx
from eth_account import Account
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

# Force utf-8 stdout on Windows so box-drawing characters render.
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

from negotiatorgrid.config import config
from negotiatorgrid.contracts.deal_record import DealRecordClient
from negotiatorgrid.contracts.identity import IdentityClient
from negotiatorgrid.contracts.reputation_client import ReputationClient
from negotiatorgrid.core.attestation import AttestationPipeline
from negotiatorgrid.core.deal_hash import (
    compute_binding_deal_hash_bytes_from_result,
    compute_binding_deal_hash_hex_from_result,
)
from negotiatorgrid.core.negotiation import NegotiationSession
from negotiatorgrid.core.nash_guardrail import NashGuardrail
from negotiatorgrid.core.opponent_model import OpponentModeler
from negotiatorgrid.core.reputation import ReputationFeed
from negotiatorgrid.core.settlement import DealHashMismatchError, X402Settler
from negotiatorgrid.core.types import NegotiationConfig
from negotiatorgrid.core.x402_eip712 import (
    DEFAULT_MAX_TIMEOUT_SECONDS,
    X402_JSON_VERSION,
    build_transfer_with_authorization_typed_data,
)

# ---------------------------------------------------------------------------
# Terminal styling
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

BAR = f"{DIM}{'─' * 72}{RESET}"
DBAR = f"{DIM}{'═' * 72}{RESET}"

SURPRISE_API_BASE = os.getenv("SURPRISE_API_URL", "http://localhost:8001")
NVDA_ROUTE = "/api/nvda"
NVDA_LIST_PRICE_ATOMIC = 30_000   # $0.030 advertised by surprise_api
USDT_DECIMALS = 1_000_000


def banner() -> None:
    print(f"""
{BOLD}{CYAN}
  ╔══════════════════════════════════════════════════════════════════════╗
  ║                                                                      ║
  ║   ███╗   ██╗███████╗ ██████╗  ██████╗ ████████╗██╗ █████╗ ████████╗ ║
  ║   ████╗  ██║██╔════╝██╔════╝ ██╔═══██╗╚══██╔══╝██║██╔══██╗╚══██╔══╝ ║
  ║   ██╔██╗ ██║█████╗  ██║  ███╗██║   ██║   ██║   ██║███████║   ██║    ║
  ║   ██║╚██╗██║██╔══╝  ██║   ██║██║   ██║   ██║   ██║██╔══██║   ██║    ║
  ║   ██║ ╚████║███████╗╚██████╔╝╚██████╔╝   ██║   ██║██║  ██║   ██║    ║
  ║   ╚═╝  ╚═══╝╚══════╝ ╚═════╝  ╚═════╝    ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ║
  ║                              ██████╗ ██████╗ ██╗██████╗             ║
  ║                             ██╔════╝ ██╔══██╗██║██╔══██╗            ║
  ║                             ██║  ███╗██████╔╝██║██║  ██║            ║
  ║                             ██║   ██║██╔══██╗██║██║  ██║            ║
  ║                             ╚██████╔╝██║  ██║██║██████╔╝            ║
  ║                              ╚═════╝ ╚═╝  ╚═╝╚═╝╚═════╝             ║
  ║                                                                      ║
  ║   Agent-to-Agent negotiation, settlement, and attestation            ║
  ║   on the Kite AI testnet  ·  x402  ·  ERC-8004  ·  Game theory       ║
  ╚══════════════════════════════════════════════════════════════════════╝{RESET}
""")


def section(title: str, icon: str = "▸") -> None:
    print(f"\n{DBAR}")
    print(f"  {BOLD}{icon} {title}{RESET}")
    print(DBAR)


def act_header(act: int, title: str) -> None:
    print(f"\n{BOLD}{BG_BLUE}{WHITE}  ACT {act}  —  {title}  {RESET}\n")


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


def kitescan_link(tx_hash: str) -> str:
    if not tx_hash:
        return "(no tx)"
    h = tx_hash if tx_hash.startswith("0x") else f"0x{tx_hash}"
    return f"{config.kite.explorer_url}tx/{h}"


def kitescan_addr_link(address: str) -> str:
    return f"{config.kite.explorer_url}address/{address}"


# ---------------------------------------------------------------------------
# Bootstrap: env, web3, contract clients, preflight
# ---------------------------------------------------------------------------


@dataclass
class DemoContext:
    """Everything the three acts share: clients, accounts, prices."""

    w3: Web3
    buyer_account: Any
    identity: IdentityClient
    reputation: ReputationClient
    deal_record: DealRecordClient
    settler: X402Settler
    surprise_seller_addr: str = ""
    surprise_agent_id: int = 0
    low_rep_seller_addr: str = ""
    low_rep_agent_id: int = 0
    txs: list[dict[str, Any]] = field(default_factory=list)

    def record_tx(self, kind: str, tx_hash: str, note: str = "") -> None:
        if tx_hash:
            self.txs.append({"kind": kind, "tx": tx_hash, "note": note})


def _require_env() -> None:
    missing = []
    if not config.kite.private_key:
        missing.append("PRIVATE_KEY")
    if not config.contracts.identity_registry:
        missing.append("IDENTITY_REGISTRY_ADDR")
    if not config.contracts.reputation_registry:
        missing.append("REPUTATION_REGISTRY_ADDR")
    if not config.contracts.deal_record:
        missing.append("DEALRECORD_CONTRACT_ADDR")
    if missing:
        fail(f"Missing env vars: {', '.join(missing)}")
        print(
            f"  Run {YELLOW}node contracts/scripts/write_env_files.js{RESET} after deploying."
        )
        sys.exit(1)


def _build_web3() -> Web3:
    w3 = Web3(Web3.HTTPProvider(config.kite.rpc_url, request_kwargs={"timeout": 30}))
    # Kite Testnet is a POA chain; the extraData middleware avoids decode errors.
    try:
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    except Exception:
        pass
    if not w3.is_connected():
        fail(f"Web3 not connected to {config.kite.rpc_url}")
        sys.exit(1)
    return w3


async def _check_surprise_api(client: httpx.AsyncClient) -> dict[str, Any]:
    try:
        r = await client.get(f"{SURPRISE_API_BASE}/healthz", timeout=3.0)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        fail(f"Surprise API not reachable at {SURPRISE_API_BASE}: {exc}")
        print(f"\n  Start it in a second terminal with:\n")
        print(f"    {YELLOW}.venv-demo\\Scripts\\python -m uvicorn surprise_api.app:app --port 8001{RESET}\n")
        sys.exit(1)


async def _fetch_agent_card(client: httpx.AsyncClient) -> dict[str, Any]:
    r = await client.get(f"{SURPRISE_API_BASE}/.well-known/agent.json", timeout=5.0)
    r.raise_for_status()
    return r.json()


async def _reset_surprise_pricing(client: httpx.AsyncClient) -> None:
    """Wipe any prior demo state from a previous run."""
    try:
        await client.post(f"{SURPRISE_API_BASE}/admin/reset", timeout=3.0)
    except Exception:
        pass


async def _sync_deal_to_surprise(
    client: httpx.AsyncClient,
    *,
    route: str,
    price_atomic: int,
    deal_hash_hex: str,
    expected_buyer: str,
) -> dict[str, Any]:
    r = await client.post(
        f"{SURPRISE_API_BASE}/admin/sync-deal",
        json={
            "route": route,
            "price_atomic": price_atomic,
            "deal_hash": deal_hash_hex,
            "expected_buyer": expected_buyer,
        },
        timeout=5.0,
    )
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# x402 helpers — speak the real HTTP 402 handshake to surprise_api
# ---------------------------------------------------------------------------


async def fetch_402_payment_requirements(
    client: httpx.AsyncClient, route: str
) -> dict[str, Any]:
    """GET the route without payment; expect a 402 body with PaymentRequirements."""
    r = await client.get(f"{SURPRISE_API_BASE}{route}", timeout=10.0)
    if r.status_code != 402:
        raise RuntimeError(
            f"Expected 402 from {route}, got {r.status_code}: {r.text[:200]}"
        )
    body = r.json()
    accepts = body.get("accepts") or []
    if not accepts:
        raise RuntimeError(f"402 body had no 'accepts' array: {body}")
    return accepts[0]


def _sign_x_payment_header(
    *,
    buyer: Any,
    payment_requirements: dict[str, Any],
) -> str:
    """Sign the EIP-712 ``TransferWithAuthorization`` and pack the X-Payment header."""
    import base64
    import json

    asset = payment_requirements.get("asset", config.kite.test_usdt_addr)
    pay_to = payment_requirements["payTo"]
    amount = payment_requirements["maxAmountRequired"]
    network = payment_requirements.get("network", config.x402.network)
    chain_id = int(network.split(":")[-1])

    nonce_hex = "0x" + Web3.keccak(text=f"{buyer.address}{time.time_ns()}").hex().lstrip("0x")
    nonce_hex = "0x" + nonce_hex[2:].rjust(64, "0")
    valid_before = int(time.time()) + payment_requirements.get(
        "maxTimeoutSeconds", DEFAULT_MAX_TIMEOUT_SECONDS
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


async def pay_surprise_api(
    client: httpx.AsyncClient,
    *,
    route: str,
    payment_requirements: dict[str, Any],
    buyer: Any,
) -> dict[str, Any]:
    header = _sign_x_payment_header(buyer=buyer, payment_requirements=payment_requirements)
    r = await client.get(
        f"{SURPRISE_API_BASE}{route}",
        headers={"X-Payment": header},
        timeout=15.0,
    )
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# ACT 1 — Without NegotiatorGrid (naive list-price payment)
# ---------------------------------------------------------------------------


async def act1_baseline(ctx: DemoContext, client: httpx.AsyncClient) -> dict[str, Any]:
    act_header(1, "WITHOUT NegotiatorGrid  ·  naive buyer pays list price")

    step("Buyer hits Surprise API directly, no negotiation, no policy.")
    pr = await fetch_402_payment_requirements(client, NVDA_ROUTE)
    list_price_atomic = int(pr["maxAmountRequired"])
    list_price_display = list_price_atomic / USDT_DECIMALS
    seller = pr["payTo"]

    info_box(
        "402 Payment Required",
        [
            f"Route:        {NVDA_ROUTE}",
            f"List price:   ${list_price_display:.4f} USDT",
            f"Pay to:       {seller}",
            f"Network:      {pr['network']}",
            f"Asset:        USDT.test ({pr['asset'][:18]}...)",
        ],
    )

    step("Signing X-Payment header and paying full list price...")
    data = await pay_surprise_api(client, route=NVDA_ROUTE, payment_requirements=pr, buyer=ctx.buyer_account)

    quote = data["data"]
    paid = data["paid_amount_atomic"] or 0
    tx = data.get("tx_hash") or ""
    ctx.record_tx("x402_baseline", tx, "Act 1 naive payment")

    ok("NVDA quote received (no negotiation discount).")
    info_box(
        "Quote (Act 1)",
        [
            f"Symbol:    {quote['symbol']}",
            f"Price USD: ${quote['price_usd']:.2f}  ({quote['change_pct']:+.2f}%)",
            f"Volume:    {quote['volume']:,}",
            f"Source:    {quote['source']}",
            f"Paid:      ${paid / USDT_DECIMALS:.4f} USDT  (= list price)",
        ],
    )
    print(f"  {DIM}No on-chain attestation. No deal hash. No reputation update.{RESET}")
    return {
        "price_atomic": list_price_atomic,
        "price_display": list_price_display,
        "seller": seller,
        "quote": quote,
    }


# ---------------------------------------------------------------------------
# ACT 2 — With NegotiatorGrid (happy path + hash-mismatch hero)
# ---------------------------------------------------------------------------


def _run_negotiation(
    *,
    buyer_id: str,
    seller_id: str,
    list_price_atomic: int,
    buyer_reservation_atomic: int,
    seller_reservation_atomic: int,
    buyer_exponent: float = 4.0,
    seller_exponent: float = 4.0,
    max_rounds: int = 7,
) -> Any:
    """Run a NegMAS bilateral SAOP and tag the result with real wallet IDs."""
    # We discretise pricing into a 200-step grid over [min, max] for NegMAS.
    price_min = float(min(buyer_reservation_atomic, seller_reservation_atomic) - 5_000)
    price_max = float(max(buyer_reservation_atomic, seller_reservation_atomic) + 5_000)
    price_min = max(price_min, 1.0)

    cfg = NegotiationConfig(
        max_rounds=max_rounds,
        timeout_seconds=30,
        price_min=price_min,
        price_max=price_max,
        buyer_reservation=float(buyer_reservation_atomic),
        seller_reservation=float(seller_reservation_atomic),
    )
    buyer_om = OpponentModeler(is_opponent_seller=True, price_min=price_min, price_max=price_max)
    seller_om = OpponentModeler(is_opponent_seller=False, price_min=price_min, price_max=price_max)
    session = NegotiationSession(
        config=cfg,
        buyer_opponent_modeler=buyer_om,
        seller_opponent_modeler=seller_om,
        buyer_exponent=buyer_exponent,
        seller_exponent=seller_exponent,
    )
    result = session.run()

    # Re-tag with real on-chain identifiers so deal_hash bytes match Solidity.
    result.buyer_id = buyer_id
    result.seller_id = seller_id
    return result


def _print_rounds(result: Any, buyer_label: str, seller_label: str) -> None:
    """Render a transcript as alternating buyer/seller rounds."""
    rounds: list[dict[str, Any]] = []
    cur: dict[str, Any] = {}
    rn = 0
    for offer in result.transcript:
        role = "buyer" if offer.agent_id == "buyer" else "seller"
        if role == "buyer":
            rn += 1
            cur = {"r": rn, "buyer": offer.price}
        else:
            cur["seller"] = offer.price
            rounds.append(cur)

    guard = NashGuardrail(deviation_threshold=0.20)
    bres = float(result.transcript[0].price) if result.transcript else 0.0
    for rd in rounds:
        bp = rd["buyer"] / USDT_DECIMALS
        sp = rd.get("seller", rd["buyer"]) / USDT_DECIMALS
        print(f"\n  {BG_BLUE}{WHITE}{BOLD} ROUND {rd['r']} {RESET}")
        print(f"  {BLUE}{buyer_label:<22}{RESET}  ${bp:.4f}")
        print(f"  {MAGENTA}{seller_label:<22}{RESET}  ${sp:.4f}")


async def act2_with_negotiatorgrid(
    ctx: DemoContext,
    client: httpx.AsyncClient,
    agent_card: dict[str, Any],
) -> dict[str, Any]:
    act_header(2, "WITH NegotiatorGrid  ·  discovery → negotiation → attestation")

    # -- Stage A: Discovery (real /.well-known + ERC-8004 identity check) --
    section("Stage A: Discovery (A2A + ERC-8004)", "🔍")

    step(f"GET {SURPRISE_API_BASE}/.well-known/agent.json (A2A protocol v0.2.9)")
    advertised_seller = agent_card["registrations"][0]["agentAddress"]
    advertised_id = int(agent_card["registrations"][0]["agentId"])

    info_box(
        "Discovered service (Surprise API)",
        [
            f"Name:               {agent_card['name']}",
            f"Description:        {agent_card['description'][:55]}",
            f"x402-capable:       {agent_card['capabilities'].get('x402', False)}",
            f"NVDA quote route:   {NVDA_ROUTE}",
            f"Advertised agent#:  {advertised_id}",
            f"Advertised wallet:  {advertised_seller}",
        ],
    )

    step("Registering advertised seller on IdentityRegistry (Kite Testnet)...")
    onchain_seller_id = await ctx.identity.register_agent(
        f"https://surprise.negotiatorgrid.dev/agents/{advertised_id}.json",
        metadata={"role": "seller", "service": "surprise-api"},
    )
    if onchain_seller_id <= 0:
        onchain_seller_id = advertised_id or 1
    ctx.surprise_agent_id = onchain_seller_id
    ctx.surprise_seller_addr = advertised_seller

    await ctx.identity.set_agent_wallet(onchain_seller_id, advertised_seller)
    ok(f"Seller bound on-chain: agentId={onchain_seller_id} → {advertised_seller}")

    onchain_wallet = ctx.identity.get_agent_wallet(onchain_seller_id)
    matches = onchain_wallet.lower() == advertised_seller.lower()
    if matches:
        ok(f"ERC-8004 wallet check passed (on-chain == advertised).")
    else:
        warn(f"ERC-8004 wallet mismatch: on-chain={onchain_wallet} advertised={advertised_seller}")

    # -- Stage B: Reputation lookup --
    section("Stage B: Reputation lookup (ReputationRegistry)", "⭐")
    feed = ReputationFeed(ctx.reputation, ctx.deal_record)
    profile = feed.get_agent_reputation(advertised_seller)
    rep_score = float(getattr(profile, "reputation_score", 0.85))
    strategy = ReputationFeed.map_reputation_to_strategy(rep_score)
    info_box(
        "Seller reputation",
        [
            f"Score:            {rep_score:.2f} / 1.0",
            f"Buyer strategy:   {strategy['label']}",
            f"Boulware/Conceder exponent (Act 2): {strategy.get('exponent', 4.0):.2f}",
        ],
    )

    # -- Stage C: Bilateral negotiation --
    section("Stage C: Bilateral negotiation (NegMAS SAOP)", "🤝")
    print(f"  {DIM}Buyer reservation: $0.0300 (would accept up to list price){RESET}")
    print(f"  {DIM}Seller reservation: $0.0220 (will not go below){RESET}")

    result = _run_negotiation(
        buyer_id=ctx.buyer_account.address,
        seller_id=advertised_seller,
        list_price_atomic=NVDA_LIST_PRICE_ATOMIC,
        buyer_reservation_atomic=30_000,
        seller_reservation_atomic=22_000,
        buyer_exponent=float(strategy.get("exponent", 4.0)),
        seller_exponent=4.0,
    )

    _print_rounds(result, "BUYER", "SELLER (Surprise)")
    if result.agreed_price is None:
        fail("Negotiation did not converge")
        sys.exit(1)
    agreed_atomic = int(result.agreed_price)
    agreed_display = agreed_atomic / USDT_DECIMALS
    savings_atomic = NVDA_LIST_PRICE_ATOMIC - agreed_atomic
    savings_display = savings_atomic / USDT_DECIMALS
    savings_pct = (savings_atomic / NVDA_LIST_PRICE_ATOMIC) * 100.0

    deal_hash_hex = compute_binding_deal_hash_hex_from_result(
        result, bound_at=result.deal_bound_at, resource_uri=NVDA_ROUTE
    )

    print(f"\n  {BG_GREEN}{BLACK}{BOLD}  DEAL  {RESET}  "
          f"Price: {GREEN}${agreed_display:.4f}{RESET}  "
          f"vs list ${NVDA_LIST_PRICE_ATOMIC / USDT_DECIMALS:.4f}  "
          f"({GREEN}−{savings_pct:.1f}%{RESET})")
    print(f"  {DIM}Off-chain binding hash:  {result.deal_hash[:34]}...{RESET}")
    print(f"  {DIM}On-chain canonical hash: {deal_hash_hex[:34]}...{RESET}")
    print(f"  {DIM}Bound at (unix sec):     {result.deal_bound_at}{RESET}")

    # -- Stage D: HERO #1 — hash-mismatch rejection --
    section("Stage D: Hash-mismatch rejection (autonomy hero shot)", "🛡️")
    print(f"  {DIM}Buyer agreed on ${agreed_display:.4f}. Seller still advertises list price.{RESET}")

    step("Buyer fetches a fresh 402 from the seller...")
    stale_pr = await fetch_402_payment_requirements(client, NVDA_ROUTE)
    stale_price_atomic = int(stale_pr["maxAmountRequired"])
    stale_display = stale_price_atomic / USDT_DECIMALS

    print(f"  {DIM}Seller's 402 maxAmountRequired:  {stale_display:.4f} USDT{RESET}")
    print(f"  {DIM}Negotiated price:                {agreed_display:.4f} USDT{RESET}")

    try:
        ctx.settler.verify_payment_requirements(
            agreed_price_atomic=agreed_atomic,
            deal_hash=deal_hash_hex,
            seller_wallet=advertised_seller,
            resource_url=NVDA_ROUTE,
            payment_requirements=stale_pr,
        )
        warn("Verification did not reject the stale 402 — check demo state.")
    except DealHashMismatchError as exc:
        print(f"\n  {BG_RED}{WHITE}{BOLD}  PAYMENT BLOCKED  {RESET}")
        print(f"  {RED}Field mismatched:{RESET}  {exc.field}")
        print(f"  {RED}Expected:{RESET}         {exc.expected}")
        print(f"  {RED}Actual:{RESET}           {exc.actual}")
        avoided = (int(exc.actual_atomic or 0) - agreed_atomic) / USDT_DECIMALS if exc.actual_atomic else 0.0
        if avoided > 0:
            print(f"  {GREEN}Overpayment avoided:{RESET} ${avoided:.4f} USDT  "
                  f"({GREEN}{avoided / agreed_display * 100:.1f}%{RESET})")

    # Demonstrate the second variant too: tamper extra.deal_hash and re-verify.
    print(f"\n  {DIM}Variant: same price, but seller mutates extra.deal_hash.{RESET}")
    tampered = dict(stale_pr)
    tampered["maxAmountRequired"] = str(agreed_atomic)  # honest price
    tampered["extra"] = {**tampered.get("extra", {}), "deal_hash": "0xdeadbeef"}
    try:
        ctx.settler.verify_payment_requirements(
            agreed_price_atomic=agreed_atomic,
            deal_hash=deal_hash_hex,
            seller_wallet=advertised_seller,
            resource_url=NVDA_ROUTE,
            payment_requirements=tampered,
        )
        warn("Tampered deal hash slipped through — check verify logic.")
    except DealHashMismatchError as exc:
        print(f"  {RED}✗ Tampered extra.deal_hash blocked{RESET} "
              f"({DIM}{exc.field}: {str(exc.expected)[:20]}... vs {str(exc.actual)[:20]}...{RESET})")

    # -- Stage E: Sync deal, re-fetch, pay for real --
    section("Stage E: Policy sync + real x402 settlement", "💰")
    step("NegotiatorGrid policy pushes negotiated terms to the seller...")
    await _sync_deal_to_surprise(
        client,
        route=NVDA_ROUTE,
        price_atomic=agreed_atomic,
        deal_hash_hex=deal_hash_hex,
        expected_buyer=ctx.buyer_account.address,
    )
    ok(f"Seller PricingStore updated: {NVDA_ROUTE} → ${agreed_display:.4f}")

    step("Buyer re-fetches the 402...")
    fresh_pr = await fetch_402_payment_requirements(client, NVDA_ROUTE)
    ctx.settler.verify_payment_requirements(
        agreed_price_atomic=agreed_atomic,
        deal_hash=deal_hash_hex,
        seller_wallet=advertised_seller,
        resource_url=NVDA_ROUTE,
        payment_requirements=fresh_pr,
    )
    ok("PaymentRequirements now match — buyer accepts.")

    step("Signing EIP-712 TransferWithAuthorization, sending X-Payment...")
    paid = await pay_surprise_api(client, route=NVDA_ROUTE, payment_requirements=fresh_pr, buyer=ctx.buyer_account)
    x402_tx = paid.get("tx_hash") or ""
    ctx.record_tx("x402_negotiated", x402_tx, "Act 2 negotiated payment")
    quote = paid["data"]

    info_box(
        "Quote (Act 2 — NegotiatorGrid path)",
        [
            f"Symbol:    {quote['symbol']}",
            f"Price USD: ${quote['price_usd']:.2f}  ({quote['change_pct']:+.2f}%)",
            f"Paid:      ${paid['paid_amount_atomic'] / USDT_DECIMALS:.4f} USDT",
            f"Saved:     ${savings_display:.4f}  ({savings_pct:.1f}%) vs list",
            f"x402 tx:   {(x402_tx or 'local-verify')[:46]}",
            f"Facilit?   {paid.get('facilitator_used')}",
        ],
    )

    # -- Stage F: On-chain attestation (real DealRecord write) --
    section("Stage F: On-chain attestation (DealRecord)", "📜")
    step("Writing DealRecord to Kite Testnet...")

    # Build the attestation explicitly so we keep the actual record_tx hash.
    from negotiatorgrid.core.types import DealAttestation, SLATerms

    bound_at = result.deal_bound_at or int(time.time())
    final_price_atomic = int((result.agreed_price or 0))
    opening_buyer = 0
    opening_seller = 0
    for offer in result.transcript:
        if offer.agent_id == "buyer" and opening_buyer == 0:
            opening_buyer = int(offer.price)
        elif offer.agent_id == "seller" and opening_seller == 0:
            opening_seller = int(offer.price)

    x402_bytes = (
        bytes.fromhex(x402_tx.removeprefix("0x"))
        if x402_tx and len(x402_tx) >= 64
        else b"\x00" * 32
    )
    attestation = DealAttestation(
        deal_hash=compute_binding_deal_hash_bytes_from_result(
            result, bound_at=bound_at, resource_uri=NVDA_ROUTE
        ),
        buyer=Web3.to_checksum_address(ctx.buyer_account.address),
        seller=Web3.to_checksum_address(advertised_seller),
        buyer_agent_id=0,
        seller_agent_id=ctx.surprise_agent_id,
        resource_uri=NVDA_ROUTE,
        opening_buyer_price=opening_buyer,
        opening_seller_price=opening_seller,
        final_price=final_price_atomic,
        negotiation_rounds=int(result.rounds or 0),
        sla=SLATerms(),
        x402_tx_hash=x402_bytes,
        timestamp=bound_at,
        settled=bool(x402_tx),
    )
    record_tx = await ctx.deal_record.record_deal(attestation)
    ctx.record_tx("dealrecord", record_tx, "Act 2 attestation")

    info_box(
        "Attestation",
        [
            f"Deal hash:    {deal_hash_hex[:48]}...",
            f"x402 tx:      {(x402_tx or '(local-verify)')[:48]}",
            f"DealRecord tx: {(record_tx or '(failed)')[:48]}",
            f"KiteScan:     {kitescan_link(record_tx)[:60]}",
        ],
    )

    return {
        "agreed_atomic": agreed_atomic,
        "agreed_display": agreed_display,
        "savings_display": savings_display,
        "savings_pct": savings_pct,
        "deal_hash_hex": deal_hash_hex,
        "x402_tx": x402_tx,
        "attest_tx": record_tx,
        "result": result,
    }


# ---------------------------------------------------------------------------
# ACT 3 — Reputation-conditioned strategy (second on-chain seller)
# ---------------------------------------------------------------------------


async def act3_reputation_conditioned(
    ctx: DemoContext, client: httpx.AsyncClient
) -> dict[str, Any]:
    act_header(3, "REPUTATION-CONDITIONED STRATEGY  ·  same buyer, low-rep seller")

    # Register a synthetic low-rep seller on-chain
    section("Stage A: Register second seller on Kite Testnet", "🆕")
    low_rep_addr = Web3.to_checksum_address("0x" + "ab" * 20)
    low_rep_id = await ctx.identity.register_agent(
        "https://negotiatorgrid.dev/agents/sketchy-quotes.json",
        metadata={"role": "seller", "service": "sketchy-quotes"},
    )
    if low_rep_id <= 0:
        low_rep_id = ctx.surprise_agent_id + 1
    ctx.low_rep_agent_id = low_rep_id
    ctx.low_rep_seller_addr = low_rep_addr

    await ctx.identity.set_agent_wallet(low_rep_id, low_rep_addr)
    ok(f"Registered low-rep seller: agentId={low_rep_id} → {low_rep_addr}")

    section("Stage B: Write negative feedback", "👎")
    feedback_tx = await ctx.reputation.give_feedback(
        agent_id=low_rep_id,
        value=-1,
        tag1="overpriced",
        tag2="missed_sla",
        endpoint=NVDA_ROUTE,
        feedback_uri="ipfs://demo/feedback/low-rep",
        feedback_hash=Web3.keccak(text=f"low-rep-feedback-{int(time.time())}"),
    )
    ctx.record_tx("reputation_feedback", feedback_tx, "Act 3 negative feedback")
    ok(f"Negative feedback submitted: tx={feedback_tx[:30]}...")
    print(f"  KiteScan: {kitescan_link(feedback_tx)}")

    section("Stage C: Reputation-conditioned negotiation", "🧠")
    feed = ReputationFeed(ctx.reputation, ctx.deal_record)
    profile = feed.get_agent_reputation(low_rep_addr)
    rep_score = float(getattr(profile, "reputation_score", 0.25))
    strategy = ReputationFeed.map_reputation_to_strategy(rep_score)

    info_box(
        "Buyer's adapted strategy",
        [
            f"Seller reputation:   {rep_score:.2f} / 1.0  (low)",
            f"Label:               {strategy['label']}",
            f"Exponent:            {strategy.get('exponent', 1.0):.2f}",
            f"Effect:              less patient, harder concession demands",
        ],
    )

    result_lo = _run_negotiation(
        buyer_id=ctx.buyer_account.address,
        seller_id=low_rep_addr,
        list_price_atomic=NVDA_LIST_PRICE_ATOMIC,
        buyer_reservation_atomic=30_000,
        seller_reservation_atomic=22_000,
        buyer_exponent=float(strategy.get("exponent", 1.0)),
        seller_exponent=4.0,
    )
    _print_rounds(result_lo, "BUYER (rep-cond.)", "SELLER (low-rep)")

    if result_lo.agreed_price is None:
        warn("Low-rep negotiation did not converge (buyer walked away).")
    else:
        lo_atomic = int(result_lo.agreed_price)
        print(f"\n  {BG_YELLOW}{BLACK}{BOLD}  DEAL (Act 3)  {RESET}  "
              f"Price: {YELLOW}${lo_atomic / USDT_DECIMALS:.4f}{RESET}")
    return {"result_lo": result_lo}


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def print_summary(
    ctx: DemoContext,
    a1: dict[str, Any],
    a2: dict[str, Any],
    a3: dict[str, Any] | None,
    elapsed: float,
) -> None:
    section("SUMMARY", "📊")

    list_disp = a1["price_display"]
    neg_disp = a2["agreed_display"]
    saved = a2["savings_display"]
    pct = a2["savings_pct"]

    print(f"""
  {BOLD}Per-call price comparison{RESET}
  {BAR}
  Without NegotiatorGrid (Act 1):  ${list_disp:.4f} USDT
  With NegotiatorGrid (Act 2):     ${neg_disp:.4f} USDT
  Per-call savings:                ${saved:.4f}  ({GREEN}{pct:.1f}%{RESET})

  {BOLD}On-chain artefacts{RESET}
  {BAR}""")

    for tx in ctx.txs:
        if not tx["tx"]:
            continue
        print(f"  • {tx['kind']:<22} {tx['tx'][:48]}...")
        print(f"    {DIM}{kitescan_link(tx['tx'])}{RESET}")

    print(f"""
  {BOLD}Deployed contracts (Kite Testnet, chain 2368){RESET}
  {BAR}
  IdentityRegistry    {config.contracts.identity_registry}
    {DIM}{kitescan_addr_link(config.contracts.identity_registry)}{RESET}
  ReputationRegistry  {config.contracts.reputation_registry}
    {DIM}{kitescan_addr_link(config.contracts.reputation_registry)}{RESET}
  DealRecord          {config.contracts.deal_record}
    {DIM}{kitescan_addr_link(config.contracts.deal_record)}{RESET}

  {BOLD}{GREEN}Demo complete in {elapsed:.1f}s.{RESET}
  {DIM}NegotiatorGrid v0.1 · Kite AI × Encode Club Hackathon · Novel track{RESET}
""")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def run_demo() -> None:
    banner()
    started = time.time()

    section("Preflight", "🔧")
    _require_env()
    w3 = _build_web3()
    chain_id = w3.eth.chain_id
    buyer_account = Account.from_key(config.kite.private_key)
    balance_wei = w3.eth.get_balance(buyer_account.address)
    info_box(
        "Buyer wallet (deployer)",
        [
            f"Address:   {buyer_account.address}",
            f"Chain ID:  {chain_id}  ({DIM}Kite Testnet{RESET})",
            f"Balance:   {w3.from_wei(balance_wei, 'ether')} KITE",
            f"RPC:       {config.kite.rpc_url}",
        ],
    )
    pk = config.kite.private_key
    identity = IdentityClient(w3, config.contracts.identity_registry, pk)
    reputation = ReputationClient(w3, config.contracts.reputation_registry, pk)
    deal_record = DealRecordClient(w3, config.contracts.deal_record, pk)
    settler = X402Settler(private_key=pk)
    ctx = DemoContext(
        w3=w3, buyer_account=buyer_account,
        identity=identity, reputation=reputation, deal_record=deal_record,
        settler=settler,
    )

    async with httpx.AsyncClient() as client:
        health = await _check_surprise_api(client)
        ok(f"Surprise API healthy: network={health.get('network')}")
        await _reset_surprise_pricing(client)

        agent_card = await _fetch_agent_card(client)

        a1 = await act1_baseline(ctx, client)
        a2 = await act2_with_negotiatorgrid(ctx, client, agent_card)
        a3 = None
        try:
            a3 = await act3_reputation_conditioned(ctx, client)
        except Exception as exc:
            warn(f"Act 3 partial failure (non-blocking): {exc}")

        elapsed = time.time() - started
        print_summary(ctx, a1, a2, a3, elapsed)


def main() -> None:
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Demo interrupted.{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
