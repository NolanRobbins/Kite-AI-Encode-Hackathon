# Graph Report - C:\Users\Robbinhood\OneDrive\Desktop\VS Code Projects\Hackathons\Kite AI Encode Hackathon  (2026-05-12)

## Corpus Check
- 91 files · ~272,846 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 985 nodes · 2892 edges · 88 communities detected
- Extraction: 35% EXTRACTED · 65% INFERRED · 0% AMBIGUOUS · INFERRED: 1893 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 87|Community 87]]

## God Nodes (most connected - your core abstractions)
1. `OpponentModeler` - 126 edges
2. `NegotiationOffer` - 126 edges
3. `NegotiationConfig` - 119 edges
4. `NegotiationSession` - 116 edges
5. `OfferGenerator` - 109 edges
6. `NashGuardrail` - 108 edges
7. `NegotiationResult` - 65 edges
8. `DealRecordClient` - 60 edges
9. `AgentConfig` - 57 edges
10. `X402Settler` - 55 edges

## Surprising Connections (you probably didn't know these)
- `LocalRegistry` --calls--> `registry()`  [INFERRED]
  C:\Users\Robbinhood\OneDrive\Desktop\VS Code Projects\Hackathons\Kite AI Encode Hackathon\negotiatorgrid\discovery\local_registry.py → C:\Users\Robbinhood\OneDrive\Desktop\VS Code Projects\Hackathons\Kite AI Encode Hackathon\tests\test_surprise_api.py
- `AgentInfo` --uses--> `NegotiationSession`  [INFERRED]
  C:\Users\Robbinhood\OneDrive\Desktop\VS Code Projects\Hackathons\Kite AI Encode Hackathon\demo.py → C:\Users\Robbinhood\OneDrive\Desktop\VS Code Projects\Hackathons\Kite AI Encode Hackathon\negotiatorgrid\core\negotiation.py
- `AgentInfo` --uses--> `OpponentModeler`  [INFERRED]
  C:\Users\Robbinhood\OneDrive\Desktop\VS Code Projects\Hackathons\Kite AI Encode Hackathon\demo.py → C:\Users\Robbinhood\OneDrive\Desktop\VS Code Projects\Hackathons\Kite AI Encode Hackathon\negotiatorgrid\core\opponent_model.py
- `AgentInfo` --uses--> `NashGuardrail`  [INFERRED]
  C:\Users\Robbinhood\OneDrive\Desktop\VS Code Projects\Hackathons\Kite AI Encode Hackathon\demo.py → C:\Users\Robbinhood\OneDrive\Desktop\VS Code Projects\Hackathons\Kite AI Encode Hackathon\negotiatorgrid\core\nash_guardrail.py
