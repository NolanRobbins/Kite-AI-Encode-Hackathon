"use client";

import { Scale, ShieldCheck, TriangleAlert } from "lucide-react";
import { PassportSessionFitCard } from "@/components/passport-session-fit-card";
import type { DealMetrics, PassportStatus } from "@/lib/types";

function money(value?: number) {
  return `$${(value ?? 0).toFixed(4)}`;
}

function pct(value?: number) {
  return `${((value ?? 0) * 100).toFixed(1)}%`;
}

export function DealMetricsPanel({
  metrics,
  passportStatus = "stubbed",
  className = "",
}: {
  metrics?: DealMetrics;
  passportStatus?: PassportStatus;
  className?: string;
}) {
  const socialRisk = metrics?.social_risk ?? "watch";
  const riskColor =
    socialRisk === "high"
      ? "text-[var(--color-error)]"
      : socialRisk === "watch"
      ? "text-[var(--color-warning)]"
      : "text-[var(--color-deal)]";

  return (
    <div className={`card-base p-5 ${className}`}>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-[var(--color-text)]">
            Deal Quality Metrics
          </h3>
          <p className="mt-0.5 text-xs text-[var(--color-text-faint)]">
            Nash is a benchmark; objective mode determines how the agents use it.
          </p>
        </div>
        <Scale size={16} className="text-[var(--color-cyan)]" />
      </div>

      <div className="grid grid-cols-4 gap-3">
        {[
          ["Buyer Surplus", money(metrics?.buyer_surplus)],
          ["Seller Surplus", money(metrics?.seller_surplus)],
          ["Seller Discount", money(metrics?.seller_discount)],
          ["Buyer Movement", money(metrics?.buyer_movement)],
          ["Nash Price", money(metrics?.nash_price)],
          ["Nash Drift", pct(metrics?.nash_deviation_pct)],
          ["Objective", (metrics?.objective_mode ?? "fairness_guardrail").replaceAll("_", " ")],
          ["Social Risk", socialRisk],
        ].map(([label, value]) => (
          <div key={label} className="rounded-lg bg-[#0f1117] p-3 border border-[var(--color-border-subtle)]">
            <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-faint)]">
              {label}
            </div>
            <div className={`mt-1 text-sm font-mono font-semibold ${label === "Social Risk" ? riskColor : "text-[var(--color-text)]"}`}>
              {value}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 flex items-start gap-2 rounded-lg border border-[var(--color-border-subtle)] bg-[#0f1117] p-3">
        {passportStatus === "disabled" ? (
          <TriangleAlert size={14} className="mt-0.5 text-[var(--color-warning)]" />
        ) : (
          <ShieldCheck size={14} className="mt-0.5 text-[var(--color-deal)]" />
        )}
        <div>
          <div className="text-xs font-medium text-[var(--color-text)]">
            Kite Passport: {passportStatus}
          </div>
          <div className="text-[10px] text-[var(--color-text-faint)]">
            Passport controls whether the agent can spend; NegotiatorGrid decides whether the deal is worth paying for.
          </div>
        </div>
      </div>

      <PassportSessionFitCard metrics={metrics} passportStatus={passportStatus} className="mt-3" />

      <div className="mt-3 grid grid-cols-3 gap-3">
        <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[#0f1117] p-3">
          <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-faint)]">
            Model Mode
          </div>
          <div className="mt-1 text-sm font-mono font-semibold text-[var(--color-cyan)]">
            {(metrics?.model_runtime?.model_mode ?? "policy_only").replaceAll("_", " ")}
          </div>
        </div>
        <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[#0f1117] p-3">
          <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-faint)]">
            Model Calls
          </div>
          <div className="mt-1 text-sm font-mono font-semibold text-[var(--color-text)]">
            {metrics?.model_runtime?.model_calls ?? 0}
          </div>
        </div>
        <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[#0f1117] p-3">
          <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-faint)]">
            Avg Latency
          </div>
          <div className="mt-1 text-sm font-mono font-semibold text-[var(--color-text)]">
            {(metrics?.model_runtime?.avg_model_latency_ms ?? 0).toFixed(0)}ms
          </div>
        </div>
      </div>
      <div className="mt-2 text-[10px] text-[var(--color-text-faint)]">
        {metrics?.model_runtime?.runtime_note ?? "Policy-only mode keeps the demo deterministic and fast."}
      </div>
      <div className="mt-2 grid grid-cols-2 gap-3 text-[10px]">
        <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[#0f1117] p-2.5">
          <div className="uppercase tracking-wider text-[var(--color-text-faint)]">Buyer Runtime</div>
          <div className="mt-1 font-mono text-[var(--color-buyer)]">
            {metrics?.model_runtime?.buyer_runtime?.provider ?? "template"} /{" "}
            {metrics?.model_runtime?.buyer_runtime?.model ?? "template"}
          </div>
        </div>
        <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[#0f1117] p-2.5">
          <div className="uppercase tracking-wider text-[var(--color-text-faint)]">Seller Runtime</div>
          <div className="mt-1 font-mono text-[var(--color-seller)]">
            {metrics?.model_runtime?.seller_runtime?.provider ?? "template"} /{" "}
            {metrics?.model_runtime?.seller_runtime?.model ?? "template"}
          </div>
        </div>
      </div>
    </div>
  );
}
