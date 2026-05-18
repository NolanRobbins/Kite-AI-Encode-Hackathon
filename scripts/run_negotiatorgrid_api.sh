#!/bin/bash
# Run NegotiatorGrid FastAPI on :8000 using the repo virtualenv

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$REPO_ROOT/.venv-demo/bin/python"

if [ ! -f "$PY" ]; then
    echo "ERROR: Missing interpreter: $PY"
    echo "Run: uv venv .venv-demo  then  uv pip install -r requirements.txt"
    exit 1
fi

cd "$REPO_ROOT"
export PYTHONIOENCODING=utf-8
"$PY" -m uvicorn negotiatorgrid.api.server:app --host 127.0.0.1 --port 8000 "$@"
