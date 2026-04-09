"""AgentCard definition for NegotiatorGrid — served at /.well-known/agent-card.json."""

from __future__ import annotations

AGENT_CARD: dict = {
    "name": "NegotiatorGrid",
    "description": (
        "Agent-to-agent price negotiation with game-theoretic strategies, "
        "x402 settlement, and on-chain attestation on Kite AI"
    ),
    "url": "http://localhost:8000",
    "version": "0.1.0",
    "provider": {
        "organization": "NegotiatorGrid",
        "url": "https://negotiatorgrid.dev",
    },
    "capabilities": {
        "streaming": True,
        "negotiation": True,
        "x402_payment": True,
        "erc8004_identity": True,
        "reputation_feed": True,
        "extensions": [
            {
                "uri": "x402:payment",
                "description": "x402 on-chain payment settlement via Kite facilitator",
                "required": True,
            },
            {
                "uri": "negotiatorgrid:bilateral-negotiation",
                "description": "Multi-round bilateral price negotiation with game-theoretic strategies",
                "required": True,
            },
        ],
    },
    "defaultInputModes": ["text"],
    "defaultOutputModes": ["text"],
    "skills": [
        {
            "id": "price-negotiation",
            "name": "Bilateral Price Negotiation",
            "description": (
                "Negotiate service prices through multi-round alternating offers "
                "with aspiration, tit-for-tat, and boulware strategies"
            ),
            "tags": ["negotiation", "pricing", "game-theory", "negotiatorgrid-v1"],
            "examples": [
                "Negotiate a price for weather API access",
                "Start a bilateral negotiation with budget $0.01-$0.10",
            ],
        },
        {
            "id": "deal-attestation",
            "name": "On-Chain Deal Attestation",
            "description": "Record negotiated deals on Kite blockchain with cryptographic proofs",
            "tags": ["attestation", "on-chain", "deal-record"],
        },
        {
            "id": "reputation-query",
            "name": "Agent Reputation Lookup",
            "description": "Query ERC-8004 reputation scores and deal history for any agent",
            "tags": ["reputation", "erc-8004", "identity"],
        },
    ],
    "extensions": [
        {
            "uri": "x402:payment",
            "required": True,
        },
        {
            "uri": "negotiatorgrid:bilateral-negotiation",
            "required": True,
            "config": {
                "max_rounds": 7,
                "supported_tokens": ["USDT"],
                "supported_strategies": ["aspiration", "tit-for-tat", "boulware"],
            },
        },
    ],
}
