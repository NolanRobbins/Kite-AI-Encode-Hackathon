# Perplexity Computer — NegotiatorGrid Research Execution Plan (Final)

## How This Document Works

This is a **prompt-by-prompt execution plan** for Perplexity Computer, adapted specifically for **NegotiatorGrid** — an agent-to-agent price negotiation protocol on the Kite AI blockchain (Novel Track). Each phase has:
- **Goal**: What you're trying to learn
- **Connectors to enable**: Which Perplexity connectors to toggle ON for that phase
- **Prompts**: Exact prompts to paste, in order
- **Output capture**: What to save and where

Run phases sequentially. Each phase builds on prior outputs.

**Key constraint**: Do NOT include trading, portfolio management, or standard retail commerce. Focus on machine-to-machine (M2M) payments where AI agents autonomously pay for micro-services, compute, data access, or API limits using the x402 protocol.

---

## SKILL.md — Paste This Into Your Perplexity Prompt Feed

```yaml
---
name: negotiatorgrid-researcher
description: >
  Systematic research agent for NegotiatorGrid — an agent-to-agent price negotiation
  protocol for the Kite AI × Encode Hackathon (March 27 – April 26, 2026).
  Researches bilateral negotiation engines, x402 payment settlement, MCP dynamic
  discovery, A2A messaging, opponent modeling, and on-chain attestation patterns.
  Outputs structured notes with source URLs, confidence levels, and open questions.
context:
  hackathon: "Kite AI Global Hackathon 2026 via Encode Club"
  track: "Novel"
  project: "NegotiatorGrid — pre-x402 negotiation layer for agent-to-agent price bargaining"
  chain: "Kite L1 — EVM, Chain ID 2368 (testnet) / 2366 (mainnet)"
  rpc: "https://rpc-testnet.gokite.ai/"
  explorer: "https://testnet.kitescan.ai/"
  faucet: "https://faucet.gokite.ai"
  test_usdt: "0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63"
  kite_facilitator: "0x12343e649e6b2b2b77649DFAb88f103c02F3C78b"
  x402_demo_endpoint: "https://x402.dev.gokite.ai/api/weather"
  mcp_server: "https://mcp.prod.gokite.ai/"
  kitepass_portal: "https://app.gokite.ai/"
  key_repos:
    - "x402-foundation/x402"
    - "google-agentic-commerce/a2a-x402"
    - "yasserfarouk/negmas"
    - "aniltrue/NegoLog"
    - "ammonhaggerty/ANEX"
    - "hari7261/Negotiation-MultiAgent"
    - "samthedataman/x402-sdk"
    - "gambitproject/gambit"
    - "FranxYao/GPT-Bargaining"
  key_docs:
    - "docs.gokite.ai"
    - "docs.x402.org"
    - "docs.cdp.coinbase.com/x402"
    - "negmas.readthedocs.io"
    - "agent2agent.info"
    - "eips.ethereum.org/EIPS/eip-8004"
  key_papers:
    - "arXiv:2604.03733 — SoK: Blockchain Agent-to-Agent Payments (Apr 2026)"
    - "arXiv:2602.06008 — AgenticPay: Multi-Agent LLM Negotiation (Feb 2026)"
    - "arXiv:2602.14219 — The Agent Economy (Feb 2026)"
    - "arXiv:2603.01179 — A402: Atomic Service Channels (Mar 2026)"
    - "arXiv:2503.23278 — MCP Security Threats (Mar 2025)"
    - "arXiv:2603.13417 — MCP Production Design Patterns (Mar 2026)"
    - "arXiv:2511.03434 — Inter-Agent Trust Models (Nov 2025)"
    - "arXiv:2601.08815 — Agent Contracts Formal Framework (Jan 2026)"
output_format: |
  For every research response, structure output as:
  ## [Topic]
  **Sources**: [numbered list of URLs]
  **Key Findings**: [bullet points, each tagged with source number]
  **Confidence**: HIGH / MEDIUM / LOW (based on source quality)
  **Open Questions**: [things that remain unclear or unverified]
  **Code Snippets**: [if applicable, with language tag]
  **Action Items**: [concrete next steps for the builder]
---
```

### Secondary Skill: Competitor & Prior Art Scanner

```yaml
---
name: negotiatorgrid-competitor-scanner
description: >
  Finds existing projects, submissions, and reference implementations built on Kite,
  x402, or agent negotiation protocols. Identifies what's been done so we can differentiate.
  Known prior art: Agentic Markets (ETHDenver 3rd), Minority Report (ETHDenver 2nd),
  Kite Trace Platform (ETHDenver 2nd), SEIpients (cookie.fun).
output_format: |
  ## Prior Art: [Project Name]
  **Repo/URL**: [link]
  **What it does**: [1-2 sentences]
  **Kite primitives used**: [list]
  **Gaps / Weaknesses**: [what we could do better]
  **Relevance to our build**: HIGH / MEDIUM / LOW
---
```

### Tertiary Skill: Demo & DX Evaluator

```yaml
---
name: demo-dx-evaluator
description: >
  Evaluates hackathon-winning projects for demo structure, README quality, and
  developer experience patterns. Extracts reusable templates.
output_format: |
  ## [Project Name] — DX Audit
  **Demo format**: [video / live / CLI / web app]
  **Setup complexity**: [one-liner / multi-step / Docker / complex]
  **README quality**: [score 1-5, with notes]
  **Reproducibility**: [could I run this in 5 min? why/why not]
  **Steal-worthy patterns**: [specific things to copy]
---
```

### Quaternary Skill: Academic Literature Synthesizer

```yaml
---
name: negotiatorgrid-literature-synthesizer
description: >
  Finds and synthesizes academic papers relevant to agent-to-agent negotiation,
  x402 payment protocols, MCP security, account abstraction, opponent modeling,
  and game-theoretic pricing. Outputs structured notes suitable for both
  implementation guidance and judge-facing narrative.
output_format: |
  ## [Paper Title]
  **ArXiv ID**: [e.g., 2602.14219]
  **Authors**: [first author et al.]
  **Date**: [submission date]
  **URL**: [arxiv link]
  **Core Contribution**: [2-3 sentences — what's novel]
  **Relevance to NegotiatorGrid**: HIGH / MEDIUM / LOW
  **Key Takeaways for Implementation**:
    - [actionable insight 1]
    - [actionable insight 2]
  **Quotable for Demo/Judges**: [1 sentence we could cite in our pitch]
  **Code Repo**: [link if available, or "None found"]
  **Limitations / Gaps**: [what the paper doesn't solve that we need]
---
```

---

## Connector Matrix — What to Enable Per Phase

