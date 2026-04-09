# Academic Papers for NegotiatorGrid
*Research compiled for NegotiatorGrid — an agent-to-agent price negotiation protocol adding a bargaining layer before x402 payments on the Kite AI blockchain.*

---

## Category 1: LLM-Powered Negotiation & Bargaining

---

### Paper 1.1
**Title:** AgenticPay: A Multi-Agent LLM Negotiation System for Buyer-Seller Transactions  
**ArXiv ID:** arXiv:2602.06008  
**Authors:** Xianyang Liu, Shangding Gu, Dawn Song  
**Date:** February 5, 2026  
**URL:** https://arxiv.org/abs/2602.06008

**Core Contribution:** Introduces AgenticPay, a benchmark and simulation framework for multi-agent buyer-seller negotiation driven by natural language, where agents possess private constraints and product-dependent valuations. Supports 110+ tasks spanning bilateral bargaining to many-to-many markets, with metrics for feasibility, efficiency, and welfare. Benchmarks reveal substantial gaps in long-horizon strategic reasoning across state-of-the-art LLMs.

**Relevance to NegotiatorGrid:** HIGH  
*Directly validates the NegotiatorGrid protocol concept: LLM-driven buyer and seller agents conducting structured multi-round price negotiation before financial settlement. The "agentic commerce" framing and private valuation modeling mirror NegotiatorGrid's pre-x402 bargaining layer.*

**Key Implementation Takeaways:**
- Use structured action extraction (bid/accept/reject parse layer) rather than free-form dialogue to ensure deterministic protocol progression
- Implement private reservation-value constraints that agents never disclose directly — inferred by opponent model
- Welfare metrics (social surplus, individual utility) should be logged on-chain for audit; AgenticPay's metrics map to NegotiatorGrid's settlement accountability

**Quotable for Demo/Judges:**
> "AgenticPay models markets in which buyers and sellers possess private constraints and product-dependent valuations, and must reach agreements through multi-round linguistic negotiation rather than numeric bidding alone."

---

### Paper 1.2
**Title:** ASTRA: A Negotiation Agent with Adaptive and Strategic Reasoning through Action in Dynamic Offer Optimization  
**ArXiv ID:** arXiv:2503.07129  
**Authors:** Deuksin Kwon, Jiwon Hae, Emma Clift, Daniel Shamsoddini, Jonathan Gratch, Gale M. Lucas  
**Date:** March 10, 2025  
**URL:** https://arxiv.org/abs/2503.07129

**Core Contribution:** Introduces ASTRA, a principle-driven LLM negotiation framework for turn-level offer optimization grounded in opponent modeling and Tit-for-Tat reciprocity. Operates in three stages: (1) interpret counterpart behavior, (2) optimize counteroffers via linear programming solver, (3) select offers based on acceptance probability. Validated through large-scale simulations and human evaluation.

**Relevance to NegotiatorGrid:** HIGH  
*ASTRA's three-stage architecture (observe → optimize → act) directly informs NegotiatorGrid's per-round offer generation loop. The LP-solver integration for Pareto-optimal offers and TFT reciprocity maps to NegotiatorGrid's concession strategy module.*

**Key Implementation Takeaways:**
- Integrate an LP solver as a tool call within the LLM's negotiation loop to generate mathematically Pareto-optimal counteroffers — avoids irrational extremes
- Tit-for-Tat reciprocity (mirror opponent concession rate) is the simplest convergence-guaranteeing concession policy; implement as default strategy
- The "acceptance probability" estimation stage can be approximated with a learned logistic model trained on offer trajectories

**Quotable for Demo/Judges:**
> "ASTRA operates in three stages: interpreting counterpart behavior, optimizing counteroffers via a linear programming solver, and selecting offers based on negotiation tactics and the partner's acceptance probability."

---

### Paper 1.3
**Title:** LLM Agents for Bargaining with Utility-based Feedback  
**ArXiv ID:** arXiv:2505.22998  
**Authors:** Ji-Yun Oh, Murad Aghazada, SeYoung Yun, Taehyeon Kim  
**Date:** May 29, 2025  
**URL:** https://arxiv.org/abs/2505.22998

**Core Contribution:** Introduces BargainArena, a benchmark with six intricate negotiation scenarios (deceptive practices, monopolies) and human-aligned utility-theoretic evaluation metrics including agent utility and negotiation power. Proposes a structured feedback mechanism enabling LLMs to iteratively refine bargaining strategies, promoting opponent-aware reasoning (OAR).

**Relevance to NegotiatorGrid:** HIGH  
*The utility-theoretic metrics (agent utility, negotiation power) and opponent-aware reasoning (OAR) concept are directly applicable to NegotiatorGrid's scoring and strategy modules. The structured feedback loop informs how agents should update strategies within a negotiation session.*

**Key Implementation Takeaways:**
- Define agent utility as a function of agreed price relative to reservation price — enables normalized welfare comparison across sessions
- "Negotiation power" metric (ratio of surplus claimed) should be emitted as part of the on-chain settlement record for transparency
- Structured feedback (post-round critique) can be implemented as an intra-session self-reflection prompt before each new offer

**Quotable for Demo/Judges:**
> "Our structured feedback mechanism significantly improves [LLM] performance, yielding deeper strategic and opponent-aware reasoning."

---

### Paper 1.4
**Title:** LLM Rationalis? Measuring Bargaining Capabilities of AI Negotiators  
**ArXiv ID:** arXiv:2512.13063  
**Authors:** Cheril Shah, Akshita Agarwal, Kanak Garg, Mourad Heddaya  
**Date:** December 15, 2025  
**URL:** https://arxiv.org/abs/2512.13063

**Core Contribution:** Introduces a unified mathematical framework for concession dynamics using a hyperbolic tangent curve, proposing two metrics: burstiness (τ) and the Concession-Rigidity Index (CRI). Empirically compares human vs. LLM negotiators across multiple scenarios and power-asymmetry conditions. Finds LLMs systematically anchor at extremes and fail to adapt to leverage or context.

**Relevance to NegotiatorGrid:** HIGH  
*Directly identifies failure modes that NegotiatorGrid must mitigate: anchoring bias and context-blindness. CRI and burstiness are ready-to-use metrics for NegotiatorGrid's negotiation quality monitor. The concession curve mathematics inform the offer-generation function.*

**Key Implementation Takeaways:**
- Implement anti-anchoring logic: first offer should be derived from market-rate oracle + noise, not from LLM's unconstrained generation
- Use CRI (Concession-Rigidity Index) as a session health metric — high CRI → trigger fallback to pre-agreed price schedule
- Hyperbolic tangent concession curve provides a smooth, bounded offer trajectory suitable for time-deadline negotiations

**Quotable for Demo/Judges:**
> "Unlike humans who smoothly adapt to situations and infer the opponents' position and strategies, LLMs systematically anchor at extremes of the possible agreement zone."

---

### Paper 1.5
**Title:** How Well Can LLMs Negotiate? NegotiationArena Platform and Analysis  
**ArXiv ID:** arXiv:2402.05863  
**Authors:** Federico Bianchi, Patrick John Chia, Mert Yuksekgonul, Jacopo Tagliabue, Dan Jurafsky, James Zou  
**Date:** February 8, 2024  
**URL:** https://arxiv.org/abs/2402.05863

**Core Contribution:** Develops NegotiationArena, a flexible multi-turn framework for evaluating LLM negotiation across ultimatum games, trading games, and price negotiations. Finds that behavioral tactics (e.g., simulating desperation) can boost LLM payoffs by 20%. Quantifies irrational behaviors exhibited by LLM negotiators.

**Relevance to NegotiatorGrid:** HIGH  
*The behavioral manipulation findings are a critical security concern for NegotiatorGrid — agents must be resistant to "desperation framing" or similar prompt injection attacks from counterparties. NegotiationArena's evaluation protocol is directly usable for NegotiatorGrid benchmarking.*

**Key Implementation Takeaways:**
- Add a manipulation-detection module: flag rounds where counterparty uses extreme emotional framing or urgency cues
- Implement "rationality guardrails" — agent must not accept offers below reservation price regardless of counterparty framing
- Use NegotiationArena's ultimatum game as a unit test for NegotiatorGrid's accept/reject threshold logic

