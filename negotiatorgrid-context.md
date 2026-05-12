# NegotiatorGrid + Kite Agent Passport Context

Kite Agent Passport has now launched as the payment-control layer for agent commerce. The important framing for NegotiatorGrid is:

> NegotiatorGrid is the negotiation and trust layer for Kite-powered agent procurement.

Passport handles user/agent identity, Sessions, Delegations, payment authorization, x402 payment flow, and the user-visible dashboard audit trail. NegotiatorGrid decides whether an autonomous purchase is a good deal before the agent asks Passport to authorize payment.

For the **embedding model** (NegotiatorGrid as a dev-time Python module on procurement agents, asymmetric vs bilateral Nash-oriented play), see the repo root **`CONTEXT.md`**.

## Where NegotiatorGrid Sits

```text
LLM / Agent Brain
  |
  | proposes goals, language, strategy summaries
  v
NegotiatorGrid
  |
  | discovers providers, verifies reputation, negotiates terms,
  | caps rounds, checks Nash drift, binds final deal hash
  v
Kite Agent Passport / MCP / x402
  |
  | checks active Session budget, merchant, asset, TTL,
  | creates Delegation/payment authorization, settles payment
  v
Seller API / Data Service / Asset Provider
```

So NegotiatorGrid is not "just context." It is the procurement policy and control layer. The LLM can narrate or advise, but NegotiatorGrid owns typed fields: price, round, terms hash, seller identity, buyer identity, and settlement amount.

## Product Claim

NegotiatorGrid extends Kite Agent Passport from "authorized agent payments" to "authorized agent procurement." Passport controls whether an agent is allowed to spend. NegotiatorGrid decides whether the deal is good, fair, bounded, and safe enough to pay.

## Demo Stance

For the finished demo:

- Show NegotiatorGrid negotiating a concrete asset or service procurement.
- Show the accepted price becoming a Passport-compatible payment intent.
- Show a "Passport Session Fit" check: negotiated price, remaining budget, merchant allowlist, asset/token, and expiration.
- Use live Passport/MCP/x402 where access is stable.
- Keep mock/stub fallback paths for recording, and label them as Passport-compatible mocks if live infrastructure is unavailable.

## MCP Tool Poisoning Mitigation

Passport reduces financial blast radius, but it does not automatically solve MCP/tool poisoning. Descriptor scanning, tool trust, network egress limits, and isolated execution are still our responsibility before live MCP tools.

For demo now:

- Do not give agents filesystem access.
- Do not give agents arbitrary MCP tools.
- Do not pass secrets, wallet keys, `.env`, or private reservation prices into prompts.
- Treat LLM messages as display-only.
- Make typed protocol fields authoritative: price, round, deal_hash, agent_id.

Before broader live MCP usage:

- Scan MCP tool descriptors for hidden instructions.
- Pin tool metadata hashes and alert on changes.
- Allow-list MCP server URLs and payment recipients.
- Use identity/reputation checks before trusting a seller/tool.
- Run external tools in isolated containers with no host env and restricted network.
- Add response-size limits and secret-pattern scanning before tool output enters LLM context.

## Kite AI Business Value

This is not "just crypto." The stronger story is:

Kite enables agentic commerce infrastructure: agents can discover services, authorize bounded payments, and create auditable records. NegotiatorGrid adds the missing market layer:

- Agents should not blindly pay listed prices.
- Sellers should not have to expose one static price.
- Buyers need bounded autonomy and payment controls.
- Markets need reputation, auditability, and settlement guarantees.
- Businesses need explainable agent decisions before trusting autonomous spend.

Kite Passport handles controlled spending. x402 handles machine payments. MCP handles service discovery/tool access. NegotiatorGrid decides whether the deal is worth paying for.
