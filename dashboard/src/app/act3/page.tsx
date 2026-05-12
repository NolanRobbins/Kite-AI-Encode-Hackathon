"use client";

/**
 * Act 3 — side-by-side reputation-conditioned negotiation view.
 *
 * Maps directly to the demo script (`research-plan-docs/8.3-...` Act 3,
 * 2:00 – 2:25): same buyer, two sellers of identical capability but
 * different on-chain reputation. The buyer's aspiration strategy reacts
 * to the seller's rep — lower rep → more aggressive initial price and
 * slower concession → ~30% savings vs. the high-rep deal.
 *
 * Design principles:
 *  - Pure client rendering (static export compatible).
 *  - Hybrid live/scripted per project decision: tries backend first,
 *    falls back to deterministic rehearsal so demo recording is safe.
 *  - No external state library — all driven by `useAct3Compare`.
 */

import { useMemo } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowLeft, PlayCircle, Radio, TrendingDown, Award } from "lucide-react";

import {
  useAct3Compare,
  SCRIPTED_STATUS,
} from "@/lib/use-act3-compare";
import type { Act3Side } from "@/lib/api";
import { cn } from "@/lib/cn";

export default function Act3Page() {
  const { mode, isRunning, status, start, reset, error } = useAct3Compare();

  const effectiveStatus = status;

  return (
    <div className="px-8 py-10 max-w-[1400px] mx-auto">
      <div className="flex items-center gap-3 mb-6 text-sm text-[var(--color-text-muted)]">
        <Link
          href="/"
          className="hover:text-[var(--color-text)] flex items-center gap-1"
        >
          <ArrowLeft size={14} />
          Back to dashboard
        </Link>
        <span className="text-[var(--color-text-faint)]">/</span>
        <span className="text-[var(--color-text)]">Act 3 — reputation swap</span>
      </div>

      <header className="mb-8">
        <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-[var(--color-cyan)] mb-2">
          <Radio size={12} /> Wow moment #2
        </div>
        <h1 className="text-3xl font-semibold text-[var(--color-text)]">
          Reputation-conditioned negotiation
        </h1>
        <p className="text-sm text-[var(--color-text-muted)] mt-2 max-w-2xl">
          The same buyer negotiates with two sellers of identical capability
          but different on-chain reputation. Watch the strategy adapt: lower
          reputation &rarr; more aggressive opener, slower concession, and a
          measurably cheaper deal. This is the 30% savings moment from the
          demo script.
        </p>

        <div className="flex flex-wrap items-center gap-3 mt-5">
          <button
            onClick={() => start()}
            disabled={isRunning}
            className={cn(
              "inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors",
              "bg-[var(--color-cyan)] text-black hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed",
            )}
          >
            <PlayCircle size={16} />
            {isRunning ? "Running..." : "Start paired negotiations"}
          </button>
          <button
            onClick={() => start({ forceScripted: true })}
            disabled={isRunning}
            className={cn(
              "inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors",
              "border border-[var(--color-border)] text-[var(--color-text-muted)] hover:text-[var(--color-text)]",
              "disabled:opacity-50 disabled:cursor-not-allowed",
            )}
          >
            Play scripted rehearsal
          </button>
          {mode !== "idle" && (
            <button
              onClick={reset}
              className="text-sm text-[var(--color-text-faint)] hover:text-[var(--color-text)] underline"
            >
              Reset
            </button>
          )}
          <ModeBadge mode={mode} />
        </div>
        {error && (
          <div className="mt-3 text-xs text-amber-400">{error}</div>
        )}
      </header>

      <SavingsHeadline status={effectiveStatus} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <NegotiationColumn
          tone="high"
          side={effectiveStatus?.high_rep ?? null}
          placeholderLabel={SCRIPTED_STATUS.high_rep.label}
          placeholderStars={SCRIPTED_STATUS.high_rep.reputation_stars}
        />
        <NegotiationColumn
          tone="low"
          side={effectiveStatus?.low_rep ?? null}
          placeholderLabel={SCRIPTED_STATUS.low_rep.label}
          placeholderStars={SCRIPTED_STATUS.low_rep.reputation_stars}
        />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Presentational pieces
// ---------------------------------------------------------------------------

function ModeBadge({ mode }: { mode: "idle" | "live" | "scripted" }) {
  if (mode === "idle") return null;
  const styles: Record<string, string> = {
    live: "bg-emerald-500/10 text-emerald-300 border-emerald-500/40",
    scripted: "bg-amber-500/10 text-amber-300 border-amber-500/40",
  };
  const labels: Record<string, string> = {
    live: "LIVE BACKEND",
    scripted: "SCRIPTED FALLBACK",
  };
  return (
    <span
      className={cn(
        "text-[10px] font-mono uppercase tracking-wider px-2 py-1 rounded border",
        styles[mode],
      )}
    >
      {labels[mode]}
    </span>
  );
}

function SavingsHeadline({
  status,
}: {
  status: { savings_pct: number; savings_abs: number; both_complete: boolean } | null;
}) {
  const pct = status?.savings_pct ?? 0;
  const abs = status?.savings_abs ?? 0;
  const ready = status?.both_complete ?? false;

  return (
    <div
      className={cn(
        "border rounded-xl px-6 py-5 flex items-center gap-5 transition-colors",
        ready
          ? "border-[var(--color-cyan)]/40 bg-[var(--color-cyan-glow)]"
          : "border-[var(--color-border)] bg-[var(--color-card)]",
      )}
    >
      <TrendingDown
        size={36}
        className={cn(
          "shrink-0",
          ready ? "text-[var(--color-cyan)]" : "text-[var(--color-text-faint)]",
        )}
      />
      <div className="flex-1">
        <div className="text-xs font-mono uppercase tracking-wider text-[var(--color-text-muted)]">
          Savings from reputation-aware strategy
        </div>
        <div className="flex items-baseline gap-3 mt-1">
          <span
            className={cn(
              "text-4xl font-semibold tabular-nums",
              ready ? "text-[var(--color-cyan)]" : "text-[var(--color-text-faint)]",
            )}
          >
            {ready ? `${pct.toFixed(1)}%` : "—"}
          </span>
          <span className="text-sm text-[var(--color-text-muted)]">
            {ready ? `(saved $${abs.toFixed(4)} per call)` : "awaiting both deals"}
          </span>
        </div>
      </div>
    </div>
  );
}

function NegotiationColumn({
  tone,
  side,
  placeholderLabel,
  placeholderStars,
}: {
  tone: "high" | "low";
  side: Act3Side | null;
  placeholderLabel: string;
  placeholderStars: number;
}) {
  const label = side?.label || placeholderLabel;
  const stars = side?.reputation_stars ?? placeholderStars;
  const price = side?.agreed_price ?? 0;
  const rounds = side?.rounds ?? [];
  const done = side?.success ?? false;

  const accent =
    tone === "high"
      ? "border-emerald-500/30 bg-emerald-500/5"
      : "border-amber-500/30 bg-amber-500/5";
  const accentText =
    tone === "high" ? "text-emerald-300" : "text-amber-300";

  return (
    <section
      className={cn(
        "border rounded-xl p-5 flex flex-col gap-4",
        accent,
      )}
    >
      <header className="flex items-start justify-between gap-3">
        <div>
          <div className={cn("text-xs font-mono uppercase tracking-wider", accentText)}>
            {tone === "high" ? "Known agent" : "Unknown / low-rep agent"}
          </div>
          <h2 className="text-lg font-semibold text-[var(--color-text)]">
            {label}
          </h2>
          <div className="flex items-center gap-1 mt-1 text-sm text-[var(--color-text-muted)]">
            <Award size={14} className={accentText} />
            <span className="font-mono tabular-nums">
              {stars.toFixed(1)} / 5.0
            </span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-[10px] font-mono uppercase tracking-wider text-[var(--color-text-faint)]">
            Agreed price
          </div>
          <div
            className={cn(
              "text-2xl font-semibold tabular-nums",
              done ? "text-[var(--color-cyan)]" : "text-[var(--color-text-faint)]",
            )}
          >
            {done ? `$${price.toFixed(4)}` : "—"}
          </div>
          <div className="text-xs text-[var(--color-text-muted)]">
            {side?.total_rounds ? `${side.total_rounds} rounds` : "waiting"}
          </div>
        </div>
      </header>

      <RoundList rounds={rounds} />
    </section>
  );
}

function RoundList({
  rounds,
}: {
  rounds: Act3Side["rounds"];
}) {
  const shown = useMemo(() => rounds.slice(-5), [rounds]);

  if (shown.length === 0) {
    return (
      <div className="text-xs text-[var(--color-text-faint)] italic">
        No rounds yet — waiting for the agent to open.
      </div>
    );
  }

  return (
    <ol className="space-y-2">
      {shown.map((r, idx) => (
        <motion.li
          key={`${r.round}-${idx}`}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
          className="border border-[var(--color-border)] rounded-md px-3 py-2 bg-[var(--color-surface)] text-xs"
        >
          <div className="flex items-center justify-between mb-1">
            <span className="font-mono text-[var(--color-text-faint)]">
              R{r.round}
            </span>
            <span className="font-mono tabular-nums text-[var(--color-text-muted)]">
              buyer ${r.buyer_offer?.toFixed(4) ?? "—"} · seller ${" "}
              {r.seller_offer?.toFixed(4) ?? "—"}
            </span>
          </div>
          {r.buyer_nl && (
            <p className="text-[var(--color-text-muted)] leading-relaxed">
              <span className="text-emerald-400 font-medium">Buyer: </span>
              {r.buyer_nl}
            </p>
          )}
          {r.seller_nl && (
            <p className="text-[var(--color-text-muted)] leading-relaxed mt-1">
              <span className="text-amber-400 font-medium">Seller: </span>
              {r.seller_nl}
            </p>
          )}
        </motion.li>
      ))}
    </ol>
  );
}