**Quotable for Demo/Judges:**
> "LLM agents can significantly boost their negotiation outcomes by employing certain behavioral tactics. For example, by pretending to be desolate and desperate, LLMs can improve their payoffs by 20%."

---

### Paper 1.6
**Title:** NegoLog: An Integrated Python-based Automated Negotiation Framework with Enhanced Assessment Components  
**DOI:** 10.24963/ijcai.2024/998  
**Authors:** Anıl Doğru, Mehmet Onur Keskin, Catholijn M. Jonker, Tim Baarslag, Reyhan Aydoğan  
**Date:** August 2024 (IJCAI-24)  
**URL:** https://www.ijcai.org/proceedings/2024/998

**Core Contribution:** Introduces NegoLog, a Python-based automated negotiation framework providing advanced analytics, comprehensive logging, visualization tools, and auto-generated negotiation domains. Key novelty is independent evaluation of opponent modeling algorithms decoupled from bidding strategies. Supports tournament generation with configurable competitiveness and domain balance scores.

**Relevance to NegotiatorGrid:** HIGH  
*NegoLog is a directly usable development framework for prototyping and benchmarking NegotiatorGrid agents. The modular BOA (Bidding/Opponent model/Acceptance) architecture maps cleanly to NegotiatorGrid's component structure. Opponent model evaluation independent of strategy is critical for NegotiatorGrid's modular design.*

**Key Implementation Takeaways:**
- Adopt NegoLog's BOA architecture: separate Bidding strategy, Opponent Model, and Acceptance criterion into distinct modules with clean interfaces
- Use NegoLog's Nash distance and Kalai distance metrics as convergence indicators — target sessions that achieve <0.1 Nash distance
- NegoLog's YAML tournament config system can be adapted for NegotiatorGrid's session parameter management

**Quotable for Demo/Judges:**
> "NegoLog enables modular, independent evaluation of opponent modeling approaches; it provides analytics including Pareto optimality, distance to Nash, average utilities, and sensitivity to opponent's moves."

---

### Paper 1.7
**Title:** Advancing AI Negotiations: New Theory and Evidence from a Large-Scale Autonomous Negotiations Competition  
**ArXiv ID:** arXiv:2503.06416  
**Authors:** Michelle Vaccaro, Michael Caoson, Harang Ju, Sinan Aral, Jared R. Curhan  
**Date:** March 9, 2025  
**URL:** https://arxiv.org/abs/2503.06416

**Core Contribution:** Analyzes 182,812 negotiations between AI agents in a large-scale competition involving 286 participants. Finds that classical negotiation theory principles (warmth, dominance) translate to AI-AI negotiation, and identifies AI-specific strategies (chain-of-thought reasoning, prompt injection) as significant performance drivers. Calls for a new theory of AI negotiation integrating classical and AI-specific factors.

**Relevance to NegotiatorGrid:** MEDIUM  
*Empirical evidence at scale provides statistical grounding for NegotiatorGrid's design choices. The prompt-injection-as-strategy finding reinforces the need for NegotiatorGrid's manipulation-detection layer.*

**Key Implementation Takeaways:**
- Chain-of-thought reasoning in negotiation prompts significantly improves outcomes — enable CoT for all NegotiatorGrid agent turns
- Prompt injection between agents is a real attack vector — implement output filtering/sanitization on all inter-agent message payloads
- Warmth signals (gratitude, positivity) correlate with deal rates — agents can be designed with configurable "social style" parameters

**Quotable for Demo/Judges:**
> "AI-specific strategies that established negotiation theory cannot explain, including chain-of-thought reasoning and prompt injection, were important determinants of agents' negotiation performance."

---

### Paper 1.8
**Title:** Game-theoretic LLM: Agent Workflow for Negotiation Games  
**ArXiv ID:** arXiv:2411.05990  
**Authors:** Wenyue Hua, Ollie Liu, Lingyao Li, Alfonso Amayuelas, et al.  
**Date:** November 12, 2024  
**URL:** https://arxiv.org/abs/2411.05990

**Core Contribution:** Investigates LLM rationality in strategic decision-making through game-theoretic frameworks, finding that LLMs deviate from rational strategies as game complexity increases. Designs game-theoretic workflows that guide LLM reasoning and decision-making, demonstrating measurable improvement in strategic outcomes.

**Relevance to NegotiatorGrid:** HIGH  
*Directly provides workflow templates for structuring LLM negotiation to remain game-theoretically rational — critical for NegotiatorGrid's correctness guarantees. The finding that rationality degrades with complexity motivates simplifying the negotiation state representation.*

**Key Implementation Takeaways:**
- Structure negotiation as a sequential game tree within the prompt, not as open-ended conversation — reduces irrational deviations
- Precompute dominant strategies for common price-range scenarios and inject as "decision hints" in the agent prompt
- Implement game-theoretic workflow as a state machine: each round transition is validated against rationality constraints before offer submission

**Quotable for Demo/Judges:**
> "LLMs frequently deviate from rational strategies, particularly as the complexity of the game increases. Game-theoretic workflows that guide the reasoning and decision-making processes of LLMs [significantly improve performance]."

---

## Category 2: Agent-to-Agent Payments & Economic Actors

---

### Paper 2.1 ⭐ CRITICAL
**Title:** SoK: Blockchain Agent-to-Agent Payments  
**ArXiv ID:** arXiv:2604.03733  
**Authors:** Yuanzhe Zhang, Yuexin Xiang, Yuchen Lei, Qin Wang, Tian Qiu, Yujing Sun, Spiridon Zarkov, Tsz Hon Yuen, Andreas Deppeler, Jiangshan Yu, Kwok-Yan Lam  
**Date:** April 4, 2026  
**URL:** https://arxiv.org/abs/2604.03733

**Core Contribution:** First systematic treatment of blockchain-based A2A payments, specifically including x402, using a four-stage lifecycle: discovery, authorization, execution, and accounting. Identifies key challenges including weak intent binding, misuse under valid authorization, payment-service decoupling, and limited accountability. Proposes future directions for behavior-aware control and compositional payment workflows.

**Relevance to NegotiatorGrid:** HIGH  
*This is the canonical reference paper for the entire NegotiatorGrid payment stack. The four-stage lifecycle (discovery → authorization → execution → accounting) directly maps to NegotiatorGrid's pre-payment negotiation layer. The identified challenge of "payment-service decoupling" is precisely the problem NegotiatorGrid's bargaining protocol addresses.*

**Key Implementation Takeaways:**
- NegotiatorGrid operates at the "discovery/intent-binding" stage of the SoK lifecycle — the agreed price from negotiation becomes the intent that binds the subsequent x402 payment
- Address "weak intent binding" by cryptographically anchoring the negotiated price and terms on-chain before payment execution
- The paper's "behavior-aware control" future direction is exactly what NegotiatorGrid's pre-payment bargaining layer implements
- Use the four-stage lifecycle as the architectural skeleton for NegotiatorGrid's documentation

**Quotable for Demo/Judges:**
> "For the first time, we systematize blockchain-based A2A payments, e.g., X402, with a four-stage lifecycle: discovery, authorization, execution, and accounting... [identifying] weak intent binding, misuse under valid authorization, payment-service decoupling, and limited accountability."

---

### Paper 2.2
**Title:** A402: Binding Cryptocurrency Payments to Service Execution for Agentic Commerce  
**ArXiv ID:** arXiv:2603.01179  
**Authors:** Yue Li, Lei Wang, Kaixuan Wang, Zhiqiang Yang, Ke Wang, Zhi Guan, Jianbo Gao  
**Date:** March 1, 2026 (revised March 19, 2026)  
**URL:** https://arxiv.org/abs/2603.01179

**Core Contribution:** Presents A402, a trust-minimized payment architecture that binds cryptocurrency payments to service execution via Atomic Service Channels (ASCs). Uses TEE-assisted adaptor signatures to ensure payments finalize only if service is correctly delivered. A TEE-based Liquidity Vault aggregates settlements into single on-chain transactions with orders-of-magnitude performance improvement over x402.

**Relevance to NegotiatorGrid:** HIGH  
*A402 solves the atomicity gap that x402 leaves open — the same gap NegotiatorGrid's negotiation layer addresses at a higher level. NegotiatorGrid's agreed price becomes the parameter for an ASC, ensuring the negotiated deal is honored at settlement. The TEE-attestation mechanism is directly applicable to Kite AI's trust model.*

