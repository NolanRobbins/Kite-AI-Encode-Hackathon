# Perplexity Computer — Kite Hackathon Research Execution Plan

## How This Document Works

This is a **prompt-by-prompt execution plan** for Perplexity Computer. Each phase has:
- **Goal**: What you're trying to learn
- **Connectors to enable**: Which Perplexity connectors to toggle ON for that phase
- **Prompts**: Exact prompts to paste, in order
- **Output capture**: What to save and where

Run phases sequentially. Each phase builds on prior outputs.

---

## SKILL.md — Paste This Into Your Perplexity Prompt Feed

```yaml
---
name: kite-hackathon-researcher
description: >
  Systematic research agent for the Kite AI × Encode Hackathon (March 27 – April 26, 2026).
  Researches Kite chain, x402 protocol, ACP, MCP, and agent architecture patterns.
  Outputs structured notes with source URLs, confidence levels, and open questions.
context:
  hackathon: "Kite AI Global Hackathon 2026 via Encode Club"
  tracks: ["Agentic Commerce", "Agentic Trading & Portfolio Management", "Novel"]
  chain: "Kite L1 — EVM, Chain ID 2368 (testnet) / 2366 (mainnet)"
  rpc: "https://rpc-testnet.gokite.ai/"
  explorer: "https://testnet.kitescan.ai/"
  faucet: "https://faucet.gokite.ai"
  key_repos: ["gokite-ai/x402", "gokite-ai/agentic-commerce-protocol", "gokite-ai/AP2-kite", "gokite-ai/kite_counter_dapp"]
  key_docs: ["docs.gokite.ai", "docs.x402.org", "docs.cdp.coinbase.com/x402", "agenticcommerce.dev", "gokite.ai/kite-whitepaper"]
  test_usdt: "0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63"
  x402_demo_endpoint: "https://x402.dev.gokite.ai/api/weather"
  mcp_server: "https://mcp.prod.gokite.ai/"
  kitepass_portal: "https://app.gokite.ai/"
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
name: hackathon-competitor-scanner
description: >
  Finds existing projects, submissions, and reference implementations built on Kite,
  x402, or agentic payment protocols. Identifies what's been done so we can differentiate.
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
name: arxiv-literature-synthesizer
description: >
  Finds and synthesizes academic papers (arXiv, Semantic Scholar, Google Scholar)
  relevant to agentic payments, agent identity, on-chain attestation, account
  abstraction, MCP security, and autonomous commerce. Outputs structured notes
  suitable for both implementation guidance and judge-facing narrative.
output_format: |
  ## [Paper Title]
  **ArXiv ID**: [e.g., 2602.14219]
  **Authors**: [first author et al.]
  **Date**: [submission date]
  **URL**: [arxiv link]
  **Core Contribution**: [2-3 sentences — what's novel]
  **Relevance to Our Build**: HIGH / MEDIUM / LOW
  **Key Takeaways for Implementation**:
    - [actionable insight 1]
    - [actionable insight 2]
  **Quotable for Demo/Judges**: [1 sentence we could cite in our pitch]
  **Limitations / Gaps**: [what the paper doesn't solve that we need]
---
```

---

## Connector Matrix — What to Enable Per Phase

