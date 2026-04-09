# NegotiatorGrid — Full Technical Architecture

## Elevator Pitch
A protocol layer where AI agents autonomously negotiate price, SLA terms, and payment schedules with each other **before** executing x402 transactions — turning one-shot micropayments into multi-round, game-theoretic bargaining.

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      KITE BLOCKCHAIN (L1)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐ │
│  │ AA Wallet    │  │ Attestation  │  │ ERC-8004 Agent    │ │
│  │ Constraints  │  │ Registry     │  │ Identity Registry │ │
│  └──────────────┘  └──────────────┘  └───────────────────┘ │
└─────────────────────────────────────────────────────────────┘
        ▲                   ▲                    ▲
        │                   │                    │
┌───────┴───────────────────┴────────────────────┴────────────┐
│                   NEGOTIATORGRID PROTOCOL LAYER              │
│                                                              │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐ │
│  │ Negotiation  │  │ Deal Contract │  │ x402 Settlement  │ │
│  │ Engine       │  │ (Agreed Terms)│  │ Executor         │ │
│  │ (ANEX/FIPA)  │  │               │  │                  │ │
│  └──────┬───────┘  └───────┬───────┘  └────────┬─────────┘ │
│         │                  │                    │           │
│         ▼                  ▼                    ▼           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           A2A Message Bus (Google A2A Protocol)      │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
        ▲                                         ▲
        │                                         │
   ┌────┴─────┐                              ┌────┴─────┐
   │ BUYER    │                              │ SELLER   │
   │ AGENT    │                              │ AGENT    │
   │ (Client) │                              │ (Server) │
   └──────────┘                              └──────────┘
```

---

## 2. How Each Kite Primitive Maps to a System Component

### Primitive 1: ERC-8004 Agent Identity → Agent Discovery & Trust

**What it does in the system:**
Every agent that participates in NegotiatorGrid registers an on-chain identity via Kite's ERC-8004 registry. This identity is the agent's "passport" — it proves who the agent is, what it can do, and who authorized it.

**Concrete fields used:**

```
AgentDID {
  did: "did:kite:alice.eth/gpt/gpu-provider-v1",  // Unique agent identity
  user_wallet: "0x891h42Kk9634...",                // Owner's wallet
  verification_methods: [{
    type: "EcdsaSecp256k1VerificationKey2019",
    public_key_hex: "0x04a1b2c3..."
  }],
  provider: "ChatGPT",                             // Agent platform
  created: 1712620800,
  updated: 1712620800
}
```

**AgentCard (published for discovery):**

```json
{
  "agent_did": "did:kite:alice.eth/gpt/gpu-provider-v1",
  "capabilities": ["gpu_inference", "streaming", "negotiation_v1"],
  "pricing_hint": { "min_usd": "0.001", "max_usd": "0.50", "unit": "per_request" },
  "security_schemes": ["session_key", "did_auth"],
  "endpoints": {
    "negotiate": "wss://agent.example.com/negotiate",
    "x402_service": "https://agent.example.com/api/inference"
  },
  "reputation_score": 0.94,
  "total_deals_completed": 1247
}
```

**Why it's required:** Without ERC-8004, agents have no way to verify each other's identity before entering a negotiation. A buyer agent needs to confirm the seller is a real, registered entity — not a spoofed endpoint — before sending any payment signature. The DID resolution chain (session → agent → user) is verified cryptographically, no central authority needed.

---

### Primitive 2: AA Wallets with Programmable Constraints → Negotiation Guardrails

**What it does in the system:**
The buyer agent's AA Wallet enforces the negotiated deal as a cryptographic constraint. Once agents agree on a price, the buyer's wallet is programmed to **reject** any x402 `PAYMENT-REQUIRED` response that demands more than the agreed amount. The seller's wallet rejects payments below the agreed floor.

**Concrete implementation:**

```solidity
// Buyer-side: Session key locked to negotiated terms
addSessionKeyRule(
  sessionKeyAddress: 0xBuyerSessionKey,
  agentId: keccak256("did:kite:bob.eth/claude/buyer-v1"),
  functionSelector: bytes4(keccak256("pay()")),
  valueLimit: 0.05e6  // $0.05 USDC — the negotiated price
);
```

**Constraint flow during NegotiatorGrid lifecycle:**

| Phase | Wallet State | Constraint |
|-------|-------------|------------|
| Pre-negotiation | Session key created | `valueLimit = user's max budget (e.g., $1.00)` |
| During negotiation | Agent exchanges offers | No spending allowed — wallet locked to negotiation-only mode |
| Post-agreement | Session key updated | `valueLimit = agreed price (e.g., $0.05)` |
| Execution (x402) | Payment signed | Wallet rejects any 402 response > $0.05 |
| Post-execution | Session key expired | Auto-revoke after `validUntil` timestamp |