**Key Implementation Takeaways:**
- After price negotiation completes, instantiate an ASC with the negotiated price as the channel's transfer amount — this atomically binds the deal to execution
- TEE-assisted adaptor signatures enable conditional payment release — NegotiatorGrid can condition payment on service delivery proof submitted by the payee agent
- The Liquidity Vault pattern reduces on-chain footprint: batch-settle multiple negotiated micro-agreements in one transaction

**Quotable for Demo/Judges:**
> "A402 ensures that payments are finalized if and only if the requested service is correctly executed and the corresponding result is delivered... delivering orders-of-magnitude performance and on-chain cost improvements over x402."

---

### Paper 2.3
**Title:** The Agent Economy: A Blockchain-Based Foundation for Autonomous AI Agents  
**ArXiv ID:** arXiv:2602.14219  
**Authors:** Minghui Xu  
**Date:** February 15, 2026  
**URL:** https://arxiv.org/abs/2602.14219

**Core Contribution:** Proposes the "Agent Economy," a five-layer blockchain architecture enabling autonomous AI agents to operate as economic peers: (1) Physical Infrastructure via DePIN, (2) Identity & Agency via W3C DIDs, (3) Cognitive & Tooling via RAG and MCP, (4) Economic & Settlement via account abstraction, (5) Collective Governance via Agentic DAOs. Identifies six core research challenges and ethical implications.

**Relevance to NegotiatorGrid:** HIGH  
*The five-layer architecture provides the theoretical framing within which NegotiatorGrid operates: the cognitive-tooling layer (MCP) enables negotiation, the economic-settlement layer (account abstraction) handles payment, and the identity layer (DIDs) provides agent authentication. NegotiatorGrid implements layers 2–4 for the specific use case of price bargaining.*

**Key Implementation Takeaways:**
- Use W3C DID standards for agent identity in NegotiatorGrid — each negotiating agent should have a DID-anchored identity registered on Kite AI
- Account abstraction (ERC-4337 or equivalent) provides the spending-policy enforcement that makes negotiation outcomes binding — agents cannot pay more than negotiated
- MCP is explicitly identified as the cognitive-tooling layer; NegotiatorGrid's MCP tool calls sit correctly within this architecture

**Quotable for Demo/Judges:**
> "Blockchain technology provides three critical properties enabling genuine agent autonomy: permissionless participation, trustless settlement, and machine-to-machine micropayments."

---

### Paper 2.4
**Title:** Towards Multi-Agent Economies: Enhancing the A2A Protocol with Ledger-Anchored Identities and x402 Micropayments for AI Agents  
**ArXiv ID:** arXiv:2507.19550  
**Authors:** Awid Vaziry, Sandro Rodriguez Garzon, Axel Küpper  
**Date:** July 24, 2025  
**URL:** https://arxiv.org/abs/2507.19550

**Core Contribution:** Presents a novel architecture combining A2A protocol with DLT-based agent discovery and x402 micropayments. Enables on-chain AgentCard publishing as smart contracts and HTTP-based payment flow via EIP-3009 signed transactions embedded in HTTP headers. Provides a working prototype demonstrating blockchain-agnostic, frictionless agent-to-agent commerce.

**Relevance to NegotiatorGrid:** HIGH  
*This is the closest existing implementation to NegotiatorGrid's architecture. The A2A + x402 integration demonstrates the exact payment flow NegotiatorGrid extends with a bargaining layer before the x402 step. The on-chain AgentCard discovery mechanism is directly applicable to Kite AI.*

**Key Implementation Takeaways:**
- NegotiatorGrid inserts a negotiation handshake between the A2A task assignment and the x402 payment header submission — the negotiated price replaces the static x402 amount
- EIP-3009 signed payment transactions as HTTP headers is the right implementation pattern for x402 on EVM chains
- On-chain AgentCards enable capability discovery before negotiation — agents can verify counterparty capabilities before entering bargaining

**Quotable for Demo/Judges:**
> "By seamlessly integrating the x402 micropayment flow into the A2A protocol through standard HTTP headers, frictionless, blockchain-agnostic payments are facilitated between agents."

---

### Paper 2.5
**Title:** Secure Autonomous Agent Payments: Verifying Authenticity and Intent in a Trustless Environment  
**ArXiv ID:** arXiv:2511.15712  
**Authors:** Vivek Acharya  
**Date:** November 8, 2025  
**URL:** https://arxiv.org/abs/2511.15712

**Core Contribution:** Proposes a blockchain-based framework combining DID standards, on-chain intent proofs, ZKPs for privacy, and TEE attestations to cryptographically verify AI agent identity and payment intent. The hybrid on-chain/off-chain architecture provides an immutable audit trail linking user authorization to payment outcome.

**Relevance to NegotiatorGrid:** HIGH  
*The "intent binding" problem — ensuring the negotiated price is the one that gets paid — is precisely what this paper's on-chain intent proof mechanism addresses. ZKP-based privacy preservation allows NegotiatorGrid agents to prove they're negotiating within policy bounds without revealing their reservation price.*

**Key Implementation Takeaways:**
- On-chain intent proofs: after negotiation completes, publish a commitment (hash of agreed terms) on Kite AI before triggering x402 payment — this is the intent proof
- ZKPs can prove "agreed price ≤ authorized budget" without revealing the budget — preserve agent policy privacy
- TEE attestations for NegotiatorGrid agents would allow counterparties to verify agent code integrity (no manipulation of negotiation logic)

**Quotable for Demo/Judges:**
> "On-chain intent proofs record user authorization, and zero-knowledge proofs preserve privacy while ensuring policy compliance... providing an immutable audit trail linking user intent to payment outcome."

---

### Paper 2.6
**Title:** Governing the Agent-to-Agent Economy of Trust via Progressive Decentralization  
**ArXiv ID:** arXiv:2501.16606  
**Authors:** Tomer Jordi Chaffer  
**Date:** January 28, 2025 (revised April 25, 2025)  
**URL:** https://arxiv.org/abs/2501.16606

**Core Contribution:** Proposes AgentBound Tokens (ABTs) — non-transferable, non-fungible tokens uniquely tied to individual AI agents (analogous to Soulbound tokens) — staked as collateral for autonomous actions. Advocates cryptoeconomic incentive design for decentralized agent governance with progressive human oversight.

**Relevance to NegotiatorGrid:** MEDIUM  
*ABTs provide an elegant reputation-staking mechanism for NegotiatorGrid: agents that consistently negotiate in good faith build stake-backed reputation; agents that renege on negotiated agreements lose stake. This creates economic alignment for honest bargaining behavior.*

**Key Implementation Takeaways:**
- Implement an ABT-style reputation stake in NegotiatorGrid: agents post collateral before entering negotiation; slashed if they refuse agreed settlement
- Progressive decentralization: start with human-in-the-loop for high-value negotiations, automate as trust accumulates
- Non-transferable agent-specific tokens prevent reputation laundering across agent identities

**Quotable for Demo/Judges:**
> "By staking ABTs as collateral for autonomous actions within an agent-to-agent network via a proof-of-stake mechanism, agents may be incentivized towards ethical behavior, and penalties for misconduct are automatically enforced."

---

## Category 3: Trust, Reputation & Mechanism Design for Autonomous Agents

---

### Paper 3.1
**Title:** Inter-Agent Trust Models: A Comparative Study of Brief, Claim, Proof, Stake, Reputation and Constraint in Agentic Web Protocol Design — A2A, AP2, ERC-8004, and Beyond  
**ArXiv ID:** arXiv:2511.03434  
**Authors:** Botao 'Amber' Hu, Helena Rong  
**Date:** November 5, 2025  
**URL:** https://arxiv.org/abs/2511.03434

**Core Contribution:** Comprehensive comparative study of six trust model categories (Brief, Claim, Proof, Stake, Reputation, Constraint) across emerging agent protocols (Google A2A, AP2, ERC-8004). Emphasizes LLM-specific fragilities (prompt injection, sycophancy, hallucination) that make purely reputational approaches brittle. Recommends trustless-by-default architectures anchored in Proof and Stake.