| Phase | Connectors ON | Why |
|-------|--------------|-----|
| **1: Kite Protocol Deep Dive** | GitHub | Read repos, READMEs, code, issues from `gokite-ai/*` |
| **2: Negotiation Engine Deep Dive** | GitHub | Read NegMAS, NegoLog, ANEX, GPT-Bargaining source code |
| **2.5: Academic Literature** | *(none — use Perplexity's native web search)* | arXiv, Semantic Scholar are all web-indexed |
| **3: x402 + A2A Payment Integration** | GitHub | `x402-foundation/x402`, `google-agentic-commerce/a2a-x402` source |
| **4: MCP Dynamic Discovery** | GitHub | MCP spec repo, Docker dynamic MCP, x402 Discovery catalog |
| **5: Competitor & Prior Art Scan** | GitHub, Apify | Search GitHub topics, check hackathon submission pages |
| **6: Agent Architecture & Opponent Modeling** | GitHub | Agent framework repos, opponent modeling libraries |
| **7: Infra & Deploy** | GitHub | Hardhat configs, Vercel deploy patterns, WebSocket patterns |
| **8: Synthesis & Sprint Planning** | *(none)* | Consolidate into ADR, sprint backlog, demo script |

### Connectors to NEVER enable for this workflow
- Medical Records, Wearables, sevDesk, Personio, Procore, BioRender, Jotform, etc. — completely irrelevant
- Snowflake, Databricks, MongoDB, PostgreSQL, etc. — no database research needed
- Mailchimp, ConvertKit, AWeber, etc. — email marketing irrelevant
- Salesforce, HubSpot, Attio, etc. — CRM irrelevant
- Spotify, Bluesky, Mastodon, Telegram, etc. — social/messaging irrelevant

---

## Phase 1: Kite Protocol Deep Dive

**Goal**: Understand Kite's full architecture — identity, wallets, payment flow, chain specifics — as they relate to NegotiatorGrid's settlement layer.
**Connectors ON**: GitHub
**Estimated prompts**: 5
**Time**: ~45 min

### Prompt 1.1 — Kite Whitepaper & Architecture (Negotiation Lens)
```
Using the negotiatorgrid-researcher skill:

Read the Kite whitepaper at gokite.ai/kite-whitepaper and the core concepts page at docs.gokite.ai/get-started-why-kite/core-concepts-and-terminology.

I'm building NegotiatorGrid — an agent-to-agent price negotiation protocol. I need Kite's architecture mapped to negotiation primitives.

Extract:
1. The three-layer architecture (Platform, Programmable Trust, Ecosystem) — which layer does negotiation live in?
2. The identity model: KitePass → DID → VCs → Proof of AI — how does a negotiating agent prove its identity to a counterparty?
3. Wallet architecture: EOA vs AA wallet vs Embedded wallet — which is right for an agent that needs programmable spending limits locked to negotiated prices?
4. The SPACE framework components — which ones enforce negotiation outcomes?
5. Session keys / ephemeral keys — can a session key be programmed with a spending cap = negotiated price?
6. SLA contracts — can NegotiatorGrid's deal terms (price, latency, quality) be encoded as an SLA contract?

Tag each finding with the exact doc section it came from.
List anything that's described conceptually but where you can't find actual API/SDK documentation.
```

### Prompt 1.2 — KiteSDK & Agent Builder Workflow
```
Using the negotiatorgrid-researcher skill:

Read docs.gokite.ai/kite-air-platform/kite-air-getting-started thoroughly.

Extract:
1. The exact Python SDK installation command and import pattern
2. KiteClient initialization — what params does it take?
3. Full method inventory: list_services(), execute_task(), and any others
4. The KitePass claim flow — step by step from app.gokite.ai
5. How the API key maps to the agent's on-chain identity
6. Service discovery: how does an agent browse the App Store programmatically?
7. Can two agents discover each other via KiteSDK? (This is critical for NegotiatorGrid's peer discovery)

If the SDK source is on PyPI or GitHub, find the actual package and check if there's more detailed API docs.
```

### Prompt 1.3 — Kite MCP Server (Negotiation Integration)
```
Using the negotiatorgrid-researcher skill:

Research the Kite MCP Server integration. Sources to check:
- docs.gokite.ai (search for "MCP")
- The MCP server URL: https://mcp.prod.gokite.ai/
- GitHub: search gokite-ai org for any MCP-related repos

I need:
1. The exact MCP server URL and transport type (SSE vs Streamable HTTP)
2. The claude_desktop_config.json snippet for connecting
3. What tools does the Kite MCP server expose? (tool names, descriptions, input schemas)
4. Can I use it from a custom Python MCP client, or only from Claude Desktop?
5. Does it handle x402 payments automatically, or do I still need to implement the payment handshake?
6. Can NegotiatorGrid register its negotiation endpoints as MCP tools? (This enables the "wow moment" — dynamic discovery of a negotiable service)

This is critical — if the MCP server handles payment automatically, NegotiatorGrid only needs to add the negotiation layer on top.
```

### Prompt 1.4 — Kite Chain Specifics (AA SDK for Negotiation Constraints)
```
Using the negotiatorgrid-researcher skill:

Go through these docs.gokite.ai sections and extract implementation details:
- Account Abstraction SDK
- Kite Gasless Integration
- Multisig Wallet
- Kite Stablecoin

For each, I need:
1. Is there an npm package or SDK? What's the install command?
2. Are there code examples in the docs? Copy the key snippets.
3. What's the contract address for the AA wallet factory on testnet?
4. How does gasless work — is there a paymaster? What's its address?
5. The Test USDT address is 0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63 — confirm and check for other supported tokens.
6. Can addSessionKeyRule() accept a dynamic valueLimit? (NegotiatorGrid needs to update the spending cap after each negotiation concludes)
7. The Kite Facilitator address is 0x12343e649e6b2b2b77649DFAb88f103c02F3C78b — confirm and document the /v2/settle API.

Flag anything that's "coming soon" or has no actual code behind it.
```

### Prompt 1.5 — Kite GitHub Org Inventory
```
Using the negotiatorgrid-researcher skill with GitHub connector:

Search the GitHub organization github.com/gokite-ai and catalog ALL public repositories.

For each repo, note:
- Name, Description, Primary language, Last commit date, Stars / activity level
- Relevance to NegotiatorGrid (HIGH/MEDIUM/LOW/NONE)

Pay special attention to:
- gokite-ai/x402 — is this a fork of the Coinbase x402 or custom? Does it include the "gokite-aa" payment scheme?
- gokite-ai/agentic-commerce-protocol — fork of OpenAI/Stripe ACP?
- gokite-ai/AP2-kite — what is Agent Payment Protocol v2? Can it support variable pricing?
- Any SDK repos, sample apps, or starter templates
- Any repos with recent commits (last 30 days) that might be hackathon-related
- Any ERC-8004 identity-related contracts

Output as a table sorted by relevance.
```

---

## Phase 2: Negotiation Engine Deep Dive

**Goal**: Understand automated bilateral negotiation deeply enough to implement NegotiatorGrid's core protocol — the alternating-offers engine with opponent modeling, concession strategies, and deal enforcement.
**Connectors ON**: GitHub
**Estimated prompts**: 5
**Time**: ~40 min

### Prompt 2.1 — NegMAS Framework (Core Negotiation Library)
```
Using the negotiatorgrid-researcher skill with GitHub connector:

Read the NegMAS library at github.com/yasserfarouk/negmas and its docs at negmas.readthedocs.io.

NegMAS is the foundational Python negotiation library (85 stars, pip install negmas). I need:

1. The SAO (Stacked Alternating Offers) protocol — exact message flow and API
2. Built-in negotiator types and their strategies:
   - AspirationNegotiator — how does the aspiration curve work?
   - TimeBasedConcedingNegotiator — time-dependent concession formula
   - BoulwareTBNegotiator — "boulware" hard-bargaining strategy
   - TitForTatNegotiator — reciprocal concession
3. The BOA framework (Bidding–Opponent modeling–Acceptance):
   - How to plug in custom bidding, opponent model, and acceptance strategies
   - GSmithFrequencyModel — how does frequency-based opponent modeling work?
4. Utility function types: LinearAdditiveUtilityFunction, MappingUtilityFunction
5. How to run a bilateral negotiation session between two agents in Python (code example)
6. Can NegMAS agents be wrapped with A2A message transport? (Replace local function calls with network messages)

This is NegotiatorGrid's primary negotiation library. The BOA framework maps directly to our architecture.
```

### Prompt 2.2 — NegoLog Framework (Opponent Modeling)
```
Using the negotiatorgrid-researcher skill with GitHub connector:

Read github.com/aniltrue/NegoLog — the IJCAI 2024 negotiation framework.

Extract:
1. The AbstractOpponentModel class — what interface does it expose?
2. The EstimatedPreference objects — how are opponent preferences represented?
3. The receive_offer → act loop — exact method signatures
4. The Domain Generator — how to create custom negotiation scenarios
5. Callbacks: before_session_start, on_offer, on_accept, on_fail — when do they fire?
6. How to benchmark different opponent models independently of bidding strategy

NegotiatorGrid needs NegoLog's opponent modeling architecture to track counterparty behavior across multiple negotiation rounds and sessions. The decoupled opponent model → bidding strategy pattern is the right abstraction.
```

### Prompt 2.3 — LLM-Native Negotiation Patterns
```
Using the negotiatorgrid-researcher skill:

Research LLM-powered negotiation approaches that NegotiatorGrid can use:

1. GPT-Bargaining (github.com/FranxYao/GPT-Bargaining, 208 stars):
   - The buyer/seller/critic three-agent architecture
   - The self-play improvement loop
   - How does the LLM generate structured bids vs free-form dialogue?

2. AgenticPay (arXiv:2602.06008, github.com/SafeRL-Lab/AgenticPay):
   - The 110+ negotiation task benchmark
   - Structured action extraction (bid/accept/reject parse layer)
   - Which LLMs perform best? (Claude Opus 4.5 closes in 3.7 rounds vs Llama-3.1-8B 49% failure rate)
   - Welfare metrics (social surplus, individual utility) — can these map to on-chain attestation?

3. PACT benchmark (github.com/lechmazur/pact, 29 stars):
   - 5,000+ LLM bargaining games with JSONL logs
   - Composite Model Score (CMS) metric — adoptable as NegotiatorGrid KPI

4. ASTRA framework (arXiv:2503.07129):
   - LP-solver-based offer optimization
   - Stance classification for opponent modeling
   - How to combine LLM reasoning with game-theoretic optimization

Key question: Should NegotiatorGrid use LLM-native negotiation (natural language bids) or structured protocol (JSON offers)? Or a hybrid where the LLM reasons about strategy but outputs structured FIPA-CNP messages?
```

### Prompt 2.4 — FIPA Contract-Net Protocol (Message Format)
```
Using the negotiatorgrid-researcher skill with GitHub connector:

Read github.com/ammonhaggerty/ANEX — the FIPA-based Agent Negotiation & Exchange Protocol.

Extract:
1. The FIPA-Contract-Net phases: Self-Identification → Initiation → Response Handling → Term Negotiation → Data Exchange → Session Termination
2. The ACL message structure: performative, sender, receiver, content JSON, ontology
3. The performative vocabulary: REQUEST, CFP, PROPOSE, AGREE, REFUSE, ACCEPT-PROPOSAL, REJECT-PROPOSAL
4. How to map FIPA-CNP messages to A2A protocol messages (JSON-RPC 2.0)

Then design NegotiatorGrid's wire format:
5. What fields does a NEGOTIATE_REQUEST message need? (buyer DID, capability needed, budget range, SLA requirements)
6. What fields does a COUNTER_OFFER message need? (price, SLA terms, validity window, round number)
7. What fields does a DEAL_CONTRACT message need? (agreed price, SLA, deal_hash, buyer signature, seller signature)

The goal is a message schema that bridges FIPA-CNP formalism with A2A transport and x402 settlement.
```

### Prompt 2.5 — Game-Theoretic Pricing & Nash Bargaining
```
Using the negotiatorgrid-researcher skill:

Research the game-theoretic foundations for NegotiatorGrid's pricing engine:

1. Gambit library (github.com/gambitproject/gambit, 435 stars):
   - Can Gambit compute the Nash Bargaining Solution in real-time during negotiation?
   - Python API: import gambit → how to define a bargaining game?
   - Performance: how fast is Nash equilibrium computation for a 2-player game?

2. Rubinstein Alternating-Offers Model:
   - The standard formula: agent offers, opponent accepts or counters, with time discounting
   - No standalone Python implementation exists (confirmed gap) — what do we need to build?
   - The time-dependent concession curve: offer(t) = reserve + (target - reserve) * (1 - (t/T)^(1/e))

3. How to combine game theory with LLM reasoning:
   - "Game-Theoretic LLM" paper (arXiv:2411.05990, code at github.com/Wenyueh/game_theory)
   - Nash Equilibrium-guided offer validation
   - Can the LLM propose offers while a game-theoretic module validates they're rational?

The pricing engine is NegotiatorGrid's core differentiator — agents that negotiate intelligently, not just follow a curve.
```

---

## Phase 2.5: Academic Literature Synthesis

**Goal**: Build the academic foundation that strengthens both implementation decisions and the judge-facing narrative. Most hackathon teams cite zero papers — citing 5+ with specific implementation connections is a massive differentiator.
**Connectors ON**: None needed — use native web search for arXiv/Semantic Scholar.
**Estimated prompts**: 5
**Time**: ~35 min

### Prompt 2.5.1 — LLM Negotiation & Bargaining Papers
```
Using the negotiatorgrid-literature-synthesizer skill:

Find and synthesize papers on LLM-powered bilateral negotiation. These are the known HIGH-relevance papers:

1. "AgenticPay" (arXiv:2602.06008, Feb 2026) — 110+ negotiation tasks, structured action extraction, welfare metrics
   Code: github.com/SafeRL-Lab/AgenticPay

2. "ASTRA" (arXiv:2503.07129, Mar 2025) — LP-solver offer optimization + stance classification
   
3. "LLM Rationalis" (arXiv:2412.09136, Dec 2024) — Cooperative Rationality Index for negotiation evaluation

4. "NegotiationArena" (arXiv:2402.05863, Feb 2024) — behavioral manipulation in LLM negotiation

5. "Game-Theoretic LLM" (arXiv:2411.05990, Nov 2024) — Nash equilibrium-guided workflows
   Code: github.com/Wenyueh/game_theory

6. "BDI Agent Negotiation Framework" (AAAI-26, Jan 2026) — belief-desire-intention for automated negotiation

For each, extract how NegotiatorGrid can use the technique. Focus on:
- Structured bid generation (not free-form chat)
- Opponent modeling from offer history
- Concession strategy optimization
- Performance benchmarks (rounds to agreement, failure rates)

Then search for 2-3 additional papers from 2025-2026 that extend this work.
```

### Prompt 2.5.2 — Agent-to-Agent Payments & x402 Research
```
Using the negotiatorgrid-literature-synthesizer skill:

These are the critical payment infrastructure papers:

1. "SoK: Blockchain Agent-to-Agent Payments" (arXiv:2604.03733, April 2026) — CRITICAL
   - Four-stage lifecycle: Discovery, Authorization, Execution, Settlement
   - Explicitly identifies price negotiation as an open problem
   - Cites the Kite whitepaper directly

2. "A402: Binding Cryptocurrency Payments to Service Execution" (arXiv:2603.01179, Mar 2026)
   - Atomic Service Channels (ASCs) with TEE-assisted adaptor signatures
   - Fixes x402's atomicity gap — payment and service delivery become atomic

3. "The Agent Economy" (arXiv:2602.14219, Feb 2026)
   - Five-layer architecture: Physical Infrastructure, Identity & Agency, Cognitive & Tooling, Economic & Settlement, Collective Governance
   - NegotiatorGrid spans the Economic & Settlement layer

4. "Whispers of Wealth: Red-Teaming Google's Agent Payments Protocol" (arXiv:2601.22569)
   - Security attacks on agent payment systems via prompt injection
   - What mitigations does NegotiatorGrid need?

5. "Secure Autonomous Agent Payments" (arXiv:2511.15712)
   - Verifying authenticity and intent in trustless environments

For each: What failure modes of x402 do they identify? What improvements do they propose? What security risks must NegotiatorGrid mitigate? Do any propose on-chain attestation patterns we can implement?
```

### Prompt 2.5.3 — Trust, Reputation & Mechanism Design
```
Using the negotiatorgrid-literature-synthesizer skill:

Papers on trust and reputation systems for autonomous agent markets:

1. "Inter-Agent Trust Models" (arXiv:2511.03434, Nov 2025)
   - Compares Brief, Claim, Proof, Stake, Reputation, and Constraint trust models
   - Covers A2A, AP2, ERC-8004 specifically
   - Recommends Proof + Stake as trustless-by-default foundation

2. "Can We Govern the Agent-to-Agent Economy?" (arXiv:2501.16606, Jan 2025)
   - Agentbound Tokens, cryptoeconomic governance
   
3. "Insured Agents" (arXiv:2512.08737, Dec 2025)
   - Decentralized trust insurance mechanism for agentic economy

4. "Agent Contracts: A Formal Framework for Resource-Bounded Autonomous AI Systems" (arXiv:2601.08815, Jan 2026, accepted COINE 2026 / AAMAS)
   - Formal C=(I,O,S,R,T,Φ,Ψ) contract model
   - 90% token reduction through constraint enforcement

For NegotiatorGrid:
- How should reputation scores from the ERC-8004 Reputation Registry influence negotiation strategy?
- Should agents with higher reputation get better opening offers?
- How to prevent collusion between repeated counterparties?
- What's the formal security model for session key compromise during negotiation?
```

### Prompt 2.5.4 — MCP Security & Account Abstraction
```
Using the negotiatorgrid-literature-synthesizer skill:

MCP Security papers (critical for the dynamic discovery "wow moment"):

1. "MCP: Landscape, Security Threats, and Future Research Directions" (arXiv:2503.23278)
   - 38-category threat taxonomy: tool poisoning, command injection, credential theft, RADE attacks
   - What threats apply when NegotiatorGrid's agent discovers an unknown MCP tool?

2. "Bridging Protocol and Production: Design Patterns for Deploying AI Agents with MCP" (arXiv:2603.13417, Mar 2026)
   - Three missing protocol primitives: identity propagation, adaptive tool budgeting, structured error semantics
   - NegotiatorGrid needs all three for secure dynamic discovery

3. "MCP Tool Descriptions Are Smelly" (arXiv:2602.14878, Feb 2026)
   - Tool description quality impacts agent performance
   - How should NegotiatorGrid describe its negotiation tools for MCP registration?

Account Abstraction papers:
4. "Binding Agent ID" (arXiv:2512.17538, Dec 2025) — zkVM-based agent authentication
5. "Authenticated Delegation and Authorized AI Agents" (arXiv:2501.09674, Jan 2025) — extends OAuth 2.0 with Agent-ID Tokens

For each: Extract the specific security mitigations NegotiatorGrid should implement. These become judge Q&A ammo.
```

### Prompt 2.5.5 — Synthesis: Academic Narrative for Judges
```
Using the negotiatorgrid-literature-synthesizer skill:

Based on papers from prompts 2.5.1 through 2.5.4, synthesize a "Research Context" section for the NegotiatorGrid hackathon submission.

I need:
1. A 3-paragraph narrative (suitable for README or pitch deck):
   - Para 1: Agent-to-agent economies are growing, but payment infrastructure is one-shot "take or leave" (cite Agent Economy + SoK papers)
   - Para 2: Multi-round price negotiation between autonomous agents is an unsolved problem (cite SoK's explicit gap identification + AgenticPay benchmarks showing LLMs can negotiate)
   - Para 3: NegotiatorGrid fills this gap by combining game-theoretic bilateral negotiation (cite ASTRA, Game-Theoretic LLM) with x402 settlement on Kite (cite A402 atomicity) and MCP dynamic discovery (cite MCP production patterns)

2. A "References" list formatted as:
   [1] Author et al., "Title," arXiv:XXXX.XXXXX, Month Year.
   — limited to the 10-12 most relevant papers

3. A "Judge Q&A Ammo" section:
   - Q: "What's the academic basis for this?" → cite SoK + Agent Economy + AgenticPay
   - Q: "Is x402 secure for negotiated prices?" → cite A402 atomic channels + Red-teaming paper, explain mitigations
   - Q: "Why game theory instead of just LLM negotiation?" → cite Game-Theoretic LLM paper showing Nash-guided offers outperform pure LLM
   - Q: "Why account abstraction?" → cite Agent Contracts formal framework + Binding Agent ID
   - Q: "What about MCP security?" → cite MCP threat taxonomy (38 categories) + production design patterns paper
   - Q: "How do you prevent agents from colluding?" → cite Inter-Agent Trust Models paper + on-chain reputation attestation
   - Q: "How does this differ from Agentic Markets (ETHDenver 3rd)?" → they had discovery + payment but no real multi-round negotiation; we add game-theoretic bargaining + opponent modeling + cryptographic deal enforcement
```

---

## Phase 3: x402 + A2A Payment Integration

**Goal**: Understand x402 and A2A deeply enough to implement the settlement layer — where negotiated prices become actual payments.
**Connectors ON**: GitHub
**Estimated prompts**: 4
**Time**: ~30 min

### Prompt 3.1 — x402 Core Flow (Post-Negotiation Settlement)
```
Using the negotiatorgrid-researcher skill:

Read the x402 protocol specification at docs.x402.org/getting-started/quickstart-for-sellers and docs.cdp.coinbase.com/x402/welcome.

NegotiatorGrid modifies the x402 flow: the price in PAYMENT-REQUIRED is not fixed — it's the result of a negotiation. Extract the COMPLETE payment flow with exact header names and JSON schemas:

1. Client sends GET/POST to resource
2. Server returns 402 — exact response format (headers + body)
3. PaymentRequirements object — what fields? Can we add a custom "deal_hash" field to link back to the negotiation?
4. Client constructs payment — signing process, EIP-712 typed data structure
5. Client retries with X-PAYMENT header — exact format (base64 of what?)
6. Facilitator verifies and settles — what's the Kite facilitator's API? (/v2/settle endpoint)
7. Server returns 200 + resource

Critical for NegotiatorGrid: Can the server dynamically set the price in PAYMENT-REQUIRED based on a prior negotiation? Or is the price always static in the server config?
```

### Prompt 3.2 — A2A Protocol for Negotiation Transport
```
Using the negotiatorgrid-researcher skill with GitHub connector:

Read github.com/google/A2A — the Agent-to-Agent protocol (23.1k stars).

NegotiatorGrid uses A2A as the transport for negotiation messages. Extract:

1. The AgentCard specification — fields, discovery mechanism, storage options (blockchain/IPFS envisioned)
2. JSON-RPC 2.0 message format for A2A
3. Task lifecycle: how does a task progress through states?
4. SSE streaming — how to stream negotiation round updates in real-time
5. Can A2A carry custom message types? (NegotiatorGrid needs NEGOTIATE_REQUEST, COUNTER_OFFER, DEAL_CONTRACT)

Then read github.com/google-agentic-commerce/a2a-x402 (488 stars):
6. The payment-required → payment-submitted → payment-completed A2A message flow
7. The x402_a2a Python library — how does it bridge A2A with x402?
8. The Google Codelabs A2A codelab (codelabs.developers.google.com/intro-a2a-purchasing-concierge) — extract the multi-seller agent pattern

NegotiatorGrid inserts a negotiation phase between agent discovery and payment-required. Document exactly where in the a2a-x402 flow we inject the negotiation loop.
```

### Prompt 3.3 — x402 Client SDKs for Negotiated Payments
```
Using the negotiatorgrid-researcher skill:

Find ALL available x402 client libraries that NegotiatorGrid could use:

1. x402-foundation/x402 (5.9k stars) — @x402/express, @x402/fetch, Python pip install x402, Go package
   - Does the Python SDK handle the full 402→sign→retry cycle?
   - Can I inject a custom price validator? (Check: price ≤ negotiated_deal_price)

2. samthedataman/x402-sdk — fast-x402 FastAPI middleware + x402-langchain
   - 3-line FastAPI integration for the seller side
   - LangChain integration for autonomous payment decisions

3. Kite-specific x402 — the "gokite-aa" scheme
   - How does it differ from standard EVM x402?
   - What facilitator does Kite use? Is it Coinbase free-tier or custom (Pieverse)?
   - Facilitator address: 0x12343e649e6b2b2b77649DFAb88f103c02F3C78b

4. LangChain x402 integration (xpay.sh/x402-agent-frameworks/langchain)
5. OpenAI Agents SDK + x402 (agents.laso.finance/frameworks/openai-agents)

For each: install command, usage example, Kite compatibility, and whether it supports dynamic pricing from a negotiation outcome.
```

### Prompt 3.4 — x402 Edge Cases & Negotiation Failure Modes
```
Using the negotiatorgrid-researcher skill:

Research x402 failure modes AND NegotiatorGrid-specific edge cases:

Standard x402 failures:
1. Payment settles but server is down (idempotency)
2. Replay attack prevention — payment window mechanism
3. Facilitator slow/unreachable
4. Insufficient funds handling
5. Multiple payment options in accepts[]

NegotiatorGrid-specific failures:
6. What if negotiation succeeds but the seller changes the x402 price afterward? (deal_hash mismatch detection)
7. What if the buyer's AA Wallet constraint is stricter than the negotiated price? (constraint conflict)
8. What if both agents agree on a price but the facilitator rejects the payment? (settlement failure after negotiation)
9. What if an agent walks away mid-negotiation after learning the opponent's reservation price? (information leakage)
10. What if the same agent negotiates with multiple sellers simultaneously and commits to all of them? (double-commit prevention)

These directly impact demo reliability and judge Q&A. Build retry logic and fallbacks for each.
```

---

## Phase 4: MCP Dynamic Discovery (The "Wow Moment")

**Goal**: Implement the demo's killer feature — an agent that discovers an unknown x402-gated service at runtime via MCP, negotiates its price, and pays for it.
**Connectors ON**: GitHub
**Estimated prompts**: 3
**Time**: ~25 min

### Prompt 4.1 — MCP Protocol for Runtime Tool Discovery
```
Using the negotiatorgrid-researcher skill with GitHub connector:

Read the MCP specification at github.com/modelcontextprotocol/specification.

Extract what I need to build an MCP-aware negotiation agent:
1. The tools/list request/response format
2. The tools/call request/response format
3. Transport options: stdio vs SSE vs Streamable HTTP
4. notifications/tools/list_changed — server-push capability updates
5. The MCP Python SDK (mcp-python-sdk) — how to build a client
6. How to connect to a remote MCP server from Python (not just Claude Desktop)

Then research Docker's Dynamic MCP pattern:
7. The mcp-find / mcp-add / mcp-exec primordial tools (docker.com/blog/dynamic-mcps-stop-hardcoding-your-agents-world)
8. How does mcp-find search a registry? Can it filter by payment protocol (x402)?
9. Can I build a custom mcp-find that searches for x402-gated services AND checks ERC-8004 identity?

This is the "wow moment": the agent discovers a tool at runtime, verifies its identity on-chain, negotiates its price, pays via x402, and uses the result.
```

### Prompt 4.2 — x402 Discovery Catalog & MCP Registry
```
Using the negotiatorgrid-researcher skill:

Research the available MCP registries and x402 service catalogs:

1. x402 Discovery MCP server (mcpmarket.com/server/x402-discovery)
   - 250+ x402-payable services cataloged
   - Does it include uptime, latency, and trust scores?
   - Can NegotiatorGrid's seller agents register here?

2. Official MCP Registry at registry.modelcontextprotocol.io
   - How to register a new MCP server
   - What metadata is required?

3. Coinbase MCP x402 Server (docs.cdp.coinbase.com/x402/mcp-server)
   - Step-by-step x402+MCP bridge code
   - Can this be used as a template for NegotiatorGrid's MCP registration?

4. Dynamic FastMCP (Ragie open-source)
   - Runtime tool registration and deregistration

For the demo: I need to register 3-5 mock x402-gated services as MCP tools, then have the buyer agent discover and negotiate with one it's never seen before. Document how to set this up.
```

### Prompt 4.3 — MCP Security for Dynamic Discovery
```
Using the negotiatorgrid-researcher skill:

The MCP dynamic discovery "wow moment" introduces security risks. Research mitigations:

From arXiv:2503.23278 (MCP threat taxonomy):
1. Tool poisoning — a malicious MCP tool could manipulate the agent's behavior
2. Command injection via tool descriptions
3. Credential theft through tool parameters
4. RADE attacks (Remote Agent Deception via MCP)

From arXiv:2603.13417 (MCP production design patterns):
5. Identity propagation — how to verify the discovered tool's identity
6. Adaptive tool budgeting — spending limits per discovered tool
7. Structured error semantics — handling 402 errors from unknown tools

NegotiatorGrid's mitigations:
8. ERC-8004 trust gate: verify agent identity on-chain before negotiating
9. AA Wallet constraint: spending cap per tool, per session
10. Attestation audit trail: record every discovery → negotiation → payment on-chain

Document these as a "Security Model" section for the README. Judges will ask about security.
```

---

## Phase 5: Competitor & Prior Art Scan

**Goal**: Find what's already been built on Kite/x402/agent-negotiation so we can differentiate NegotiatorGrid.
**Connectors ON**: GitHub, Apify
**Estimated prompts**: 3
**Time**: ~20 min

### Prompt 5.1 — GitHub Topic Scan
```
Using the negotiatorgrid-competitor-scanner skill with GitHub connector:

Search GitHub for these topics and keyword combinations:
- topic:kite-ai, topic:gokite-ai, topic:x402
- "agent negotiation" + "x402"
- "bilateral negotiation" + blockchain
- "kite testnet" + hackathon
- "encode hackathon" + kite

Known prior art to check in detail:
- epappas/seipients-agent-to-agent — agent auction + blockchain escrow on SEI
- mashharuki/AgenticEthereum2025 — multi-agent DeFi on EigenLayer
- Any repos tagged "kite-ai" or "gokite" from 2025-2026

For each: Repo URL, what it does, Kite primitives used, quality level, last updated, whether it's a competing hackathon submission, and how NegotiatorGrid differentiates.
```

### Prompt 5.2 — ETHDenver & Encode Hackathon Winners
```
Using the demo-dx-evaluator skill:

Research past Kite-related hackathon winners to understand the bar:

Known winners (ETHDenver 2026):
1. Agentic Markets (3rd place) — agents discover, negotiate, pay across chains
   - YouTube: https://www.youtube.com/watch?v=5Ee31USfUsA
   - How did they implement negotiation? (Likely basic — NegotiatorGrid should exceed this)

2. Minority Report (2nd place) — LLM Council with VeriScore + Kite Escrow
   - YouTube: https://www.youtube.com/watch?v=EjiIdSY8pbQ
   - What Kite primitives did they use? Can we reuse their escrow pattern?

3. Kite Trace Platform (2nd place) — agents transacting via XMTP + x402 + ERC-8004
   - YouTube: https://www.youtube.com/watch?v=ya85SxqG_A4
   - How did they implement ERC-8004 identity?

For each: demo format, README quality, what made them stand out, what NegotiatorGrid does that they didn't.

Also search for Encode Club hackathon patterns at encodeclub.com.
```

### Prompt 5.3 — Academic Prior Art Gap Analysis
```
Using the negotiatorgrid-competitor-scanner skill:

Confirm NegotiatorGrid's unique position in the academic landscape:

1. The SoK paper (arXiv:2604.03733, April 2026) explicitly identifies multi-round price negotiation as an OPEN PROBLEM in agent payment systems. Quote the exact passage.

2. Search for any paper that combines ALL of:
   - Bilateral agent-to-agent negotiation
   - x402/HTTP 402 payment settlement
   - On-chain deal attestation
   - MCP dynamic service discovery
   
   (Expected: no paper combines all four — this is NegotiatorGrid's novel contribution)

3. Identify the 5 publishable research gaps NegotiatorGrid fills:
   a. Negotiation-to-payment atomicity (combining AgenticPay + A402)
   b. Reputation-conditioned negotiation strategy
   c. MCP as negotiation transport
   d. ERC-4337 spending limits dynamically set by negotiation outcomes
   e. Anti-collusion monitoring in repeated LLM-to-LLM agent markets

Document these gaps as "Novel Contributions" for the hackathon submission.
```

---

## Phase 6: Agent Architecture & Opponent Modeling

**Goal**: Decide the agent framework, implement opponent modeling, and design the full agent decision loop.
**Connectors ON**: GitHub
**Estimated prompts**: 4
**Time**: ~30 min

### Prompt 6.1 — Agent Framework Selection
```
Using the negotiatorgrid-researcher skill:

Compare agent framework options for NegotiatorGrid's 2-week hackathon build:

1. OpenAI Agents SDK (20.7k stars) + x402 tool
   - agents.laso.finance has working x402 integration pattern
   - Multi-agent handoffs between buyer/seller/mediator

2. LangGraph (28.7k stars) + custom negotiation nodes
   - Supply chain negotiation paper validates bilateral negotiation graph pattern
   - Dynamic node creation for multi-round offers

3. Google A2A + NegMAS hybrid
   - A2A for transport, NegMAS for negotiation logic
   - Most architecturally clean but most integration work

4. CrewAI (48.4k stars) + x402 tool
   - Built-in multi-agent patterns
   - Buyer/Seller/Mediator crews

5. Raw Python + google-agentic-commerce/a2a-x402 base
   - Fork the a2a-x402 repo and add negotiation
   - Least abstraction overhead, most control

For each:
- Setup complexity for 2-week hackathon
- x402/Kite compatibility (native or requires custom integration)
- NegMAS integration difficulty
- Demo impressiveness (real-time negotiation visualization)
- Risk level (dependency on external services)

Recommend one primary and one fallback.
```

### Prompt 6.2 — Opponent Modeling Architecture
```
Using the negotiatorgrid-researcher skill with GitHub connector:

Design NegotiatorGrid's opponent modeling system using these libraries:

1. NegMAS BOA framework — GSmithFrequencyModel:
   - Frequency-based opponent preference estimation
   - How to update the model after each counteroffer?

2. NegoLog AbstractOpponentModel:
   - Decoupled evaluation: test models independently of bidding
   - What's the interface contract?

3. Transformer-based opponent modeling (kushalchawla/opponent-modeling):
   - Infers opponent priority ordering from dialogue history
   - Is this relevant for structured bids or only natural language?

4. ASTRA stance classification:
   - Competitive, cooperative, or mixed stance detection
   - How to adjust concession rate based on detected stance?

Design a hybrid opponent model for NegotiatorGrid that:
- Tracks offer history (structured: price, SLA terms, round number)
- Estimates opponent's reservation price (Bayesian inference from counteroffers)
- Classifies opponent's stance (competitive vs cooperative)
- Adjusts concession strategy based on reputation score from ERC-8004
- Learns across sessions (opponent model persists in on-chain attestation data)
```

### Prompt 6.3 — Buyer Agent Decision Loop Implementation
```
Using the negotiatorgrid-researcher skill:

Based on the NegotiatorGrid architecture document, implement the buyer agent's 8-step decision loop:

1. DISCOVER → ERC-8004 registry query OR MCP dynamic discovery
2. EVALUATE → Read seller's AgentCard (reputation, pricing hint, deal history)
3. RANK → Score sellers by utility = w1*price + w2*reputation + w3*sla_quality + w4*history
4. NEGOTIATE → Open A2A channel, execute alternating-offers with NegMAS BOA framework
5. COMMIT → Sign DealContract, update AA Wallet constraint (valueLimit = agreed_price)
6. EXECUTE → Send x402 request, wallet auto-signs if price matches deal
7. VERIFY → Check SLA compliance (latency, response quality)
8. LEARN → Update opponent model, attest result on-chain

For each step:
- Python function signature
- Key library used (NegMAS, x402 SDK, A2A, web3.py)
- Expected latency
- Failure mode and fallback
- What gets attested on-chain

Produce a skeleton buyer_agent.py with all 8 steps as async methods.
```

### Prompt 6.4 — Seller Agent & Mediator Design
```
Using the negotiatorgrid-researcher skill:

Design the seller agent and optional mediator agent:

Seller Agent:
1. PUBLISH → Register AgentCard on ERC-8004 with capabilities, pricing hint, x402 endpoint
2. LISTEN → Wait for NEGOTIATE_REQUEST on A2A bus
3. EVALUATE BUYER → Check buyer's DID, reputation, deal history
4. SET STRATEGY → Adjust based on demand: high demand → concede slowly, low demand → concede faster
5. NEGOTIATE → Respond with counteroffers using time-dependent concession
6. COMMIT → Sign DealContract, update x402 middleware to serve at negotiated price
7. SERVE → Process x402 request, deliver result, collect payment
8. ATTEST → Record outcome on-chain, update reputation

Mediator Agent (optional, for the wow factor):
- Could MCP enable a mediator agent that observes negotiations and suggests fair prices?
- The Negotiation-MultiAgent repo (hari7261) has a buyer/seller/mediator pattern with Flask UI
- What role does a mediator play in NegotiatorGrid's protocol?

For the seller: How does the x402 middleware dynamically set the price per-buyer based on a prior negotiation? Is this supported by fast-x402 or does it need a custom middleware?
```

---

## Phase 7: Infrastructure, Dashboard & Deployment

**Goal**: Lock down the deployment stack, build the real-time dashboard, and set up CI/CD for demo day.
**Connectors ON**: GitHub
**Estimated prompts**: 3
**Time**: ~25 min

### Prompt 7.1 — Smart Contract Deployment on Kite
```
Using the negotiatorgrid-researcher skill:

NegotiatorGrid needs three contracts on Kite testnet:

1. DealRecord Attestation Contract:
   - Stores: deal_id, buyer DID, seller DID, negotiation rounds, opening/final prices, SLA terms, x402 tx hash, reputation updates
   - Schema from the architecture document
   
2. ERC-8004 Agent Identity Registration:
   - Register buyer and seller agents on the Identity Registry
   - Set up Reputation Registry entries
   - The EIP is live on mainnet (Jan 29, 2026) — extract contract interfaces from the EIP

3. AA Wallet with Dynamic Spending Rules:
   - addSessionKeyRule(valueLimit = negotiated_price)
   - Must support runtime updates after each negotiation

From docs.gokite.ai, extract:
- Complete Hardhat setup for Kite testnet (Chain ID 2368, RPC, config)
- Contract verification on KiteScan — is there a verify plugin?
- Gas estimation for deploy + runtime attestation writes
- Faucet limits at faucet.gokite.ai
- Does Kite support Foundry or only Hardhat?
```

### Prompt 7.2 — Real-Time Dashboard & Negotiation Visualization
```
Using the negotiatorgrid-researcher skill:

Design the NegotiatorGrid dashboard that judges will see during the demo:

1. shadcn/ui web3 blocks (shadcn.io/blocks/web3-activity-feed, updated 2026-03-24):
   - Real-time activity feed component
   - Transaction history with expandable rows
   - Wallet analytics dashboard
   - How to wire these to NegotiatorGrid's negotiation event stream?

2. Real-time negotiation visualization:
   - Price convergence chart (Recharts or d3) — live chart showing offers narrowing
   - Negotiation round timeline (offer → counter → accept flow)
   - Agent decision log with reasoning (LLM chain-of-thought)
   
3. On-chain data display:
   - wagmi + viem for Kite chain connection (custom EVM chain config)
   - Live attestation feed from KiteScan
   - Wallet balance (AA wallet USDC balance)
   - Deal history table with tx hash links

4. WebSocket architecture:
   - Socket.io or native WebSocket for streaming negotiation events from Python backend to Next.js frontend
   - ag2ai/realtime-agent-over-websockets as reference pattern

5. MCP Discovery Panel:
   - Visual display of available MCP tools (x402-gated services)
   - Real-time discovery animation when agent finds a new tool

Produce a component inventory with import paths and a page layout wireframe.
```

### Prompt 7.3 — Vercel Deployment + Production Setup
```
Using the negotiatorgrid-researcher skill:

Plan the production deployment for demo day:

1. Frontend: Next.js on Vercel
   - wagmi + viem with Kite chain config
   - Issues with crypto/ethers.js in edge runtime?
   
2. Backend: Python (FastAPI) for negotiation engine + x402 settlement
   - Where to host? (Railway, Render, AWS Lambda, self-hosted)
   - WebSocket support for real-time negotiation streaming
   
3. Smart contracts: Kite Ozone testnet
   - Pre-deployed contract addresses
   - Hardhat deploy scripts in CI

4. Environment variables:
   - KITE_RPC_URL, KITEPASS_API_KEY, PRIVATE_KEY (AA wallet)
   - OPENAI_API_KEY or ANTHROPIC_API_KEY
   - X402_FACILITATOR_URL

5. Docker setup as fallback for "one command run"
6. GitHub Actions CI — smoke test on every push

Search for any x402 + Vercel examples or templates.
```

---

## Phase 8: Synthesis & Sprint Planning

**Goal**: Consolidate all research into actionable build plan. Store artifacts.
**Estimated prompts**: 3
**Time**: ~20 min

### Prompt 8.1 — Architecture Decision Record (NegotiatorGrid-Specific)
```
Using the negotiatorgrid-researcher skill:

Write an Architecture Decision Record (ADR) for NegotiatorGrid based on Phases 1-7.

Sections:
1. **Decision**: NegotiatorGrid — a pre-x402 bilateral negotiation layer for agent-to-agent price bargaining on Kite
2. **Context**: Novel Track hackathon, $10K prize, 2-week build, 1 builder. SoK paper (2604.03733) identifies price negotiation as an open problem.
3. **Architecture**: Component diagram:
   - Negotiation Engine: NegMAS BOA framework + LLM reasoning + game-theoretic validation
   - Payment Layer: x402 SDK + AA Wallet constraints + Kite Facilitator
   - Communication: A2A protocol for negotiation transport, MCP for dynamic discovery
   - Identity: ERC-8004 agent identity + reputation registry
   - Chain Layer: DealRecord attestation contract on Kite testnet
   - UI: Next.js dashboard with real-time negotiation visualization
4. **Key Libraries**:
   - NegMAS (pip install negmas) — negotiation protocol + opponent modeling
   - x402 (pip install x402) — payment settlement
   - google-agentic-commerce/a2a-x402 — A2A+x402 bridge (FORK THIS AS BASE)
   - gambit (pip install gambit) — Nash equilibrium computation
   - fast-x402 — seller-side FastAPI middleware
5. **Alternatives considered**: Raw OpenAI Agents, CrewAI, LangGraph — why a2a-x402 fork is better
6. **Risks**: Top 5 risks with mitigation
7. **Open questions**: Things still unresolved
```

### Prompt 8.2 — Sprint Backlog (NegotiatorGrid Build)
```
Using the negotiatorgrid-researcher skill:

Create a sprint backlog for a 2-week build (1 builder, ~6 hrs/day). Deadline: April 26, 2026.

Structure as:
- **Week 1 (P0 — Foundation & Negotiation Engine)**
  - Day 1-2: Fork a2a-x402, set up Kite testnet, KitePass, faucet, deploy ERC-8004 identities
  - Day 3-4: Implement NegMAS-based negotiation engine (SAO protocol, BOA framework, opponent model)
  - Day 5-6: Wire negotiation output to x402 settlement, implement AA Wallet constraint updates
  - Day 7: First end-to-end flow: discover → negotiate → lock price → pay → verify → attest

- **Week 2 (P1 — MCP Wow Moment, Dashboard & Polish)**
  - Day 8-9: MCP dynamic discovery integration (mcp-find → ERC-8004 verify → negotiate → pay)
  - Day 10-11: Dashboard UI (price convergence chart, negotiation timeline, attestation feed, wallet display)
  - Day 12: Demo rehearsal, video recording, README draft
  - Day 13: Final polish, documentation, security model, academic narrative
  - Day 14: Buffer / bug fixes / submission

Each task: estimated hours, dependency, definition of done, risk flag.
```

### Prompt 8.3 — Demo Script & Judge Q&A (with Academic Backing)
```
Using the demo-dx-evaluator skill:

Write the final NegotiatorGrid demo script (5 minutes) and judge Q&A prep.

Demo script format:
| Timestamp | Screen | Narration | Judge Criterion Hit | Backup Plan |

Key moments:
- [0:00-0:30] Context slide: "Price negotiation is an open problem" (cite SoK paper)
- [0:30-1:30] Two known agents negotiate: show price convergence in real-time
- [1:30-2:30] THE WOW MOMENT: Agent discovers unknown API via MCP → verifies identity → negotiates price down → pays → uses data
- [2:30-3:30] On-chain attestation: judges click tx hash, see full DealRecord
- [3:30-4:30] The "aha": agent REFUSES to pay a seller who changed price after negotiation (deal_hash mismatch)
- [4:30-5:00] Closing: academic references, future work (cite A402 atomic channels)

Judge Q&A (10 answers with academic citations):
1. "How is this different from Agentic Markets?" → They had no multi-round negotiation or opponent modeling
2. "What happens if the agent overspends?" → AA Wallet constraint + Agent Contracts paper (2601.08815)
3. "How do you verify attestations?" → On-chain immutability + Kite's PoAI
4. "Could this work on mainnet?" → Yes, x402 + ERC-8004 are live on mainnet (Jan 2026)
5. "What would you build next?" → A402 atomic service channels (2603.01179) for payment-service atomicity
6. "Why Kite instead of Base/Solana?" → SPACE framework + native x402 + gasless + AA wallets + ERC-8004
7. "MCP security risks?" → Cite 38-category threat taxonomy (2503.23278), explain ERC-8004 trust gate + AA spending caps
8. "Latency of full payment cycle?" → ~4 seconds (negotiation ~2s + x402 settlement ~1s + attestation ~1s)
9. "Academic basis?" → SoK (2604.03733), Agent Economy (2602.14219), AgenticPay (2602.06008)
10. "Why game theory + LLM hybrid?" → Game-Theoretic LLM paper (2411.05990) shows Nash-guided offers outperform pure LLM by 23%
```

---

## Output Tracking Checklist

After completing all phases, you should have these artifacts:

| # | Artifact | Phase | Description |
|---|----------|-------|-------------|
| 1 | Kite architecture notes (negotiation lens) | 1.1 | How Kite primitives map to NegotiatorGrid |
| 2 | KiteSDK API inventory | 1.2 | Agent builder workflow for NegotiatorGrid |
| 3 | Kite MCP server tool inventory | 1.3 | MCP integration for dynamic discovery |
| 4 | AA SDK / Gasless / Spending Rules | 1.4 | Dynamic constraint programming |
| 5 | gokite-ai repo inventory table | 1.5 | All repos with NegotiatorGrid relevance ratings |
| 6 | NegMAS framework guide | 2.1 | SAO protocol, BOA framework, opponent models |
| 7 | NegoLog opponent modeling architecture | 2.2 | AbstractOpponentModel, EstimatedPreference |
| 8 | LLM negotiation benchmarks | 2.3 | AgenticPay, GPT-Bargaining, PACT results |
| 9 | FIPA-CNP → A2A message schema | 2.4 | NegotiatorGrid wire format design |
| 10 | Game-theoretic pricing engine design | 2.5 | Nash bargaining + Rubinstein + LLM hybrid |
| 11 | LLM negotiation papers | 2.5.1 | 6+ papers with implementation takeaways |
| 12 | A2A payment papers | 2.5.2 | SoK, A402, Agent Economy, security papers |
| 13 | Trust & mechanism design papers | 2.5.3 | Inter-Agent Trust, Agent Contracts, Insured Agents |
| 14 | MCP security + AA identity papers | 2.5.4 | Threat taxonomy, production patterns, Binding Agent ID |
| 15 | Academic narrative for judges | 2.5.5 | 3-paragraph narrative + 12 references + Q&A ammo |
| 16 | x402 post-negotiation settlement flow | 3.1 | Modified x402 flow with deal_hash |
| 17 | A2A negotiation transport design | 3.2 | Custom message types over A2A JSON-RPC |
| 18 | x402 client library comparison | 3.3 | SDK comparison for negotiated payments |
| 19 | Edge case & failure mode guide | 3.4 | 10 failure modes with mitigations |
| 20 | MCP dynamic discovery implementation | 4.1 | mcp-find + ERC-8004 trust gate |
| 21 | x402 Discovery catalog setup | 4.2 | Mock service registry for demo |
| 22 | MCP security model | 4.3 | 10 mitigations for README |
| 23 | Competitor project table | 5.1 | GitHub scan results |
| 24 | Hackathon winner analysis | 5.2 | ETHDenver patterns, bar for winning |
| 25 | Novel contribution gap analysis | 5.3 | 5 publishable research gaps |
| 26 | Agent framework decision | 6.1 | Primary + fallback recommendation |
| 27 | Opponent modeling architecture | 6.2 | Hybrid model design |
| 28 | Buyer agent skeleton (buyer_agent.py) | 6.3 | 8-step decision loop implementation |
| 29 | Seller agent + mediator design | 6.4 | Seller loop + optional mediator |
| 30 | Smart contract specs + Hardhat config | 7.1 | DealRecord, ERC-8004, AA wallet |
| 31 | Dashboard component inventory | 7.2 | UI wireframe + component list |
| 32 | Deploy architecture | 7.3 | Vercel + FastAPI + Kite testnet |
| 33 | Architecture Decision Record | 8.1 | Full ADR for NegotiatorGrid |
| 34 | Sprint backlog | 8.2 | 14-day build plan with tasks |
| 35 | Demo script + Judge Q&A | 8.3 | 5-min script + 10 Q&A with citations |

---

## Key GitHub Repos (Quick Reference)

### Critical (Must Fork/Use)
| Repo | Stars | What For |
|------|-------|----------|
| [x402-foundation/x402](https://github.com/x402-foundation/x402) | 5.9k | x402 SDK (TypeScript/Python/Go) — payment settlement |
| [google-agentic-commerce/a2a-x402](https://github.com/google-agentic-commerce/a2a-x402) | 488 | **FORK AS BASE** — A2A + x402 bridge in Python |
| [yasserfarouk/negmas](https://github.com/yasserfarouk/negmas) | 85 | Negotiation engine: SAO protocol, BOA framework, opponent models |
| [gambitproject/gambit](https://github.com/gambitproject/gambit) | 435 | Nash equilibrium computation |
| [ERC-8004 EIP](https://eips.ethereum.org/EIPS/eip-8004) | — | Agent identity standard (live on mainnet Jan 2026) |

### High Priority (Reference/Adapt)
| Repo | Stars | What For |
|------|-------|----------|
| [aniltrue/NegoLog](https://github.com/aniltrue/NegoLog) | 7 | IJCAI 2024 — opponent model evaluation framework |
| [FranxYao/GPT-Bargaining](https://github.com/FranxYao/GPT-Bargaining) | 208 | LLM buyer/seller/critic self-play negotiation |
| [lechmazur/pact](https://github.com/lechmazur/pact) | 29 | 5,000+ LLM bargaining games benchmark |
| [samthedataman/x402-sdk](https://github.com/samthedataman/x402-sdk) | — | fast-x402 FastAPI middleware + LangChain integration |
| [ammonhaggerty/ANEX](https://github.com/ammonhaggerty/ANEX) | 2 | FIPA-Contract-Net message schema |
| [hari7261/Negotiation-MultiAgent](https://github.com/hari7261/Negotiation-MultiAgent) | — | Buyer/Seller/Mediator with Flask UI |
| [autoneg/anl](https://github.com/autoneg/anl) | — | ANAC competition agents (state-of-the-art strategies) |
| [SafeRL-Lab/AgenticPay](https://github.com/SafeRL-Lab/AgenticPay) | — | 110+ negotiation task benchmark |
| [google/A2A](https://github.com/google/A2A) | 23.1k | A2A protocol spec |
| [decentralized-identity/veramo](https://github.com/decentralized-identity/veramo) | 534 | DID resolution on EVM chains |

### Medium Priority (Reference Patterns)
| Repo | Stars | What For |
|------|-------|----------|
| [Wenyueh/game_theory](https://github.com/Wenyueh/game_theory) | — | Nash equilibrium-guided LLM workflows |
| [mcpdotdirect/evm-mcp-server](https://github.com/mcpdotdirect/evm-mcp-server) | ~200 | EVM MCP tools for agent blockchain interaction |
| [ag2ai/realtime-agent-over-websockets](https://github.com/ag2ai/realtime-agent-over-websockets) | 10 | FastAPI WebSocket agent reference |
| [epappas/seipients-agent-to-agent](https://github.com/epappas/seipients-agent-to-agent) | 2 | Closest prior art: agent auction + blockchain escrow |
| [velochy/rl-bargaining](https://github.com/velochy/rl-bargaining) | ~5 | RL-based Rubinstein bargaining environment |
| [coinbase/x402](https://github.com/coinbase/x402) | 41 | Coinbase fork of x402 (Python SDK) |

---

## Key Academic Papers (Quick Reference)

### Must-Cite (Judge Narrative)
| Paper | ArXiv | Date | Why |
|-------|-------|------|-----|
| SoK: Blockchain A2A Payments | 2604.03733 | Apr 2026 | Identifies price negotiation as open problem — NegotiatorGrid fills it |
| AgenticPay | 2602.06008 | Feb 2026 | Directly validates LLM bilateral negotiation concept |
| The Agent Economy | 2602.14219 | Feb 2026 | Five-layer architecture — NegotiatorGrid spans Economic & Settlement |
| A402: Atomic Service Channels | 2603.01179 | Mar 2026 | Fixes x402 atomicity gap — future work for NegotiatorGrid |
| Inter-Agent Trust Models | 2511.03434 | Nov 2025 | Recommends Proof+Stake — NegotiatorGrid's trust model |

### Should-Cite (Implementation Guidance)
| Paper | ArXiv | Date | Why |
|-------|-------|------|-----|
| MCP Security Threats | 2503.23278 | Mar 2025 | 38-category threat taxonomy for dynamic discovery |
| MCP Production Patterns | 2603.13417 | Mar 2026 | Identity propagation, tool budgeting, error semantics |
| Agent Contracts Framework | 2601.08815 | Jan 2026 | Formal model for resource-bounded agents |
| Binding Agent ID | 2512.17538 | Dec 2025 | zkVM agent authentication + ERC-4337 |
| Game-Theoretic LLM | 2411.05990 | Nov 2024 | Nash-guided offers outperform pure LLM |
| Red-Teaming Agent Payments | 2601.22569 | Jan 2026 | Security attacks on agent payment systems |
| Authenticated Delegation | 2501.09674 | Jan 2025 | OAuth 2.0 extension with Agent-ID Tokens |

---

## Estimated Total Time: ~4.5 hours

| Phase | Prompts | Est. Time | Focus Area |
|-------|---------|-----------|------------|
| 1: Kite Protocol Deep Dive | 5 | 45 min | Settlement infrastructure |
| 2: Negotiation Engine Deep Dive | 5 | 40 min | Core protocol implementation |
| 2.5: Academic Literature | 5 | 35 min | Judge narrative + implementation guidance |
| 3: x402 + A2A Integration | 4 | 30 min | Payment settlement layer |
| 4: MCP Dynamic Discovery | 3 | 25 min | The "wow moment" |
| 5: Competitor Scan | 3 | 20 min | Differentiation |
| 6: Agent Architecture | 4 | 30 min | Decision loop + opponent modeling |
| 7: Infra & Deploy | 3 | 25 min | Dashboard, contracts, deployment |
| 8: Synthesis | 3 | 20 min | ADR, sprint, demo script |
| **Total** | **35** | **~4.5 hrs** | |

---

## How This Plan Differs From Research Plan (2)

| Dimension | Research Plan (2) | This Plan (Final) |
|-----------|-------------------|-------------------|
| **Track** | General (all 3 tracks) | Novel Track only |
| **Focus** | Kite overview + ACP commerce + trading | Bilateral negotiation + x402 settlement |
| **Phase 2** | x402 payment mechanics (generic) | NegMAS, NegoLog, opponent modeling, game theory |
| **Phase 3** | ACP + Agentic Commerce | x402 + A2A integration for negotiated payments |
| **Phase 4** | Competitor scan | MCP Dynamic Discovery ("wow moment") |
| **Phase 5** | Agent architecture (generic) | Competitor scan (moved) |
| **Phase 6** | Infrastructure | Agent architecture + opponent modeling |
| **New Phase** | — | Phase 2: Negotiation Engine Deep Dive (5 prompts) |
| **Academic** | 4 categories of papers | 6 categories including negotiation + game theory papers |
| **Key repos** | gokite-ai repos + x402 | NegMAS, NegoLog, GPT-Bargaining, a2a-x402, gambit, AgenticPay |
| **Papers cited** | ~15 | 37+ across 6 categories |
| **Artifacts** | 21 | 35 |
| **Sprint plan** | Generic 2-week build | NegotiatorGrid-specific: negotiation engine → MCP wow → dashboard |
| **Exclusions** | None | Trading, portfolio management, standard retail commerce |

---

Start Phase 1 now. Each prompt is self-contained — if Perplexity hits a dead end on one, skip it and move to the next. The skill frontmatter ensures consistent output formatting across all prompts.
