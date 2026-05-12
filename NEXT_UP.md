# NEXT_UP - operator checklist

**Last updated:** May 11, 2026

Practical checklist for refining the finished NegotiatorGrid demo now that Kite Agent Passport has launched. Order is roughly by impact.

---

## 1. Tighten the Passport procurement story

- Update demo language to: **NegotiatorGrid extends Kite Agent Passport from authorized payments to authorized procurement.**
- Make the flow explicit: negotiate terms -> create Passport-compatible payment intent -> check active Session -> settle via x402 -> attest deal.
- Avoid claiming NegotiatorGrid creates its own Passport spending authority. Passport Sessions/Delegations are the authority layer; NegotiatorGrid is the policy/deal-quality layer.

## 2. Dashboard refinement

- Add or emphasize a **Passport Session Fit** panel: negotiated price, remaining Session budget, per-payment cap, merchant/payee, asset/token, TTL, and pass/fail status.
- In the settlement/attestation panels, label live vs mock clearly: `Passport MCP live`, `Passport-compatible mock`, `x402 live`, or `mock facilitator`.
- Keep the first screen focused on the actual procurement workflow, not a landing page.
- **Deferred (optional):** add a small **Act 3 compare** panel when you want self-serve testing without leaving the UI. The backend already exposes `POST /api/act3/compare` and `GET /api/act3/compare/{high_id}/{low_id}` (see `negotiatorgrid/api/act3_compare.py`). Judges do not require this in the dashboard if you hit the same flow from curl, Postman, or your demo script; treat it as a later polish item.

## 3. Environment & secrets

- Copy `.env.example` -> `.env` and fill in what you actually use: **`PRIVATE_KEY` / buyer wallet**, **`OPENAI_API_KEY`** if you want live LLM offers, and Kite Passport MCP credentials/token only if you want live Passport MCP.
- **Never commit** `.env` or keys; confirm nothing sensitive is staged before you push.

## 4. Kite network, money, and Passport

- Use whichever Passport environment is currently available for your account. Keep Kite testnet/faucet setup as the safe demo path until live payment access is stable.
- If you run real x402/USDT-style flows, note `current_tech_problems.md`: stablecoin/facilitator mismatches are a known pain. Have **mock facilitator** + CLI backup ready for recording.
- If you want real on-chain attestations, deploy `DealRecord`, `IdentityRegistry`, and `ReputationRegistry` to Kite testnet and put their addresses into backend + dashboard env vars.

## 5. Deploy backend + dashboard

- **Backend**: Railway using root `Dockerfile` + `railway.toml`, or run `uvicorn` manually for local demo.
- **Dashboard**: Vercel or similar with **`NEXT_PUBLIC_API_BASE_URL`** and **`NEXT_PUBLIC_WS_URL`** pointing at real API/WebSocket URLs **before** `npm run build`.
- **Surprise API** if shown: deploy separately from `surprise_api/`.

## 6. One live smoke pass

- Open deployed dashboard -> **Start Negotiation** -> confirm rounds + Passport Session Fit + settlement/attestation.
- **Act 3 compare (API):** `POST /api/act3/compare` with body `{}` → take `high_rep.negotiation_id` and `low_rep.negotiation_id` → poll `GET /api/act3/compare/{high_id}/{low_id}` until `both_complete` is true. No dashboard page required for this path.
- Hit **Act 5** flows if those are in your script.
- Confirm **WebSocket** works through your real URL, not `localhost`.

## 7. Demo artifacts

- **Record** the main demo against the deployed app.
- Keep a **backup**: `python demo.py`, Passport-compatible mock flow, and a pre-recorded clip if the network hiccups.
- Write the **~250-word** submission text and grab **screenshots/GIFs** when the deployed UI looks good.

## 8. Encode Club submission

- Submit before the deadline, **screenshot** confirmation, then **stop changing** the stack unless something breaks.

# Potential sandbox of agents

- https://veris.ai/sandbox

---

**Short version:** refine Passport procurement story -> show Session Fit in dashboard -> set env -> deploy backend + frontend with correct public URLs -> run one end-to-end click-through -> record video -> submit.
