Kite Passport will help with payment authorization and spending limits, but it will not automatically solve MCP/tool poisoning. Passport can reduce financial blast radius, but descriptor scanning, tool trust, network egress limits, and isolated execution are still our responsibility before live MCP tools.
For the live demo, I’d keep MCP/tool access disabled and say clearly: “NegotiatorGrid is running live negotiation and guardrails; Passport/MCP payment execution is stubbed until Passport access is ready.”
Where NegotiatorGrid Sits
NegotiatorGrid should sit between the agent brain and the payment/tool layer.
LLM / Agent Brain
  |
  | proposes language, strategy summaries
  v
NegotiatorGrid
  |
  | validates offers, caps rounds, checks Nash drift,
  | enforces typed price fields, binds final deal hash
  v
Kite Passport / x402 / MCP Tools
  |
  | approves bounded payment, calls paid service
  v
Seller API / Data Service
So NegotiatorGrid is not just “context.” It is the policy and control layer. The LLM can narrate or advise, but NegotiatorGrid decides what is valid, what gets paid, and what gets logged.
MCP Tool Poisoning Mitigation
For demo now:
Do not give agents filesystem access.
Do not give agents arbitrary MCP tools.
Do not pass secrets, wallet keys, .env, or private reservation prices into prompts.
Treat LLM messages as display-only.
Make typed protocol fields authoritative: price, round, deal_hash, agent_id.
Keep Kite Passport as stubbed until live access is stable.
Before live MCP:
Scan MCP tool descriptors for hidden instructions.
Pin tool metadata hashes and alert on changes.
Allow-list MCP server URLs and payment recipients.
Use ERC-8004 identity/reputation checks before trusting a seller/tool.
Run external tools in isolated containers with no host env and restricted network.
Add response-size limits and secret-pattern scanning before tool output enters LLM context.
Demo LLM Setup
For the hackathon demo, I’d use:
Default: policy_only or slm mode for reliability.
Optional wow mode: API-based LLM narrator for better language.
Avoid: letting an LLM directly decide exact prices or payment execution.
Best setup:
Use API calls to a major provider if you want polished language. Use on-device only if you already have a reliable local model running. On-device is nice for privacy, but often worse for latency, formatting, and setup friction during a live demo.
Kite AI Business Value
This is not “just crypto.” The stronger story is:
Kite enables agentic commerce infrastructure: agents can discover services, negotiate terms, authorize bounded payments, and create auditable records.
NegotiatorGrid adds the missing market layer:
Agents should not blindly pay listed prices.
Sellers should not have to expose one static price.
Buyers need bounded autonomy and payment controls.
Markets need reputation, auditability, and settlement guarantees.
Businesses need explainable agent decisions before trusting autonomous spend.
So our hackathon value prop is strong if we frame it as:
> NegotiatorGrid is the negotiation and trust layer for Kite-powered agent commerce.
Kite Passport handles controlled spending. x402 handles machine payments. MCP handles service discovery/tool access. NegotiatorGrid decides whether the deal is good, fair, bounded, and safe enough to pay.