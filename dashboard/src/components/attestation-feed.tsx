"use client";

import { motion } from "framer-motion";
import { ExternalLink, Copy } from "lucide-react";
import { ATTESTATION_FEED } from "@/lib/mock-data";
import { useState } from "react";

function formatTime(ts: string) {
  const d = new Date(ts);
  return d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false });
}

function truncateHash(hash: string, chars = 8) {
  return `${hash.slice(0, chars)}...${hash.slice(-6)}`;
}

export function AttestationFeed({ className = "" }: { className?: string }) {
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  const handleCopy = (text: string, idx: number) => {
    navigator.clipboard.writeText(text).catch(() => {});
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 1500);
  };

  return (
    <div className={`card-base p-5 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-[var(--color-text)]">
          Attestation Feed
        </h3>
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-deal)] animate-pulse-slow" />
          <span className="text-[10px] text-[var(--color-text-faint)]">Live</span>
        </div>
      </div>

      <div className="space-y-2">
        {ATTESTATION_FEED.map((entry, i) => (
          <motion.div
            key={entry.attestationId}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: i * 0.08 }}
            className="bg-[#0f1117] rounded-lg p-3 border border-[var(--color-border-subtle)] hover:border-[var(--color-border)] transition-colors"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono text-[var(--color-cyan)] bg-[var(--color-cyan-glow)] px-1.5 py-0.5 rounded">
                  {entry.attestationId}
                </span>
                <span className="text-[10px] text-[var(--color-text-faint)]">
                  {formatTime(entry.timestamp)}
                </span>
              </div>
              <span className="font-mono text-xs font-semibold text-[var(--color-deal)]">
                ${entry.price.toFixed(4)}
              </span>
            </div>

            <div className="flex items-center gap-3 text-[10px]">
              <div className="flex items-center gap-1">
                <span className="text-[var(--color-buyer)]">●</span>
                <span className="text-[var(--color-text-faint)] font-mono">{entry.buyerId}</span>
              </div>
              <span className="text-[var(--color-text-faint)]">↔</span>
              <div className="flex items-center gap-1">
                <span className="text-[var(--color-seller)]">●</span>
                <span className="text-[var(--color-text-faint)] font-mono">{entry.sellerId}</span>
              </div>
              <span className="text-[var(--color-text-faint)]">
                {entry.rounds} rounds
              </span>
            </div>

            <div className="flex items-center gap-2 mt-2 pt-2 border-t border-[var(--color-border-subtle)]">
              <span className="text-[10px] text-[var(--color-text-faint)]">Tx:</span>
              <span className="text-[10px] font-mono text-[var(--color-text-muted)]">
                {truncateHash(entry.txHash, 10)}
              </span>
              <button
                onClick={() => handleCopy(entry.txHash, i)}
                className="text-[var(--color-text-faint)] hover:text-[var(--color-cyan)] transition-colors"
                title="Copy tx hash"
              >
                <Copy size={10} />
              </button>
              {copiedIdx === i && (
                <span className="text-[9px] text-[var(--color-cyan)]">Copied</span>
              )}
              <a
                href={`https://testnet.kitescan.ai/tx/${entry.txHash}`}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-auto text-[var(--color-text-faint)] hover:text-[var(--color-cyan)] transition-colors"
                title="View on KiteScan"
              >
                <ExternalLink size={10} />
              </a>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
