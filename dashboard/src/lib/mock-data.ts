export interface NegotiationRound {
  round: number;
  buyerPrice: number;
  sellerPrice: number;
  buyerMessage: string;
  sellerMessage: string;
}

export interface Deal {
  id: string;
  hash: string;
  buyerId: string;
  buyerName: string;
  sellerId: string;
  sellerName: string;
  agreedPrice: number;
  rounds: number;
  timestamp: string;
  txHash: string;
  status: "settled" | "in_progress" | "failed";
}

export interface Agent {
  id: string;
  name: string;
  walletAddress: string;
  reputation: number;
  dealCount: number;
  strategy: string;
  role: "buyer" | "seller";
  avatar: string;
}

export const NEGOTIATION_ROUNDS: NegotiationRound[] = [
  {
    round: 1,
    buyerPrice: 0.0800,
    sellerPrice: 0.1200,
    buyerMessage: "I'd like to start at $0.08/call. Given current market rates for weather data APIs, this seems fair for bulk access.",
    sellerMessage: "My WeatherPro service at $0.12/call includes sub-150ms latency, 99.9% uptime SLA, and real-time satellite feeds.",
  },
  {
    round: 2,
    buyerPrice: 0.0802,
    sellerPrice: 0.1198,
    buyerMessage: "I appreciate the quality metrics. Adjusting slightly to $0.0802 — still need to stay within my operational budget.",
    sellerMessage: "Noted your constraints. At $0.1198, you're getting enterprise-grade data at near-wholesale pricing.",
  },
  {
    round: 3,
    buyerPrice: 0.0808,
    sellerPrice: 0.1192,
    buyerMessage: "Moving to $0.0808. I'm projecting 50K calls/month which should offset your volume concerns.",
    sellerMessage: "Volume commitment helps. $0.1192 factors in the dedicated throughput I'd allocate for your traffic.",
  },
  {
    round: 4,
    buyerPrice: 0.0825,
    sellerPrice: 0.1175,
    buyerMessage: "I can move to $0.0825. Let's find middle ground — I'm committed to a 6-month contract.",
    sellerMessage: "6 months is attractive. $0.1175 with that commitment. My infrastructure costs demand this floor.",
  },
  {
    round: 5,
    buyerPrice: 0.0861,
    sellerPrice: 0.1139,
    buyerMessage: "Significant move to $0.0861. This is stretching my budget but shows good faith.",
    sellerMessage: "Matching your energy — $0.1139. We're converging. Nash equilibrium analysis supports this range.",
  },
  {
    round: 6,
    buyerPrice: 0.0927,
    sellerPrice: 0.1073,
    buyerMessage: "Final push: $0.0927. This represents my maximum viable cost per call.",
    sellerMessage: "$0.1073 is where I need to be. We're within the optimal agreement zone.",
  },
];

export const DEAL_PRICE = 0.1034;

export const RECENT_DEALS: Deal[] = [
  {
    id: "neg-047",
    hash: "0x7a3f...e91c",
    buyerId: "agent-001",
    buyerName: "DataBuyer-Alpha",
    sellerId: "agent-002",
    sellerName: "WeatherPro-Service",
    agreedPrice: 0.1034,
    rounds: 6,
    timestamp: "2025-01-18T14:32:00Z",
    txHash: "0xabc123...def456",
    status: "settled",
  },
  {
    id: "neg-046",
    hash: "0x5b2e...a73d",
    buyerId: "agent-003",
    buyerName: "PredictBot-7",
    sellerId: "agent-004",
    sellerName: "GeoData-Prime",
    agreedPrice: 0.0892,
    rounds: 5,
    timestamp: "2025-01-18T14:28:00Z",
    txHash: "0x9ef012...345abc",
    status: "settled",
  },
  {
    id: "neg-045",
    hash: "0x1d4c...f28e",
    buyerId: "agent-005",
    buyerName: "InsightEngine",
    sellerId: "agent-006",
    sellerName: "StreamFeed-Pro",
    agreedPrice: 0.1150,
    rounds: 4,
    timestamp: "2025-01-18T14:21:00Z",
    txHash: "0x678def...901ghi",
    status: "settled",
  },
  {
    id: "neg-044",
    hash: "0x8e9a...c54b",
    buyerId: "agent-007",
    buyerName: "AnalyticsMesh",
    sellerId: "agent-008",
    sellerName: "SatLink-Oracle",
    agreedPrice: 0.0765,
    rounds: 7,
    timestamp: "2025-01-18T14:15:00Z",
    txHash: "0xjkl234...mno567",
    status: "settled",
  },
  {
    id: "neg-043",
    hash: "0x3f7b...d16a",
    buyerId: "agent-009",
    buyerName: "FlowTrader-X",
    sellerId: "agent-010",
    sellerName: "APIVault-Core",
    agreedPrice: 0.0981,
    rounds: 5,
    timestamp: "2025-01-18T14:08:00Z",
    txHash: "0xpqr890...stu123",
    status: "settled",
  },
];

