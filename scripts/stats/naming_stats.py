#!/usr/bin/env python
"""Extract ICRA 2026 title-naming statistics from data/metadata.json.

Renderer-agnostic: pure counting, no Manim/plotting imports. Produces the data
for the five panels of the "How ICRA 2026 names things" figure and writes it to
data/stats/naming.json. The patterns are tuned to the ICRA corpus (measured),
not the CVPR cliches (which are near-absent here).

Usage:
    python scripts/stats/naming_stats.py
"""

from __future__ import annotations

import collections
import json
import re
import statistics
from pathlib import Path

# scripts/stats/naming_stats.py -> repo root is two parents up.
ROOT = Path(__file__).resolve().parents[2]
METADATA = ROOT / "data" / "metadata.json"
OUT_JSON = ROOT / "data" / "stats" / "naming.json"

_WORD = re.compile(r"[a-z0-9']+")


def tokenize(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


# --- panel 1: structural / template patterns -------------------------------
# label -> predicate over a single title. Document frequency = #titles matching.
_HYPHEN = re.compile(r"\w-\w")
PATTERNS: dict[str, callable] = {
    "has a colon": lambda t: ":" in t,
    '"X for Y" (for)': lambda t: re.search(r"\bfor\b", t, re.I) is not None,
    "uses 'with'": lambda t: re.search(r"\bwith\b", t, re.I) is not None,
    "uses 'via'": lambda t: re.search(r"\bvia\b", t, re.I) is not None,
    "uses 'using'": lambda t: re.search(r"\busing\b", t, re.I) is not None,
    "hyphenated compound": lambda t: _HYPHEN.search(t) is not None,
    "'X Anything'": lambda t: re.search(r"\w+\s*anything\b", t, re.I) is not None,
    "is a question (?)": lambda t: t.strip().endswith("?"),
}

# --- panel 3: how titles open ----------------------------------------------
FIRST_WORD_INTEREST = [
    "Learning", "Towards", "A", "Design", "Real-Time", "Robust", "Efficient",
    "Autonomous", "Adaptive", "Safe", "Enhancing", "Beyond", "Multi-Robot",
    "Deep", "Dynamic", "Robotic", "Scalable", "Bridging", "Rethinking",
]

# --- panel 5: domain themes (doc-frequency over titles) --------------------
# label -> regex. Order is the display order (we sort by count at plot time).
THEMES: dict[str, str] = {
    "learning": r"\blearn",
    "manipulation": r"manipulat",
    "navigation": r"navigat",
    "human-robot": r"\bhuman",
    "autonomous": r"autonomous",
    "real-time": r"real[\s-]?time",
    "reinforcement learning": r"reinforcement",
    "legged / humanoid": r"legged|quadruped|humanoid",
    "diffusion": r"diffusion",
    "grasping": r"grasp",
    "tactile": r"tactile|taxel",
    "soft robotics": r"soft[\s-]?(?:robot|gripper|actuator|hand|manipulat)",
    "LLM / VLM / VLA": r"\b(?:llm|vlm|vla|language model|foundation model)\b",
    "SLAM": r"\bslam\b",
    "place recognition / VPR": r"place recognition|\bVPR\b",
    "sim-to-real": r"sim[\s-]?to[\s-]?real|sim2real",
    # neuromorphic vision: the field plus its staples (SNN, event cameras,
    # event-based sensing).
    "neuromorphic": r"neuromorphic|spiking neural|\bSNN\b|event[\s-]?camera"
                    r"|event[\s-]?based",
}

_ACRO = re.compile(r"\b[A-Za-z0-9]*[A-Z][A-Za-z0-9]*[A-Z][A-Za-z0-9]*\b")


def compute_naming(papers: list[dict]) -> dict:
    titles = [p["title"] for p in papers]
    total = len(titles)

    patterns = {label: sum(1 for t in titles if pred(t))
                for label, pred in PATTERNS.items()}

    lengths = [len(tokenize(t)) for t in titles]
    length_hist = collections.Counter(lengths)

    first = collections.Counter()
    for t in titles:
        m = re.match(r"\s*([A-Za-z][A-Za-z0-9-]*)", t)
        if m:
            # Capitalize but preserve internal hyphen casing (Real-Time, Multi-Robot).
            w = m.group(1)
            first["-".join(p.capitalize() for p in w.split("-"))] += 1
    first_words = {w: first.get(w, 0) for w in FIRST_WORD_INTEREST
                   if first.get(w, 0) > 0}

    acro = collections.Counter()
    for t in titles:
        for tok in _ACRO.findall(t):
            if 2 <= len(tok) <= 14:
                acro[tok] += 1

    themes = {label: sum(1 for t in titles if re.search(rx, t, re.I))
              for label, rx in THEMES.items()}

    return {
        "total": total,
        "patterns": patterns,
        "length": {
            "hist": {str(k): v for k, v in sorted(length_hist.items())},
            "min": min(lengths), "max": max(lengths),
            "median": statistics.median(lengths),
            "mean": round(statistics.mean(lengths), 2),
        },
        "first_words": first_words,
        "acronyms": dict(acro.most_common(14)),
        "themes": themes,
    }


def main() -> None:
    papers = load(METADATA)
    stats = compute_naming(papers)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(stats, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"Wrote {OUT_JSON} ({stats['total']} papers)")

    # Self-check against the measured survey, so a regression is obvious.
    p = stats["patterns"]
    print(f"  colon={p['has a colon']} for={p['\"X for Y\" (for)']} "
          f"median_len={stats['length']['median']} "
          f"top_acronym={next(iter(stats['acronyms']))}")
    assert 1300 <= p["has a colon"] <= 1450, p["has a colon"]
    assert 1450 <= p['"X for Y" (for)'] <= 1600, p['"X for Y" (for)']
    assert stats["length"]["median"] == 12, stats["length"]["median"]
    print("  self-check OK")


if __name__ == "__main__":
    main()
