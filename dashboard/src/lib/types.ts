export type AgentRole = "buyer" | "seller";
export type BargainingTendency = "dominant" | "balanced" | "submissive" | "cooperative";
export type ObjectiveMode =
  | "fairness_guardrail"
  | "buyer_advantage"
  | "seller_advantage"
  | "pure_nash";
export type PassportStatus = "stubbed" | "ready" | "disabled";
export type ModelMode = "policy_only" | "slm" | "llm" | "reasoning_llm";

export interface ReasoningSummary {
  goal?: string;
  signal?: string;
  action?: string;
  risk?: string;
}

export interface LiveNegotiationRound {
  negotiation_id?: string;
  round: number;
  buyer_offer: number | null;
  seller_offer: number | null;
  buyer_nl: string;
  seller_nl: string;
  buyer_stance?: string;
  seller_stance?: string;
  buyer_reasoning?: ReasoningSummary;
  seller_reasoning?: ReasoningSummary;
  opponent_model?: {
    estimated_reservation?: number;
    confidence?: number;
    buyer_grid_enabled?: boolean;
    seller_grid_enabled?: boolean;
  };
  nash_check?: string;
  nash_price?: number;
  nash_deviation_pct?: number;
  runtime?: ModelRuntimeMetrics;
}

export interface ModelRuntimeMetrics {
  model_mode?: ModelMode;
  provider?: string;
  base_url?: string;
  api_configured?: boolean;
  model?: string;
  model_calls?: number;
  fallback_messages?: number;
  last_error?: string;
  avg_model_latency_ms?: number;
  total_model_latency_ms?: number;
  latency_budget_ms?: number;
  runtime_note?: string;
  buyer_runtime?: ModelRuntimeMetrics;
  seller_runtime?: ModelRuntimeMetrics;
}

export interface SandboxPosture {
  buyer_agent_isolated?: boolean;
  seller_agent_isolated?: boolean;
  shared_private_state?: boolean;
  transport?: string;
  llm_tool_access?: string;
  filesystem_access?: string;
  network_access?: string;
  secrets_in_prompt?: boolean;
  typed_fields_authoritative?: boolean;
  free_text_can_execute_actions?: boolean;
  mcp_tools_enabled?: boolean;
  note?: string;
}

export interface EdgeCaseStatus {
  round_cap?: number;
  timeout_seconds?: number;
  deadlock_policy?: string;
  price_mismatch_policy?: string;
  streaming_policy?: string;
  payment_failure_policy?: string;
  mcp_policy?: string;
}

export interface PassportSessionFit {
  mode?: "live" | "mock";
  status?: "pass" | "fail" | "pending";
  negotiated_price?: number;
  remaining_budget?: number;
  per_payment_cap?: number;
  merchant?: string;
  payee?: string;
  asset?: string;
  ttl_seconds?: number;
  reason?: string;
}

export interface DealMetrics {
  buyer_surplus?: number;
  seller_surplus?: number;
  seller_discount?: number;
  buyer_movement?: number;
  nash_price?: number;
  nash_deviation_pct?: number;
  objective_mode?: ObjectiveMode;
  social_risk?: "low" | "watch" | "high" | "benchmark";
  buyer_grid_enabled?: boolean;
  seller_grid_enabled?: boolean;
  buyer_tendency?: string;
  seller_tendency?: string;
  passport_status?: PassportStatus;
  model_runtime?: ModelRuntimeMetrics;
  sandbox?: SandboxPosture;
  edge_case_status?: EdgeCaseStatus;
  passport_session_fit?: PassportSessionFit;
}

export interface NegotiationResult {
  negotiation_id: string;
  success: boolean;
  agreed_price: number;
  total_rounds: number;
  deal_hash: string;
  buyer_utility: number;
  seller_utility: number;
  duration_seconds: number;
  rounds: LiveNegotiationRound[];
  metrics: DealMetrics;
  objective_mode: ObjectiveMode;
  passport_status: PassportStatus;
  reason: string;
}

export interface DashboardStats {
  total_negotiations: number;
  total_deals: number;
  avg_rounds: number;
  total_volume: number;
  passport_status?: PassportStatus;
}

export interface AgentControls {
  gridEnabled: boolean;
  tendency: BargainingTendency;
}

export interface NegotiationControls {
  buyer: AgentControls;
  seller: AgentControls;
  objectiveMode: ObjectiveMode;
  modelMode: ModelMode;
}

export interface StreamMessage {
  type: "round_update" | "negotiation_result" | "error" | string;
  data: LiveNegotiationRound | NegotiationResult | Record<string, unknown>;
}

/** WebSocket ``pipeline_stage`` payload — mirrors ``demo.py`` stages in the API. */
export interface PipelineStageEvent {
  phase: string;
  title?: string;
  detail?: string;
  url?: string;
  wallet?: string;
  score?: number;
  [key: string]: unknown;
}
