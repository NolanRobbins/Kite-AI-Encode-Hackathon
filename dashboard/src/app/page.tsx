"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  Activity,
  ArrowLeftRight,
  BarChart3,
  CreditCard,
  DollarSign,
  FileCheck2,
  Handshake,
  Radar,
  Search,
  ShieldCheck,
  Zap,
} from "lucide-react";
import { StatCard } from "@/components/stat-card";
import { PriceConvergenceChart } from "@/components/price-convergence";
import { NegotiationTimeline } from "@/components/negotiation-timeline";
import { AgentCard } from "@/components/agent-card";
import { AttestationFeed } from "@/components/attestation-feed";
import { RecentActivity } from "@/components/recent-activity";
import { DecisionTracePanel } from "@/components/decision-trace-panel";
import { DealMetricsPanel } from "@/components/deal-metrics-panel";
import { EdgeCasePanel } from "@/components/edge-case-panel";
import { PassportSessionFitCard } from "@/components/passport-session-fit-card";
import { AgentIsolationPanel } from "@/components/agent-isolation-panel";
import { fetchStats, startNegotiation as startNegotiationRequest } from "@/lib/api";
import { useNegotiationStream } from "@/lib/use-negotiation-stream";
import type {
  BargainingTendency,
  ModelMode,
  NegotiationControls,
  ObjectiveMode,
  PassportStatus,
} from "@/lib/types";
import {
  NEGOTIATION_ROUNDS,
  BUYER_AGENT,
  SELLER_AGENT,
  STATS,
} from "@/lib/mock-data";

const tendencyOptions: Array<{ value: BargainingTendency; label: string }> = [
  { value: "dominant", label: "Dominant" },
  { value: "balanced", label: "Balanced" },
  { value: "submissive", label: "Submissive" },
];

const objectiveOptions: Array<{ value: ObjectiveMode; label: string }> = [
  { value: "fairness_guardrail", label: "Fairness Guardrail" },
  { value: "buyer_advantage", label: "Buyer Advantage" },
  { value: "seller_advantage", label: "Seller Advantage" },
  { value: "pure_nash", label: "Pure Nash Benchmark" },
];

const modelOptions: Array<{ value: ModelMode; label: string }> = [
  { value: "policy_only", label: "Policy Only" },
  { value: "slm", label: "SLM Narrator" },
  { value: "llm", label: "LLM Narrator" },
  { value: "reasoning_llm", label: "Reasoning Advisor" },
];

const procurementSteps: Array<{
  label: string;
  icon: typeof Search;
  targetId: string;
}> = [
  { label: "Discover", icon: Search, targetId: "section-discover" },
  { label: "Negotiate", icon: ArrowLeftRight, targetId: "section-negotiate" },
  { label: "Session Fit", icon: ShieldCheck, targetId: "section-session-fit" },
  { label: "Settle", icon: CreditCard, targetId: "section-settle" },
  { label: "Attest", icon: FileCheck2, targetId: "section-attest" },
];