export const BUYER_AGENT: Agent = {
  id: "agent-001",
  name: "DataBuyer-Alpha",
  walletAddress: "0x742d35Cc6634C0532925a3b844Bc9e7595bD18",
  reputation: 4.8,
  dealCount: 47,
  strategy: "Aspiration-Based",
  role: "buyer",
  avatar: "DB",
};

export const SELLER_AGENT: Agent = {
  id: "agent-002",
  name: "WeatherPro-Service",
  walletAddress: "0x2096c34E1F3B4aA7C5f8dE90b6cA42Ef1d2cE",
  reputation: 4.5,
  dealCount: 123,
  strategy: "Time-Concession",
  role: "seller",
  avatar: "WP",
};

export const ATTESTATION_FEED = [
  {
    dealHash: "0x7a3f8b2c...e91cd4a7",
    buyerId: "agent-001",
    sellerId: "agent-002",
    price: 0.1034,
    rounds: 6,
    txHash: "0xabc123def456789abc123def456789abc123def456789abc123def456789abcd",
    timestamp: "2025-01-18T14:32:00Z",
    attestationId: "ATT-00047",
  },
  {
    dealHash: "0x5b2e9d1a...a73df582",
    buyerId: "agent-003",
    sellerId: "agent-004",
    price: 0.0892,
    rounds: 5,
    txHash: "0x9ef012345abc678def012345abc678def012345abc678def012345abc678def01",
    timestamp: "2025-01-18T14:28:00Z",
    attestationId: "ATT-00046",
  },
  {
    dealHash: "0x1d4c7e3f...f28e6a19",
    buyerId: "agent-005",
    sellerId: "agent-006",
    price: 0.1150,
    rounds: 4,
    txHash: "0x678def901ghi234jkl678def901ghi234jkl678def901ghi234jkl678def901g",
    timestamp: "2025-01-18T14:21:00Z",
    attestationId: "ATT-00045",
  },
  {
    dealHash: "0x8e9a4b5c...c54b1d28",
    buyerId: "agent-007",
    sellerId: "agent-008",
    price: 0.0765,
    rounds: 7,
    txHash: "0xjkl234mno567pqr890jkl234mno567pqr890jkl234mno567pqr890jkl234mno5",
    timestamp: "2025-01-18T14:15:00Z",
    attestationId: "ATT-00044",
  },
  {
    dealHash: "0x3f7b2a9e...d16a8c45",
    buyerId: "agent-009",
    sellerId: "agent-010",
    price: 0.0981,
    rounds: 5,
    txHash: "0xpqr890stu123vwx456pqr890stu123vwx456pqr890stu123vwx456pqr890stu1",
    timestamp: "2025-01-18T14:08:00Z",
    attestationId: "ATT-00043",
  },
];

export const STATS = {
  totalNegotiations: 47,
  totalDeals: 42,
  totalVolume: 4.82,
  avgRounds: 4.3,
};
