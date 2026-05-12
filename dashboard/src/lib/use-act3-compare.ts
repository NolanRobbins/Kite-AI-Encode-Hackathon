/**
 * Hook driving the Act 3 side-by-side compare page.
 *
 * Flow:
 * 1. Caller invokes `start()` → POSTs /api/act3/compare, which returns
 *    two `negotiation_id`s.
 * 2. We poll /api/act3/compare/{high}/{low} every 750ms. Once both
 *    sides succeed, `status.both_complete` flips true and polling
 *    stops.
 * 3. If the backend is unreachable OR the start call fails, we flip
 *    into `mode === "scripted"` and drive a deterministic rehearsal
 *    using numbers from the demo script (Act 3, 2:00–2:25):
 *       - High-rep deal: $0.10, 5 rounds, 4.8★ seller.
 *       - Low-rep deal:  $0.07, 3 rounds, 3.2★ seller.
 *       - 30% savings delta.
 *
 * Everything is client-side — works inside the Next.js static export.
 */

"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import {
  ApiError,
  api,
  type Act3CompareKickoff,
  type Act3CompareStatus,
  type Act3Side,
} from "@/lib/api";

export type Act3Mode = "idle" | "live" | "scripted";

const POLL_INTERVAL_MS = 750;
const POLL_TIMEOUT_MS = 25_000;

// Deterministic fallback numbers drawn from the demo script so the
// dashboard always has something to show during a recording even if
// the backend is offline.
export const SCRIPTED_STATUS: Act3CompareStatus = {
  high_rep: {
    negotiation_id: "neg-scripted-high",
    status: "completed",
    label: "WeatherPro (known, 4.8\u2605)",
    reputation_stars: 4.8,
    agreed_price: 0.1,
    total_rounds: 5,
    deal_hash: "0xDEADBEEFCAFE" + "00".repeat(26),
    rounds: [
      {
        round: 1,
        buyer_offer: 0.06,
        seller_offer: 0.15,
        buyer_nl:
          "Starting at $0.06 — trusted seller, happy to go fair from the open.",
        seller_nl:
          "At $0.15 you get our SLA-backed 99.9% uptime and sub-150ms p95.",
        opponent_model: { estimated_reservation: 0.09, confidence: 0.6 },
        nash_check: "pending",
      },
      {
        round: 2,
        buyer_offer: 0.072,
        seller_offer: 0.132,
        buyer_nl: "Moving to $0.072. 4.8\u2605 reputation justifies a concession.",
        seller_nl: "Meeting you partway at $0.132. Dedicated throughput allocation.",
        opponent_model: { estimated_reservation: 0.09, confidence: 0.7 },
        nash_check: "pending",
      },
      {
        round: 3,
        buyer_offer: 0.086,
        seller_offer: 0.118,
        buyer_nl: "$0.086 — your ratings say you'll honor the commitment.",
        seller_nl: "$0.118 reflects my infra cost floor.",
        opponent_model: { estimated_reservation: 0.09, confidence: 0.82 },
        nash_check: "pending",
      },
      {
        round: 4,
        buyer_offer: 0.095,
        seller_offer: 0.107,
        buyer_nl: "Near close at $0.095.",
        seller_nl: "$0.107. Nash-optimal zone confirmed.",
        opponent_model: { estimated_reservation: 0.1, confidence: 0.9 },
        nash_check: "valid",
      },
      {
        round: 5,
        buyer_offer: 0.1,
        seller_offer: 0.1,
        buyer_nl: "Agreed at $0.10.",
        seller_nl: "Deal at $0.10. Signing.",
        opponent_model: { estimated_reservation: 0.1, confidence: 0.95 },
        nash_check: "valid",
      },
    ],
    settlement: {
      settled: true,
      x402_tx_hash: "0xscripted-x402-tx-high",
      x402_network: "eip155:2368",
      attestation_tx: "0xscripted-attestation-high",
      kitescan_tx_url: "",
      pipeline_error: "",
      mock_mode: true,
    },
    success: true,
  },
  low_rep: {
    negotiation_id: "neg-scripted-low",
    status: "completed",
    label: "WeatherPro-7 (unknown, 3.2\u2605)",
    reputation_stars: 3.2,
    agreed_price: 0.07,
    total_rounds: 3,
    deal_hash: "0xBADCAFEBABE0" + "00".repeat(26),
    rounds: [
      {
        round: 1,
        buyer_offer: 0.04,
        seller_offer: 0.12,
        buyer_nl:
          "Opening at $0.04. 3.2\u2605 reputation — I price in the risk.",
        seller_nl: "Asking $0.12. Weather data at competitive rates.",
        opponent_model: { estimated_reservation: 0.06, confidence: 0.5 },
        nash_check: "pending",
      },
      {
        round: 2,
        buyer_offer: 0.055,
        seller_offer: 0.085,
        buyer_nl: "$0.055 — slow concession because I'm wary of the rep.",
        seller_nl: "$0.085. Volume commitment would help.",
        opponent_model: { estimated_reservation: 0.06, confidence: 0.7 },
        nash_check: "pending",
      },
      {
        round: 3,
        buyer_offer: 0.07,
        seller_offer: 0.07,
        buyer_nl: "Agreed at $0.07 — below the high-rep deal.",
        seller_nl: "Deal at $0.07. Signing.",
        opponent_model: { estimated_reservation: 0.07, confidence: 0.85 },
        nash_check: "valid",
      },
    ],
    settlement: {
      settled: true,
      x402_tx_hash: "0xscripted-x402-tx-low",
      x402_network: "eip155:2368",
      attestation_tx: "0xscripted-attestation-low",
      kitescan_tx_url: "",
      pipeline_error: "",
      mock_mode: true,
    },
    success: true,
  },
  both_complete: true,
  savings_abs: 0.03,
  savings_pct: 30.0,
};

