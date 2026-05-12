"""Merge graphify semantic chunks, normalize schema, run build/cluster/report/export."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


FILE_STUB_TO_PATH: dict[str, str] = {
    "file_3_4": "research-plan-docs/3.4-x402-failure-modes-negotiatorgrid.md",
    "file_4_1": "research-plan-docs/4.1-mcp-negotiation-agent-research.md",
    "file_4_2": "research-plan-docs/4.2-mcp-registries-x402-catalogs-research.md",
    "file_4_3": "research-plan-docs/4.3-negotiatorgrid-security-model.md",
    "file_5_1": "research-plan-docs/5.1-negotiatorgrid-competitor-scan.md",
    "file_5_2": "research-plan-docs/5.2-kite-winners-dx-audit.md",
    "file_5_3": "research-plan-docs/5.3-negotiatorgrid-novel-contributions.md",
    "file_6_1": "research-plan-docs/6.1-negotiatorgrid-framework-comparison.md",
    "file_6_2": "research-plan-docs/6.2-negotiatorgrid-opponent-modeling.md",
    "file_6_3": "research-plan-docs/6.3-negotiatorgrid-buyer-agent-design.md",
    "file_6_4": "research-plan-docs/6.4-negotiatorgrid-seller-mediator-design.md",
    "file_7_1": "research-plan-docs/7.1-kite-contracts-negotiatorgrid.md",
    "file_7_2": "research-plan-docs/7.2-negotiatorgrid-dashboard-spec.md",
    "file_7_3": "research-plan-docs/7.3-negotiatorgrid-deployment-plan.md",
    "file_8_1": "research-plan-docs/8.1-negotiatorgrid-adr.md",
    "file_8_2": "research-plan-docs/8.2-negotiatorgrid-sprint-backlog.md",
    "file_8_3": "research-plan-docs/8.3-negotiatorgrid-demo-script.md",
}


def normalize_chunk_b(nodes: list[dict], edges: list[dict]) -> tuple[list[dict], list[dict]]:
    """Chunk B used from/to and misused 'source' for confidence label."""
    out_nodes: list[dict] = []
    for n in nodes:
        stub = n.get("id", "")
        default_path = FILE_STUB_TO_PATH.get(stub, "")
        row = {
            "id": n["id"],
            "label": n.get("label", n["id"]),
            "file_type": n.get("file_type") or n.get("type") or "document",
            "source_file": n.get("source_file") or default_path,
            "source_location": n.get("source_location"),
            "source_url": n.get("source_url"),
            "captured_at": n.get("captured_at"),
            "author": n.get("author"),
            "contributor": n.get("contributor"),
        }
        if not row["source_file"]:
            row["source_file"] = "research-plan-docs/merged.md"
        out_nodes.append(row)

    out_edges: list[dict] = []
    for e in edges:
        e = dict(e)
        if "from" in e and "to" in e:
            src = e.pop("from")
            tgt = e.pop("to")
            conf = e.pop("source", None)
            e["source"] = src
            e["target"] = tgt
            if conf in ("EXTRACTED", "INFERRED", "AMBIGUOUS"):
                e["confidence"] = conf
            elif "confidence" not in e:
                e["confidence"] = "INFERRED"
        if "confidence" not in e:
            e["confidence"] = "INFERRED"
        if "confidence_score" not in e:
            e["confidence_score"] = 0.75
        out_edges.append(e)
    return out_nodes, out_edges


def main() -> None:
    a_path = ROOT / "graphify_chunk_a.json"
    b_path = ROOT / "graphify_chunk_b.json"
    if not a_path.exists() or not b_path.exists():
        print("Missing graphify_chunk_a.json or graphify_chunk_b.json in project root.", file=sys.stderr)
        sys.exit(1)

    a = json.loads(a_path.read_text(encoding="utf-8"))
    b = json.loads(b_path.read_text(encoding="utf-8"))

    ast = {"nodes": [], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}

    b_nodes, b_edges = normalize_chunk_b(b.get("nodes", []), b.get("edges", []))

    combined_nodes = ast["nodes"] + a.get("nodes", []) + b_nodes
    combined_edges = ast["edges"] + a.get("edges", []) + b_edges
    hyperedges = (a.get("hyperedges") or []) + (b.get("hyperedges") or [])

    seen: set[str] = set()
    deduped: list[dict] = []
    for n in combined_nodes:
        if n["id"] in seen:
            continue
        seen.add(n["id"])
        deduped.append(n)

    extract = {
        "nodes": deduped,
        "edges": combined_edges,
        "hyperedges": hyperedges,
        "input_tokens": int(a.get("input_tokens", 0)) + int(b.get("input_tokens", 0)),
        "output_tokens": int(a.get("output_tokens", 0)) + int(b.get("output_tokens", 0)),
    }

    out_extract = ROOT / ".graphify_extract.json"
    out_extract.write_text(json.dumps(extract, indent=2), encoding="utf-8")
    print(f"Wrote {out_extract} ({len(deduped)} nodes, {len(combined_edges)} edges)")

    from graphify.build import build_from_json
    from graphify.cluster import cluster, score_all
    from graphify.analyze import god_nodes, surprising_connections, suggest_questions
    from graphify.report import generate
    from graphify.export import to_json, to_html

    detection = json.loads((ROOT / ".graphify_detect.json").read_text(encoding="utf-8"))
    G = build_from_json(extract)
    communities = cluster(G)
    cohesion = score_all(G, communities)
    tokens = {"input": extract.get("input_tokens", 0), "output": extract.get("output_tokens", 0)}
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)

    labels: dict[int, str] = {}
    for cid, members in communities.items():
        sample = [G.nodes[n].get("label", n) for n in list(members)[:5]]
        labels[cid] = ", ".join(sample)[:60] if sample else f"Community {cid}"

    questions = suggest_questions(G, communities, labels)
    report = generate(
        G,
        communities,
        cohesion,
        labels,
        gods,
        surprises,
        detection,
        tokens,
        "research-plan-docs",
        suggested_questions=questions,
    )

    out_dir = ROOT / "graphify-out"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")
    to_json(G, communities, str(out_dir / "graph.json"))

    analysis = {
        "communities": {str(k): v for k, v in communities.items()},
        "cohesion": {str(k): v for k, v in cohesion.items()},
        "gods": gods,
        "surprises": surprises,
        "questions": questions,
    }
    (ROOT / ".graphify_analysis.json").write_text(json.dumps(analysis, indent=2), encoding="utf-8")

    if G.number_of_nodes() > 5000:
        print("Graph too large for HTML viz; skipped graph.html")
    else:
        to_html(G, communities, str(out_dir / "graph.html"), community_labels=labels)
        print(f"Wrote {out_dir / 'graph.html'}")

    print(f"Done. {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities")


if __name__ == "__main__":
    main()
