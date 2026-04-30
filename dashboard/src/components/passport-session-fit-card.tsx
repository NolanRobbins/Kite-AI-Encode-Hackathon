"use client";

import { ShieldCheck, TriangleAlert } from "lucide-react";
import type { DealMetrics, PassportSessionFit, PassportStatus } from "@/lib/types";

function money(value?: number) {
  return `$${(value ?? 0).toFixed(4)}`;
}

function getDefaultSessionFit(metrics?: DealMetrics, passportStatus?: PassportStatus): PassportSessionFit {
  return {
    mode: passportStatus === "ready" ? "live" : "mock",
    status: passportStatus === "disabled" ? "pending" : "pass",
    negotiated_price: metrics?.nash_price ?? 0.1034,
    remaining_budget: 4.25,
    per_payment_cap: 0.25,
    merchant: "WeatherPro-Service",
    payee: "0x2096...1d2cE",
    asset: "USDT",
    ttl_seconds: 1320,
    reason: "Negotiated amount fits the active demo Session policy.",
  };
}

export function PassportSessionFitCard({
  metrics,
  passportStatus = "stubbed",
  compact = false,
  className = "",
}: {
  metrics?: DealMetrics;
  passportStatus?: PassportStatus;
  compact?: boolean;
  className?: string;
}) {
  const sessionFit = metrics?.passport_session_fit ?? getDefaultSessionFit(metrics, passportStatus);
  const status = sessionFit.status ?? "pending";
  const statusColor =
    status === "fail"
      ? "text-[var(--color-error)]"
      : status === "pending"
      ? "text-[var(--color-warning)]"
      : "text-[var(--color-deal)]";
  const ttlMinutes = Math.max(0, Math.floor((sessionFit.ttl_seconds ?? 0) / 60));
  const items = [
    ["Negotiated", money(sessionFit.negotiated_price)],
    ["Budget Left", money(sessionFit.remaining_budget)],
    ["Per-Pay Cap", money(sessionFit.per_payment_cap)],
    ["Asset", sessionFit.asset ?? "USDT"],
    ["Merchant", sessionFit.merchant ?? "Unknown"],
    ["Payee", sessionFit.payee ?? "Unresolved"],
    ["TTL", `${ttlMinutes}m`],
    ["Reason", sessionFit.reason ?? "Awaiting Passport Session policy."],
  ];

  return (
    <div className={`card-base p-4 ${className}`}>
      <div className="mb-3 flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck size={15} className="text-[var(--color-deal)]" />
            <h3 className="text-sm font-semibold text-[var(--color-text)]">
              Passport Session Fit
            </h3>
          </div>
          <p className="mt-0.5 text-[10px] text-[var(--color-text-faint)]">
            {sessionFit.mode === "live" ? "Passport MCP live" : "Passport-compatible mock"}
          </p>
        </div>
        <div className={`rounded-full border border-[var(--color-border)] px-2 py-1 text-[10px] font-mono uppercase ${statusColor}`}>
          {status}
        </div>
      </div>

      <div className={`grid ${compact ? "grid-cols-2" : "grid-cols-4"} gap-2`}>
        {items.slice(0, compact ? 6 : items.length).map(([label, value]) => (
          <div key={label} className="min-w-0 rounded-md border border-[var(--color-border-subtle)] bg-[#0b0d12] p-2">
            <div className="text-[9px] uppercase tracking-wider text-[var(--color-text-faint)]">
              {label}
            </div>
            <div className="mt-1 truncate text-[11px] font-mono font-semibold text-[var(--color-text)]" title={value}>
              {value}
            </div>
          </div>
        ))}
      </div>

      {status === "fail" && (
        <div className="mt-3 flex items-start gap-2 rounded-md border border-red-900/60 bg-red-950/20 p-2 text-[10px] text-[var(--color-error)]">
          <TriangleAlert size={13} className="mt-0.5 shrink-0" />
          Blocked before Passport authorization.
        </div>
      )}
    </div>
  );
}
