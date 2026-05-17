"use client";

import { motion } from "framer-motion";
import type { ModelRuntimeMetrics, ReasoningSummary } from "@/lib/types";

interface TimelineProps {
  rounds: Array<{
    round: number;
    buyerPrice: number | null;
    sellerPrice: number | null;
    buyerMessage: string;
    sellerMessage: string;
    buyerStance?: string;
    sellerStance?: string;
    buyerReasoning?: ReasoningSummary;
    sellerReasoning?: ReasoningSummary;
    nashCheck?: string;
    nashDeviationPct?: number;
    runtime?: ModelRuntimeMetrics;
  }>;
  visibleRounds: number;
  dealReached: boolean;
  finalPrice?: number;
  negotiationId?: string;
  className?: string;
}

function ReasoningMini({ reasoning }: { reasoning?: ReasoningSummary }) {
  if (!reasoning) return null;
  return (
    <div className="mt-2 grid gap-1 border-t border-white/5 pt-2">
      {[reasoning.goal, reasoning.signal, reasoning.action, reasoning.risk]
        .filter(Boolean)
        .map((line) => (
          <div key={line} className="text-[10px] leading-snug text-[var(--color-text-faint)]">
            {line}
          </div>
        ))}
    </div>
  );
}

export function NegotiationTimeline({
  rounds,
  visibleRounds,
  dealReached,
  finalPrice,
  negotiationId,
  className = "",
}: TimelineProps) {
  const displayedRounds = rounds.slice(0, visibleRounds);

  return (
    <div className={`card-base p-5 ${className}`}>
      <h3 className="mb-4 text-sm font-semibold text-[var(--color-text)]">Negotiation Timeline</h3>

      <div className="max-h-[420px] space-y-3 overflow-y-auto pr-2">
        {displayedRounds.map((round, i) => (
          <motion.div
            key={round.round}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: i * 0.05 }}
          >
            <div className="mb-2 flex items-center gap-2">
              <div className="text-[10px] font-mono uppercase tracking-widest text-[var(--color-text-faint)]">
                Round {round.round}
              </div>
              {round.nashCheck ? (
                <span
                  className={`rounded-full border px-1.5 py-0.5 text-[9px] font-mono ${
                    round.nashCheck === "PASS"
                      ? "border-[var(--color-deal-dim)] bg-[var(--color-deal-bg)] text-[var(--color-deal)]"
                      : "border-yellow-900 bg-yellow-950/30 text-[var(--color-warning)]"
                  }`}
                >
                  {round.nashCheck}
                  {typeof round.nashDeviationPct === "number"
                    ? ` ${(round.nashDeviationPct * 100).toFixed(1)}%`
                    : ""}
                </span>
              ) : null}
              {round.runtime ? (
                <span className="text-[9px] font-mono text-[var(--color-text-faint)]">
                  calls={round.runtime.model_calls ?? 0} | fallback=
                  {round.runtime.fallback_messages ?? 0}
                </span>
              ) : null}
              <div className="h-px flex-1 bg-[var(--color-border-subtle)]" />
            </div>

            <div className="mb-2 flex gap-2">
              <div className="mt-0.5 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full border border-[var(--color-buyer-dim)] bg-[var(--color-buyer-bg)]">
                <span className="text-[9px] font-bold text-[var(--color-buyer)]">B</span>
              </div>
              <div className="max-w-[85%] flex-1">
                <div className="rounded-lg rounded-tl-sm border border-[rgba(59,130,246,0.15)] bg-[var(--color-buyer-bg)] px-3 py-2">
                  <div className="mb-1 flex items-center gap-2">
                    <span className="font-mono text-xs font-semibold text-[var(--color-buyer)]">
                      ${round.buyerPrice?.toFixed(4) ?? "----"}
                    </span>
                    {round.buyerStance ? (
                      <span className="text-[9px] uppercase tracking-wider text-[var(--color-buyer)]">
                        {round.buyerStance}
                      </span>
                    ) : null}
                  </div>
                  <p className="text-xs leading-relaxed text-[var(--color-text-muted)]">
                    {round.buyerMessage}
                  </p>
                  <ReasoningMini reasoning={round.buyerReasoning} />
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2">
              <div className="flex max-w-[85%] flex-1 justify-end">
                <div className="rounded-lg rounded-tr-sm border border-[rgba(168,85,247,0.15)] bg-[var(--color-seller-bg)] px-3 py-2">
                  <div className="mb-1 flex items-center justify-end gap-2">
                    {round.sellerStance ? (
                      <span className="text-[9px] uppercase tracking-wider text-[var(--color-seller)]">
                        {round.sellerStance}
                      </span>
                    ) : null}
                    <span className="font-mono text-xs font-semibold text-[var(--color-seller)]">
                      ${round.sellerPrice?.toFixed(4) ?? "----"}
                    </span>
                  </div>
                  <p className="text-right text-xs leading-relaxed text-[var(--color-text-muted)]">
                    {round.sellerMessage}
                  </p>
                  <ReasoningMini reasoning={round.sellerReasoning} />
                </div>
              </div>
              <div className="mt-0.5 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full border border-[var(--color-seller-dim)] bg-[var(--color-seller-bg)]">
                <span className="text-[9px] font-bold text-[var(--color-seller)]">S</span>
              </div>
            </div>
          </motion.div>
        ))}

        {dealReached ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="mt-4"
          >
            <div className="rounded-lg border border-[var(--color-deal-dim)] bg-[var(--color-deal-bg)] p-4 text-center">
              <div className="mx-auto mb-2 flex h-8 w-8 items-center justify-center rounded-full bg-[var(--color-deal)] bg-opacity-20">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path
                    d="M3 8L6.5 11.5L13 5"
                    stroke="#22c55e"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
              <div className="mb-1 text-xs font-semibold uppercase tracking-wider text-[var(--color-deal)]">
                Deal Agreed
              </div>
              <div className="font-mono text-lg font-bold text-[var(--color-deal)]">
                ${(finalPrice ?? 0).toFixed(4)} USDT
              </div>
              <div className="mt-1 text-[10px] text-[var(--color-text-faint)]">
                Recorded on Kite AI | {displayedRounds.length} rounds
                {negotiationId ? ` | ${negotiationId}` : ""}
              </div>
            </div>
          </motion.div>
        ) : null}
      </div>
    </div>
  );
}
