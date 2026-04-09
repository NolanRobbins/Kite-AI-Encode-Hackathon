# Engineering Resources for NegotiatorGrid

**NegotiatorGrid** — An agent-to-agent price negotiation protocol on the Kite AI blockchain using x402 payments.

*Compiled: April 2026 | 7 Sections | 60+ Resources*

---

## Section 1: x402 Protocol Implementation

Resources for implementing the x402 HTTP 402 payment standard — the core payment mechanism for NegotiatorGrid's price settlement layer.

---

### 1.1 x402-foundation/x402

| Field | Details |
|---|---|
| **Name** | x402-foundation/x402 |
| **URL** | https://github.com/x402-foundation/x402 |
| **Type** | Repo |
| **Stars** | 5.9k |
| **Last Updated** | Active (731+ commits; now under Linux Foundation stewardship as of March 2026) |
| **Description** | The canonical open-source monorepo for the x402 payment protocol. Contains TypeScript, Python, Go, Java, and Solidity SDKs. TypeScript is 43.2%, Python 32.9%, Go 22.7%. Includes `@x402/express`, `@x402/fetch`, `@x402/axios`, `@x402/hono`, `@x402/next`, `@x402/paywall`, and `@x402/mcp` packages. Python: `pip install x402`. Go: `go get github.com/x402-foundation/x402/go`. |
| **Relevance** | **Direct** — Core protocol implementation library. NegotiatorGrid uses x402 for every micro-payment during price negotiation rounds. All offer/counter-offer settlement flows pass through x402-compatible middleware. |

---

### 1.2 Coinbase x402 Documentation

| Field | Details |
|---|---|
| **Name** | Coinbase x402 Docs — Welcome & Core Concepts |
| **URL** | https://docs.cdp.coinbase.com/x402/welcome |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | March 2026 |
| **Description** | Official Coinbase Developer Platform documentation for x402. Covers the 7-step payment flow (client request → 402 response → payment signature → facilitator verification → settlement → resource delivery), CAIP-2 network identifiers, multi-network support (EVM + Solana), the Bazaar extensions system for service discovery, and gasless Permit2 approvals. Includes how-it-works guides, client/server role definitions, and network/facilitator reference tables. |
| **Relevance** | **Direct** — Reference for configuring NegotiatorGrid's payment facilitator, understanding `PAYMENT-REQUIRED` / `PAYMENT-SIGNATURE` / `PAYMENT-RESPONSE` headers, and implementing the exact payment flow between negotiating agents. |

---

### 1.3 samthedataman/x402-sdk

| Field | Details |
|---|---|
| **Name** | samthedataman/x402-sdk |
| **URL** | https://github.com/samthedataman/x402-sdk |
| **Type** | Repo |
| **Stars** | Not publicly tracked (community SDK) |
| **Last Updated** | June 2025 |
| **Description** | Python monorepo containing two packages: `fast-x402` (FastAPI middleware — accept payments with 3 lines of code using `x402_middleware`) and `x402-langchain` (LangChain agent with `create_x402_agent`, private key injection, daily spending limits). Supports `pip install fast-x402` and `pip install x402-langchain`. Roadmap includes multi-chain support (Polygon, Arbitrum), subscription payments, and analytics dashboard. |
| **Relevance** | **High** — If NegotiatorGrid's backend agents are Python-based, `fast-x402` provides drop-in FastAPI middleware for serving paid negotiation endpoints. `x402-langchain` enables LangChain-powered agents to autonomously pay for negotiation services. |

---

### 1.4 x402 Python SDK (PyPI)

| Field | Details |
|---|---|
| **Name** | x402 Python Package |
| **URL** | https://pypi.org/project/x402/ |
| **Type** | Docs / Package |
| **Stars** | N/A |
| **Last Updated** | August 2025 |
| **Description** | Core Python implementation of the x402 protocol. Transport-agnostic client, server, and facilitator components with both async (`asyncio`) and sync variants. Supports FastAPI middleware (`x402.fastapi.middleware.require_payment`), Flask middleware, `httpx` client for paying resources, and `requests` client. Provides `PaymentRequiredResponse`, `PaymentPayload`, `FacilitatorClient` types. |
| **Relevance** | **Direct** — The Python SDK is the foundation for any Python-based NegotiatorGrid agent that needs to receive or make x402 payments. |

---

### 1.5 Coinbase x402 MCP Server

| Field | Details |
|---|---|
| **Name** | MCP Server with x402 — Coinbase Docs |
| **URL** | https://docs.cdp.coinbase.com/x402/mcp-server |
| **Type** | Docs / Tutorial |
| **Stars** | N/A |
| **Last Updated** | March 2026 |
| **Description** | Step-by-step guide for running an MCP server that bridges Claude Desktop (or any MCP client) to x402-gated paid APIs. The MCP server uses `@x402/axios` to detect HTTP 402 responses, sign payment payloads automatically, and return paid data to the agent. Includes full TypeScript implementation, environment variable reference, multi-network (EVM + Solana) support, and architecture diagram. The server registers `get-data-from-resource-server` as an MCP tool that Claude calls. |
| **Relevance** | **Direct** — NegotiatorGrid agents connect to the Kite MCP server via this pattern. The x402 MCP bridge is how agents authorize payments during negotiation without manual wallet interaction. |

---

### 1.6 How to Implement a Crypto Paywall with x402 — QuickNode Guide

| Field | Details |
|---|---|
| **Name** | x402 Crypto Paywall Implementation Guide |
| **URL** | https://www.quicknode.com/guides/x402/how-to-use-x402-payment-required |
| **Type** | Tutorial |
| **Stars** | N/A |
| **Last Updated** | February 2026 |
| **Description** | Full hands-on guide building a buyer/seller x402 demo on Base Sepolia. Covers Express `paymentMiddleware` setup, wallet connection, ERC-3009 gasless transfers, protected endpoint configuration, and deployment. Includes working code snippets for both client (buyer) and server (seller) sides. Addresses common questions: facilitators, chain-agnostic support, and dynamic pricing. |
| **Relevance** | **High** — Practical reference for implementing the NegotiatorGrid service endpoints that respond to buyer/seller agent payment flows. |

---

### 1.7 x402 Complete Guide — Simplescraper

| Field | Details |
|---|---|
| **Name** | How to x402: The Complete Guide to the AI Agent Payment Protocol |
| **URL** | https://simplescraper.io/blog/x402-payment-protocol |
| **Type** | Blog |
| **Stars** | N/A |
| **Last Updated** | February 2026 |
| **Description** | Detailed explainer of the full 7-step x402 payment flow with annotated code snippets. Covers: v2 `x402ResourceServer` pattern, `HTTPFacilitatorClient`, dual-auth wrapper (API key + x402), `registerExactEvmScheme`, MCP tool integration with `@x402/mcp`, and CAIP-2 network identifiers. Includes a table of all three x402 headers (`PAYMENT-REQUIRED`, `PAYMENT-SIGNATURE`, `PAYMENT-RESPONSE`). |
| **Relevance** | **High** — Excellent reference for NegotiatorGrid's payment header implementation, especially the dual-auth pattern where agents use x402 and human operators use API keys. |

---

### 1.8 x402 Discovery Catalog — MCP Market

