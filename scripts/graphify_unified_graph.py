"""Build graphify-out from AST (code) + optional research semantic layer (spec/docs).

Run from repo root (or set NEGOTIATORGRID_ROOT):

  .venv\\Scripts\\python.exe scripts/graphify_unified_graph.py
  .venv\\Scripts\\python.exe scripts/graphify_unified_graph.py --no-merge-research
  .venv\\Scripts\\python.exe scripts/graphify_unified_graph.py --full-code
  .venv\\Scripts\\python.exe scripts/graphify_unified_graph.py --research-layer path/to/graph.json

Requires: graphify, tree-sitter (same as ``graphify update``).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# Chunk B stub ids → paths (must match scripts/graphify_merge_and_build.py)
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


def normalize_chunk_b(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> tuple[list[dict], list[dict]]:
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


def _rel_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def filter_focused_code(paths: list[Path], root: Path) -> list[Path]:
    """Keep negotiatorgrid/, dashboard/src/, surprise_api/, tests/ only."""
    prefixes = (
        "negotiatorgrid/",
        "dashboard/src/",
        "surprise_api/",
        "tests/",
    )
    out: list[Path] = []
    for p in paths:
        try:
            rel = _rel_posix(p, root)
        except ValueError:
            continue
        if any(rel.startswith(pref) for pref in prefixes):
            out.append(p)
    return sorted(out, key=lambda x: str(x))


def load_research_layer(root: Path, explicit: Path | None) -> dict[str, Any] | None:
    """Return merged research extraction dict {nodes, edges, hyperedges} or None."""
    if explicit is not None:
        if not explicit.is_file():
            print(f"error: --research-layer not found: {explicit}", file=sys.stderr)
            sys.exit(1)
        data = json.loads(explicit.read_text(encoding="utf-8"))
        return _as_extraction_dict(data)

    single = root / "graphify-research.json"
    if single.is_file():
        data = json.loads(single.read_text(encoding="utf-8"))
        return _as_extraction_dict(data)

    a_path = root / "graphify_chunk_a.json"
    b_path = root / "graphify_chunk_b.json"
    if not a_path.is_file() or not b_path.is_file():
        return None

    a = json.loads(a_path.read_text(encoding="utf-8"))
    b = json.loads(b_path.read_text(encoding="utf-8"))
    b_nodes, b_edges = normalize_chunk_b(b.get("nodes", []), b.get("edges", []))
    return {
        "nodes": list(a.get("nodes", [])) + b_nodes,
        "edges": list(a.get("edges", [])) + b_edges,
        "hyperedges": list(a.get("hyperedges") or []) + list(b.get("hyperedges") or []),
        "input_tokens": int(a.get("input_tokens", 0)) + int(b.get("input_tokens", 0)),
        "output_tokens": int(a.get("output_tokens", 0)) + int(b.get("output_tokens", 0)),
    }


def _as_extraction_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Accept raw extraction or exported graph.json (nodes + links)."""
    nodes = data.get("nodes", [])
    edges = data.get("edges") or data.get("links", [])
    return {
        "nodes": nodes,
        "edges": edges,
        "hyperedges": data.get("hyperedges", []),
        "input_tokens": int(data.get("input_tokens", 0)),
        "output_tokens": int(data.get("output_tokens", 0)),
    }


