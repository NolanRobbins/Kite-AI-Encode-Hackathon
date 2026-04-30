"use client";

import { Boxes, LockKeyhole, Shield } from "lucide-react";

const rows = [
  ["Buyer sandbox", "private ceiling, independent policy"],
  ["Typed bus", "offers, counters, accept/reject only"],
  ["Seller sandbox", "private floor, independent policy"],
  ["Authority boundary", "prose cannot execute payment"],
];

export function AgentIsolationPanel({ className = "" }: { className?: string }) {
  return (
    <div className={`card-base p-4 ${className}`}>
      <div className="mb-3 flex items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Boxes size={15} className="text-[var(--color-cyan)]" />
            <h3 className="text-sm font-semibold text-[var(--color-text)]">
              Agent Isolation
            </h3>
          </div>
          <p className="mt-0.5 text-[10px] text-[var(--color-text-faint)]">
            Independent buyer and seller policies, connected by typed offers.
          </p>
        </div>
        <Shield size={15} className="text-[var(--color-deal)]" />
      </div>

      <div className="space-y-2">
        {rows.map(([label, value], index) => (
          <div key={label} className="flex items-center gap-2 rounded-md border border-[var(--color-border-subtle)] bg-[#0b0d12] px-2.5 py-2">
            <div className={`h-1.5 w-1.5 rounded-full ${
              index === 0
                ? "bg-[var(--color-buyer)]"
                : index === 2
                ? "bg-[var(--color-seller)]"
                : "bg-[var(--color-cyan)]"
            }`} />
            <div className="min-w-0 flex-1">
              <div className="text-[10px] font-mono uppercase tracking-wider text-[var(--color-text-faint)]">
                {label}
              </div>
              <div className="truncate text-[11px] text-[var(--color-text-muted)]">
                {value}
              </div>
            </div>
            {index === 3 && <LockKeyhole size={12} className="text-[var(--color-warning)]" />}
          </div>
        ))}
      </div>
    </div>
  );
}
