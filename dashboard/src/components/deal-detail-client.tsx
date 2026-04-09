"use client";

import { useState, useCallback, useRef } from "react";
import { motion } from "framer-motion";
import { ArrowLeft, Zap, ExternalLink, Shield, CheckCircle } from "lucide-react";
import Link from "next/link";
import { PriceConvergenceChart } from "@/components/price-convergence";
import { NegotiationTimeline } from "@/components/negotiation-timeline";
import { AgentCard } from "@/components/agent-card";
import {
  NEGOTIATION_ROUNDS,
  BUYER_AGENT,
  SELLER_AGENT,
  DEAL_PRICE,
} from "@/lib/mock-data";

const CONFIDENCE_DATA = [
  { round: 1, buyer: 0.35, seller: 0.40 },
  { round: 2, buyer: 0.42, seller: 0.45 },
  { round: 3, buyer: 0.55, seller: 0.52 },
  { round: 4, buyer: 0.68, seller: 0.65 },
  { round: 5, buyer: 0.82, seller: 0.78 },
  { round: 6, buyer: 0.94, seller: 0.91 },
];

const NASH_CHECKS = [
  { round: 1, withinBounds: true, deviation: 0.0 },
  { round: 2, withinBounds: true, deviation: 0.002 },
  { round: 3, withinBounds: true, deviation: 0.004 },
  { round: 4, withinBounds: true, deviation: 0.003 },
  { round: 5, withinBounds: true, deviation: 0.001 },
  { round: 6, withinBounds: true, deviation: 0.0 },
];

