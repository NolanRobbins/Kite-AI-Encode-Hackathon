"""WebSocket endpoint for live negotiation streaming."""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()


class NegotiationBroadcaster:
    """Manages WebSocket connections and broadcasts negotiation events."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)
        logger.info("WebSocket client connected (%d total)", len(self._connections))

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)
        logger.info("WebSocket client disconnected (%d remaining)", len(self._connections))

    @property
    def client_count(self) -> int:
        return len(self._connections)

    async def broadcast_round(self, round_data: dict[str, Any]) -> None:
        """Send a round update to all connected clients."""
        message = json.dumps({"type": "round_update", "data": round_data})
        await self._send_all(message)

    async def broadcast_result(self, result: dict[str, Any]) -> None:
        """Send the final negotiation result to all connected clients."""
        message = json.dumps({"type": "negotiation_result", "data": result})
        await self._send_all(message)

    async def broadcast_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Send an arbitrary event to all connected clients."""
        message = json.dumps({"type": event_type, "data": data})
        await self._send_all(message)

    async def _send_all(self, message: str) -> None:
        disconnected: list[WebSocket] = []
        for ws in self._connections:
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)


# Module-level singleton
broadcaster = NegotiationBroadcaster()


@router.websocket("/ws/negotiate")
async def ws_negotiate(websocket: WebSocket) -> None:
    """WebSocket endpoint that streams negotiation events to dashboard clients."""
    await broadcaster.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                logger.debug("WS received: %s", msg.get("type", "unknown"))
            except json.JSONDecodeError:
                await websocket.send_text(
                    json.dumps({"type": "error", "data": {"message": "Invalid JSON"}})
                )
    except WebSocketDisconnect:
        broadcaster.disconnect(websocket)