**Relevance to NegotiatorGrid:** HIGH  
*This paper provides the trust model framework for NegotiatorGrid's inter-agent trust architecture. The "Proof and Stake" recommendation maps directly to NegotiatorGrid's design: ZKP-verified agent credentials (Proof) plus collateral posted before negotiation (Stake). The LLM-fragility analysis explains why NegotiatorGrid cannot rely on self-reported capabilities alone.*

**Key Implementation Takeaways:**
- For NegotiatorGrid, combine Proof (zkVM attestation of agent code) + Stake (collateral for agreement enforcement) + Brief (DID-anchored capability card) as the baseline trust stack
- Claim-only trust (AgentCard self-assertion) is insufficient — require on-chain Proof verification for any high-value negotiation
- ERC-8004 "Trustless Agents" standard should be monitored for Kite AI compatibility

**Quotable for Demo/Judges:**
> "We argue for trustless-by-default architectures anchored in Proof and Stake to gate high-impact actions... No single [trust] mechanism suffices."

---

### Paper 3.2
**Title:** BlockA2A: Towards Secure and Verifiable Agent-to-Agent Interoperability  
**ArXiv ID:** arXiv:2508.01332  
**Authors:** Zhenhua Zou, Zhuotao Liu, Lepeng Zhao, Qiuyang Zhan  
**Date:** August 2, 2025  
**URL:** https://arxiv.org/abs/2508.01332

**Core Contribution:** First systematic analysis of multi-agent security risks (fragmented identity, insecure channels, Byzantine agents). Proposes BlockA2A: a unified framework using DIDs for cross-domain authentication, blockchain-anchored ledgers for auditability, and smart contracts for context-aware access control. Includes Defense Orchestration Engine (DOE) for real-time Byzantine agent flagging.

**Relevance to NegotiatorGrid:** HIGH  
*BlockA2A's threat model (prompt-based attacks, Byzantine agents, communication manipulation) directly applies to NegotiatorGrid's negotiation protocol. The DOE's real-time Byzantine flagging is applicable as NegotiatorGrid's manipulation-detection layer. Sub-second overhead makes it production-viable for payment-gated negotiations.*

**Key Implementation Takeaways:**
- Implement NegotiatorGrid using DID-based cross-domain authentication — agents from different orgs can negotiate with cryptographic identity guarantees
- Smart contract access control: the negotiation smart contract enforces that only credentialed agents can enter negotiation sessions
- DOE's "reactive execution halting" pattern maps to NegotiatorGrid's deadlock-detection and fallback-to-reserve-price mechanism

**Quotable for Demo/Judges:**
> "BlockA2A eliminates centralized trust bottlenecks, ensures message authenticity and execution integrity, and guarantees accountability across agent interactions... operating with sub-second overhead."

---

### Paper 3.3
**Title:** Toward Transparent and Incentive-Compatible Collaboration in Decentralized LLM Multi-Agent Systems: A Blockchain-Driven Approach  
**DOI:** 10.1109/TNSE.2026.3659486  
**Authors:** Minfeng Qi, Tianqing Zhu, Lefeng Zhang, Ningran Li, Yu-an Tan, Wanlei Zhou  
**Date:** 2026  
**URL:** https://ieeexplore.ieee.org/document/11368731/

**Core Contribution:** Proposes a behavior-shaping incentive mechanism for decentralized LLM multi-agent systems that models agent utility as a function of task rewards, capability mismatch, and workload. Couples short-term utility optimization with long-term trust via dynamic reputation updates. Implements a blockchain enforcement layer for verifiable identity binding and task commitment.

**Relevance to NegotiatorGrid:** HIGH  
*The incentive-compatibility requirement is central to NegotiatorGrid: agents must have economic incentives to negotiate honestly. This paper's reputation-plus-incentive mechanism provides the mathematical model for designing NegotiatorGrid's collateral and reputation scoring system.*

**Key Implementation Takeaways:**
- Model negotiating agent utility as: U = task_reward - capability_cost - misrepresentation_penalty
- Dynamic reputation updates after each negotiation session — weight recent behavior more heavily (exponential decay of historical scores)
- Blockchain logging of incentive-relevant state transitions enables auditable negotiation histories on Kite AI

**Quotable for Demo/Judges:**
> "The mechanism incentivizes cooperative behavior and discourages strategic misrepresentation... jointly shaping task assignment probabilities, reputation evolution, and skill profiles over repeated interactions."

---

### Paper 3.4
**Title:** Towards Trust and Reputation as a Service in a Blockchain-based Decentralized Marketplace  
**ArXiv ID:** arXiv:2403.04779  
**Authors:** Stephen Olariu, Ravi Mukkamala, Meshari Aljohani  
**Date:** March 2, 2024  
**URL:** https://arxiv.org/abs/2403.04779

**Core Contribution:** Proposes a novel trust and reputation service for decentralized marketplaces using smart contracts for automatic feedback generation, replacing unreliable buyer feedback with objective transaction outcome assessment. Positions trust/reputation as a composable on-chain service accessible to any marketplace participant.

**Relevance to NegotiatorGrid:** MEDIUM  
*The "Trust-as-a-Service" model directly applies to Kite AI: NegotiatorGrid can consume a shared reputation oracle rather than maintaining its own reputation store, reducing implementation complexity and increasing ecosystem composability.*

**Key Implementation Takeaways:**
- Design NegotiatorGrid's reputation component as a composable smart contract (callable by any agent protocol on Kite AI)
- Automatic smart-contract-based feedback generation: upon settlement, the contract scores negotiation quality (rounds to completion, price vs. market rate, deal-or-no-deal)
- Reputation should be queryable before negotiation begins — agents can refuse counterparties with sub-threshold reputation scores

**Quotable for Demo/Judges:**
> "A Smart Contract is associated with each transaction and is responsible for providing automatic feedback, replacing notoriously unreliable buyer feedback with a more objective assessment of how well the parties [performed]."

---

## Category 4: Account Abstraction & Agent Identity

---

### Paper 4.1
**Title:** Binding Agent ID (BAID): Unleashing the Power of AI Agents with Accountability and Credibility  
**ArXiv ID:** arXiv:2512.17538  
**Authors:** Zibin Lin, Shengli Zhang, Guofu Liao, Dacheng Tao, Taotao Wang  
**Date:** December 19, 2025  
**URL:** https://arxiv.org/abs/2512.17538

**Core Contribution:** Proposes BAID, a comprehensive identity infrastructure establishing verifiable user-code binding for AI agents via three mechanisms: biometric local binding, decentralized on-chain identity management, and a zkVM-based Code-Level Authentication protocol. Treats the program binary as the identity using recursive proofs, providing cryptographic guarantees for operator identity, agent configuration integrity, and execution provenance.

**Relevance to NegotiatorGrid:** HIGH  
*BAID addresses the exact problem NegotiatorGrid faces: how does a counterparty know they're negotiating with an agent running legitimate, unmodified NegotiatorGrid code? The zkVM-based code-level authentication enables proof that the negotiation logic hasn't been tampered with — critical for trust in autonomous price negotiation.*

**Key Implementation Takeaways:**
- Integrate BAID's zkVM proof generation into NegotiatorGrid agent initialization: agent presents code-level attestation at the start of each negotiation session
- The "recursive proof" approach allows BAID attestations to be verified on-chain without revealing proprietary negotiation strategy code
- BAID's on-chain identity management maps to Kite AI's agent registry — register NegotiatorGrid agent identities via BAID-compatible credentials

**Quotable for Demo/Judges:**
> "BAID provides cryptographic guarantees for operator identity, agent configuration integrity, and complete execution provenance, thereby effectively preventing unauthorized operation and code substitution."

---

### Paper 4.2
**Title:** Agent Contracts: A Formal Framework for Resource-Bounded Autonomous AI Systems  
**ArXiv ID:** arXiv:2601.08815  
**Authors:** Qing Ye, Jing Tan  
**Date:** January 13, 2026 (revised March 25, 2026)  
**URL:** https://arxiv.org/abs/2601.08815

**Core Contribution:** Introduces Agent Contracts, a formal framework unifying input/output specifications, multi-dimensional resource constraints, temporal boundaries, and success criteria into a coherent governance mechanism. Establishes conservation laws for delegated budget hierarchies. Empirically demonstrates 90% token reduction with 525x lower variance in iterative workflows, with zero conservation violations.

