"use client";

import { useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ReferenceArea,
  ResponsiveContainer,
  Legend,
  Dot,
} from "recharts";

interface PriceConvergenceProps {
  rounds: Array<{
    round: number;
    buyerPrice: number | null;
    sellerPrice: number | null;
  }>;
  visibleRounds: number;
  dealReached: boolean;
  finalPrice?: number;
  nashPrice?: number;
  className?: string;
}

function CustomDot(props: Record<string, unknown>) {
  const { cx, cy, index, dataKey, visibleRounds } = props as {
    cx: number;
    cy: number;
    index: number;
    dataKey: string;
    visibleRounds: number;
  };
  if (index >= visibleRounds) return null;

  const isBuyer = dataKey === "buyerPrice";
  const color = isBuyer ? "#3b82f6" : "#a855f7";

  return (
    <Dot
      cx={cx}
      cy={cy}
      r={4}
      fill={color}
      stroke="#0f1117"
      strokeWidth={2}
    />
  );
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ dataKey: string; value: number; color: string }>;
  label?: string;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#1a1d26] border border-[#2a2d3a] rounded-lg p-3 shadow-lg">
      <p className="text-xs text-[#94a3b8] mb-2 font-medium">Round {label}</p>
      {payload.map((entry) => (
        <div key={entry.dataKey} className="flex items-center gap-2 text-xs">
          <div
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-[#94a3b8]">
            {entry.dataKey === "buyerPrice" ? "Buyer" : "Seller"}:
          </span>
          <span className="font-mono font-medium text-[#e2e8f0]">
            ${entry.value.toFixed(4)}
          </span>
        </div>
      ))}
    </div>
  );
}

