# NegotiatorGrid: Missing Repos & Critical Resources

> Compiled research identifying GitHub repositories and resources critical to the NegotiatorGrid project — an agent-to-agent bargaining system with blockchain settlement. Organized by domain, with full metadata and NegotiatorGrid-specific relevance.

---

## 1. Opponent Modeling Libraries

### 1.1 NegMAS (Negotiation Multi-Agent System)

| Field | Value |
|---|---|
| **Name** | yasserfarouk/negmas |
| **URL** | https://github.com/yasserfarouk/negmas |
| **Language** | Python (Jupyter Notebook 70.1%, Python 29.7%) |
| **Stars** | 85 |
| **Last Updated** | March 17, 2026 (v0.15.4) |
| **Install** | `pip install negmas` |
| **Docs** | https://negmas.readthedocs.io |

**Description:** The core Python library for autonomous negotiation agents in simulated environments. Designed for situated simultaneous negotiations in business-like settings. Powers the ANL competition.

**Key features:**
- Bilateral and multilateral negotiation protocols (SAO/Stacked Alternating Offers, Single-Text, Auctions)
- Rich utility function types: `LinearAdditiveUtilityFunction`, `MappingUtilityFunction`, probabilistic and dynamic utility functions
- Built-in negotiators: `AspirationNegotiator`, `TimeBasedConcedingNegotiator`, `NaiveTitForTatNegotiator`, `BoulwareTBNegotiator`, `TitForTatNegotiator`
- BOA (Bidding–Opponent modeling–Acceptance) framework with `GSmithFrequencyModel` for opponent modeling
- Concurrent negotiations: agents running multiple negotiations simultaneously
- Genius integration: bridge to run Java-based Genius agents
- CLI: `negotiate` command for quick experimentation

**NegotiatorGrid relevance:** The foundational library for implementing concession strategies, opponent preference modeling, and the SAO protocol that mirrors bilateral price negotiation. The `BOANegotiator` and `GSmithFrequencyModel` map directly to NegotiatorGrid's opponent state-tracking and pricing logic. `pip install negmas` is the single fastest way to get production-grade negotiation infrastructure.

---

### 1.2 ANL — Automated Negotiation League (ANAC 2024–2025)

| Field | Value |
|---|---|
| **Name** | autoneg/anl |
| **URL** | https://github.com/autoneg/anl |
| **Language** | Jupyter Notebook (90.8%), Python (9.2%) |
| **Stars** | ~0 (official competition platform) |
| **Last Updated** | March 16, 2025 |
| **Install** | `pip install anl` |
| **Docs** | https://yasserfarouk.github.io/anl/ / https://autoneg.github.io/anl2025/ |

**Description:** Official platform for the ANAC Automated Negotiation Leagues (2024–present). A thin wrapper around NegMAS providing tournament generation, CLI, and official competition agent implementations. The 2025 challenge: sequential multi-deal negotiation where an agent encounters multiple opponents in sequence and is rewarded for the specific combination of deals across all negotiations.

**Key features:**
- `anl2025_tournament()` for generating standardized competition scenarios
- CLI: `anl tournament run --generate=5`
- Official reference agents for all ANL years post-2024 in `anl.anl2025.negotiator`
- Standardized testing against real competition domains

**NegotiatorGrid relevance:** The competition agents inside this repo represent state-of-the-art negotiation strategies peer-reviewed against hundreds of other agents. The sequential multi-deal framing (ANL 2025) is architecturally identical to NegotiatorGrid's multi-session scenario where an agent must optimize across a sequence of counterparties.

---

### 1.3 GENIUS / GeniusWeb — TU Delft Negotiation Platform

| Field | Value |
|---|---|
| **Name** | GENIUS (Java desktop), GeniusWeb (distributed) |
| **URL (GENIUS site)** | https://ii.tudelft.nl/genius/ |
| **URL (GitLab)** | https://automatednegotiation.gitlab.io/genius/ |
| **Language** | Java (primary); Python adapter available |
| **Stars** | N/A (institutional download) |
| **Last Updated** | Actively maintained (ANAC 2020+) |

**Description:** The original TU Delft negotiation platform — the de facto standard in automated negotiation research since 2008 (won CIA 2008 System Innovation Award). GeniusWeb is the distributed successor, separating preferences, protocols, and agents onto separate servers. The Python adapter (`geniusweb-pyson`) allows Python agents to connect to GeniusWeb tournaments.

**Key features:**
- Stacked Alternating Offers Protocol (SAOP) — the industry standard bilateral protocol
- Large repository of ANAC competition domains (2010–2023)
- Supports preference uncertainty, elicitation, and user modeling
- Response timeout enforcement (10 seconds per move)
- BOA component implementations in Java with Python interop