**Relevance to NegotiatorGrid:** HIGH  
*Agent Contracts formalize exactly what NegotiatorGrid needs to represent: a negotiated price agreement with resource constraints (max payment), temporal bounds (offer deadline), and success criteria (deal completion). The conservation laws for hierarchical delegation apply to multi-agent negotiation chains.*

**Key Implementation Takeaways:**
- Model each NegotiatorGrid negotiation session as an Agent Contract with: input (service request), resource constraint (max price budget), temporal bound (negotiation deadline), success criterion (price agreement within bounds)
- Conservation law: parent agent's delegated budget must be ≥ sum of child agents' budgets — enforce via smart contract before session initiation
- Contract modes (strict/relaxed) map to NegotiatorGrid's configurable negotiation postures

**Quotable for Demo/Judges:**
> "Agent Contracts provide formal foundations for predictable, auditable, and resource-bounded autonomous AI deployment... 90% token reduction with 525x lower variance in iterative workflows."

---

### Paper 4.3
**Title:** Account Abstraction for Enforcing Blockchain-Based AI Agent Non-Functional Requirements  
**DOI:** 10.1109/REW66121.2025.00053  
**Authors:** Jan Gorzny, Fatemeh Heidari Soureshjani, Martin Derka  
**Date:** September 2025  
**URL:** https://ieeexplore.ieee.org/document/11190297/

**Core Contribution:** Proposes using account abstraction (ERC-4337 / EIP-7702) primitives to enforce non-functional requirements (security, safety) for AI agents managing blockchain wallets. Smart wallets allow selective delegation of specific actions to AI agents while maintaining user-defined policy constraints encoded in smart contracts.

**Relevance to NegotiatorGrid:** HIGH  
*Account abstraction is the enforcement layer that makes NegotiatorGrid's negotiated price binding: the smart wallet's spending policy can be set to the agreed price, preventing the agent from overpaying. This paper provides the technical justification and implementation pattern for this critical property.*

**Key Implementation Takeaways:**
- After negotiation, update the agent's smart wallet spending policy to exactly the negotiated price — this is the on-chain enforcement of the bargain
- EIP-7702 enables delegating specific actions (pay exactly X to address Y) without surrendering full wallet control — ideal for NegotiatorGrid's constrained payment model
- Encode NegotiatorGrid's negotiation outcome as a smart contract policy: if negotiation = success → allow payment up to agreed_price, else → block payment

**Quotable for Demo/Judges:**
> "Smart wallets allow delegation of some actions, but not all, to AI agents... end users can leverage AI agents to their benefit while satisfying key non-functional requirements like security and safety."

---

### Paper 4.4
**Title:** Leveraging AI Agents for Task Automation in Blockchain Wallets with Account Abstraction  
**DOI:** 10.1109/BCCA66705.2025.11229558  
**Authors:** Ivan Dimitrov, Wolfgang Prinz  
**Date:** October 14, 2025  
**URL:** https://ieeexplore.ieee.org/document/11229558/

**Core Contribution:** Investigates AI agent integration with ERC-4337 smart wallets for automated transaction management, gas optimization, DeFi interactions, and real-time fraud detection. Proposes an architecture combining modular smart contracts (upgradability) with AI agent decision logic (adaptability) for intelligent wallet behavior.

**Relevance to NegotiatorGrid:** MEDIUM  
*Provides the practical implementation patterns for integrating NegotiatorGrid's negotiation outcome with ERC-4337 wallet management. Gas optimization and fraud detection modules are directly applicable to NegotiatorGrid's payment execution phase.*

**Key Implementation Takeaways:**
- NegotiatorGrid agent wallet: modular smart contract with a "negotiated spending limit" module that gets updated after each successful bargaining session
- Gas fee optimization module should run between negotiation completion and payment submission — minimizes transaction cost for negotiated micropayments
- Real-time fraud detection (anomalous payment amounts) acts as a sanity check that payment matches negotiated price

**Quotable for Demo/Judges:**
> "AI agents autonomously detect and prevent malicious activities such as unauthorized transactions, ensuring user funds are protected in real-time."

---

### Paper 4.5
**Title:** Eliza: A Web3-Friendly AI Agent Operating System  
**ArXiv ID:** arXiv:2501.06781  
**Authors:** Shaw Walters, Sam Gao, Shakker Nerd, Feng Da, Warren Williams, et al.  
**Date:** January 24, 2025  
**URL:** https://arxiv.org/abs/2501.06781

**Core Contribution:** Presents Eliza, an AI agent operating system designed for Web3 environments, bridging LLM-powered cognitive cores with on-chain asset management, wallet control, and DeFi interactions. Provides a plugin architecture enabling agents to autonomously manage crypto assets and execute blockchain transactions.

**Relevance to NegotiatorGrid:** MEDIUM  
*Eliza's Web3 agent OS provides the runtime environment in which NegotiatorGrid agents could operate. Its plugin architecture directly supports adding a NegotiatorGrid negotiation plugin that intercepts payments and runs the bargaining protocol before execution.*

**Key Implementation Takeaways:**
- NegotiatorGrid can be implemented as an Eliza plugin: intercept payment calls → run negotiation → submit negotiated payment
- Eliza's wallet management abstractions are compatible with ERC-4337 spending policies needed for NegotiatorGrid enforcement
- Plugin architecture allows NegotiatorGrid to be enabled/disabled per agent instance without modifying core agent logic

**Quotable for Demo/Judges:**
> "At the intersection between AI and Web3, Eliza provides an AI agent operating system capable of autonomously controlling and determining execution paths under user instructions."

---

## Category 5: MCP Security & Architecture

---

### Paper 5.1 ⭐ KEY PAPER
**Title:** Model Context Protocol (MCP): Landscape, Security Threats, and Future Research Directions  
**ArXiv ID:** arXiv:2503.23278  
**Authors:** Xinyi Hou, Yanjie Zhao, Shenao Wang, Haoyu Wang  
**Date:** April 6, 2025 (also published ACM DL: doi:10.1145/3796519)  
**URL:** https://arxiv.org/abs/2503.23278

**Core Contribution:** First systematic study of MCP from architectural and security perspectives. Defines a full MCP server lifecycle (creation, deployment, operation, maintenance) decomposed into 16 activities. Constructs a comprehensive threat taxonomy across four attacker types (malicious developers, external attackers, malicious users, security flaws) encompassing 16 threat scenarios. Proposes fine-grained safeguards per lifecycle phase.

**Relevance to NegotiatorGrid:** HIGH  
*NegotiatorGrid exposes MCP tools for negotiation initiation, offer submission, and session management. This paper's threat taxonomy directly identifies risks to NegotiatorGrid's MCP interface: tool poisoning (malicious negotiation tools), supply-chain attacks (compromised protocol servers), and privilege escalation through negotiation context.*

**Key Implementation Takeaways:**
- Apply lifecycle-phase-specific safeguards: at creation (code audit), at deployment (sandboxing), at operation (runtime monitoring), at maintenance (integrity verification)
- Tool poisoning defense: NegotiatorGrid's MCP tool descriptors must be immutably signed and versioned — any modification invalidates existing sessions
- Malicious user threat: counterparty agents can craft adversarial negotiation messages to manipulate NegotiatorGrid agents — apply semantic vetting to all incoming offer messages

**Quotable for Demo/Judges:**
> "MCP enables seamless interaction between AI models and external tools... yet [introduces] 16 distinct threat scenarios across four major attacker types. We propose fine-grained, actionable security safeguards tailored to each lifecycle phase."

---

### Paper 5.2 ⭐ KEY PAPER
**Title:** Bridging Protocol and Production: Design Patterns for Deploying AI Agents with Model Context Protocol  
**ArXiv ID:** arXiv:2603.13417  
**Authors:** Vasundra Srinivasan  
**Date:** March 12, 2026  
**URL:** https://arxiv.org/abs/2603.13417

**Core Contribution:** Identifies three missing MCP protocol-level primitives from enterprise deployment experience: identity propagation, adaptive tool budgeting, and structured error semantics. Proposes Context-Aware Broker Protocol (CABP) for identity-scoped routing, Adaptive Timeout Budget Allocation (ATBA) for latency management, and Structured Error Recovery Framework (SERF) for machine-readable failure semantics.

