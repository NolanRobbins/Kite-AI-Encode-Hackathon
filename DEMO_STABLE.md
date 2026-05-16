# Demo-Stable Runbook

This branch is optimized for the hackathon demo and submission flow:

- Keep the polished dashboard style and negotiation-focused UX.
- Keep autonomy signals from the newer code (discovery, Act 3 route, ledger-backed API).
- Keep demo startup reproducible with minimal setup friction.

## 1) Environment Setup

From repo root:

```powershell
uv venv .venv-demo
uv pip install -r requirements.txt
```

For the dashboard:

```powershell
cd dashboard
npm install
cd ..
```

## 2) Stable Demo Path (Recommended for Recording)

Open Terminal 1:

```powershell
.\scripts\run_negotiatorgrid_api.ps1
```

Open Terminal 2:

```powershell
.\scripts\run_dashboard.ps1
```

Open browser to:

- `http://localhost:3000`

Run the main negotiation from the home dashboard.

## 3) Optional Wow-Moment Route

If you want the reputation-conditioned side-by-side narrative from the judge critique:

- Open `http://localhost:3000/act3`
- Run paired negotiations

This keeps the main submission demo clean while preserving a high-impact secondary scene.

## 4) Hackathon Checklist Mapping

- Agent performs a task and settles on Kite: use the end-to-end negotiation + settlement path.
- Functional UI: dashboard home route is the primary demo surface.
- Reproducible demo: this runbook + root README quick links.
- Autonomy narrative: emphasize discovery/trust/negotiation/payment/attestation chain.