- `AgentInfo` --uses--> `NegotiationConfig`  [INFERRED]
  C:\Users\Robbinhood\OneDrive\Desktop\VS Code Projects\Hackathons\Kite AI Encode Hackathon\demo.py → C:\Users\Robbinhood\OneDrive\Desktop\VS Code Projects\Hackathons\Kite AI Encode Hackathon\negotiatorgrid\core\types.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (116): Enum, NashGuardrail, aspiration_value(), BuyerNegotiator, _exponent(), NegotiationSession, NegotiationState, price_from_aspiration() (+108 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (101): AttestationPipeline, _compute_deal_hash(), Deal attestation pipeline — binds negotiation outcomes to on-chain records., Retrieve all deal attestations for an agent., Best-effort reputation feedback — never raises., Compute keccak256(buyer, seller, price, timestamp, nonce).      Uses abi.encod, Orchestrates the full post-negotiation attestation flow:      1. Compute deal, Run the full attestation pipeline. Returns the deal hash hex string. (+93 more)

### Community 2 - "Community 2"
Cohesion: 0.04
Nodes (85): NegotiatorGrid API package., default_registry(), LocalRegistry, In-process service catalog used as the discovery fallback.  Rationale (from ``, Thread-safe (single-threaded async) service catalog.      The registry exposes, Return services matching the given filters., Return a fresh registry populated with the default fixture., One negotiable service entry.      Matches the shape of Kite's ``get_service_d (+77 more)

### Community 3 - "Community 3"
Cohesion: 0.03
Nodes (86): build_app(), _fetch_live_weather(), from_env(), _module_app(), FastAPI application factory for the Surprise API seller.  Endpoints:  * ``GE, Construct the Surprise API FastAPI application.      Args:         settings:, Used by ``uvicorn surprise_api.app:app``., SurpriseAPISettings (+78 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (63): compare_status(), _high_rep_scenario(), _low_rep_scenario(), _negotiation_id(), Act 3 side-by-side compare: high-reputation vs low-reputation buyer scenarios., Start two parallel negotiations: high-rep vs low-rep buyer framing., Poll negotiation status for a compare pair started via POST /compare., Cooperative high-trust buyer; tends to settle at a higher price. (+55 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (51): x402 payment protocol configuration., X402Config, inflate_payment_requirements(), Act 5 — malicious seller simulation (demo / tests only).  After an honest bila, Return a **copy** of *payment_requirements* with ``maxAmountRequired``     mult, MockFacilitator, Mock x402 facilitator for local testing.  Used when KITE_FACILITATOR_URL is no, Simulates the x402 facilitator verify/settle endpoints.      Every call succee (+43 more)

### Community 6 - "Community 6"
Cohesion: 0.11
Nodes (19): _agent_exponent(), build_counteroffer_message(), build_offer_message(), _build_scaled_core_config(), compute_deal_hash(), _edge_case_status(), _group_core_offers_by_round(), _make_grid_modelers() (+11 more)

### Community 7 - "Community 7"
Cohesion: 0.1
Nodes (22): A2A protocol + a2a-x402 payment extension, AgenticPay (Liu et al., arXiv:2602.06008), ANEX/FIPA performatives mapped to A2A JSON-RPC, AP2-kite fork (variable PaymentCurrencyAmount, negotiation roadmap), ASTRA (Kwon et al., EMNLP 2025 / arXiv:2503.07129), gokite-aa-sdk (ERC-4337, ClientAgentVault), GPT-Bargaining (Yao Fu et al., arXiv:2305.10142), Kite Programmable Trust Layer (+14 more)

### Community 8 - "Community 8"
Cohesion: 0.13
Nodes (9): deployFixture(), NegotiationBroadcaster, WebSocket endpoint for live negotiation streaming., Manages WebSocket connections and broadcasts negotiation events., Send a round update to all connected clients., Send the final negotiation result to all connected clients., Send an arbitrary event to all connected clients., WebSocket endpoint that streams negotiation events to dashboard clients. (+1 more)

### Community 9 - "Community 9"
Cohesion: 0.17
Nodes (11): _price_grid(), Nash equilibrium guardrail — game-theoretic deal validation.  Discretises the, Find pure-strategy Nash equilibria by best-response enumeration.          For, When no pure-strategy NE is found, use the Nash Bargaining Solution., Create evenly-spaced price grid., Compute Nash equilibria and validate negotiated prices.      Parameters     -, Find Nash equilibrium price over a discretised price grid.          Both *buye, Check whether *agreed_price* is close to Nash equilibrium.          Returns a (+3 more)

### Community 10 - "Community 10"
Cohesion: 0.13
Nodes (13): explorer_address_url(), explorer_tx_url(), get_account(), get_contract(), get_web3(), load_abi(), Web3 helpers for Kite testnet interaction., Build a KiteScan URL for a transaction hash. (+5 more)

### Community 11 - "Community 11"
Cohesion: 0.16
Nodes (7): error(), getJsonSchemaFiles(), getOpenApiFiles(), validateFieldDescriptions(), validateModelExamples(), validateOpenApiDescriptions(), validateOpenApiExamples()

### Community 12 - "Community 12"
Cohesion: 0.12
Nodes (15): AppConfig, ContractConfig, KiteConfig, LLMConfig, MCPConfig, NegotiationConfig, NegotiatorGrid configuration — loads from environment variables., Kite blockchain network configuration. (+7 more)

### Community 13 - "Community 13"
Cohesion: 0.22
Nodes (9): Buyer 8-step loop, deal_hash cryptographic binding, DealRecord / IDealRecord, Gap C MCP as negotiation transport, NegGridOpponentModel hybrid, NegMAS, NegotiatorGrid, SoK Blockchain A2A Payments (+1 more)

### Community 14 - "Community 14"
Cohesion: 0.39
Nodes (7): _deployed_addresses_path(), _load_env_file(), main(), Return the ``.env`` as a list of lines (creating it from example if missing)., Replace ``KEY=...`` in *lines* or append it. Preserves other keys., sync(), _upsert_env_line()

### Community 15 - "Community 15"
Cohesion: 0.33
Nodes (4): ApiError, request(), startNegotiation(), tendencyToStrategy()

### Community 16 - "Community 16"
Cohesion: 0.33
Nodes (5): agent_card(), lifespan(), FastAPI application for NegotiatorGrid., Application startup / shutdown lifecycle., Serve the A2A AgentCard for agent discovery.

### Community 17 - "Community 17"
Cohesion: 0.4
Nodes (2): Act3Page(), useAct3Compare()

### Community 18 - "Community 18"
Cohesion: 0.4
Nodes (0): 

### Community 19 - "Community 19"
Cohesion: 0.5
Nodes (1): DealDetailPage()

### Community 20 - "Community 20"
Cohesion: 0.5
Nodes (0): 

### Community 21 - "Community 21"
Cohesion: 0.5
Nodes (4): ERC-8004 Identity Registry, ERC-8004 Reputation Registry, mcp Python SDK, negotiate-find (ERC-8004 + x402)

### Community 22 - "Community 22"
Cohesion: 0.67
Nodes (0): 

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (2): EdgeCasePanel(), pretty()

### Community 24 - "Community 24"
Cohesion: 0.67
Nodes (0): 

### Community 25 - "Community 25"
Cohesion: 0.67
Nodes (0): 

### Community 26 - "Community 26"
Cohesion: 0.67
Nodes (3): Kite dual MCP servers (AIR vs Passport OAuth), MCP security taxonomy + CABP/SERF + OAuth agent delegation, x402 MCP authorization (402 parse, approve_payment, retry)

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (0): 

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (0): 

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (0): 

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (0): 

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (0): 

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (0): 

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (0): 

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): AgentCard definition for NegotiatorGrid — served at /.well-known/agent-card.json

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (2): gokite Python KiteClient (neo.prod.gokite.ai), Kite REST agent discovery (/v1/agents/search)

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (2): FastAPI WebSocket broadcaster, Next.js NegotiatorGrid dashboard

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (0): 

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (0): 

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (0): 

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (0): 

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (0): 

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (0): 

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (0): 

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (0): 

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (0): 

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (0): 

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (0): 

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (0): 

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (0): 

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (0): 

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (0): 

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (0): 

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (0): 

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (0): 

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (0): 

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (0): 

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (0): 

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (0): 

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): Application startup / shutdown lifecycle.

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): Serve the A2A AgentCard for agent discovery.

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (1): Parameters controlling a negotiation session.

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (1): Profile for an agent participating in negotiations.

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (1): Estimated model of an opponent's behavior.

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (1): Result of Nash equilibrium guardrail check.

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (1): Raised when the buyer cannot complete a paid fetch.

### Community 68 - "Community 68"
Cohesion: 1.0
Nodes (1): Outcome of a ``fetch_with_payment`` call.

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (1): Minimal x402 buyer client that follows the 402 handshake.      Example::

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (1): Fetch a URL, paying an x402 toll if the server demands one.          If ``max_

### Community 71 - "Community 71"
Cohesion: 1.0
Nodes (1): Trivial async context that yields a caller-owned client.

### Community 72 - "Community 72"
Cohesion: 1.0
Nodes (1): Wraps OpenAI GPT-4o-mini to generate negotiation dialogue.      Parameters

### Community 73 - "Community 73"
Cohesion: 1.0
Nodes (1): Generate a natural-language buyer offer message.

### Community 74 - "Community 74"
Cohesion: 1.0
Nodes (1): Generate a natural-language seller counter-offer message.

### Community 75 - "Community 75"
Cohesion: 1.0
Nodes (1): Generate an acceptance message for a completed deal.

### Community 76 - "Community 76"
Cohesion: 1.0
Nodes (1): Generate a rejection / walk-away message.

### Community 77 - "Community 77"
Cohesion: 1.0
Nodes (1): In-memory map: ``route → atomic price (str, micro-USDT)``.      Shared (by ref

### Community 78 - "Community 78"
Cohesion: 1.0
Nodes (1): TTL-bounded set of used nonces. Not durable — per-process only.      The TTL i

### Community 79 - "Community 79"
Cohesion: 1.0
Nodes (1): Return True if the nonce is fresh and record it; False if replayed.

### Community 80 - "Community 80"
Cohesion: 1.0
Nodes (1): Configuration injected by the app factory.

### Community 81 - "Community 81"
Cohesion: 1.0
Nodes (1): Raised when a payment payload is rejected. The ``code`` is     surfaced in the

### Community 82 - "Community 82"
Cohesion: 1.0
Nodes (1): Result of verifying a decoded X-Payment payload.

### Community 83 - "Community 83"
Cohesion: 1.0
Nodes (1): Base64-decode the X-Payment header value → JSON payload dict.

### Community 84 - "Community 84"
Cohesion: 1.0
Nodes (1): Verify EIP-712 signature and business invariants. Returns payer address.

### Community 85 - "Community 85"
Cohesion: 1.0
Nodes (1): Try the real facilitator. Returns ``None`` on failure so callers can fall back.

### Community 86 - "Community 86"
Cohesion: 1.0
Nodes (1): FastAPI middleware that gates protected routes behind x402 payment.      Usage

### Community 87 - "Community 87"
Cohesion: 1.0
Nodes (1): Build x402 PaymentRequirements advertised in the 402 body.

## Knowledge Gaps
- **174 isolated node(s):** `NegotiatorGrid configuration — loads from environment variables.`, `Kite blockchain network configuration.`, `Deployed contract addresses.`, `x402 payment protocol configuration.`, `LLM provider configuration.` (+169 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 27`** (2 nodes): `layout.tsx`, `RootLayout()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (2 nodes): `page.tsx`, `updateAgentControl()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (2 nodes): `AgentCard()`, `agent-card.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (2 nodes): `logo.tsx`, `NegotiatorGridLogo()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (2 nodes): `negotiation-timeline.tsx`, `ReasoningMini()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (2 nodes): `stat-card.tsx`, `StatCard()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (2 nodes): `cn.ts`, `cn()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (2 nodes): `use-deals.ts`, `useDeals()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (2 nodes): `use-negotiation-stream.ts`, `useNegotiationStream()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (2 nodes): `AgentCard definition for NegotiatorGrid — served at /.well-known/agent-card.json`, `agent_card.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (2 nodes): `gokite Python KiteClient (neo.prod.gokite.ai)`, `Kite REST agent discovery (/v1/agents/search)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (2 nodes): `FastAPI WebSocket broadcaster`, `Next.js NegotiatorGrid dashboard`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `hardhat.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `NegotiatorGrid.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `Deploy.s.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `eslint.config.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `next-env.d.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `next.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `postcss.config.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `agent-isolation-panel.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `deal-detail-client.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `decision-trace-panel.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `price-convergence.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `sidebar.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `mock-data.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `types.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `deploy_kite.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `Application startup / shutdown lifecycle.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `Serve the A2A AgentCard for agent discovery.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `Parameters controlling a negotiation session.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `Profile for an agent participating in negotiations.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `Estimated model of an opponent's behavior.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `Result of Nash equilibrium guardrail check.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `Raised when the buyer cannot complete a paid fetch.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `Outcome of a ``fetch_with_payment`` call.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `Minimal x402 buyer client that follows the 402 handshake.      Example::`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `Fetch a URL, paying an x402 toll if the server demands one.          If ``max_`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `Trivial async context that yields a caller-owned client.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 72`** (1 nodes): `Wraps OpenAI GPT-4o-mini to generate negotiation dialogue.      Parameters`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 73`** (1 nodes): `Generate a natural-language buyer offer message.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 74`** (1 nodes): `Generate a natural-language seller counter-offer message.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 75`** (1 nodes): `Generate an acceptance message for a completed deal.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 76`** (1 nodes): `Generate a rejection / walk-away message.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 77`** (1 nodes): `In-memory map: ``route → atomic price (str, micro-USDT)``.      Shared (by ref`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 78`** (1 nodes): `TTL-bounded set of used nonces. Not durable — per-process only.      The TTL i`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 79`** (1 nodes): `Return True if the nonce is fresh and record it; False if replayed.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 80`** (1 nodes): `Configuration injected by the app factory.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 81`** (1 nodes): `Raised when a payment payload is rejected. The ``code`` is     surfaced in the`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 82`** (1 nodes): `Result of verifying a decoded X-Payment payload.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 83`** (1 nodes): `Base64-decode the X-Payment header value → JSON payload dict.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 84`** (1 nodes): `Verify EIP-712 signature and business invariants. Returns payer address.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 85`** (1 nodes): `Try the real facilitator. Returns ``None`` on failure so callers can fall back.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 86`** (1 nodes): `FastAPI middleware that gates protected routes behind x402 payment.      Usage`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 87`** (1 nodes): `Build x402 PaymentRequirements advertised in the 402 body.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `OpponentModeler` connect `Community 0` to `Community 1`, `Community 4`, `Community 6`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `NashGuardrail` connect `Community 0` to `Community 9`, `Community 4`, `Community 1`, `Community 6`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `LocalRegistry` connect `Community 2` to `Community 3`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 116 inferred relationships involving `OpponentModeler` (e.g. with `AgentInfo` and `Generate natural-language offer text (template mode — no LLM needed).`) actually correct?**
  _`OpponentModeler` has 116 INFERRED edges - model-reasoned connections that need verification._
- **Are the 123 inferred relationships involving `NegotiationOffer` (e.g. with `AgentInfo` and `Generate natural-language offer text (template mode — no LLM needed).`) actually correct?**
  _`NegotiationOffer` has 123 INFERRED edges - model-reasoned connections that need verification._
- **Are the 116 inferred relationships involving `NegotiationConfig` (e.g. with `AgentInfo` and `Generate natural-language offer text (template mode — no LLM needed).`) actually correct?**
  _`NegotiationConfig` has 116 INFERRED edges - model-reasoned connections that need verification._
- **Are the 112 inferred relationships involving `NegotiationSession` (e.g. with `AgentInfo` and `Generate natural-language offer text (template mode — no LLM needed).`) actually correct?**
  _`NegotiationSession` has 112 INFERRED edges - model-reasoned connections that need verification._