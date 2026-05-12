/**
 * React hook that subscribes to the NegotiatorGrid backend WebSocket
 * (`/ws/negotiate`) and exposes typed event streams for the UI.
 *
 * Backend event schema (see negotiatorgrid/api/websocket.py +
 * api/pipeline.py):
 *
 *   { type: "round_update",         data: NegotiationRoundRecord }
 *   { type: "negotiation_result",   data: NegotiationResultRecord }
 *   { type: "settlement_started",   data: { negotiation_id, agreed_price, atomic_amount, seller_wallet } }
 *   { type: "settlement_completed", data: { success, tx_hash, network, error } }
 *   { type: "attestation_started",  data: { negotiation_id, deal_hash, mock_mode } }
 *   { type: "attestation_completed", data: { deal_hash, attestation_tx, kitescan_url, mock_mode, duration_seconds, error, status?, rejection_reason? } }
 *   { type: "payment_refused",      data: { negotiation_id, deal_hash, message, seller_agent_id, expected_atomic, requested_atomic, rejection_reason } }
 *   { type: "error",                data: { message } }
 *
 * Design notes:
 *
 * - Exponential-backoff reconnect (1s → 2s → 4s → 8s → max 15s) because
 *   the backend on Railway may cold-start the first few seconds after
 *   a deploy. Giving up silently would leave the "Live" dot red forever.
 *
 * - The hook keeps the last ~50 events in a bounded ring buffer so the
 *   dashboard can render a scrolling event log without unbounded memory.
 *
 * - A single WebSocket is shared across the whole React tree by keying
 *   the hook on ``url``. Callers can opt out of auto-connect by passing
 *   ``{ enabled: false }`` — useful for SSG dry builds and tests.
 */

"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import {
  API_BASE_URL,
  type NegotiationResultRecord,
  type NegotiationRoundRecord,
} from "@/lib/api";

// ---------------------------------------------------------------------------
// Event types
// ---------------------------------------------------------------------------

export type NegotiationWsEvent =
  | { type: "round_update"; data: NegotiationRoundRecord }
  | { type: "negotiation_result"; data: NegotiationResultRecord }
  | {
      type: "settlement_started";
      data: {
        negotiation_id: string;
        agreed_price: number;
        atomic_amount: number;
        seller_wallet: string;
      };
    }
  | {
      type: "settlement_completed";
      data: {
        success: boolean;
        tx_hash: string;
        network: string;
        error: string;
      };
    }
  | {
      type: "attestation_started";
      data: {
        negotiation_id: string;
        deal_hash: string;
        mock_mode: boolean;
      };
    }
  | {
      type: "attestation_completed";
      data: {
        deal_hash: string;
        attestation_tx: string;
        kitescan_url: string;
        mock_mode: boolean;
        duration_seconds: number;
        error: string;
        status?: string;
        rejection_reason?: string;
      };
    }
  | {
      type: "payment_refused";
      data: {
        negotiation_id: string;
        deal_hash: string;
        message: string;
        seller_agent_id: number;
        expected_atomic: number;
        requested_atomic: number;
        rejection_reason: string;
      };
    }
  | { type: "error"; data: { message: string } };

export type ConnectionStatus =
  | "idle"
  | "connecting"
  | "open"
  | "closed"
  | "error";

export interface UseNegotiationSocketOptions {
  /** When false, the hook never opens a socket (useful for SSG builds). */
  enabled?: boolean;
  /** Override the default `ws(s)://<API_BASE_URL>/ws/negotiate`. */
  url?: string;
  /** Called for every event before it's stored in the ring buffer. */
  onEvent?: (event: NegotiationWsEvent) => void;
  /** Ring-buffer size (default 50). */
  historyLimit?: number;
}

