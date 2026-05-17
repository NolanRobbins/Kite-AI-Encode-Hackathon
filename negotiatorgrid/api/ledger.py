"""In-memory negotiation and deal ledger for the demo API host.

Production deployments would replace this with a persistence adapter; the
negotiation engine in ``negotiatorgrid/`` stays independent of this module.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
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
        self._trace_dir = self._default_trace_dir()
        self._trace_dir.mkdir(parents=True, exist_ok=True)
        self._stats: dict[str, int | float] = {
            "total_negotiations": 0,
            "total_deals": 0,
            "total_rounds": 0,
            "total_volume": 0.0,
        }

    @staticmethod
    def _default_trace_dir() -> Path:
        # negotiatorgrid/api/ledger.py -> repo_root/logs/negotiation_traces
        repo_root = Path(__file__).resolve().parents[2]
        return repo_root / "logs" / "negotiation_traces"

    def _trace_path(self, negotiation_id: str) -> Path:
        safe_id = "".join(ch for ch in negotiation_id if ch.isalnum() or ch in {"-", "_"})
        return self._trace_dir / f"{safe_id}.json"

    def _append_event_locked(
        self,
        negotiation_id: str,
        event_type: str,
        detail: dict[str, Any] | None = None,
    ) -> None:
        row = self._negotiations.get(negotiation_id)
        if row is None:
            return
        events = row.setdefault("_events", [])
        if isinstance(events, list):
            events.append(
                {
                    "ts": time.time(),
                    "type": event_type,
                    "detail": detail or {},
                }
            )

    def _trace_snapshot_locked(self, negotiation_id: str) -> dict[str, Any]:
        row = self._negotiations.get(negotiation_id) or {}
        result = row.get("result") or {}
        deal_hash = ""
        if isinstance(result, dict):
            deal_hash = str(result.get("deal_hash") or "")
        deal = self._deals.get(deal_hash) if deal_hash else None
        return {
            "schema_version": 1,
            "negotiation_id": negotiation_id,
            "updated_at": time.time(),
            "status": row.get("status", "unknown"),
            "request": {
                "buyer_config": row.get("buyer_config"),
                "seller_config": row.get("seller_config"),
                "params": row.get("params"),
                "created_at": row.get("created_at"),
            },
            "result": result or None,
            "deal": deal or None,
            "events": row.get("_events", []),
        }

    def _write_trace_locked(self, negotiation_id: str) -> Path:
        payload = self._trace_snapshot_locked(negotiation_id)
        path = self._trace_path(negotiation_id)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    @staticmethod
    def _read_trace_file(path: Path) -> dict[str, Any] | None:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

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
            self._append_event_locked(negotiation_id, "submitted")
            self._write_trace_locked(negotiation_id)
            self._stats["total_negotiations"] += 1

    def mark_negotiating(self, negotiation_id: str) -> None:
        with self._lock:
            self._negotiations[negotiation_id]["status"] = "negotiating"
            self._append_event_locked(negotiation_id, "negotiating")
            self._write_trace_locked(negotiation_id)

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
            self._append_event_locked(
                negotiation_id,
                "completed" if success else "failed",
                {"total_rounds": total_rounds},
            )
            self._stats["total_rounds"] += total_rounds
            if deal is not None:
                self._deals[deal["deal_hash"]] = deal
                self._stats["total_deals"] += 1
                self._stats["total_volume"] += float(deal["agreed_price"])
            self._write_trace_locked(negotiation_id)

    def record_settlement(
        self,
        negotiation_id: str,
        deal_hash: str,
        settlement: dict[str, Any],
    ) -> None:
        with self._lock:
            deal = self._deals.get(deal_hash)
            if deal is None:
                self._append_event_locked(
                    negotiation_id,
                    "settlement_skipped",
                    {"reason": "deal_not_found", "deal_hash": deal_hash},
                )
                self._write_trace_locked(negotiation_id)
                return
            deal.update(settlement)
            self._append_event_locked(
                negotiation_id,
                "settlement_updated",
                {
                    "deal_hash": deal_hash,
                    "settled": bool(settlement.get("settled")),
                    "settlement_status": settlement.get("settlement_status", ""),
                },
            )
            self._write_trace_locked(negotiation_id)

    def record_run_exception(self, negotiation_id: str, message: str) -> None:
        with self._lock:
            self._negotiations[negotiation_id]["status"] = "failed"
            self._negotiations[negotiation_id]["error"] = message
            self._append_event_locked(
                negotiation_id,
                "exception",
                {"message": message},
            )
            self._write_trace_locked(negotiation_id)

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

    def get_trace(self, negotiation_id: str) -> dict[str, Any] | None:
        with self._lock:
            if negotiation_id in self._negotiations:
                payload = self._trace_snapshot_locked(negotiation_id)
                payload["trace_path"] = str(self._trace_path(negotiation_id))
                return payload

            path = self._trace_path(negotiation_id)
            if not path.exists():
                return None
            payload = self._read_trace_file(path)
            if payload is None:
                return None
            payload["trace_path"] = str(path)
            return payload

    def list_traces(self) -> list[dict[str, Any]]:
        with self._lock:
            out_by_id: dict[str, dict[str, Any]] = {}
            out: list[dict[str, Any]] = []
            for negotiation_id, row in self._negotiations.items():
                path = self._trace_path(negotiation_id)
                out_by_id[negotiation_id] = {
                    "negotiation_id": negotiation_id,
                    "status": row.get("status", "unknown"),
                    "created_at": row.get("created_at"),
                    "trace_path": str(path),
                    "trace_exists": path.exists(),
                    "source": "memory",
                }

            for path in sorted(self._trace_dir.glob("*.json")):
                negotiation_id = path.stem
                if negotiation_id in out_by_id:
                    continue
                payload = self._read_trace_file(path) or {}
                created_at = None
                request = payload.get("request")
                if isinstance(request, dict):
                    created_at = request.get("created_at")
                out_by_id[negotiation_id] = {
                    "negotiation_id": negotiation_id,
                    "status": payload.get("status", "unknown"),
                    "created_at": created_at,
                    "trace_path": str(path),
                    "trace_exists": True,
                    "source": "disk",
                }

            out.extend(out_by_id.values())
            out.sort(key=lambda row: float(row.get("created_at") or 0.0), reverse=True)
            return out
