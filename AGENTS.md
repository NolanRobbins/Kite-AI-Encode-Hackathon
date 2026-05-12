# NegotiatorGrid — agent instructions

## Engineering workflow

Follow skill files under:

`c:\Users\Robbinhood\OneDrive\Desktop\VS Code Projects\Go-Tos\agent-skills\skills\`

Use especially:

- **spec-driven-development** — PRD / acceptance criteria before implementation
- **test-driven-development** — red–green–refactor; test pyramid
- **code-review-and-quality** — before merge: design, correctness, complexity, tests, naming
- **shipping-and-launch** — pre-launch checks, rollback mindset

When a task needs a workflow, `@`-reference the relevant `SKILL.md` under that folder (or summarize its process in-chat).

## Repo-specific context

- **Product framing (embedding NG in procurement agents):** see root `CONTEXT.md` — dev-time module on agents, asymmetric vs bilateral Nash-oriented outcomes; keep the importable package separable from the demo API.
- **Dashboard (Next.js static export):** see `dashboard/AGENTS.md` for non-negotiable Next.js constraints, API/WebSocket contracts, and mock fallbacks.

## Agent skills

### Issue tracker

GitHub Issues for this repository; use the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Canonical triage roles map to labels `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: root `CONTEXT.md` and `docs/adr/` when present. See `docs/agents/domain.md`.