| Phase | Connectors ON | Why |
|-------|--------------|-----|
| **1: Protocol Deep Dive** | GitHub | Read repos, READMEs, code, issues from `gokite-ai/*` |
| **1.5: Academic Literature** | *(none — use Perplexity's native web search)* | arXiv, Semantic Scholar, Google Scholar are all web-indexed |
| **2: x402 Mechanics** | GitHub | `gokite-ai/x402` source, Coinbase x402 reference |
| **3: ACP + Commerce** | GitHub, Stripe | ACP spec repo, Stripe docs for ACP patterns |
| **4: Competitor Scan** | GitHub, Apify | Search GitHub topics, scrape hackathon submission pages |
| **5: Agent Architecture** | GitHub | MCP spec repo, agent framework repos |
| **6: Infra & Deploy** | GitHub | Hardhat configs, Vercel deploy patterns, Goldsky/indexer setup |
| **7: Synthesis & Planning** | Notion or Google Docs, Asana or Linear | Store final PRD, create sprint backlog |

### Connectors to NEVER enable for this workflow
- Medical Records, Wearables, sevDesk, Personio, Procore, BioRender, Jotform, HeroBot, OptimoRoute, Canvas (LMS), PandaDoc, Wealthbox, Zoho Books, Close, Unleashed, Connectwise, Snipe-IT — completely irrelevant
- Snowflake, Databricks, MongoDB, PostgreSQL, Azure SQL, MotherDuck, Turso, Supabase, Firebase Admin, Prisma Postgres — no database research needed
- Mailchimp, ConvertKit, AWeber, Loops.so, Mailgun, ZeroBounce, Resend — email marketing irrelevant
- Salesforce, HubSpot, Attio, Pipeline, Streak, Microsoft Dynamics — CRM irrelevant
- Spotify, Bluesky, Mastodon, Telegram, 2Chat, SMS Messages — social/messaging irrelevant
- All other connectors not listed in the "ON" column above

---

## Phase 1: Kite Protocol Deep Dive

**Goal**: Understand Kite's full architecture — identity, wallets, payment flow, chain specifics.
**Connectors ON**: GitHub
**Estimated prompts**: 5
**Time**: ~45 min

### Prompt 1.1 — Kite Whitepaper & Architecture
```
Using the kite-hackathon-researcher skill:

Read the Kite whitepaper at gokite.ai/kite-whitepaper and the core concepts page at docs.gokite.ai/get-started-why-kite/core-concepts-and-terminology.

I need a structured breakdown of:
1. The three-layer architecture (Platform, Programmable Trust, Ecosystem)
2. The identity model: KitePass → DID → VCs → Proof of AI
3. Wallet architecture: EOA vs AA wallet vs Embedded wallet — how they relate
4. The SPACE framework components
5. Session keys / ephemeral keys — how delegation works cryptographically
6. SLA contracts — how they differ from traditional SLAs

Tag each finding with the exact doc section it came from.
List anything that's described conceptually but where you can't find actual API/SDK documentation.
```

### Prompt 1.2 — KiteSDK & Agent Builder Workflow
```
Using the kite-hackathon-researcher skill:

Read docs.gokite.ai/kite-air-platform/kite-air-getting-started thoroughly.

Extract:
1. The exact Python SDK installation command and import pattern
2. KiteClient initialization — what params does it take?
3. Full method inventory: list_services(), execute_task(), and any others
4. The KitePass claim flow — step by step from app.gokite.ai
5. How the API key maps to the agent's on-chain identity
6. The current limitation: "agent builder is also the agent user" — what does this mean practically?
7. Service discovery: how does an agent browse the App Store programmatically?

If the SDK source is on PyPI or GitHub, find the actual package and check if there's more detailed API docs than what's on the GitBook.
```

### Prompt 1.3 — Kite MCP Server
```
Using the kite-hackathon-researcher skill:

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
6. Any authentication required beyond KitePass API key?

This is critical — if the MCP server handles payment automatically, it dramatically simplifies our agent.
```

### Prompt 1.4 — Kite Chain Specifics (AA SDK, Gasless, Multisig)
```
Using the kite-hackathon-researcher skill:

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
5. The Test USDT address is 0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63 — confirm this and check if there are other supported tokens.
6. What's the multisig pattern — Gnosis Safe compatible or custom?

Flag anything that's "coming soon" or has no actual code behind it.
```

### Prompt 1.5 — Kite GitHub Org Inventory
```
Using the kite-hackathon-researcher skill with GitHub connector:

Search the GitHub organization github.com/gokite-ai and catalog ALL public repositories.

For each repo, note:
- Name
- Description
- Primary language
- Last commit date
- Stars / activity level
- Relevance to hackathon (HIGH/MEDIUM/LOW/NONE)

Pay special attention to:
- gokite-ai/x402 — is this a fork of the Coinbase x402 or custom?
- gokite-ai/agentic-commerce-protocol — fork of OpenAI/Stripe ACP?
- gokite-ai/AP2-kite — what is Agent Payment Protocol v2?
- Any SDK repos, sample apps, or starter templates
- Any repos with recent commits (last 30 days) that might be hackathon-related

Output as a table sorted by relevance.
```

---

## Phase 1.5: Academic & Technical Literature

**Goal**: Build an academic foundation that strengthens both implementation decisions and judge narrative. Most hackathon teams cite zero papers — citing even 2-3 in your demo is a massive differentiator.
**Connectors ON**: None needed — Perplexity's native web search covers arXiv, Semantic Scholar, and Google Scholar.
**Estimated prompts**: 5
**Time**: ~35 min

### Prompt 1.5.1 — Agent Economy & Blockchain Foundations
```
Using the arxiv-literature-synthesizer skill:

Search arXiv for papers on autonomous AI agents operating as economic actors on blockchains. I'm building an agent that pays for services via x402 on Kite (an EVM L1). I need the theoretical foundation.

Start with these known papers and find related work:
1. "The Agent Economy: A Blockchain-Based Foundation for Autonomous AI Agents" (arXiv:2602.14219, Feb 2026) — proposes a five-layer architecture: Physical Infrastructure, Identity & Agency, Cognitive & Tooling, Economic & Settlement, Collective Governance
2. "Autonomous Agents on Blockchains: Standards, Execution Models, and Trust Boundaries" (arXiv:2601.04583) — systematic survey of 317 works on agent-blockchain interoperability
3. "Can We Govern the Agent-to-Agent Economy?" (arXiv:2501.16606) — Agentbound Tokens, cryptoeconomic governance

For each paper, extract:
- The architectural layers or frameworks proposed
- How they model agent identity (DIDs, VCs, on-chain reputation)
- How they handle payment delegation and spending limits
- Security threat models for autonomous agents with wallets
- Any mention of Kite, x402, ERC-4337, or account abstraction

Then search for 3-5 additional papers from 2025-2026 that cite or extend these works. Focus on papers with implementation details, not just theory.
```

### Prompt 1.5.2 — x402 & Agentic Payment Protocol Research
```
Using the arxiv-literature-synthesizer skill:

Search arXiv and Semantic Scholar for papers specifically about x402, HTTP 402 payments, and agentic payment protocols.

Known key papers:
1. "A402: Binding Cryptocurrency Payments to Service Execution for Agentic Commerce" (arXiv:2603.01179, March 2026) — proposes Atomic Service Channels (ASCs) with TEE-assisted adaptor signatures to fix x402's atomicity gap
2. "SoK: Blockchain Agent-to-Agent Payments" (arXiv:2604.03733, April 2026) — systematization of knowledge covering x402, AP2, ERC-8004, and more. CRITICALLY: this paper cites the Kite whitepaper directly.
3. "Secure Autonomous Agent Payments: Verifying Authenticity and Intent in a Trustless Environment" (arXiv:2511.15712)
4. "Whispers of Wealth: Red-Teaming Google's Agent Payments Protocol via Prompt Injection" (arXiv:2601.22569) — security attacks on agent payment systems
5. "Inter-Agent Trust Models: A Comparative Study of Brief, Claim, Proof, Stake, Reputation and Constraint" (arXiv:2511.03434) — compares trust models across A2A, AP2, ERC-8004

For each:
- What failure modes of x402 do they identify?
- What improvements do they propose?
- Do any propose on-chain attestation patterns we could implement?
- Are there security risks we need to mitigate in our demo?

This is critical — the SoK paper (2604.03733) is published THIS WEEK and directly covers our tech stack. It's the best source for understanding the academic landscape around our build.
```

### Prompt 1.5.3 — MCP Security & Architecture Papers
```
Using the arxiv-literature-synthesizer skill:

Search arXiv for papers on Model Context Protocol (MCP) architecture, security, and agent tool use.

Known papers:
1. "MCP: Landscape, Security Threats, and Future Research Directions" (arXiv:2503.23278) — comprehensive threat taxonomy: tool poisoning, command injection, credential theft, RADE attacks
2. "MCPAgentBench: A Real-world Task Benchmark for Evaluating LLM Agent MCP Tool Use" (arXiv:2512.24565) — benchmark for MCP tool selection and multi-step execution
3. "Enhancing MCP with Context-Aware Server Collaboration" (arXiv:2601.11595) — CA-MCP with shared context store for multi-agent coordination
4. "Bridging Protocol and Production: Design Patterns for Deploying AI Agents with MCP" (arXiv:2603.13417) — identifies three missing protocol primitives: identity propagation, adaptive tool budgeting, structured error semantics
5. "MCP Tool Descriptions Are Smelly" (arXiv:2602.14878) — tool description quality impacts agent performance
6. "MCPToolBench++: A Large Scale AI Agent MCP Tool Use Benchmark" (arXiv:2508.07575) — 4k+ MCP servers benchmark

Extract from each:
- Security threats relevant to our Kite MCP integration (we're connecting to mcp.prod.gokite.ai)
- Design patterns for production MCP deployments
- Performance benchmarks — what success rates should we expect for multi-tool agent tasks?
- Any findings about tool description quality that we should apply when building our own MCP tools

The MCP security papers are especially relevant — if judges ask "what about security?", citing these papers with specific mitigations is a strong answer.
```

### Prompt 1.5.4 — Account Abstraction & Agent Identity
```
Using the arxiv-literature-synthesizer skill:

Search for papers on ERC-4337 account abstraction applied to AI agent delegation, session keys, and spending controls.

Known papers:
1. "Binding Agent ID: Unleashing the Power of AI Agents with..." (arXiv:2512.17538) — uses ERC-4337 EntryPoint for agent identity, zkVM-based authentication
2. "Agent Contracts: A Formal Framework for Resource-Bounded Autonomous AI Systems" (arXiv:2601.08815, accepted at COINE 2026 / AAMAS) — formal C=(I,O,S,R,T,Φ,Ψ) contract model, 90% token reduction
3. "Insured Agents: A Decentralized Trust Insurance Mechanism for Agentic Economy" (arXiv:2512.08737)
4. "Authenticated Delegation and Authorized AI Agents" (arXiv:2501.09674) — extends OAuth 2.0 with Agent-ID Tokens

For each:
- How do they model the user → agent → session key delegation chain? (This maps directly to Kite's three-tier identity)
- What spending limit / constraint mechanisms do they propose?
- Do any implement on EVM chains we could reuse or reference?
- What's the formal security model for session key compromise?

Kite's AA wallet uses session keys with spending caps — these papers give us the theoretical justification and security analysis for that design choice.
```

### Prompt 1.5.5 — Synthesis: Academic Narrative for Judges
```
Using the arxiv-literature-synthesizer skill:

Based on the papers found in prompts 1.5.1 through 1.5.4, synthesize a "Research Context" section for our hackathon submission.

I need:
1. A 3-paragraph narrative (suitable for README or pitch deck) that positions our project within the academic landscape:
   - Para 1: The agent economy is real and growing (cite agent economy papers + market projections)
   - Para 2: Payment infrastructure is the bottleneck (cite x402 papers, A402 atomicity gap, security red-teaming)
   - Para 3: Our project addresses [specific gap] by combining [Kite primitives] with [specific technique from papers]

2. A "References" list formatted as:
   [1] Author et al., "Title," arXiv:XXXX.XXXXX, Month Year.
   — limited to the 8-10 most relevant papers

3. A "Judge Q&A Ammo" section:
   - Q: "What's the academic basis for this?" → cite the SoK and Agent Economy papers
   - Q: "Is x402 secure?" → cite A402 and the red-teaming paper, explain mitigations
   - Q: "Why account abstraction?" → cite the Agent Contracts and Binding Agent ID papers
   - Q: "Why MCP?" → cite MCPAgentBench and the production design patterns paper

This synthesis is the highest-leverage artifact from the academic phase — it turns raw papers into judge-facing narrative.
```

---

## Phase 2: x402 Protocol Mechanics

**Goal**: Understand x402 deeply enough to implement the client-side payment handshake.
**Connectors ON**: GitHub
**Estimated prompts**: 4
**Time**: ~30 min

### Prompt 2.1 — x402 Core Flow
```
Using the kite-hackathon-researcher skill:

Read the x402 protocol specification at docs.x402.org/introduction and the Coinbase implementation docs at docs.cdp.coinbase.com/x402/welcome.

Extract the COMPLETE payment flow with exact header names and JSON schemas:
1. Client sends GET/POST to resource
2. Server returns 402 — what's the exact response format? (headers + body)
3. Client constructs payment — what's the signing process? EIP-712 typed data structure?
4. Client retries with X-PAYMENT header — what's the exact format? (base64 of what?)
5. Facilitator verifies and settles — what's the facilitator's API?
6. Server returns 200 + resource

Include the PAYMENT-REQUIRED header format and the PAYMENT-SIGNATURE header format.
Distinguish between x402 V1 and V2 if both exist.
```

### Prompt 2.2 — Kite x402 Variant
```
Using the kite-hackathon-researcher skill with GitHub connector:

Read the source code at github.com/gokite-ai/x402 — the README, any docs, and the key source files.

Compare Kite's x402 implementation to the standard Coinbase x402:
1. What's the "gokite-aa" scheme? How does it differ from standard EVM x402?
2. What facilitator does Kite use? Is it the Coinbase free-tier facilitator or custom?
3. The Pieverse facilitator at facilitator.pieverse.io — what is it? How does it work with Kite?
4. Are there TypeScript/Python client libraries specific to Kite's x402?
5. What's the exact 402 response JSON from x402.dev.gokite.ai/api/weather?

Then read the Service Provider Guide at docs.gokite.ai/kite-agent-passport/service-provider-guide and extract:
6. How to build a new x402-protected service endpoint on Kite
7. The payment verification flow on the server side
8. The facilitator URLs for testnet vs mainnet
```

### Prompt 2.3 — x402 Client SDKs
```
Using the kite-hackathon-researcher skill:

Find ALL available x402 client libraries:
1. @x402/client (npm) — TypeScript, from Coinbase
2. Python x402 client — does one exist? Check PyPI and GitHub
3. Go x402 client — check the Coinbase x402 repo
4. Any Kite-specific x402 client wrapper

For each library found:
- Install command
- Basic usage example (make a paid request)
- Does it handle the full 402→sign→retry cycle automatically?
- Does it support the "gokite-aa" scheme or only standard EVM?
- Can I plug in a custom signer (for AA wallets)?

If there's no Python client that supports Kite's scheme, document exactly what I'd need to build — the signing logic, header construction, and facilitator call.
```

### Prompt 2.4 — x402 Edge Cases & Error Handling
```
Using the kite-hackathon-researcher skill:

Research x402 failure modes and edge cases. Check docs.x402.org, the GitHub issues on the x402 repos, and any blog posts.

I need to know:
1. What happens if payment settles but the server is down? (idempotency)
2. Replay attack prevention — how does the payment window work?
3. What if the facilitator is slow or unreachable?
4. Insufficient funds handling — what error does the agent get?
5. Multiple payment options in accepts[] — how should the agent choose?
6. Pre-authorization / session payments — is this supported? How?
7. Refund flow — does it exist?

This directly impacts demo reliability. I need to build retry logic and fallbacks.
```

---

## Phase 3: ACP + Agentic Commerce

**Goal**: Understand ACP well enough to implement or adapt for the Commerce track.
**Connectors ON**: GitHub, Stripe
**Estimated prompts**: 3
**Time**: ~25 min

### Prompt 3.1 — ACP Specification Deep Dive
```
Using the kite-hackathon-researcher skill with GitHub connector:

Read github.com/agentic-commerce-protocol/agentic-commerce-protocol — the full README, the spec/ directory (latest version), and the RFCs.

Extract:
1. The four ACP endpoints: CreateCheckout, UpdateCheckout, CompleteCheckout, CancelCheckout — exact request/response schemas
2. How SharedPaymentToken (SPT) works in the standard flow
3. The product feed format — what fields are required?
4. Capability negotiation RFC — what does this enable?
5. Payment handlers RFC — how do different payment methods plug in?
6. The discount extension — how does it work?
7. MCP transport — can ACP run over MCP?

Then check github.com/gokite-ai/agentic-commerce-protocol:
8. What did Kite change or add vs the upstream ACP spec?
9. Is there a Kite-specific payment handler that uses x402 instead of Stripe SPT?
```

### Prompt 3.2 — Kite AP2 (Agent Payment Protocol v2)
```
Using the kite-hackathon-researcher skill with GitHub connector:

Read github.com/gokite-ai/AP2-kite thoroughly.

This is separate from ACP — it's the "Agent Payment Protocol" version 2.

1. What is AP2 and how does it differ from ACP?
2. What's the relationship to x402? Is AP2 built on top of x402?
3. Is there a specification document or just code?
4. What use cases does AP2 target that ACP doesn't?
5. Are there working examples or is it early-stage?

This could be a key differentiator if AP2 is Kite-native and ACP is the OpenAI/Stripe standard.
```

### Prompt 3.3 — Commerce Track Strategy
```
Using the kite-hackathon-researcher skill:

I'm evaluating two commerce track approaches:

Approach A: Implement standard ACP spec but swap Stripe SPT for Kite x402 settlement.
Approach B: Build a native Kite marketplace using AP2 + x402 + MCP tool discovery.

Research and compare:
1. Which approach better matches what judges at Encode/Kite hackathons typically reward?
2. Search for past Encode hackathon winners — what patterns won? (Check encodeclub.com, Devpost)
3. Is anyone else likely building Approach A? (Check Discord, Twitter, GitHub for signals)
4. Which approach uses more Kite-native primitives? (KitePass, AA wallet, SLA contracts, gasless)
5. Which is more feasible in 2-3 weeks of building?

Be honest about what you can and can't find. Competitive intelligence is speculative — label it as such.
```

---

## Phase 4: Competitor & Prior Art Scan

**Goal**: Find what's already been built on Kite/x402 so we don't duplicate and can differentiate.
**Connectors ON**: GitHub, Apify
**Estimated prompts**: 3
**Time**: ~20 min

### Prompt 4.1 — GitHub Topic Scan
```
Using the hackathon-competitor-scanner skill with GitHub connector:

Search GitHub for these topics and keyword combinations:
- topic:kite-ai
- topic:gokite-ai
- topic:x402
- "kite testnet" + "x402"
- "kite agent" + hackathon
- "encode hackathon" + kite

For each relevant project found, capture:
- Repo URL
- What it does (from README)
- Kite primitives used
- Quality level (toy / prototype / production)
- Last updated
- Whether it could be a competing hackathon submission

Also check: github.com/topics/kite-ai and github.com/topics/gokite-ai for the community project listings.
```

### Prompt 4.2 — Existing x402 Projects
```
Using the hackathon-competitor-scanner skill:

Search for existing x402 implementations and projects beyond Kite:
1. The Coinbase x402 reference implementation — what sample apps exist?
2. AWS x402 reference architecture — what did they build?
3. Cloudflare Workers + x402 — any examples?
4. "KiteTrace" project (seen on GitHub topics) — what is it? ERC8004 + x402?
5. "OfferLock" project — trustless settlement for study abroad payments on Kite?

For each, assess: can we learn from their architecture? Are they in the same hackathon?
```

### Prompt 4.3 — Past Encode Hackathon Winners
```
Using the demo-dx-evaluator skill with Apify connector:

Search for past Encode Club hackathon results and winner announcements:
- encodeclub.com past programmes/hackathons
- Twitter/X: @encodeclub winner announcements
- YouTube: Encode Club channel for demo day recordings

For each winner you can find:
1. Project name and track
2. What they built
3. Demo format (video, live, CLI)
4. README quality (if repo is public)
5. What made them stand out?

I want to understand the bar for winning and the patterns that judges reward.
Focus on any blockchain/AI intersection hackathons — especially those sponsored by a chain.
```

---

## Phase 5: Agent Architecture & MCP

**Goal**: Decide the agent framework and MCP integration pattern.
**Connectors ON**: GitHub
**Estimated prompts**: 3
**Time**: ~20 min

### Prompt 5.1 — MCP Protocol for Tool Discovery
```
Using the kite-hackathon-researcher skill with GitHub connector:

Read the MCP specification at github.com/modelcontextprotocol/specification.

Extract what I need to build an MCP-aware agent:
1. The tools/list request/response format
2. The tools/call request/response format
3. Transport options: stdio vs SSE vs Streamable HTTP
4. How does a client discover what tools a server offers?
5. Can an MCP client be written in Python? What libraries exist? (check mcp-python-sdk)
6. How do I connect to a remote MCP server from a Python script (not Claude Desktop)?

Then specifically for Kite's MCP server:
7. Can I call tools/list on https://mcp.prod.gokite.ai/ to see what's available?
8. Does calling a Kite MCP tool trigger x402 payment automatically?
```

### Prompt 5.2 — Agent Framework Options
```
Using the kite-hackathon-researcher skill:

Compare these agent framework options for a hackathon build on Kite:

1. Raw Python + OpenAI/Anthropic function calling + x402 client
   - Most control, most work
2. LangChain/LangGraph + custom x402 tool
   - Popular but heavy
3. Anthropic Claude + MCP (via Kite MCP server)
   - Least code if MCP server handles payments
4. CrewAI or AutoGen + x402 tool
   - Multi-agent patterns
5. Coinbase AgentKit (from the AWS reference)
   - Built for x402 but may be Base-only

For each:
- Setup complexity for a 2-week hackathon
- x402/Kite compatibility (native or requires custom integration)
- Demo impressiveness (judges want to see autonomy)
- Risk level (dependency on external services)

Recommend one primary and one fallback.
```

### Prompt 5.3 — Production Agent UI Patterns
```
Using the kite-hackathon-researcher skill:

Search for agent dashboard / agent UI patterns that I can adapt:

1. GitHub: search for "agent dashboard" + react/next.js
2. Any Kite-provided UI templates? (check gokite-ai GitHub org)
3. The gokite-ai/kite_counter_dapp and kite_voting_dapp — can I use these as UI scaffolds?
4. wagmi + viem for Kite chain connection — any gotchas with custom EVM chains?
5. How to display real-time transaction feed from KiteScan API
6. Goldsky indexer — is there a subgraph or Mirror pipeline I can query for Kite events?

I need a Next.js dashboard that shows:
- Agent activity log (task, tool used, cost, tx hash with KiteScan link)
- Cumulative spend chart
- Tool marketplace (available services + prices)
- Wallet balance (AA wallet on Kite)
```

---

## Phase 6: Infrastructure & Deployment

**Goal**: Lock down the deployment stack and CI/CD for demo day.
**Connectors ON**: GitHub
**Estimated prompts**: 2
**Time**: ~15 min

### Prompt 6.1 — Smart Contract Deployment on Kite
```
Using the kite-hackathon-researcher skill:

I need to deploy a custom attestation contract to Kite testnet.

From docs.gokite.ai, extract:
1. Complete Hardhat setup for Kite testnet (config, env vars, deploy script)
2. Contract verification on KiteScan — is there a verify plugin? What's the API?
3. Gas estimation — roughly how much KITE does a contract deploy cost?
4. The faucet at faucet.gokite.ai — how much does it give per claim? Any rate limits?
5. Are there any Kite-specific Solidity libraries or interfaces I should use?
6. The block explorer API — can I query events programmatically?

Also check: does Kite support Foundry, or is Hardhat the only documented path?
```

### Prompt 6.2 — Vercel Deployment + Environment Setup
```
Using the kite-hackathon-researcher skill:

Plan the production deployment:

1. Next.js on Vercel — any issues with crypto/ethers.js in edge runtime?
2. Python agent backend — where to host? (Railway, Render, AWS Lambda, self-hosted)
3. Environment variable management for demo:
   - KITE_RPC_URL
   - KITEPASS_API_KEY
   - PRIVATE_KEY (for AA wallet)
   - OPENAI_API_KEY or ANTHROPIC_API_KEY
4. Can I use Vercel serverless functions as x402 service endpoints?
5. Docker setup as fallback for "one command run"
6. GitHub Actions CI — smoke test on every push (hit testnet RPC, verify contracts)

Search for any x402 + Vercel examples or templates.
```

---

## Phase 7: Synthesis & Sprint Planning

**Goal**: Consolidate all research into actionable build plan. Store artifacts.
**Connectors ON**: Notion or Google Docs (for storage), Asana or Linear (for task tracking)
**Estimated prompts**: 3
**Time**: ~20 min

### Prompt 7.1 — Architecture Decision Record
```
Using the kite-hackathon-researcher skill:

Based on everything I've researched in Phases 1-6, help me write an Architecture Decision Record (ADR) for my hackathon submission.

Sections:
1. **Decision**: What are we building? (one paragraph)
2. **Context**: What constraints drove this? (hackathon criteria, Kite primitives, time)
3. **Architecture**: Component diagram (describe in text, I'll draw it)
   - Agent layer (framework, LLM, MCP client)
   - Payment layer (x402 client, AA wallet, Kite facilitator)
   - Service layer (x402-protected APIs we build or wrap)
   - Chain layer (attestation contract, KiteScan)
   - UI layer (Next.js dashboard)
4. **Alternatives considered**: What we didn't pick and why
5. **Risks**: Top 5 risks with mitigation
6. **Open questions**: Things still unresolved from research

Save this to Notion / Google Docs if connected.
```

### Prompt 7.2 — Sprint Backlog
```
Using the kite-hackathon-researcher skill:

Create a sprint backlog for a 2-week build (assuming 1 builder, ~6 hrs/day).

Structure as:
- **Week 1 (P0 — Foundation)**
  - Day 1-2: Environment setup, KitePass, faucet, smoke test
  - Day 3-4: x402 client implementation, first paid API call
  - Day 5-6: Attestation contract deploy, first on-chain attestation
  - Day 7: Agent scaffold with LLM tool-use, first autonomous task
- **Week 2 (P1 — Integration & Polish)**
  - Day 8-9: Dashboard UI, tx feed, wallet display
  - Day 10-11: Multiple service endpoints, marketplace UI
  - Day 12: Demo rehearsal, video recording
  - Day 13: README, documentation, final deploy
  - Day 14: Buffer / bug fixes / submission

Each task should have:
- Estimated hours
- Dependency (what must be done first)
- Definition of done
- Risk flag if applicable

Create this as issues in Asana or Linear if connected.
```

### Prompt 7.3 — Demo Script & Judge Q&A (with Academic Backing)
```
Using the demo-dx-evaluator skill:

Write the final demo script (5 minutes) and judge Q&A prep.

Demo script format:
| Timestamp | Screen | Narration | Judge Criterion Hit | Backup Plan |

IMPORTANT: Incorporate the academic narrative from Phase 1.5.5 into the demo. Specifically:
- At the 0:30 mark, include a brief "Research Context" slide citing 2-3 key papers
- In the closing, reference the SoK paper (arXiv:2604.03733) to show we're building on cutting-edge research

Judge Q&A — prepare answers for:
1. "How is this different from just using the Coinbase x402 facilitator on Base?"
2. "What happens if the agent overspends?" → cite Agent Contracts paper (arXiv:2601.08815) on resource-bounded execution
3. "How do you verify the attestations are legitimate?" → reference on-chain immutability + Kite's cryptographic proof model
4. "Could this work on mainnet today?"
5. "What would you build next with another month?" → cite A402 (arXiv:2603.01179) atomic service channels as future direction
6. "Why Kite instead of building on Base/Solana directly?" → cite Kite whitepaper's SPACE framework + the SoK comparison table
7. "How does the MCP integration add value vs direct API calls?" → cite MCP production design patterns paper (arXiv:2603.13417) on runtime tool discovery
8. "What's the latency of the full payment cycle?"
9. "What's the academic basis for this approach?" → cite Agent Economy (arXiv:2602.14219) five-layer architecture alignment
10. "What about MCP security risks?" → cite MCP threat taxonomy paper (arXiv:2503.23278), explain specific mitigations we implemented

For each: 2-3 sentence answer that references both Kite-specific technical details AND academic citations. This is the differentiator — most hackathon teams can't cite a single paper.
```

---

## Output Tracking Checklist

After completing all phases, you should have these artifacts:

| # | Artifact | Phase | Storage Location |
|---|----------|-------|-----------------|
| 1 | Kite architecture notes | 1.1 | Notion / Google Doc |
| 2 | KiteSDK API inventory | 1.2 | Notion / Google Doc |
| 3 | MCP server tool inventory | 1.3 | Notion / Google Doc |
| 4 | AA SDK / Gasless notes | 1.4 | Notion / Google Doc |
| 5 | gokite-ai repo inventory table | 1.5 | Notion / Google Doc |
| 5a | Agent economy & blockchain foundations papers | 1.5.1 | Notion / Google Doc |
| 5b | x402 / agentic payment protocol papers | 1.5.2 | Notion / Google Doc |
| 5c | MCP security & architecture papers | 1.5.3 | Notion / Google Doc |
| 5d | Account abstraction & agent identity papers | 1.5.4 | Notion / Google Doc |
| 5e | Academic narrative for judges + reference list | 1.5.5 | Notion / Google Doc + README |
| 6 | x402 flow diagram (text) | 2.1 | Notion / Google Doc |
| 7 | Kite x402 variant differences | 2.2 | Notion / Google Doc |
| 8 | x402 client library comparison | 2.3 | Notion / Google Doc |
| 9 | x402 error handling guide | 2.4 | Notion / Google Doc |
| 10 | ACP endpoint schemas | 3.1 | Notion / Google Doc |
| 11 | AP2 vs ACP comparison | 3.2 | Notion / Google Doc |
| 12 | Commerce track decision | 3.3 | Notion / Google Doc |
| 13 | Competitor project table | 4.1-4.2 | Notion / Google Doc |
| 14 | Past winner patterns | 4.3 | Notion / Google Doc |
| 15 | Agent framework decision | 5.2 | Notion / Google Doc |
| 16 | UI component plan | 5.3 | Notion / Google Doc |
| 17 | Hardhat deploy guide | 6.1 | README draft |
| 18 | Deploy architecture | 6.2 | README draft |
| 19 | ADR | 7.1 | Notion / Google Doc |
| 20 | Sprint backlog | 7.2 | Asana / Linear |
| 21 | Demo script + Q&A | 7.3 | Notion / Google Doc |

---

## Estimated Total Time: ~3.5 hours

| Phase | Prompts | Est. Time |
|-------|---------|-----------|
| 1: Protocol Deep Dive | 5 | 45 min |
| 1.5: Academic Literature | 5 | 35 min |
| 2: x402 Mechanics | 4 | 30 min |
| 3: ACP + Commerce | 3 | 25 min |
| 4: Competitor Scan | 3 | 20 min |
| 5: Agent Architecture | 3 | 20 min |
| 6: Infra & Deploy | 2 | 15 min |
| 7: Synthesis | 3 | 20 min |
| **Total** | **28** | **~3.5 hrs** |

Start Phase 1 now. Each prompt is self-contained — if Perplexity hits a dead end on one, skip it and move to the next. The skill frontmatter ensures consistent output formatting across all prompts.