export default function DealDetailClient() {
  const [visibleRounds, setVisibleRounds] = useState(6);
  const [dealReached, setDealReached] = useState(true);
  const [isReplaying, setIsReplaying] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  const replayNegotiation = useCallback(() => {
    if (isReplaying) return;
    timerRef.current.forEach(clearTimeout);
    timerRef.current = [];
    setIsReplaying(true);
    setVisibleRounds(0);
    setDealReached(false);

    NEGOTIATION_ROUNDS.forEach((_, i) => {
      const timer = setTimeout(() => setVisibleRounds(i + 1), (i + 1) * 1000);
      timerRef.current.push(timer);
    });

    const dealTimer = setTimeout(() => {
      setDealReached(true);
      setIsReplaying(false);
    }, (NEGOTIATION_ROUNDS.length + 1) * 1000);
    timerRef.current.push(dealTimer);
  }, [isReplaying]);

  return (
    <div className="p-6 space-y-6 max-w-[1280px]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="w-8 h-8 rounded-lg bg-[var(--color-card)] border border-[var(--color-border)] flex items-center justify-center text-[var(--color-text-muted)] hover:text-[var(--color-cyan)] hover:border-[var(--color-cyan-dim)] transition-colors"
          >
            <ArrowLeft size={16} />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-semibold tracking-tight">
                Negotiation #047
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[var(--color-deal-bg)] border border-[var(--color-deal-dim)] text-[var(--color-deal)]">
                SETTLED
              </span>
            </div>
            <p className="text-xs text-[var(--color-text-faint)] mt-0.5 font-mono">
              0x7a3f8b2c...e91cd4a7 • Jan 18, 2025 14:32 UTC
            </p>
          </div>
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={replayNegotiation}
          disabled={isReplaying}
          className={`
            flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all
            ${isReplaying
              ? "bg-[var(--color-cyan-dim)] text-[var(--color-text-muted)] cursor-wait"
              : "bg-[var(--color-card)] border border-[var(--color-border)] text-[var(--color-cyan)] hover:border-[var(--color-cyan-dim)]"
            }
          `}
          data-testid="button-replay"
        >
          <Zap size={14} />
          {isReplaying ? "Replaying..." : "Replay"}
        </motion.button>
      </div>

      {/* Chart + Timeline */}
      <div className="grid grid-cols-[1fr_380px] gap-4">
        <PriceConvergenceChart
          rounds={NEGOTIATION_ROUNDS}
          visibleRounds={visibleRounds}
          dealReached={dealReached}
        />
        <NegotiationTimeline
          rounds={NEGOTIATION_ROUNDS}
          visibleRounds={visibleRounds}
          dealReached={dealReached}
        />
      </div>

      {/* Agent Cards */}
      <div className="grid grid-cols-2 gap-4">
        <AgentCard agent={BUYER_AGENT} delay={0.1} />
        <AgentCard agent={SELLER_AGENT} delay={0.2} />
      </div>

      {/* Bottom row: Confidence + Nash + Attestation */}
      <div className="grid grid-cols-3 gap-4">
        {/* Model Confidence */}
        <div className="card-base p-5">
          <h3 className="text-sm font-semibold text-[var(--color-text)] mb-3">
            Model Confidence
          </h3>
          <div className="space-y-2">
            {CONFIDENCE_DATA.slice(0, visibleRounds).map((c) => (
              <div key={c.round} className="flex items-center gap-3">
                <span className="text-[10px] font-mono text-[var(--color-text-faint)] w-6">
                  R{c.round}
                </span>
                <div className="flex-1 flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-[#1f2230] rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${c.buyer * 100}%` }}
                      transition={{ duration: 0.5 }}
                      className="h-full bg-[var(--color-buyer)] rounded-full"
                    />
                  </div>
                  <span className="text-[10px] font-mono text-[var(--color-buyer)] w-8">
                    {(c.buyer * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="flex-1 flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-[#1f2230] rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${c.seller * 100}%` }}
                      transition={{ duration: 0.5 }}
                      className="h-full bg-[var(--color-seller)] rounded-full"
                    />
                  </div>
                  <span className="text-[10px] font-mono text-[var(--color-seller)] w-8">
                    {(c.seller * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Nash Guardrail Checks */}
        <div className="card-base p-5">
          <h3 className="text-sm font-semibold text-[var(--color-text)] mb-3">
            Nash Guardrail Checks
          </h3>
          <div className="space-y-2">
            {NASH_CHECKS.slice(0, visibleRounds).map((check) => (
              <motion.div
                key={check.round}
                initial={{ opacity: 0, x: -4 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center gap-3 bg-[#0f1117] rounded-lg px-3 py-2"
              >
                <CheckCircle size={14} className="text-[var(--color-deal)] flex-shrink-0" />
                <span className="text-[10px] font-mono text-[var(--color-text-faint)]">
                  Round {check.round}
                </span>
                <span className="text-[10px] text-[var(--color-deal)]">
                  Within bounds
                </span>
                <span className="ml-auto text-[10px] font-mono text-[var(--color-text-faint)]">
                  Δ {check.deviation.toFixed(3)}
                </span>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Attestation Detail */}
        <div className="card-base p-5">
          <h3 className="text-sm font-semibold text-[var(--color-text)] mb-3">
            On-Chain Attestation
          </h3>
          <div className="space-y-3">
            <div>
              <div className="text-[10px] text-[var(--color-text-faint)] uppercase tracking-wider mb-1">
                Deal Hash
              </div>
              <div className="text-xs font-mono text-[var(--color-text-muted)] bg-[#0f1117] rounded px-2 py-1.5">
                0x7a3f8b2c...e91cd4a7
              </div>
            </div>
            <div>
              <div className="text-[10px] text-[var(--color-text-faint)] uppercase tracking-wider mb-1">
                Agreed Price
              </div>
              <div className="text-lg font-mono font-bold text-[var(--color-deal)]">
                ${DEAL_PRICE.toFixed(4)} USDT
              </div>
            </div>
            <div>
              <div className="text-[10px] text-[var(--color-text-faint)] uppercase tracking-wider mb-1">
                Tx Hash
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-[var(--color-text-muted)] bg-[#0f1117] rounded px-2 py-1.5 flex-1 truncate">
                  0xabc123def456...789
                </span>
                <a
                  href="https://testnet.kitescan.ai/tx/0xabc123def456789"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[var(--color-cyan)] hover:text-[var(--color-text)]"
                >
                  <ExternalLink size={12} />
                </a>
              </div>
            </div>
            <div className="flex items-center gap-2 pt-2 border-t border-[var(--color-border-subtle)]">
              <Shield size={14} className="text-[var(--color-deal)]" />
              <span className="text-xs text-[var(--color-deal)]">
                Verified on Kite AI Testnet
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
