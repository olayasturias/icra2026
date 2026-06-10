#!/usr/bin/env python
"""Build data/workshops.json for the ICRA 2026 workshops & tutorials, and
download any accepted workshop papers into ./data/workshop_papers/<slug>/.

Source: each event's dedicated website (scraped 2026-06-09), listed at
https://2026.ieee-icra.org/workshops-and-tutorials/ . For every event we keep
the name, type, day, url, organizers, speakers and scheduled talks, plus the
link to its accepted papers (if any) and the local files we managed to fetch.

Paper PDFs are NOT in the proceedings folder (data/proceedings/data/papers);
they live in a separate data/workshop_papers tree.

Usage:
    python build_workshops.py            # scrape data is inline; downloads papers
    python build_workshops.py --no-download
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
import urllib.error
import http.client
from pathlib import Path

# scripts/workshops/build_workshops.py -> repo root is two parents up.
ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
OUT_JSON = ROOT / "data" / "workshops.json"
PAPERS_ROOT = ROOT / "data" / "workshop_papers"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def slugify(name: str) -> str:
    s = re.sub(r"[^\w\s-]", "", name.lower())
    s = re.sub(r"[\s_-]+", "-", s).strip("-")
    return s[:60]


def normalize_pdf_url(u: str) -> str:
    """Turn a paper page URL into a direct-download URL where possible."""
    # OpenReview: forum?id=X or pdf?id=X  -> pdf?id=X ; attachment links kept.
    m = re.search(r"openreview\.net/(?:forum|pdf)\?id=([\w-]+)", u)
    if m:
        return f"https://openreview.net/pdf?id={m.group(1)}"
    if "openreview.net/attachment" in u:
        return u
    # arXiv abstract -> pdf
    m = re.search(r"arxiv\.org/abs/([\w.\-/]+)", u)
    if m:
        return f"https://arxiv.org/pdf/{m.group(1)}"
    # Google Drive file view -> direct download
    m = re.search(r"drive\.google\.com/file/d/([\w-]+)", u)
    if m:
        return f"https://drive.google.com/uc?export=download&id={m.group(1)}"
    return u


def download(url: str, dest: Path, timeout: int = 90, retries: int = 3) -> bool:
    """Fetch url to dest. Retries with backoff to ride out rate-limiting
    (OpenReview throttles bursts) and transient incomplete reads."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
            # Reject obvious HTML error pages masquerading as a download.
            head = data[:512].lstrip().lower()
            if data[:4] != b"%PDF" and (b"<html" in head or b"<!doctype" in head):
                return False
            if len(data) < 1000:
                return False
            dest.write_bytes(data)
            return True
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
                OSError, http.client.HTTPException):
            if attempt < retries - 1:
                time.sleep(2 + 3 * attempt)
    return False


# --- scraped event data (2026-06-09) ---------------------------------------
# Each: name, type, day, url, organizers, speakers, talks[{title,speaker}],
# accepted_papers_link, paper_pdf_urls[].
WORKSHOPS = json.loads((SCRIPT_DIR / "workshops_raw.json").read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-download", action="store_true", help="skip PDF downloads")
    args = ap.parse_args(argv)

    PAPERS_ROOT.mkdir(exist_ok=True)
    records = []
    dl_ok = dl_fail = 0

    for w in WORKSHOPS:
        slug = slugify(w["name"])
        urls = w.get("paper_pdf_urls") or []
        local_files: list[str] = []

        if urls:
            folder = PAPERS_ROOT / slug
            folder.mkdir(parents=True, exist_ok=True)
            for i, raw in enumerate(urls, 1):
                dl = normalize_pdf_url(raw)
                dest = folder / f"{slug}_{i:02d}.pdf"
                if dest.exists() and dest.stat().st_size > 1000:
                    local_files.append(str(dest.relative_to(ROOT)).replace("\\", "/"))
                    continue
                if args.no_download:
                    continue
                if download(dl, dest):
                    dl_ok += 1
                    local_files.append(str(dest.relative_to(ROOT)).replace("\\", "/"))
                    print(f"  OK  {slug} [{i}/{len(urls)}]")
                else:
                    dl_fail += 1
                    print(f"  XX  {slug} [{i}/{len(urls)}]  {dl}")
                # OpenReview throttles bursts; pace those requests harder.
                time.sleep(2.5 if "openreview.net" in dl else 0.3)

        records.append(
            {
                "name": w["name"],
                "type": w["type"],
                "day": w["day"],
                "url": w["url"],
                "organizers": w.get("organizers", []),
                "speakers": w.get("speakers", []),
                "talks": w.get("talks", []),
                "accepted_papers_link": w.get("accepted_papers_link"),
                "paper_source_urls": urls,
                "paper_files": local_files,
            }
        )

    OUT_JSON.write_text(
        json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    n_papers = sum(1 for r in records if r["accepted_papers_link"])
    print(f"\nWrote {len(records)} events to {OUT_JSON}")
    print(f"  {sum(1 for r in records if r['type']=='workshop')} workshops, "
          f"{sum(1 for r in records if r['type']=='tutorial')} tutorials")
    print(f"  {n_papers} events expose accepted papers")
    print(f"  downloaded {dl_ok} PDFs, {dl_fail} failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
