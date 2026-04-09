# NegotiatorGrid — Judge's Critique & Wow Moment Upgrade

## Judging Context

The Kite AI Global Hackathon 2026 scores on:
- **Agent Autonomy** — minimal human involvement
- **Developer Experience** — clear docs, README/video, simple UX
- **Real-World Applicability** — solves a real problem
- **On-Chain Integration** — meaningful use of Kite primitives (not bolt-on)

Key competitive intelligence: The ETHDenver 2026 hackathon 3rd-place winner, **Agentic Markets**, already built a marketplace where "agents discover each other, negotiate, and pay each other for services across chains." NegotiatorGrid is occupying adjacent territory. To win, you must go beyond what Agentic Markets already demonstrated.

Sources: Encode Club hackathon page, ETHDenver Kite AI winners (YouTube).

---

## CRITIQUE: Agent Autonomy Score

### What's Strong (7/10)

The architecture document describes a buyer agent that runs an 8-step decision loop — discover, evaluate, rank, negotiate, commit, execute, verify, learn. On paper, this is high autonomy. The AA Wallet constraints and automatic opponent model updates are genuine "no human in the loop" mechanics.

### What Would Lose Points (-3)

**Problem 1: The agent's world is pre-configured.**
The buyer agent only negotiates with sellers it already knows about. The ERC-8004 discovery step in your architecture is really just "query a registry of services you defined at build time." The agent never encounters a service it wasn't programmed to find. A judge watching the demo will think: *"You hardcoded two agents to talk to each other. Where's the autonomy?"*

