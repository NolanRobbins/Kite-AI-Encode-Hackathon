# NegotiatorGrid

**Agent-to-agent price negotiation protocol with game-theoretic strategies, x402 settlement, and on-chain attestation on Kite AI.**

[![Kite Testnet](https://img.shields.io/badge/Kite_Testnet-Chain_2368-blue)](<https://testnet.kitescan.ai>)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](<https://python.org>)
[![Solidity](https://img.shields.io/badge/Solidity-0.8.26-purple)](<https://soliditylang.org>)
[![Tests](https://img.shields.io/badge/Tests-33_Python_|_17_Solidity-brightgreen)](#testing)
[![License](https://img.shields.io/badge/License-Apache_2.0-orange)](LICENSE)

---

## The Problem

Today's agent-to-agent payments are **take-it-or-leave-it**. A seller sets a price, a buyer pays it or walks away. There is no negotiation.

The most comprehensive survey of blockchain A2A payments — Zhang et al., *"SoK: Blockchain Agent-to-Agent Payments"* (arXiv:2604.03733, April 2026) — explicitly identifies this as an open problem:

> *"Agent-mediated interactions can involve iterative or multi-round negotiation over price, volume, or service scope, as reflected in evolving x402-style pricing models such as 'up-to' pricing and negotiated schemes. Therefore, lifecycle models should account for how payable conditions are formed across interactions, rather than assuming they are fully specified prior to authorization and execution."*
> — Section 5.6, Future Directions [1]

AgenticPay [2] benchmarks LLM negotiation but has no settlement layer. CPMM [3] formalizes bilateral games over HTTP 402 but remains purely theoretical. Agent-OSI [4] builds a six-layer stack with escrow but treats negotiation as off-chain coordination.

**No existing system combines bilateral agent negotiation, x402 payment settlement, on-chain deal attestation, and MCP dynamic discovery.**

NegotiatorGrid fills that gap.

---

## The Solution

NegotiatorGrid adds a **negotiation phase before x402 settlement**. Instead of fixed pricing, agents discover each other via MCP, verify on-chain identities, negotiate price through multi-round game-theoretic bargaining, settle payments atomically via x402, and attest every deal on Kite's blockchain.

### 6-Stage Pipeline

```
1. Discovery    → Agent queries Kite MCP server, finds counterparty capabilities
2. Identity     → ERC-8004 on-chain identity resolved, reputation score retrieved
3. Negotiation  → NegMAS bilateral bargaining (SAO protocol, Boulware concession)
4. Binding      → Agreed price → x402 PaymentRequirements + ERC-4337 session key
5. Settlement   → x402 payment flow via Kite Facilitator on Kite testnet
6. Attestation  → DealRecord written on-chain with negotiation metadata
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        NegotiatorGrid                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────┐    ┌─────────────────────────────────┐  │
│  │   Next.js Dashboard │    │    MCP Dynamic Discovery        │  │
│  │   - Live negotiation│    │    - Agent capability queries   │  │
│  │     visualization   │    │    - Service listing/matching   │  │
│  │   - Deal history    │    │    - mcp.prod.gokite.ai         │  │
│  │   - Reputation view │    │                                 │  │
│  └────────┬───────────┘    └──────────┬──────────────────────┘  │
│           │                           │                          │
│  ┌────────▼───────────────────────────▼──────────────────────┐  │
│  │              A2A Protocol Transport Layer                  │  │
│  │  - AgentCard discovery + x402 extension declaration       │  │
│  │  - JSON-RPC messaging (offers, counteroffers, accept/     │  │
│  │    reject) via A2A Task lifecycle                          │  │
│  │  - Fork of google-agentic-commerce/a2a-x402               │  │
│  └────────┬───────────────────────────┬──────────────────────┘  │
│           │                           │                          │
│  ┌────────▼───────────┐    ┌─────────▼──────────────────────┐  │
│  │  Negotiation Engine │    │      Payment Layer              │  │
│  │                     │    │                                 │  │
│  │  NegMAS SAO Protocol│    │  x402 SDK (Python)              │  │
│  │  - SAOMechanism     │    │  - PaymentRequirements from     │  │
│  │  - BOA components:  │    │    negotiated price             │  │
│  │    B: Bidding       │    │  - FacilitatorClient verify +   │  │
│  │       strategy      │    │    settle                       │  │
│  │    O: Opponent      │    │  - fast-x402 seller middleware  │  │
│  │       modeling      │    │                                 │  │
│  │    A: Acceptance    │    │  AA Wallet (ERC-4337)           │  │
│  │       criteria      │    │  - Session key spending limit   │  │
│  │                     │    │    = negotiated price            │  │
│  │  LLM Reasoning      │    │  - UserOperation construction  │  │
│  │  - Natural language │    │                                 │  │
│  │    offer generation │    │  Kite Facilitator               │  │
│  │  - Context-aware    │    │  - 0x1234...3C78b              │  │
│  │    concession logic │    │  - Verify + settle on Kite     │  │
│  │                     │    │                                 │  │
│  │  Gambit Validation  │    │                                 │  │
│  │  - Nash equilibrium │    │                                 │  │
│  │    computation      │    │                                 │  │
│  │  - Strategy profile │    │                                 │  │
│  │    validation       │    │                                 │  │
│  └────────┬───────────┘    └──────────┬──────────────────────┘  │
│           │                           │                          │
│  ┌────────▼───────────────────────────▼──────────────────────┐  │
│  │                   Identity Layer                           │  │
│  │  ERC-8004 (Draft EIP)                                     │  │
│  │  - Identity Registry: ERC-721 agent NFT with metadata     │  │
│  │  - Reputation Registry: on-chain feedback (giveFeedback,  │  │
│  │    getSummary) → feeds into negotiation strategy           │  │
│  │  - Validation Registry: stake-secured re-execution        │  │
│  │  - Links to A2A AgentCard + MCP endpoint via agentURI     │  │
│  └────────────────────────┬──────────────────────────────────┘  │
│                           │                                      │
│  ┌────────────────────────▼──────────────────────────────────┐  │
│  │                   Chain Layer                              │  │
│  │  Kite Testnet (Chain ID 2368, EVM-compatible)             │  │
│  │  - RPC: https://rpc-testnet.gokite.ai                    │  │
│  │  - Explorer: https://testnet.kitescan.ai                  │  │
│  │  - Test USDT: 0x0fF5...e63                                │  │
│  │                                                            │  │
│  │  DealRecord Contract (Solidity)                            │  │
│  │  - recordDeal(buyerAgent, sellerAgent, agreedPrice,        │  │
│  │    negotiationRounds, finalTermsHash, x402TxHash)          │  │
│  │  - getDealHistory(agentId) → reputation feed               │  │
│  │  - Events: DealRecorded, DisputeRaised                     │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Data Flow: A Complete Negotiation Cycle

```
1. Discovery    Agent A queries MCP server → finds Agent B's capabilities + AgentCard
2. Identity     Agent A resolves Agent B's ERC-8004 identity → reads reputation from
                Reputation Registry (getSummary) → injects reputation score into
                negotiation strategy parameters
3. Negotiation  A2A Task created → NegMAS SAOMechanism runs multi-round bilateral
                negotiation:
                  Round 1: Agent A proposes $0.08 (LLM generates NL offer)
                  Round 2: Agent B counters $0.12 (opponent model updates)
                  Round 3: Agent A concedes to $0.10 (gambit validates Nash)
                  Round 4: Agent B accepts (acceptance criteria met)
4. Binding      Agreed price ($0.10) → x402 PaymentRequirements constructed →
                ERC-4337 session key created with spending limit = $0.10
5. Settlement   x402 payment flow: 402 → X-PAYMENT header → Kite Facilitator
                verifies → settles on Kite testnet
6. Attestation  DealRecord.recordDeal() called with negotiation metadata →
                on-chain event emitted → reputation updated
```

---

## Key Features

- **NegMAS-powered bilateral negotiation** — SAO (Stacked Alternating Offers) protocol with Boulware time-dependent concession, the same framework used in ANAC international negotiation competitions
- **Opponent modeling** — Linear regression on concession patterns estimates counterparty reservation prices in real time
- **Nash equilibrium guardrail** — pygambit computes Nash equilibria for the bilateral game; deals outside the equilibrium range are flagged as exploitative
- **LLM natural language offers** — GPT-4o-mini generates human-readable offer explanations with context-aware persuasion arguments
- **ERC-8004 agent identity** — On-chain ERC-721 agent registration with structured reputation scores that feed into negotiation strategy parameters
- **Reputation-conditioned strategies** — Agents adjust concession speed, initial offers, and walk-away thresholds based on counterparty's on-chain reputation
- **x402 payment settlement** — Negotiated price flows directly into x402 PaymentRequirements; settled atomically on Kite testnet via the Kite Facilitator
- **DealRecord on-chain attestation** — Every deal is permanently recorded with buyer/seller identities, agreed price, round count, terms hash, and x402 tx hash
- **Real-time dashboard** — Next.js frontend with live price convergence visualization, agent identity cards, and deal history

---

## Quick Start

```bash
git clone https://github.com/NolanRobbins/Kite-AI-Encode-Hackathon.git
cd Kite-AI-Encode-Hackathon
pip install -e .
python demo.py
```

The demo runs a complete 7-round bilateral negotiation between a buyer agent ("DataBuyer-Alpha") and a seller agent ("WeatherPro-Service"), including ERC-8004 identity registration, reputation lookup, NegMAS negotiation with opponent modeling, Nash equilibrium validation, x402 settlement, and on-chain attestation — all with formatted terminal output and an ASCII price convergence chart.

### Requirements

- Python 3.11+
- Node.js 20+ (for smart contracts)
- See [Configuration](#configuration) for environment variables

---

## Project Structure

```
negotiatorgrid/
├── core/
│   ├── negotiation.py          # NegotiationSession — NegMAS SAOMechanism integration
│   ├── opponent_model.py       # OpponentModeler — linear regression on concession patterns
│   ├── nash_guardrail.py       # NashGuardrail — pygambit equilibrium validation
│   ├── reputation.py           # ReputationFeed — on-chain reputation → strategy params
│   ├── settlement.py           # X402Settler — x402 payment construction + submission
│   ├── attestation.py          # AttestationPipeline — DealRecord on-chain writing
│   └── types.py                # Core data types (Offer, Deal, AgentProfile)
├── contracts/
│   ├── identity.py             # IdentityClient — ERC-8004 Identity Registry wrapper
│   ├── reputation_client.py    # ReputationClient — on-chain reputation queries
│   └── deal_record.py          # DealRecordClient — attestation contract interaction
├── llm/
│   └── offer_generator.py      # OfferGenerator — GPT-4o-mini NL offer generation
├── api/
│   ├── server.py               # FastAPI server setup
│   ├── routes.py               # REST API endpoints
│   ├── agent_card.py           # A2A AgentCard metadata
│   └── websocket.py            # WebSocket for live negotiation updates
├── executors/
│   └── negotiation.py          # NegotiationExecutor — orchestrates full pipeline
├── utils/
│   ├── web3_helpers.py         # Web3 connection + contract helpers
│   └── mock_facilitator.py     # Mock x402 facilitator for testing
└── config.py                   # Configuration from environment

contracts/
├── src/
│   ├── DealRecord.sol          # On-chain deal attestation (recordDeal, getDealHistory)
│   ├── IdentityRegistry.sol    # ERC-721 agent registration (ERC-8004)
│   └── ReputationRegistry.sol  # Structured reputation feedback (giveFeedback, getSummary)
├── test/                       # Hardhat test suite (17 tests)
└── script/                     # Deployment scripts

dashboard/                      # Next.js real-time negotiation dashboard
tests/                          # Python test suite (33 tests)
demo.py                         # Golden path demo entrypoint
```

---

## Smart Contracts

All contracts are deployed on **Kite Testnet** (Chain ID 2368) and written in Solidity 0.8.26.

| Contract | Purpose | Key Functions |
|----------|---------|---------------|
| **DealRecord.sol** | On-chain attestation of negotiation outcomes | `recordDeal()`, `getDealHistory()`, `getDeal()` |
| **IdentityRegistry.sol** | ERC-721 agent identity registration (ERC-8004) | `registerAgent()`, `getAgent()`, `setWallet()` |
| **ReputationRegistry.sol** | Structured on-chain reputation feedback | `giveFeedback()`, `getSummary()`, `getHistory()` |

**Chain details:**
- **RPC**: `https://rpc-testnet.gokite.ai`
- **Explorer**: [testnet.kitescan.ai](https://testnet.kitescan.ai)
- **Test USDT**: `0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63`
- **Kite Facilitator**: `0x12343e649e6b2b2b77649DFAb88f103c02F3C78b`

### Running Solidity Tests

```bash
cd contracts
npm install
npx hardhat test    # 17 passing tests
```

---

## Research Contributions

NegotiatorGrid fills **five publishable research gaps** validated against the full academic landscape. No prior system combines all of these:

### 1. Negotiation-to-Payment Atomicity

The agreed price from multi-round negotiation is cryptographically bound to the x402 payment execution. The deal cannot settle at a price that was not agreed upon. A `finalTermsHash` (keccak256 of the negotiation transcript) is stored on-chain and can be independently verified.

> *Prior art gap*: A402 [5] achieves payment-to-service atomicity; Agent-OSI [4] keeps negotiation off-chain. **No system binds negotiation to payment.** [1, Section 5.3]

### 2. Reputation-Conditioned Negotiation Strategy

On-chain ERC-8004 reputation scores feed directly into the LLM negotiation agent's strategy parameters. Against a high-reputation seller (4.8 stars), the buyer concedes faster and opens with a fairer price. Against a low-reputation seller (3.2 stars), the buyer opens aggressively and concedes slowly — saving up to 30% per deal.

> *Prior art gap*: Louta et al. [6] condition on centralized reputation (2006, pre-blockchain). AgentCity [7] uses reputation for reward scaling, not strategy conditioning. **No system feeds on-chain reputation into live LLM negotiation.** [1, Section 5.6]

### 3. MCP as Negotiation Transport

Agents discover counterparties, exchange offers, and finalize deals through MCP tool calls, making negotiation composable with any MCP-compatible agent framework.

> *Prior art gap*: Soni et al. [8] use MCP for enterprise data integration (human-facing). Li & Xie [9] identify "semantic negotiation mechanisms" as a needed advancement but don't implement any. **No system uses MCP as agent-to-agent negotiation transport.**

### 4. ERC-4337 Session Keys Derived from Negotiation Outcomes

After negotiation concludes, the agreed price is encoded into an ERC-4337 UserOperation with a session key whose spending limit equals exactly the negotiated amount. The wallet physically cannot overspend.

> *Prior art gap*: The SoK [1, Section 4.2] discusses static ERC-4337 spending limits. **No system derives session key limits dynamically from negotiation outcomes.**

### 5. Anti-Collusion via On-Chain Deal Attestation

Every deal is attested on-chain with full metadata, creating a transparent price history. Statistical anomaly detection over the attestation graph can flag suspiciously convergent pricing between agents that repeatedly transact — collusion detection that is impossible when deals are off-chain.

> *Prior art gap*: "On the Fragility of AI Agent Collusion" [10] simulates Bertrand pricing but has no blockchain or marketplace context. **No system addresses anti-collusion for LLM-to-LLM agent service marketplaces with on-chain evidence.**

---

## Configuration

Copy `.env.example` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|----------|-------------|---------|
| `KITE_RPC_URL` | Kite testnet RPC endpoint | `https://rpc-testnet.gokite.ai/` |
| `KITE_CHAIN_ID` | Kite testnet chain ID | `2368` |
| `KITE_EXPLORER_URL` | Block explorer URL | `https://testnet.kitescan.ai/` |
| `PRIVATE_KEY` | Deployer/agent wallet private key | — |
| `DEALRECORD_CONTRACT_ADDR` | Deployed DealRecord contract address | — |
| `IDENTITY_REGISTRY_ADDR` | Deployed IdentityRegistry address | — |
| `REPUTATION_REGISTRY_ADDR` | Deployed ReputationRegistry address | — |
| `KITE_FACILITATOR_URL` | x402 facilitator endpoint | `https://facilitator.pieverse.io` |
| `KITE_FACILITATOR_ADDR` | Kite Facilitator contract address | `0x12343e649e6b2b2b77649DFAb88f103c02F3C78b` |
| `KITE_TEST_USDT_ADDR` | Test USDT token address | `0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63` |
| `OPENAI_API_KEY` | OpenAI API key for LLM offer generation | — |
| `OPENAI_MODEL` | LLM model for natural language offers | `gpt-4o-mini` |
| `KITE_MCP_ENDPOINT` | Kite MCP server endpoint | `https://neo.dev.gokite.ai/v1/mcp` |
| `API_HOST` | API server bind address | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |

---

## Testing

```bash
# Python tests (negotiation engine, integration pipeline)
pytest tests/                              # 33 tests

# Solidity tests (smart contracts)
cd contracts && npx hardhat test           # 17 tests
```

### What's Tested

**Python tests** cover:
- Negotiation agreement within ZOPA (Zone of Possible Agreement)
- Timeout behavior when no agreement is possible
- Round counting and state management
- Opponent model estimation accuracy
- Nash guardrail exploitation detection and fair deal validation
- Natural language offer generation
- Full pipeline integration: NegotiationSession → X402Settler → AttestationPipeline

**Solidity tests** cover:
- Agent registration and identity lookup
- Reputation feedback submission and aggregation
- Deal recording and history retrieval
- Access control and edge cases

---

## Tech Stack

| Library | Purpose | Why This Library |
|---------|---------|------------------|
| [NegMAS](https://github.com/yasserfarouk/negmas) | Bilateral negotiation engine (SAO protocol) | Battle-tested through all ANAC competitions; BOA architecture separates bidding, opponent modeling, and acceptance |
| [pygambit](https://github.com/gambitproject/gambit) | Nash equilibrium computation | Standard game theory library; Lemke-Howson algorithm for 2-player games |
| [web3.py](https://github.com/ethereum/web3.py) | Blockchain interaction | Standard Python Ethereum library |
| [eth-account](https://github.com/ethereum/eth-account) | ERC-4337 UserOperation signing | Transaction signing and account abstraction |
| [OpenAI SDK](https://github.com/openai/openai-python) | Natural language offer generation | GPT-4o-mini for cost-effective per-round LLM calls |
| [FastAPI](https://fastapi.tiangolo.com/) | REST API + WebSocket server | Async-native, OpenAPI docs, WebSocket support |
| [Hardhat](https://hardhat.org/) | Smart contract development + testing | Industry-standard Solidity toolchain |
| [Next.js](https://nextjs.org/) | Real-time negotiation dashboard | React SSR with WebSocket integration |
| [Pydantic](https://docs.pydantic.dev/) | Data validation and serialization | Type-safe configuration and message schemas |
| [httpx](https://www.python-httpx.org/) | Async HTTP client | x402 facilitator communication |

---

## Kite Primitives Used

| Primitive | How NegotiatorGrid Uses It |
|-----------|---------------------------|
| **Kite Chain** (Chain ID 2368) | All smart contracts deployed here; DealRecord attestation, IdentityRegistry, ReputationRegistry |
| **x402 Protocol** | Payment settlement after negotiation — agreed price flows into PaymentRequirements, settled via Kite Facilitator |
| **MCP** (Kite MCP Server) | Agent discovery — buyer finds seller capabilities via `https://neo.dev.gokite.ai/v1/mcp` |
| **ERC-8004** | Agent identity — ERC-721 tokenized agent entries with reputation scores that condition negotiation strategies |
| **Kite Facilitator** | x402 verify + settle endpoint at `0x12343e649e6b2b2b77649DFAb88f103c02F3C78b` |
| **Kite Test USDT** | Settlement currency for agent-to-agent payments at `0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63` |

---

## How It Compares

| Capability | Agentic Markets (ETHDenver 3rd) | Kite Trace (ETHDenver 2nd) | NegotiatorGrid |
|---|---|---|---|
| Multi-round negotiation | Single counter-offer | Fixed bounty pricing | Multi-round with concessions |
| Opponent modeling | None | None | Linear regression on concession patterns |
| Game-theoretic pricing | None | None | Nash equilibrium validation (pygambit) |
| Concession strategies | None | None | Configurable (Boulware, linear, conceder) |
| Dynamic price discovery | Seller sets price | Requester sets price | Price emerges from negotiation |
| x402 settlement | Yes | Yes | Yes |
| ERC-8004 identity | Yes (Passport) | Yes | Yes + reputation-conditioned strategy |
| MCP discovery | Via Kite API | Yes | Yes |
| On-chain attestation | No | Trust anchors | Full DealRecord with terms hash |

---

## References

1. Zhang et al., "SoK: Blockchain Agent-to-Agent Payments," arXiv:2604.03733, April 2026 — https://arxiv.org/abs/2604.03733
2. "AgenticPay: A Multi-Agent LLM Negotiation System," arXiv:2602.06008, Feb 2026 — https://arxiv.org/abs/2602.06008
3. Huang et al., "Capability-Priced Micro-Markets (CPMM)," March 2026 — https://www.semanticscholar.org/paper/3bb6f801c96fe9c90eeed45cdc165fe02492c776
4. Xu et al., "Agent-OSI," arXiv:2602.13795, Feb 2026 — https://arxiv.org/abs/2602.13795
5. Li et al., "A402: Binding Cryptocurrency Payments to Service Execution," arXiv:2603.01179, March 2026 — https://arxiv.org/abs/2603.01179
6. Louta et al., "Reputation Based Intelligent Agent Negotiation in e-Marketplaces," 2006 — https://www.scitepress.org/papers/2006/14266/14266.pdf
7. "AgentCity: Constitutional Governance for Autonomous Agent Systems," arXiv:2604.07007, April 2026 — https://arxiv.org/html/2604.07007v1
8. Soni et al., "LLM and MCP Based Automated Deal Pricing Negotiation," IJAIA 2025 — https://aircconline.com/ijaia/V16N5/16525ijaia04.pdf
9. Li & Xie, "From Glue-Code to Protocols: A2A and MCP Integration," arXiv:2505.03864, 2025 — https://arxiv.org/abs/2505.03864
10. "On the Fragility of AI Agent Collusion," arXiv:2603.20281, March 2026 — https://arxiv.org/html/2603.20281v1
11. Hua et al., "Game-theoretic LLM: Agent Workflow for Negotiation Games," arXiv:2411.05990, Nov 2024 — https://arxiv.org/abs/2411.05990
12. Xu, "The Agent Economy," arXiv:2602.14219, Feb 2026 — https://arxiv.org/abs/2602.14219
13. Hou et al., "MCP Security Threats and Future Directions," arXiv:2503.23278, March 2025 — https://arxiv.org/abs/2503.23278
14. ERC-8004: Trustless Agents — https://eips.ethereum.org/EIPS/eip-8004
15. x402 Protocol Documentation — https://docs.x402.org
16. NegMAS Documentation — https://negmas.readthedocs.io/en/latest/
17. Gambit Documentation — https://gambitproject.readthedocs.io/en/latest/
18. Kite AI Documentation — https://docs.gokite.ai
19. A2A Protocol — https://agent2agent.info
20. x402 Whitepaper — https://www.x402.org/x402-whitepaper.pdf

---

## License

[Apache 2.0](LICENSE) — see [LICENSE](LICENSE) for the full text.

---

Built for the [Kite AI x Encode Club Global Hackathon](https://www.encode.club/kite-hackathon) (March 27 - April 26, 2026) — Novel Track.