**Progressive trust integration:**

```
Standing Intent (SI) = sign_user({
  iss: user_address,
  sub: "did:kite:bob.eth/claude/buyer-v1",
  caps: {
    max_tx: 0.50,          // No single deal > $0.50
    max_daily: 10.00,      // Total daily spend cap
    allowed_services: ["gpu_inference", "data_access"]
  },
  exp: timestamp + 86400   // 24h expiry
})
```

**Why it's required:** Without programmable constraints, a negotiation agreement is just a handshake — either agent can defect. AA Wallets make the deal **cryptographically binding**: the buyer literally cannot overpay, and the seller cannot underprice, because the wallets enforce the agreed terms at the protocol level.

---

### Primitive 3: x402 Protocol → Post-Negotiation Settlement

**What it does in the system:**
x402 is the execution layer **after** negotiation concludes. Today, x402 is "take it or leave it" — the server posts a fixed price, the client pays or walks away. NegotiatorGrid adds a pre-402 negotiation phase. Once agents agree, the negotiated price is locked into the 402 response header.

**The modified x402 flow (12 steps → 15 steps):**

```
STANDARD x402 (steps 1-2):
  1. Client → GET /api/inference
  2. Server → 402 + PAYMENT-REQUIRED header (price: $0.10)
     Client must pay $0.10 or leave. No negotiation.

NEGOTIATORGRID x402 (steps 1-15):
  1.  Client discovers Seller via AgentCard (ERC-8004)
  2.  Client → NEGOTIATE_REQUEST via A2A message bus
  3.  Seller → COUNTER_OFFER (price: $0.08, latency SLA: 200ms)
  4.  Client → COUNTER_OFFER (price: $0.04, latency SLA: 500ms)
  5.  Seller → COUNTER_OFFER (price: $0.06, latency SLA: 300ms)
  6.  Client → ACCEPT_PROPOSAL (price: $0.06, latency: 300ms)
  7.  Both agents sign DealContract → attested on-chain
  8.  Client updates AA Wallet constraint: valueLimit = $0.06
  9.  Client → GET /api/inference
  10. Server → 402 + PAYMENT-REQUIRED header (price: $0.06 — matches deal)
  11. Client wallet verifies: $0.06 ≤ valueLimit ✓
  12. Client signs EIP-3009 payment → X-PAYMENT header
  13. Server → POST /verify to Facilitator
  14. Facilitator → settles on Kite, returns Settlement Response
  15. Server → 200 OK + inference result + PAYMENT-RESPONSE header
```

**Key x402 headers used:**

| Header | Direction | Content |
|--------|-----------|---------|
| `PAYMENT-REQUIRED` | Server → Client | Base64 `PaymentRequirements` (price, token, recipient, network, **deal_hash**) |
| `PAYMENT-SIGNATURE` | Client → Server | Base64 `PaymentPayload` (signed EIP-3009 authorization) |
| `PAYMENT-RESPONSE` | Server → Client | Base64 `Settlement Response` (on-chain tx hash) |

**Critical addition:** The `PaymentRequirements` object includes a `deal_hash` field — the keccak256 hash of the negotiated DealContract. The client wallet verifies this hash matches the on-chain attestation before signing. If the seller changes the price after negotiation, the hash won't match and the wallet refuses to sign.

---

### Primitive 4: On-Chain Attestation → Auditable Negotiation History

**What it does in the system:**
Every completed negotiation and its outcome are recorded as immutable attestations on Kite. This creates a public, tamper-proof record that judges (and future agents) can inspect.

**Attestation data schema (what judges see on-chain):**

