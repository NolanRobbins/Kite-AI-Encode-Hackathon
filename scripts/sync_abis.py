#!/usr/bin/env python3
"""Sync Hardhat contract ABIs → ``negotiatorgrid/contracts/abi/``.

The Python clients in ``negotiatorgrid/contracts/*.py`` use
``load_abi(name)`` which reads from ``negotiatorgrid/contracts/abi/<name>.json``.

This script extracts the ``abi`` field from the compiled Hardhat
artifact JSON and writes it as a bare ABI array to the Python package,
matching the inline ABI fallbacks that already exist in each client.

It is idempotent — rerun after any ``npx hardhat compile`` to pick up
contract changes (e.g., when we add the Day-5 rejected-deal fields).

Usage::

    python scripts/sync_abis.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = PROJECT_ROOT / "contracts" / "artifacts" / "src"
ABI_OUT_DIR = PROJECT_ROOT / "negotiatorgrid" / "contracts" / "abi"

CONTRACTS = ["DealRecord", "IdentityRegistry", "ReputationRegistry"]


def _artifact_path(name: str) -> Path:
    return ARTIFACTS_DIR / f"{name}.sol" / f"{name}.json"


def sync() -> int:
    if not ARTIFACTS_DIR.exists():
        print(
            f"ERROR: {ARTIFACTS_DIR} not found.\n"
            f"Run `npm run compile` in contracts/ first.",
            file=sys.stderr,
        )
        return 1

    ABI_OUT_DIR.mkdir(parents=True, exist_ok=True)

    synced: list[str] = []
    for name in CONTRACTS:
        art_path = _artifact_path(name)
        if not art_path.exists():
            print(f"WARNING: {art_path} missing, skipping", file=sys.stderr)
            continue
        artifact = json.loads(art_path.read_text(encoding="utf-8"))
        abi = artifact.get("abi")
        if not isinstance(abi, list):
            print(f"WARNING: {art_path} has no 'abi' array, skipping", file=sys.stderr)
            continue
        out_path = ABI_OUT_DIR / f"{name}.json"
        out_path.write_text(json.dumps(abi, indent=2) + "\n", encoding="utf-8")
        synced.append(name)

    print(f"Synced ABIs for {len(synced)} contract(s): {', '.join(synced)}")
    return 0


if __name__ == "__main__":
    sys.exit(sync())
