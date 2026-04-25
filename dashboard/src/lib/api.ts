import type { DashboardStats, NegotiationControls } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const tendencyToStrategy = (tendency: string) => {
  if (tendency === "dominant") return "boulware";
  if (tendency === "cooperative") return "conceder";
  return "linear";
};

export async function startNegotiation(controls: NegotiationControls) {
  const response = await fetch(`${API_BASE}/api/negotiate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      buyer_config: {
        agent_id: "agent-buyer-alpha",
        address: "0x742d35Cc6634C0532925a3b844Bc9e7595bD18",
        role: "buyer",
        initial_price: 0.08,
        reservation_price: 0.12,
        strategy: tendencyToStrategy(controls.buyer.tendency),
        grid_enabled: controls.buyer.gridEnabled,
        tendency: controls.buyer.tendency,
        reputation_score: 84,
      },
      seller_config: {
        agent_id: "agent-weatherpro",
        address: "0x2096c34E1F3B4aA7C5f8dE90b6cA42Ef1d2cE",
        role: "seller",
        initial_price: 0.13,
        reservation_price: 0.09,
        strategy: tendencyToStrategy(controls.seller.tendency),
        grid_enabled: controls.seller.gridEnabled,
        tendency: controls.seller.tendency,
        reputation_score: 78,
      },
      negotiation_params: {
        max_rounds: 7,
        timeout_seconds: 30,
        resource_uri: "/api/weather-pro",
        scope: "weather-data",
        objective_mode: controls.objectiveMode,
        passport_status: "stubbed",
        model_mode: controls.modelMode,
        model_provider: controls.modelMode === "policy_only" ? "template" : "openai-compatible",
        model_name:
          controls.modelMode === "reasoning_llm"
            ? "reasoning-advisor"
            : controls.modelMode === "llm"
            ? "gpt-4o-mini"
            : controls.modelMode === "slm"
            ? "local-small-narrator"
            : "template",
        model_latency_budget_ms: controls.modelMode === "reasoning_llm" ? 5000 : 1200,
      },
    }),
  });

  if (!response.ok) {
    throw new Error(`Negotiation start failed (${response.status})`);
  }

  return response.json() as Promise<{ negotiation_id: string; status: string }>;
}

export async function fetchStats(): Promise<DashboardStats> {
  const response = await fetch(`${API_BASE}/api/stats`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Stats request failed (${response.status})`);
  }
  return response.json();
}
