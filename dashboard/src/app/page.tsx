"use client";

import { useState, useCallback, useRef } from "react";
import { motion } from "framer-motion";
import { Activity, Handshake, DollarSign, BarChart3, Zap } from "lucide-react";
import { StatCard } from "@/components/stat-card";
import { PriceConvergenceChart } from "@/components/price-convergence";
import { NegotiationTimeline } from "@/components/negotiation-timeline";
import { AgentCard } from "@/components/agent-card";
import { AttestationFeed } from "@/components/attestation-feed";
import { RecentActivity } from "@/components/recent-activity";
import {
  NEGOTIATION_ROUNDS,
  BUYER_AGENT,
  SELLER_AGENT,
  STATS,
} from "@/lib/mock-data";

export default function DashboardPage() {
  const [visibleRounds, setVisibleRounds] = useState(6);
  const [dealReached, setDealReached] = useState(true);
  const [isNegotiating, setIsNegotiating] = useState(false);
  const [stats, setStats] = useState(STATS);
  const timerRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  const startNegotiation = useCallback(() => {
    if (isNegotiating) return;

    // Clear any existing timers
    timerRef.current.forEach(clearTimeout);
    timerRef.current = [];

    // Reset
    setIsNegotiating(true);
    setVisibleRounds(0);
    setDealReached(false);

    // Animate rounds appearing one by one
    NEGOTIATION_ROUNDS.forEach((_, i) => {
      const timer = setTimeout(() => {
        setVisibleRounds(i + 1);
      }, (i + 1) * 1200);
      timerRef.current.push(timer);
    });

    // Deal reached after all rounds
    const dealTimer = setTimeout(() => {
      setDealReached(true);
      setIsNegotiating(false);
      setStats((prev) => ({
        totalNegotiations: prev.totalNegotiations + 1,
        totalDeals: prev.totalDeals + 1,
        totalVolume: parseFloat((prev.totalVolume + 0.1034).toFixed(4)),
        avgRounds: parseFloat(
          (((prev.avgRounds * prev.totalDeals) + 6) / (prev.totalDeals + 1)).toFixed(1)
        ),
      }));
    }, (NEGOTIATION_ROUNDS.length + 1) * 1200);
    timerRef.current.push(dealTimer);
  }, [isNegotiating]);

  return (
    <div className="p-6 space-y-6 max-w-[1280px]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">
            Dashboard
          </h1>
          <p className="text-xs text-[var(--color-text-faint)] mt-0.5">
            Agent-to-agent price negotiation protocol on Kite AI
          </p>
        </div>

        {/* Start Negotiation CTA */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={startNegotiation}
          disabled={isNegotiating}
          className={`
            flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium text-sm
            transition-all duration-200
            ${
              isNegotiating
                ? "bg-[var(--color-cyan-dim)] text-[var(--color-text-muted)] cursor-wait"
                : "bg-[var(--color-cyan)] text-[#0f1117] hover:shadow-[0_0_20px_rgba(34,211,238,0.3)] glow-cyan"
            }
          `}
          data-testid="button-start-negotiation"
        >
          <Zap size={16} />
          {isNegotiating ? "Negotiating..." : "Start Negotiation"}
        </motion.button>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard
          label="Total Negotiations"
          value={stats.totalNegotiations.toString()}
          icon={Activity}
          accent="var(--color-cyan)"
        />
        <StatCard
          label="Deals Settled"
          value={stats.totalDeals.toString()}
          icon={Handshake}
          accent="var(--color-deal)"
        />
        <StatCard
          label="Total Volume"
          value={`$${stats.totalVolume.toFixed(2)}`}
          icon={DollarSign}
          accent="var(--color-buyer)"
          subtext="USDT"
        />
        <StatCard
          label="Avg Rounds"
          value={stats.avgRounds.toFixed(1)}
          icon={BarChart3}
          accent="var(--color-seller)"
          subtext="per deal"
        />
      </div>

      {/* Hero chart + Timeline */}
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
      <div id="agents" className="grid grid-cols-2 gap-4">
        <AgentCard agent={BUYER_AGENT} delay={0.1} />
        <AgentCard agent={SELLER_AGENT} delay={0.2} />
      </div>

      {/* Bottom row: Recent + Attestations */}
      <div id="deals" className="grid grid-cols-[1fr_1fr] gap-4">
        <RecentActivity />
        <AttestationFeed />
      </div>
    </div>
  );
}
