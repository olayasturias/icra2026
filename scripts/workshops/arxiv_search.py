#!/usr/bin/env python
"""Search arXiv for each workshop accepted-paper title in workshop_titles.json.
Writes workshop_titles_arxiv.json: {workshop_name: [{title, arxiv}]} for matches
scoring >= THRESH. Strict, to avoid mis-attributing unrelated papers.

Helper/analysis script (not part of the build_workshops pipeline)."""
import urllib.request, urllib.parse, re, time, json
from difflib import SequenceMatcher
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ua = {"User-Agent": "Mozilla/5.0 (research; mailto:oat@eiva.com)"}
THRESH = 0.85
titles = json.loads((SCRIPT_DIR / "workshop_titles.json").read_text(encoding="utf-8"))


def norm(s):
    return re.sub(r"[^a-z0-9 ]", " ", s.lower()).split()


def jac(a, b):
    A, B = set(norm(a)), set(norm(b))
    return len(A & B) / len(A | B) if A | B else 0


def search(title):
    key = title.split(":")[0]
    words = [w for w in norm(title) if len(w) > 2]
    for qs in [f'ti:"{key}"', "all:" + " ".join(words[:11])]:
        qy = urllib.parse.urlencode({"search_query": qs, "max_results": 8})
        try:
            xml = urllib.request.urlopen(
                urllib.request.Request(f"http://export.arxiv.org/api/query?{qy}", headers=ua),
                timeout=40,
            ).read().decode("utf-8", "replace")
        except Exception:
            time.sleep(3)
            continue
        best = None
        for e in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
            at = re.search(r"<title>(.*?)</title>", e, re.S)
            ai = re.search(r"<id>(.*?)</id>", e, re.S)
            if not at:
                continue
            atitle = re.sub(r"\s+", " ", at.group(1)).strip()
            sc = max(SequenceMatcher(None, title.lower(), atitle.lower()).ratio(), jac(title, atitle))
            if best is None or sc > best[0]:
                best = (sc, atitle, ai.group(1).strip() if ai else "")
        time.sleep(3)
        if best and best[0] >= THRESH:
            m = re.search(r"arxiv\.org/abs/([\w.]+)", best[2])
            return (best[0], m.group(1) if m else "", best[1])
    return None


out = {}
total = found = 0
for name, ts in titles.items():
    hits = []
    for t in ts:
        total += 1
        r = search(t)
        if r:
            found += 1
            hits.append({"title": t, "arxiv": r[1], "score": round(r[0], 2)})
            print(f"  OK  {r[1]}  {t[:50]}")
        else:
            print(f"  --  {t[:55]}")
    out[name] = hits
    print(f"== {name[:45]}: {len(hits)}/{len(ts)}")
(SCRIPT_DIR / "workshop_titles_arxiv.json").write_text(
    json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8"
)
print(f"\nFOUND {found}/{total}")
