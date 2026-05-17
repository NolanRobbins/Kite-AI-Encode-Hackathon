# NEXT_UP — operator pointer

**Last updated:** May 12, 2026

**Authoritative plan:** [`research-plan-docs/8.7-hackathon-final-sprint.md`](research-plan-docs/8.7-hackathon-final-sprint.md)

That doc supersedes the older operator checklists in `STATUS.md`, `8.3`, `8.4`, `8.5` for demo, deployment, and submission scope. Older docs are kept for historical reference, not execution.

## Quick state

- **Track:** Novel
- **Target:** 3:30 demo video, 3 live deploys (Railway × 2 + Vercel), on-chain attestation on Kite testnet, Novel-first 250-word submission
- **Paid task in demo:** NVDA quote via `surprise_api`
- **Hero moments:** hash-mismatch rejection + reputation-conditioned strategy
- **Glossary lock:** `deal_hash = keccak256(buyer_id, seller_id, agreed_price, deal_bound_at, nonce)` per `CONTEXT.md`

## Execution order

1. Glossary fix (Solidity ↔ Python ↔ narration alignment)
2. Deploy 3 contracts to Kite testnet
3. Rewrite `demo.py` against deployed contracts (MCP discovery → surprise_api → NVDA → 2 negotiations → rejection)
4. Deploy 3 services (backend, surprise_api, dashboard)
5. Dashboard polish (Session Fit, rejection state, rep-conditioned split, KiteScan links, badges)
6. Record + edit + submit

Full backlog with estimates, acceptance criteria, risk register, and env var cheat sheet: [`research-plan-docs/8.7-hackathon-final-sprint.md`](research-plan-docs/8.7-hackathon-final-sprint.md).