function SelectPill<T extends string>({
  value,
  options,
  onChange,
}: {
  value: T;
  options: Array<{ value: T; label: string }>;
  onChange: (value: T) => void;
}) {
  return (
    <select
      value={value}
      onChange={(event) => onChange(event.target.value as T)}
      className="rounded-lg border border-[var(--color-border)] bg-[#0f1117] px-2 py-1.5 text-xs text-[var(--color-text)] outline-none transition-colors hover:border-[var(--color-cyan-dim)]"
    >
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}

export default function DashboardPage() {
  const [isNegotiating, setIsNegotiating] = useState(false);
  const [stats, setStats] = useState(STATS);
  const [passportStatus, setPassportStatus] = useState<PassportStatus>("stubbed");
  const [controls, setControls] = useState<NegotiationControls>({
    buyer: { gridEnabled: true, tendency: "balanced" },
    seller: { gridEnabled: true, tendency: "balanced" },
    objectiveMode: "fairness_guardrail",
    modelMode: "llm",
  });
  const [startError, setStartError] = useState("");
  const {
    connected,
    rounds,
    result,
    error,
    reset,
    pipelineStages,
    activeNegotiationId,
    setActiveNegotiationId,
  } = useNegotiationStream();

  useEffect(() => {
    fetchStats()
      .then((apiStats) => {
        setStats({
          totalNegotiations: apiStats.total_negotiations || STATS.totalNegotiations,
          totalDeals: apiStats.total_deals || STATS.totalDeals,
          totalVolume: apiStats.total_volume || STATS.totalVolume,
          avgRounds: apiStats.avg_rounds || STATS.avgRounds,
        });
        setPassportStatus(apiStats.passport_status ?? "stubbed");
      })
      .catch(() => {
        // Keep the pre-seeded demo stats if the backend is not running yet.
      });
  }, []);

  const hasLiveRounds = rounds.length > 0;
  const showScriptedFallback =
    !connected && !isNegotiating && !result && !hasLiveRounds;
  const chartRounds = useMemo(() => {
    if (showScriptedFallback) {
      return NEGOTIATION_ROUNDS.map((round) => ({
        round: round.round,
        buyerPrice: round.buyerPrice,
        sellerPrice: round.sellerPrice,
        buyerMessage: round.buyerMessage,
        sellerMessage: round.sellerMessage,
        nashCheck: "PASS",
        nashDeviationPct: 0.04,
      }));
    }

    return rounds.map((round) => ({
      round: round.round,
      buyerPrice: round.buyer_offer,
      sellerPrice: round.seller_offer,
      buyerMessage: round.buyer_nl,
      sellerMessage: round.seller_nl,
      buyerStance: round.buyer_stance,
      sellerStance: round.seller_stance,
      buyerReasoning: round.buyer_reasoning,
      sellerReasoning: round.seller_reasoning,
      nashCheck: round.nash_check,
      nashDeviationPct: round.nash_deviation_pct,
      runtime: round.runtime,
    }));
  }, [rounds, showScriptedFallback]);

  const latestRound = rounds.at(-1);
  const buyerRuntime =
    latestRound?.runtime?.buyer_runtime ??
    result?.metrics?.model_runtime?.buyer_runtime;
  const sellerRuntime =
    latestRound?.runtime?.seller_runtime ??
    result?.metrics?.model_runtime?.seller_runtime;
  const finalPrice = result?.agreed_price ?? (showScriptedFallback ? 0.1034 : undefined);
  const nashPrice = result?.metrics?.nash_price ?? latestRound?.nash_price ?? (showScriptedFallback ? 0.1034 : 0);
  const dealReached = Boolean(result?.success) || showScriptedFallback;
  const visibleRounds = chartRounds.length;
  const activeStep = dealReached ? 4 : hasLiveRounds ? 1 : isNegotiating ? 1 : 0;
  const totalModelCalls =
    (buyerRuntime?.model_calls ?? 0) + (sellerRuntime?.model_calls ?? 0);
  const totalFallbackMessages =
    (buyerRuntime?.fallback_messages ?? 0) + (sellerRuntime?.fallback_messages ?? 0);
  const isTemplateFallbackInModelMode =
    controls.modelMode !== "policy_only" &&
    totalModelCalls === 0 &&
    totalFallbackMessages > 0;
  const buyerFallbackReason = buyerRuntime?.last_error ?? "";
  const sellerFallbackReason = sellerRuntime?.last_error ?? "";

  const handleStartNegotiation = useCallback(() => {
    if (isNegotiating) return;
    setStartError("");
    setIsNegotiating(true);
    reset();

    startNegotiationRequest(controls)
      .then((started) => {
        setActiveNegotiationId(started.negotiation_id);
        setStats((prev) => ({
          ...prev,
          totalNegotiations: prev.totalNegotiations + 1,
        }));
      })
      .catch((err: Error) => {
        setStartError(err.message);
        setIsNegotiating(false);
      });
  }, [controls, isNegotiating, reset, setActiveNegotiationId]);

  const handleStartLiveNvda = useCallback(() => {
    if (isNegotiating) return;
    setStartError("");
    setIsNegotiating(true);
    reset();

    startNegotiationRequest(controls, { liveNvda: true })
      .then((started) => {
        setActiveNegotiationId(started.negotiation_id);
        setStats((prev) => ({
          ...prev,
          totalNegotiations: prev.totalNegotiations + 1,
        }));
      })
      .catch((err: Error) => {
        setStartError(err.message);
        setIsNegotiating(false);
      });
  }, [controls, isNegotiating, reset, setActiveNegotiationId]);

  useEffect(() => {
    if (!result) return;
    const timer = window.setTimeout(() => {
      setIsNegotiating(false);
      if (result.success) {
        setStats((prev) => ({
          totalNegotiations: prev.totalNegotiations,
          totalDeals: prev.totalDeals + 1,
          totalVolume: parseFloat((prev.totalVolume + result.agreed_price).toFixed(4)),
          avgRounds: parseFloat(
            (((prev.avgRounds * prev.totalDeals) + result.total_rounds) / (prev.totalDeals + 1)).toFixed(1)
          ),
        }));
      }
    }, 0);
    return () => window.clearTimeout(timer);
  }, [result]);

  const updateAgentControl = (
    side: "buyer" | "seller",
    patch: Partial<NegotiationControls["buyer"]>
  ) => {
    setControls((prev) => ({
      ...prev,
      [side]: { ...prev[side], ...patch },
    }));
  };

  const jumpToSection = useCallback((targetId: string) => {
    if (typeof window === "undefined") return;
    const node = document.getElementById(targetId);
    if (!node) return;
    node.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  return (
    <div className="p-6 space-y-6 max-w-[1440px]">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="mb-1 flex items-center gap-2 text-[10px] font-mono uppercase tracking-[0.18em] text-[var(--color-cyan)]">
            <Radar size={13} />
            Passport-powered procurement
          </div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Watch the deal form
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-[var(--color-text-muted)]">
            Independent buyer and seller agents barter through typed offers. NegotiatorGrid validates the deal before Kite Passport authorizes spend.
          </p>
          <div className="mt-2 flex items-center gap-2 text-[10px] text-[var(--color-text-faint)]">
            <span className={`h-1.5 w-1.5 rounded-full ${connected ? "bg-[var(--color-deal)]" : "bg-[var(--color-warning)]"}`} />
            {connected ? "Backend stream connected" : "Backend stream offline"}
            {activeNegotiationId ? (
              <span className="font-mono">| run {activeNegotiationId}</span>
            ) : null}
            <span>· Passport Session Fit uses live MCP when configured, otherwise a labeled mock</span>
          </div>
          <div className="mt-1 flex flex-wrap items-center gap-2 text-[10px] text-[var(--color-text-faint)]">
            <span>
              Buyer model:{" "}
              <span className="font-mono text-[var(--color-buyer)]">
                {buyerRuntime?.provider ?? "openai"} / {buyerRuntime?.model ?? "gpt-4o-mini"}
              </span>
            </span>
            <span>·</span>
            <span>
              Seller model:{" "}
              <span className="font-mono text-[var(--color-seller)]">
                {sellerRuntime?.provider ?? "xai"} / {sellerRuntime?.model ?? "grok-4"}
              </span>
            </span>
          </div>
        </div>

        {/* Start negotiation — sandbox vs live NVDA (same server path as demo.py) */}
        <div className="flex flex-col items-end gap-2 sm:flex-row">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleStartLiveNvda}
            disabled={isNegotiating}
            className={`
            flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm border border-[var(--color-cyan-dim)]
            transition-all duration-200
            ${
              isNegotiating
                ? "bg-[#0b0d12] text-[var(--color-text-muted)] cursor-wait"
                : "bg-[#0f1117] text-[var(--color-cyan)] hover:border-[var(--color-cyan)]"
            }
          `}
            type="button"
            title="Requires FastAPI :8000, surprise_api :8001, repo .env with Kite contracts + PRIVATE_KEY"
          >
            <Handshake size={16} />
            {isNegotiating ? "Running…" : "Live NVDA + Kite"}
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleStartNegotiation}
            disabled={isNegotiating}
            className={`
            flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium text-sm
            transition-all duration-200
            ${
              isNegotiating
                ? "bg-[var(--color-cyan-dim)] text-[var(--color-text-muted)] cursor-wait"
                : "bg-[var(--color-cyan)] text-[#0f1117] hover:shadow-[0_0_20px_rgba(34,211,238,0.3)] glow-cyan"
            }
          `}
            data-testid="button-start-negotiation"
            type="button"
          >
            <Zap size={16} />
            {isNegotiating ? "Negotiating..." : "Start Negotiation"}
          </motion.button>
        </div>
      </div>

      {(error || startError) && (
        <div className="rounded-lg border border-yellow-900 bg-yellow-950/30 px-4 py-3 text-xs text-[var(--color-warning)]">
          {startError || error}
        </div>
      )}
      {isTemplateFallbackInModelMode && (
        <div className="rounded-lg border border-yellow-900 bg-yellow-950/30 px-4 py-3 text-xs text-[var(--color-warning)]">
          Model fallback detected. This run is using template narration instead of live OpenAI/xAI outputs.
          {(buyerFallbackReason || sellerFallbackReason) && (
            <div className="mt-1 font-mono text-[10px] text-yellow-300">
              buyer: {buyerFallbackReason || "unknown"} | seller: {sellerFallbackReason || "unknown"}
            </div>
          )}
        </div>
      )}

      <div id="section-discover" />
      {pipelineStages.length > 0 && (
        <div className="card-base p-4">
          <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-[var(--color-cyan)]">
            Live pipeline (same stages as demo.py)
          </div>
          <ol className="max-h-48 space-y-2 overflow-y-auto text-xs text-[var(--color-text-muted)]">
            {pipelineStages.map((s, i) => (
              <li
                key={`${String(s.phase)}-${i}`}
                className="border-l-2 border-[var(--color-cyan-dim)] pl-3"
              >
                <span className="font-mono text-[var(--color-text-faint)]">{String(s.phase)}</span>
                {s.title ? (
                  <span className="ml-2 font-medium text-[var(--color-text)]">{String(s.title)}</span>
                ) : null}
                {s.detail ? (
                  <div className="mt-0.5 text-[var(--color-text-faint)]">{String(s.detail)}</div>
                ) : null}
              </li>
            ))}
          </ol>
        </div>
      )}

      <div className="card-base p-3">
        <div className="grid grid-cols-5 gap-2">
          {procurementSteps.map((step, index) => {
            const Icon = step.icon;
            const isDone = index <= activeStep;
            const isCurrent = index === activeStep;
            return (
              <div
                key={step.label}
                role="button"
                tabIndex={0}
                onClick={() => jumpToSection(step.targetId)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    jumpToSection(step.targetId);
                  }
                }}
                className={`flex items-center gap-2 rounded-lg border px-3 py-2 ${
                  isCurrent
                    ? "border-[var(--color-cyan-dim)] bg-[var(--color-cyan-glow)] text-[var(--color-cyan)]"
                    : isDone
                    ? "border-[var(--color-deal-dim)] bg-[var(--color-deal-bg)] text-[var(--color-deal)]"
                    : "border-[var(--color-border-subtle)] bg-[#0b0d12] text-[var(--color-text-faint)]"
                } cursor-pointer`}
              >
                <Icon size={14} />
                <span className="text-xs font-semibold">{step.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Hero barter view */}
      <div id="section-negotiate" className="grid grid-cols-[minmax(0,1fr)_380px] gap-4">
        <PriceConvergenceChart
          rounds={chartRounds}
          visibleRounds={visibleRounds}
          dealReached={dealReached}
          finalPrice={finalPrice}
          nashPrice={nashPrice}
          className="min-h-[460px]"
        />
        <div className="space-y-4">
          <NegotiationTimeline
            rounds={chartRounds}
            visibleRounds={visibleRounds}
            dealReached={dealReached}
            finalPrice={finalPrice}
            negotiationId={result?.negotiation_id ?? activeNegotiationId ?? undefined}
          />
          <div id="section-session-fit">
            <PassportSessionFitCard
              metrics={result?.metrics}
              passportStatus={result?.passport_status ?? passportStatus}
              compact
            />
          </div>
          <div id="section-isolation">
            <AgentIsolationPanel />
          </div>
        </div>
      </div>

      {/* Demo controls */}
      <div className="card-base p-4">
        <div className="mb-3 flex items-start justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-[var(--color-text)]">Demo Controls</h2>
            <p className="mt-1 text-[10px] text-[var(--color-text-faint)]">
              Buyer runtime targets OpenAI and seller runtime targets xAI in LLM modes.
            </p>
            <p className="text-xs text-[var(--color-text-faint)]">
              Toggle each agent’s framework and bargaining posture, then compare the outcome against Nash.
            </p>
          </div>
          <div className="flex flex-wrap items-center justify-end gap-2">
            <div>
              <div className="mb-1 text-[10px] uppercase tracking-wider text-[var(--color-text-faint)]">
                Objective
              </div>
              <SelectPill
                value={controls.objectiveMode}
                options={objectiveOptions}
                onChange={(objectiveMode) => setControls((prev) => ({ ...prev, objectiveMode }))}
              />
            </div>
            <div>
              <div className="mb-1 text-[10px] uppercase tracking-wider text-[var(--color-text-faint)]">
                Model runtime
              </div>
              <SelectPill
                value={controls.modelMode}
                options={modelOptions}
                onChange={(modelMode) => setControls((prev) => ({ ...prev, modelMode }))}
              />
            </div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {(["buyer", "seller"] as const).map((side) => (
            <div key={side} className="rounded-lg border border-[var(--color-border-subtle)] bg-[#0f1117] p-3">
              <div className="mb-2 flex items-center justify-between">
                <div className={`text-xs font-semibold capitalize ${side === "buyer" ? "text-[var(--color-buyer)]" : "text-[var(--color-seller)]"}`}>
                  {side} agent
                </div>
                <button
                  onClick={() => updateAgentControl(side, { gridEnabled: !controls[side].gridEnabled })}
                  className={`rounded-full border px-2 py-1 text-[10px] font-mono ${
                    controls[side].gridEnabled
                      ? "border-[var(--color-cyan-dim)] bg-[var(--color-cyan-glow)] text-[var(--color-cyan)]"
                      : "border-[var(--color-border)] text-[var(--color-text-faint)]"
                  }`}
                >
                  Grid {controls[side].gridEnabled ? "ON" : "OFF"}
                </button>
              </div>
              <div className="flex items-center justify-between gap-3">
                <span className="text-[10px] uppercase tracking-wider text-[var(--color-text-faint)]">
                  Bargaining tendency
                </span>
                <SelectPill
                  value={controls[side].tendency}
                  options={tendencyOptions}
                  onChange={(tendency) => updateAgentControl(side, { tendency })}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard
          label="Total Negotiations"
          value={stats.totalNegotiations.toString()}
          icon={Activity}
          accent="var(--color-cyan)"
        />
        <StatCard
          label="Deals Settled"
          value={stats.totalDeals.toString()}
          icon={Handshake}
          accent="var(--color-deal)"
        />
        <StatCard
          label="Total Volume"
          value={`$${stats.totalVolume.toFixed(2)}`}
          icon={DollarSign}
          accent="var(--color-buyer)"
          subtext="USDT"
        />
        <StatCard
          label="Avg Rounds"
          value={stats.avgRounds.toFixed(1)}
          icon={BarChart3}
          accent="var(--color-seller)"
          subtext="per deal"
        />
      </div>

      <DecisionTracePanel latestRound={latestRound} connected={connected} />
      <DealMetricsPanel
        metrics={result?.metrics}
        passportStatus={result?.passport_status ?? passportStatus}
      />
      <EdgeCasePanel
        edgeCaseStatus={result?.metrics?.edge_case_status}
        sandbox={result?.metrics?.sandbox}
      />

      {/* Agent Cards */}
      <div id="agents" className="grid grid-cols-2 gap-4">
        <AgentCard
          agent={BUYER_AGENT}
          gridEnabled={controls.buyer.gridEnabled}
          tendency={controls.buyer.tendency}
          objectiveMode={controls.objectiveMode}
          providerLabel={buyerRuntime?.provider ?? "openai"}
          modelLabel={buyerRuntime?.model ?? "gpt-4o-mini"}
          calls={buyerRuntime?.model_calls ?? 0}
          fallbacks={buyerRuntime?.fallback_messages ?? 0}
          delay={0.1}
        />
        <AgentCard
          agent={SELLER_AGENT}
          gridEnabled={controls.seller.gridEnabled}
          tendency={controls.seller.tendency}
          objectiveMode={controls.objectiveMode}
          providerLabel={sellerRuntime?.provider ?? "xai"}
          modelLabel={sellerRuntime?.model ?? "grok-4"}
          calls={sellerRuntime?.model_calls ?? 0}
          fallbacks={sellerRuntime?.fallback_messages ?? 0}
          delay={0.2}
        />
      </div>

      {/* Bottom row: Recent + Attestations */}
      <div id="deals" className="grid grid-cols-[1fr_1fr] gap-4">
        <div id="section-settle">
          <RecentActivity />
        </div>
        <div id="section-attest">
          <AttestationFeed />
        </div>
      </div>
    </div>
  );
}
