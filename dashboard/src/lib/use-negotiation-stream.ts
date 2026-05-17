"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type {
  LiveNegotiationRound,
  NegotiationResult,
  PipelineStageEvent,
  StreamMessage,
} from "@/lib/types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws/negotiate";
const MAX_BACKOFF_MS = 10_000;

function payloadNegotiationId(payload: unknown): string | undefined {
  if (!payload || typeof payload !== "object") return undefined;
  const maybeId = (payload as { negotiation_id?: unknown }).negotiation_id;
  return typeof maybeId === "string" && maybeId.length > 0 ? maybeId : undefined;
}

export function useNegotiationStream() {
  const [connected, setConnected] = useState(false);
  const [rounds, setRounds] = useState<LiveNegotiationRound[]>([]);
  const [result, setResult] = useState<NegotiationResult | null>(null);
  const [error, setError] = useState<string>("");
  const [pipelineStages, setPipelineStages] = useState<PipelineStageEvent[]>([]);
  const [activeNegotiationId, setActiveNegotiationId] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectBackoffMsRef = useRef(500);
  const activeNegotiationIdRef = useRef<string | null>(null);

  useEffect(() => {
    activeNegotiationIdRef.current = activeNegotiationId;
  }, [activeNegotiationId]);

  useEffect(() => {
    let isUnmounted = false;

    const shouldAcceptPayload = (payload: unknown) => {
      const currentNegotiationId = activeNegotiationIdRef.current;
      if (!currentNegotiationId) return true;
      const payloadId = payloadNegotiationId(payload);
      if (!payloadId) return true; // Backwards-compatible with legacy payloads.
      return payloadId === currentNegotiationId;
    };

    const scheduleReconnect = () => {
      if (isUnmounted) return;
      if (reconnectTimerRef.current) {
        window.clearTimeout(reconnectTimerRef.current);
      }
      const delayMs = reconnectBackoffMsRef.current;
      reconnectBackoffMsRef.current = Math.min(delayMs * 2, MAX_BACKOFF_MS);
      reconnectTimerRef.current = window.setTimeout(() => {
        if (!isUnmounted) {
          connect();
        }
      }, delayMs);
    };

    const connect = () => {
      if (isUnmounted) return;

      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        if (isUnmounted) return;
        reconnectBackoffMsRef.current = 500;
        setConnected(true);
        setError("");
      };

      ws.onclose = () => {
        if (isUnmounted) return;
        setConnected(false);
        scheduleReconnect();
      };

      ws.onerror = () => {
        if (isUnmounted) return;
        setError("WebSocket connection failed. Start the FastAPI backend on port 8000.");
      };

      ws.onmessage = (event) => {
        if (isUnmounted) return;
        let message: StreamMessage;
        try {
          message = JSON.parse(event.data) as StreamMessage;
        } catch {
          return;
        }

        if (message.type === "round_update") {
          if (!shouldAcceptPayload(message.data)) return;
          setRounds((prev) => [...prev, message.data as LiveNegotiationRound]);
          return;
        }

        if (message.type === "negotiation_result") {
          if (!shouldAcceptPayload(message.data)) return;
          setResult(message.data as NegotiationResult);
          return;
        }

        if (message.type === "pipeline_stage") {
          if (!shouldAcceptPayload(message.data)) return;
          setPipelineStages((prev) => [...prev, message.data as PipelineStageEvent]);
          return;
        }

        if (message.type === "error") {
          const data = message.data as { message?: string };
          setError(data.message ?? "Negotiation stream error");
        }
      };
    };

    connect();

    return () => {
      isUnmounted = true;
      if (reconnectTimerRef.current) {
        window.clearTimeout(reconnectTimerRef.current);
      }
      if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
        wsRef.current.close();
      }
    };
  }, []);

  const reset = useCallback(() => {
    setRounds([]);
    setResult(null);
    setError("");
    setPipelineStages([]);
    setActiveNegotiationId(null);
  }, []);

  return {
    connected,
    rounds,
    result,
    error,
    reset,
    pipelineStages,
    activeNegotiationId,
    setActiveNegotiationId,
  };
}
