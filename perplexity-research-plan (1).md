# Kite AI × Encode Hackathon — Perplexity Computer Research Plan

## Part 1: Skills to Inject into Your Perplexity Prompt Feed

Add these as system-level context blocks at the start of each Perplexity session. They constrain outputs to be hackathon-useful rather than generic.

---

### Skill 1: `kite-chain-investigator`

```yaml
---
name: kite-chain-investigator
description: >
  Research Kite chain infrastructure: contracts, DEX pools, LayerZero endpoints,
  stablecoin bridges, attestation patterns, and account abstraction support.
  Always distinguish verified on-chain facts from inferred/analogous patterns.
  Output structured findings with source URLs, verification status, and
  confidence level (confirmed / likely / speculative).
---
```

**Instructions for Perplexity:**
1. When researching Kite chain, always search for official docs first (kite.network, any GitHub org).
2. For every contract address or ABI found, mark as `UNVERIFIED` unless linked from official docs.
3. Separate facts into: (a) confirmed from primary source, (b) inferred from analogous L2/L3 patterns, (c) speculative.
4. Output a structured JSON-like block per finding:
   ```
   FINDING: <topic>
   SOURCE: <url>
   STATUS: confirmed | inferred | speculative
   RELEVANCE: P0 | P1 | P2
   NEXT_STEP: <what to verify or build>
   ```

---

### Skill 2: `agentic-trading-architecture`

```yaml
---
name: agentic-trading-architecture
description: >
  Design autonomous trading agent architectures for DeFi.
  Covers: signal generation, risk gates, execution flow, state management,
  attestation/audit logging, and cross-chain messaging.
  Bias toward production patterns (idempotency, circuit breakers, position limits)
  over academic models.
---
```

**Instructions for Perplexity:**
1. When researching trading bot architectures, prioritize open-source repos with actual execution code over blog posts.
2. For every architecture pattern found, extract: tech stack, risk controls present, state management approach.
3. Flag any pattern that assumes CEX APIs — we need DEX/on-chain execution.
4. For cross-chain patterns, always note trust assumptions and failure modes.

---

### Skill 3: `hackathon-scope-enforcer`

```yaml
---
name: hackathon-scope-enforcer
description: >
  Constrain all research outputs to hackathon-viable scope (5-7 day build).
  For every feature or integration found, classify as:
  REAL (can demo live), MOCK (simulated with realistic data), or CUT (out of scope).
  Bias toward impressive-but-honest demos over ambitious-but-broken ones.
---
```

**Instructions for Perplexity:**
1. After gathering research on any topic, append a `HACKATHON VIABILITY` assessment.
2. Flag anything requiring: mainnet funds > $50, private API keys with approval wait > 24h, or infrastructure setup > 2h.
3. For every "real" component, estimate setup time. For every "mock," describe what the mock looks like to judges.

---

### Skill 4: `attestation-designer`

```yaml
---
name: attestation-designer
description: >
  Design on-chain attestation schemas for auditability of AI agent decisions.
  Covers: what to hash, what to store on-chain vs off-chain, gas cost tradeoffs,
  schema versioning, and query patterns for dashboards.
  Optimize for judge-visible proof that the agent acted autonomously with guardrails.
---
```

**Instructions for Perplexity:**
1. Research EAS (Ethereum Attestation Service) patterns and any Kite-specific attestation infra.
2. For trading attestations specifically, find examples of: trade intent records, risk check logs, execution receipts.
3. Always estimate gas cost per attestation and suggest batching strategies if needed.

---

### Skill 5: `arxiv-scout`

```yaml
---
name: arxiv-scout
description: >
  Search arxiv.org for papers relevant to autonomous DeFi trading agents,
  reputation systems, cross-chain architectures, and on-chain attestation.
  Extract structured summaries with arxiv IDs, core techniques,
  implementation feasibility, and links to code repos.
  Bias toward papers from 2023-2026 with practical implementations.
---
```