def merge_extractions(ast: dict[str, Any], research: dict[str, Any] | None) -> dict[str, Any]:
    """AST first, then research nodes/edges; dedupe nodes by id."""
    if not research:
        return ast

    combined_nodes = list(ast.get("nodes", [])) + list(research.get("nodes", []))
    combined_edges = list(ast.get("edges", [])) + list(research.get("edges", []))
    hyperedges = list(ast.get("hyperedges", [])) + list(research.get("hyperedges", []))

    seen: set[str] = set()
    deduped: list[dict] = []
    for n in combined_nodes:
        nid = n.get("id")
        if not nid or nid in seen:
            continue
        seen.add(nid)
        deduped.append(n)

    return {
        "nodes": deduped,
        "edges": combined_edges,
        "hyperedges": hyperedges,
        "input_tokens": int(ast.get("input_tokens", 0)) + int(research.get("input_tokens", 0)),
        "output_tokens": int(ast.get("output_tokens", 0)) + int(research.get("output_tokens", 0)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Unified AST + research graphify build.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(os.environ.get("NEGOTIATORGRID_ROOT", str(ROOT))),
        help="Repository root (default: parent of scripts/)",
    )
    parser.add_argument(
        "--full-code",
        action="store_true",
        help="Include all detected code (contracts/scripts/demo/etc.); default is focused paths only",
    )
    parser.add_argument(
        "--no-merge-research",
        action="store_true",
        help="AST + docs from detect only (no graphify_chunk_*.json / graphify-research.json)",
    )
    parser.add_argument(
        "--research-layer",
        type=Path,
        default=None,
        help="Explicit JSON (extraction or graph.json) to merge as the research layer",
    )
    args = parser.parse_args()
    root: Path = args.root.resolve()

    focus = not args.full_code

    from graphify.detect import detect  # noqa: PLC0415
    from graphify.extract import extract  # noqa: PLC0415
    from graphify.build import build_from_json  # noqa: PLC0415
    from graphify.cluster import cluster, score_all  # noqa: PLC0415
    from graphify.analyze import god_nodes, surprising_connections, suggest_questions  # noqa: PLC0415
    from graphify.report import generate  # noqa: PLC0415
    from graphify.export import to_json, to_html  # noqa: PLC0415

    detected = detect(root)
    (root / ".graphify_detect.json").write_text(
        json.dumps(
            {
                "files": detected["files"],
                "total_files": detected["total_files"],
                "total_words": detected["total_words"],
                "needs_graph": detected["needs_graph"],
                "warning": detected.get("warning"),
                "graphifyignore_patterns": detected.get("graphifyignore_patterns"),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    code_paths = [Path(f) for f in detected["files"]["code"]]
    if focus:
        code_paths = filter_focused_code(code_paths, root)
    if not code_paths:
        print("No code files after filtering — nothing to extract.", file=sys.stderr)
        sys.exit(1)

    print(f"AST extract: {len(code_paths)} code file(s) (focus={focus})")
    ast_result = extract(code_paths, cache_root=root)

    research: dict[str, Any] | None = None
    if not args.no_merge_research:
        research = load_research_layer(root, args.research_layer)
        if research:
            print(
                f"Research layer: {len(research['nodes'])} nodes, "
                f"{len(research['edges'])} edges (merged with AST)",
            )
        else:
            print("Research layer: not found (use graphify_chunk_a/b.json or --research-layer) — AST only")

    extract_out = merge_extractions(ast_result, research)
    (root / ".graphify_extract.json").write_text(json.dumps(extract_out, indent=2), encoding="utf-8")

    detection_for_report = {
        "files": detected["files"],
        "total_files": detected["total_files"],
        "total_words": detected["total_words"],
    }
    tokens = {
        "input": extract_out.get("input_tokens", 0),
        "output": extract_out.get("output_tokens", 0),
    }

    G = build_from_json(extract_out)
    communities = cluster(G)
    cohesion = score_all(G, communities)
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
        detection_for_report,
        tokens,
        str(root),
        suggested_questions=questions,
    )

    out_dir = root / "graphify-out"
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
    (root / ".graphify_analysis.json").write_text(json.dumps(analysis, indent=2), encoding="utf-8")

    if G.number_of_nodes() > 5000:
        print("Graph too large for HTML viz; skipped graph.html")
    else:
        to_html(G, communities, str(out_dir / "graph.html"), community_labels=labels)
        print(f"Wrote {out_dir / 'graph.html'}")

    print(f"Done. {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities")
    print(f"Outputs: {out_dir / 'graph.json'}, {out_dir / 'GRAPH_REPORT.md'}")


if __name__ == "__main__":
    main()