| Field | Details |
|---|---|
| **Name** | x402 Discovery: AI Agent Service Catalog |
| **URL** | https://mcpmarket.com/server/x402-discovery |
| **Type** | Docs / Service |
| **Stars** | N/A |
| **Last Updated** | March 2026 |
| **Description** | An MCP server providing a real-time discovery layer for 250+ x402-payable services. Includes quality signals (uptime, latency, facilitator compatibility), ERC-8004 trust scores, capability-based search, health checks, and endpoint registration. Designed for Claude, Cursor, and Windsurf AI agents. Addresses the discovery gap identified by Coinbase. Also see **X402 Search** (https://mcpmarket.com/server/x402-search) covering 13,000+ x402-enabled HTTP APIs at $0.01 USDC per search. |
| **Relevance** | **High** — NegotiatorGrid agents can use this catalog to discover competing price services and dynamically route to the best x402-compatible providers during negotiations. |

---

### 1.9 x402 Protocol Explained — StablecoinInsider

| Field | Details |
|---|---|
| **Name** | x402 Protocol Explained: The HTTP 402 Payment Standard |
| **URL** | https://stablecoininsider.org/x402-protocol/ |
| **Type** | Blog |
| **Stars** | N/A |
| **Last Updated** | February 2026 |
| **Description** | Comprehensive deep-dive covering x402 v2 wire format, all three headers in detail, the challenge-retry pattern, security considerations for autonomous agents (spending limits, replay prevention, key management), buyer/seller implementation checklists, and facilitator architecture. Includes a complete reference table of on-the-wire objects. |
| **Relevance** | **Medium** — Good conceptual reference for designing NegotiatorGrid's payment security model, especially spending limit enforcement between negotiating agents. |

---

### 1.10 x402 SDKs Hub — xpay.sh

| Field | Details |
|---|---|
| **Name** | x402 SDKs & Libraries Hub |
| **URL** | https://www.xpay.sh/x402-sdks |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | March 2026 |
| **Description** | Community aggregator listing all x402 SDKs: `@coinbase/x402` (TypeScript v2.1.3), official Python SDK (v1.8.2 with AI agent framework integrations), Rust SDK (v0.8.0), Go SDK (v1.4.1), PHP SDK (v3.2.0), and `mogami-x402` community TypeScript with React hooks. Covers features: payment signing, facilitator support, async/await, type safety, batch payments, refund support, webhook handling. |
| **Relevance** | **Medium** — Useful for choosing the right SDK for NegotiatorGrid's multi-language service architecture. |

---

## Section 2: MCP Dynamic Discovery & Tool Use

Resources for building MCP servers/clients with runtime tool discovery — essential for NegotiatorGrid's agent-side capability registration.

---

### 2.1 MCP Specification

| Field | Details |
|---|---|
| **Name** | Model Context Protocol Specification |
| **URL** | https://modelcontextprotocol.io/specification/2025-06-18 |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | June 2025 |
| **Description** | The authoritative MCP specification (2025-06-18 version). Covers JSON-RPC 2.0 message format, capability negotiation, Resources (GET-like context), Tools (POST-like actions), Prompts (templated workflows), Sampling, Roots, and Elicitation. Key for dynamic tool discovery: servers can notify clients via `notifications/tools/list_changed`; tools can be added/removed at runtime. Stateful connections with client/server lifecycle management. |
| **Relevance** | **Direct** — NegotiatorGrid agents register as MCP servers, advertising `negotiate_price`, `submit_offer`, `accept_offer` tools. This spec defines the exact wire protocol. |

---

### 2.2 modelcontextprotocol/python-sdk

| Field | Details |
|---|---|
| **Name** | MCP Python SDK |
| **URL** | https://github.com/modelcontextprotocol/python-sdk |
| **Type** | Repo |
| **Stars** | Actively maintained (official Anthropic SDK) |
| **Last Updated** | Active (frequent releases) |
| **Description** | Official Python SDK implementing the full MCP specification. Supports building MCP servers (expose resources, prompts, tools) and MCP clients (connect to any MCP server). Standard transports: stdio, SSE, and Streamable HTTP. Uses `FastMCP` for rapid server development. `list_tools()` returns tool schemas with auto-inferred Pydantic parameter types. Install: `pip install mcp`. |
| **Relevance** | **Direct** — Python NegotiatorGrid agents use this SDK to register as MCP servers, expose negotiation tools, and connect to the Kite MCP infrastructure at `mcp.prod.gokite.ai`. |

---

### 2.3 MCP Python SDK Docs

| Field | Details |
|---|---|
| **Name** | MCP Python SDK Documentation |
| **URL** | https://modelcontextprotocol.github.io/python-sdk/ |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | Active |
| **Description** | Full API documentation for the MCP Python SDK. Covers server/client architecture, `FastMCP` quick-start, Streamable HTTP transport, tool schema auto-generation from type hints, resource management, and the MCP Inspector for debugging. Includes Streamable HTTP example (`mcp.run(transport="streamable-http")`). |
| **Relevance** | **Direct** — Reference for building NegotiatorGrid's Python-based MCP server components. |

---

### 2.4 Docker Dynamic MCP

| Field | Details |
|---|---|
| **Name** | Dynamic MCP — Docker Docs |
| **URL** | https://docs.docker.com/ai/mcp-catalog-and-toolkit/dynamic-mcp/ |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | March 2026 |
| **Description** | Official Docker documentation for the Dynamic MCP pattern. The Docker MCP Toolkit gateway provides six primordial tools: `mcp-find` (search catalog by name/description), `mcp-add` (add server to session), `mcp-config-set` (configure server settings), `mcp-remove` (remove from session), `mcp-exec` (execute tool by name), `code-mode` (compose multiple MCP tools into JavaScript functions). Available in Docker Desktop 4.50+. Catalog includes 270+ curated servers. |
| **Relevance** | **High** — NegotiatorGrid agents can use this pattern to dynamically discover and add negotiation service MCP servers at runtime, without pre-configuration. |

---

### 2.5 Docker Dynamic MCPs Blog Post

| Field | Details |
|---|---|
| **Name** | Dynamic MCPs with Docker: Stop Hardcoding Your Agents' World |
| **URL** | https://www.docker.com/blog/dynamic-mcps-stop-hardcoding-your-agents-world/ |
| **Type** | Blog |
| **Stars** | N/A |
| **Last Updated** | November 2025 |
| **Description** | In-depth blog explaining the motivation and architecture behind Docker's Dynamic MCP approach. Covers how `mcp-find` and `mcp-add` enable agents to self-configure tool access during runtime. Includes live demo examples of adding DuckDuckGo MCP server on-the-fly, `docker mcp tools ls` output (89 pre-loaded tools), and real-world workflows for content creation pipelines and conference demos. |
| **Relevance** | **High** — Architectural pattern for NegotiatorGrid's dynamic service discovery layer. Agents can find and connect to price oracle MCPs on demand. |

---

### 2.6 Dynamic Tool Registry (LinkedIn/Walid Negm)

| Field | Details |
|---|---|
| **Name** | Dynamic Tool Registry with Anthropic's MCP |
| **URL** | https://www.linkedin.com/pulse/dynamic-tool-registry-anthropics-mcp-foundation-multi-step-walid-negm-54lye |
| **Type** | Blog |
| **Stars** | N/A |
| **Last Updated** | September 2025 |
| **Description** | Technical article implementing an MCP server that registers Python functions dynamically using a JSON manifest. Full code for `ToolRegistry` class (JSON manifest loading, dynamic `importlib` imports, Pydantic validation), `MCPClient` (asyncio, `list_tools()` schema discovery, `call_tool()`), and `FastMCP` server integration. Demonstrates `list_tools()` returning parameter schemas automatically inferred from type hints. |
| **Relevance** | **High** — Reference implementation for NegotiatorGrid's dynamic negotiation strategy registry, where different pricing algorithms can be hot-loaded as MCP tools. |

---

### 2.7 Dynamic FastMCP — Ragie

| Field | Details |
|---|---|
| **Name** | Making MCP Tool Use Feel Natural with Dynamic FastMCP |
| **URL** | https://www.ragie.ai/blog/making-mcp-tool-use-feel-natural-with-context-aware-tools |
| **Type** | Blog |
| **Stars** | N/A |
| **Last Updated** | August 2025 |
| **Description** | Open-source library `dynamic_fastmcp` extending official `FastMCP` with per-tenant, context-aware tool descriptions resolved at runtime. Introduces `DynamicTool` class with `handle_description(ctx)` and `handle_call(ctx)` methods. Tool descriptions are generated just-in-time based on request context (tenant data, partition info). No protocol changes — clients still receive standard MCP `Tool` payloads. |
| **Relevance** | **Medium** — Useful if NegotiatorGrid needs per-agent dynamic tool descriptions, e.g., a seller agent advertising different price ranges to different buyer agents. |

---

### 2.8 Official MCP Registry

| Field | Details |
|---|---|
| **Name** | The MCP Registry |
| **URL** | https://modelcontextprotocol.io/registry/about |
| **Type** | Docs / Service |
| **Stars** | N/A |
| **Last Updated** | March 2026 |
| **Description** | Official centralized metadata repository for publicly accessible MCP servers. REST API at `registry.modelcontextprotocol.io`. Backed by Anthropic, GitHub, PulseMCP, and Microsoft. Uses `server.json` format with reverse DNS namespacing (`io.github.user/server-name`). Supports npm, PyPI, Docker Hub, and GitHub Releases package types. Provides namespace authentication via GitHub account or domain verification. |
| **Relevance** | **Medium** — NegotiatorGrid can publish its MCP negotiation server to this registry, making it discoverable to any MCP-compatible client or agent framework. |

---

### 2.9 MCP Server Registry Discussion

| Field | Details |
|---|---|
| **Name** | MCP Server Registry — GitHub Discussion #159 |
| **URL** | https://github.com/orgs/modelcontextprotocol/discussions/159 |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | March 2025 |
| **Description** | Community design document for the MCP registry architecture. Covers security scanning for CVEs and MCP-specific vulnerabilities (prompt injection, authorization spec adherence), SSE-based real-time registry updates, Service Hub architecture with health checks, and REST APIs for registration/unregistration. |
| **Relevance** | **Low-Medium** — Architectural background for understanding MCP registry design, useful if NegotiatorGrid builds a private negotiation service registry. |

---

### 2.10 MCP Server Development Guide

| Field | Details |
|---|---|
| **Name** | MCP Server Development Guide |
| **URL** | https://github.com/cyanheads/model-context-protocol-resources/blob/main/guides/mcp-server-development-guide.md |
| **Type** | Tutorial |
| **Stars** | N/A |
| **Last Updated** | November 2024 |
| **Description** | Comprehensive guide covering MCP server architecture, transport layers (stdio vs. Streamable HTTP comparison table), tool/resource/prompt implementation with Zod schema validation, security (OAuth 2.0, HTTPS, CORS), dynamic server capabilities, and performance optimization. Includes working TypeScript examples for all MCP primitives. |
| **Relevance** | **High** — The go-to guide for building NegotiatorGrid's MCP server components that expose negotiation tools to buyer/seller agents. |

---

## Section 3: A2A (Agent-to-Agent) Protocol

Resources for Google's A2A protocol — the inter-agent communication layer that NegotiatorGrid uses for structured negotiation exchanges.

---

### 3.1 google/A2A (a2aproject/A2A)

| Field | Details |
|---|---|
| **Name** | Agent2Agent (A2A) Protocol |
| **URL** | https://github.com/google-a2a/A2A |
| **Type** | Repo |
| **Stars** | 23.1k |
| **Last Updated** | Active (552+ commits) |
| **Description** | Google's open protocol for agent-to-agent communication. Standardizes JSON-RPC 2.0 over HTTP(S), agent discovery via AgentCards at `/.well-known/agent.json`, and flexible interaction modes: synchronous request/response, SSE streaming, and async push notifications. Supports text, files, and structured JSON data exchange. Task lifecycle management with states: SUBMITTED, WORKING, INPUT_REQUIRED, COMPLETED, FAILED, CANCELED. Enterprise-ready with authentication and observability. |
| **Relevance** | **Direct** — A2A is the inter-agent protocol for NegotiatorGrid. Buyer and seller agents communicate via A2A tasks. Each negotiation round is a structured A2A message exchange. |

---

### 3.2 google-agentic-commerce/a2a-x402

| Field | Details |
|---|---|
| **Name** | A2A x402 Extension |
| **URL** | https://github.com/google-agentic-commerce/a2a-x402 |
| **Type** | Repo |
| **Stars** | 488 |
| **Last Updated** | September 2025 (v0.1.0) |
| **Description** | Bridges the A2A protocol with x402 cryptocurrency payments. Three-step payment flow within A2A: `payment-required` message (merchant requests payment), `payment-submitted` message (client signs and sends), `payment-completed` message (merchant settles and delivers). Python implementation in `python/x402_a2a/`. Functional core + imperative shell architecture with Executors (middleware automating payment flow). Apache-2.0 license. Install via git (`pip install` from subdirectory). |
| **Relevance** | **Critical** — This is the exact bridge NegotiatorGrid needs: A2A negotiation rounds that trigger x402 payments on the Kite blockchain. The executor middleware automates the payment handshake within the negotiation loop. |

---

### 3.3 AgentCard Specification

| Field | Details |
|---|---|
| **Name** | AgentCard — A2A Protocol Community Docs |
| **URL** | https://agent2agent.info/docs/concepts/agentcard/ |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | Active |
| **Description** | Complete AgentCard specification. Fields: `name`, `description`, `url`, `provider`, `version`, `documentationUrl`, `capabilities` (streaming, pushNotifications, stateTransitionHistory), `authentication` (schemes, credentials), `defaultInputModes`, `defaultOutputModes`, `skills` (id, name, description, tags, examples, inputModes, outputModes). AgentCard served at `/.well-known/agent.json`. Python SDK provides `AgentCard`, `AgentCapabilities`, `AgentSkill` classes. |
| **Relevance** | **Direct** — Every NegotiatorGrid agent (buyer/seller/mediator) publishes an AgentCard advertising its negotiation capabilities, accepted payment methods, and skill set. |

---

### 3.4 Google Codelabs: Getting Started with A2A

| Field | Details |
|---|---|
| **Name** | Getting Started with Agent2Agent (A2A) Protocol — Google Codelabs |
| **URL** | https://codelabs.developers.google.com/intro-a2a-purchasing-concierge |
| **Type** | Tutorial |
| **Stars** | N/A |
| **Last Updated** | March 2026 |
| **Description** | Hands-on A2A tutorial deploying a Purchasing Concierge system: Burger Agent (CrewAI), Pizza Agent (LangGraph), and Concierge (ADK) as A2A client. Demonstrates `A2ACardResolver`, `RemoteAgentConnections`, `AgentCapabilities` with streaming, and multi-framework agent communication. Full Python code for `before_agent_callback` that discovers agent cards and builds connection clients. Shows MCP + A2A complementarity. |
| **Relevance** | **High** — The closest publicly available tutorial to NegotiatorGrid's architecture: multiple agents negotiating via A2A. Directly applicable patterns for buyer/seller/mediator roles. |

---

### 3.5 A2A Protocol Tutorial — LinkedIn (Bhuiyan)

| Field | Details |
|---|---|
| **Name** | Google Agent-to-Agent (A2A) Protocol Explained — with Working Python Examples |
| **URL** | https://www.linkedin.com/pulse/google-agent-to-agent-a2a-protocol-explained-real-working-bhuiyan-mgzne |
| **Type** | Blog / Tutorial |
| **Stars** | N/A |
| **Last Updated** | April 2025 |
| **Description** | Step-by-step Python tutorial building a Travel Planner AI using A2A. Implements WeatherAgent and BraveSearchAgent with `python-a2a` library (`@agent`, `@skill` decorators, `run_server`, `TaskStatus`). Includes LangChain/Ollama integration via `to_a2a_server()`. Covers A2A vs MCP relationship, task states, message roles, and `AgentNetwork` for multi-agent coordination. Full code available at GitHub repo. |
| **Relevance** | **High** — Practical Python patterns directly applicable to NegotiatorGrid's buyer/seller agent implementation using `python-a2a`. |

---

### 3.6 A2A Tutorial with MCP Integration — YouTube

| Field | Details |
|---|---|
| **Name** | Google A2A Protocol Explained: Tutorial, Demo & MCP Integration |
| **URL** | https://www.youtube.com/watch?v=GUozMSpnmcc |
| **Type** | Tutorial (Video) |
| **Stars** | N/A |
| **Last Updated** | April 2025 |
| **Description** | YouTube tutorial covering A2A protocol fundamentals, live GitHub walkthrough, Python implementation demo, and how A2A and MCP work together (MCP = LLM + tools/data; A2A = agent-to-agent communication). Shows agent cards, multi-agent workflow chaining, and framework interoperability. |
| **Relevance** | **Medium** — Good onboarding video for developers new to A2A who will work on NegotiatorGrid. |

---

### 3.7 Building Agentic Systems with A2A — Searce Blog

| Field | Details |
|---|---|
| **Name** | Building an Agentic System with Google's A2A Protocol |
| **URL** | https://blog.searce.com/building-an-agentic-system-with-googles-a2a-protocol-jira-and-github-integration-aedde4ca71cc |
| **Type** | Blog |
| **Stars** | N/A |
| **Last Updated** | April 2025 |
| **Description** | Tutorial building an agentic system with A2A integrating JIRA and GitHub. Demonstrates real-world A2A deployment with streaming capabilities, authentication, and multi-service orchestration patterns. |
| **Relevance** | **Medium** — Shows enterprise-grade A2A deployment patterns applicable to NegotiatorGrid's production architecture. |

---

## Section 4: Negotiation Engines & Frameworks

Core negotiation algorithm implementations — the strategy layer that determines offer/counter-offer logic in NegotiatorGrid.

---

### 4.1 ammonhaggerty/ANEX

| Field | Details |
|---|---|
| **Name** | Agent Negotiation & Exchange Protocol (ANEX) |
| **URL** | https://github.com/ammonhaggerty/ANEX |
| **Type** | Repo |
| **Stars** | Not tracked (protocol spec/draft) |
| **Last Updated** | November 2024 |
| **Description** | Draft specification for a universal AI agent handshake and data exchange protocol using FIPA ACL standards. Defines a 6-phase protocol: self-identification → engagement initiation → response handling → term negotiation (FIPA Contract-Net) → data exchange → session termination. Uses JSON ACL messages with performatives (CFP, PROPOSE, ACCEPT-PROPOSAL, REFUSE). Transport: secure WebSockets (`wss://`). Implementations in Node.js (SPADE) and Python. Includes compact compliance indicator `[PA*]`. |
| **Relevance** | **High** — ANEX provides the handshake and negotiation term structure that NegotiatorGrid can implement for the pre-payment negotiation phase. The FIPA-Contract-Net Protocol maps directly to NegotiatorGrid's call-for-proposal → offer → counter-offer → acceptance flow. |

---

### 4.2 aniltrue/NegoLog

| Field | Details |
|---|---|
| **Name** | NegoLog: Automated Bilateral Negotiation Framework |
| **URL** | https://github.com/aniltrue/NegoLog |
| **Type** | Repo |
| **Stars** | 7 |
| **Last Updated** | March 2025 (v1.0 released) |
| **Description** | IJCAI 2024 paper implementation. Python 3.10 bilateral negotiation framework with: `nenv` (Negotiation Environment) library, `AbstractAgent` class (bidding strategy + acceptance strategy + opponent model), `AbstractOpponentModel` (preference estimation), `AbstractLogger` (analytics callbacks), Domain Generator Tool (automated scenario creation with configurable utility distributions), Web-based UI for tournament management. Supports multi-agent tournaments, session/round/tournament-level logging, and statistical graph generation. GPL-3.0 license. |
| **Relevance** | **High** — NegoLog provides production-ready bilateral negotiation infrastructure. NegotiatorGrid can use the `AbstractAgent` framework to implement buyer/seller pricing strategies, with `AbstractOpponentModel` estimating counterpart reservation prices. |

---

### 4.3 hari7261/Negotiation-MultiAgent

| Field | Details |
|---|---|
| **Name** | AI-Powered Multi-Agent Negotiation Platform |
| **URL** | https://github.com/hari7261/Negotiation-MultiAgent |
| **Type** | Repo |
| **Stars** | Small (educational) |
| **Last Updated** | July 2025 |
| **Description** | Python + Flask + Google Gemini AI platform simulating price negotiations between Buyer, Seller, and Mediator agents. Three-phase process: initialization (item details, price ranges) → negotiation rounds (LLM-generated offers/counter-offers) → agreement detection (automatic price validation against constraints). SQLite for negotiation history. Includes setup scripts for Windows/Unix. Frontend in vanilla JS with custom animations. |
| **Relevance** | **High** — The most architecturally similar existing project to NegotiatorGrid. Three-role model (buyer/seller/mediator), LLM-generated negotiation messages, and price range constraints are all directly applicable patterns. |

---

### 4.4 Sina-Baharlou/Contract-Net-Protocol

| Field | Details |
|---|---|
| **Name** | Contract-Net-Protocol Implementation |
| **URL** | https://github.com/Sina-Baharlou/Contract-Net-Protocol |
| **Type** | Repo |
| **Stars** | Small |
| **Last Updated** | 2019 (C++) |
| **Description** | C++ OpenCV implementation of the FIPA Contract-Net Protocol in an attacker/defender scenario. The CNP algorithm enables defender agents to collectively respond to a CFP and award contracts based on bids. While not Python, demonstrates the protocol's state machine clearly. |
| **Relevance** | **Low-Medium** — Reference for understanding CNP state machine structure, even though NegotiatorGrid will use Python. |

---

### 4.5 SPADE: Smart Python Agent Development Environment

| Field | Details |
|---|---|
| **Name** | SPADE |
| **URL** | https://github.com/javipalanca/spade |
| **Type** | Repo |
| **Stars** | 600+ |
| **Last Updated** | Active |
| **Description** | Python multi-agent systems framework implementing FIPA standards. Agents are Python asyncio objects with XMPP messaging. Supports cyclic, periodic, one-shot, and FSM behaviors. Used as the Python implementation foundation in the ANEX protocol spec. Provides `spade.agent.Agent`, `spade.behaviour.CyclicBehaviour`, and `spade.message.Message` primitives. |
| **Relevance** | **Medium** — SPADE's FIPA-compliant message passing can provide the backbone for NegotiatorGrid's agent communication layer if a standards-compliant ACL approach is preferred. |

---

### 4.6 Agent Communication & Contract Net Protocol — Notes.muthu.co

| Field | Details |
|---|---|
| **Name** | Agent Communication Protocols and Message-Passing Patterns |
| **URL** | https://notes.muthu.co/2025/11/agent-communication-protocols-and-message-passing-patterns-for-coordination/ |
| **Type** | Blog / Tutorial |
| **Stars** | N/A |
| **Last Updated** | November 2025 |
| **Description** | Practical Python implementation of FIPA ACL message-passing with a `Message`, `Agent`, `InfoAgent`, `ExecutorAgent`, and `MessageBus` implementation. Includes a Contract-Net Protocol challenge: `ManagerAgent` (sends CFP, evaluates bids, awards contract) and `WorkerAgent` (handles CFP, generates bid). Full code with `SpeechAct` enum (INFORM, REQUEST, PROPOSE, ACCEPT-PROPOSAL, REFUSE, CFP). |
| **Relevance** | **High** — Ready-to-run CNP Python implementation that NegotiatorGrid can adapt directly for its price-negotiation round mechanics. |

---

### 4.7 Introduction to Automated Negotiation — arXiv

| Field | Details |
|---|---|
| **Name** | Introduction to Automated Negotiation (Book) |
| **URL** | https://arxiv.org/pdf/2511.08659 |
| **Type** | Academic |
| **Stars** | N/A |
| **Last Updated** | January 2026 |
| **Description** | Free textbook targeting CS students new to automated negotiation. Covers alternating offers protocol (AOP), bilateral multi-issue negotiation, utility functions, time pressure models, concession strategies, and opponent modeling. Published January 2026. |
| **Relevance** | **Medium** — Theoretical foundation for NegotiatorGrid's price convergence algorithm design and bidding strategy implementation. |

---

## Section 5: Kite AI Specific Resources

Resources specific to the Kite AI blockchain — NegotiatorGrid's target deployment environment.

---

### 5.1 Kite AI Documentation Hub

| Field | Details |
|---|---|
| **Name** | Kite AI Docs |
| **URL** | https://docs.gokite.ai |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | February 2026 |
| **Description** | Main documentation portal for Kite AI, "The First AI Payment Blockchain." Covers: Cryptographic Identity (3-tier identity system), Native Stablecoin Payments (USDC, instant settlement), x402 compatibility (A2A intents + verifiable message passing), Verifiable Delegation, and Agent-First Design. Architecture: base EVM-compatible L1 (optimized for stablecoin payments + state channels) → Platform Layer (agent-ready APIs) → Programmable Trust Layer (Kite Passport, Agent SLAs) → Ecosystem Layer (Application + Agents marketplaces). |
| **Relevance** | **Critical** — NegotiatorGrid deploys on Kite AI. This is the primary reference for all chain-specific configurations, identity setup, and payment flow integration. |

---

### 5.2 Kite Agent Passport — Introduction

| Field | Details |
|---|---|
| **Name** | Kite Agent Passport Introduction |
| **URL** | https://docs.gokite.ai/kite-agent-passport/kite-agent-passport |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | February 2026 |
| **Description** | Architecture overview of Kite's three-layer payment system: Passport Layer (identity, auth, delegation — User/Agent IDs, Sessions with budgets, Delegations with signed payment intents), Payment Layer (on-chain Kite L1, x402 facilitator integration, service redemption APIs), MCP Tool Layer (Kite Payment tools, session/delegation handling, user prompts). Three developer modes: Mode 1 (self-serve MCP), Mode 2 (API-managed), Mode 3 (fully managed). MCP server URL: `https://neo.dev.gokite.ai/v1/mcp`. |
| **Relevance** | **Critical** — Defines NegotiatorGrid's payment authorization architecture. Every negotiation session maps to a Kite Passport session with budget constraints. |

---

### 5.3 Kite Developer Guide

| Field | Details |
|---|---|
| **Name** | Kite Agent Passport Developer Guide |
| **URL** | https://docs.gokite.ai/kite-agent-passport/developer-guide |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | February 2026 |
| **Description** | Developer integration guide covering the full payment flow: Mode 1 MCP integration (user self-serve portal), Mode 3 managed integration (programmatic agent/session creation via API + on-chain SDK registration). Code examples for `get_payer_addr`, `approve_payment` MCP tool calls. OAuth authentication flow. Kite Portal at `https://x402-portal-eight.vercel.app/`. Testnet faucet at `https://faucet.gokite.ai/`. |
| **Relevance** | **Critical** — Step-by-step integration reference for connecting NegotiatorGrid to Kite's payment infrastructure. |

---

### 5.4 Kite Service Provider Guide

| Field | Details |
|---|---|
| **Name** | Kite Agent Passport Service Provider Guide |
| **URL** | https://docs.gokite.ai/kite-agent-passport/service-provider-guide |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | February 2026 |
| **Description** | Guide for services (like NegotiatorGrid price endpoints) accepting payments from AI agents. 6-step flow: service returns 402 → agent gets signed authorization via Kite MCP → service receives `X-Payment` header → service calls facilitator `/v2/settle` → facilitator executes on-chain transfer → service delivers response. Recommends Pieverse Facilitator (`https://facilitator.pieverse.io`) as primary. Demo x402 weather API at `https://x402.dev.gokite.ai/api/weather`. Reference implementation at `https://github.com/gokite-ai/x402`. |
| **Relevance** | **Critical** — NegotiatorGrid's price service endpoints implement this exact pattern. Both the buyer and seller agent services follow this flow. |

---

### 5.5 Kite gokite-ai/x402 Demo

| Field | Details |
|---|---|
| **Name** | gokite-ai/x402 Demo Repository |
| **URL** | https://github.com/gokite-ai/x402 |
| **Type** | Repo |
| **Stars** | N/A |
| **Last Updated** | Active |
| **Description** | Kite AI's reference implementation of x402 facilitators and demo services. Contains demo facilitators showing how to enable x402 facilitation with Kite, example weather API service at `https://x402.dev.gokite.ai/api/weather`, and integration patterns for Kite L1 testnet. Service providers should use this as their implementation reference. |
| **Relevance** | **Direct** — The reference implementation for all x402 integrations on the Kite network. NegotiatorGrid should fork or reference this for its facilitator setup. |

---

### 5.6 Kite AA Wallet SDK

| Field | Details |
|---|---|
| **Name** | GoKite Account Abstraction (AA) SDK |
| **URL** | https://docs.gokite.ai/kite-chain/account-abstraction-sdk |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | October 2025 |
| **Description** | `gokite-aa-sdk` npm package implementing ERC-4337 Account Abstraction on the Kite AI L1. Features: create/manage AA wallets, deploy upgradeable agent vaults (UUPS proxy pattern), set spending rules (time windows, budgets, target providers), send gasless transactions via bundler, integrate Privy/Particle auth for user signing. Key addresses on Kite Testnet: Settlement Token `0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63`, Settlement Contract `0x8d9FaD78d5Ce247aA01C140798B9558fd64a63E3`. |
| **Relevance** | **Critical** — NegotiatorGrid agents use AA wallets to enforce spending constraints during negotiations. The vault's `configureSpendingRules` enforces per-session budget limits, preventing runaway negotiation costs. |

---

### 5.7 Kite Chain Getting Started

| Field | Details |
|---|---|
| **Name** | Kite Chain Getting Started |
| **URL** | https://docs.gokite.ai/kite-chain/1-getting-started |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | October 2025 |
| **Description** | Quick start for Kite Chain development: network information (chain IDs, RPC endpoints), block explorer, wallet setup, DeFi tools. Entry point for connecting wagmi/viem to Kite's custom EVM chain. |
| **Relevance** | **High** — Required for configuring NegotiatorGrid's frontend wallet connection to Kite L1. |

---

### 5.8 ERC-8004 Overview — eco.com

| Field | Details |
|---|---|
| **Name** | What is ERC-8004? The Ethereum Standard Enabling Trustless AI Agents |
| **URL** | https://eco.com/support/en/articles/13221214-what-is-erc-8004-the-ethereum-standard-enabling-trustless-ai-agents |
| **Type** | Blog / Docs |
| **Stars** | N/A |
| **Last Updated** | March 2026 |
| **Description** | Comprehensive ERC-8004 explainer. Three registries: Identity Registry (ERC-721 NFT → agent registration file at `/.well-known/agent-card.json` with name, description, MCP/A2A endpoints, payment address), Reputation Registry (0-100 score attestations with KECCAK-256 hash, tags, off-chain URI), Validation Registry (flexible verification hooks). 260+ agents registered on Ethereum/Base/Arbitrum as of February 2026. Extends A2A protocol with blockchain-based trust. Went live on Ethereum mainnet January 29, 2026. |
| **Relevance** | **High** — NegotiatorGrid agents register under ERC-8004 to establish on-chain identity and build reputation scores from completed negotiations, enabling trust without pre-existing relationships. |

---

### 5.9 ERC-8004 Developer Guide — QuickNode

| Field | Details |
|---|---|
| **Name** | ERC-8004: A Developer's Guide to Trustless AI Agent Identity |
| **URL** | https://blog.quicknode.com/erc-8004-a-developers-guide-to-trustless-ai-agent-identity/ |
| **Type** | Blog / Tutorial |
| **Stars** | N/A |
| **Last Updated** | April 2026 |
| **Description** | Technical implementation guide for ERC-8004. Covers 5-step workflow: Register (deploy to Identity Registry) → Discover (query registry by capability/reputation) → Connect (A2A/MCP handshake) → Transact → Pay and Record (x402 payment → Reputation Registry attestation). Explains ENS + DID + ERC-8004 composability. Authors: Marco De Rossi (MetaMask), Davide Crapis (Ethereum Foundation), Jordan Ellis (Google), Erik Reppel (Coinbase). |
| **Relevance** | **High** — Implementation reference for registering NegotiatorGrid agents with on-chain identity and recording negotiation outcomes as reputation attestations. |

---

### 5.10 Kite AI x402 Implementation Video

| Field | Details |
|---|---|
| **Name** | Implementing x402 Payment Protocol with KiteAI's CTO |
| **URL** | https://www.youtube.com/watch?v=fylv-WsWPfQ |
| **Type** | Tutorial (Video) |
| **Stars** | N/A |
| **Last Updated** | July 2025 |
| **Description** | YouTube demo by Kite AI's CTO showing x402 integration with Kite network wallet and transactions. Demonstrates example agent server providing services, local agent making payments, result export and discovery, and payment flow for results requiring payment. |
| **Relevance** | **High** — Direct demonstration of the exact deployment pattern NegotiatorGrid targets on Kite. |

---

## Section 6: Agent Frameworks with Payment Capabilities

Frameworks for orchestrating NegotiatorGrid's agent logic with integrated wallet/payment support.

---

### 6.1 OpenAI Agents SDK (openai-agents-python)

| Field | Details |
|---|---|
| **Name** | OpenAI Agents SDK |
| **URL** | https://github.com/openai/openai-agents-python |
| **Type** | Repo |
| **Stars** | 20.7k |
| **Last Updated** | April 2026 (v0.13.5) |
| **Description** | Lightweight Python framework for multi-agent workflows. Core primitives: Agents (LLMs + instructions + tools), Handoffs (agent-to-agent delegation), Guardrails (input/output validation), Function Tools (auto-schema from Python functions with Pydantic validation), Sessions (persistent memory), built-in MCP server tool calling. Tracing dashboard integration. Supports 100+ LLMs via Chat Completions API. Install: `pip install openai-agents`. Production-ready upgrade of Swarm. |
| **Relevance** | **High** — NegotiatorGrid buyer/seller agents can be built as OpenAI Agents SDK agents with handoffs between negotiation roles and MCP tool calling for x402 payments. |

---

### 6.2 OpenAI Agents SDK Docs

| Field | Details |
|---|---|
| **Name** | OpenAI Agents SDK Documentation |
| **URL** | https://openai.github.io/openai-agents-python/ |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | Active |
| **Description** | Official documentation site. Covers agent loop (tool invocation → LLM → continue until task complete), Python-first design, MCP server tool calling, Guardrails (parallel input validation), Sessions (persistent working context), Human-in-the-loop mechanisms, Realtime Agents (voice), and built-in tracing for debugging. |
| **Relevance** | **High** — Reference for integrating MCP tool calling (Kite payment tools) into NegotiatorGrid's OpenAI-based agents. |

---

### 6.3 Coinbase AgentKit

| Field | Details |
|---|---|
| **Name** | Coinbase AgentKit |
| **URL** | https://github.com/coinbase/agentkit |
| **Type** | Repo |
| **Stars** | 1.2k |
| **Last Updated** | Active (517+ commits) |
| **Description** | TypeScript (53.9%) + Python (43.7%) toolkit giving AI agents onchain capabilities. Framework-agnostic (LangChain, OpenAI Agents, etc.) and wallet-agnostic (CDP Server Wallet, Privy, ZeroDev, Viem, smart wallets). Key action providers: `cdp_api_action_provider`, `erc20_action_provider`, `wallet_action_provider`, `weth_action_provider`. x402 payments built-in (via Agentic Wallet). Multi-chain: EVM (Base, mainnet, Sepolia) + Solana. Python: `from coinbase_agentkit import AgentKit`. |
| **Relevance** | **High** — AgentKit provides NegotiatorGrid agents with wallet management, ERC-20 transfers, and x402 payment capabilities across multiple chains. |

---

### 6.4 Coinbase AgentKit Documentation

| Field | Details |
|---|---|
| **Name** | Welcome to AgentKit — Coinbase CDP Docs |
| **URL** | https://docs.cdp.coinbase.com/agent-kit/welcome |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | March 2026 |
| **Description** | Official AgentKit documentation. Covers wallet configuration (CDP Server Wallet, Smart Wallet, ZeroDev, Privy), action providers reference, LangGraph integration (`get_langchain_tools`), Python and TypeScript usage, and multi-chain support. Agentic Wallet comparison table vs AgentKit. |
| **Relevance** | **High** — Integration reference for connecting NegotiatorGrid agents to CDP wallets for x402 payment execution. |

---

### 6.5 Coinbase Agentic Wallet

| Field | Details |
|---|---|
| **Name** | Agentic Wallet — Coinbase CDP Docs |
| **URL** | https://docs.cdp.coinbase.com/agentic-wallet/welcome |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | March 2026 |
| **Description** | Standalone agent wallet (no SDK import required). Access via CLI (`npx awal send`) or MCP tools. Features: self-custody wallet with configurable spending limits, gasless token swaps on Base, x402 machine-to-machine payments, KYT screening, OFAC compliance. Skills: authenticate, fund, send, trade, search-for-service, pay-for-service, monetize-service. Built on CDP infrastructure. 50M+ x402 transactions processed. |
| **Relevance** | **High** — Alternative to AgentKit for NegotiatorGrid agents that don't need full SDK integration but require x402 payment capability via MCP. |

---

### 6.6 LangGraph

| Field | Details |
|---|---|
| **Name** | LangGraph |
| **URL** | https://github.com/langchain-ai/langgraph |
| **Type** | Repo |
| **Stars** | 28.7k |
| **Last Updated** | April 2026 (langgraph-cli v0.4.21) |
| **Description** | Build resilient language agents as graphs (Python + TypeScript). State management for multi-step agentic workflows, multi-actor support, branching/looping control flow, human-in-the-loop interrupts, and persistent checkpointing. Native LangChain tools integration. `create_react_agent` works directly with AgentKit tools. Supports complex negotiation state machines (offer → counter-offer → accept/reject → settlement). |
| **Relevance** | **High** — LangGraph's state machine model maps directly to NegotiatorGrid's negotiation round lifecycle. Each negotiation state (PROPOSED, COUNTERED, ACCEPTED, SETTLING) is a graph node. |

---

### 6.7 LangGraph x402 Payment Integration

| Field | Details |
|---|---|
| **Name** | LangGraph Integration — PayStabl AgentPay Docs |
| **URL** | https://agentpay-docs.replit.app/integrations/langgraph |
| **Type** | Docs / Tutorial |
| **Stars** | N/A |
| **Last Updated** | Active |
| **Description** | Detailed guide integrating x402 payments into LangGraph workflows. Introduces `PaymentNode` (handles x402 API payments within workflow steps) and `AgentPaymentNode` (facilitates payments between agents with dynamic/fixed payment logic and quality multipliers). Full code for building payment workflow graphs (`StateGraph`, `check_balance`, `send_payment`, `handle_result` nodes). |
| **Relevance** | **Direct** — The `AgentPaymentNode` is exactly what NegotiatorGrid needs: automatic payment processing when a negotiation agreement is reached within a LangGraph workflow. |

---

### 6.8 CrewAI

| Field | Details |
|---|---|
| **Name** | CrewAI |
| **URL** | https://github.com/crewAIInc/crewAI |
| **Type** | Repo |
| **Stars** | 48.4k |
| **Last Updated** | April 2026 (v1.14.1) |
| **Description** | Framework for orchestrating role-playing autonomous AI agents. Role-based agent teams with collaborative intelligence, task delegation, shared memory, and output chaining. Model-agnostic (OpenAI, Anthropic, Ollama, any OpenAI-compatible API). x402 payment tools can be assigned to specific agents within a crew for collaborative financial operations. Production-ready with scalability and pre-built agents. |
| **Relevance** | **High** — NegotiatorGrid can use CrewAI to define a negotiation crew: BuyerAgent, SellerAgent, MediatorAgent with assigned x402 payment tools and role-specific negotiation tasks. |

---

### 6.9 Agentic Frameworks & x402 Integration — xpay.sh

| Field | Details |
|---|---|
| **Name** | Agentic Frameworks & x402 Integration Guide |
| **URL** | https://www.xpay.sh/x402-agent-frameworks/ |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | Active |
| **Description** | Comprehensive guide covering x402 integration with 8 frameworks: LangChain (custom payment tools with retry logic + spending controls), AutoGPT (plugin-based), CrewAI (tool assignment to specific agents), AutoGen (multi-agent payment negotiations), LangGraph (state management + multi-step validation), Flowise (visual tool creation), n8n (HTTP request nodes), Zapier Central (webhook automation). Each entry rated by difficulty (beginner/intermediate/advanced) and production readiness. |
| **Relevance** | **Critical** — Framework selection guide for NegotiatorGrid. Use this to choose the right framework combination and understand x402 integration complexity for each. |

---

### 6.10 Vercel AI SDK

| Field | Details |
|---|---|
| **Name** | Vercel AI SDK |
| **URL** | https://vercel.com/docs/ai-sdk |
| **Type** | Docs |
| **Stars** | 20M+ monthly downloads |
| **Last Updated** | December 2025 (v6) |
| **Description** | TypeScript toolkit for AI applications. 20M+ monthly downloads. AI SDK 6 features: full MCP support, agents with tool execution approval, DevTools, reranking, image editing. Works with Next.js, React, Svelte, Vue, Node.js. Unified API for any AI provider. x402 integration via Cloudflare's `withX402Client` (wraps MCP client, handles payment confirmation callbacks). Install: `npm i ai`. |
| **Relevance** | **High** — If NegotiatorGrid's frontend is built on Next.js, the Vercel AI SDK provides the agent runtime with native MCP and x402 support via `withX402Client`. |

---

### 6.11 Cloudflare x402 + Agents SDK Integration

| Field | Details |
|---|---|
| **Name** | Launching the x402 Foundation — Cloudflare Blog |
| **URL** | https://blog.cloudflare.com/x402/ |
| **Type** | Blog |
| **Stars** | N/A |
| **Last Updated** | September 2025 |
| **Description** | Cloudflare's announcement of x402 Foundation support. Shows `withX402Client` wrapping an MCP client for the OpenAI Agents SDK. Agent calls `x402Client.callTool(onPaymentRequired, {name, arguments})` — the first parameter is a payment confirmation callback (set to `null` for autonomous payment). Demonstrates full Agents SDK + MCP + x402 stack. |
| **Relevance** | **High** — Reference implementation for NegotiatorGrid agents that need autonomous x402 payment within OpenAI Agents SDK workflows. |

---

## Section 7: Dashboard & UI for Agent Systems

Frontend resources for NegotiatorGrid's real-time negotiation visualization dashboard.

---

### 7.1 wagmi

| Field | Details |
|---|---|
| **Name** | wagmi |
| **URL** | https://wagmi.sh |
| **Type** | Docs / Repo |
| **Stars** | Large (widely adopted) |
| **Last Updated** | March 2026 |
| **Description** | React hooks library for Ethereum. Multichain-ready (100+ EVM networks out of the box), TypeScript-first, TanStack Query integration for caching, ~70kB gzipped. Custom chain support via `configureChains` + `jsonRpcProvider`. Key hooks: `useAccount`, `useConnect`, `useDisconnect`, `useBalance`, `useSendTransaction`. For Kite AI custom chain: use `createConfig` with `[flowTestnet]`-pattern and `injected()` connector. wagmi Core wraps viem for multi-chain + connector awareness. |
| **Relevance** | **Direct** — NegotiatorGrid's dashboard uses wagmi to connect to the Kite L1 custom EVM chain. Users connect wallets to view negotiation sessions and authorize spending limits. |

---

### 7.2 wagmi + viem Guide — QuickNode

| Field | Details |
|---|---|
| **Name** | How to Build a React Frontend with wagmi |
| **URL** | https://www.quicknode.com/guides/ethereum-development/dapps/building-dapps-with-wagmi |
| **Type** | Tutorial |
| **Stars** | N/A |
| **Last Updated** | November 2025 |
| **Description** | Full tutorial building a React dApp with wagmi + viem + Bootstrap. Covers `WagmiConfig`, `createConfig`, `configureChains`, `jsonRpcProvider` with custom RPC URL, `InjectedConnector`, `useAccount`, `useBalance`, and wallet connection UI. Shows how to add custom network support with `jsonRpcProvider` pointing to a custom RPC endpoint. |
| **Relevance** | **High** — Step-by-step reference for connecting NegotiatorGrid's React dashboard to the Kite L1 RPC endpoint. |

---

### 7.3 viem

| Field | Details |
|---|---|
| **Name** | viem |
| **URL** | https://viem.sh |
| **Type** | Docs / Repo |
| **Stars** | Large |
| **Last Updated** | Active |
| **Description** | Low-level TypeScript interface for Ethereum. Provides JSON-RPC abstractions, smart contract interaction, wallet/signing implementations. Used directly via `createPublicClient`, `createWalletClient`. Used by wagmi under the hood. Supports custom chains via chain configuration objects. `privateKeyToAccount` for agent wallet management. Tree-shakable actions via `viem/actions`. |
| **Relevance** | **Direct** — viem is used by NegotiatorGrid's frontend for direct contract reads (negotiation state, payment history) and agent wallet signing on Kite L1. |

---

### 7.4 WAGMI Basics Guide — Shapkarin

| Field | Details |
|---|---|
| **Name** | WAGMI Library: Complete Guide to Building React dApps in 2025 |
| **URL** | https://shapkarin.me/articles/WAGMI-basics/ |
| **Type** | Tutorial |
| **Stars** | N/A |
| **Last Updated** | January 2025 |
| **Description** | Comprehensive wagmi guide covering key features (React-first, TypeScript, 100+ EVM networks, TanStack Query caching), `defaultWagmiConfig` setup with WalletConnect, `WagmiProvider` + `QueryClientProvider` wrapper, `ERC-20` token transfers using `simulateContract` + `writeContract`, and multi-chain configuration patterns. |
| **Relevance** | **Medium** — Supplementary reference for setting up NegotiatorGrid's multi-chain wallet connection (Base for x402 demo + Kite L1 for production). |

---

### 7.5 Recharts

| Field | Details |
|---|---|
| **Name** | Recharts |
| **URL** | https://recharts.org |
| **Type** | Repo / Docs |
| **Stars** | 23k+ |
| **Last Updated** | Active |
| **Description** | React charting library built on D3. Component-based (`LineChart`, `AreaChart`, `BarChart`, `PieChart` with `ResponsiveContainer`). `useMemo` for data transformation, loading/error state handling, responsive containers for mobile. Best for React-native declarative chart composition. Low bundle size vs. full D3. |
| **Relevance** | **High** — NegotiatorGrid's price convergence visualization: `LineChart` with two lines (buyer offer trajectory, seller counter-offer trajectory) converging to agreement price. Use `AreaChart` for price range narrowing. |

---

### 7.6 Recharts Dynamic Charts Tutorial — DEV Community

| Field | Details |
|---|---|
| **Name** | How to Build Dynamic Charts in React with Recharts |
| **URL** | https://dev.to/calebali/how-to-build-dynamic-charts-in-react-with-recharts-including-edge-cases-3e72 |
| **Type** | Tutorial |
| **Stars** | N/A |
| **Last Updated** | May 2025 |
| **Description** | Practical Recharts tutorial with `LineChart`, `PieChart`, edge case handling (100% single category), dynamic data fetching with `useMemo` optimization, `ResponsiveContainer` for mobile layouts, and `CartesianGrid`, `Tooltip`, `Legend` components. Full code examples with TypeScript-friendly patterns. |
| **Relevance** | **High** — Code patterns for NegotiatorGrid's live price chart that updates as negotiation rounds progress. |

---

### 7.7 Socket.io Real-Time Dashboards

| Field | Details |
|---|---|
| **Name** | How to Build Real-Time Dashboards with Socket.io in Node.js |
| **URL** | https://oneuptime.com/blog/post/2026-01-26-socketio-realtime-dashboards/ |
| **Type** | Tutorial |
| **Stars** | N/A |
| **Last Updated** | January 2026 |
| **Description** | Complete guide for real-time dashboards with typed Socket.io events (`ServerToClientEvents`, `ClientToServerEvents`). Covers: room-based subscriptions (`subscribe:metrics`, room `metrics:{service}`), delta broadcasting (only changed values), `BroadcastManager` for batched updates, authentication via `auth.token`, `MetricsUpdate` typed payloads, and React `useDashboard` hook with `useEffect` Socket.io client. |
| **Relevance** | **High** — NegotiatorGrid's dashboard needs real-time updates for negotiation round events. The room-based subscription pattern maps to per-negotiation-session rooms. |

---

### 7.8 Next.js Real-Time Dashboard with WebSocket

| Field | Details |
|---|---|
| **Name** | Realtime Dashboard with FastAPI, Streamlit and Next.js — Part 3 |
| **URL** | https://jaehyeon.me/blog/2025-03-04-realtime-dashboard-3/ |
| **Type** | Tutorial |
| **Stars** | N/A |
| **Last Updated** | March 2025 |
| **Description** | Building a Next.js real-time monitoring dashboard using `react-use-websocket`, HeroUI (NextUI), Tailwind CSS, and Apache ECharts. Covers WebSocket connection lifecycle, `useWebSocket` hook with auto-reconnect, `lastJsonMessage` state updates, and chart option creation from WebSocket data. Full code at GitHub. |
| **Relevance** | **High** — Next.js WebSocket integration pattern for NegotiatorGrid's live negotiation dashboard. Shows how to handle real-time offer/counter-offer events via WebSocket. |

---

### 7.9 D3.js vs Chart.js vs Recharts Comparison

| Field | Details |
|---|---|
| **Name** | D3.js vs Chart.js vs Recharts: Which Library Should You Pick in 2026? |
| **URL** | https://www.youtube.com/watch?v=hEkcaZlP5-s |
| **Type** | Tutorial (Video) |
| **Stars** | N/A |
| **Last Updated** | January 2026 |
| **Description** | 2026 comparison video: Chart.js (canvas-based, quick setup, 16.8ms render, limited customization), Recharts (React-native components, D3 under the hood, React-only), D3.js (full SVG control, custom visualizations, industry standard). Recommendation: Recharts for React standard charts; D3 for custom visualizations; Chart.js for non-React speed. |
| **Relevance** | **Medium** — Framework selection reference for NegotiatorGrid's chart layer. Recharts is recommended for standard price convergence charts; D3 for custom negotiation space visualizations. |

---

### 7.10 Agent Dashboard React Pattern

| Field | Details |
|---|---|
| **Name** | GitHub: Next.js + WebSocket Real-time examples |
| **URL** | https://github.com/vercel/next.js/discussions/14950 |
| **Type** | Docs |
| **Stars** | N/A |
| **Last Updated** | 2020 (ongoing discussion) |
| **Description** | Community discussion on Next.js WebSocket patterns for real-time applications. Shows multiple approaches: WebSocket API in API routes, Socket.io integration, Server-Sent Events as fallback. Useful for pushing negotiation progress updates to the dashboard without polling. |
| **Relevance** | **Medium** — Supplementary reference for WebSocket architecture in Next.js for NegotiatorGrid's dashboard. |

---

### 7.11 Vercel AI SDK Cloudflare x402 Agent Pattern

| Field | Details |
|---|---|
| **Name** | Vercel AI SDK 6 Announcement |
| **URL** | https://vercel.com/blog/ai-sdk-6 |
| **Type** | Blog |
| **Stars** | N/A |
| **Last Updated** | December 2025 |
| **Description** | AI SDK 6 introduces: full MCP client support, agent loop with tool execution approval (human-in-the-loop payment confirmation), DevTools for debugging, provider-agnostic gateway routing, Anthropic tool search (BM25 + Regex for dynamic tool discovery), tool memory. x402 integration via `withX402Client`. Works in Next.js App Router with React Server Components. |
| **Relevance** | **High** — If NegotiatorGrid's frontend uses Vercel/Next.js, AI SDK 6's MCP support and tool execution approval are the right primitives for the dashboard's payment confirmation flow. |

---

## Additional Resources

### A. FIPA Standard Resources

| Name | URL | Type | Relevance |
|---|---|---|---|
| FIPA ACL Alternatives | https://agentsindex.ai/alternatives/fipa-agent-communication-language | Docs | Understanding FIPA ACL performatives and comparison with modern alternatives for NegotiatorGrid |
| Introduction to Automated Negotiation (textbook) | https://www.iiia.csic.es/~davedejonge/intro_to_nego/downloads/Introduction%20to%20Automated%20Negotiation%20v0.2.pdf | Academic | Alternating Offers Protocol theory, utility functions, and time-pressure concession models |

### B. Multi-Agent Framework Comparisons

| Name | URL | Type | Stars | Relevance |
|---|---|---|---|---|
| Best Multi-Agent Frameworks 2026 | https://gurusup.com/blog/best-multi-agent-frameworks-2026 | Blog | N/A | Framework selection guide comparing OpenAI Agents SDK, LangGraph, CrewAI, AutoGen, Google ADK |
| AutoGen (Microsoft AG2) | https://github.com/microsoft/autogen | Repo | 40k+ | Conversational multi-agent system with dynamic, code-executable agent negotiation conversations |

### C. Kite Ecosystem

| Name | URL | Type | Relevance |
|---|---|---|---|
| Kite MiCAR Whitepaper | https://gokite.ai/mica-whitepaper | Docs | Full architecture: 3-layer identity (user→agent→session), Standing Intents, Delegation Tokens, A2A/MCP/OAuth 2.1 compatibility |
| Kite Core Concepts | https://docs.gokite.ai/get-started-why-kite/core-concepts-and-terminology | Docs | AA Wallet unified account model: one on-chain AA account, multiple agent session keys, per-session risk isolation |
| ERC-8004 Reddit Discussion | https://www.reddit.com/r/AI_Agents/comments/1qwrdny/erc8004_is_quietly_building_an_onchain_identity/ | Blog | Community overview: 260+ agents registered on Ethereum/Base/Arbitrum with capabilities and metadata |

---

## Quick Reference Matrix

| Component | Primary Resource | Secondary Resource |
|---|---|---|
| x402 payment server (Python) | [x402 PyPI](https://pypi.org/project/x402/) | [samthedataman/x402-sdk](https://github.com/samthedataman/x402-sdk) |
| x402 payment client (TypeScript) | [x402-foundation/x402](https://github.com/x402-foundation/x402) | [Coinbase x402 Docs](https://docs.cdp.coinbase.com/x402/welcome) |
| MCP server (Python) | [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) | [MCP Dev Guide](https://github.com/cyanheads/model-context-protocol-resources/blob/main/guides/mcp-server-development-guide.md) |
| MCP dynamic discovery | [Docker Dynamic MCP](https://docs.docker.com/ai/mcp-catalog-and-toolkit/dynamic-mcp/) | [x402 Discovery Catalog](https://mcpmarket.com/server/x402-discovery) |
| A2A inter-agent protocol | [google/A2A](https://github.com/google-a2a/A2A) | [A2A Codelabs](https://codelabs.developers.google.com/intro-a2a-purchasing-concierge) |
| A2A + x402 bridge | [a2a-x402](https://github.com/google-agentic-commerce/a2a-x402) | — |
| Negotiation algorithm | [NegoLog](https://github.com/aniltrue/NegoLog) | [hari7261/Negotiation-MultiAgent](https://github.com/hari7261/Negotiation-MultiAgent) |
| FIPA CNP implementation | [ANEX](https://github.com/ammonhaggerty/ANEX) | [Agent Comm Protocols Blog](https://notes.muthu.co/2025/11/agent-communication-protocols-and-message-passing-patterns-for-coordination/) |
| Kite payment flow | [Kite Service Provider Guide](https://docs.gokite.ai/kite-agent-passport/service-provider-guide) | [gokite-ai/x402](https://github.com/gokite-ai/x402) |
| Kite AA wallet | [Kite AA SDK](https://docs.gokite.ai/kite-chain/account-abstraction-sdk) | [Kite Core Concepts](https://docs.gokite.ai/get-started-why-kite/core-concepts-and-terminology) |
| Agent identity (ERC-8004) | [ERC-8004 eco.com](https://eco.com/support/en/articles/13221214-what-is-erc-8004-the-ethereum-standard-enabling-trustless-ai-agents) | [ERC-8004 QuickNode](https://blog.quicknode.com/erc-8004-a-developers-guide-to-trustless-ai-agent-identity/) |
| Agent framework | [CrewAI](https://github.com/crewAIInc/crewAI) | [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) |
| Payment-enabled agents | [Coinbase AgentKit](https://github.com/coinbase/agentkit) | [Agentic Wallet](https://docs.cdp.coinbase.com/agentic-wallet/welcome) |
| Multi-agent state machine | [LangGraph](https://github.com/langchain-ai/langgraph) | [LangGraph x402 Integration](https://agentpay-docs.replit.app/integrations/langgraph) |
| Dashboard wallet connection | [wagmi](https://wagmi.sh) | [wagmi QuickNode Guide](https://www.quicknode.com/guides/ethereum-development/dapps/building-dapps-with-wagmi) |
| Price visualization | [Recharts](https://recharts.org) | [Recharts Tutorial](https://dev.to/calebali/how-to-build-dynamic-charts-in-react-with-recharts-including-edge-cases-3e72) |
| Real-time updates | [Socket.io Dashboard Guide](https://oneuptime.com/blog/post/2026-01-26-socketio-realtime-dashboards/) | [Next.js WebSocket](https://jaehyeon.me/blog/2025-03-04-realtime-dashboard-3/) |
