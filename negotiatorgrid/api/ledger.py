"""In-memory negotiation and deal ledger for the demo API host.

Production deployments would replace this with a persistence adapter; the
negotiation engine in ``negotiatorgrid/`` stays independent of this module.
"""

from __future__ import annotations

import threading
from typing import Any


def _address_matches_deal(deal: dict[str, Any], address: str) -> bool:
    """True if *address* refers to the buyer or seller (agent id or wallet)."""
    raw = address.strip()
    low = raw.lower()
    if raw in (deal.get("buyer_agent", ""), deal.get("seller_agent", "")):
        return True
    for key in ("buyer_wallet", "seller_wallet"):
        w = (deal.get(key) or "").strip()
        if w and w.lower() == low:
            return True
    return False


class NegotiationLedger:
    """Single process, in-memory store for negotiations, deals, and counters."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._negotiations: dict[str, dict[str, Any]] = {}
        self._deals: dict[str, dict[str, Any]] = {}
        self._stats: dict[str, int | float] = {
            "total_negotiations": 0,
            "total_deals": 0,
            "total_rounds": 0,
            "total_volume": 0.0,
        }

    def create_submitted(
        self,
        negotiation_id: str,
        *,
        buyer_config: dict[str, Any],
        seller_config: dict[str, Any],
        params: dict[str, Any],
        created_at: float,
    ) -> None:
        with self._lock:
            self._negotiations[negotiation_id] = {
                "negotiation_id": negotiation_id,
                "status": "submitted",
                "buyer_config": buyer_config,
                "seller_config": seller_config,
                "params": params,
                "created_at": created_at,
                "result": None,
            }
            self._stats["total_negotiations"] += 1

    def mark_negotiating(self, negotiation_id: str) -> None:
        with self._lock:
            self._negotiations[negotiation_id]["status"] = "negotiating"

    def record_completed_run(
        self,
        negotiation_id: str,
        *,
        success: bool,
        result_dict: dict[str, Any],
        total_rounds: int,
        deal: dict[str, Any] | None,
    ) -> None:
        """Persist engine outcome: negotiation row, optional deal, round stats."""
        with self._lock:
            self._negotiations[negotiation_id].update(
                {
                    "status": "completed" if success else "failed",
                    "result": result_dict,
                }
            )
            self._stats["total_rounds"] += total_rounds
            if deal is not None:
                self._deals[deal["deal_hash"]] = deal
                self._stats["total_deals"] += 1
                self._stats["total_volume"] += float(deal["agreed_price"])

    def record_run_exception(self, negotiation_id: str, message: str) -> None:
        with self._lock:
            self._negotiations[negotiation_id]["status"] = "failed"
            self._negotiations[negotiation_id]["error"] = message

    def list_negotiation_summaries(self) -> list[dict[str, Any]]:
        with self._lock:
            return [
                {
                    "negotiation_id": nid,
                    "status": data["status"],
                    "created_at": data.get("created_at"),
                }
                for nid, data in self._negotiations.items()
            ]

    def get_negotiation(self, negotiation_id: str) -> dict[str, Any] | None:
        with self._lock:
            row = self._negotiations.get(negotiation_id)
            return dict(row) if row is not None else None

    def list_deals(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._deals.values())

    def get_deal(self, deal_hash: str) -> dict[str, Any] | None:
        with self._lock:
            d = self._deals.get(deal_hash)
            return dict(d) if d is not None else None

    def reputation_summary(self, address: str) -> dict[str, Any]:
        with self._lock:
            agent_deals = [d for d in self._deals.values() if _address_matches_deal(d, address)]
            total = len(agent_deals)
            avg_price = (
                sum(float(d["agreed_price"]) for d in agent_deals) / total if total else 0.0
            )
        return {
            "address": address,
            "total_deals": total,
            "average_price": round(avg_price, 6),
            "reputation_score": min(100, 50 + total * 5),
            "positive_feedback": total,
            "negative_feedback": 0,
        }

    def dashboard_stats(self, *, passport_status: str = "stubbed") -> dict[str, Any]:
        with self._lock:
            tn = int(self._stats["total_negotiations"])
            tr = int(self._stats["total_rounds"])
            td = int(self._stats["total_deals"])
            vol = float(self._stats["total_volume"])
        avg_rounds = tr / max(tn, 1)
        return {
            "total_negotiations": tn,
            "total_deals": td,
            "avg_rounds": round(avg_rounds, 1),
            "total_volume": round(vol, 6),
            "passport_status": passport_status,
        }
