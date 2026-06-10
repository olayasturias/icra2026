#!/usr/bin/env python
"""Stage B (no-API route) — shard the untagged corpus into batch files for
Claude Code sub-agents to classify.

Each batch file data/topics/batches/batch_NNN.json holds a list of
{id, title, abstract} (abstract trimmed for classification). An agent reads one
batch, assigns 1-4 taxonomy topic ids per paper, and writes
data/topics/out/batch_NNN.json as {id: {topics, primary}}. merge_tags.py then
folds the out/ files into data/topics/tags.json.

Usage:
    python scripts/topics/make_batches.py [--size 150]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METADATA_JSON = ROOT / "data" / "metadata.json"
WORKSHOP_JSON = ROOT / "data" / "workshop_papers.json"
TAGS_JSON = ROOT / "data" / "topics" / "tags.json"
BATCH_DIR = ROOT / "data" / "topics" / "batches"

ABSTRACT_CHARS = 600  # enough signal for topic classification, keeps batches small


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=150, help="papers per batch")
    args = ap.parse_args(argv)

    tagged = set()
    if TAGS_JSON.exists():
        tagged = set(json.loads(TAGS_JSON.read_text(encoding="utf-8")).keys())

    corpus = []
    for r in json.loads(METADATA_JSON.read_text(encoding="utf-8")):
        corpus.append((f"pp:{r['id']}", r["title"], r["abstract"]))
    for r in json.loads(WORKSHOP_JSON.read_text(encoding="utf-8")):
        corpus.append((r["id"], r["title"], r["abstract"]))

    todo = [
        {"id": pid, "title": title, "abstract": (abs or "")[:ABSTRACT_CHARS]}
        for pid, title, abs in corpus
        if pid not in tagged
    ]

    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for f in BATCH_DIR.glob("batch_*.json"):
        f.unlink()

    n = 0
    for i in range(0, len(todo), args.size):
        part = todo[i : i + args.size]
        (BATCH_DIR / f"batch_{n:03d}.json").write_text(
            json.dumps(part, indent=1, ensure_ascii=False), encoding="utf-8"
        )
        n += 1
    print(f"{len(corpus)} papers, {len(tagged)} already tagged, "
          f"{len(todo)} to tag → {n} batches of ~{args.size} in {BATCH_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
