"use client";

import { LockKeyhole, RadioTower, ShieldAlert, TimerReset } from "lucide-react";
import type { EdgeCaseStatus, SandboxPosture } from "@/lib/types";

function pretty(value?: string | number | boolean) {
  if (typeof value === "boolean") return value ? "yes" : "no";
  if (typeof value === "number") return String(value);
  return (value ?? "pending").replaceAll("_", " ");
}

export function EdgeCasePanel({
  edgeCaseStatus,
  sandbox,
  className = "",
}: {
  edgeCaseStatus?: EdgeCaseStatus;
  sandbox?: SandboxPosture;
  className?: string;
}) {
  const safeguards = [
    {
      icon: TimerReset,
      label: "Infinite Loop Guard",
      value: `${edgeCaseStatus?.round_cap ?? 7} rounds / ${edgeCaseStatus?.timeout_seconds ?? 30}s`,
    },
    {
      icon: ShieldAlert,
      label: "Deal Breakdown",
      value: pretty(edgeCaseStatus?.deadlock_policy ?? "walk_away_no_payment"),
    },
    {
      icon: RadioTower,
      label: "Streaming Prices",
      value: pretty(edgeCaseStatus?.streaming_policy ?? "round_updates_only_no_mid_round_price_mutation"),
    },
    {
      icon: LockKeyhole,
      label: "Payment Bait-and-Switch",
      value: pretty(edgeCaseStatus?.price_mismatch_policy ?? "abort_payment_on_deal_hash_or_amount_mismatch"),
    },
  ];

  return (
    <div className={`card-base p-5 ${className}`}>
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-[var(--color-text)]">
          Edge Cases & Sandbox Posture
        </h3>
        <p className="mt-0.5 text-xs text-[var(--color-text-faint)]">
          The language layer narrates. Typed protocol fields, round caps, and payment checks control execution.
        </p>
      </div>

      <div className="grid grid-cols-4 gap-3">
        {safeguards.map(({ icon: Icon, label, value }) => (
          <div key={label} className="rounded-lg border border-[var(--color-border-subtle)] bg-[#0f1117] p-3">
            <div className="mb-2 flex items-center gap-2 text-[var(--color-cyan)]">
              <Icon size={14} />
              <span className="text-[10px] uppercase tracking-wider">{label}</span>
            </div>
            <div className="text-[11px] leading-snug text-[var(--color-text-muted)]">
              {value}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 grid grid-cols-4 gap-3">
        {([
          ["LLM tools", sandbox?.llm_tool_access ?? "none"],
          ["Filesystem", sandbox?.filesystem_access ?? "none"],
          ["Network", sandbox?.network_access ?? "none"],
          ["MCP tools", sandbox?.mcp_tools_enabled ?? false],
        ] as Array<[string, string | boolean]>).map(([label, value]) => (
          <div key={label} className="rounded-lg border border-[var(--color-border-subtle)] bg-[#0f1117] p-3">
            <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-faint)]">
              {label}
            </div>
            <div className="mt-1 text-xs font-mono font-semibold text-[var(--color-text)]">
              {pretty(value)}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-[10px] leading-relaxed text-[var(--color-text-faint)]">
        {sandbox?.note ??
          "Current demo agents have no filesystem, wallet, or MCP tool access. Future MCP mode should add ERC-8004 trust gates, descriptor hashing, response scanning, and container/network isolation before enabling live tools."}
      </div>
    </div>
  );
}
