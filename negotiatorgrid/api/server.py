"""FastAPI application for NegotiatorGrid."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from negotiatorgrid.api.agent_card import AGENT_CARD
from negotiatorgrid.api.act3_compare import router as act3_router
from negotiatorgrid.api.routes import router as api_router
from negotiatorgrid.api.websocket import router as ws_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application startup / shutdown lifecycle."""
    logger.info("NegotiatorGrid API starting up")
    yield
    logger.info("NegotiatorGrid API shutting down")


app = FastAPI(
    title="NegotiatorGrid API",
    description=(
        "Agent-to-agent price negotiation protocol on Kite AI — "
        "bilateral bargaining with game-theoretic strategies, "
        "x402 settlement, and on-chain attestation"
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(api_router)
app.include_router(act3_router)
app.include_router(ws_router)


@app.get("/", include_in_schema=False)
async def root() -> dict[str, object]:
    """Browser-friendly index - this host is a JSON API, not a web page."""
    return {
        "service": "negotiatorgrid-api",
        "message": "No HTML UI here - open /docs for Swagger, or use the dashboard.",
        "links": {
            "health": "/api/health",
            "openapi": "/openapi.json",
            "docs": "/docs",
            "redoc": "/redoc",
            "agent_card": "/.well-known/agent-card.json",
            "negotiate": "POST /api/negotiate",
            "websocket": "ws://127.0.0.1:8000/ws/negotiate",
        },
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    """Silence browser favicon requests (no asset bundled)."""
    return Response(status_code=204)


# Agent card discovery endpoint
@app.get("/.well-known/agent-card.json")
async def agent_card() -> JSONResponse:
    """Serve the A2A AgentCard for agent discovery."""
    return JSONResponse(content=AGENT_CARD)
