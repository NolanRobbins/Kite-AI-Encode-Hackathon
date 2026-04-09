# Security Model

NegotiatorGrid's core value proposition — agents discovering and transacting with unknown counterparties at runtime — introduces a fundamentally different risk profile than static integrations. This document describes the threat model, mitigations, and defense-in-depth architecture.

---

## Threat Model

### Attack Vector 1: Sybil Attacks (Multiple Fake Agents)

**Description**: An attacker creates many fake agent identities to manipulate the marketplace — flooding discovery results, inflating reputation through self-dealing, or cornering pricing in a specific service category.

**Risk**: HIGH — In an open marketplace, identity creation is cheap without gating mechanisms.

**Mitigation**:
- **ERC-8004 Identity Registry** requires on-chain agent registration as an ERC-721 NFT. Each registration costs gas and is permanently associated with a wallet address.
- **Reputation minimum threshold**: The buyer agent's trust gate rejects any counterparty with a reputation score below `MIN_TRUST_SCORE`. New agents with zero history cannot participate in high-value negotiations until they build a track record.
- **Validation Registry**: Third-party validators can independently verify agent capabilities. An agent with no validation results is treated as higher-risk (more aggressive negotiation strategy, lower spending caps).

```python
# Trust gate pseudocode
reputation = await reputation_registry.get_summary(seller_address)
if reputation.score < MIN_TRUST_SCORE:
    return False  # Reject — insufficient reputation
```

---

### Attack Vector 2: Price Manipulation (Colluding Buyer/Seller)

**Description**: Two agents controlled by the same party execute artificial negotiations to create fake deal history — inflating reputation scores or establishing misleading price benchmarks that other agents then use as reference points.

**Risk**: MEDIUM — Profitable in repeated marketplaces where reputation directly affects pricing.

**Mitigation**:
- **Nash guardrail detection**: Every negotiation outcome is validated against the Nash equilibrium computed by pygambit. Deals where both parties "agree" at prices far from the equilibrium range are flagged as suspicious.
- **On-chain attestation transparency**: All deals are recorded on-chain via DealRecord. Statistical anomaly detection over the attestation graph can flag suspiciously convergent pricing patterns between agents that repeatedly transact.
- **Reputation decay**: Reputation scores incorporate recency weighting. An agent that inflates its score through collusion must continuously maintain the scheme to sustain the inflated score.

```python
# Nash guardrail check
equilibria = pygambit.nash.lcp_solve(bilateral_game)
if not any(is_near_equilibrium(agreed_price, eq) for eq in equilibria):
    flag_suspicious_deal(deal_id, reason="outside_nash_range")
```

---

### Attack Vector 3: Replay Attacks (Reusing Old Negotiations)

**Description**: An attacker captures a valid negotiation transcript and replays it to trigger duplicate payments or create false attestations for deals that already settled.

**Risk**: MEDIUM — Standard attack vector in any protocol with signed messages.

**Mitigation**:
- **`deal_hash` uniqueness**: Every deal is identified by a unique `negotiation_id` derived from `keccak256(buyer, seller, timestamp, nonce, transcript)`. The DealRecord contract rejects duplicate `negotiation_id` values.
- **Nonce tracking**: Each agent maintains a monotonically increasing nonce per counterparty. A replayed negotiation with a stale nonce is rejected before reaching the settlement phase.
- **Timestamp validation**: The DealRecord contract validates that the `timestamp` in the attestation is within an acceptable window of the current block timestamp.

```solidity
// DealRecord.sol — replay protection
mapping(bytes32 => bool) public recordedDeals;

function recordDeal(bytes32 negotiationId, ...) external {
    require(!recordedDeals[negotiationId], "Deal already recorded");
    recordedDeals[negotiationId] = true;
    // ... record deal
}
```

---

### Attack Vector 4: Front-Running (MEV on Attestation Transactions)

**Description**: A miner or MEV bot observes a pending `recordDeal()` transaction in the mempool and front-runs it — either to extract value from the settlement or to submit a competing attestation that alters the deal record.

