# NegotiatorGrid — project context

Canonical domain and product framing for this repository. Longer Passport, x402, and demo-runbook detail lives in `negotiatorgrid-context.md`; prefer **this file** for names in issues, refactors, and tests.

## Glossary

| Term | Meaning |
| ---- | ------- |
| **NegotiatorGrid (NG)** | Python-side negotiation and trust layer: bounded rounds, reputation signals, Nash-oriented guardrails, and a binding **deal hash** before payment rails run. |
| **Deal** | A completed bilateral outcome: agreed price, round count, and **deal hash** suitable for x402 / Passport alignment. |
| **Deal hash** | Cryptographic binding over negotiation outcome fields; authoritative for matching payment requirements to the negotiated **deal**. |
| **Passport** | Kite Agent Passport: Session, Delegation, payment authorization, audit trail (see `negotiatorgrid-context.md`). |

## Embedding model (north star)

Treat **NegotiatorGrid as a development-time Python module** that teams integrate into **payment / procurement agents** before those agents are deployed. The reference FastAPI app and dashboard in this repo are a **host and demo surface**, not the only way NG ships.

**Asymmetric adoption:** If the buyer’s agent embeds NG and the seller’s stack does not, the NG-backed side should have a structural advantage in **deal** shaping (information, pacing, guardrails, and recorded rationale on typed fields—not prompt tricks).

**Symmetric adoption:** If **both** agents embed NG, the framework’s job is to drive outcomes toward a **fair, bounded negotiation** with explicit Nash-related checks so neither side blindly accepts listed price or opaque terms.

Engineering implication: keep the **library surface** (negotiation engine, types, settlement helpers) **separable** from HTTP, in-memory demo stores, and WebSocket broadcasting so the same package can sit beside an agent runtime in production.

## Repo layout note

- **`negotiatorgrid/`** — importable package: core negotiation, executors, settlement, contracts helpers.
- **`negotiatorgrid/api/`** — demo and operator HTTP/WebSocket host.
- **`dashboard/`** — static operator UI; see `dashboard/AGENTS.md`.
