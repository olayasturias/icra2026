#!/usr/bin/env python
"""Stage B of the topic-map pipeline.

Tag every paper (proceedings + workshop) with 1-4 topics from the curated
taxonomy, using Claude Haiku 4.5. Results are cached in data/topics/tags.json
and the run is resumable — only untagged papers cost tokens.

Two modes:
  * default: Message Batches API (50% cheaper, async; best for the full corpus).
  * --sync:  sequential messages.create (use with --limit to spot-check quickly).

Requires credentials in the environment: ANTHROPIC_API_KEY, or an
`ant auth login` profile (the SDK resolves either automatically).

Usage:
    python scripts/topics/tag_topics.py --sync --limit 30     # spot-check
    python scripts/topics/tag_topics.py                       # full corpus, batched
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "topics"))
from taxonomy import IDS, taxonomy_prompt  # noqa: E402

METADATA_JSON = ROOT / "data" / "metadata.json"
WORKSHOP_JSON = ROOT / "data" / "workshop_papers.json"
OUT_JSON = ROOT / "data" / "topics" / "tags.json"

MODEL = "claude-haiku-4-5"
MAX_TOKENS = 200
ABSTRACT_CHARS = 2200  # trim very long abstracts to control input cost

SYSTEM = (
    "You classify robotics research papers into topics from a fixed taxonomy.\n"
    "Choose the 1-4 topic ids that best match the paper; pick the single most "
    "central one as `primary`. Use only ids from this taxonomy:\n\n"
    + taxonomy_prompt()
)

SCHEMA = {
    "type": "object",
    "properties": {
        "topics": {
            "type": "array",
            "items": {"type": "string", "enum": IDS},
        },
        "primary": {"type": "string", "enum": IDS},
    },
    "required": ["topics", "primary"],
    "additionalProperties": False,
}
OUTPUT_CONFIG = {"format": {"type": "json_schema", "schema": SCHEMA}}


def load_corpus() -> list[dict]:
    """Combined [{id, title, abstract}] for proceedings + workshop papers."""
    corpus = []
    for r in json.loads(METADATA_JSON.read_text(encoding="utf-8")):
        corpus.append({"id": f"pp:{r['id']}", "title": r["title"], "abstract": r["abstract"]})
    for r in json.loads(WORKSHOP_JSON.read_text(encoding="utf-8")):
        corpus.append({"id": r["id"], "title": r["title"], "abstract": r["abstract"]})
    return corpus


def user_text(p: dict) -> str:
    return f"Title: {p['title']}\n\nAbstract: {(p['abstract'] or '')[:ABSTRACT_CHARS]}"


def load_tags() -> dict[str, dict]:
    if OUT_JSON.exists():
        return json.loads(OUT_JSON.read_text(encoding="utf-8"))
    return {}


def save_tags(tags: dict) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(tags, indent=1, ensure_ascii=False), encoding="utf-8")


def parse_result(text: str) -> dict | None:
    try:
        obj = json.loads(text)
    except Exception:
        return None
    topics = [t for t in obj.get("topics", []) if t in IDS]
    primary = obj.get("primary") if obj.get("primary") in IDS else (topics[0] if topics else None)
    if not topics and primary:
        topics = [primary]
    if not topics:
        return None
    if primary and primary not in topics:
        topics.insert(0, primary)
    return {"topics": topics, "primary": primary or topics[0]}


def run_sync(client, todo: list[dict], tags: dict) -> None:
    for i, p in enumerate(todo, 1):
        resp = client.messages.create(
            model=MODEL, max_tokens=MAX_TOKENS,
            system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": user_text(p)}],
            output_config=OUTPUT_CONFIG,
        )
        text = next((b.text for b in resp.content if b.type == "text"), "")
        parsed = parse_result(text)
        if parsed:
            tags[p["id"]] = parsed
        print(f"  {i}/{len(todo)} {p['id']}: {parsed['topics'] if parsed else 'FAILED'}")
        if i % 25 == 0:
            save_tags(tags)
    save_tags(tags)


def run_batch(client, todo: list[dict], tags: dict, chunk: int = 1000) -> None:
    for start in range(0, len(todo), chunk):
        part = todo[start : start + chunk]
        requests = [
            Request(
                custom_id=p["id"].replace(":", "__"),  # custom_id must be [A-Za-z0-9_-]
                params=MessageCreateParamsNonStreaming(
                    model=MODEL, max_tokens=MAX_TOKENS,
                    system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
                    messages=[{"role": "user", "content": user_text(p)}],
                    output_config=OUTPUT_CONFIG,
                ),
            )
            for p in part
        ]
        batch = client.messages.batches.create(requests=requests)
        print(f"batch {batch.id}: {len(part)} requests ({start + len(part)}/{len(todo)})")
        while True:
            b = client.messages.batches.retrieve(batch.id)
            if b.processing_status == "ended":
                break
            print(f"  ...{b.processing_status} (done {b.request_counts.succeeded + b.request_counts.errored})")
            time.sleep(20)
        ok = 0
        for res in client.messages.batches.results(batch.id):
            if res.result.type != "succeeded":
                continue
            pid = res.custom_id.replace("__", ":", 1)
            text = next((bl.text for bl in res.result.message.content if bl.type == "text"), "")
            parsed = parse_result(text)
            if parsed:
                tags[pid] = parsed
                ok += 1
        save_tags(tags)
        print(f"  tagged {ok}/{len(part)}; total cached {len(tags)}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="tag only the first N untagged")
    ap.add_argument("--sync", action="store_true", help="sequential calls instead of Batch API")
    args = ap.parse_args(argv)

    try:
        client = anthropic.Anthropic()
    except Exception as e:  # pragma: no cover
        print(f"Could not init Anthropic client: {e}", file=sys.stderr)
        return 2

    corpus = load_corpus()
    tags = load_tags()
    todo = [p for p in corpus if p["id"] not in tags]
    if args.limit:
        todo = todo[: args.limit]
    print(f"Corpus {len(corpus)}, already tagged {len(tags)}, to tag {len(todo)}")
    if not todo:
        print("Nothing to do.")
        return 0

    try:
        (run_sync if args.sync else run_batch)(client, todo, tags)
    except anthropic.AuthenticationError:
        print("\nERROR: no valid Anthropic credentials. Set ANTHROPIC_API_KEY "
              "or run `ant auth login`.", file=sys.stderr)
        return 2

    print(f"\nDone. {len(tags)}/{len(corpus)} papers tagged → {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