export function PriceConvergenceChart({
  rounds,
  visibleRounds,
  dealReached,
  finalPrice,
  nashPrice,
  className = "",
}: PriceConvergenceProps) {
  const chartData = useMemo(() => {
    return rounds.slice(0, visibleRounds).map((r) => ({
      round: r.round,
      buyerPrice: r.buyerPrice,
      sellerPrice: r.sellerPrice,
    }));
  }, [rounds, visibleRounds]);

  const dealData = useMemo(() => {
    if (!dealReached) return [];
    return [
      ...chartData,
      {
        round: rounds.length + 1,
        buyerPrice: finalPrice ?? chartData.at(-1)?.buyerPrice ?? 0,
        sellerPrice: finalPrice ?? chartData.at(-1)?.sellerPrice ?? 0,
      },
    ];
  }, [chartData, dealReached, finalPrice, rounds.length]);

  const finalData = dealReached ? dealData : chartData;

  // Calculate dynamic y-axis domain based on actual price range
  const yAxisDomain = useMemo(() => {
    if (finalData.length === 0) return [0.05, 0.15]; // fallback

    const allPrices = finalData.flatMap(d => [d.buyerPrice, d.sellerPrice].filter((p): p is number => p !== null));
    if (allPrices.length === 0) return [0.05, 0.15];

    const minPrice = Math.min(...allPrices);
    const maxPrice = Math.max(...allPrices);
    const range = maxPrice - minPrice;

    // Add 10% padding on each side, with minimum 0.02 range
    const padding = Math.max(range * 0.1, 0.01);
    return [
      Math.max(0, minPrice - padding),
      maxPrice + padding,
    ];
  }, [finalData]);

  return (
    <div className={`card-base p-5 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-[var(--color-text)]">
            Bilateral Barter Curve
          </h3>
          <p className="text-xs text-[var(--color-text-faint)] mt-0.5">
            Independent buyer and seller offers moving toward an accepted price
          </p>
        </div>
        {dealReached && (
          <div className="flex items-center gap-2 bg-[var(--color-deal-bg)] border border-[var(--color-deal-dim)] px-3 py-1.5 rounded-full">
            <div className="w-2 h-2 rounded-full bg-[var(--color-deal)] animate-pulse-slow" />
            <span className="text-xs font-mono font-medium text-[var(--color-deal)]">
              DEAL @ ${(finalPrice ?? 0).toFixed(4)}
            </span>
          </div>
        )}
      </div>

      <ResponsiveContainer width="100%" height={380}>
        <LineChart data={finalData} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
          <defs>
            <linearGradient id="buyerGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.8} />
              <stop offset="100%" stopColor="#60a5fa" stopOpacity={1} />
            </linearGradient>
            <linearGradient id="sellerGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#a855f7" stopOpacity={0.8} />
              <stop offset="100%" stopColor="#c084fc" stopOpacity={1} />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="2" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#1f2230" vertical={false} />

          {/* Nash equilibrium zone */}
          {nashPrice && (
            <ReferenceArea
              y1={Math.max(0, nashPrice * 0.95)}
              y2={nashPrice * 1.05}
              fill="#22d3ee"
              fillOpacity={0.04}
              stroke="#22d3ee"
              strokeOpacity={0.1}
              strokeDasharray="4 4"
            />
          )}

          <XAxis
            dataKey="round"
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: "#2a2d3a" }}
            label={{ value: "Round", position: "insideBottom", offset: -2, fill: "#64748b", fontSize: 10 }}
          />
          <YAxis
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: "#2a2d3a" }}
            domain={yAxisDomain}
            tickFormatter={(v: number) => `$${v.toFixed(4)}`}
            width={60}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            height={36}
            formatter={(value: string) => (
              <span className="text-xs text-[#94a3b8]">
                {value === "buyerPrice" ? "Buyer Offers" : "Seller Offers"}
              </span>
            )}
          />

          {/* Deal reference line */}
          {dealReached && (
            <ReferenceLine
              y={finalPrice ?? 0}
              stroke="#22c55e"
              strokeDasharray="6 3"
              strokeWidth={1.5}
              label={{
                value: `Deal $${(finalPrice ?? 0).toFixed(4)}`,
                position: "right",
                fill: "#22c55e",
                fontSize: 11,
              }}
            />
          )}

          <Line
            type="monotone"
            dataKey="buyerPrice"
            stroke="url(#buyerGradient)"
            strokeWidth={2.5}
            dot={(props: Record<string, unknown>) => <CustomDot key={`buyer-${(props as { index: number }).index}`} {...props} dataKey="buyerPrice" visibleRounds={dealReached ? visibleRounds + 1 : visibleRounds} />}
            activeDot={{ r: 6, fill: "#3b82f6", stroke: "#0f1117", strokeWidth: 2 }}
            filter="url(#glow)"
            animationDuration={800}
            animationEasing="ease-out"
          />
          <Line
            type="monotone"
            dataKey="sellerPrice"
            stroke="url(#sellerGradient)"
            strokeWidth={2.5}
            dot={(props: Record<string, unknown>) => <CustomDot key={`seller-${(props as { index: number }).index}`} {...props} dataKey="sellerPrice" visibleRounds={dealReached ? visibleRounds + 1 : visibleRounds} />}
            activeDot={{ r: 6, fill: "#a855f7", stroke: "#0f1117", strokeWidth: 2 }}
            filter="url(#glow)"
            animationDuration={800}
            animationEasing="ease-out"
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Legend for Nash zone */}
      <div className="flex items-center gap-4 mt-3 pt-3 border-t border-[var(--color-border-subtle)]">
        <div className="flex items-center gap-2 text-[10px] text-[var(--color-text-faint)]">
          <div className="w-6 h-3 rounded-sm bg-[#22d3ee] opacity-10 border border-[#22d3ee] border-opacity-20" />
          Nash Equilibrium Zone
        </div>
        <div className="flex items-center gap-2 text-[10px] text-[var(--color-text-faint)]">
          <div className="w-4 border-t-2 border-dashed border-[var(--color-deal)]" />
          Agreement Line
        </div>
      </div>
    </div>
  );
}