```json
{
  "attestation_type": "NegotiatorGrid_DealRecord_v1",
  "deal_id": "0xabc123...",
  "timestamp": 1712620800,

  "participants": {
    "buyer": {
      "agent_did": "did:kite:bob.eth/claude/buyer-v1",
      "wallet": "0xBuyerWallet..."
    },
    "seller": {
      "agent_did": "did:kite:alice.eth/gpt/gpu-provider-v1",
      "wallet": "0xSellerWallet..."
    }
  },

  "negotiation_summary": {
    "rounds": 3,
    "opening_ask": "0.10 USDC",
    "opening_bid": "0.03 USDC",
    "final_price": "0.06 USDC",
    "price_convergence_rate": 0.78,
    "negotiation_duration_ms": 4200,
    "sla_terms": {
      "max_latency_ms": 300,
      "min_uptime_pct": 99.5
    }
  },

  "transcript_hash": "0xdef456...",

  "execution": {
    "x402_tx_hash": "0x789ghi...",
    "amount_settled": "0.06 USDC",
    "settlement_chain": "kite-mainnet",
    "service_delivered": true,
    "sla_met": true,
    "actual_latency_ms": 187
  },

  "reputation_update": {
    "buyer_new_score": 0.91,
    "seller_new_score": 0.95,
    "deal_rating": "fair"
  },

  "signatures": {
    "buyer_si": "0x...",
    "seller_si": "0x...",
    "deal_contract_hash": "0x..."
  }
}
```

**What judges can verify from this:**
1. **The negotiation was real** — round count, price convergence, and duration prove multi-round bargaining occurred (not a hardcoded demo)
2. **The price was dynamically discovered** — opening ask ≠ final price, with measurable convergence
3. **The deal was enforced** — `deal_contract_hash` matches the on-chain constraint in the buyer's AA Wallet
4. **The service was delivered** — `x402_tx_hash` links to the actual settlement, and `sla_met` is verified by oracle attestation
5. **Reputation is earned** — scores update based on cryptographic proofs of behavior, not self-reporting

---

## 3. What the AI Agent Does Autonomously (Decision Loop)

### Buyer Agent Autonomous Behavior

```
┌─────────────────────────────────────────────────┐
│              BUYER AGENT DECISION LOOP           │
│                                                  │
│  1. DISCOVER: Query ERC-8004 registry for        │
│     agents with matching capabilities            │
│     (e.g., "gpu_inference" + "negotiation_v1")   │
│                                                  │
│  2. EVALUATE: Read each seller's AgentCard:      │
│     - reputation_score (from attestation history)│
│     - pricing_hint (min/max range)               │
│     - total_deals_completed                      │
│                                                  │
│  3. RANK: Score sellers by:                      │
│     utility = w1*price + w2*reputation +         │
│               w3*sla_quality + w4*history         │
│     (weights set by user's Standing Intent)      │
│                                                  │
│  4. NEGOTIATE: Open A2A channel with top-ranked  │
│     seller. Execute alternating-offers protocol: │
│     - Start at reservation price (low bid)       │
│     - Concede based on time pressure + opponent  │
│       model (estimated from counteroffer pattern)│
│     - Accept when offer ≥ acceptance threshold   │
│     - Walk away if max rounds exceeded           │
│                                                  │
│  5. COMMIT: On agreement, sign DealContract and  │
│     update AA Wallet constraint to lock price    │
│                                                  │
│  6. EXECUTE: Send standard x402 request to       │
│     seller's service endpoint. Wallet auto-signs │
│     if price matches deal.                       │
│                                                  │
│  7. VERIFY: Check SLA compliance (latency,       │
│     response quality). Attest result on-chain.   │
│                                                  │
│  8. LEARN: Update opponent model for this seller │
│     based on negotiation outcome. Adjust future  │
│     opening bids accordingly.                    │
└─────────────────────────────────────────────────┘
```

### Seller Agent Autonomous Behavior

```
┌─────────────────────────────────────────────────┐
│              SELLER AGENT DECISION LOOP          │
│                                                  │
│  1. PUBLISH: Register AgentCard on ERC-8004      │
│     with capabilities, pricing hint, and         │
│     x402-gated service endpoint                  │
│                                                  │
│  2. LISTEN: Wait for NEGOTIATE_REQUEST on A2A    │
│     message bus                                  │
│                                                  │
│  3. EVALUATE BUYER: Check buyer's ERC-8004 DID,  │
│     reputation score, and deal history via        │
│     attestation registry                         │
│                                                  │
│  4. SET STRATEGY: Based on current demand:       │
│     - High demand → concede slowly, hold price   │
│     - Low demand → concede faster to win deal    │
│     - Adjust floor price based on compute costs  │
│                                                  │
│  5. NEGOTIATE: Respond with counteroffers using  │
│     time-dependent concession strategy:          │
│     offer(t) = reserve + (target - reserve) *    │
│                (1 - (t/T)^(1/e))                 │
│     where e = patience parameter                 │
│                                                  │
│  6. COMMIT: On agreement, sign DealContract.     │
│     Update x402 middleware to serve this buyer   │
│     at the negotiated price (not the posted      │
│     default price)                               │
│                                                  │
│  7. SERVE: Process x402 request, deliver result, │
│     collect payment via Facilitator              │
│                                                  │
│  8. ATTEST: Record deal outcome and SLA metrics  │
│     on-chain. Update own reputation.             │
└─────────────────────────────────────────────────┘
```

