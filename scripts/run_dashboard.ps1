# Run Next.js dashboard on :3000 from repo root.
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Dashboard = Join-Path $RepoRoot "dashboard"
Set-Location -LiteralPath $Dashboard
npm.cmd run dev -- --hostname 127.0.0.1 --port 3000