function scriptedInitialStatus(): Act3CompareStatus {
  // Initial "running" state used while we animate the scripted rounds.
  const blank = (side: Act3Side, label: string): Act3Side => ({
    ...side,
    status: "negotiating",
    agreed_price: 0,
    total_rounds: 0,
    deal_hash: "",
    rounds: [],
    settlement: {},
    success: false,
    label,
  });
  return {
    high_rep: blank(SCRIPTED_STATUS.high_rep, SCRIPTED_STATUS.high_rep.label),
    low_rep: blank(SCRIPTED_STATUS.low_rep, SCRIPTED_STATUS.low_rep.label),
    both_complete: false,
    savings_abs: 0,
    savings_pct: 0,
  };
}

interface UseAct3Result {
  mode: Act3Mode;
  isRunning: boolean;
  status: Act3CompareStatus | null;
  kickoff: Act3CompareKickoff | null;
  error: string | null;
  /** Returns a promise that resolves when the compare is kicked off.
   * If `forceScripted` is true, skips the HTTP call and plays the
   * pre-recorded rehearsal. */
  start: (opts?: { forceScripted?: boolean }) => Promise<void>;
  reset: () => void;
}

export function useAct3Compare(): UseAct3Result {
  const [mode, setMode] = useState<Act3Mode>("idle");
  const [isRunning, setIsRunning] = useState(false);
  const [status, setStatus] = useState<Act3CompareStatus | null>(null);
  const [kickoff, setKickoff] = useState<Act3CompareKickoff | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollTimerRef = useRef<number | null>(null);
  const scriptedTimerRef = useRef<number | null>(null);

  const stopTimers = useCallback(() => {
    if (pollTimerRef.current !== null) {
      window.clearTimeout(pollTimerRef.current);
      pollTimerRef.current = null;
    }
    if (scriptedTimerRef.current !== null) {
      window.clearTimeout(scriptedTimerRef.current);
      scriptedTimerRef.current = null;
    }
  }, []);

  const playScripted = useCallback((reason: string | null) => {
    setMode("scripted");
    setIsRunning(true);
    setError(reason);
    setStatus(scriptedInitialStatus());

    // Roll rounds out over ~5s so the UI animates naturally.
    const allHigh = SCRIPTED_STATUS.high_rep.rounds;
    const allLow = SCRIPTED_STATUS.low_rep.rounds;
    const totalSteps = Math.max(allHigh.length, allLow.length);
    let step = 0;
    const tick = () => {
      step += 1;
      const isFinal = step >= totalSteps;
      setStatus({
        high_rep: {
          ...SCRIPTED_STATUS.high_rep,
          rounds: allHigh.slice(0, Math.min(step, allHigh.length)),
          status: isFinal ? "completed" : "negotiating",
          agreed_price: isFinal ? SCRIPTED_STATUS.high_rep.agreed_price : 0,
          total_rounds: isFinal ? SCRIPTED_STATUS.high_rep.total_rounds : 0,
          success: isFinal,
        },
        low_rep: {
          ...SCRIPTED_STATUS.low_rep,
          rounds: allLow.slice(0, Math.min(step, allLow.length)),
          status: isFinal ? "completed" : "negotiating",
          agreed_price: isFinal ? SCRIPTED_STATUS.low_rep.agreed_price : 0,
          total_rounds: isFinal ? SCRIPTED_STATUS.low_rep.total_rounds : 0,
          success: isFinal,
        },
        both_complete: isFinal,
        savings_abs: isFinal ? SCRIPTED_STATUS.savings_abs : 0,
        savings_pct: isFinal ? SCRIPTED_STATUS.savings_pct : 0,
      });
      if (!isFinal) {
        scriptedTimerRef.current = window.setTimeout(tick, 900);
      } else {
        setIsRunning(false);
      }
    };
    scriptedTimerRef.current = window.setTimeout(tick, 600);
  }, []);

  const pollUntilDone = useCallback(
    (highId: string, lowId: string) => {
      const startTime = Date.now();
      const loop = async () => {
        try {
          const next = await api.getAct3CompareStatus(highId, lowId);
          setStatus(next);
          if (next.both_complete) {
            setIsRunning(false);
            return;
          }
          if (Date.now() - startTime > POLL_TIMEOUT_MS) {
            setIsRunning(false);
            setError("Compare did not complete in time");
            return;
          }
          pollTimerRef.current = window.setTimeout(loop, POLL_INTERVAL_MS);
        } catch (err) {
          // Network / 5xx blip — retry until timeout.
          if (Date.now() - startTime > POLL_TIMEOUT_MS) {
            setIsRunning(false);
            setError(err instanceof Error ? err.message : String(err));
            return;
          }
          pollTimerRef.current = window.setTimeout(loop, POLL_INTERVAL_MS);
        }
      };
      loop();
    },
    [],
  );

  const start = useCallback(
    async (opts?: { forceScripted?: boolean }) => {
      stopTimers();
      setStatus(null);
      setKickoff(null);
      setError(null);

      if (opts?.forceScripted) {
        playScripted(null);
        return;
      }

      setMode("live");
      setIsRunning(true);
      try {
        const resp = await api.startAct3Compare({});
        setKickoff(resp);
        pollUntilDone(resp.high_rep.negotiation_id, resp.low_rep.negotiation_id);
      } catch (err) {
        const msg =
          err instanceof ApiError ? err.message : (err as Error)?.message || String(err);
        playScripted(`Backend unreachable — playing scripted fallback (${msg})`);
      }
    },
    [playScripted, pollUntilDone, stopTimers],
  );

  const reset = useCallback(() => {
    stopTimers();
    setMode("idle");
    setIsRunning(false);
    setStatus(null);
    setKickoff(null);
    setError(null);
  }, [stopTimers]);

  useEffect(() => stopTimers, [stopTimers]);

  return { mode, isRunning, status, kickoff, error, start, reset };
}
