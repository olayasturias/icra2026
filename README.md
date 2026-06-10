# ICRA 2026 conference stats

Extracts structured metadata from the ICRA 2026 conference for analysis.

## Repository layout

```
scripts/
  proceedings/            # the main paper proceedings
    build_metadata.py     # -> data/metadata.json
    manual_overrides.json # hand-sourced abstracts for un-extractable PDFs (committed)
  workshops/              # workshops & tutorials
    build_workshops.py    # -> data/workshops.json (+ downloads workshop papers)
    workshops_raw.json    # hand-assembled scrape of the 74 event pages (committed)
    arxiv_search.py       # helper: match workshop paper titles to arXiv
    workshop_titles.json  # input for arxiv_search (committed)
  stats/                  # statistics figures (Manim animations)
    naming_stats.py       # extraction: metadata.json -> data/stats/naming.json
    render_naming.py      # render the naming figure to mp4 + GIF + PNG
    scenes/naming.py      # Manim scene "How ICRA 2026 names things"
data/                     # inputs + generated outputs (gitignored)
  proceedings/            # the downloaded proceedings package (PDFs)
  workshop_papers/        # downloaded accepted workshop papers
  metadata.json           # output: one record per proceedings paper
  workshops.json          # output: one record per workshop/tutorial
  stats/                  # output: extracted stats JSON per figure
  charts/                 # output: rendered figures (mp4 / gif / png)
scratch/                  # throwaway analysis artifacts (gitignored)
.venv/                    # isolated env for the Manim stack (gitignored)
```

Scripts compute the repo root from their own location, so run them from
anywhere. Committed inputs live next to their script under `scripts/`; bulky
PDFs and generated JSON live under the gitignored `data/`.

## Proceedings metadata

`scripts/proceedings/build_metadata.py` builds `data/metadata.json` — one record
per paper PDF, with fields: `title`, `keywords`, `id` (= paper PDF filename, e.g.
`0011`), `code` (repo/project-page URL, or `""`), `visual` (bool — has an uploaded
supplementary video), `abstract`, `authors`.

### Input layout (`data/proceedings/`, not committed)

```
data/proceedings/
  TopMenu.pdf
  data/
    TOC.pdf            # program: title + authors + a link to each paper PDF
    AuthorIndex.pdf
    ConfInfo.pdf, Program.pdf, Welcome.pdf
    papers/NNNN.pdf    # 2665 paper PDFs
```

### Run

```bash
pip install -r requirements.txt
python scripts/proceedings/build_metadata.py            # all papers -> data/metadata.json
python scripts/proceedings/build_metadata.py --limit 20 # first N (dev)
```

## How it works

Two sources are joined on the paper id:

- **TOC.pdf -> title, authors, id.** Each program entry is `<session code>`,
  then the title ending in `, pp. X-Y.`, then alternating author/affiliation
  lines. The paper id comes from the hyperlink drawn on the title text, matched
  to the entry by **vertical bbox overlap** of the link rect with the title line
  (robust to the file-number order differing from program order, to titles that
  wrap across page breaks, and to entries with no page range).
- **papers/NNNN.pdf -> abstract, keywords**, read from the IEEE first page
  (`Abstract-- ...`, `Index Terms/Keywords-- ...`).

Papers on disk drive the output; title/authors fall back to the paper PDF's own
first page when an id is absent from the TOC.

## Coverage (2665 papers)

| field    | filled | note |
|----------|--------|------|
| title    | 2665   | 100% |
| authors  | 2665   | 7 not in the TOC fall back to the paper's author block ("First Last" vs the TOC's "Last, First") |
| abstract | 2665   | 4 sourced via `manual_overrides.json` (see below) |
| keywords | 758    | only ~28% of papers print an `Index Terms` block; it is optional in the IEEE template |
| code     | 922    | URL of the paper's code repo / project page, when the PDF links one |
| visual   | 1733   | has an uploaded supplementary video (see below) |

### Visuals

`visual` is `true` when the paper has an uploaded visual (supplementary video).
The live rasevents site (`rasevents.org/event.php?id=167`) is login-gated and not
reachable here, but the TOC -- generated from the same program database -- links
a `papers/NNNN_VI_fi.mp4` for every paper that has one (this exactly equals the
`Attachment` marker in the program: 1772 of them). 1733 of those map to on-disk
papers. The video files themselves are not in the downloaded package.

### Code links

