#!/usr/bin/env python
"""Stage C of the topic-map pipeline.

Combine the corpus (proceedings + workshop papers) with the LLM topic tags and
emit the two JSON files the visualization consumes:

  site/assets/json/topic_graph.json  — {nodes, edges, meta}
      nodes: one per taxonomy topic with >=1 paper {id,label,group,count,paperIds}
      edges: topic pairs co-occurring on >= EDGE_MIN papers {source,target,weight}
  site/assets/json/topic_papers.json — {id: {title,abstract,authors,source,workshop,code,url,primary,topics}}

Usage:
    python scripts/topics/build_graph.py [--edge-min 3]
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "topics"))
from taxonomy import TOPICS  # noqa: E402

METADATA_JSON = ROOT / "data" / "metadata.json"
WORKSHOP_JSON = ROOT / "data" / "workshop_papers.json"
TAGS_JSON = ROOT / "data" / "topics" / "tags.json"
OUT_DIR = ROOT / "site" / "assets" / "json"
GRAPH_JSON = OUT_DIR / "topic_graph.json"
PAPERS_JSON = OUT_DIR / "topic_papers.json"

TOPIC_BY_ID = {t["id"]: t for t in TOPICS}


def load_papers() -> dict[str, dict]:
    """id -> full paper record for both sources."""
    papers: dict[str, dict] = {}
    for r in json.loads(METADATA_JSON.read_text(encoding="utf-8")):
        pid = f"pp:{r['id']}"
        papers[pid] = {
            "title": r["title"], "abstract": r["abstract"], "authors": r["authors"],
            "source": "proceedings", "workshop": None, "code": r.get("code", ""),
            "url": "",
        }
    for r in json.loads(WORKSHOP_JSON.read_text(encoding="utf-8")):
        papers[r["id"]] = {
            "title": r["title"], "abstract": r["abstract"], "authors": r["authors"],
            "source": "workshop", "workshop": r.get("workshop"), "code": r.get("code", ""),
            "url": r.get("source_url", ""),
        }
    return papers


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--edge-min", type=int, default=6, help="min co-occurrence to draw an edge")
    args = ap.parse_args(argv)

    if not TAGS_JSON.exists():
        print(f"Missing {TAGS_JSON} — run tag_topics.py first.", file=sys.stderr)
        return 2

    papers = load_papers()
    tags = json.loads(TAGS_JSON.read_text(encoding="utf-8"))

    node_papers: dict[str, list[str]] = {t["id"]: [] for t in TOPICS}
    edge_w: dict[tuple[str, str], int] = {}
    out_papers: dict[str, dict] = {}

    for pid, tag in tags.items():
        if pid not in papers:
            continue
        topics = [t for t in tag.get("topics", []) if t in TOPIC_BY_ID]
        if not topics:
            continue
        for t in topics:
            node_papers[t].append(pid)
        for a, b in combinations(sorted(set(topics)), 2):
            edge_w[(a, b)] = edge_w.get((a, b), 0) + 1
        rec = dict(papers[pid])
        rec["topics"] = topics
        rec["primary"] = tag.get("primary", topics[0])
        out_papers[pid] = rec

    nodes = []
    for t in TOPICS:
        ids = node_papers[t["id"]]
        if not ids:
            continue
        nodes.append({
            "id": t["id"], "label": t["label"], "group": t["group"],
            "count": len(ids), "paperIds": ids,
        })
    live = {n["id"] for n in nodes}
    edges = [
        {"source": a, "target": b, "weight": w}
        for (a, b), w in edge_w.items()
        if w >= args.edge_min and a in live and b in live
    ]
    edges.sort(key=lambda e: -e["weight"])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_JSON.write_text(json.dumps(
        {"nodes": nodes, "edges": edges,
         "meta": {"papers": len(out_papers), "edge_min": args.edge_min}},
        indent=1, ensure_ascii=False), encoding="utf-8")
    PAPERS_JSON.write_text(json.dumps(out_papers, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {len(nodes)} nodes, {len(edges)} edges → {GRAPH_JSON}")
    print(f"Wrote {len(out_papers)} papers → {PAPERS_JSON}")
    print("\nTop topics by paper count:")
    for n in sorted(nodes, key=lambda n: -n["count"])[:12]:
        print(f"  {n['count']:4}  {n['label']}")
    print("\nStrongest topic connections:")
    for e in edges[:10]:
        print(f"  {e['weight']:4}  {TOPIC_BY_ID[e['source']]['label']} — {TOPIC_BY_ID[e['target']]['label']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
