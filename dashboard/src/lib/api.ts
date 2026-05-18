import type { DashboardStats, NegotiationControls } from "@/lib/types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";
const API_BASE = API_BASE_URL;
const DEFAULT_TIMEOUT_MS = 10_000;

const tendencyToStrategy = (tendency: string) => {
  if (tendency === "dominant") return "boulware";
  if (tendency === "cooperative" || tendency === "submissive") return "conceder";
  return "linear";
};

export interface NegotiationRoundRecord {
  round: number;
  buyer_offer: number | null;
  seller_offer: number | null;
  buyer_nl: string;
  seller_nl: string;
  opponent_model: {
    estimated_reservation?: number;
    confidence?: number;
    [key: string]: unknown;
  };
  nash_check: string;
}

export interface NegotiationResultRecord {
  negotiation_id: string;
  success: boolean;
  agreed_price: number;
  total_rounds: number;
  deal_hash: string;
  buyer_utility: number;
  seller_utility: number;
  duration_seconds: number;
  rounds: NegotiationRoundRecord[];
  reason: string;
}

export interface SettlementRecord {
  settled: boolean;
  x402_tx_hash: string;
  x402_network: string;
  attestation_tx: string;
  attestation_deal_hash: string;
  kitescan_tx_url: string;
  kitescan_attestation_url: string;
  pipeline_error: string;
  mock_mode: boolean;
  duration_seconds: number;
  payment_refused?: boolean;
  rejection_reason?: string;
  expected_atomic?: number;
  requested_atomic?: number;
}

export interface DealRecord extends SettlementRecord {
  deal_hash: string;
  negotiation_id: string;
  agreed_price: number;
  total_rounds: number;
  buyer_agent: string;
  seller_agent: string;
  buyer_wallet: string;
  seller_wallet: string;
  buyer_utility: number;
  seller_utility: number;
  timestamp: number;
  pipeline_duration_seconds: number;
  deal_status?: "pending" | "settled" | "rejected";
  seller_agent_id?: number;
}

export interface Act3CompareKickoff {
  scope: string;
  resource_uri: string;
  high_rep: { negotiation_id: string; label: string; reputation_stars: number };
  low_rep: { negotiation_id: string; label: string; reputation_stars: number };
}

export interface Act3Side {
  negotiation_id: string;
  status: string;
  label: string;
  reputation_stars: number;
  agreed_price: number;
  total_rounds: number;
  deal_hash: string;
  rounds: NegotiationRoundRecord[];
  settlement: Partial<SettlementRecord>;
  success: boolean;
}

export interface Act3CompareStatus {
  high_rep: Act3Side;
  low_rep: Act3Side;
  both_complete: boolean;
  savings_abs: number;
  savings_pct: number;
}

export interface NegotiationTraceRecord {
  schema_version: number;
  negotiation_id: string;
  updated_at: number;
  status: string;
  trace_path: string;
  request: Record<string, unknown>;
  result?: Record<string, unknown>;
  deal?: Record<string, unknown>;
  events: Array<Record<string, unknown>>;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly endpoint: string,
    public readonly cause?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  opts: {
    method?: "GET" | "POST";
    body?: unknown;
    signal?: AbortSignal;
    timeoutMs?: number;
  } = {},
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(
    () => controller.abort(),
    opts.timeoutMs ?? DEFAULT_TIMEOUT_MS,
  );
  const onAbort = () => controller.abort();
  opts.signal?.addEventListener("abort", onAbort, { once: true });

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      method: opts.method ?? "GET",
      headers: opts.body ? { "Content-Type": "application/json" } : undefined,
      body: opts.body ? JSON.stringify(opts.body) : undefined,
      signal: controller.signal,
      cache: opts.method === "POST" ? undefined : "no-store",
    });
    if (!response.ok) {
      throw new ApiError(`${path} failed (${response.status})`, response.status, path);
    }
    return (await response.json()) as T;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(
      `${path} network error: ${(err as Error)?.message ?? String(err)}`,
      0,
      path,
      err,
    );
  } finally {
    window.clearTimeout(timeoutId);
    opts.signal?.removeEventListener("abort", onAbort);
  }
}

export const api = {
  listDeals: (signal?: AbortSignal) =>
    request<DealRecord[]>("/api/deals", { signal }),
  startAct3Compare: (body: Record<string, unknown> = {}, signal?: AbortSignal) =>
    request<Act3CompareKickoff>("/api/act3/compare", {
      method: "POST",
      body,
      signal,
    }),
  getAct3CompareStatus: (
    highId: string,
    lowId: string,
    signal?: AbortSignal,
  ) =>
    request<Act3CompareStatus>(
      `/api/act3/compare/${encodeURIComponent(highId)}/${encodeURIComponent(lowId)}`,
      { signal },
    ),
  listTraces: (signal?: AbortSignal) => request<Array<Record<string, unknown>>>("/api/traces", { signal }),
  getTrace: (negotiationId: string, signal?: AbortSignal) =>
    request<NegotiationTraceRecord>(
      `/api/negotiations/${encodeURIComponent(negotiationId)}/trace`,
      { signal },
    ),
} as const;

export async function startNegotiation(
  controls: NegotiationControls,
  opts?: { liveNvda?: boolean },
) {
  const liveNvda = Boolean(opts?.liveNvda);
  const response = await fetch(`${API_BASE}/api/negotiate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(
      liveNvda
        ? {
            buyer_config: {
              agent_id: "server-buyer",
              address: "0x0000000000000000000000000000000000000000",
              role: "buyer",
              grid_enabled: controls.buyer.gridEnabled,
              tendency: controls.buyer.tendency,
            },
            seller_config: {
              agent_id: "server-seller",
              address: "0x0000000000000000000000000000000000000000",
              role: "seller",
              grid_enabled: controls.seller.gridEnabled,
              tendency: controls.seller.tendency,
            },
            negotiation_params: {
              max_rounds: 12,
              timeout_seconds: 30,
              resource_uri: "/api/nvda",
              scope: "nvda-market-data",
              objective_mode: controls.objectiveMode,
              passport_status: "stubbed",
              model_mode: controls.modelMode,
              model_provider:
                controls.modelMode === "policy_only" ? "template" : "openai-compatible",
              model_name:
                controls.modelMode === "reasoning_llm"
                  ? "reasoning-advisor"
                  : controls.modelMode === "llm"
                    ? "gpt-4o-mini"
                    : controls.modelMode === "slm"
                      ? "local-small-narrator"
                      : "template",
              model_latency_budget_ms: controls.modelMode === "reasoning_llm" ? 5000 : 1200,
              scenario: "nvda_surprise_live",
              deal_binding_mode: "canonical_eip712",
            },
          }
        : {
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
              max_rounds: 12,
              timeout_seconds: 30,
              resource_uri: "/api/weather-pro",
              scope: "weather-data",
              objective_mode: controls.objectiveMode,
              passport_status: "stubbed",
              model_mode: controls.modelMode,
              model_provider:
                controls.modelMode === "policy_only" ? "template" : "openai-compatible",
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
          },
    ),
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