**Relevance to NegotiatorGrid:** HIGH  
*Identity propagation is critical for NegotiatorGrid: the negotiating agent's identity must propagate through the MCP tool calls to ensure correct attribution and reputation updates. ATBA is directly applicable to NegotiatorGrid's round-deadline management. SERF enables structured error handling when negotiation fails or times out.*

**Key Implementation Takeaways:**
- Implement CABP-style identity propagation: each NegotiatorGrid MCP tool call carries the agent's DID as part of the request context
- ATBA for negotiation round management: model each offer round as a budget allocation problem with per-round time limits summing to total session deadline
- SERF error codes: define NegotiatorGrid-specific error types (NEGOTIATION_DEADLOCK, PRICE_FLOOR_BREACH, SESSION_TIMEOUT) as machine-readable structured responses

**Quotable for Demo/Judges:**
> "Three protocol-level primitives remain missing: identity propagation, adaptive tool budgeting, and structured error semantics... reliable agent tool integration requires infrastructure-level mechanisms that the specification does not yet address."

---

### Paper 5.3
**Title:** Securing the Model Context Protocol (MCP): Risks, Controls, and Governance  
**ArXiv ID:** arXiv:2511.20920  
**Authors:** Herman Errico, Jiquan Ngiam, Shanita Sojan  
**Date:** November 25, 2025  
**URL:** https://arxiv.org/abs/2511.20920

**Core Contribution:** Focuses on three MCP adversary types: content-injection attackers, supply-chain attackers, and unintentional adversarial agents. Proposes practical controls: per-user scoped authorization, provenance tracking, containerized sandboxing, inline policy enforcement, and centralized governance via private registries or gateway layers.

**Relevance to NegotiatorGrid:** HIGH  
*NegotiatorGrid's MCP interface is a potential content-injection attack surface: counterparty agents could embed malicious instructions in offer messages. The gateway/registry model provides a governance layer for restricting which agents can initiate NegotiatorGrid sessions.*

**Key Implementation Takeaways:**
- Implement per-session scoped authorization for NegotiatorGrid MCP tools: buyer agent can only call buyer-side tools, seller agent can only call seller-side tools
- Provenance tracking: log all MCP tool calls within a negotiation session with cryptographic signatures for post-session auditing on Kite AI
- Private registry pattern: maintain an authorized agent registry on Kite AI; only registered agents can initiate NegotiatorGrid sessions

**Quotable for Demo/Judges:**
> "MCP's flexibility introduces three adversary types... we propose per-user authentication with scoped authorization, provenance tracking across agent workflows, and centralized governance using private registries."

---

### Paper 5.4
**Title:** Securing the Model Context Protocol: Defending LLMs Against Tool Poisoning and Adversarial Attacks  
**ArXiv ID:** arXiv:2512.06556  
**Authors:** Saeid Jamshidi, Kawser Wazed Nafi, Arghavan Moradi Dakhel, Negar Shahabi, F. Khomh, Naser Ezzati-Jivan  
**Date:** December 6, 2025  
**URL:** https://arxiv.org/abs/2512.06556

**Core Contribution:** Analyzes three classes of semantic attacks on MCP systems: Tool Poisoning (adversarial instructions hidden in tool descriptors), Shadowing (trusted tools compromised via contaminated shared context), and Rug Pulls (descriptor alterations after approval). Introduces a layered security framework: RSA-based manifest signing, LLM-on-LLM semantic vetting, and lightweight heuristic guardrails. GPT-4 blocks ~71% of unsafe tool calls.

**Relevance to NegotiatorGrid:** HIGH  
*Tool Poisoning and Rug Pulls are direct threats to NegotiatorGrid: a malicious counterparty could register poisoned negotiation tools or alter tool descriptors mid-session. RSA manifest signing and semantic vetting are implementable defenses.*

**Key Implementation Takeaways:**
- RSA-sign all NegotiatorGrid MCP tool descriptors at deployment time; reject any session where descriptor signature fails verification (Rug Pull prevention)
- Implement LLM-on-LLM semantic vetting for incoming offer messages: a lightweight "vetting LLM" screens for adversarial instructions before forwarding to the negotiation LLM
- Heuristic guardrails: flag any offer message with unusual formatting, encoding, or length anomalies as potential Tool Poisoning attempts

**Quotable for Demo/Judges:**
> "Tool Poisoning [involves] adversarial instructions hidden in tool descriptors; Rug Pulls [involve] descriptors altered after approval. RSA-based manifest signing enforces descriptor integrity [and] reduces unsafe tool invocation rates without model fine-tuning."

---

### Paper 5.5
**Title:** Enterprise-Grade Security for the Model Context Protocol (MCP): Frameworks and Mitigation Strategies  
**ArXiv ID:** arXiv:2504.08623  
**Authors:** Vineeth Sai Narajala, Idan Habler  
**Date:** April 11, 2025  
**URL:** https://arxiv.org/abs/2504.08623

**Core Contribution:** Translates theoretical MCP security concerns into enterprise-grade, implementable mitigation frameworks via systematic threat modeling. Focuses on sophisticated threats like tool poisoning and provides actionable security patterns tailored for MCP implementers at production scale.

**Relevance to NegotiatorGrid:** MEDIUM  
*Provides production-grade security implementation patterns applicable to NegotiatorGrid's MCP deployment on Kite AI. The enterprise framing is suitable for pitching NegotiatorGrid to enterprise clients.*

**Key Implementation Takeaways:**
- Adopt the paper's threat modeling methodology for NegotiatorGrid's MCP interface security review before production deployment
- Tool poisoning mitigation: implement allowlisting of approved NegotiatorGrid tool schemas at the MCP server level
- Create a security runbook for NegotiatorGrid MCP operations using this paper's framework

**Quotable for Demo/Judges:**
> "This paper delivers enterprise-grade mitigation frameworks and detailed technical implementation strategies... translating theoretical security concerns into a practical, implementable framework with actionable controls."

---

### Paper 5.6
**Title:** A Systematic Security Analysis of Model Context Protocol: Vulnerabilities, Exploits, and Mitigations  
**DOI:** 10.1109/ICAIC67076.2026.11395848  
**Authors:** Theophilus Siameh, Abigail Akosua Addobea, Chun-Hung Liu, Eric Kudjoe Fiah  
**Date:** February 18, 2026  
**URL:** https://ieeexplore.ieee.org/document/11395848/

**Core Contribution:** First thorough security assessment of MCP implementations via penetration testing of 15 MCP server implementations. Finds that 87% have at least one critical security flaw and 34% are vulnerable to full system takeover. Develops a classification system for MCP security threats with defensive measures that decrease successful attack rates by up to 94%.

**Relevance to NegotiatorGrid:** MEDIUM  
*The empirical finding that 87% of MCP servers have critical flaws is a strong justification for NegotiatorGrid's defensive security layer. The 94% attack reduction figure from proposed mitigations validates the investment in MCP security for production deployment.*

**Key Implementation Takeaways:**
- Before production deployment, conduct penetration testing of NegotiatorGrid's MCP server against the paper's attack taxonomy (directory traversal, SQL injection, credential theft, resource exhaustion)
- Implement resource exhaustion limits for negotiation sessions: maximum rounds, maximum message length, maximum session duration
- Use the paper's classification system as a checklist for NegotiatorGrid's security review

**Quotable for Demo/Judges:**
> "87% of examined MCP servers have at least one critical security flaw... [Our] effective defensive measures decrease successful attack rates by as much as 94%."

---

## Category 6: Opponent Modeling & Strategy Adaptation

---

### Paper 6.1
**Title:** BDI-based Opponent Modeling and Strategy Generation for Multi-Issue Negotiation  
**DOI:** 10.1609/aaai.v40i48.42246  
**Authors:** Tianzi Ma, Yulin Wu, H. Ren, Xiaozhen Sun, Shuhan Qi, Xuan Wang  
**Date:** March 14, 2026 (AAAI-26)  
**URL:** https://ojs.aaai.org/index.php/AAAI/article/view/42246

**Core Contribution:** Proposes a BDI (Belief-Desire-Intention) framework for opponent modeling and strategy generation in multi-issue automated negotiation. The Belief module tracks opponent responses, Desire module predicts preference weights and utility functions, and Intention module infers utilities of future offers. Builds a responsive strategy enabling gradual concessions and balanced outcomes, tested across 45 negotiation domains against 12 representative opponents.

