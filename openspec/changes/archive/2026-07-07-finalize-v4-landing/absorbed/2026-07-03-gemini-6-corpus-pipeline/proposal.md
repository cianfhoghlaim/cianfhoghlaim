# Change: 2026-07-03-gemini-6-corpus-pipeline

## Why

The `leabharlann/gemini_deep_research/` directory contains 224 agent-
generated PDFs across 6 sub-corpora (law / medical / politics /
culture / technology / other) totaling ~78 MB. These are currently
unprocessed — no BAML extraction, no DuckLake ingestion, no Cognee
cognify, no Graphiti temporal episodes.

Per user direction:
- Process **all 6 corpora** (NOT just law)
- Use the v4 OCR/VLM registry's `qwen3-vl-8b` workhorse
- Timeline uses **PDF content only** for `event_time` (NOT file mtime)
- Bypass the existing `gemini_deep_research.py` (which only handles law
  + 1 BAML function). New source handles 6 corpora + 6 BAML functions.

## What changes

This change creates a 7-stage pipeline for **all 6 Gemini corpora**:

### Stage 1 — VLM/OCR

`qwen3-vl-8b` is the workhorse for all 6 corpora. The
`gemini_corpus_source.py` DLT source tags each PDF with `model_key =
qwen3-vl-8b`.

### Stage 2 — BAML extraction

2 new BAML files in `cianfhoghlaim/baml/processing/`:

1. `legal_case_profile.baml` — `class LegalCaseProfile` (for law corpus),
   `class MedicalCaseProfile` (for medical), `class TimelineEvent`,
   `class StatuteReference`, `enum CaseCategory`, `enum Jurisdiction`
2. `topic_profile.baml` — `class PoliticalTopicProfile`,
   `class CultureTopicProfile`, `class TechTopicProfile`,
   `enum PoliticalTopic`, `enum CultureTopic`, `enum TechTopic`

### Stage 3 — DuckLake (5 tables per corpus = 30 tables)

6 schemas: `gemini_<corpus>_research`. Each schema has 5 tables:
`<corpus>_cases`, `<corpus>_timeline_events`, `<corpus>_issues`,
`<corpus>_entities`, `<corpus>_recommended_actions`.

### Stage 4 — LanceDB embeddings (BGE-large, 6 tables, 224 vectors)

6 LanceDB tables: `gemini_<corpus>_lance` (1 per corpus).

### Stage 5 — Graphiti temporal episodes (PDF content ONLY)

6 per-corpus Graphiti streams, 224 episodes total. **`event_time`
extracted from PDF prose via BAML** (NOT file mtime) per the user
decision "PDF content only".

### Stage 6 — Cognee cognify (6 datasets)

6 datasets: `gemini_<corpus>_research` (one per corpus).

### Stage 7 — FalkorDB cross-corpus graph

Nodes: Corpus, CaseProfile, Party, Jurisdiction, Statute, TimelineEvent.
Edges: MENTIONS, IN_JURISDICTION, CITES_STATUTE, OCCURRED_AT.

## Files

- 2 BAML files: `cianfhoghlaim/baml/processing/{gemini_corpus/legal_case_profile.baml, gemini_corpus/topic_profile.baml}`
- 1 DLT source: `cianfhoghlaim/dlt/filesystem/gemini_corpus_source.py`
- 1 Dagster assets module: `cianfhoghlaim/dagster/defs/3_model_lifecycle/legal_research/gemini_corpus/gemini_corpus_assets.py`
- 2 defs.yaml files (L1 ingestion + L3 model lifecycle)
- 9 dev notebooks (6 per-corpus overviews + 3 cross-corpus)
- Openspec change files (proposal + tasks + 1 spec delta)

## Impact

- **Affected specs:** `oideachais-pipeline` (1 spec delta)
- **Affected code:** 13 new files (2 BAML + 1 DLT + 1 dagster + 2 defs + 9 notebooks)
- **Affected hosts:** `bunchloch` only
- **Risk:** low — BAML calls return stubs when baml_client is unavailable; cognee/graphiti imports have try/except fallbacks
- **Audit gates:** `openspec validate --strict`

## Non-goals

- **Not replacing** the existing `gemini_deep_research.py` (which only
  handles law); that file is for the prior change. New code is additive.
- **Not bi-temporal** — `event_time` comes from PDF prose only (no mtime).
- **Not including 7th corpus** (e.g. `damages_estimates_tax_plannings.pdf`
  at the root of `gemini_deep_research/`); that's a one-off document,
  defer to follow-up.

## Cross-references

- Per openspec/changes/2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams/
  (Change B) — same 7-stage pipeline pattern, different domain.
- Per the lhc — `select_ocr_backend()` heuristic tree in
  `cianfhoghlaim/meaisinfhoghlaim/models/registry.py:805-865`.
