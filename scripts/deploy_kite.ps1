# deploy_kite.ps1 - end-to-end Kite Testnet deployment orchestration.
#
# Prerequisites (ONE-TIME):
#   1. Install Node.js 20+ and npm.
#   2. Generate a disposable deployer wallet. NEVER use a production key.
#   3. Fund the wallet via the Kite faucet: https://faucet.gokite.ai
#      (0.5 KITE/day; get at least two claims before running.)
#   4. Copy contracts\.env.example -> contracts\.env and paste your PRIVATE_KEY.
#
# Run from the project root:
#   .\scripts\deploy_kite.ps1
#
# What this does:
#   1. Checks that contracts\.env exists with a real private key.
#   2. npm install in contracts/ (idempotent).
#   3. npx hardhat compile.
#   4. npx hardhat ignition deploy ignition/modules/NegotiatorGrid.ts --network kiteTestnet.
#   5. python scripts\sync_abis.py               -> copies ABIs to negotiatorgrid/contracts/abi/
#   6. python scripts\sync_contract_addresses.py -> upserts addresses into root .env
#
# Re-runnable: safe to run again after contract edits; Ignition will only redeploy
# contracts whose bytecode changed.

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$contractsDir = Join-Path $projectRoot "contracts"
$envFile = Join-Path $contractsDir ".env"

# ---------------------------------------------------------------------------
# 1. Sanity checks
# ---------------------------------------------------------------------------

if (-not (Test-Path $envFile)) {
    Write-Error "contracts\.env not found. Copy contracts\.env.example and set PRIVATE_KEY."
    exit 1
}

$envLines = Get-Content $envFile
$pkLine = $envLines | Where-Object { $_ -match '^PRIVATE_KEY=' }
if (-not $pkLine -or $pkLine -match 'your_deployer_private_key') {
    Write-Error "PRIVATE_KEY not set in contracts\.env. Add a real 0x... key before running."
    exit 1
}

Write-Host "==> Project root: $projectRoot" -ForegroundColor Cyan
Write-Host "==> Using deployer key from contracts\.env" -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# 2. npm install
# ---------------------------------------------------------------------------

Write-Host ""
Write-Host "==> [1/4] npm install in contracts/" -ForegroundColor Green
Push-Location $contractsDir
try {
    if (-not (Test-Path (Join-Path $contractsDir "node_modules"))) {
        npm install
        if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
    } else {
        Write-Host "    node_modules already present, skipping (delete to reinstall)"
    }

    # ---------------------------------------------------------------------------
    # 3. Compile
    # ---------------------------------------------------------------------------

    Write-Host ""
    Write-Host "==> [2/4] hardhat compile" -ForegroundColor Green
    npx hardhat compile
    if ($LASTEXITCODE -ne 0) { throw "hardhat compile failed" }

    # ---------------------------------------------------------------------------
    # 4. Deploy via Ignition
    # ---------------------------------------------------------------------------

    Write-Host ""
    Write-Host "==> [3/4] Deploying to Kite Testnet (chain 2368)..." -ForegroundColor Green
    Write-Host "    This will take 30-90s. Ignition will output deployed addresses at the end." -ForegroundColor Gray
    npx hardhat ignition deploy ignition/modules/NegotiatorGrid.ts --network kiteTestnet
    if ($LASTEXITCODE -ne 0) { throw "ignition deploy failed" }
}
finally {
    Pop-Location
}

# ---------------------------------------------------------------------------
# 5. Sync artifacts back into the Python package + root .env
# ---------------------------------------------------------------------------

Write-Host ""
Write-Host "==> [4/4] Syncing ABIs + addresses into Python package" -ForegroundColor Green

python scripts\sync_abis.py
if ($LASTEXITCODE -ne 0) { Write-Warning "ABI sync failed (continuing)" }

python scripts\sync_contract_addresses.py --chain 2368
if ($LASTEXITCODE -ne 0) { throw "Address sync failed" }

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

Write-Host ""
Write-Host "==> DONE." -ForegroundColor Green
Write-Host "    Verify deployed contracts on KiteScan:" -ForegroundColor Cyan
Write-Host "      https://testnet.kitescan.ai/" -ForegroundColor Cyan
Write-Host ""
Write-Host "    Root .env now contains DEALRECORD_CONTRACT_ADDR / IDENTITY_REGISTRY_ADDR / REPUTATION_REGISTRY_ADDR." -ForegroundColor Cyan
Write-Host "    The Python backend will pick these up on next startup and switch out of mock mode." -ForegroundColor Cyan