**Relevance to NegotiatorGrid:** HIGH  
*The BDI architecture maps directly to NegotiatorGrid's negotiation agent structure: Belief (track counterparty offers), Desire (model their utility function/reservation price), Intention (predict acceptance probability of next offer). The multi-domain testing across 12 opponents validates the approach's generalizability.*

**Key Implementation Takeaways:**
- Implement NegotiatorGrid's opponent model using BDI architecture: Belief layer updates after each offer, Desire layer maintains utility function estimate, Intention layer generates acceptance probability for candidate offers
- D-MBUE (Desire Module's utility estimation) and I-DABI (Intention Module's acceptance inference) are specific algorithms implementable in Python
- Test NegotiatorGrid agents across diverse counterparty types (greedy, cooperative, random, tit-for-tat) mimicking the paper's 12-opponent evaluation suite

**Quotable for Demo/Judges:**
> "The BDI Negotiator framework: analyzes opponent responses (Belief), predicts preference weights and the utility function (Desire), and infers utilities of future offers (Intention)... demonstrating effectiveness across 45 standard negotiation domains and against 12 representative opponents."

---

### Paper 6.2
**Title:** ASTRA: A Negotiation Agent with Adaptive and Strategic Reasoning through Action in Dynamic Offer Optimization  
**ArXiv ID:** arXiv:2503.07129  
*(Full entry in Category 1 — cross-referenced here for opponent modeling relevance)*  
**URL:** https://arxiv.org/abs/2503.07129

**Relevance to Category 6:** HIGH  
*ASTRA's opponent modeling stage (Stage 1) is specifically the fairness and stance assessment phase, which classifies the counterparty as Tit-for-Tat, cooperative, or greedy in real time. This is the most LLM-native opponent modeling approach in the literature.*

**Key Implementation Takeaways (opponent modeling specific):**
- ASTRA's "Preference Asker" and "Preference Consistency Checker" modules can detect when counterparty preferences shift mid-session (strategy switch detection)
- Linguistic cues for opponent stance classification: urgency words → aggressive agent, qualifiers and hedging → flexible agent, hard numbers only → algorithmic/non-LLM agent

---

### Paper 6.3
**Title:** Optimizing Automated Negotiation: Integrating Opponent Modeling with Reinforcement Learning for Strategy Enhancement  
**DOI:** 10.3390/math13040679  
**Authors:** Ya Zhang, Jinghua Wu, Ruiyang Cao  
**Date:** February 19, 2025  
**URL:** https://www.mdpi.com/2227-7390/13/4/679

**Core Contribution:** Proposes an automated negotiation framework combining network topology analysis of agent relationships with RL-based strategy optimization. Uses relationship strength from agent relational networks to adjust expectations, and relationship classification to tune discount factors in Q-learning negotiation algorithms. Outperforms existing frameworks in negotiation efficiency, utility, and fairness.

**Relevance to NegotiatorGrid:** HIGH  
*For repeated negotiations between known agents on Kite AI, the relationship-strength-based strategy adjustment is highly applicable: NegotiatorGrid agents that have negotiated before can adjust their opening offers and concession rates based on historical relationship data.*

**Key Implementation Takeaways:**
- Maintain a relationship-strength score between agent pairs, updated after each negotiation session — this score influences initial offer aggressiveness
- Q-learning discount factor should be tuned to relationship type: cooperative agent → higher discount (patient, long-horizon), competitive agent → lower discount (demand faster convergence)
- Network topology analysis: agents central to the Kite AI service graph have more negotiating leverage — encode this as a prior in the opponent model

**Quotable for Demo/Judges:**
> "Agents' expectations are adjusted according to relationship strength, ensuring that expectations of negotiating parties are accurately represented across varying levels of relationship strength."

---

### Paper 6.4
**Title:** ChargingBoul: A Competitive Negotiating Agent with Novel Opponent Modeling  
**ArXiv ID:** arXiv:2512.06595  
**Authors:** Joe Shymanski  
**Date:** December 6, 2025  
**URL:** https://arxiv.org/abs/2512.06595

**Core Contribution:** Presents ChargingBoul, a 2022 ANAC competition agent achieving near-top performance through lightweight opponent classification based on bid patterns, dynamic bidding strategy adjustment, and late-session concession policy for agreement fostering. Demonstrates effectiveness across diverse opponent strategies.

**Relevance to NegotiatorGrid:** MEDIUM  
*ChargingBoul's bid-pattern-based opponent classification is directly implementable in NegotiatorGrid as a lightweight, low-latency opponent type detector that runs between rounds. The "apply concession in later stages" policy mirrors time-deadline-aware negotiation needed for payment protocol timeouts.*

**Key Implementation Takeaways:**
- Classify counterparty type after 2–3 rounds based on bid pattern: monotone decreasing → standard agent, non-monotone → LLM agent, large variance → random/adversarial agent
- Implement deadline-aware concession: as session approaches time limit, increase concession rate to ensure deal completion before payment protocol timeout
- ChargingBoul's strategy is lightweight enough to run as a real-time subroutine within NegotiatorGrid's per-round decision loop

**Quotable for Demo/Judges:**
> "ChargingBoul classifies opponents based on bid patterns, dynamically adjusts its bidding strategy, and applies a concession policy in later negotiation stages to maximize utility while fostering agreements."

---

### Paper 6.5
**Title:** A Survey of Opponent Modeling Techniques in Automated Negotiation  
**DOI:** 10.65109/wmkq1942  
**Authors:** T. Baarslag, M. Hendrikx, K. Hindriks, C. Jonker  
**Date:** 2016 (AAMAS — foundational reference)  
**URL:** https://dl.acm.org/doi/10.5555/2936924.2937008

**Core Contribution:** Comprehensive survey of opponent modeling techniques in bilateral negotiation, introducing a taxonomy based on underlying learning techniques. Surveys all uses of opponent modeling (preference estimation, strategy recognition, acceptance modeling) and provides performance measurement guidelines. Establishes that bidding strategy dominates opponent modeling in importance.

**Relevance to NegotiatorGrid:** MEDIUM  
*Foundational reference — provides the conceptual vocabulary and evaluation metrics for NegotiatorGrid's opponent modeling component. The bidding-dominates-opponent-modeling finding suggests NegotiatorGrid should prioritize robust offer generation over elaborate opponent inference.*

**Key Implementation Takeaways:**
- Focus engineering effort on bidding strategy first (Pareto-optimal offer generation, LP-based optimization), then opponent modeling refinements
- Use Baarslag's evaluation metrics: preference estimation accuracy (RMSE), strategy recognition accuracy, and their contribution to final utility gain
- Frequency-based preference estimation (count which issues opponent concedes on most) is the simplest implementable opponent model for NegotiatorGrid v1

**Quotable for Demo/Judges:**
> "The bidding strategy in particular is of critical importance to the negotiator's success and far exceeds the importance of opponent preference modeling techniques."

---

### Paper 6.6
**Title:** Indirect Dynamic Negotiation in the Nash Demand Game  
**ArXiv ID:** arXiv:2409.06566  
**Authors:** Tatiana V. Guy, Jitka Homolová, Aleksej Gaj  
**Date:** September 10, 2024  
**URL:** https://arxiv.org/abs/2409.06566

**Core Contribution:** Addresses sequential bilateral bargaining with incomplete information using indirect negotiation via closed-loop interaction, where agents learn the opponent's model through observed behavior. Applies the model to the Nash demand game, showing that indirect negotiation leads to coordinating behavior even without direct information sharing.

**Relevance to NegotiatorGrid:** MEDIUM  
*The Nash demand game formalization applies directly to NegotiatorGrid's bilateral price negotiation: each agent demands a price, and agreement occurs when demands are compatible. The indirect learning mechanism (learn opponent model from offers) is the foundation of NegotiatorGrid's session-level strategy adaptation.*

**Key Implementation Takeaways:**
- Formalize NegotiatorGrid's protocol as a Nash demand game: buyer demands price ≤ P_max, seller demands price ≥ P_min; agreement iff P_min ≤ P_max
- Indirect negotiation: agents adjust their demands based on observed opponent behavior rather than disclosed preferences — implement via Bayesian belief update per round
- Nash bargaining solution (maximize product of surpluses) provides a fairness benchmark for evaluating NegotiatorGrid settlement quality

