/**
 * Poll /api/deals every 5s and expose a typed deal array.
 *
 * Falls back silently to the caller's `fallback` argument whenever the
 * backend is unreachable or returns an empty list — this way the demo
 * dashboard still looks populated when the FastAPI process is offline.
 *
 * The `triggerId` parameter lets a parent component force an immediate
 * refetch after it knows a new deal is imminent (e.g. right after
 * `POST /api/negotiate` returns). When `triggerId` changes, the hook
 * kicks off a short fast-poll sequence (1s, 2s, 4s) so the UI lights
 * up within seconds of settlement, without waiting for the next 5s tick.
 */

"use client";

import { useEffect, useRef, useState } from "react";

import { api, type DealRecord } from "@/lib/api";

const POLL_INTERVAL_MS = 5_000;
const FAST_POLL_DELAYS_MS = [1_000, 2_000, 4_000];

export interface UseDealsOptions {
  /** Bailout value used when the backend is offline or returns []. */
  fallback?: DealRecord[];
  /** Maximum deals returned (newest first). Default 8. */
  limit?: number;
  /** Changing this restarts a fast-poll burst. */
  triggerId?: string | null;
}

export interface UseDealsReturn {
  deals: DealRecord[];
  isLiveBackend: boolean;
  lastError: string | null;
}

export function useDeals(options: UseDealsOptions = {}): UseDealsReturn {
  const { fallback = [], limit = 8, triggerId = null } = options;
  const [deals, setDeals] = useState<DealRecord[]>([]);
  const [isLiveBackend, setIsLiveBackend] = useState(false);
  const [lastError, setLastError] = useState<string | null>(null);

  const mountedRef = useRef(true);
  const abortRef = useRef<AbortController | null>(null);
  const fastTimersRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  const fetchOnce = async () => {
    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    try {
      const list = await api.listDeals(ctrl.signal);
      if (!mountedRef.current) return;
      const sorted = [...list].sort((a, b) => b.timestamp - a.timestamp);
      setDeals(sorted.slice(0, limit));
      setIsLiveBackend(true);
      setLastError(null);
    } catch (err) {
      if (!mountedRef.current) return;
      setIsLiveBackend(false);
      setLastError((err as Error).message);
    }
  };

  // Mount: start baseline polling loop.
  useEffect(() => {
    mountedRef.current = true;
    fetchOnce();
    const interval = setInterval(fetchOnce, POLL_INTERVAL_MS);
    return () => {
      mountedRef.current = false;
      clearInterval(interval);
      abortRef.current?.abort();
      fastTimersRef.current.forEach(clearTimeout);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [limit]);

  // Trigger change: kick off a fast-poll burst.
  useEffect(() => {
    if (!triggerId) return;
    fastTimersRef.current.forEach(clearTimeout);
    fastTimersRef.current = FAST_POLL_DELAYS_MS.map((delay) =>
      setTimeout(fetchOnce, delay),
    );
    return () => {
      fastTimersRef.current.forEach(clearTimeout);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [triggerId]);

  // Fall back to the caller's mock list when backend is offline OR returned nothing.
  const effective = deals.length > 0 ? deals : isLiveBackend ? [] : fallback;
  return { deals: effective, isLiveBackend, lastError };
}
