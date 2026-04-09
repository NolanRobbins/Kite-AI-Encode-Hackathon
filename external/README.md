# External references

Offline copies of upstream repos, npm package sources, and doc snapshots for the Kite hackathon. Fetched April 2026.

## Git repositories (shallow `git clone --depth 1`)

| Folder | Source | Notes |
|--------|--------|--------|
| `coinbase-x402` | https://github.com/coinbase/x402 | Open x402 protocol implementation and specs. **Kite’s `gokite-ai/x402` demo repo is not public**; use this as the canonical HTTP 402 + payment flow reference. |
| `kite-counter-dapp` | https://github.com/gokite-ai/kite_counter_dapp | Official counter sample dApp (may include large `node_modules` if committed upstream). |
| `kite-voting-dapp` | https://github.com/gokite-ai/kite_voting_dapp | Official voting sample dApp. |
| `openai-agents-python` | https://github.com/openai/openai-agents-python | Python Agents SDK. |
| `openai-agents-js` | https://github.com/openai/openai-agents-js | TypeScript Agents SDK (MCP integration, tools). |
| `vercel-ai` | https://github.com/vercel/ai | Vercel AI SDK source (`ai` package). On Windows, one example path in this repo may be too long; if `git status` shows missing files, enable `git config core.longpaths true` and re-clone. |
| `mcp-typescript-sdk` | https://github.com/modelcontextprotocol/typescript-sdk | MCP client/server primitives for Agent Passport. |
| `cryptoalgebra-algebra` | https://github.com/cryptoalgebra/Algebra | Algebra Integral protocol (matches DEX contracts listed in `developer-docs`). |

## npm-packages

`npm pack` tarballs plus extracted folders for reading types and bundled JS without installing into an app:

| Package | Version (as fetched) |
|---------|----------------------|
| `gokite-aa-sdk` | 1.0.15 |
| `@modelcontextprotocol/sdk` | 1.29.0 |
| `@openai/agents` | 0.8.3 |
| `ai` (Vercel) | 6.0.154 |
| `@cryptoalgebra/integral-sdk` | 1.1.1 |

Tarballs: `*.tgz`. Extracted: `extracted-*` directories.

## docs-snapshots

Static HTML snapshots (for offline search; live pages may differ):

- `x402-introduction.html` — https://docs.x402.org/introduction
- `goldsky-kite-ai.html` — https://docs.goldsky.com/chains/kite-ai
- `lucidlabs-controller-contracts.html` — Lucid controller contracts reference

## ethereum-eips

- `erc-3009.md` — ERC-3009 transfer with authorization (from ethereum/ercs; EIP file moved out of EIPs repo).
- `eip-712.md` — Typed structured data hashing and signing.
- `eip-4337.md` — Account abstraction (ERC-4337).

## Still remote-only

Use these URLs in the browser when you need the latest UI or private repos:

- Kite x402 facilitators (referenced in docs): `https://github.com/gokite-ai/x402` — **not cloned** (private or removed).
- Pieverse facilitator API: `https://facilitator.pieverse.io/`
- Privy: `https://docs.privy.io/`
- LayerZero: `https://docs.layerzero.network/v2` (also summarized in `developer-docs/kite-chain/10-layerzero-kite-integration/`).
