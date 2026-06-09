# ICRA 2026 proceedings metadata

Builds `data/metadata.json` from the ICRA 2026 proceedings downloaded from the
ICRA website. One record per paper PDF, with fields: `title`, `keywords`, `id`
(= paper PDF filename, e.g. `0011`), `code` (repo/project-page URL, or `""`),
`abstract`, `authors`.

## Input layout (`data/raw/`, not committed)

```
data/raw/
  TopMenu.pdf
  data/
    TOC.pdf            # program: title + authors + a link to each paper PDF
    AuthorIndex.pdf
    ConfInfo.pdf, Program.pdf, Welcome.pdf
    papers/NNNN.pdf    # 2665 paper PDFs
```

## Run

```bash
pip install -r requirements.txt
python build_metadata.py            # all papers -> data/metadata.json
python build_metadata.py --limit 20 # first N (dev)
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
