"use client";

import { motion } from "framer-motion";
import { RECENT_DEALS } from "@/lib/mock-data";
import { ArrowRight } from "lucide-react";

function formatTimestamp(ts: string) {
  const d = new Date(ts);
  const now = new Date();
  const diff = Math.floor((now.getTime() - d.getTime()) / 60000);
  if (diff < 60) return `${diff}m ago`;
  if (diff < 1440) return `${Math.floor(diff / 60)}h ago`;
  return d.toLocaleDateString();
}

export function RecentActivity({ className = "" }: { className?: string }) {
  return (
    <div className={`card-base p-5 ${className}`}>
      <h3 className="text-sm font-semibold text-[var(--color-text)] mb-4">
        Recent Deals
      </h3>

      <div className="space-y-2">
        {RECENT_DEALS.map((deal, i) => (
          <motion.div
            key={deal.id}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: i * 0.06 }}
            className="flex items-center gap-3 bg-[#0f1117] rounded-lg px-3 py-2.5 border border-[var(--color-border-subtle)] hover:border-[var(--color-border)] transition-colors group"
          >
            {/* Deal indicator */}
            <div className="w-8 h-8 rounded-lg bg-[var(--color-deal-bg)] border border-[var(--color-deal-dim)] flex items-center justify-center flex-shrink-0">
              <span className="text-[10px] font-bold text-[var(--color-deal)]">✓</span>
            </div>

            {/* Buyer → Seller */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5 text-xs">
                <span className="text-[var(--color-buyer)] font-medium truncate">
                  {deal.buyerName}
                </span>
                <ArrowRight size={10} className="text-[var(--color-text-faint)] flex-shrink-0" />
                <span className="text-[var(--color-seller)] font-medium truncate">
                  {deal.sellerName}
                </span>
              </div>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="text-[10px] font-mono text-[var(--color-text-faint)]">
                  {deal.id}
                </span>
                <span className="text-[10px] text-[var(--color-text-faint)]">
                  {deal.rounds} rounds
                </span>
              </div>
            </div>

            {/* Price & time */}
            <div className="text-right flex-shrink-0">
              <div className="font-mono text-xs font-semibold text-[var(--color-deal)]">
                ${deal.agreedPrice.toFixed(4)}
              </div>
              <div className="text-[10px] text-[var(--color-text-faint)]">
                {formatTimestamp(deal.timestamp)}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
