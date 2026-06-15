#!/usr/bin/env python
"""Stage C of the map pipeline (taxonomy-agnostic).

Combine the corpus (proceedings + workshop papers) with the LLM category tags
and emit the JSON the visualization consumes:

  site/assets/json/<prefix>_graph.json — {nodes, edges, meta}
      nodes: one per category with >=1 paper {id,label,group,color,count,paperIds}
      edges: category pairs co-occurring on >= EDGE_MIN papers {source,target,weight}
      meta:  {papers, edge_min, groups:[{group,color}]}  (groups drive the legend)
  site/assets/json/topic_papers.json — {id: {title,abstract,authors,source,workshop,code,url}}
      Shared by every map (paper metadata is the same regardless of categorization).

--kind topics    → taxonomy.py,          site/assets/json/topic_graph.json
--kind platforms → taxonomy_platform.py, site/assets/json/platform_graph.json

Usage:
    python scripts/topics/build_graph.py --kind topics    [--edge-min 6]
    python scripts/topics/build_graph.py --kind platforms [--edge-min 6]
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "topics"))

METADATA_JSON = ROOT / "data" / "metadata.json"
WORKSHOP_JSON = ROOT / "data" / "workshop_papers.json"
OUT_DIR = ROOT / "site" / "assets" / "json"
PAPERS_JSON = OUT_DIR / "topic_papers.json"  # shared across maps

PREFIX = {"topics": "topic", "platforms": "platform"}

# Optional background-image icon (in assets/img/) per node, by kind+id.
ICONS = {
    "platforms": {"uav": "uav-multirotor.png", "humanoid": "humanoid2.svg",
                  "legged": "legged.svg", "soft": "softrobot.svg",
                  "space": "space.svg", "wearable": "exoeskeleton.svg",
                  "marine": "marine.svg", "hand": "hand.png",
                  "micro": "unconventional.svg", "arm": "robotarm.svg"},
}


def load_papers() -> dict[str, dict]:
    """id -> full paper record for both sources."""
    papers: dict[str, dict] = {}
    for r in json.loads(METADATA_JSON.read_text(encoding="utf-8")):
        papers[f"pp:{r['id']}"] = {
            "title": r["title"], "abstract": r["abstract"], "authors": r["authors"],
            "source": "proceedings", "workshop": None, "code": r.get("code", ""), "url": "",
        }
    for r in json.loads(WORKSHOP_JSON.read_text(encoding="utf-8")):
        papers[r["id"]] = {
            "title": r["title"], "abstract": r["abstract"], "authors": r["authors"],
            "source": "workshop", "workshop": r.get("workshop"),
            "code": r.get("code", ""), "url": r.get("source_url", ""),
        }
    return papers


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", default="topics", choices=["topics", "platforms"])
    ap.add_argument("--edge-min", type=int, default=6, help="min co-occurrence to draw an edge")
    args = ap.parse_args(argv)

    tax = importlib.import_module("taxonomy" if args.kind == "topics" else "taxonomy_platform")
    TOPICS, BY_ID, COLORS = tax.TOPICS, {t["id"]: t for t in tax.TOPICS}, tax.GROUP_COLORS
    tags_json = ROOT / "data" / args.kind / "tags.json"
    graph_json = OUT_DIR / f"{PREFIX[args.kind]}_graph.json"

    if not tags_json.exists():
        print(f"Missing {tags_json} — tag this kind first.", file=sys.stderr)
        return 2

    papers = load_papers()
    tags = json.loads(tags_json.read_text(encoding="utf-8"))

    node_papers: dict[str, list[str]] = {t["id"]: [] for t in TOPICS}
    edge_w: dict[tuple[str, str], int] = {}
    out_papers: dict[str, dict] = {}

    for pid, tag in tags.items():
        if pid not in papers:
            continue
        cats = [t for t in tag.get("topics", []) if t in BY_ID]
        if not cats:
            continue
        for t in cats:
            node_papers[t].append(pid)
        for a, b in combinations(sorted(set(cats)), 2):
            edge_w[(a, b)] = edge_w.get((a, b), 0) + 1
        if pid not in out_papers:
            out_papers[pid] = dict(papers[pid])

    icons = ICONS.get(args.kind, {})
    nodes = []
    for t in TOPICS:
        ids = node_papers[t["id"]]
        if not ids:
            continue
        node = {
            "id": t["id"], "label": t["label"], "group": t["group"],
            "color": COLORS.get(t["group"], "#9aa4b2"),
            "count": len(ids), "paperIds": ids,
        }
        if t["id"] in icons:
            node["icon"] = icons[t["id"]]
        nodes.append(node)
    live = {n["id"] for n in nodes}
    edges = [
        {"source": a, "target": b, "weight": w}
        for (a, b), w in edge_w.items()
        if w >= args.edge_min and a in live and b in live
    ]
    edges.sort(key=lambda e: -e["weight"])
    live_groups = [g for g in COLORS if any(n["group"] == g for n in nodes)]
    groups_meta = [{"group": g, "color": COLORS[g]} for g in live_groups]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    graph_json.write_text(json.dumps(
        {"nodes": nodes, "edges": edges,
         "meta": {"kind": args.kind, "papers": len(out_papers),
                  "edge_min": args.edge_min, "groups": groups_meta}},
        indent=1, ensure_ascii=False), encoding="utf-8")
    # Refresh the shared papers file (only proceedings/workshop fields).
    PAPERS_JSON.write_text(json.dumps(out_papers, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"[{args.kind}] {len(nodes)} nodes, {len(edges)} edges → {graph_json}")
    print(f"          {len(out_papers)} papers → {PAPERS_JSON}")
    print("\nTop categories by paper count:")
    for n in sorted(nodes, key=lambda n: -n["count"])[:12]:
        print(f"  {n['count']:4}  {n['label']}")
    print("\nStrongest connections:")
    for e in edges[:10]:
        print(f"  {e['weight']:4}  {BY_ID[e['source']]['label']} — {BY_ID[e['target']]['label']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
