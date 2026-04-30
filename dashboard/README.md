# NegotiatorGrid Dashboard

Next.js static-export dashboard for the NegotiatorGrid demo.

The dashboard should present the actual procurement workflow on the first screen:

```text
discover provider -> negotiate terms -> Passport Session Fit -> x402 settlement -> attestation
```

## Demo Narrative

NegotiatorGrid extends Kite Agent Passport from **authorized payments** to **authorized procurement**. Passport controls whether an agent is allowed to spend. NegotiatorGrid decides whether the negotiated deal is good, fair, bounded, and safe enough to pay.

Key UI surfaces:

- Price convergence chart with buyer/seller offers and Nash band.
- Negotiation timeline with typed deal fields treated as authoritative.
- Agent identity/reputation cards.
- **Passport Session Fit** panel showing negotiated price, remaining Session budget, per-payment cap, merchant/payee, asset/token, TTL, and pass/fail status.
- Settlement and attestation feed with clear live/mock labels.

## Commands

```bash
npm install
npm run dev
npm run build
```

The app is configured for static export. Build output goes to `out/`.

## Environment

Copy `.env.local.example` to `.env.local` when running locally.

Expected public values:

- `NEXT_PUBLIC_API_BASE_URL` - backend REST API base URL
- `NEXT_PUBLIC_WS_URL` - backend WebSocket URL
- `NEXT_PUBLIC_CHAIN_ID` - Kite network chain ID used by the demo
- `NEXT_PUBLIC_EXPLORER_URL` - KiteScan/explorer URL for attestation links

Label mock paths honestly in the UI: `Passport MCP live`, `Passport-compatible mock`, `x402 live`, or `mock facilitator`.
