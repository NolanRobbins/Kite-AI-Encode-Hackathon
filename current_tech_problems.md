Current as of: April 16, 2026

🟢 What is Fully Supported (Your Best Bets)
If you want a smooth integration without waiting on the Kite team to unblock you, pivot toward these officially supported paths:

Service Provider Integration (The Golden Path): This is the most mature path right now. You can build an API or service that is payable by AI Agents via the x402 protocol.

How it works: Agents pay automatically using Kite Passport. You don't need API keys or human intervention.

Requirement: You need to implement the x402 protocol and use a facilitator like Pieverse for verification and settlement.

Third-Party Skills (Mode 1): You can build your own skill code by integrating the Kite MCP (Model Context Protocol) Tool.

How it works: You paste a JSON configuration into a supported AI client (like Claude Desktop or Cursor). This "Mode 1" is fully available for building and testing.

🔴 What is Blocked or Unsupported (Avoid These)
Don't waste hackathon hours trying to make these work, as the team explicitly stated they aren't supported yet:

Mainnet KITE Tokens: Despite rumors in the chat, do not try to build on Mainnet right now. Stick strictly to Testnet.

Direct Agent Publishing: You cannot use Kite Passport to let third parties publish their own agents with one click yet.

Custom / Unofficial Agents: The only officially supported agents right now are Claude Code and Codex. Building custom agents directly on top of the Anthropic API (or others) is "at your own risk" and may not work with skill installation.

Waiting for Passport Invites: A huge chunk of the chat is people begging for Passport access. If your project strictly relies on a custom invite, you might get bottlenecked. Lean into the open Service Provider (x402) path if possible.

⚠️ Important Community Intel & Bugs
Other builders have uncovered a few quirks you should keep in mind:

The Stablecoin Mismatch: The Testnet faucet and docs give out Test USDT, but the live gasless endpoint currently only returns PYUSD. Be prepared for potential friction here if you are implementing gasless transactions.

Community Workarounds: One builder (Jamal) noted that agentic payments can be tricky with malicious users and built an "optimistic release + challenge period" specification. If you are handling escrow or delayed payments, you might need to build your own safety logic.

🛠️ Key Resources Mentioned
Testnet Faucet: https://faucet.gokite.ai/

Official Docs: https://docs.gokite.ai/