**NegotiatorGrid relevance:** GENIUS domains are the canonical test scenarios for negotiation research. NegMAS ships with GENIUS domain compatibility (`negmas[genius]`). If NegotiatorGrid needs to benchmark against research-grade agents or use established utility functions, GENIUS domains are the standard reference. The Python adapter `brenting/ANL-2023-example-agent` (https://github.com/brenting/ANL-2023-example-agent) is the most accessible entry point for Python-native GENIUS agent development.

---

### 1.4 NegoLog — Python Negotiation Framework with Opponent Modeling

| Field | Value |
|---|---|
| **Name** | aniltrue/NegoLog |
| **URL** | https://github.com/aniltrue/NegoLog |
| **Language** | Python 99.9% |
| **Stars** | 7 |
| **Last Updated** | March 28, 2025 |

**Description:** Published at IJCAI 2024. A Python framework built specifically around modular opponent modeling evaluation — the `AbstractOpponentModel` class allows opponent models to be developed and benchmarked independently of the bidding strategy, which is uniquely valuable for isolating Bayesian inference quality.

**Key features:**
- `AbstractOpponentModel`: decoupled opponent model development and evaluation
- `EstimatedPreference` objects: structured output of opponent preference estimates
- Domain Generator: automated scenario creation with configurable utility distributions
- Web UI for tournament configuration and monitoring
- Callbacks: `before_session_start`, `on_offer`, `on_accept`, `on_fail`
- Analytics: negotiation process, outcome, and preference estimation accuracy

**NegotiatorGrid relevance:** The cleanest Python implementation for standalone Bayesian/ML opponent preference estimation. If NegotiatorGrid wants to A/B test different opponent models (frequency heuristic vs Gaussian process vs neural network) without rewriting the bidding engine each time, NegoLog's architecture is the template to follow.

---

### 1.5 kushalchawla/opponent-modeling — Transformer-Based Opponent Modeling

| Field | Value |
|---|---|
| **Name** | kushalchawla/opponent-modeling |
| **URL** | https://github.com/kushalchawla/opponent-modeling |
| **Language** | Python 98.8% |
| **Stars** | ~10 |
| **Last Updated** | 2022 |

**Description:** NAACL 2022 Findings paper implementation. Uses a transformer-based hierarchical ranker to infer an opponent's priority ordering over issues from partial negotiation dialogue. Formulates opponent modeling as a ranking task with data adaptation from related datasets (argument-centric and offer-centric).

**NegotiatorGrid relevance:** Represents the NLP-meets-negotiation approach. If NegotiatorGrid's agents communicate in natural language (not just structured bids), this architecture provides a principled way to extract opponent preference orderings from dialogue history — relevant for LLM-native agent negotiators.

---

### 1.6 velochy/rl-bargaining — RL-Based Rubinstein Bargaining

| Field | Value |
|---|---|
| **Name** | velochy/rl-bargaining |
| **URL** | https://github.com/velochy/rl-bargaining |
| **Language** | Python 100% |
| **Stars** | ~5 |
| **Last Updated** | 2019 |

**Description:** Deep RL (DDPG) experiments for Rubinstein-based bargaining with incomplete information. Buyer and seller have hidden reservation prices; agents must infer the other's threshold while making alternating offers. Uses OpenAI Gym format.

**NegotiatorGrid relevance:** Provides a minimal, clean implementation of the Rubinstein incomplete-information bargaining environment. Useful as a training environment baseline for RL-based negotiation agent policies.

---

### 1.7 FranxYao/GPT-Bargaining — LLM Self-Play Negotiation

| Field | Value |
|---|---|
| **Name** | FranxYao/GPT-Bargaining |
| **URL** | https://github.com/FranxYao/GPT-Bargaining |
| **Language** | Python / Jupyter Notebook |
| **Stars** | 208 |
| **Last Updated** | 2023 |

**Description:** Implementation of "Improving Language Model Negotiation with Self-Play and In-Context Learning from AI Feedback" (Arxiv 2023). Two LLMs negotiate as buyer/seller; a third LLM acts as critic and provides feedback to improve strategy iteratively across rounds.

**NegotiatorGrid relevance:** Directly models NegotiatorGrid's agent-to-agent bargaining architecture. The critic-agent feedback loop is directly applicable to improving NegotiatorGrid agent strategies through self-play. The `agent.py` structure (buyer agent, seller agent, critic agent) is a copy-paste starting point.

---

### 1.8 lechmazur/PACT — LLM Bargaining Benchmark

| Field | Value |
|---|---|
| **Name** | lechmazur/pact |
| **URL** | https://github.com/lechmazur/pact |
| **Language** | Python |
| **Stars** | 29 |
| **Last Updated** | August 21, 2025 |

**Description:** Pairwise Auction Conversation Testbed. 5,000+ 1v1 LLM bargaining games, 20 rounds each, with complete JSONL logs. Buyer and seller hold hidden private values; deal clears when bid ≥ ask at the midpoint.

**NegotiatorGrid relevance:** The most up-to-date benchmark dataset for LLM-native agent bargaining. Provides empirical baselines for measuring NegotiatorGrid agent performance against state-of-the-art LLMs (GPT-5, Claude, etc.). The Composite Model Score (CMS) metric is directly adoptable as a NegotiatorGrid performance KPI.

---

## 2. Game-Theoretic Pricing

### 2.1 gambitproject/gambit — Nash Equilibrium Computation

| Field | Value |
|---|---|
| **Name** | gambitproject/gambit |
| **URL** | https://github.com/gambitproject/gambit |
| **Language** | C++ (78%), Python API (7.4%) |
| **Stars** | 435 |
| **Last Updated** | January 13, 2025 (v16.3.0) |
| **Install** | `pip install gambit` |
| **Docs** | http://www.gambit-project.org |

**Description:** The canonical open-source package for computation in non-cooperative game theory. Computes one or more Nash equilibria of games in extensive or strategic form. Supports mixed strategy profiles, quantal response equilibria (QRE), and QRE data fitting.

**NegotiatorGrid relevance:** The reference implementation for computing Nash Bargaining Solutions. NegotiatorGrid's pricing engine can use Gambit to compute the theoretically optimal Nash bargaining outcome as a benchmark or target price. The Python API (`import gambit`) allows integration into the negotiation loop.

---

### 2.2 gucci-j/predicting-nash — Nash Bargaining in Negotiation Dialogue

| Field | Value |
|---|---|
| **Name** | gucci-j/predicting-nash |
| **URL** | https://github.com/gucci-j/predicting-nash |
| **Language** | Python (PyTorch) |
| **Stars** | ~5 |
| **Last Updated** | Archived May 2024 |

**Description:** PyTorch implementation predicting the Nash Bargaining Solution from negotiation dialogue history. Achieves 71% accuracy, matching the paper's reported 70% baseline. Uses NLP features from dialogue turns to predict which outcome maximizes the Nash product.

**NegotiatorGrid relevance:** Provides a learnable approximation of the Nash Bargaining Solution — useful when the exact solution is intractable in real-time and NegotiatorGrid needs a fast neural approximator to guide concession targets.

---

### 2.3 krichelj/PyDiffGame — Nash Equilibrium in Differential Games

| Field | Value |
|---|---|
| **Name** | krichelj/PyDiffGame |
| **URL** | https://github.com/krichelj/PyDiffGame |
| **Language** | Python 100% |
| **Stars** | 52 |
| **Last Updated** | February 19, 2025 (v1.0.0) |
| **Install** | `pip install PyDiffGame` |

**Description:** Nash Equilibrium computation for continuous-time differential games via Hamilton-Jacobi-Bellman reduction to Algebraic/Differential Riccati equations. Used for multi-objective dynamical control systems.

**NegotiatorGrid relevance:** Relevant when NegotiatorGrid needs to model negotiations as continuous-time dynamic systems (e.g., time-discounted Rubinstein alternating offers). The Nash equilibrium solutions from differential game theory directly characterize the theoretical fair price in time-pressured bilateral negotiations.

---

### 2.4 SivamPillai/Auctions — VCG Mechanism Design

| Field | Value |
|---|---|
| **Name** | SivamPillai/Auctions |
| **URL** | https://github.com/SivamPillai/Auctions |
| **Language** | Python |
| **Stars** | ~5 |
| **Last Updated** | 2017 |

**Description:** Python implementation of VCG (Vickrey–Clarke–Groves) mechanism for computing allocations and payoffs in multi-item auctions. Includes second-price auction analysis with IID bidder valuations.

**NegotiatorGrid relevance:** Provides a foundational implementation of truthful mechanism design. If NegotiatorGrid extends to multi-item or multi-party settings, VCG is the starting point for incentive-compatible pricing. Useful as a reference for automated mechanism design components.

---

### 2.5 alimama-tech/AuctionNet — Large-Scale Auction Benchmark

| Field | Value |
|---|---|
| **Name** | alimama-tech/AuctionNet |
| **URL** | https://github.com/alimama-tech/AuctionNet |
| **Language** | Python |
| **Stars** | ~50 |
| **Last Updated** | December 2024 |

**Description:** NeurIPS 2024 competition benchmark for bid decision-making in large-scale ad auctions. Contains 500M+ records, 80GB dataset, baseline algorithms (linear programming, RL, generative models), and 48 competing agent strategies.

**NegotiatorGrid relevance:** The largest open-source auction decision-making dataset available. Provides RL-compatible environments and baseline agents for training NegotiatorGrid's pricing strategy under competitive pressure. The `simul_bidding_env` module can be repurposed for NegotiatorGrid scenario simulation.

---

### 2.6 savente93/pyneg — Modular Concession Strategy Library

| Field | Value |
|---|---|
| **Name** | savente93/pyneg |
| **URL** | https://github.com/savente93/pyneg |
| **Language** | Python 99.9% |
| **Stars** | 4 |
| **Last Updated** | Archived November 2021 |

**Description:** Modular Python library for automated negotiation using probabilistic models (ProbLog). Favors composition over inheritance. Implements `make_linear_concession_agent` — a ready-to-run concession strategy with configurable utility functions and reservation values.

**NegotiatorGrid relevance:** The cleanest Python implementation of linear concession strategies with probabilistic reasoning. Despite being archived, the `make_linear_concession_agent` pattern is a direct starting template for NegotiatorGrid's fallback concession policy.

---

## 3. ERC-8004 & Agent Identity On-Chain

### 3.1 ERC-8004 — Trustless Agents (Official EIP)

| Field | Value |
|---|---|
| **Name** | ERC-8004: Trustless Agents |
| **URL** | https://eips.ethereum.org/EIPS/eip-8004 |
| **Discussion** | https://ethereum-magicians.org/t/erc-8004-trustless-agents/25098 |
| **Mainnet Status** | Live on Ethereum Mainnet as of January 29, 2026 |
| **Authors** | Marco De Rossi (MetaMask), Davide Crapis (Ethereum Foundation), Jordan Ellis (Google), Erik Reppel (Coinbase) |

**Description:** Three lightweight on-chain registries for AI agent identity, reputation, and validation. Uses ERC-721 with URIStorage for the Identity Registry — every agent gets an NFT-like portable identity. Agent addresses follow CAIP-10 format (`eip155:{chainId}:{address}`). Deployed as per-chain singletons on L2 or Mainnet.

**Three registries:**
1. **Identity Registry**: ERC-721 token per agent, linking to an off-chain agent registration JSON (`agent-card.json`) containing name, description, service endpoints (A2A, MCP, ENS, DID, email), and payment address.
2. **Reputation Registry**: Standardized feedback and rating collection.
3. **Validation Registry**: Pluggable verification (stake-secured re-execution, zkML, TEE attestations).

**Agent registration format:**
```json
{
  "type": "https://eips.ethereum.org/EIPS/eip-8004#registration-v1",
  "name": "myAgentName",
  "services": [{"name": "A2A", "endpoint": "..."}, {"name": "MCP", "endpoint": "..."}],
  "x402Support": true,
  "active": true
}
```

**NegotiatorGrid relevance:** **Critical infrastructure.** ERC-8004 is the on-chain identity layer NegotiatorGrid needs for trustless agent discovery. Each NegotiatorGrid agent registers once on the Identity Registry and becomes discoverable to any counterparty. The Reputation Registry enables NegotiatorGrid agents to accumulate verifiable deal history on-chain, which is the trust signal that unlocks better deal terms in future sessions. The Validation Registry is the hook for ZK-proof settlement verification.

---

### 3.2 decentralized-identity/veramo — DID Resolution Framework

| Field | Value |
|---|---|
| **Name** | decentralized-identity/veramo |
| **URL** | https://github.com/decentralized-identity/veramo |
| **Language** | TypeScript 99.6% |
| **Stars** | 534 |
| **Last Updated** | February 11, 2026 (v7.0.0) |

**Description:** JavaScript/TypeScript framework for Verifiable Data. Modular DID resolution and Verifiable Credential management across multiple DID methods. Supports `did:ethr`, `did:pkh`, `did:web`, and others. Native EVM integration.

**NegotiatorGrid relevance:** The most mature open-source framework for DID resolution on EVM chains. Veramo bridges ERC-8004 identity (ERC-721 token IDs) with W3C DID standards (`did:ethr:`, `did:pkh:`). NegotiatorGrid agents can use Veramo to issue and verify Verifiable Credentials (e.g., "this agent completed 500 successful deals at >0.7 Nash efficiency") which become the trust signals fed into the ERC-8004 Reputation Registry. The `@veramo/did-resolver` package resolves `did:ethr:` to on-chain identity data.

---

### 3.3 mcpdotdirect/evm-mcp-server — EVM MCP Server for AI Agents

| Field | Value |
|---|---|
| **Name** | mcpdotdirect/evm-mcp-server |
| **URL** | https://github.com/mcpdotdirect/evm-mcp-server |
| **Language** | TypeScript |
| **Stars** | ~200 |
| **Last Updated** | March 2025 |

**Description:** MCP (Model Context Protocol) server providing 22 blockchain tools to AI agents across 30+ EVM chains. Enables agents to read chain state, call contracts, transfer tokens, and resolve ENS names — all via a unified MCP interface. Every tool that accepts addresses also supports ENS names.

**NegotiatorGrid relevance:** Provides the MCP-native interface for NegotiatorGrid agents to interact with on-chain settlement contracts. Agents can query their ERC-8004 identity registry, check escrow balances, and read deal history without managing raw Web3 calls. ENS resolution is automatic, enabling human-readable agent addressing.

---

### 3.4 coinbase/x402 — HTTP-Native Agent Payment Protocol

| Field | Value |
|---|---|
| **Name** | coinbase/x402 (forked from x402-foundation/x402) |
| **URL** | https://github.com/coinbase/x402 |
| **Language** | TypeScript (43%), Python (33%), Go (23%), Solidity (0.5%) |
| **Stars** | 41 |
| **Last Updated** | April 2026 |
| **License** | Apache-2.0 |
| **Install (Python)** | `pip install x402` |

**Description:** Open standard for HTTP-native payments between AI agents. When an agent requests a resource, the server responds with HTTP 402 Payment Required; the agent reads instructions, signs a stablecoin transaction (USDC via EIP-3009 gasless, or any ERC-20 via Permit2), and retries. Settlement is handled by a facilitator. Supports `exact` (fixed-amount) and `upto` (usage-based) payment schemes.

**NegotiatorGrid relevance:** **Critical infrastructure.** x402 is the payment execution layer for NegotiatorGrid's on-chain settlement. After two NegotiatorGrid agents agree on a price, the buyer agent executes an x402 payment — no manual transaction construction required. The Python SDK (`pip install x402`) integrates directly with FastAPI. The `upto` scheme supports variable-price service agreements where final settlement depends on negotiated outcome.

---

### 3.5 epappas/seipients-agent-to-agent — P2P Agentic Auction Network

| Field | Value |
|---|---|
| **Name** | epappas/seipients-agent-to-agent |
| **URL** | https://github.com/epappas/seipients-agent-to-agent |
| **Language** | Rust 95.2% |
| **Stars** | 2 |
| **Last Updated** | February 2025 |

**Description:** cookie.fun Hackathon project on the SEI blockchain. P2P agent network with auction mechanics, JSON-RPC bidding, and SEI smart contract escrow. Agents bid on subtasks, receive instant payment upon proof-of-work via Merkle proof submission. Capability discovery via GossipSub/libp2p; peer routing via Kademlia DHT.

**JSON-RPC methods:** `TaskProposal`, `BidSubmission`, `WorkProof`, `PaymentFinalize`

**NegotiatorGrid relevance:** Closest prior art to NegotiatorGrid's architecture. This repo implements agent-to-agent auction + blockchain settlement in a hackathon context. The task delegation flow (`TaskProposal` → `BidSubmission` → `WorkProof` → `PaymentFinalize`) is a direct template for NegotiatorGrid's negotiation lifecycle. The trust model (whitelist + on-chain reputation) is architecturally identical to what NegotiatorGrid needs.

---

### 3.6 agntcy/oasf — Open Agent Schema Framework (Referenced in ERC-8004)

| Field | Value |
|---|---|
| **Name** | agntcy/oasf |
| **URL** | https://github.com/agntcy/oasf/tree/v0.8.0 |
| **Notes** | Referenced directly in ERC-8004 service endpoint schema |

**Description:** The Open Agent Schema Framework is explicitly referenced in the ERC-8004 registration file format for OASF-compatible endpoints. Defines a standardized schema for agent capabilities, skills, and domains.

**NegotiatorGrid relevance:** If NegotiatorGrid registers agents under ERC-8004 with OASF endpoints, it gets schema-level interoperability with any OASF-aware agent discovery platform. Critical for ensuring NegotiatorGrid agents appear correctly in ERC-8004 explorers (e.g., Agentscan).

---

## 4. Real-Time WebSocket Negotiation

### 4.1 ag2ai/realtime-agent-over-websockets — FastAPI + WebSocket Agent Demo

| Field | Value |
|---|---|
| **Name** | ag2ai/realtime-agent-over-websockets |
| **URL** | https://github.com/ag2ai/realtime-agent-over-websockets |
| **Language** | Python (64.5%), HTML (32.4%), JavaScript (3.1%) |
| **Stars** | 10 |
| **Last Updated** | January 2025 |

**Description:** Official AG2 demo for real-time agent communication over WebSockets using FastAPI. Demonstrates streaming audio/message from browser to FastAPI server with a persistent two-way connection to an AG2 RealtimeAgent.

**NegotiatorGrid relevance:** The reference implementation for FastAPI WebSocket agent backends. The pattern — `@app.websocket("/ws/chat")` → `await websocket.accept()` → streaming agent responses — is the exact architecture NegotiatorGrid needs for its real-time negotiation session transport. The `WebSocketApiService` class on the frontend side is a reusable client template.

---

### 4.2 Youssef-Adell/BidX-API — Real-Time Bidding Platform with SignalR/WebSocket

| Field | Value |
|---|---|
| **Name** | Youssef-Adell/BidX-API |
| **URL** | https://github.com/Youssef-Adell/BidX-API |
| **Language** | C# / ASP.NET Core |
| **Stars** | ~30 |
| **Last Updated** | February 2025 |

**Description:** Real-time auction/bidding platform with live bidding, auction feeds, notifications, chat, and reviews. Uses SignalR (WebSocket-backed) for real-time updates. Docker-compose deployable.

**NegotiatorGrid relevance:** Shows production-grade real-time bidding architecture — live feed updates, outbid notifications, auction state synchronization. While the language is C#, the WebSocket messaging patterns and session state management (bid history, current price, participant tracking) translate directly to NegotiatorGrid's Python/FastAPI negotiation session management.

---

### 4.3 gustavomazzoni/auction-system — AngularJS + Socket.io Real-Time Auction

| Field | Value |
|---|---|
| **Name** | gustavomazzoni/auction-system |
| **URL** | https://github.com/gustavomazzoni/auction-system |
| **Language** | JavaScript (Node.js, AngularJS) |
| **Stars** | ~50 |
| **Last Updated** | 2016 (Socket.io reference architecture) |

**Description:** Single-page application with real-time auction updates via Socket.io. Demonstrates the classic emit/listen pattern for broadcasting bid state changes to all connected participants simultaneously.

**NegotiatorGrid relevance:** Classic reference for the socket.io broadcast pattern. The server-side `io.emit('bid_update', data)` → client `socket.on('bid_update', callback)` pattern is the lowest-friction way to implement NegotiatorGrid's negotiation state broadcasting for a web frontend.

---

### 4.4 rogers-cyber/auction-management-system — Python Sockets Auction

| Field | Value |
|---|---|
| **Name** | rogers-cyber/auction-management-system |
| **URL** | https://github.com/rogers-cyber/auction-management-system |
| **Language** | Python 100% |
| **Stars** | ~10 |
| **Last Updated** | January 2026 |

**Description:** Real-time Python auction system using raw sockets, Tkinter GUIs, and SQLite. Server manages auctions; clients connect for live bid updates. Uses threading per client connection. Tutorial-level code with clean separation of auction server, admin app, and bidder app.

**NegotiatorGrid relevance:** Cleanest Python-native example of a real-time auction server. The `handle_client()` pattern with JSON request/response over TCP sockets is directly adaptable for NegotiatorGrid's agent-to-agent negotiation session server.

---

## 5. Kite Hackathon Prior Art & Similar Projects

### 5.1 GoKite.ai — The Kite AI Blockchain (EVM L1 for Agentic Payments)

| Field | Value |
|---|---|
| **Website** | https://gokite.ai |
| **Docs** | https://docs.gokite.ai/ |
| **Twitter** | https://x.com/gokiteai |
| **Chain type** | EVM-compatible L1, Proof of Artificial Intelligence (PoAI) |
| **Gas fees** | < $0.000001 |
| **Block time** | ~1 second |

**Description:** Purpose-built L1 blockchain for agentic payments. Provides native support for: agent-to-API payments via X402, verifiable cryptographic identity (ERC-8004), stablecoin settlement, real-time execution, and micro-transactions. Governance is programmable and fine-grained.

**Hackathon tracks (Global Hackathon 2026, announced via @encodeclub March 3, 2026):**
1. **Agentic Commerce**: agents discover, transact, settle autonomously using stablecoins and X402
2. **Agentic Trading**: agents analyze markets, execute on-chain, manage capital across DeFi protocols
3. **Novelty Track**: open-ended AI use cases

**NegotiatorGrid relevance:** **Primary deployment target.** Kite is the natural home chain for NegotiatorGrid — it was designed for exactly the agent-to-agent payment + identity + governance stack that NegotiatorGrid requires. Deploying on Kite means near-zero gas for the high-frequency offer/counteroffer messages, native X402 support for settlement, and ERC-8004 identity for agent trust. NegotiatorGrid should be submitted to the Kite Global Hackathon 2026 Agentic Commerce track.

---

### 5.2 Kite AI ETHDenver 2026 Hackathon — Prior Winners

**Winners (March 2026):**
- **1st Place**: Unknown (full details not publicly indexed)
- **2nd Place**: "Minority Report" — LLM Council system where multiple AI models evaluate decisions together; uses VeriScore verification and Kite Escrow to incentivize novel, verified insights from LLMs. ([YouTube](https://www.youtube.com/watch?v=EjiIdSY8pbQ))
- **2nd Place (alt)**: "Kite Trace Platform" — Demonstrates agentic economy with agents transacting and coordinating on-chain via XMPT (secure communication), X402 (auditable interactions), and ERC-804 (identity). ([YouTube](https://www.youtube.com/watch?v=ya85SxqG_A4))

**NegotiatorGrid relevance:** These projects validate the technology stack. Neither prior winner implemented bilateral price negotiation between agents — this is NegotiatorGrid's differentiated angle. The Kite Escrow mechanism (used by Minority Report) is directly usable as NegotiatorGrid's deal settlement contract.

---

### 5.3 epappas/seipients-agent-to-agent — Agent Bargaining + Blockchain (Closest Prior Art)

*(Covered in Section 3.5 above — referenced here as hackathon prior art)*

This cookie.fun hackathon project (February 2025) is the single closest prior art to NegotiatorGrid. It implements:
- Agent-to-agent auction with bid collection
- JSON-RPC bidding protocol (`BidSubmission`, `PaymentFinalize`)
- Smart contract escrow with Merkle proof release
- On-chain reputation via settlement receipts

**Key differentiators for NegotiatorGrid vs SEIpients:**
- SEIpients: task delegation (one agent hires another) — NegotiatorGrid: bilateral price negotiation (two equal agents bargain)
- SEIpients: no opponent modeling — NegotiatorGrid: Bayesian/ML opponent preference estimation
- SEIpients: Rust/SEI — NegotiatorGrid: Python/Kite (EVM)
- SEIpients: auction (lowest bid wins) — NegotiatorGrid: alternating offers with Nash equilibrium targeting

---

### 5.4 ammonhaggerty/ANEX — Agent Negotiation & Exchange Protocol

| Field | Value |
|---|---|
| **Name** | ammonhaggerty/ANEX |
| **URL** | https://github.com/ammonhaggerty/ANEX |
| **Language** | Protocol spec (Node.js/Python reference) |
| **Stars** | 2 |
| **Last Updated** | November 2024 |

**Description:** Draft protocol spec for AI-powered Personal Agent handshake and data exchange. Uses FIPA-Contract-Net Interaction Protocol for negotiation. Defines phases: Self-Identification → Initiation → Response Handling → Term Negotiation → Data Exchange → Session Termination.

**NegotiatorGrid relevance:** ANEX's FIPA-Contract-Net phase (`CFP` → `Proposal` → `Accept/Reject`) maps precisely to NegotiatorGrid's offer-counteroffer-accept/reject lifecycle. The FIPA ACL message structure (performative, sender, receiver, content JSON, ontology) is a clean wire format template for NegotiatorGrid's WebSocket negotiation messages.

---

### 5.5 mashharuki/AgenticEthereum2025 — Multi-Agent DeFi Hackathon

| Field | Value |
|---|---|
| **Name** | mashharuki/AgenticEthereum2025 |
| **URL** | https://github.com/mashharuki/AgenticEthereum2025 |
| **Language** | TypeScript/JavaScript |
| **Stars** | ~5 |
| **Last Updated** | February 2025 (Agentic Ethereum hackathon) |

**Description:** EigenLayer hackathon submission ($20,000 category). Multiple AI agents discuss, then execute on-chain DeFi operations (staking, swaps) as a group. Sequence diagram shows agent-to-agent coordination with blockchain transaction signing.

**NegotiatorGrid relevance:** Demonstrates the agent coordination + on-chain execution pattern that NegotiatorGrid's settlement layer needs. The LangChain + EigenLayer tool integration shows how to bridge LLM agent reasoning with smart contract execution.

---

### 5.6 Multi-Agent A2A + Blockchain Payment Architecture (arXiv 2507.19550)

| Field | Value |
|---|---|
| **Paper** | "Towards Multi-Agent Economies: Enhancing the A2A Protocol with DLT-based Agent Discovery and Micropayments" |
| **URL** | https://arxiv.org/html/2507.19550v1 |
| **Code** | Prototype on local Hardhat network with USDC + EIP-3009 |

**Description:** Academic paper implementing exactly the NegotiatorGrid use case: blockchain-based agent discovery (smart contract AgentCards), x402 micropayment flow between agents, EIP-3009 signed payments. Five-component prototype: A2A service agent, x402 middleware, blockchain facilitator, smart contract identity, mock USDC.

**NegotiatorGrid relevance:** This is the academic prior art for NegotiatorGrid's core architecture. The four-phase flow (Discovery → 402 Response → Payment Construction → Settlement) is the payment settlement sequence NegotiatorGrid should implement. The authors' implementation code (Hardhat-based) is usable as a development scaffold.

---

### 5.7 SoK: Blockchain Agent-to-Agent Payments (arXiv 2604.03733)

| Field | Value |
|---|---|
| **Paper** | "SoK: Blockchain Agent-to-Agent Payments" |
| **URL** | https://arxiv.org/html/2604.03733v1 |
| **Published** | April 2026 |

**Description:** Systematization of knowledge for blockchain-based A2A payments. Four-stage lifecycle: Discovery, Authorization, Execution, Settlement. Identifies key challenges: weak intent binding, misuse under valid authorization, payment–service decoupling. Notably flags that "negotiating payable terms" (variable price negotiation) is an open problem in current x402/A2A systems.

**NegotiatorGrid relevance:** This paper explicitly identifies price negotiation as a gap in current agent payment systems: *"payment terms may not always be fixed upfront... agent-mediated interactions can involve iterative or multi-round negotiation over price"*. NegotiatorGrid directly fills this gap. Citing this paper positions NegotiatorGrid at the research frontier.

---

## Summary Table

| Repo / Resource | Category | Language | Stars | Last Updated | Priority for NegotiatorGrid |
|---|---|---|---|---|---|
| [yasserfarouk/negmas](https://github.com/yasserfarouk/negmas) | Opponent Modeling | Python | 85 | Mar 2026 | ⭐⭐⭐ Critical |
| [autoneg/anl](https://github.com/autoneg/anl) | Opponent Modeling | Python | — | Mar 2025 | ⭐⭐⭐ Critical |
| [GENIUS / GeniusWeb](https://ii.tudelft.nl/genius/) | Opponent Modeling | Java + Python adapter | — | Active | ⭐⭐ High |
| [aniltrue/NegoLog](https://github.com/aniltrue/NegoLog) | Opponent Modeling | Python | 7 | Mar 2025 | ⭐⭐ High |
| [kushalchawla/opponent-modeling](https://github.com/kushalchawla/opponent-modeling) | Opponent Modeling | Python | ~10 | 2022 | ⭐ Medium |
| [velochy/rl-bargaining](https://github.com/velochy/rl-bargaining) | Game Theory / RL | Python | ~5 | 2019 | ⭐ Medium |
| [FranxYao/GPT-Bargaining](https://github.com/FranxYao/GPT-Bargaining) | Opponent Modeling | Python | 208 | 2023 | ⭐⭐ High |
| [lechmazur/pact](https://github.com/lechmazur/pact) | Opponent Modeling | Python | 29 | Aug 2025 | ⭐⭐ High |
| [gambitproject/gambit](https://github.com/gambitproject/gambit) | Nash Bargaining | C++/Python | 435 | Jan 2025 | ⭐⭐⭐ Critical |
| [gucci-j/predicting-nash](https://github.com/gucci-j/predicting-nash) | Nash Bargaining | Python | ~5 | Archived | ⭐ Medium |
| [krichelj/PyDiffGame](https://github.com/krichelj/PyDiffGame) | Nash / Differential Games | Python | 52 | Feb 2025 | ⭐ Medium |
| [SivamPillai/Auctions](https://github.com/SivamPillai/Auctions) | Mechanism Design | Python | ~5 | 2017 | ⭐ Low |
| [alimama-tech/AuctionNet](https://github.com/alimama-tech/AuctionNet) | Auction Benchmark | Python | ~50 | Dec 2024 | ⭐⭐ High |
| [savente93/pyneg](https://github.com/savente93/pyneg) | Concession Strategy | Python | 4 | Archived | ⭐ Medium |
| [ERC-8004 EIP](https://eips.ethereum.org/EIPS/eip-8004) | Agent Identity | Solidity | — | Jan 2026 mainnet | ⭐⭐⭐ Critical |
| [decentralized-identity/veramo](https://github.com/decentralized-identity/veramo) | DID on EVM | TypeScript | 534 | Feb 2026 | ⭐⭐ High |
| [mcpdotdirect/evm-mcp-server](https://github.com/mcpdotdirect/evm-mcp-server) | EVM Agent Tools | TypeScript | ~200 | Mar 2025 | ⭐⭐ High |
| [coinbase/x402](https://github.com/coinbase/x402) | Agent Payments | TS/Python/Go | 41 | Apr 2026 | ⭐⭐⭐ Critical |
| [epappas/seipients-agent-to-agent](https://github.com/epappas/seipients-agent-to-agent) | A2A Auction + Settlement | Rust | 2 | Feb 2025 | ⭐⭐⭐ Critical (Prior Art) |
| [agntcy/oasf](https://github.com/agntcy/oasf/tree/v0.8.0) | Agent Schema | — | — | Active | ⭐⭐ High |
| [ag2ai/realtime-agent-over-websockets](https://github.com/ag2ai/realtime-agent-over-websockets) | WebSocket | Python | 10 | Jan 2025 | ⭐⭐⭐ Critical |
| [Youssef-Adell/BidX-API](https://github.com/Youssef-Adell/BidX-API) | Real-Time Bidding | C# | ~30 | Feb 2025 | ⭐⭐ High |
| [gustavomazzoni/auction-system](https://github.com/gustavomazzoni/auction-system) | Real-Time Auction | JS | ~50 | 2016 | ⭐ Medium |
| [ammonhaggerty/ANEX](https://github.com/ammonhaggerty/ANEX) | Negotiation Protocol | Spec | 2 | Nov 2024 | ⭐⭐ High |
| [GoKite.ai](https://gokite.ai) | Deployment Chain | — | — | Active | ⭐⭐⭐ Critical |
| [arXiv 2507.19550](https://arxiv.org/html/2507.19550v1) | A2A + Blockchain Paper | — | — | 2025 | ⭐⭐⭐ Critical |
| [arXiv 2604.03733](https://arxiv.org/html/2604.03733v1) | SoK A2A Payments | — | — | Apr 2026 | ⭐⭐ High |

---

## Key Gaps Identified

1. **No open-source Rubinstein alternating-offers implementation** exists as a standalone Python library with time-discounting. The closest is `velochy/rl-bargaining` (incomplete, RL-based) and the theoretical description in Gambit. NegotiatorGrid should implement this as a novel contribution.

2. **No ERC-8004 reference implementation repo found** — the EIP is live on mainnet but the authors have not published a public GitHub repo with the contract code as of research date. The Ethereum Magicians discussion thread is the best source of implementation details. NegotiatorGrid's own ERC-8004 contract deployment would be novel.

3. **No Kite AI hackathon repos are publicly indexed on GitHub** with `kite-ai` or `gokite` topics for 2025–2026 project submissions. The prior hackathon was ETHDenver (March 2026); the Global Hackathon 2026 was announced March 3, 2026. No project repos from these events appear in public GitHub search, suggesting NegotiatorGrid would be entering relatively clear ground.

4. **Agent-to-agent price negotiation + blockchain settlement** (as opposed to agent payment for fixed-price services) is explicitly flagged as an open problem in the SoK paper (arXiv 2604.03733, April 2026). NegotiatorGrid directly fills this gap in the academic literature.

---

*Research compiled: 2026. All URLs verified during collection.*
