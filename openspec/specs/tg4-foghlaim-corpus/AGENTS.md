# `tg4-foghlaim-corpus/` — TG4 + Foghlaim Media Corpus

> The canonical home for the TG4.ie player catalog + Foghlaim.tg4.ie lesson
> corpus as a multimodal Irish-language dataset (subtitles + audio audit +
> frame captions + BAML triples + worksheet answers). Added by the
> `2026-08-25-tg4-foghlaim-corpus-v1` change.

## Routing

Load this AGENTS.md when:

- You need to add / modify a DLT source that scrapes TG4.ie or foghlaim.tg4.ie
- You need to wire a new BAML fn (ClassifyTg4Episode / ExtractSpeakerLineup /
  ExtractWorksheetAnswers / AuditTranscriptQuality) into the TG4 v1 App
- You need to extend the `biep_subject` taxonomy
- You need to re-run the daily TG4 player catalog refresh

## Quick start

```bash
# Run the 2 DLT sources
uv run python -m dlt_sources.cli run-pipeline tg4_player_shows
uv run python -m dlt_sources.cli run-pipeline foghlaim_lessons

# Open the marimo corpus notebook
marimo edit notebooks/41_tg4_foghlaim_corpus.py

# Materialise the Dagster asset group (requires mise.toml sync:tg4-all)
mise run sync:tg4-all

# Validate against the openspec
openspec validate 2026-08-25-tg4-foghlaim-corpus-v1 --strict
```

## Key sources

| Path | Why it matters |
|:--|:--|
| `dlt_sources/api_sources/tg4_player_shows.py` | The TG4 player catalog scraper (8 genres + Bailiúcháin) |
| `dlt_sources/api_sources/foghlaim_lessons.py` | The Foghlaim Nuxt.js lesson scraper |
| `baml_src/media/tg4_classification.baml` | 4 BAML fns: classify, speakers, worksheets, audit |
| `cocoindex_flows/media/tg4_foghlaim_embedding.py` | The R1–R4 v1 App (4 LanceDB tables) |
| `orchestration/defs/2_materials/tg4_foghlaim/` | The 6 Dagster assets |
| `notebooks/41_tg4_foghlaim_corpus.py` | The 5-tab marimo notebook |

## Adjacent specs

- [`british-isles-education-pipeline-v3`](../british-isles-education-pipeline-v3/spec.md)
  — the destination spec for the 2 ADDED Requirements that link TG4 +
  Foghlaim into the BIEP v3 subject taxonomy
- [`multimodal-code-and-media-intel`](../multimodal-code-and-media-intel/spec.md)
  — the sibling capability (YouTube KG Phase 1 + local media Phase 5)
- [`celtic-language-pipeline`](../celtic-language-pipeline/spec.md) —
  the downstream consumer

## DO NOT

- **Never** download MP4 files unless `TG4_DOWNLOAD_MEDIA=full` is
  explicitly set. The default is metadata-only + VTT + frame captions.
- **Never** use a literal HuggingFace model ID — route through
  `meaisinfhoghlaim.models.registry.MODEL_REGISTRY`.
- **Never** edit `openspec/specs/tg4-foghlaim-corpus/spec.md` directly —
  only the deltas under `openspec/changes/<id>/specs/tg4-foghlaim-corpus/spec.md`.

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`openspec`](../../../.agents/skills/openspec/SKILL.md) | Spec delta format + validation |
| [`dlt`](../../../.agents/skills/dlt/SKILL.md) | DLT source canonical pattern |
| [`baml`](../../../.agents/skills/baml/SKILL.md) | BAML schema authoring |
| [`cocoindex`](../../../.agents/skills/cocoindex/SKILL.md) | R1–R4 conformance + LanceDB targets |
| [`dagster`](../../../.agents/skills/dagster/SKILL.md) | 5-layer KCG component + asset authoring |
| [`centralized-registry`](../../../.agents/skills/centralized-registry/SKILL.md) | MODEL_REGISTRY + schema introspection |
| [`dignified-python`](../../../.agents/skills/dignified-python/SKILL.md) | Production Python standards |

<!-- generated: 2026-08-25; do not hand-edit -->