`code` is the URL of the paper's own repository or project page (GitHub, GitLab,
Bitbucket, `*.github.io`, Hugging Face), scanned from all pages' text and the PDF
hyperlink annotations. To separate the paper's code from cited tools, a repo is
taken when introduced by a code-intent phrase ("code available at", "project
page", "we release", …) or when it is the only repo link in the paper; when
several repos appear with no such cue it is left empty (avoids tagging a
dependency). Line-wrapped URLs are rejoined and common library repos (opencv,
pytorch, mmsegmentation, …) are filtered out. A few cited tools still slip
through; treat `code` as high-but-not-perfect precision.

### `manual_overrides.json`

Four papers have no extractable abstract in their PDF text layer and are filled
from this committed file (applied by the build, overriding the extracted values):

- **6332** — image-only T-RO reprint; its labeled `Abstract`/`Index Terms` were
  transcribed from the rendered first page.
- **5806, 6166, 6109** — IEEE R&A *Magazine* articles with no `Abstract` label;
  the value is the article's editorial lead/summary paragraph (taken verbatim
  from the PDF text), which is the abstract-equivalent.

The extractor also normalises a common font artifact where the em-dash renders
as `Ð` (e.g. `AbstractÐ`, `Index TermsÐ`) and searches the first two pages, since
some papers put the abstract on page 1 and its terminating heading on page 2.

Authors are stored as printed in the program ("Last, First"). The `MuPDF error:
cmsOpenProfileFromMem` lines during a run are harmless image-colour-profile
warnings.

## Workshops & tutorials metadata

`scripts/workshops/build_workshops.py` reads the committed
`scripts/workshops/workshops_raw.json` (a hand-assembled scrape of the 74 event
pages) and writes `data/workshops.json` — per event: name, type (workshop /
tutorial), day, url, organizers, speakers, talks, accepted-papers link, and the
locally downloaded paper files. It also downloads any accepted workshop papers
into `data/workshop_papers/<slug>/`.

```bash
python scripts/workshops/build_workshops.py               # build + download papers
python scripts/workshops/build_workshops.py --no-download  # metadata only
```

## Statistics figures (Manim)

Conference statistics are visualised as animated figures, built one at a time.
Each figure is a clean split: a **pure extraction** step (stdlib only, writes a
small JSON) and a **Manim scene** that animates that JSON. Style mirrors the
sibling `cvpr2026` dashboard (accent blue on white); text only, no LaTeX.

### Setup (isolated venv — required)

Manim pulls numpy 2.x / scipy and clashes with a conda base env, so install it
in a project venv:

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # manim + imageio-ffmpeg
```

No system `ffmpeg`/LaTeX needed: the render wrapper exposes the
`imageio-ffmpeg` binary as `ffmpeg`, and scenes use Manim `Text`.

### Figure 1 — "How ICRA 2026 names things"

Title-linguistics of the 2665 proceedings titles, re-derived from this corpus
(the CVPR clichés — "all you need", "Towards…", "?" — are near-absent at ICRA).

```bash
.venv/Scripts/python scripts/stats/naming_stats.py    # -> data/stats/naming.json
.venv/Scripts/python scripts/stats/render_naming.py   # -> data/charts/{mp4,gif,png}
```

`render_naming.py` produces three artifacts from one scene: a 1080p mp4, a 480p
looping GIF, and a final-frame PNG poster (under `data/charts/...`).

**Five panels**, animated as a sequence:
1. **Title patterns** — colon, `"X for Y"`, `with`, `via`, `using`, hyphenated
   compound, `'X Anything'` (Segment/Depth-Anything trope), `?`.
2. **Title length** — word-count histogram (median 12).
3. **How titles open** — first-word counts (Learning, A, Design, Real-Time…).
4. **Most-reused acronyms / tech terms** — SLAM, LiDAR, UAV, MPC, LLM…
5. **Domain themes** — learning, manipulation, navigation, human-robot, …,
   place recognition/VPR, neuromorphic, tactile, soft robotics.

**Animation behaviour (in each bar panel):** rows cascade top→bottom — a row's
name appears, then its bar loads from 0 to its value while the count label rides
the bar's tip and ticks up 0→value (with %); a short offset after each bar
starts, the next row begins. Implemented with a per-row `ValueTracker` +
`always_redraw` (drives bar width, label position and the number together) inside
a `Succession(name, bar-load)` per row, staggered by `LaggedStart`.

**Adding a theme/pattern:** edit the `THEMES` or `PATTERNS` table in
`scripts/stats/naming_stats.py` (a label → regex / predicate), then re-run the
two commands above. Each new entry slots into its panel automatically.
