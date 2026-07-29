# `cocoindex/` — CocoIndex v1 embedding layer

> **The 94+ CocoIndex v1 Apps for the British-Isles Education Pipeline (BIEP v3) + 9 infrastructure indexes + corpus embeddings. Embedder is `BAAI/bge-m3` (1024-d, multilingual).**

## Quick start

```bash
# Verify the canonical lifespan + embedder
python -c "from cocoindex._shared._lifespan import EMBED_MODEL, EMBED_DIM, LANCE_DB; print(EMBED_MODEL, EMBED_DIM, LANCE_DB)"
# Expected: BAAI/bge-m3 1024 rest://lakehouse-lance-namespace:8182

# Run the R1-R4 conformance audit
mise run cocoindex:conformance

# Update a single App
mise run cocoindex:update -- <module>:<App>

# Use CCC (the codebase semantic search)
mise run ccc:search "your query here"
```

## The 9 sub-trees

| Sub-tree | Purpose |
|:--|:--|
| `_shared/` | The canonical shared home (`_lifespan.py` + `cli.py` + `languages.py` + `caighdean_standardize.py` + `reranker.py` + `repo_embedding.py` + `repo_type_detector.py`) |
| `biep_parity/` | 14 explicit Apps + 88 Ireland JC factory Apps + 147 England A-Level factory Apps + 129 England GCSE factory Apps = **378 Apps in this dir** |
| `british_isles/` | Per-nation Apps for England (AQA/OCR/Edexcel/A-Level) + Ireland (5 ie_law modules + canuint + ireland_legal_embedding) |
| `celtic/` | Celtic-language family Apps: Gaeilge, UD Celtic, Gaois (NLI), Mythology, Multilingual, Curriculum |
| `commonwealth/` | Australia + Canada-Quebec + India + Nigeria + New-Zealand + South-Africa per-jurisdiction Apps |
| `corpus/` | The big shared-corpus Apps: `leabharlann_embedding` (38KB), `unified_embedding` (22KB), `university_embedding`, `government_circulars_embedding`, `duchas_embedding`, `local_documents_embedding`, `root_pdfs_embedding` |
| `european_nations/` | 40 per-country sub-dirs; each has one `education_embedding.py` |
| `european_nations_cross/` | Cross-EU-wide Apps: `law_embedding`, `medicine_embedding`, `education_embedding` |
| `european_union/` | EU-wide: `official_embedding`, `eu_multilingual_alignment_embedding` |
| `american_nations/` | US-California (only nation currently populated) |
| `infrastructure/` | Codebase + API + filesystem + storage + config indexing + `cocoindex_v1_conformance.py` (the R1-R4 linter) |
| `knowledge_graph/` | `youtube_kg_embedding`, `file_graph`, `multihop_search`, `terminology_linking` |
| `media/` | Apple Photos (4 variants) + OCR + Artwork + Computer-Vision embeddings |
| `portfolio/` | Personal `heritage_embedding` + `culture_heritage_embedding` |
| `subjects/` | Cross-subject competency + JC + LC + education_subject embeddings |

## The R1-R4 conformance contract

`infrastructure/cocoindex_v1_conformance.py:13–31` enforces the
4-rule R1-R4 contract at scaffold time by static AST inspection of
every v1 App module:

| Rule | Meaning |
|:--|:--|
| **R1** | The App imports from `.._shared._lifespan` (or `..._shared._lifespan` for 3-deep dirs, etc.) |
| **R2** | No new `coco.ContextKey[` declared outside `_lifespan.py` without `# R2-exempt:` comment |
| **R3** | `app = coco.App(coco.AppConfig(...))` (or any name ending in `_app` / `_embedding` / `_App`) at module scope |
| **R4** | At least one `@coco.fn(` decorator is present |

## The LanceDB namespace convention

All CocoIndex v1 Apps write to **LanceDB**:

- BIEP v3 per-jurisdiction (LC): `cianhoghlaim.<jurisdiction>.<stage>.<subject>.<level>_<lang>_chunks`
- BIEP v3 per-jurisdiction (A-Level/GCSE): `cianhoghlaim.<jurisdiction>.<stage>.<board>.<subject>_<...>_chunks`
- BIEP v1 corpus: `cianhoghlaim.<vertical>.<sub>.<level>_<lang>` (e.g. `cianhoghlaim.lc.gaeilge.hl_ga`)
- Infrastructure indexes: bare names (`codebase_chunks`, `codebase_graph`, `codebase_graph_edges`)

## Cross-references

- [`AGENTS.md`](AGENTS.md) — the canonical quadrant overview
- [`_shared/_lifespan.py`](_shared/_lifespan.py) — the canonical lifespan + embedder home
- [`../.agents/skills/cocoindex/SKILL.md`](../.agents/skills/cocoindex/SKILL.md) — the CocoIndex master skill
- [`../.agents/skills/lancedb/SKILL.md`](../.agents/skills/lancedb/SKILL.md) — the LanceDB vector store
- [`../openspec/specs/british-isles-education-pipeline/spec.md`](../openspec/specs/british-isles-education-pipeline/spec.md) — flagship BIEP spec
- [`../LEGACY_ALIASES.md`](LEGACY_ALIASES.md) — the v7 ISO-3 → snake_case rename map (historical)