**Risk**: LOW on Kite testnet (low MEV competition), MEDIUM on production EVM chains.

**Mitigation**:
- **DealRecord commit-reveal pattern**: The attestation uses a two-phase approach. First, a commitment hash is submitted (`commitDeal(hash)`). Then, the full deal data is revealed (`revealDeal(data)`). Front-runners who see the commitment cannot extract meaningful information without the reveal data.
- **x402 Facilitator settlement**: The actual payment settlement happens through the Kite Facilitator contract, which processes the x402 payment independently of the attestation. Even if the attestation transaction is front-run, the payment is already settled.
- **Signed deal data**: Both buyer and seller sign the deal terms before attestation. A front-runner cannot forge valid signatures.

---

### Attack Vector 5: Strategy Extraction (Inferring Opponent's Reservation Price)

**Description**: A sophisticated agent systematically probes its counterparty across multiple negotiations to infer the opponent's reservation price (walk-away point), BATNA (best alternative), or concession function parameters — then exploits this information in future negotiations.

**Risk**: MEDIUM — Any multi-round protocol leaks some information through offers.

**Mitigation**:
- **NegMAS BOA separation**: The Bidding, Opponent modeling, and Acceptance components are architecturally separated. An agent's true reservation price is never directly communicated — only offers computed from the utility function are revealed.
- **Aspiration noise**: The bidding strategy adds controlled randomness to offer values, preventing exact inference of the underlying concession curve from observed offers.
- **Reputation-conditioned parameters**: Strategy parameters change based on the counterparty's reputation score, so an attacker cannot learn a fixed strategy profile — the target's behavior varies with each counterparty.
- **Limited round count**: Negotiations are capped at a configurable maximum (default: 10 rounds), limiting the data available for strategy extraction.

---

## Defense-in-Depth Architecture

The three core mitigations form a layered defense stack. Each layer catches what the previous one misses:

```
                    ┌─────────────────────────────────────┐
                    │        DISCOVERY (MCP)               │
                    │   Agent finds unknown counterparty   │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
        Layer 1 →   │     ERC-8004 TRUST GATE              │
                    │  Identity? ✓  Reputation? ✓          │
                    │  Validation? ✓  Endpoint match? ✓    │
                    │                                      │
                    │  BLOCKS: spoofing, unregistered       │
                    │  tools, low-reputation services       │
                    └──────────────┬──────────────────────┘
                                   │ (passes gate)
                    ┌──────────────▼──────────────────────┐
                    │        NEGOTIATION ENGINE             │
                    │  Multi-round price bargaining         │
                    │  + Nash equilibrium validation        │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
        Layer 2 →   │     AA WALLET CONSTRAINT             │
                    │  Per-tx cap ≤ MAX_TX_AMOUNT          │
                    │  Session cap ≤ MAX_SESSION_BUDGET     │
                    │  Session key: expires, whitelisted    │
                    │                                      │
                    │  BLOCKS: wallet drain, overspend,    │
                    │  exfiltration to unknown addresses    │
                    └──────────────┬──────────────────────┘
                                   │ (payment executes)
                    ┌──────────────▼──────────────────────┐
                    │        x402 PAYMENT + SERVICE         │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
        Layer 3 →   │   ATTESTATION AUDIT TRAIL            │
                    │  Record: metadata hash, price,       │
                    │  payment hash, output hash            │
                    │                                      │
                    │  DETECTS: rug-pulls (hash change),   │
                    │  feeds ERC-8004 reputation,           │
                    │  enables forensics                    │
                    └──────────────────────────────────────┘
```

### Coverage Matrix

| Attack | Layer 1 (Trust Gate) | Layer 2 (Wallet) | Layer 3 (Attestation) |
|--------|:-------------------:|:-----------------:|:---------------------:|
| Sybil attacks | Primary | Limits damage | Records for analysis |
| Price manipulation | Partial (reputation) | N/A | Primary (Nash + history) |
| Replay attacks | N/A | Rejects duplicate payment | Primary (unique deal hash) |
| Front-running | N/A | Payment already settled | Commit-reveal pattern |
| Strategy extraction | Partial (varies strategy) | N/A | Limits data via round cap |
| Tool poisoning | Rejects unregistered | Caps financial damage | Records for forensics |
| Rug-pull updates | Reputation may lag | Caps per-session loss | Detects via hash change |

