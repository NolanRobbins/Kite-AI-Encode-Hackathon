# Run Surprise API on :8001 using the repo virtualenv (avoids Conda TypeIs / old typing_extensions).
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Py = Join-Path $RepoRoot '.venv-demo\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Py)) {
    Write-Error "Missing interpreter: $Py - run: uv venv .venv-demo  then  uv pip install -r requirements.txt"
}
Set-Location -LiteralPath $RepoRoot
$env:PYTHONIOENCODING = 'utf-8'
& $Py -m uvicorn surprise_api.app:app --host 127.0.0.1 --port 8001 @args
