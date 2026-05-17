"""NegotiatorGrid configuration — loads from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


@dataclass(frozen=True)
class KiteConfig:
    """Kite blockchain network configuration."""

    rpc_url: str = os.getenv("KITE_RPC_URL", "https://rpc-testnet.gokite.ai/")
    chain_id: int = int(os.getenv("KITE_CHAIN_ID", "2368"))
    explorer_url: str = os.getenv("KITE_EXPLORER_URL", "https://testnet.kitescan.ai/")
    private_key: str = os.getenv("PRIVATE_KEY", "")
    test_usdt_addr: str = os.getenv(
        "KITE_TEST_USDT_ADDR", "0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63"
    )


@dataclass(frozen=True)
class ContractConfig:
    """Deployed contract addresses."""

    deal_record: str = os.getenv("DEALRECORD_CONTRACT_ADDR", "")
    identity_registry: str = os.getenv("IDENTITY_REGISTRY_ADDR", "")
    reputation_registry: str = os.getenv("REPUTATION_REGISTRY_ADDR", "")


@dataclass(frozen=True)
class X402Config:
    """x402 payment protocol configuration."""

    facilitator_url: str = os.getenv("KITE_FACILITATOR_URL", "https://facilitator.pieverse.io")
    facilitator_addr: str = os.getenv(
        "KITE_FACILITATOR_ADDR", "0x12343e649e6b2b2b77649DFAb88f103c02F3C78b"
    )
    network: str = "eip155:2368"
    scheme: str = "exact"


@dataclass(frozen=True)
class LLMConfig:
    """LLM provider configuration."""

    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    xai_api_key: str = os.getenv("XAI_API_KEY", "")
    xai_model: str = os.getenv("XAI_MODEL", "grok-4")
    xai_base_url: str = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
    max_tokens: int = 256
    temperature: float = 0.7


@dataclass(frozen=True)
class NegotiationConfig:
    """Negotiation engine defaults."""

    max_rounds: int = 7
    timeout_seconds: int = 30
    price_issue_min: float = 0.01
    price_issue_max: float = 1.00
    nash_deviation_threshold: float = 0.20  # Flag if >20% from Nash
    nash_grid_size: int = 10  # Discretize price into N buckets


@dataclass(frozen=True)
class MCPConfig:
    """MCP server configuration."""

    endpoint: str = os.getenv("KITE_MCP_ENDPOINT", "https://neo.dev.gokite.ai/v1/mcp")
    auth_token: str = os.getenv("KITE_MCP_AUTH_TOKEN", "")


@dataclass(frozen=True)
class PassportConfig:
    """Kite Agent Passport runtime configuration."""

    mode: str = os.getenv("KITE_PASSPORT_MODE", "mock")
    agent_id: str = os.getenv("KITE_PASSPORT_AGENT_ID", "")
    session_id: str = os.getenv("KITE_PASSPORT_SESSION_ID", "")


@dataclass(frozen=True)
class ServerConfig:
    """API server configuration."""

    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "8000"))


@dataclass
class AppConfig:
    """Top-level application configuration."""

    kite: KiteConfig = field(default_factory=KiteConfig)
    contracts: ContractConfig = field(default_factory=ContractConfig)
    x402: X402Config = field(default_factory=X402Config)
    llm: LLMConfig = field(default_factory=LLMConfig)
    negotiation: NegotiationConfig = field(default_factory=NegotiationConfig)
    mcp: MCPConfig = field(default_factory=MCPConfig)
    passport: PassportConfig = field(default_factory=PassportConfig)
    server: ServerConfig = field(default_factory=ServerConfig)


# Singleton config instance
config = AppConfig()