### What the Agent Decides Without Human Input

| Decision | Buyer Agent | Seller Agent |
|----------|-------------|--------------|
| **Who to negotiate with** | Ranks sellers by reputation + price hint | Accepts/rejects buyers by reputation score |
| **Opening offer** | Calculated from budget + opponent model | Calculated from compute cost + demand level |
| **Concession rate** | Time-pressure curve + opponent's pattern | Demand-adjusted patience parameter |
| **When to accept** | Utility threshold (price × quality ≥ min) | Profit threshold (price ≥ floor + margin) |
| **When to walk away** | Max rounds exceeded OR no convergence | Buyer reputation too low OR price below floor |
| **How much to pay** | Locked by AA Wallet to agreed price | Locked by x402 header to agreed price |
| **Whether SLA was met** | Measures latency, compares to deal terms | Self-reports, verified by buyer attestation |

---

## 4. What Is Paid For via x402 (Exactly)

The x402 payment is for **access to the seller agent's service endpoint**. In the hackathon demo, this is a specific, concrete service:

### Demo Scenario: GPU Inference Marketplace

| What's Being Sold | How It's Priced | x402 Mechanic |
|-------------------|-----------------|---------------|
| A single LLM inference call (e.g., GPT-4-class completion) | Per-request, negotiated from $0.01–$0.50 range | Buyer pays per-call via `PAYMENT-SIGNATURE` header |

