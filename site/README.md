# ICRA 2026 Interactive Maps — al-folio artifacts

Two interactive graphs of all 3,028 ICRA 2026 papers (2,665 proceedings + 363
workshop papers), sharing one Cytoscape.js widget and one paper-metadata file:

- **Topic map** — 43 research topics (`topic_graph.json`).
- **Platform map** — 16 robot platforms / embodiments, aerial · ground · marine ·
  humanoid · manipulator · … (`platform_graph.json`).

Nodes are sized by paper count; edges link categories that share papers. Search
by title/author, click a node to list its papers, click a title for the abstract.

## Files

```
site/
  _pages/topics.md    _pages/platforms.md       # al-folio pages (/topics/, /platforms/)
  assets/js/topic-graph.js                      # shared Cytoscape.js widget
  assets/json/topic_graph.json                  # topic map: {nodes,edges,meta}
  assets/json/platform_graph.json               # platform map: {nodes,edges,meta}
  assets/json/topic_papers.json                 # shared {id:{title,abstract,...}}
  preview.html   preview-platforms.html         # standalone local previews
```

A page selects which graph to load via `window.TOPIC_GRAPH_FILE`
(`topic_graph.json` by default, `platform_graph.json` for the platform map);
both reuse `topic_papers.json`. Node colours + the legend come from each graph's
`meta.groups`, so the same JS renders either map.

## Preview locally

```sh
cd site
python -m http.server 8000
# open http://localhost:8000/preview.html            (topics)
#  and  http://localhost:8000/preview-platforms.html  (platforms)
```

## Install into an al-folio site

Copy these into your al-folio repo at the same paths:

- `_pages/topics.md`, `_pages/platforms.md`   → `_pages/`
- `assets/js/topic-graph.js`                  → `assets/js/`
- `assets/json/topic_graph.json`, `platform_graph.json`, `topic_papers.json` → `assets/json/`

Cytoscape + cytoscape-fcose load from a CDN inside `topics.md` (al-folio bundles
ECharts but not a graph library). The page sets
`window.TOPIC_DATA_BASE = "{{ '/assets/json/' | relative_url }}"` so the JS finds
the data under your site's `baseurl`. Build with `bundle exec jekyll serve` and
visit `/topics/`.

## Regenerate the data

The pipeline is taxonomy-agnostic via `--kind {topics,platforms}`:

```sh
python scripts/workshops/extract_workshop_papers.py        # data/workshop_papers.json (once)

# For each KIND in {topics, platforms}:
python scripts/topics/make_batches.py  --kind KIND          # shard untagged corpus
#   → tag each data/KIND/batches/batch_NNN.json into data/KIND/out/batch_NNN.json
#     (Claude Code sub-agents reading data/KIND/taxonomy.txt, or tag_topics.py + API key)
python scripts/topics/merge_tags.py    --kind KIND          # data/KIND/tags.json
python scripts/topics/build_graph.py   --kind KIND [--edge-min 6]   # site/assets/json/<prefix>_graph.json
```

Categories come from curated taxonomies: `scripts/topics/taxonomy.py` (43 topics,
8 groups) and `scripts/topics/taxonomy_platform.py` (16 platforms, 9 groups) —
each defines `GROUP_COLORS`, baked into the graph JSON as node colours +
`meta.groups`. Tagging is multi-label (1–4 categories/paper); edges are
co-occurrence counts. Re-running is idempotent and resumable.
