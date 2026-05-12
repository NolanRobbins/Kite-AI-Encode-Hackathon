#!/usr/bin/env python3
"""Sync Hardhat Ignition deployment addresses → root ``.env``.

After ``npm run deploy:kite`` runs, Ignition writes every deployed
contract address to::

    contracts/ignition/deployments/chain-2368/deployed_addresses.json

Keys look like ``NegotiatorGrid#IdentityRegistry``. This script reads
that file and upserts the three relevant env vars into the root ``.env``
(creating ``.env`` from ``.env.example`` if it does not exist) so the
Python backend can flip from mock mode to live on-chain reads.

Usage::

    python scripts/sync_contract_addresses.py
    python scripts/sync_contract_addresses.py --chain 2368
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Map: Ignition key suffix → .env key name
ADDRESS_MAP: dict[str, str] = {
    "DealRecord": "DEALRECORD_CONTRACT_ADDR",
    "IdentityRegistry": "IDENTITY_REGISTRY_ADDR",
    "ReputationRegistry": "REPUTATION_REGISTRY_ADDR",
}


def _deployed_addresses_path(chain_id: int) -> Path:
    return (
        PROJECT_ROOT
        / "contracts"
        / "ignition"
        / "deployments"
        / f"chain-{chain_id}"
        / "deployed_addresses.json"
    )


def _load_env_file(path: Path) -> list[str]:
    """Return the ``.env`` as a list of lines (creating it from example if missing)."""
    if path.exists():
        return path.read_text(encoding="utf-8").splitlines()
    example = PROJECT_ROOT / ".env.example"
    if example.exists():
        return example.read_text(encoding="utf-8").splitlines()
    return []


def _upsert_env_line(lines: list[str], key: str, value: str) -> list[str]:
    """Replace ``KEY=...`` in *lines* or append it. Preserves other keys."""
    prefix = f"{key}="
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith(prefix) or stripped.startswith(f"#{key}="):
            lines[i] = f"{key}={value}"
            return lines
    lines.append(f"{key}={value}")
    return lines


def sync(chain_id: int = 2368) -> int:
    deployed_path = _deployed_addresses_path(chain_id)
    if not deployed_path.exists():
        print(
            f"ERROR: {deployed_path} not found.\n"
            f"Run `npm run deploy:kite` in contracts/ first.",
            file=sys.stderr,
        )
        return 1

    addresses_raw: dict[str, str] = json.loads(deployed_path.read_text(encoding="utf-8"))

    resolved: dict[str, str] = {}
    for ignition_key, address in addresses_raw.items():
        suffix = ignition_key.rsplit("#", 1)[-1]
        env_key = ADDRESS_MAP.get(suffix)
        if env_key:
            resolved[env_key] = address

    missing = set(ADDRESS_MAP.values()) - set(resolved.keys())
    if missing:
        print(
            f"WARNING: deployed_addresses.json is missing entries for: {sorted(missing)}",
            file=sys.stderr,
        )

    env_path = PROJECT_ROOT / ".env"
    lines = _load_env_file(env_path)
    for key, value in resolved.items():
        lines = _upsert_env_line(lines, key, value)
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Synced {len(resolved)} contract address(es) to {env_path}:")
    for k, v in resolved.items():
        print(f"  {k}={v}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--chain",
        type=int,
        default=2368,
        help="EVM chain id (default: 2368 for Kite Testnet)",
    )
    args = parser.parse_args()
    sys.exit(sync(chain_id=args.chain))


if __name__ == "__main__":
    main()