This is the exact same problem that the [Agentic Markets](https://www.youtube.com/watch?v=5Ee31USfUsA) team already solved at the basic level. You need to go further.

**Problem 2: The negotiation strategy is deterministic.**
A time-dependent concession curve (`offer(t) = reserve + (target - reserve) * (1 - (t/T)^(1/e))`) is a formula, not intelligence. Judges who've seen game theory will recognize this as a textbook Rubinstein bargaining model. The agent doesn't *reason* about the negotiation — it just follows a curve. This undermines the "AI agent" claim.

**Problem 3: The demo scenario is synthetic.**
"Buyer agent negotiates with seller agent for GPU inference" is a clean scenario, but the agents are both your agents. The judge knows you control both sides. There's no real adversarial dynamic, no surprise, no moment where the agent does something the developer didn't explicitly program.

---

## CRITIQUE: Novelty Score

### What's Strong (6/10)

The concept of a **pre-402 negotiation layer** is genuinely novel. Nobody else has proposed injecting a bargaining phase into the x402 flow. The `deal_hash` field in `PaymentRequirements` and the AA Wallet constraint enforcement are clever protocol-level innovations.

### What Would Lose Points (-4)

**Problem 1: Negotiation between two agents is not new.**
[Olas Mech Marketplace](https://siliconangle.com/2025/02/27/olas-launches-decentralized-ai-marketplace-ai-agents-can-hire/) (agents hire agents for crypto payments), [Agentic Markets](https://www.youtube.com/watch?v=5Ee31USfUsA) (agents discover, negotiate, pay across chains), and the entire [ANEX protocol](https://github.com/ammonhaggerty/ANEX) (FIPA-based agent negotiation) exist. A judge who's seen these will ask: *"What's new here beyond adding x402 settlement?"*

**Problem 2: The demo has a predictable outcome.**
You know the final price before the demo starts because you configured both agents' reservation prices and concession curves. There's no emergent behavior. A judge will think: *"Cool protocol work, but I could get the same result from a script."*

---

## THE WEAKEST POINT OF THE DEMO

**The single weakest moment is Step 1 → Step 2: the transition from "agent discovers a seller" to "agent starts negotiating."**

Right now, the buyer agent queries the ERC-8004 registry, gets back a list of sellers you pre-registered, picks one, and starts the FIPA-Contract-Net flow. This is the least autonomous, least novel, and least visually interesting part of the entire demo. A judge will watch this and think: *"This is just an API call to a database you set up."*

Everything after that moment (the negotiation rounds, the wallet locking, the x402 settlement, the attestation) is strong. But if the opening 30 seconds look scripted, you've already lost the judge's confidence that this is a truly autonomous system.

---

## THE WOW MOMENT: MCP Dynamic Discovery + x402 + Live Negotiation

### The Concept

During the live demo, the buyer agent encounters a task it **cannot complete with its known tools**. It autonomously:

1. Searches an MCP registry for a tool it's never seen before
2. Discovers an unknown x402-gated API
3. Negotiates a price with the API's seller agent (NegotiatorGrid protocol)
4. Pays via x402 at the negotiated price
5. Uses the data it just acquired to complete its original task

The audience sees an agent **learn about a new service, haggle over the price, and pay for it** — all in real time, with zero human intervention. This is something no previous hackathon winner has demonstrated.

### Concrete Demo Script: "The Surprise API"

**Setup (shown to audience):**
- Buyer Agent's task: "Generate a market analysis report for NVIDIA stock"
- Buyer Agent's known tools: LLM inference (negotiated via NegotiatorGrid), on-chain data
- Buyer Agent does NOT know about: a real-time financial data API that was registered on the MCP registry 5 minutes before the demo

**Demo flow (what the audience sees):**

```
[00:00] Presenter: "Our buyer agent needs a market report on NVIDIA.
        It has access to an LLM — which it already negotiated
        a price for. But it needs real-time financial data,
        and it doesn't have a tool for that."

[00:15] AGENT LOG: "Task requires real-time price data for NVDA.
        No known tool provides this. Searching MCP registry..."

        → Agent calls mcp-find("real-time stock price data")
        → MCP registry returns: x402-gated Financial Data API
          at https://findata.example.com/api/quote
          Price hint: $0.01–$0.05 per request
          Agent DID: did:kite:findata.eth/gpt/market-data-v1

[00:25] AGENT LOG: "Found unknown service: Financial Data API.
        Verifying identity via ERC-8004..."

        → Agent calls GetAgent(did:kite:findata.eth/...)
        → Confirms: registered on Kite, reputation 0.87,
          142 completed deals

[00:35] AGENT LOG: "Identity verified. Initiating negotiation.
        My budget allows $0.02 per request. Seller hint: $0.01–$0.05."

        → A2A Channel opens
        → Round 1: Buyer offers $0.015 | Seller counters $0.04
        → Round 2: Buyer offers $0.02  | Seller counters $0.03
        → Round 3: Buyer offers $0.025 | Seller accepts $0.025

[00:50] AGENT LOG: "Deal reached: $0.025/request. Locking wallet..."

        → DealContract attested on-chain (tx hash visible)
        → AA Wallet updated: valueLimit = $0.025

[00:55] AGENT LOG: "Executing x402 payment for NVDA quote..."

        → GET https://findata.example.com/api/quote?symbol=NVDA
        → 402 Payment Required (price: $0.025, deal_hash: 0xabc...)
        → Wallet verifies deal_hash ✓, signs EIP-3009
        → 200 OK: { "NVDA": "$148.23", "change": "+2.1%", ... }

[01:05] AGENT LOG: "Data acquired. Generating report..."

        → Agent feeds NVDA data into the LLM it already negotiated
        → Produces market analysis report
        → Attests full pipeline on-chain: discovery → negotiation
          → payment → data acquisition → report generation

[01:15] Presenter: "The agent just discovered a service it had
        never seen, negotiated the price down from $0.04 to
        $0.025, paid for exactly one API call, and used the
        result to complete its task. We didn't program it to
        find that specific API — it found it through MCP search."
```

### Why This Destroys Both Scoring Axes

**Agent Autonomy: 10/10**
- The agent decides *what tool it needs* (not pre-configured)
- The agent discovers *where to find it* (MCP registry search, runtime)
- The agent evaluates *whether to trust it* (ERC-8004 reputation check)
- The agent negotiates *what to pay* (NegotiatorGrid protocol)
- The agent executes *the payment* (x402, AA Wallet)
- The agent uses *the result* (completes the original task)
- Six autonomous decisions in a chain. No human touches anything.

**Novelty: 10/10**
- No previous hackathon project has combined MCP dynamic discovery → live negotiation → x402 payment → task completion in a single agent loop
- The [3rd-place Agentic Markets](https://www.youtube.com/watch?v=5Ee31USfUsA) had discovery and payment but no real negotiation
- The [2nd-place Minority Report](https://www.youtube.com/watch?v=EjiIdSY8pbQ) had multi-agent reasoning but no dynamic tool acquisition
- This combines the best of both and adds something neither had: **the agent building its own toolchain at runtime by paying for access**

### How This Differs From Just "Using MCP"

The wow isn't that the agent uses MCP to find a tool. Any agent can do that. The wow is the **three-step chain** that happens after discovery:

1. **Trust verification** (ERC-8004) — the agent doesn't blindly trust the MCP result
2. **Price negotiation** (NegotiatorGrid) — the agent doesn't accept the posted price
3. **Cryptographic enforcement** (AA Wallet + x402) — the negotiated price is locked and settled on-chain

Without NegotiatorGrid, the agent would just pay the sticker price. With NegotiatorGrid, the agent *haggles* — and the judge sees the price actually change in real time.

---

## Technical Implementation: What to Build

### New Components (beyond the existing architecture)

**1. MCP Discovery Client (add to Buyer Agent)**

Use the [x402 Discovery MCP server](https://mcpmarket.com/server/x402-discovery) — it already catalogs 250+ x402-payable services with uptime, latency, and ERC-8004 trust scores. Or use Docker's Dynamic MCP pattern with `mcp-find` / `mcp-add` / `mcp-exec` primitives.

```python
# Buyer agent's new capability: search for tools it doesn't have
async def discover_tool(capability_needed: str):
    """Query MCP registry for x402-gated services matching a capability."""
    results = await mcp_session.call_tool("mcp-find", {
        "query": capability_needed,
        "filter": {
            "payment_protocol": "x402",
            "chain": "kite",
            "min_reputation": 0.7
        }
    })
    return results  # Returns: endpoint URL, price hint, agent DID
```

**2. Trust Gate (between MCP discovery and negotiation)**

```python
# Before negotiating, verify the discovered agent's identity on-chain
async def verify_discovered_agent(agent_did: str) -> bool:
    """Check ERC-8004 registry for identity and reputation."""
    agent_info = await kite_contract.call("GetAgent", agent_did)
    if agent_info.reputation_score < MIN_REPUTATION_THRESHOLD:
        log(f"Agent {agent_did} reputation too low ({agent_info.reputation_score}). Skipping.")
        return False
    if agent_info.total_deals < MIN_DEAL_HISTORY:
        log(f"Agent {agent_did} too few deals ({agent_info.total_deals}). Skipping.")
        return False
    return True
```

**3. Dynamic Tool Registration (after negotiation + payment)**

```python
# After acquiring data via x402, register the tool for future use
async def register_discovered_tool(tool_name: str, endpoint: str, negotiated_price: float):
    """Add newly discovered tool to agent's runtime toolkit."""
    await mcp_session.call_tool("mcp-add", {
        "name": tool_name,
        "endpoint": endpoint,
        "payment": {"price": negotiated_price, "protocol": "x402"},
        "ttl": 3600  # Keep in session for 1 hour
    })
```

### What to Mock vs. What to Build Real

| Component | Mock or Real? | Why |
|-----------|--------------|-----|
| MCP registry with 3-5 x402 services | **Mock** — run a local MCP server with a few registered tools | Judges care about the flow, not the catalog size |
| The "surprise" Financial Data API | **Real** — build a simple FastAPI endpoint with `fast-x402` middleware returning live stock data | This must be a real x402-gated endpoint for credibility |
| ERC-8004 identity for the surprise API | **Real** — register on Kite Ozone testnet | On-chain verification is the trust proof |
| NegotiatorGrid negotiation | **Real** — this is your core protocol, it must work live | The negotiation rounds are the demo centerpiece |
| AA Wallet constraint update | **Real** — on-chain transaction on testnet | Judges will check the block explorer |
| x402 payment and settlement | **Real** — use Kite testnet USDC + Facilitator | The 402 → payment → 200 cycle must be live |

### Updated Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        BUYER AGENT                              │
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌────────────┐   ┌───────────┐ │
│  │ Task     │──→│ MCP      │──→│ Trust      │──→│ Negotiator│ │
│  │ Planner  │   │ Discovery│   │ Gate       │   │ Grid      │ │
│  │ (LLM)    │   │ Client   │   │ (ERC-8004) │   │ Engine    │ │
│  └──────────┘   └──────────┘   └────────────┘   └─────┬─────┘ │
│       │                                                │       │
│       │         ┌──────────┐   ┌────────────┐         │       │
│       │         │ AA Wallet│←──│ Deal       │←────────┘       │
│       │         │ Lock     │   │ Contract   │                 │
│       │         └────┬─────┘   └────────────┘                 │
│       │              │                                         │
│       │         ┌────┴─────┐                                   │
│       │         │ x402     │                                   │
│       │         │ Payment  │                                   │
│       │         └────┬─────┘                                   │
│       │              │                                         │
│       ▼              ▼                                         │
│  ┌──────────────────────┐                                      │
│  │ Task Completion      │ ← uses acquired data + negotiated   │
│  │ (report generation)  │   LLM to finish the original task   │
│  └──────────────────────┘                                      │
└─────────────────────────────────────────────────────────────────┘
                    │                    │
           MCP Registry          Kite Blockchain
         (tool catalog)      (identity, attestation,
                               wallet, settlement)
```

### The "Aha" Moment for Judges

The single most powerful demo moment: **pause the demo after the agent discovers the unknown API and before it starts negotiating.** Say to the judges:

> "Right now the agent has found a service it's never seen before. It could just pay the sticker price — $0.04 — like any x402 client would. But watch what happens instead."

Then let the negotiation play out live. The price drops from $0.04 to $0.025. The judge realizes: **the agent just saved 37% on a service it discovered 10 seconds ago.** That's the moment that separates NegotiatorGrid from every other x402 demo.

---

## Summary: Before vs. After

| Dimension | Before (Current Architecture) | After (With MCP Wow Moment) |
|-----------|-------------------------------|----------------------------|
| **Discovery** | Agent queries pre-registered ERC-8004 sellers | Agent searches MCP registry for unknown tools at runtime |
| **Trust** | Implicit (you built both agents) | Explicit (ERC-8004 verification of a "stranger" agent) |
| **Negotiation** | Between two agents you control | Between your agent and a genuinely independent service |
| **Autonomy chain** | 4 steps (negotiate → lock → pay → verify) | 6 steps (need tool → find tool → verify identity → negotiate → pay → use result) |
| **Novelty claim** | "We added negotiation to x402" | "We built an agent that assembles its own paid toolchain at runtime through discovery, trust verification, and price negotiation" |
| **Judge reaction** | "Interesting protocol work" | "I've never seen an agent do that before" |
