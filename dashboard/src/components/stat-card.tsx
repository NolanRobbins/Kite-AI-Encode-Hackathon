"use client";

import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string;
  icon: LucideIcon;
  accent?: string;
  subtext?: string;
}

export function StatCard({ label, value, icon: Icon, accent = "var(--color-cyan)", subtext }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="card-base p-5 flex flex-col gap-3 relative overflow-hidden group"
    >
      {/* Subtle glow top border */}
      <div
        className="absolute top-0 left-0 right-0 h-[1px]"
        style={{ background: `linear-gradient(90deg, transparent, ${accent}, transparent)`, opacity: 0.4 }}
      />

      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-[var(--color-text-faint)] uppercase tracking-wider">
          {label}
        </span>
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: `color-mix(in srgb, ${accent} 12%, transparent)` }}
        >
          <Icon size={16} style={{ color: accent }} />
        </div>
      </div>

      <div className="flex items-baseline gap-2">
        <span className="text-2xl font-semibold tracking-tight font-mono" style={{ color: accent }}>
          {value}
        </span>
        {subtext && (
          <span className="text-xs text-[var(--color-text-faint)]">{subtext}</span>
        )}
      </div>
    </motion.div>
  );
}
