#!/usr/bin/env python
"""Build data/metadata.json for the ICRA 2026 proceedings.

Two sources, joined on the paper id (= paper PDF filename, e.g. "0011"):

  * TOC.pdf  -> title + authors + id. Each program entry has the shape
        <session code>            e.g. TuI1I.1
        <title ...>, pp. X-Y.     (optionally followed by "Attachment")
        <Author Last, First>      alternating with affiliation lines
        ...
    and a hyperlink on the title pointing at papers/NNNN.pdf, which is how we
    recover the id (program order is NOT the file-number order).

  * papers/NNNN.pdf -> abstract + keywords, read from the IEEE first page
    ("Abstract-- ..." and "Index Terms/Keywords-- ...").

Papers on disk drive the output. Title/authors come from the TOC when the id is
found there, otherwise they fall back to the paper PDF's own first page.

Usage:
    python build_metadata.py            # all papers
    python build_metadata.py --limit 20 # first N (dev)
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw" / "data"
TOC_PDF = RAW / "TOC.pdf"
PAPERS_DIR = RAW / "papers"
OUT_JSON = ROOT / "data" / "metadata.json"
# Hand-sourced abstract/keywords for papers whose text layer has none (image-only
# scans, or magazine articles with no "Abstract" label). See the file's _note.
OVERRIDES_JSON = ROOT / "manual_overrides.json"


def load_overrides() -> dict[str, dict]:
    if not OVERRIDES_JSON.exists():
        return {}
    return json.loads(OVERRIDES_JSON.read_text(encoding="utf-8")).get("overrides", {})

# --- regexes ---------------------------------------------------------------

CODE = re.compile(r"^[A-Z][a-z][A-Za-z0-9]+\.\d+$")          # e.g. TuI1I.1
PP = re.compile(r"(?<![A-Za-z])pp\.")                        # "pp." page marker.
#   The page numbers and even the comma can wrap onto adjacent lines, so match
#   the literal "pp." (not preceded by a letter, to skip "app."/"Supp.").
NAME = re.compile(r"^[A-Z][\w'’.\-]+(?: [A-Z][\w'’.\-]+)*,\s+[A-Z].*$")
TIME = re.compile(r"^\d{1,2}:\d{2}-\d{1,2}:\d{2}$")          # "09:00-10:30"
PAPER_LINK = re.compile(r"papers/(\d+)\.pdf$")


def title_ends(line: str) -> bool:
    """A title runs until the page marker, the first author, a session time,
    or an 'Attachment' tag -- some entries have no 'pp.' page range at all."""
    return bool(
        CODE.match(line)
        or PP.search(line)
        or NAME.match(line)
        or TIME.match(line)
        or line == "Attachment"
    )

# "I. INTRODUCTION" but also "1. INTRODUCTION", "II. INTRODUCTION", etc.
_INTRO = r"^\s*(?:[IVXivx]+|\d+)\.?\s+INTRODUCTION"

ABSTRACT = re.compile(
    r"Abstract\s*[—:\-]\s*(.+?)(?=(?:Index\s+Terms|Keywords?)\s*[—:\-]|"
    + _INTRO + ")",
    re.IGNORECASE | re.DOTALL | re.MULTILINE,
)
# Fallback for papers whose abstract has no "Index Terms"/"Introduction" on the
# first page, or a plain "Abstract" heading with no dash: separator optional,
# and a blank line also terminates (most ICRA abstracts are one paragraph).
ABSTRACT_LOOSE = re.compile(
    r"Abstract\b\s*[—:\-]?\s*(.+?)(?=(?:Index\s+Terms|Keywords?)\s*[—:\-]|"
    + _INTRO + r"|\n\s*\n)",
    re.IGNORECASE | re.DOTALL | re.MULTILINE,
)
# Index Terms is a single period-terminated list of comma-separated phrases, so
# the first sentence-ending period is the most reliable boundary; the rest are
# fallbacks for papers that omit the period.
KEYWORDS = re.compile(
    r"(?:Index\s+Terms|Keywords?)\s*[—:\-]\s*(.+?)"
    r"(?=\.\s|\.$|\n\s*\n|" + _INTRO + r"|Manuscript\b|Digital\s+Object|©|\S+@\S+"
    r"|\b(?:19|20)\d{2}\b)",
    re.IGNORECASE | re.DOTALL | re.MULTILINE,
)


# Zero-width / invisible chars that the PDFs sprinkle into text and that would
# otherwise break markers like "pp." or "Index Terms".
ZW = str.maketrans("", "", "​‌‍﻿\xad")


def clean(text: str) -> str:
    text = text.translate(ZW)
    text = re.sub(r"-\n", "", text)      # join hyphenated line breaks
    text = re.sub(r"\s+", " ", text)
    return text.strip(" ,")


# --- TOC parsing -----------------------------------------------------------


def parse_toc() -> dict[str, dict]:
    """Return {id: {"title": str, "authors": [str]}} from TOC.pdf."""
    doc = fitz.open(TOC_PDF)

    # Line stream as (page, y0, y1, text) and per-page paper links as
    # (y0, y1, id). The title hyperlink is physically drawn on the title text,
    # so a link is matched to the entry whose title line its rect overlaps.
    lines: list[tuple[int, float, float, str]] = []
    links: dict[int, list[tuple[float, float, str]]] = {}
    for pno, page in enumerate(doc):
        d = page.get_text("dict")
        for block in d["blocks"]:
            for ln in block.get("lines", []):
                txt = "".join(s["text"] for s in ln["spans"]).translate(ZW).strip()
                if txt:
                    y0, y1 = ln["bbox"][1], ln["bbox"][3]
                    lines.append((pno, round(y0, 1), round(y1, 1), txt))
        page_links = []
        for l in page.get_links():
            m = PAPER_LINK.search(l.get("file", "") or "")
            if m:
                r = l["from"]
                page_links.append((round(r.y0, 1), round(r.y1, 1), m.group(1)))
        links[pno] = page_links

    def resolve_id(spans: list[tuple[int, float, float]]) -> str | None:
        """Id of the link whose rect best overlaps the entry's title lines.

        Falls back to the vertically nearest link on a title page when no rect
        overlaps (a few entries' link rects are drawn just off the text line).
        """
        best: tuple[float, str] | None = None        # (overlap, id)
        nearest: tuple[float, str] | None = None      # (gap, id)
        for pno, ly0, ly1 in spans:
            lc = (ly0 + ly1) / 2
            for ky0, ky1, pid in links.get(pno) or []:
                overlap = min(ly1, ky1) - max(ly0, ky0)
                if overlap > 0 and (best is None or overlap > best[0]):
                    best = (overlap, pid)
                gap = abs((ky0 + ky1) / 2 - lc)
                if nearest is None or gap < nearest[0]:
                    nearest = (gap, pid)
        if best:
            return best[1]
        # Only accept a nearby (non-overlapping) link, not an arbitrary far one.
        if nearest and nearest[0] < 15:
            return nearest[1]
        return None

    result: dict[str, dict] = {}
    i, n = 0, len(lines)
    while i < n:
        if not CODE.match(lines[i][3]):
            i += 1
            continue
        i += 1  # consume code line

        # Title: lines until the page marker / first author / time / Attachment.
        title_parts: list[str] = []
        title_spans: list[tuple[int, float, float]] = []
        while i < n and not title_ends(lines[i][3]):
            title_spans.append(lines[i][:3])
            title_parts.append(lines[i][3])
            i += 1
        # If we stopped on the "pp." line, keep any title text before "pp.".
        if i < n and (m := PP.search(lines[i][3])) and not CODE.match(lines[i][3]):
            title_spans.append(lines[i][:3])
            pre = lines[i][3][: m.start()].rstrip(", ")
            if pre:
                title_parts.append(pre)
            i += 1

        # Authors: NAME-matching lines until the next entry code.
        authors: list[str] = []
        while i < n and not CODE.match(lines[i][3]):
            if NAME.match(lines[i][3]):
                authors.append(lines[i][3])
            i += 1

        pid = resolve_id(title_spans)
        if pid and pid not in result:
            result[pid] = {"title": clean(" ".join(title_parts)), "authors": authors}
    return result


# --- paper PDF parsing -----------------------------------------------------


def pdf_title(page: fitz.Page) -> str:
    """Largest-font text in the top third of the first page (fallback title)."""
    info = page.get_text("dict")
    h = page.rect.height
    spans = [
        s
        for b in info["blocks"]
        for ln in b.get("lines", [])
        for s in ln["spans"]
        if s["bbox"][1] < h * 0.33 and s["text"].strip()
    ]
    if not spans:
        return ""
    mx = max(s["size"] for s in spans)
    top = [s for s in spans if s["size"] >= mx - 0.5]
    top.sort(key=lambda s: (round(s["bbox"][1]), s["bbox"][0]))
    return clean(" ".join(s["text"] for s in top))


_STOP_AUTH = re.compile(
    r"@|http|^\d|Universit|Institut|Department|Laborator|School|Faculty"
    r"|Cent(?:er|re)|Academy|College|Ministry|Email|Politecnico|Corporation"
    r"|Robotics and Automation Letters",
    re.IGNORECASE,
)
_MEMBER = re.compile(
    r"(?i)\b(?:student|senior|graduate)?\s*(?:member|fellow)\s*(?:member)?\s*,?\s*ieee\b"
)
_MARKS = re.compile(r"[\d\*∗†‡§¶∥]+")
_NAME_PIECE = re.compile(r"[A-Z][\w.'’\-]*(?: [A-Za-z][\w.'’\-]*){1,4}")


def _is_author_line(t: str) -> bool:
    """A line of one or more "First Last" names (commas / 'and' separated)."""
    if _STOP_AUTH.search(t):
        return False
    cleaned = _MARKS.sub("", _MEMBER.sub("", t)).strip(" ,")
    pieces = [p.strip() for p in re.split(r",|\band\b|&", cleaned) if p.strip()]
    return bool(pieces) and all(_NAME_PIECE.fullmatch(p) for p in pieces)


def pdf_authors(page: fitz.Page) -> list[str]:
    """Author names from the block between the title and the abstract.

    Used only as a fallback for papers absent from the TOC. Names come out in
    "First Last" form (the PDF order), unlike the TOC's "Last, First".
    """
    info = page.get_text("dict")
    h = page.rect.height
    rows: list[tuple[float, float, str]] = []  # (y0, size, text)
    for b in info["blocks"]:
        for ln in b.get("lines", []):
            txt = "".join(s["text"] for s in ln["spans"]).translate(ZW).strip()
            if txt:
                size = max(s["size"] for s in ln["spans"])
                rows.append((ln["bbox"][1], size, txt))
    rows.sort()
    # Stop at the abstract.
    for k, (_, _, t) in enumerate(rows):
        if re.match(r"(?i)abstract\b", t):
            rows = rows[:k]
            break
    top = [s for y, s, _ in rows if y < h * 0.33]
    if not top:
        return []
    title_size = max(top)
    last_title_y = max((y for y, s, _ in rows if s >= title_size - 0.5), default=0.0)

    # Author lines: the contiguous run of name lines just below the title.
    auth_lines: list[str] = []
    for y, _, t in rows:
        if y <= last_title_y:
            continue
        if not _is_author_line(t):
            break
        auth_lines.append(t)

    s = _MEMBER.sub("", ", ".join(auth_lines))
    s = _MARKS.sub("", s)
    out, seen = [], set()
    for part in re.split(r",|\band\b|&", s):
        name = part.strip(" ,.")
        if len(name) >= 3 and re.search(r"[A-Za-z]", name) and name not in seen:
            seen.add(name)
            out.append(name)
    return out


def parse_paper(pdf: Path) -> dict:
    """Return abstract, keywords, and a fallback title from a paper PDF."""
    with fitz.open(pdf) as doc:
        title = pdf_title(doc[0])
        authors = pdf_authors(doc[0])
        # Some papers put the abstract on page 1 but its terminating "Index
        # Terms"/"Introduction" heading on page 2, so search both pages. Normal
        # papers still match their page-1 terminator first, so they're unchanged.
        text = "\n".join(
            doc[p].get_text("text") for p in range(min(2, doc.page_count))
        ).translate(ZW)
    # Some Type-1-font PDFs render the em-dash as "Ð" (e.g. "AbstractÐ ...",
    # "Index TermsÐ ..."), which hides the marker from the regexes below.
    text = text.replace("Ð", "—")
    ab = ABSTRACT.search(text) or ABSTRACT_LOOSE.search(text)
    kw = KEYWORDS.search(text)
    keywords: list[str] = []
    if kw:
        raw = clean(kw.group(1)).rstrip(".")
        keywords = [
            re.sub(r"^and\s+", "", k.strip(), flags=re.IGNORECASE)
            for k in re.split(r"[;,]", raw)
            if k.strip()
        ]
    return {
        "title": title,
        "authors": authors,
        "abstract": clean(ab.group(1)) if ab else "",
        "keywords": keywords,
    }


# --- driver ----------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="process first N papers")
    args = ap.parse_args(argv)

    print("Parsing TOC.pdf ...")
    toc = parse_toc()
    print(f"  {len(toc)} entries mapped to paper ids")

    overrides = load_overrides()
    pdfs = sorted(PAPERS_DIR.glob("*.pdf"))
    if args.limit:
        pdfs = pdfs[: args.limit]
    print(f"Reading {len(pdfs)} paper PDFs ...")

    records, no_toc, applied = [], 0, 0
    for idx, pdf in enumerate(pdfs, 1):
        pid = pdf.stem
        meta = parse_paper(pdf)
        toc_entry = toc.get(pid)
        if toc_entry:
            title, authors = toc_entry["title"], toc_entry["authors"]
        else:
            no_toc += 1
            title, authors = meta["title"], meta["authors"]
        abstract, keywords = meta["abstract"], meta["keywords"]
        if ov := overrides.get(pid):
            applied += 1
            abstract = ov.get("abstract", abstract)
            keywords = ov.get("keywords", keywords)
        records.append(
            {
                "title": title or meta["title"],
                "keywords": keywords,
                "id": pid,
                "abstract": abstract,
                "authors": authors,
            }
        )
        if idx % 250 == 0:
            print(f"  {idx}/{len(pdfs)}")

    OUT_JSON.write_text(
        json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    no_abstract = sum(1 for r in records if not r["abstract"])
    print(f"\nWrote {len(records)} records to {OUT_JSON}")
    print(f"  {no_toc} papers had no TOC entry (title & authors from the PDF)")
    print(f"  {applied} manual overrides applied")
    print(f"  {no_abstract} papers still have no abstract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
