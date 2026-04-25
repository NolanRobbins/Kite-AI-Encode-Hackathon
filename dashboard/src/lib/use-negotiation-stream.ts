"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { LiveNegotiationRound, NegotiationResult, StreamMessage } from "@/lib/types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws/negotiate";

export function useNegotiationStream() {
  const [connected, setConnected] = useState(false);
  const [rounds, setRounds] = useState<LiveNegotiationRound[]>([]);
  const [result, setResult] = useState<NegotiationResult | null>(null);
  const [error, setError] = useState<string>("");
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      setError("");
    };
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setError("WebSocket connection failed. Start the FastAPI backend on port 8000.");
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data) as StreamMessage;
      if (message.type === "round_update") {
        setRounds((prev) => [...prev, message.data as LiveNegotiationRound]);
      }
      if (message.type === "negotiation_result") {
        setResult(message.data as NegotiationResult);
      }
      if (message.type === "error") {
        const data = message.data as { message?: string };
        setError(data.message ?? "Negotiation stream error");
      }
    };

    return () => ws.close();
  }, []);

  const reset = useCallback(() => {
    setRounds([]);
    setResult(null);
    setError("");
  }, []);

  return { connected, rounds, result, error, reset };
}
