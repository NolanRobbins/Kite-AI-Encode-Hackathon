#!/bin/bash
# Run Next.js dashboard on :3000 from repo root

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DASHBOARD="$REPO_ROOT/dashboard"

cd "$DASHBOARD"
npm run dev -- --hostname 127.0.0.1 --port 3000
