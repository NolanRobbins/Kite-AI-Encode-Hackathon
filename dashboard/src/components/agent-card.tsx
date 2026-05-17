"use client";

import { motion } from "framer-motion";
import { Copy, Star, Shield } from "lucide-react";
import type { Agent } from "@/lib/mock-data";
import { useState } from "react";

interface AgentCardProps {
  agent: Agent;
  gridEnabled?: boolean;
  tendency?: string;
  objectiveMode?: string;
  providerLabel?: string;
  modelLabel?: string;
  calls?: number;
  fallbacks?: number;
  delay?: number;
}

export function AgentCard({
  agent,
  gridEnabled = true,
  tendency = "balanced",
  objectiveMode = "fairness_guardrail",
  providerLabel = "template",
  modelLabel = "template",
  calls = 0,
  fallbacks = 0,
  delay = 0,
}: AgentCardProps) {
  const [copied, setCopied] = useState(false);
  const isBuyer = agent.role === "buyer";
  const accent = isBuyer ? "var(--color-buyer)" : "var(--color-seller)";
  const accentBg = isBuyer ? "var(--color-buyer-bg)" : "var(--color-seller-bg)";
  const accentDim = isBuyer ? "var(--color-buyer-dim)" : "var(--color-seller-dim)";

  const truncatedWallet = `${agent.walletAddress.slice(0, 6)}...${agent.walletAddress.slice(-4)}`;

  const handleCopy = () => {
    navigator.clipboard.writeText(agent.walletAddress).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const fullStars = Math.floor(agent.reputation);
  const hasHalf = agent.reputation - fullStars >= 0.3;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: [0.16, 1, 0.3, 1] }}
      className="card-base p-5 flex-1 relative overflow-hidden"
    >
      {/* Top accent line */}
      <div
        className="absolute top-0 left-0 right-0 h-[1px]"
        style={{ background: `linear-gradient(90deg, transparent, ${accent}, transparent)`, opacity: 0.4 }}
      />

      {/* Header */}
      <div className="flex items-start gap-3 mb-4">
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold"
          style={{ backgroundColor: accentBg, color: accent, border: `1px solid ${accentDim}` }}
        >
          {agent.avatar}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-[var(--color-text)] truncate">
              {agent.name}
            </span>
            <span
              className="text-[9px] font-mono px-1.5 py-0.5 rounded-full uppercase tracking-wider"
              style={{ backgroundColor: accentBg, color: accent, border: `1px solid ${accentDim}` }}
            >
              {agent.role}
            </span>
          </div>
          <div className="text-[10px] font-mono text-[var(--color-text-faint)] mt-0.5">
            {agent.id}
          </div>
        </div>
      </div>

      {/* Wallet */}
      <div className="flex items-center gap-2 mb-3 bg-[#0f1117] rounded-lg px-3 py-2">
        <span className="text-xs font-mono text-[var(--color-text-muted)]">
          {truncatedWallet}
        </span>
        <button
          onClick={handleCopy}
          className="ml-auto text-[var(--color-text-faint)] hover:text-[var(--color-cyan)] transition-colors"
          title="Copy address"
        >
          <Copy size={12} />
        </button>
        {copied && (
          <span className="text-[10px] text-[var(--color-cyan)]">Copied!</span>
        )}
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <div className="text-[10px] text-[var(--color-text-faint)] uppercase tracking-wider mb-1">
            Reputation
          </div>
          <div className="flex items-center gap-1">
            {Array.from({ length: 5 }, (_, i) => (
              <Star
                key={i}
                size={12}
                className={
                  i < fullStars
                    ? "text-yellow-400 fill-yellow-400"
                    : i === fullStars && hasHalf
                    ? "text-yellow-400 fill-yellow-400 opacity-50"
                    : "text-[var(--color-border)]"
                }
              />
            ))}
            <span className="text-xs font-mono text-[var(--color-text-muted)] ml-1">
              {agent.reputation}/5.0
            </span>
          </div>
        </div>
        <div>
          <div className="text-[10px] text-[var(--color-text-faint)] uppercase tracking-wider mb-1">
            Deals
          </div>
          <div className="text-sm font-mono font-semibold text-[var(--color-text)]">
            {agent.dealCount}
          </div>
        </div>
        <div className="col-span-2">
          <div className="text-[10px] text-[var(--color-text-faint)] uppercase tracking-wider mb-1">
            Strategy
          </div>
          <div className="flex items-center gap-1.5">
            <Shield size={12} style={{ color: accent }} />
            <span className="text-xs text-[var(--color-text-muted)]">
              {gridEnabled ? "NegotiatorGrid" : "Baseline"} · {tendency}
            </span>
          </div>
          <div className="mt-1 text-[10px] text-[var(--color-text-faint)]">
            Objective: {objectiveMode.replaceAll("_", " ")}
          </div>
        </div>
        <div className="col-span-2 rounded-lg border border-[var(--color-border-subtle)] bg-[#0b0d12] px-2.5 py-2">
          <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-faint)]">
            Runtime
          </div>
          <div className="mt-1 text-[11px] font-mono text-[var(--color-text-muted)]">
            {providerLabel} / {modelLabel}
          </div>
          <div className="mt-1 text-[10px] text-[var(--color-text-faint)]">
            calls={calls} | fallbacks={fallbacks}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
