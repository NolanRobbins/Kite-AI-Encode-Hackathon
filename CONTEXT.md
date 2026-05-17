# NegotiatorGrid — project context

Canonical domain and product framing for this repository. Additional module-focused context lives in `docs/module-context.md`; prefer **this file** for names in issues, refactors, and tests.

## Glossary

| Term | Meaning |
| ---- | ------- |
| **NegotiatorGrid (NG)** | Python-side negotiation and trust layer: bounded rounds, reputation signals, Nash-oriented guardrails, and a binding **deal hash** before payment rails run. |
| **Library surface** | Stable Python API that another developer imports into an agent runtime; it exposes core negotiation primitives without requiring the demo API or dashboard. |
| **Deal** | A completed bilateral outcome: agreed price, round count, and **deal hash** suitable for x402 / Passport alignment. |
| **Deal hash** | Cryptographic identifier of a completed deal. Two distinct hashes co-exist by design: (1) **off-chain deal_hash** — a short fingerprint computed in `negotiatorgrid.core.negotiation` from buyer id, seller id, agreed price, round count, and start time; carried in `NegotiationResult.deal_hash` and in `x402` `extra.deal_hash` so the buyer can refuse any mutated 402 response. (2) **on-chain dealHash** — `keccak256(abi.encodePacked(buyer, seller, finalPrice, resourceUri, timestamp, negotiationRounds))` computed by `DealRecord.recordDeal`. Both uniquely identify the same deal in their respective layers; they are not required to be byte-equal. The attestation pipeline (`negotiatorgrid.core.attestation`) constructs a Solidity-compatible `DealAttestation` and lets the contract derive the canonical on-chain `dealHash`. |
| **deal_bound_at** | Unix second frozen when parties agree. Carried alongside the deal so the on-chain `timestamp` field used in the `dealHash` computation matches what the buyer observed at agreement time. |
| **Passport** | Kite Agent Passport: Session, Delegation, payment authorization, and audit trail. |

## Embedding model (north star)

Treat **NegotiatorGrid as a development-time Python module** that teams integrate into **payment / procurement agents** before those agents are deployed. Host APIs, dashboards, and settlement services are integration surfaces, not the core package.

**Asymmetric adoption:** If the buyer’s agent embeds NG and the seller’s stack does not, the NG-backed side should have a structural advantage in **deal** shaping (information, pacing, guardrails, and recorded rationale on typed fields—not prompt tricks).

**Symmetric adoption:** If **both** agents embed NG, the framework’s job is to drive outcomes toward a **fair, bounded negotiation** with explicit Nash-related checks so neither side blindly accepts listed price or opaque terms.

Engineering implication: keep the **library surface** (negotiation engine, types, settlement helpers) **separable** from HTTP, in-memory demo stores, and WebSocket broadcasting so the same package can sit beside an agent runtime in production.

Post-negotiation settle + attest lives in **`negotiatorgrid.post_negotiation`** (`complete_deal_after_negotiation`); callers pass an async `notify(event, payload)` **adapter** (demo uses WebSocket broadcaster). The FastAPI host runs that in a background `asyncio` task after the ledger records the deal row, then **merges** settlement fields into the same deal key.

The first supported import path is the package root for core negotiation:
`NegotiationSession`, `NegotiationConfig`, `NegotiationResult`, `NegotiationOffer`,
`OpponentModeler`, and `NashGuardrail`. Host integrations should import API,
discovery, settlement, and contract helpers from their subpackages so the core
library remains usable without coupling an agent runtime to the demo server.

## Repo layout note

- **`negotiatorgrid/`** — importable package: core negotiation, executors, settlement, discovery, and contract helpers.
- **`negotiatorgrid/api/`** — current optional demo HTTP/WebSocket host; review before keeping in the final core repo.
- **`docs/`** — compact module context, cleanup manifest, and implementation roadmap.
