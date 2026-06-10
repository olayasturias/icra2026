# ICRA 2026 Topic Map — al-folio artifacts

Interactive topic graph of all 3,028 ICRA 2026 papers (2,665 proceedings + 363
workshop papers). Nodes are topics, sized by paper count; edges link topics that
share papers. Click a topic to list its papers; click a title to read the
abstract.

## Files

```
site/
  _pages/topics.md            # al-folio page (layout: page, /topics/)
  assets/js/topic-graph.js    # Cytoscape.js widget (self-contained)
  assets/json/topic_graph.json   # {nodes, edges, meta}
  assets/json/topic_papers.json  # {id: {title, abstract, authors, source, ...}}
  preview.html                # standalone local preview (no Jekyll)
```

## Preview locally

```sh
cd site
python -m http.server 8000
# open http://localhost:8000/preview.html
```

## Install into an al-folio site

Copy these into your al-folio repo at the same paths:

- `_pages/topics.md`            → `_pages/topics.md`
- `assets/js/topic-graph.js`    → `assets/js/topic-graph.js`
- `assets/json/topic_graph.json`  → `assets/json/topic_graph.json`
- `assets/json/topic_papers.json` → `assets/json/topic_papers.json`

Cytoscape + cytoscape-fcose load from a CDN inside `topics.md` (al-folio bundles
ECharts but not a graph library). The page sets
`window.TOPIC_DATA_BASE = "{{ '/assets/json/' | relative_url }}"` so the JS finds
the data under your site's `baseurl`. Build with `bundle exec jekyll serve` and
visit `/topics/`.

## Regenerate the data

```sh
python scripts/workshops/extract_workshop_papers.py   # data/workshop_papers.json
python scripts/topics/make_batches.py                 # shard untagged corpus
#   → tag each data/topics/batches/batch_NNN.json into data/topics/out/batch_NNN.json
#     (Claude Code sub-agents, or scripts/topics/tag_topics.py with an API key)
python scripts/topics/merge_tags.py                   # data/topics/tags.json
python scripts/topics/build_graph.py [--edge-min 6]   # site/assets/json/*.json
```

Topics come from the curated taxonomy in `scripts/topics/taxonomy.py` (43 topics,
8 groups). Tagging is multi-label (1–4 topics/paper); topic↔topic edges are the
co-occurrence counts. Re-running is idempotent and resumable — already-tagged
papers are skipped.
