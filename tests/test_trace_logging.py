from __future__ import annotations

import json
import shutil
from pathlib import Path

from negotiatorgrid.api.ledger import NegotiationLedger


def test_trace_autosaves_and_exports(monkeypatch) -> None:
    trace_root = Path(".tmp-test-traces")
    if trace_root.exists():
        shutil.rmtree(trace_root, ignore_errors=True)
    monkeypatch.setattr(
        NegotiationLedger,
        "_default_trace_dir",
        staticmethod(lambda: trace_root),
    )
    ledger = NegotiationLedger()

    negotiation_id = "neg-trace-001"
    ledger.create_submitted(
        negotiation_id,
        buyer_config={"agent_id": "buyer-1"},
        seller_config={"agent_id": "seller-1"},
        params={"model_mode": "llm"},
        created_at=123.0,
    )
    ledger.mark_negotiating(negotiation_id)
    ledger.record_completed_run(
        negotiation_id,
        success=True,
        result_dict={
            "negotiation_id": negotiation_id,
            "success": True,
            "deal_hash": "0xabc",
            "agreed_price": 0.1,
            "rounds": [],
            "metrics": {},
        },
        total_rounds=3,
        deal={
            "deal_hash": "0xabc",
            "negotiation_id": negotiation_id,
            "agreed_price": 0.1,
            "settled": False,
        },
    )
    ledger.record_settlement(
        negotiation_id,
        "0xabc",
        {"settled": True, "settlement_status": "completed"},
    )

    trace_path = trace_root / f"{negotiation_id}.json"
    assert trace_path.exists()
    payload = json.loads(trace_path.read_text(encoding="utf-8"))
    assert payload["negotiation_id"] == negotiation_id
    assert payload["status"] == "completed"
    assert payload["deal"]["settled"] is True
    assert any(evt.get("type") == "settlement_updated" for evt in payload["events"])

    exported = ledger.get_trace(negotiation_id)
    assert exported is not None
    assert exported["trace_path"].endswith(f"{negotiation_id}.json")
    shutil.rmtree(trace_root, ignore_errors=True)


def test_trace_persists_across_process_restart(monkeypatch) -> None:
    trace_root = Path(".tmp-test-traces-restart")
    if trace_root.exists():
        shutil.rmtree(trace_root, ignore_errors=True)
    monkeypatch.setattr(
        NegotiationLedger,
        "_default_trace_dir",
        staticmethod(lambda: trace_root),
    )

    negotiation_id = "neg-trace-002"
    ledger_a = NegotiationLedger()
    ledger_a.create_submitted(
        negotiation_id,
        buyer_config={"agent_id": "buyer-2"},
        seller_config={"agent_id": "seller-2"},
        params={"model_mode": "llm"},
        created_at=456.0,
    )
    ledger_a.record_completed_run(
        negotiation_id,
        success=True,
        result_dict={
            "negotiation_id": negotiation_id,
            "success": True,
            "deal_hash": "0xdef",
            "agreed_price": 0.2,
            "rounds": [],
            "metrics": {},
        },
        total_rounds=2,
        deal={
            "deal_hash": "0xdef",
            "negotiation_id": negotiation_id,
            "agreed_price": 0.2,
            "settled": False,
        },
    )

    # Simulate API restart: new in-memory ledger, same trace directory.
    ledger_b = NegotiationLedger()
    traces = ledger_b.list_traces()
    row = next((t for t in traces if t["negotiation_id"] == negotiation_id), None)
    assert row is not None
    assert row.get("source") == "disk"
    assert row.get("trace_exists") is True

    exported = ledger_b.get_trace(negotiation_id)
    assert exported is not None
    assert exported["negotiation_id"] == negotiation_id

    shutil.rmtree(trace_root, ignore_errors=True)