**The payment is NOT for:**
- The negotiation itself (negotiation messages are free, sent over A2A)
- The attestation (gas fees are handled by Kite's gasless testnet)
- The agent identity registration (one-time setup)

**The payment IS for:**
- The actual API response that the seller agent returns after the 402 handshake
- Priced at exactly the amount both agents agreed to during negotiation
- Settled in USDC on Kite via the Facilitator

---

## 5. Open-Source Libraries to Wrap (Hackathon Accelerators)

### Layer 1: Negotiation Engine

| Library | Repo | What to Use | What to Build on Top |
|---------|------|-------------|---------------------|
| **ANEX Protocol** | [ammonhaggerty/ANEX](https://github.com/ammonhaggerty/ANEX) | FIPA-Contract-Net message schema (CFP → PROPOSE → ACCEPT). The performative vocabulary (`REQUEST`, `CFP`, `PROPOSE`, `AGREE`, `REFUSE`) and JSON message structure. | Replace WebSocket transport with A2A messages. Add price/SLA fields to the CFP content schema. Wire the `ACCEPT-PROPOSAL` output into DealContract signing. |
| **NegoLog** | [aniltrue/NegoLog](https://github.com/aniltrue/NegoLog) | `AbstractAgent` pattern (bidding strategy + acceptance strategy + opponent model). The `receive_offer` → `act` loop. The `EstimatedPreference` opponent modeling. | Extract the agent decision loop and concession strategies. Port from tournament simulation to real-time A2A message exchange. Use the opponent model to inform LLM-driven negotiation. |
| **Multi-Agent Negotiation Platform** | [hari7261/Negotiation-MultiAgent](https://github.com/hari7261/Negotiation-MultiAgent) | The Buyer/Seller/Mediator three-agent architecture. The Flask web UI for demo visualization. Agreement detection logic. | Replace Gemini API calls with Kite agent calls. Add x402 settlement as the post-agreement step. Use the analytics dashboard to show judges real-time negotiation metrics. |

### Layer 2: x402 Payment Execution

| Library | Repo | What to Use | What to Build on Top |
|---------|------|-------------|---------------------|
| **x402 Foundation SDK** | [x402-foundation/x402](https://github.com/x402-foundation/x402) | Official `@x402/core`, `@x402/evm`, `@x402/express` (TypeScript) or `pip install x402` (Python). The `paymentMiddleware` for Express/FastAPI. The `PAYMENT-REQUIRED` / `PAYMENT-SIGNATURE` / `PAYMENT-RESPONSE` header flow. | Add `deal_hash` field to `PaymentRequirements`. Add wallet constraint check before signing. This is the canonical implementation — use it directly. |
| **A2A x402 Extension** | [google-agentic-commerce/a2a-x402](https://github.com/google-agentic-commerce/a2a-x402) | The `payment-required` → `payment-submitted` → `payment-completed` A2A message flow. The `x402_a2a` Python library with functional core + executor middleware. | This is the **single most important repo** for NegotiatorGrid. It already bridges A2A communication with x402 settlement. Extend it by adding a negotiation phase between agent discovery and `payment-required`. |
| **x402 Python SDK (Community)** | [samthedataman/x402-sdk](https://github.com/samthedataman/x402-sdk) | `fast-x402` FastAPI middleware (3-line integration). `x402-langchain` for LLM-powered agent payment decisions. EIP-712 signing flow. | Use `fast-x402` for the seller's x402-gated endpoint. Use `x402-langchain` for the buyer agent's autonomous payment logic. Add negotiation-aware spending limits. |

### Layer 3: Agent Identity & Communication

| Library | Repo | What to Use |
|---------|------|-------------|
| **Google A2A Protocol** | [google/a2a-protocol](https://github.com/google/A2A) | Agent-to-agent messaging, AgentCard discovery, task management |
| **Kite Ozone Testnet** | [gokite.ai](https://gokite.ai) | ERC-8004 identity registration, AA Wallet deployment, attestation contracts, gasless USDC |

---

## 6. Recommended Hackathon Build Plan (5–7 Days)

### Day 1–2: Scaffold
- Fork `google-agentic-commerce/a2a-x402` as the base
- Install `x402` Python SDK + `fast-x402` middleware
- Deploy two agent identities on Kite Ozone testnet (ERC-8004)
- Get basic A2A message exchange working between agents

### Day 3–4: Negotiation Engine
- Adapt ANEX FIPA-Contract-Net schema for price/SLA negotiation
- Port NegoLog's `AbstractAgent` → `receive_offer` → `act` loop
- Implement 3-round alternating offers with time-dependent concession
- Add opponent model (track counteroffers, estimate reservation price)

### Day 5: Integration
- Wire negotiation output (agreed price) into x402 `PaymentRequirements`
- Program buyer's AA Wallet with `addSessionKeyRule(valueLimit = agreed_price)`
- Execute full flow: negotiate → lock price → x402 pay → deliver service

### Day 6: Attestation & Demo
- Deploy attestation contract with the DealRecord schema above
- Record negotiation outcomes on-chain after each deal
- Build simple dashboard showing: live negotiation rounds, price convergence chart, on-chain attestation feed

### Day 7: Polish & Edge Cases
- Handle failed negotiations (walk-away, timeout)
- Handle SLA violations (service delivered but latency exceeded)
- Record dispute attestations for SLA breaches
- Stress test with 5+ concurrent negotiations

---

## 7. What Judges See (Demo Script)

1. **Two agents discover each other** via ERC-8004 AgentCards on Kite testnet
2. **Buyer opens negotiation** — screen shows A2A messages in real-time: `CFP → PROPOSE → COUNTER → ACCEPT`
3. **Price converges** — live chart shows offers narrowing from $0.03/$0.10 to $0.06/$0.06
4. **Deal is signed** — on-chain attestation appears on Kite block explorer with full DealRecord
5. **Buyer's wallet is locked** — show the `addSessionKeyRule` transaction with `valueLimit = 0.06`
6. **x402 payment executes** — buyer hits seller's endpoint, gets 402, wallet auto-signs at $0.06, gets response
7. **Attestation records the outcome** — judges can click the tx hash and see: negotiation rounds, convergence rate, SLA compliance, reputation update
8. **Run it again with a different seller** — buyer agent adjusts opening bid based on learned opponent model

The key demo moment: **The buyer agent refuses to pay a seller who posts $0.10 after they agreed on $0.06.** The wallet constraint rejects the mismatched 402 response. This is the "aha" — the negotiation isn't just talk, it's cryptographically enforced.
