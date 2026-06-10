#!/usr/bin/env python
"""Stage B (no-API route) — merge agent batch outputs into data/topics/tags.json.

Reads every data/topics/out/batch_NNN.json ({id: {topics, primary}}), validates
topic ids against the taxonomy, and merges into tags.json (idempotent — existing
entries are kept, new ones added).

Usage:
    python scripts/topics/merge_tags.py
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "topics"))


def clean(entry: dict, VALID: set) -> dict | None:
    topics = [t for t in entry.get("topics", []) if t in VALID]
    primary = entry.get("primary")
    if primary not in VALID:
        primary = topics[0] if topics else None
    if not topics and primary:
        topics = [primary]
    if not topics:
        return None
    if primary not in topics:
        topics.insert(0, primary)
    # dedupe, preserve order
    seen, ordered = set(), []
    for t in topics:
        if t not in seen:
            seen.add(t); ordered.append(t)
    return {"topics": ordered[:4], "primary": primary or ordered[0]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", default="topics", choices=["topics", "platforms"])
    args = ap.parse_args(argv)
    tax = importlib.import_module("taxonomy" if args.kind == "topics" else "taxonomy_platform")
    VALID = set(tax.IDS)
    OUT_DIR = ROOT / "data" / args.kind / "out"
    TAGS_JSON = ROOT / "data" / args.kind / "tags.json"

    tags = {}
    if TAGS_JSON.exists():
        tags = json.loads(TAGS_JSON.read_text(encoding="utf-8"))

    added = bad = 0
    files = sorted(OUT_DIR.glob("batch_*.json")) if OUT_DIR.exists() else []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  skip {f.name}: {e}")
            continue
        for pid, entry in data.items():
            c = clean(entry, VALID) if isinstance(entry, dict) else None
            if c:
                if pid not in tags:
                    added += 1
                tags[pid] = c
            else:
                bad += 1

    TAGS_JSON.parent.mkdir(parents=True, exist_ok=True)
    TAGS_JSON.write_text(json.dumps(tags, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Merged {len(files)} batch files: +{added} new, {bad} invalid, "
          f"total {len(tags)} tagged → {TAGS_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
