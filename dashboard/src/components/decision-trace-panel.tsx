"use client";

import { BrainCircuit } from "lucide-react";
import type { LiveNegotiationRound, ReasoningSummary } from "@/lib/types";

function TraceBlock({
  label,
  accent,
  reasoning,
  runtime,
}: {
  label: string;
  accent: string;
  reasoning?: ReasoningSummary;
  runtime?: { provider?: string; model?: string; model_calls?: number; fallback_messages?: number };
}) {
  const rows = [
    ["Goal", reasoning?.goal],
    ["Signal", reasoning?.signal],
    ["Action", reasoning?.action],
    ["Risk", reasoning?.risk],
  ].filter(([, value]) => Boolean(value));

  return (
    <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[#0f1117] p-3">
      <div className="mb-2 flex items-center gap-2">
        <div className="h-2 w-2 rounded-full" style={{ backgroundColor: accent }} />
        <span className="text-xs font-semibold text-[var(--color-text)]">{label}</span>
      </div>
      <div className="mb-2 text-[10px] text-[var(--color-text-faint)]">
        {runtime?.provider ?? "template"} / {runtime?.model ?? "template"} | calls={runtime?.model_calls ?? 0} | fallback={runtime?.fallback_messages ?? 0}
      </div>
      <div className="space-y-1.5">
        {rows.map(([key, value]) => (
          <div key={key} className="text-[10px] leading-snug">
            <span className="font-mono uppercase tracking-wider text-[var(--color-text-faint)]">
              {key}:
            </span>{" "}
            <span className="text-[var(--color-text-muted)]">{value}</span>
          </div>
        ))}
        {rows.length === 0 && (
          <div className="text-[10px] text-[var(--color-text-faint)]">
            Waiting for this agent to make an offer.
          </div>
        )}
      </div>
    </div>
  );
}

export function DecisionTracePanel({
  latestRound,
  connected,
  className = "",
}: {
  latestRound?: LiveNegotiationRound;
  connected: boolean;
  className?: string;
}) {
  return (
    <div className={`card-base p-5 ${className}`}>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-[var(--color-text)]">
            Structured Decision Trace
          </h3>
          <p className="mt-0.5 text-xs text-[var(--color-text-faint)]">
            Concise summaries for auditability, not hidden chain-of-thought.
          </p>
        </div>
        <div className="flex items-center gap-1.5 text-[10px] text-[var(--color-text-faint)]">
          <BrainCircuit size={14} />
          {connected ? "streaming" : "offline"}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <TraceBlock
          label="Buyer Agent"
          accent="#3b82f6"
          reasoning={latestRound?.buyer_reasoning}
          runtime={latestRound?.runtime?.buyer_runtime as { provider?: string; model?: string; model_calls?: number; fallback_messages?: number } | undefined}
        />
        <TraceBlock
          label="Seller Agent"
          accent="#a855f7"
          reasoning={latestRound?.seller_reasoning}
          runtime={latestRound?.runtime?.seller_runtime as { provider?: string; model?: string; model_calls?: number; fallback_messages?: number } | undefined}
        />
      </div>
    </div>
  );
}
