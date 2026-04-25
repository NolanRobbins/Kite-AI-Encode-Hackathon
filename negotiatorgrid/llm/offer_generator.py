"""Natural-language offer wrapping powered by OpenAI GPT-4o-mini.

Generates human-readable negotiation messages for each protocol action
(offer, counter-offer, acceptance, rejection).  Falls back to template
strings when the OpenAI API is unavailable.
"""

from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

# Best-effort import — OpenAI may not be configured / available.
try:
    from openai import OpenAI

    _HAS_OPENAI = True
except ImportError:
    _HAS_OPENAI = False


_SYSTEM_PROMPT = (
    "You are a professional AI negotiation agent. "
    "Speak concisely and assertively. Be polite but firm. "
    "Never reveal your reservation price or internal strategy. "
    "Keep responses under 2 sentences."
)


class OfferGenerator:
    """Wraps OpenAI GPT-4o-mini to generate negotiation dialogue.

    Parameters
    ----------
    api_key:
        OpenAI API key.  If empty, template fallback is used.
    model:
        Model identifier (default ``gpt-4o-mini``).
    max_tokens:
        Hard cap per completion (default 256).
    """

    def __init__(
        self,
        api_key: str = "",
        model: str = "gpt-4o-mini",
        max_tokens: int = 256,
        model_mode: str = "policy_only",
        provider: str = "template",
        latency_budget_ms: int = 1200,
    ) -> None:
        self.model_mode = model_mode
        self.provider = provider
        self.model = model
        self.max_tokens = max_tokens
        self.latency_budget_ms = latency_budget_ms
        self.call_count = 0
        self.total_latency_ms = 0.0
        self.fallback_count = 0
        self._client: Any = None
        if api_key and _HAS_OPENAI and model_mode in {"llm", "reasoning_llm"}:
            self._client = OpenAI(api_key=api_key)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def generate_buyer_offer(
        self,
        round_num: int,
        price: float,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Generate a natural-language buyer offer message."""
        prompt = (
            f"Round {round_num}: As a buyer, propose a price of ${price:.2f}. "
            f"Context: {_fmt_context(context)}. "
            "Justify the price briefly based on market conditions."
        )
        return self._complete(prompt, fallback=f"I'd like to offer ${price:.2f} for this service.")

    def generate_seller_counter(
        self,
        round_num: int,
        price: float,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Generate a natural-language seller counter-offer message."""
        prompt = (
            f"Round {round_num}: As a seller, counter with a price of ${price:.2f}. "
            f"Context: {_fmt_context(context)}. "
            "Explain why your service is worth this price."
        )
        return self._complete(
            prompt,
            fallback=f"I appreciate your offer, but I need at least ${price:.2f} for this service.",
        )

    def generate_acceptance_message(
        self,
        agreed_price: float,
        rounds: int,
    ) -> str:
        """Generate an acceptance message for a completed deal."""
        prompt = (
            f"The negotiation concluded after {rounds} rounds at ${agreed_price:.2f}. "
            "Write a brief, positive acceptance message."
        )
        return self._complete(
            prompt,
            fallback=f"Deal! We've agreed on ${agreed_price:.2f} after {rounds} rounds.",
        )

    def generate_rejection_message(self, reason: str = "") -> str:
        """Generate a rejection / walk-away message."""
        prompt = (
            f"The negotiation failed. Reason: {reason or 'no agreement reached'}. "
            "Write a brief, professional rejection message."
        )
        return self._complete(
            prompt,
            fallback=f"Unfortunately we couldn't reach an agreement. {reason}".strip(),
        )

    # ------------------------------------------------------------------
    # Internal LLM call with graceful fallback
    # ------------------------------------------------------------------

    def _complete(self, user_prompt: str, fallback: str) -> str:
        if self._client is None:
            self.fallback_count += 1
            return fallback
        started = time.perf_counter()
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=0.7,
            )
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            self.call_count += 1
            self.total_latency_ms += elapsed_ms
            text = resp.choices[0].message.content
            if text:
                return text.strip()
            self.fallback_count += 1
            return fallback
        except Exception:
            self.fallback_count += 1
            logger.warning("OpenAI call failed, using template fallback", exc_info=True)
            return fallback

    def runtime_metrics(self) -> dict[str, Any]:
        """Return model/runtime telemetry safe to show in the dashboard."""
        avg_latency = self.total_latency_ms / self.call_count if self.call_count else 0.0
        return {
            "model_mode": self.model_mode,
            "provider": self.provider,
            "model": self.model,
            "model_calls": self.call_count,
            "fallback_messages": self.fallback_count,
            "avg_model_latency_ms": round(avg_latency, 2),
            "total_model_latency_ms": round(self.total_latency_ms, 2),
            "latency_budget_ms": self.latency_budget_ms,
            "runtime_note": _runtime_note(self.model_mode),
        }


def _fmt_context(ctx: dict[str, Any] | None) -> str:
    if not ctx:
        return "none"
    parts = [f"{k}={v}" for k, v in ctx.items()]
    return ", ".join(parts)


def _runtime_note(model_mode: str) -> str:
    if model_mode == "reasoning_llm":
        return "Reasoning advisor mode can improve strategy critique but increases round latency."
    if model_mode == "llm":
        return "LLM narrator mode enriches dialogue while typed protocol fields remain authoritative."
    if model_mode == "slm":
        return "SLM narrator mode uses lightweight/template language around deterministic policy decisions."
    return "Policy-only mode uses deterministic negotiation state and template language."
