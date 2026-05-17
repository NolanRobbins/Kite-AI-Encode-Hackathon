# Passport Quickstart (Privacy-First)

This runbook is for enabling live Kite Passport in this repo without sharing personal data, auth tokens, or wallet details in chat.

## 1) Install `kpass` (Windows PowerShell)

```powershell
irm https://cli.gokite.ai/install.ps1 | iex
```

If the installer fails while resolving `latest`, use a pinned bundle:

```powershell
$script = (Invoke-WebRequest -Uri 'https://cli.gokite.ai/install.ps1').Content
& ([scriptblock]::Create($script)) 26
```

## 2) Verify CLI + backend

```powershell
kpass --version
kpass health --output json
kpass status --output json
```

## 3) Authenticate (recommended: login flow)

Use your own email locally. Do not paste OTPs or auth output into chat.

```powershell
kpass login init --email <your_email> --output json
kpass login verify --login-id <login_id> --code <otp_code> --output json
```

If you do not have an account yet, use signup:

```powershell
kpass signup init --email <your_email> --output json
kpass signup poll --signup-id <signup_id> --wait --output json
kpass signup exchange --signup-id <signup_id> --code <exchange_code> --output json
```

## 4) Register agent + create a session

```powershell
kpass agent:register --type negotiatorgrid-buyer --output json
kpass agent:session create --max-amount-per-tx 1 --max-total-amount 5 --ttl 8h --assets USDC --task-summary "NegotiatorGrid hackathon live demo" --output json
```

Approve the session request in Passport UI, then:

```powershell
kpass agent:session status --request-id <request_id> --wait --output json
kpass agent:session use --session-id <session_id> --output json
```

## 5) Fill `.env` for live mode

Set these values in `C:\Users\Robbinhood\OneDrive\Desktop\VS Code Projects\Hackathons\Kite AI Encode Hackathon\.env`:

```dotenv
KITE_PASSPORT_MODE=live
KITE_MCP_ENDPOINT=https://neo.dev.gokite.ai/v1/mcp
KITE_MCP_AUTH_TOKEN=<token from Passport connect flow>
KITE_PASSPORT_AGENT_ID=<agent_id from kpass agent:register>
KITE_PASSPORT_SESSION_ID=<approved session_id>
```

## 6) Confirm runtime posture in this project

```powershell
kpass config show --output json
python -m pytest tests/test_passport_runtime.py -q
```

Expected behavior:
- `KITE_PASSPORT_MODE=live` + valid token => API reports Passport `ready`
- Missing token => API reports Passport `disabled`

## 7) Portal URL note

Use the current Passport dashboard:

- https://agentpassport.ai/dashboard

If your invitation email includes a one-time invite link, start there first, then continue in the dashboard.