---

## MCP-Specific Threats

NegotiatorGrid uses MCP for dynamic agent discovery, which introduces the attack surface catalogued by Hou et al. [1]:

| Threat | Description | NegotiatorGrid Mitigation |
|--------|-------------|---------------------------|
| **Tool Poisoning** | Hidden instructions in MCP tool metadata manipulate agent behavior | ERC-8004 trust gate rejects unregistered tools; tool metadata hashed at discovery time |
| **Rug-Pull Updates** | Tool behaves correctly initially, then updates to malicious behavior | Attestation trail detects metadata hash changes between sessions; reputation decays |
| **Server Spoofing** | Fake MCP server mimics legitimate one | ERC-8004 identity resolution + endpoint match verification |
| **Cross-Server Shadowing** | Malicious server injects context that redirects calls from legitimate servers | Per-server identity verification; whitelisted payment recipients |
| **RADE** | Malicious instructions embedded in retrieved data | AA wallet spending cap limits blast radius; output scrubbing strips hidden instructions |
| **Credential Theft** | Multi-tool chain exploit exfiltrates credentials | Session keys with expiry + whitelisted contracts; no access to host environment |

### Attack Surface Statistics

Field audits of real MCP servers reveal [2]:
- 43% have command-injection flaws
- 30% have unrestricted URL fetches (SSRF)
- 22% leak files outside sandboxed directories

NegotiatorGrid's ERC-8004 trust gate filters out unverified servers before any data exchange occurs.

---

## Academic References

1. Hou et al., "Model Context Protocol (MCP): Landscape, Security Threats, and Future Research Directions," arXiv:2503.23278, March 2025 — https://arxiv.org/abs/2503.23278
2. Equixly MCP Server Audit (2025), via PromptHub — https://www.prompthub.us/blog/mcp-security-in-2025
3. Zhang et al., "SoK: Blockchain Agent-to-Agent Payments," arXiv:2604.03733, April 2026 — https://arxiv.org/abs/2604.03733
4. ERC-8004: Trustless Agents — https://eips.ethereum.org/EIPS/eip-8004
5. ERC-4337: Account Abstraction — https://eips.ethereum.org/EIPS/eip-4337
6. Jamshidi et al., "MCP Security Framework," arXiv:2512.06556, 2025 — https://arxiv.org/abs/2512.06556
7. Guo et al., "MCPLIB: 31 Attack Methods," arXiv:2508.12538, 2025 — https://arxiv.org/abs/2508.12538
8. Bhatt et al., "Enhanced Tool Definition Interface (ETDI)," IEEE, 2025 — https://ieeexplore.ieee.org/document/11337310/
9. Srinivasan, "MCP Production Design Patterns (CABP, ATBA, SERF)," arXiv:2603.13417, 2026 — https://arxiv.org/abs/2603.13417
10. Errico et al., "Containerized MCP Sandboxing," arXiv:2511.20920, 2025 — https://arxiv.org/abs/2511.20920

---

## Responsible Disclosure

If you discover a security vulnerability in NegotiatorGrid, please report it responsibly:

1. **Do not** open a public GitHub issue for security vulnerabilities.
2. Email the maintainer directly at the address listed in the repository's profile.
3. Include a clear description of the vulnerability, steps to reproduce, and potential impact.
4. Allow a reasonable period (90 days) for the issue to be addressed before public disclosure.

We are committed to investigating and addressing all legitimate security reports. We will acknowledge receipt within 48 hours and provide a timeline for resolution.

**Scope**: This policy covers the NegotiatorGrid codebase, smart contracts, and API endpoints. It does not cover third-party dependencies (NegMAS, x402 SDK, OpenAI API) — please report those to their respective maintainers.

**Note**: NegotiatorGrid is a hackathon prototype deployed on Kite testnet. It is not audited for production use. Do not use it with real funds.
