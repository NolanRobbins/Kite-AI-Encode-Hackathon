"use client";

import { motion } from "framer-motion";
import type { NegotiationRound } from "@/lib/mock-data";
import { DEAL_PRICE } from "@/lib/mock-data";

interface TimelineProps {
  rounds: NegotiationRound[];
  visibleRounds: number;
  dealReached: boolean;
  className?: string;
}

export function NegotiationTimeline({
  rounds,
  visibleRounds,
  dealReached,
  className = "",
}: TimelineProps) {
  return (
    <div className={`card-base p-5 ${className}`}>
      <h3 className="text-sm font-semibold text-[var(--color-text)] mb-4">
        Negotiation Timeline
      </h3>

      <div className="space-y-3 max-h-[420px] overflow-y-auto pr-2">
        {rounds.slice(0, visibleRounds).map((round, i) => (
          <motion.div
            key={round.round}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: i * 0.05 }}
          >
            {/* Round label */}
            <div className="flex items-center gap-2 mb-2">
              <div className="text-[10px] font-mono text-[var(--color-text-faint)] uppercase tracking-widest">
                Round {round.round}
              </div>
              <div className="flex-1 h-px bg-[var(--color-border-subtle)]" />
            </div>

            {/* Buyer bubble — left aligned */}
            <div className="flex gap-2 mb-2">
              <div className="w-6 h-6 rounded-full bg-[var(--color-buyer-bg)] border border-[var(--color-buyer-dim)] flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-[9px] font-bold text-[var(--color-buyer)]">B</span>
              </div>
              <div className="flex-1 max-w-[85%]">
                <div className="bg-[var(--color-buyer-bg)] border border-[rgba(59,130,246,0.15)] rounded-lg rounded-tl-sm px-3 py-2">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-xs font-semibold text-[var(--color-buyer)]">
                      ${round.buyerPrice.toFixed(4)}
                    </span>
                  </div>
                  <p className="text-xs text-[var(--color-text-muted)] leading-relaxed">
                    {round.buyerMessage}
                  </p>
                </div>
              </div>
            </div>

            {/* Seller bubble — right aligned */}
            <div className="flex gap-2 justify-end">
              <div className="flex-1 max-w-[85%] flex justify-end">
                <div className="bg-[var(--color-seller-bg)] border border-[rgba(168,85,247,0.15)] rounded-lg rounded-tr-sm px-3 py-2">
                  <div className="flex items-center gap-2 mb-1 justify-end">
                    <span className="font-mono text-xs font-semibold text-[var(--color-seller)]">
                      ${round.sellerPrice.toFixed(4)}
                    </span>
                  </div>
                  <p className="text-xs text-[var(--color-text-muted)] leading-relaxed text-right">
                    {round.sellerMessage}
                  </p>
                </div>
              </div>
              <div className="w-6 h-6 rounded-full bg-[var(--color-seller-bg)] border border-[var(--color-seller-dim)] flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-[9px] font-bold text-[var(--color-seller)]">S</span>
              </div>
            </div>
          </motion.div>
        ))}

        {/* Deal agreement */}
        {dealReached && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="mt-4"
          >
            <div className="bg-[var(--color-deal-bg)] border border-[var(--color-deal-dim)] rounded-lg p-4 text-center">
              <div className="w-8 h-8 mx-auto mb-2 rounded-full bg-[var(--color-deal)] bg-opacity-20 flex items-center justify-center">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M3 8L6.5 11.5L13 5" stroke="#22c55e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <div className="text-xs font-semibold text-[var(--color-deal)] uppercase tracking-wider mb-1">
                Deal Agreed
              </div>
              <div className="font-mono text-lg font-bold text-[var(--color-deal)]">
                ${DEAL_PRICE.toFixed(4)} USDT
              </div>
              <div className="text-[10px] text-[var(--color-text-faint)] mt-1">
                Recorded on Kite AI • 6 rounds • Jan 18, 2025 14:32 UTC
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
