#!/usr/bin/env python
"""Stage A of the topic-map pipeline.

Extract title + abstract + authors from every downloaded workshop-paper PDF in
data/workshop_papers/<slug>/ and write data/workshop_papers.json.

The proceedings papers already have this metadata (data/metadata.json); the
workshop papers were only downloaded as PDFs, so we parse them here, reusing the
PDF extractors from scripts/proceedings/build_metadata.py.

Usage:
    python scripts/workshops/extract_workshop_papers.py
    python scripts/workshops/extract_workshop_papers.py --limit 10
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "proceedings"))
import build_metadata as bm  # noqa: E402  (pdf_title/pdf_authors/parse_paper/clean)

PAPERS_ROOT = ROOT / "data" / "workshop_papers"
WORKSHOPS_JSON = ROOT / "data" / "workshops.json"
OUT_JSON = ROOT / "data" / "workshop_papers.json"

# An arXiv side-watermark renders as the largest-font text on page 1, so
# pdf_title() can return it instead of the real title. Detect + reject.
ARXIV_LINE = re.compile(r"arxiv[:\s]", re.IGNORECASE)


def slugify(name: str) -> str:
    s = re.sub(r"[^\w\s-]", "", name.lower())
    s = re.sub(r"[\s_-]+", "-", s).strip("-")
    return s[:60]


def best_title(pdf: Path, parsed_title: str) -> str:
    """Prefer the PDF's metadata Title; fall back to the parsed first-page title
    (dropping an arXiv watermark) or the filename stem."""
    try:
        with fitz.open(pdf) as doc:
            meta = (doc.metadata or {}).get("title") or ""
    except Exception:
        meta = ""
    meta = meta.strip()
    if meta and not ARXIV_LINE.search(meta) and len(meta) > 8:
        return meta
    if parsed_title and not ARXIV_LINE.search(parsed_title):
        return parsed_title
    return pdf.stem


def first_page_fallback(pdf: Path) -> str:
    """First ~1200 chars of page 1 text, for papers whose abstract regex misses."""
    try:
        with fitz.open(pdf) as doc:
            txt = bm.clean(doc[0].get_text("text"))
    except Exception:
        return ""
    return txt[:1200]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args(argv)

    workshops = json.loads(WORKSHOPS_JSON.read_text(encoding="utf-8"))
    # slug -> (workshop name, paper_source_urls list)
    by_slug: dict[str, tuple[str, list[str]]] = {}
    for w in workshops:
        by_slug[slugify(w["name"])] = (w["name"], w.get("paper_source_urls") or [])

    pdfs = sorted(PAPERS_ROOT.glob("*/*.pdf"))
    if args.limit:
        pdfs = pdfs[: args.limit]
    print(f"Parsing {len(pdfs)} workshop PDFs ...")

    records, no_abstract, no_title = [], 0, 0
    for idx, pdf in enumerate(pdfs, 1):
        slug = pdf.parent.name
        stem = pdf.stem  # e.g. "<slug>_07"
        m = re.search(r"_(\d+)$", stem)
        n = int(m.group(1)) if m else 0
        wname, urls = by_slug.get(slug, (slug, []))
        source_url = urls[n - 1] if 0 < n <= len(urls) else ""

        meta = bm.parse_paper(pdf)
        title = best_title(pdf, meta["title"])
        abstract = meta["abstract"] or first_page_fallback(pdf)
        if not meta["abstract"]:
            no_abstract += 1
        if not title or title == stem:
            no_title += 1

        records.append(
            {
                "id": f"ws:{stem}",
                "title": title,
                "abstract": abstract,
                "authors": meta["authors"],
                "workshop": wname,
                "source_url": source_url,
                "code": meta.get("code", ""),
                "file": str(pdf.relative_to(ROOT)).replace("\\", "/"),
            }
        )
        if idx % 50 == 0:
            print(f"  {idx}/{len(pdfs)}")

    OUT_JSON.write_text(
        json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nWrote {len(records)} records to {OUT_JSON}")
    print(f"  {no_abstract} had no regex abstract (used first-page fallback)")
    print(f"  {no_title} had no usable title (used filename stem)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