export interface UseNegotiationSocketReturn {
  status: ConnectionStatus;
  /** Last ~historyLimit events, newest last. */
  events: NegotiationWsEvent[];
  /** Most recent round_update, or null if none yet this session. */
  lastRound: NegotiationRoundRecord | null;
  /** Most recent negotiation_result. */
  lastResult: NegotiationResultRecord | null;
  /** Most recent settlement_completed data. */
  settlement: Extract<NegotiationWsEvent, { type: "settlement_completed" }>["data"] | null;
  /** Most recent attestation_completed data. */
  attestation: Extract<NegotiationWsEvent, { type: "attestation_completed" }>["data"] | null;
  /** Act 5 — buyer refused inflated x402 terms (hash mismatch). */
  paymentRefused: Extract<NegotiationWsEvent, { type: "payment_refused" }>["data"] | null;
  /** Force reconnect now (e.g. after a user retry click). */
  reconnect: () => void;
  /** Clear the event buffer without reconnecting. */
  clear: () => void;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function defaultWsUrl(): string {
  // Convert http(s) base URL into ws(s) and append the negotiation path.
  // We do this at call time (not module eval) so tests can override
  // process.env before importing.
  const base = API_BASE_URL.replace(/^http/, "ws");
  return `${base}/ws/negotiate`;
}

function nextBackoff(prevMs: number): number {
  const doubled = Math.max(prevMs * 2, 1000);
  return Math.min(doubled, 15_000);
}

function isKnownEventType(t: unknown): t is NegotiationWsEvent["type"] {
  return (
    t === "round_update" ||
    t === "negotiation_result" ||
    t === "settlement_started" ||
    t === "settlement_completed" ||
    t === "attestation_started" ||
    t === "attestation_completed" ||
    t === "payment_refused" ||
    t === "error"
  );
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useNegotiationSocket(
  options: UseNegotiationSocketOptions = {},
): UseNegotiationSocketReturn {
  const { enabled = true, url, onEvent, historyLimit = 50 } = options;

  const [status, setStatus] = useState<ConnectionStatus>("idle");
  const [events, setEvents] = useState<NegotiationWsEvent[]>([]);
  const [lastRound, setLastRound] = useState<NegotiationRoundRecord | null>(null);
  const [lastResult, setLastResult] = useState<NegotiationResultRecord | null>(null);
  const [settlement, setSettlement] =
    useState<UseNegotiationSocketReturn["settlement"]>(null);
  const [attestation, setAttestation] =
    useState<UseNegotiationSocketReturn["attestation"]>(null);
  const [paymentRefused, setPaymentRefused] =
    useState<UseNegotiationSocketReturn["paymentRefused"]>(null);

  // These refs let us tear down and reconnect without re-running the effect.
  const wsRef = useRef<WebSocket | null>(null);
  const backoffRef = useRef(500);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);
  const onEventRef = useRef(onEvent);
  useEffect(() => {
    onEventRef.current = onEvent;
  }, [onEvent]);

  const pushEvent = useCallback(
    (evt: NegotiationWsEvent) => {
      onEventRef.current?.(evt);
      setEvents((prev) => {
        const next = prev.length >= historyLimit ? prev.slice(1) : prev.slice();
        next.push(evt);
        return next;
      });
      switch (evt.type) {
        case "round_update":
          setLastRound(evt.data);
          break;
        case "negotiation_result":
          setLastResult(evt.data);
          break;
        case "settlement_completed":
          setSettlement(evt.data);
          break;
        case "attestation_completed":
          setAttestation(evt.data);
          break;
        case "payment_refused":
          setPaymentRefused(evt.data);
          break;
      }
    },
    [historyLimit],
  );

  // We break the connect/reconnect circular reference by stashing the
  // latest `connect` impl in a ref. This avoids the temporal-dead-zone
  // bug of calling `scheduleReconnect` inside `connect` while also
  // depending on `connect` inside `scheduleReconnect`.
  const connectRef = useRef<() => void>(() => undefined);

  const scheduleReconnect = useCallback(() => {
    if (!mountedRef.current || !enabled) return;
    if (timerRef.current) clearTimeout(timerRef.current);
    const delay = backoffRef.current;
    backoffRef.current = nextBackoff(delay);
    timerRef.current = setTimeout(() => {
      if (!mountedRef.current) return;
      connectRef.current();
    }, delay);
  }, [enabled]);

  const connect = useCallback(() => {
    if (!enabled || typeof window === "undefined") return;

    if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
      try {
        wsRef.current.close();
      } catch {
        /* already closed */
      }
    }

    const wsUrl = url ?? defaultWsUrl();
    let ws: WebSocket;
    try {
      ws = new WebSocket(wsUrl);
    } catch (err) {
      console.warn("[useNegotiationSocket] construct failed", err);
      setStatus("error");
      scheduleReconnect();
      return;
    }

    wsRef.current = ws;
    setStatus("connecting");

    ws.onopen = () => {
      if (!mountedRef.current) return;
      backoffRef.current = 500;
      setStatus("open");
    };

    ws.onmessage = (event) => {
      if (!mountedRef.current) return;
      let parsed: unknown;
      try {
        parsed = JSON.parse(typeof event.data === "string" ? event.data : "");
      } catch {
        return;
      }
      if (
        !parsed ||
        typeof parsed !== "object" ||
        !("type" in parsed) ||
        !("data" in parsed)
      )
        return;
      const p = parsed as { type: unknown; data: unknown };
      if (!isKnownEventType(p.type)) return;
      pushEvent({ type: p.type, data: p.data } as NegotiationWsEvent);
    };

    ws.onerror = () => {
      if (!mountedRef.current) return;
      setStatus("error");
    };

    ws.onclose = () => {
      if (!mountedRef.current) return;
      setStatus("closed");
      scheduleReconnect();
    };
  }, [enabled, url, pushEvent, scheduleReconnect]);

  // Keep the ref pointed at the latest `connect` impl. Must happen in
  // an effect — mutating refs during render is disallowed by the new
  // react-hooks/refs rule.
  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  const reconnect = useCallback(() => {
    backoffRef.current = 500;
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    connect();
  }, [connect]);

  const clear = useCallback(() => {
    setEvents([]);
    setLastRound(null);
    setLastResult(null);
    setSettlement(null);
    setAttestation(null);
    setPaymentRefused(null);
  }, []);

  // `connect()` transitively calls `setStatus()` via WebSocket event
  // handlers — which is the canonical "subscribe to external system"
  // shape the React docs recommend. Lint can't see through the function
  // boundary, so we silence the cascading-renders warning here.
  useEffect(() => {
    mountedRef.current = true;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (enabled) connect();
    return () => {
      mountedRef.current = false;
      if (timerRef.current) clearTimeout(timerRef.current);
      if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
        try {
          wsRef.current.close();
        } catch {
          /* noop */
        }
      }
      wsRef.current = null;
    };
  }, [enabled, connect]);

  return {
    status,
    events,
    lastRound,
    lastResult,
    settlement,
    attestation,
    paymentRefused,
    reconnect,
    clear,
  };
}