**Instructions for Perplexity:**
1. Always include arxiv ID and date so findings are traceable.
2. For every technique found, classify as: IMPLEMENTABLE (can build in hackathon), ADAPTABLE (simplified version viable), or CITE-ONLY (reference in README but don't build).
3. Flag any paper with a linked GitHub repo — those are highest priority.
4. When a paper describes a system architecture, extract it as a component diagram or pipeline description.

---

## Part 2: Connector Selection Map

### Tier 1 — Use Every Session (Core Research)

| Connector | Purpose | What to Extract |
|-----------|---------|-----------------|
| **GitHub** | Find trading bot repos, Kite SDK examples, DEX integration code, LayerZero examples | Repo URLs, code patterns, ABIs, deployment scripts |
| **Apify** | Scrape Kite docs, protocol pages, DEX UI pages for contract addresses | Structured data from pages that Perplexity can't natively deep-read |
| **CoinMarketCap** | Kite token metadata, pairs available, market structure context | Token addresses, pair liquidity, chain IDs |

### Tier 2 — Use for Specific Phases

| Connector | Phase | Purpose |
|-----------|-------|---------|
| **Finnhub** | Phase 2 (Signal) | API pattern reference for market data feeds; map to on-chain oracle equivalents |
| **Alpaca** | Phase 2 (Execution) | Order lifecycle patterns (limit/market/stop) to model DEX swap flows with guardrails |
| **Supabase** | Phase 3 (Architecture) | Schema patterns for trade logs, portfolio state, attestation pointers |
| **Pinecone / Qdrant / Airweave** | Phase 3 (Architecture) | Agent memory patterns — storing reasoning traces for "why did the agent do X". Airweave is specifically built for agent memory and may have tighter patterns than raw vector stores |
| **Cloudflare** | Phase 4 (Deploy) | Workers/Durable Objects for always-on agent; edge execution patterns |
| **Discord Bot** | Phase 1 & 5 (Kite Research) | Search Kite's Discord for contract addresses, dev announcements, testnet faucet links, and answers to integration questions other devs have asked |
| **Telegram** | Phase 1 & 5 (Kite Research) | Same as Discord — Kite likely has a Telegram community with dev channels; search for RPC endpoints, bridge status, DEX launch announcements |
| **GitLab** | Phase 1 (Kite Research) | Some chains host contracts/SDKs on GitLab instead of GitHub; check if Kite has a GitLab presence |
| **PDF.co** | Phase 1 (Kite Research) | Parse Kite whitepapers, technical specs, or tokenomics PDFs that Perplexity can't natively deep-read |

### Tier 3 — Use Only If Needed

| Connector | When |
|-----------|------|
| **Stripe** | Only if modeling agent budget/spend-limit patterns (idempotency keys → tx nonces) |
| **Datadog** | Only if you want monitoring/alerting patterns for the agent's health (nice-to-have for "production credibility") |
| **Slack** | Only if Kite has a public Slack workspace with dev channels |
| **Notion / Linear / Asana** | Only for your own project management during build week, not research |
| **Bitget / BingX** | Only for CEX API pattern comparison (not execution) |

### Skip Entirely (confirmed irrelevant to research phase)
Canva, Vimeo, Mux, Square, Bitly, Dub, Monday, Jira, Taiga, Planner, Dart, Confluence, Coda, Google Slides, Google Docs, Firebase Admin, MongoDB, Snowflake, Databricks, Azure SQL, Ollama, Turso, Prisma Postgres, PostgreSQL, HubSpot, Salesforce, Shopify, Mailchimp, Freshservice, RingCentral, Wix, Bluesky, Mastodon, Spotify, Yelp, Medical Records, Wearables, BioRender, sevDesk, Personio, Rippling, Cal.com, Mapbox, and all other CRM/HR/marketing/scheduling connectors. Use during build if needed, not during research.

---

## Part 3: Phased Prompt Plan

Each phase is a Perplexity Computer session. Run them in order. Each prompt is copy-paste ready.

---

### PHASE 1: Kite Chain Foundation (Est. 30-45 min)

**Goal:** Map the Kite chain landscape — what exists, what's deployed, what docs say.

**Connectors to enable:** GitHub, GitLab, Apify, CoinMarketCap, Discord Bot, Telegram, PDF.co

---

**Prompt 1.1 — Kite Chain Overview**
```
Research the Kite blockchain (also called Kite chain, Kite AI chain, or kite.network).

Find and document:
1. Chain ID, RPC endpoints (mainnet and testnet)
2. Native token, gas token, and any wrapped/bridged stablecoins (especially USDC.e)
3. Official documentation URLs
4. GitHub organization(s) and key repos
5. What EVM version / L2 stack it's built on (OP Stack, Arbitrum Orbit, ZK, custom?)
6. Any deployed DEX contracts (Algebra, Uniswap v3 forks, or custom AMM)
7. LayerZero integration status — are there OApp/OFT deployments?
8. Block explorer URL
9. Any official SDKs or starter templates for building on Kite

For every contract address or endpoint found, mark as CONFIRMED (linked from official docs) or UNVERIFIED.

Output as a structured reference sheet I can use for the rest of this project.
```

---

**Prompt 1.2 — Kite DEX & DeFi Landscape**
```
Continuing Kite chain research. Search GitHub and any Kite documentation for:

1. DEX contracts deployed on Kite — specifically look for:
   - Algebra-style concentrated liquidity pools
   - Router/SwapRouter contracts
   - Factory contracts
   - Any yield/lending protocols (Lucid or similar)
2. For each contract found: address, verified status, ABI availability
3. Available trading pairs and approximate liquidity (check block explorer if accessible)
4. Fee structures (swap fees, protocol fees)
5. Any oracle infrastructure (Chainlink, Pyth, custom) deployed on Kite

Also search CoinMarketCap for any Kite-related tokens to understand market structure.

Mark everything CONFIRMED vs UNVERIFIED. If you can't find DEX contracts, document that gap — it affects our architecture.
```

---

**Prompt 1.3 — Kite Attestation & Account Abstraction**
```
Research attestation and account abstraction infrastructure on Kite chain:

1. Is EAS (Ethereum Attestation Service) or any attestation contract deployed on Kite?
   - If yes: contract address, schema registry address, supported schema types
   - If no: what's the closest pattern? Direct event logging? Custom contract?
2. Account abstraction support:
   - ERC-4337 EntryPoint deployed?
   - Any paymaster contracts for gasless/sponsored transactions?
   - Bundler endpoints?
3. Any Kite-specific attestation or proof mechanisms mentioned in their docs
4. Gas costs on Kite (approximate cost per simple tx, per contract call)

This is critical for the judging criteria around "auditability" — I need to know exactly what infrastructure exists for recording agent decisions on-chain.
```

---

**Prompt 1.4 — LayerZero on Kite**
```
Research LayerZero integration with Kite chain:

1. Is Kite listed as a supported chain on LayerZero's official docs (layerzero.network)?
2. LayerZero endpoint contract address on Kite (v1 and/or v2)
3. Any OFT (Omnichain Fungible Token) or OApp deployments on Kite
4. Connected chains — which chains can message to/from Kite via LayerZero?
5. Message delivery time estimates (Kite ↔ other chains)
6. Security model: DVN configuration, executor setup
7. Any known bridge contracts using LayerZero on Kite

If LayerZero isn't live on Kite, document that — it determines whether cross-chain arb is viable or needs to be mocked.
```

---

**Prompt 1.5 — Kite Community Channels**
```
Find Kite AI / Kite chain community channels:
1. Discord server — search for invite links, then look for channels like #dev, #builders, #contracts, #testnet
2. Telegram groups — official dev or announcements channels
3. Any developer forum, blog, or changelog

In each channel, search for:
- Testnet faucet links
- RPC endpoint announcements
- Contract deployment announcements (DEX, bridge, attestation)
- SDK or starter template links
- Known issues or gotchas other devs have hit

This is my most reliable source for ground-truth info that may not be in docs yet.
Output every useful link and quote you find.
```

---

### PHASE 2: Trading Agent Patterns (Est. 45-60 min)

**Goal:** Gather architecture patterns, risk frameworks, and execution flows from real trading bots.

**Connectors to enable:** GitHub, Finnhub, Alpaca

---

**Prompt 2.1 — DeFi Trading Bot Architectures**
```
Search GitHub for open-source DeFi trading bots and autonomous agents. I need production-quality examples, not tutorials.

Find 5-10 repos that demonstrate:
1. On-chain DEX execution (Uniswap, Algebra, or any AMM)
2. Risk management (position limits, drawdown stops, daily loss caps)
3. Signal generation (could be simple: moving averages, spread monitoring, funding rates)
4. State management (how they track positions, PnL, pending orders)
5. Error handling for failed transactions, reverts, slippage

For each repo, extract:
- Tech stack (Python/TypeScript/Rust, which libraries)
- Architecture pattern (monolith, microservices, event-driven)
- How they handle private keys / signing
- Any attestation or logging of decisions
- Stars, last commit date (is it maintained?)

Prioritize repos with >100 stars and recent activity. Skip MEV bots — I want trading agents, not sandwich attacks.
```

---

**Prompt 2.2 — Risk Framework for Autonomous Agents**
```
Research risk management frameworks for autonomous DeFi trading agents:

1. What are standard risk controls for an agent that executes trades without human approval?
   - Position size limits (% of portfolio per trade)
   - Daily/weekly loss limits (circuit breakers)
   - Slippage tolerance and MEV protection
   - Concentration limits (max % in single asset/pool)
   - Drawdown-based pause mechanisms
2. How do existing trading systems implement these? Find concrete examples (code or detailed specs).
3. What does "reputation-aware capital delegation" look like?
   - Research any DeFi protocols where agents have reputation scores
   - How is capital delegated to agents based on track record?
4. Stablecoin-first settlement patterns — what does it mean practically?
   - Always settle back to USDC after trades?
   - Use USDC as accounting unit for PnL?

I need this to be implementable in a 5-day hackathon. Flag what's realistic vs aspirational.
```

---

**Prompt 2.3 — Market Data for On-Chain Trading**
```
Research how to get market data for on-chain DeFi trading on EVM chains:

1. On-chain price feeds:
   - Chainlink / Pyth / other oracle patterns
   - Reading pool reserves or sqrtPriceX96 from AMM contracts directly
   - TWAP calculation from on-chain data
2. Off-chain data that feeds on-chain decisions:
   - Coingecko / CoinMarketCap API for reference prices
   - DEX aggregator APIs (1inch, Paraswap, 0x) — do any support Kite?
   - Subgraph / indexer queries for historical swaps and volume
3. For a hackathon demo, what's the simplest reliable price feed I can use?
   - Ideally: one API call or one contract read that gives me current price of major pairs on Kite
4. Finnhub API patterns — how does their market data API work? I want to understand the pattern (websocket vs REST, rate limits, auth) to map it onto on-chain equivalents.

Output a comparison table: data source, latency, cost, reliability, hackathon-viable (yes/no).
```

---

**Prompt 2.4 — Alpaca Order Flow as DEX Execution Model**
```
Research Alpaca's trading API as an architectural template for DEX execution:

1. Alpaca order lifecycle: how does create → fill → settle work?
2. Risk controls in Alpaca's API: buying power checks, pattern day trading, margin
3. How does Alpaca handle: partial fills, order cancellation, position tracking?
4. Map each Alpaca concept to a DEX equivalent:
   - Market order → swap with slippage tolerance
   - Limit order → on-chain limit order protocol or off-chain intent
   - Stop loss → automated monitoring + swap trigger
   - Portfolio value → on-chain balance aggregation
5. What idempotency / retry patterns does Alpaca use that we should replicate for on-chain?

I don't need Alpaca integration — I need their patterns as a blueprint for my own DEX execution layer.
```

---

### PHASE 2B: Academic & Arxiv Research (Est. 30-40 min)

**Goal:** Ground the architecture in published research — strengthens novelty score with judges and surfaces techniques you wouldn't find in GitHub repos alone.

**Connectors to enable:** Apify (for arxiv scraping if needed), PDF.co (for full paper extraction)

---

**Prompt 2B.1 — Autonomous Trading Agent Architectures (Arxiv)**
```
Search arxiv.org for recent papers (2023-2026) on autonomous trading agents in DeFi and crypto markets. Focus on:

1. Agent architectures that use LLMs or reinforcement learning for trade decisions
2. Multi-agent systems for market making or portfolio management
3. Any papers combining AI agents with on-chain execution

For each paper found, extract:
- Title, authors, arxiv ID, date
- Core contribution (1-2 sentences)
- Architecture pattern described
- Risk controls mentioned (if any)
- Whether it was tested on real chains or simulation only
- Key technique I could adapt for a hackathon demo

Search queries to try:
- "autonomous trading agent DeFi"
- "LLM trading agent blockchain"
- "multi-agent portfolio management decentralized finance"
- "reinforcement learning DEX trading"

Find 8-12 relevant papers. Prioritize papers with code repos linked.
```

---

**Prompt 2B.2 — Reputation Systems & Capital Delegation (Arxiv)**
```
Search arxiv.org for papers on reputation-based capital delegation, trust scoring for autonomous agents, and delegated portfolio management in decentralized systems:

1. Reputation scoring for DeFi agents or validators
2. Trust-aware capital allocation — how to delegate funds to an agent based on track record
3. On-chain credentialing or attestation for agent performance
4. Mechanism design for agent accountability

Search queries:
- "reputation system decentralized finance"
- "trust delegation autonomous agent"
- "on-chain attestation agent accountability"
- "delegated portfolio management blockchain"
- "agent reputation scoring DeFi"

For each paper:
- Title, arxiv ID, date
- Core mechanism described
- How reputation is computed and stored
- Could this be simplified into a hackathon-viable demo?

This directly maps to the hackathon's stated focus on "reputation-aware capital delegation" — citing research here differentiates us from teams that just build a bot.
```

---

**Prompt 2B.3 — Risk Frameworks & Safety in Autonomous Financial Agents (Arxiv)**
```
Search arxiv.org for papers on risk management and safety constraints for autonomous financial agents:

1. Circuit breaker mechanisms for automated trading
2. Formal verification or safety guarantees for DeFi agents
3. Drawdown control, position sizing, and portfolio risk in algorithmic trading
4. Adversarial robustness — how agents handle oracle manipulation, MEV, slippage attacks

Search queries:
- "risk management autonomous trading agent"
- "safety constraints DeFi bot"
- "circuit breaker algorithmic trading"
- "adversarial robustness decentralized finance"
- "portfolio risk control autonomous agent"

Also search for any survey papers on "AI agents in finance" or "LLM agents for trading" from 2024-2026 — these will have comprehensive reference lists I can mine.

For each paper, flag:
- Techniques implementable in 5 days vs research-only
- Any open-source implementations linked
```

---

**Prompt 2B.4 — Cross-Chain & Intent-Based Architectures (Arxiv)**
```
Search arxiv.org for papers on:

1. Cross-chain arbitrage detection and execution
2. Intent-based transaction architectures (ERC-7683, solver networks)
3. Cross-chain messaging security (LayerZero, Hyperlane, Wormhole analysis)
4. MEV in cross-chain contexts

Search queries:
- "cross-chain arbitrage detection"
- "intent-based transactions blockchain"
- "cross-chain bridge security analysis"
- "MEV cross-chain"
- "atomic cross-chain swaps"

For each paper:
- Core technique and trust assumptions
- Latency characteristics (can this work in practice?)
- Security model — what can go wrong?
- Hackathon applicability: REAL / MOCK / CUT

If cross-chain arb is one of our demo archetypes, this research determines whether we present it as "live execution" or "monitoring + simulated execution" — papers on latency and trust assumptions will make that call honest.
```

---

### PHASE 3: Architecture & State Management (Est. 30-45 min)

**Goal:** Design the agent's data layer, memory, and attestation pipeline.

**Connectors to enable:** GitHub, Supabase, Pinecone/Qdrant

---

**Prompt 3.1 — Agent State & Trade Logging Schema**
```
Design a database schema for an autonomous DeFi trading agent. Using Supabase (PostgreSQL) as the backend.

I need tables/schemas for:
1. **Portfolio state** — current holdings, cost basis, unrealized PnL
2. **Trade log** — every swap: timestamp, pair, direction, amount, price, slippage, tx hash, gas cost
3. **Risk state** — current drawdown, daily loss counter, position concentrations, circuit breaker status
4. **Agent decisions** — the reasoning trace: what signal fired, what risk checks passed/failed, final action taken
5. **Attestation pointers** — links between off-chain decision records and on-chain attestation tx hashes
6. **Agent config** — parameters: risk limits, allowed pairs, rebalance thresholds

Search for real examples of trading system schemas on GitHub. Give me a Supabase-compatible SQL migration I can use.

Also: what should be in Postgres vs what should be in a vector store (Pinecone/Qdrant) for agent memory?
```

---

**Prompt 3.2 — Attestation Pipeline Design**
```
Design an attestation pipeline for recording AI agent trading decisions on-chain:

1. What data to attest per trade:
   - Trade intent (what the agent wanted to do and why)
   - Risk check results (what passed, what was close to limits)
   - Execution result (tx hash, actual fill price, slippage)
   - Timestamp and agent version
2. How to structure the attestation:
   - Option A: EAS schema on Kite (if available)
   - Option B: Custom smart contract that emits structured events
   - Option C: IPFS/Arweave hash stored on-chain (cheaper, less queryable)
3. Gas optimization — if attestations cost too much per trade:
   - Batch attestations (every N trades or every M minutes)
   - Merkle root of multiple attestations stored as single tx
4. Query patterns — how would a judge or dashboard read these attestations?

Search GitHub for EAS attestation examples and on-chain audit log patterns. Give me a concrete implementation plan.
```

---

**Prompt 3.3 — Agent Memory with Vector Store**
```
Research how to implement episodic memory for a DeFi trading agent using Pinecone or Qdrant:

1. What to store as embeddings:
   - Market conditions at time of each trade decision
   - Agent reasoning traces
   - Outcomes (profitable vs not) tagged to the conditions
2. How to query memory:
   - "Have I seen similar market conditions before? What did I do and how did it go?"
   - "What's my track record on this pair?"
3. Embedding strategy:
   - What model to embed market state + reasoning? (OpenAI ada, sentence-transformers, etc.)
   - Metadata schema for filtering (pair, timestamp, outcome, confidence)
4. Practical examples — any repos doing "agent memory" with vector stores?

Keep it hackathon-scoped: what's the minimum viable memory that impresses judges vs what's overkill?
```

---

### PHASE 4: Deployment & Demo Packaging (Est. 20-30 min)

**Goal:** Nail the deployment architecture and demo narrative.

**Connectors to enable:** Cloudflare, GitHub

---

**Prompt 4.1 — Always-On Agent Deployment**
```
Research deployment patterns for an always-on DeFi trading agent:

1. Cloudflare Workers + Durable Objects:
   - Can I run a persistent agent loop in a Durable Object?
   - How do I handle: scheduled checks (cron), state persistence, secrets (private keys)?
   - Limitations: execution time, memory, network access to RPC nodes?
2. Alternative: simple Node.js/Python on a VPS (DigitalOcean, Railway, Fly.io)
   - Pros/cons vs serverless for a trading agent
3. For a hackathon specifically:
   - What's the fastest path to "live agent running at a URL judges can visit"?
   - How to handle: showing real-time agent status, recent trades, portfolio state?
4. Frontend: what's the simplest dashboard I can deploy?
   - Next.js on Vercel reading from Supabase?
   - Static page polling an API?

Give me a deployment architecture diagram (text-based) and estimated setup time for each option.
```

---

**Prompt 4.2 — Demo Storyboard Research**
```
Research what makes winning hackathon demos in crypto/DeFi agent competitions:

1. Search for past winners of:
   - Encode hackathons (any track)
   - ETHGlobal hackathons (DeFi or agent tracks)
   - Any "autonomous agent" crypto hackathon
2. What did winners demonstrate live?
   - Real transactions on testnet/mainnet?
   - Dashboard showing agent decisions in real-time?
   - Risk controls being triggered?
3. Common pitfalls:
   - What makes judges skeptical? (fake data, no real transactions, no risk controls)
   - What impresses them? (honest about limitations, live attestations, clean UX)
4. For a 3-5 minute demo, what's the ideal flow?

Give me 3 demo storyboard templates I can adapt.
```

---

### PHASE 5: Gap Fill & Verification (Est. 20-30 min)

**Goal:** Validate critical unknowns from earlier phases.

**Connectors to enable:** GitHub, Apify, Discord Bot, Telegram

---

**Prompt 5.1 — Verify Kite Contracts**
```
This is a verification pass. From my earlier research, I have the following claims about Kite chain. For each one, try to verify or refute with primary sources:

[PASTE YOUR FINDINGS FROM PHASE 1 HERE]

For each claim:
- CONFIRMED: found in official docs/explorer with URL
- CONTRADICTED: found evidence against it
- UNVERIFIABLE: couldn't find primary source either way

Also search for any Kite chain developer Discord, Telegram, or forum where I could ask questions directly.
```

---

**Prompt 5.2 — Integration Feasibility Check**
```
Based on my research so far, assess feasibility for a 5-day hackathon build:

Architecture: TypeScript agent → reads on-chain data → generates signals → executes swaps on Kite DEX → logs to Supabase → attests on-chain → displays on Next.js dashboard

For each component, answer:
1. Can I get this working in < 8 hours?
2. What's the biggest risk / blocker?
3. What should I mock vs build real?
4. What existing library or template gets me 80% there?

Components to assess:
- [ ] Kite RPC connection + reading pool state
- [ ] Swap execution on Kite DEX
- [ ] On-chain attestation recording
- [ ] Supabase trade logging
- [ ] Risk management (daily loss limit, position size cap)
- [ ] Simple signal (e.g., rebalance when allocation drifts >5%)
- [ ] Dashboard showing portfolio, trades, attestations
- [ ] LayerZero cross-chain message (if viable)

Be brutally honest about what's realistic.
```

---

## Part 4: Post-Research Synthesis Prompt

After all phases, run this final synthesis in a fresh Perplexity session with all your notes:

```
I've completed research for the Kite AI × Encode Hackathon (Agentic Trading track).
Here are my findings:

[PASTE COMPILED NOTES FROM ALL PHASES]

Now produce:
1. A final architecture decision — which demo archetype to build (execution bot, portfolio allocator, or cross-chain monitor) and why
2. A 5-day build schedule (day-by-day tasks)
3. A list of exactly which repos to clone, which APIs to set up, which contracts to interact with
4. The top 3 risks to the demo and mitigation for each
5. A 4-minute demo script with backup plan if RPC is slow

Optimize for: judges see a real agent making real decisions with real risk controls and on-chain proof.
```

---

## Quick Reference: Session Setup

Before each Perplexity session, paste this preamble:

```
CONTEXT: I'm building for the Kite AI × Encode Hackathon, Agentic Trading track.
I need an autonomous AI agent that settles on Kite chain, with on-chain attestations,
risk controls, and a functional demo.

CONSTRAINTS:
- 5-day build window
- Must be honest about what's real vs simulated
- Kite chain settlement is non-negotiable (hackathon requirement)
- Optimize for: autonomy, developer experience, real-world applicability, novelty

OUTPUT FORMAT: For every finding, include:
- Source URL
- Confidence: CONFIRMED / INFERRED / SPECULATIVE
- Hackathon viability: REAL / MOCK / CUT
- Next step to verify or implement
```
