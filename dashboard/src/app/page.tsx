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
import type { BargainingTendency, ModelMode, NegotiationControls, ObjectiveMode } from "@/lib/types";
import {
  NEGOTIATION_ROUNDS,
  BUYER_AGENT,
  SELLER_AGENT,
  STATS,
} from "@/lib/mock-data";

const tendencyOptions: Array<{ value: BargainingTendency; label: string }> = [
  { value: "dominant", label: "Dominant" },
  { value: "balanced", label: "Balanced" },
  { value: "cooperative", label: "Cooperative" },
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

const procurementSteps = [
  { label: "Discover", icon: Search },
  { label: "Negotiate", icon: ArrowLeftRight },
  { label: "Session Fit", icon: ShieldCheck },
  { label: "Settle", icon: CreditCard },
  { label: "Attest", icon: FileCheck2 },
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
  const [controls, setControls] = useState<NegotiationControls>({
    buyer: { gridEnabled: true, tendency: "balanced" },
    seller: { gridEnabled: true, tendency: "balanced" },
    objectiveMode: "fairness_guardrail",
    modelMode: "policy_only",
  });
  const [startError, setStartError] = useState("");
  const { connected, rounds, result, error, reset } = useNegotiationStream();

  useEffect(() => {
    fetchStats()
      .then((apiStats) => {
        setStats({
          totalNegotiations: apiStats.total_negotiations || STATS.totalNegotiations,
          totalDeals: apiStats.total_deals || STATS.totalDeals,
          totalVolume: apiStats.total_volume || STATS.totalVolume,
          avgRounds: apiStats.avg_rounds || STATS.avgRounds,
        });
      })
      .catch(() => {
        // Keep the pre-seeded demo stats if the backend is not running yet.
      });
  }, []);

  const hasLiveRounds = rounds.length > 0;
  const chartRounds = useMemo(() => {
    if (!hasLiveRounds) {
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
    }));
  }, [hasLiveRounds, rounds]);

  const latestRound = rounds.at(-1);
  const finalPrice = result?.agreed_price ?? (hasLiveRounds ? undefined : 0.1034);
  const nashPrice = result?.metrics?.nash_price ?? latestRound?.nash_price ?? 0.1034;
  const dealReached = Boolean(result?.success) || (!hasLiveRounds && !isNegotiating);
  const visibleRounds = chartRounds.length;
  const activeStep = dealReached ? 4 : hasLiveRounds ? 1 : 0;

  const handleStartNegotiation = useCallback(() => {
    if (isNegotiating) return;
    setStartError("");
    setIsNegotiating(true);
    reset();

    startNegotiationRequest(controls)
      .then(() => {
        setStats((prev) => ({
          ...prev,
          totalNegotiations: prev.totalNegotiations + 1,
        }));
      })
      .catch((err: Error) => {
        setStartError(err.message);
        setIsNegotiating(false);
      });
  }, [controls, isNegotiating, reset]);

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
            <span>· Passport Session Fit uses live MCP when configured, otherwise a labeled mock</span>
          </div>
        </div>

        {/* Start Negotiation CTA */}
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
        >
          <Zap size={16} />
          {isNegotiating ? "Negotiating..." : "Start Negotiation"}
        </motion.button>
      </div>

      {(error || startError) && (
        <div className="rounded-lg border border-yellow-900 bg-yellow-950/30 px-4 py-3 text-xs text-[var(--color-warning)]">
          {startError || error}
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
                className={`flex items-center gap-2 rounded-lg border px-3 py-2 ${
                  isCurrent
                    ? "border-[var(--color-cyan-dim)] bg-[var(--color-cyan-glow)] text-[var(--color-cyan)]"
                    : isDone
                    ? "border-[var(--color-deal-dim)] bg-[var(--color-deal-bg)] text-[var(--color-deal)]"
                    : "border-[var(--color-border-subtle)] bg-[#0b0d12] text-[var(--color-text-faint)]"
                }`}
              >
                <Icon size={14} />
                <span className="text-xs font-semibold">{step.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Hero barter view */}
      <div className="grid grid-cols-[minmax(0,1fr)_380px] gap-4">
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
          />
          <PassportSessionFitCard
            metrics={result?.metrics}
            passportStatus={result?.passport_status ?? "stubbed"}
            compact
          />
          <AgentIsolationPanel />
        </div>
      </div>

      {/* Demo controls */}
      <div className="card-base p-4">
        <div className="mb-3 flex items-start justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-[var(--color-text)]">Demo Controls</h2>
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
        passportStatus={result?.passport_status ?? "stubbed"}
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
          delay={0.1}
        />
        <AgentCard
          agent={SELLER_AGENT}
          gridEnabled={controls.seller.gridEnabled}
          tendency={controls.seller.tendency}
          objectiveMode={controls.objectiveMode}
          delay={0.2}
        />
      </div>

      {/* Bottom row: Recent + Attestations */}
      <div id="deals" className="grid grid-cols-[1fr_1fr] gap-4">
        <RecentActivity />
        <AttestationFeed />
      </div>
    </div>
  );
}