**Quotable for Demo/Judges:**
> "The established negotiation leads to coordinating behavior [between agents] via closed-loop interaction, enabling successful bargaining with incomplete information through indirect negotiation."

---

### Paper 6.7
**Title:** Game Theory Meets Large Language Models: A Systematic Survey  
**ArXiv ID:** arXiv:2502.09053  
**Authors:** Haoran Sun, Yusen Wu, Yukun Cheng, Xu Chu  
**Date:** February 13, 2025  
**URL:** https://arxiv.org/abs/2502.09053

**Core Contribution:** Comprehensive survey of the bidirectional relationship between game theory and LLMs: (1) applying game-theoretic methods to evaluate/enhance LLM capabilities, and (2) LLMs reshaping classic game models. Covers Nash equilibrium computation, mechanism design, auction theory, and bargaining with LLM agents.

**Relevance to NegotiatorGrid:** MEDIUM  
*Provides the theoretical grounding for NegotiatorGrid's game-theoretic foundations. The survey of Nash equilibrium computation with LLMs directly informs how NegotiatorGrid should model convergence guarantees and equilibrium properties of the bilateral bargaining game.*

**Key Implementation Takeaways:**
- Use game-theoretic analysis to derive NegotiatorGrid's convergence guarantee: under what conditions does bilateral LLM bargaining converge to an agreement within a finite number of rounds?
- Mechanism design perspective: structure the NegotiatorGrid protocol as a revelation mechanism where truthful reporting of constraints is the dominant strategy
- LLM behavioral economics findings (anchoring, loss aversion, framing effects) should inform NegotiatorGrid's offer framing logic

**Quotable for Demo/Judges:**
> "LLMs reshap[e] classic game models [including bargaining]... game-theoretic methods are being applied to evaluate and enhance LLM capabilities in strategic interaction."

---

## Summary Table

| # | Title (Short) | Category | ArXiv ID | Date | Relevance |
|---|--------------|----------|----------|------|-----------|
| 1.1 | AgenticPay Benchmark | Cat 1 | 2602.06008 | Feb 2026 | HIGH |
| 1.2 | ASTRA Framework | Cat 1 | 2503.07129 | Mar 2025 | HIGH |
| 1.3 | BargainArena / Utility Feedback | Cat 1 | 2505.22998 | May 2025 | HIGH |
| 1.4 | LLM Rationalis / Concession CRI | Cat 1 | 2512.13063 | Dec 2025 | HIGH |
| 1.5 | NegotiationArena | Cat 1 | 2402.05863 | Feb 2024 | HIGH |
| 1.6 | NegoLog Framework | Cat 1 | IJCAI-24 | Aug 2024 | HIGH |
| 1.7 | AI Negotiations Competition | Cat 1 | 2503.06416 | Mar 2025 | MEDIUM |
| 1.8 | Game-theoretic LLM Workflow | Cat 1 | 2411.05990 | Nov 2024 | HIGH |
| 2.1 | SoK A2A Payments ⭐ | Cat 2 | 2604.03733 | Apr 2026 | HIGH |
| 2.2 | A402 Atomic Payments | Cat 2 | 2603.01179 | Mar 2026 | HIGH |
| 2.3 | Agent Economy Foundation | Cat 2 | 2602.14219 | Feb 2026 | HIGH |
| 2.4 | A2A + x402 Architecture | Cat 2 | 2507.19550 | Jul 2025 | HIGH |
| 2.5 | Secure Agent Payments | Cat 2 | 2511.15712 | Nov 2025 | HIGH |
| 2.6 | Governing A2A Economy | Cat 2 | 2501.16606 | Jan 2025 | MEDIUM |
| 3.1 | Inter-Agent Trust Models | Cat 3 | 2511.03434 | Nov 2025 | HIGH |
| 3.2 | BlockA2A Security | Cat 3 | 2508.01332 | Aug 2025 | HIGH |
| 3.3 | Incentive-Compatible LLM MAS | Cat 3 | IEEE 2026 | 2026 | HIGH |
| 3.4 | Trust-as-a-Service Marketplace | Cat 3 | 2403.04779 | Mar 2024 | MEDIUM |
| 4.1 | BAID Agent Identity | Cat 4 | 2512.17538 | Dec 2025 | HIGH |
| 4.2 | Agent Contracts Formal | Cat 4 | 2601.08815 | Jan 2026 | HIGH |
| 4.3 | Account Abstraction NFR | Cat 4 | IEEE 2025 | Sep 2025 | HIGH |
| 4.4 | AA + AI Wallet Automation | Cat 4 | IEEE 2025 | Oct 2025 | MEDIUM |
| 4.5 | Eliza Web3 Agent OS | Cat 4 | 2501.06781 | Jan 2025 | MEDIUM |
| 5.1 | MCP Landscape Threats ⭐ | Cat 5 | 2503.23278 | Apr 2025 | HIGH |
| 5.2 | MCP Production Patterns ⭐ | Cat 5 | 2603.13417 | Mar 2026 | HIGH |
| 5.3 | MCP Risks Controls Governance | Cat 5 | 2511.20920 | Nov 2025 | HIGH |
| 5.4 | MCP Tool Poisoning Defense | Cat 5 | 2512.06556 | Dec 2025 | HIGH |
| 5.5 | MCP Enterprise Security | Cat 5 | 2504.08623 | Apr 2025 | MEDIUM |
| 5.6 | MCP Systematic Pentest | Cat 5 | IEEE 2026 | Feb 2026 | MEDIUM |
| 6.1 | BDI Opponent Modeling | Cat 6 | AAAI-26 | Mar 2026 | HIGH |
| 6.2 | ASTRA (Opponent Modeling) | Cat 6 | 2503.07129 | Mar 2025 | HIGH |
| 6.3 | RL + Opponent Modeling | Cat 6 | MDPI 2025 | Feb 2025 | HIGH |
| 6.4 | ChargingBoul ANAC Agent | Cat 6 | 2512.06595 | Dec 2025 | MEDIUM |
| 6.5 | Survey: Opponent Modeling | Cat 6 | ACM 2016 | 2016 | MEDIUM |
| 6.6 | Nash Demand Game Indirect | Cat 6 | 2409.06566 | Sep 2024 | MEDIUM |
| 6.7 | Game Theory Meets LLMs Survey | Cat 6 | 2502.09053 | Feb 2025 | MEDIUM |

---

## Key Quotes Bank for Demo / Judges

**On the payment gap NegotiatorGrid fills:**
> "For the first time, we systematize blockchain-based A2A payments, e.g., X402, with a four-stage lifecycle... [identifying] weak intent binding, misuse under valid authorization, payment-service decoupling, and limited accountability." — SoK A2A Payments (arXiv:2604.03733)

**On why LLM negotiation works:**
> "AgenticPay models markets in which buyers and sellers possess private constraints and product-dependent valuations, and must reach agreements through multi-round linguistic negotiation rather than numeric bidding alone." — AgenticPay (arXiv:2602.06008)

**On convergence and rationality:**
> "Game-theoretic workflows that guide the reasoning and decision-making processes of LLMs [significantly improve] performance [in negotiation games]." — Game-theoretic LLM (arXiv:2411.05990)

**On the technical x402 architecture:**
> "By seamlessly integrating the x402 micropayment flow into the A2A protocol through standard HTTP headers, frictionless, blockchain-agnostic payments are facilitated between agents." — A2A+x402 Architecture (arXiv:2507.19550)

**On trust and identity:**
> "We argue for trustless-by-default architectures anchored in Proof and Stake to gate high-impact actions." — Inter-Agent Trust Models (arXiv:2511.03434)

**On MCP as infrastructure:**
> "Three protocol-level primitives remain missing [from MCP]: identity propagation, adaptive tool budgeting, and structured error semantics." — MCP Production Patterns (arXiv:2603.13417)

**On opponent modeling:**
> "The BDI Negotiator framework: analyzes opponent responses (Belief), predicts preference weights and utility function (Desire), and infers utilities of future offers (Intention)." — BDI Opponent Modeling (AAAI-26)

**On the blockchain foundation:**
> "Blockchain technology provides three critical properties enabling genuine agent autonomy: permissionless participation, trustless settlement, and machine-to-machine micropayments." — Agent Economy (arXiv:2602.14219)

---

*Research compiled: 2026. All arXiv papers verified via direct URL fetch.*
