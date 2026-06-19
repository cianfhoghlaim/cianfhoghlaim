# Author-Archive Cross-Corpus Knowledge Graph

## Why

Stages 0.5-2 of `author-archive-v1` shipped 4 independent corpora into
DuckLake / LanceDB:

  - `oideachais.official_media` (160 sources, Stage 1)
  - `oideachais.oideachais_mata.mata_extraction` (568 files, Stage 2)
  - `oideachais.oideachais_software.software_extraction` (212 files)
  - `oideachais.oideachais_irish.irish_extraction` (134 files)
  - `oideachais.oideachais_education.education_extraction` (1008 files)
  - `oideachais.oideachais_personal_records.personal_records_extraction`
    (39 files; 29 by default with `identity/` excluded)
  - plus the existing leabharlann corpora (`gemini_deep_research`,
    `zotero`, `google_takeout`)

The user said: "we want to know what data we have and how it was
sourced". 7 separate corpora is not "we want to know what we have" —
it's "we want to know 7 unrelated things". The user wants a unified
view.

Stage 3 builds the cross-corpus knowledge graph: 8 edge types, 5
deterministic rules, 1 unified Cognee dataset.

## What Changes

### Code

- `oideachais/cognee_integration/author_archive_cognify.py` (NEW): the
  Cognee cognify helper for the 6 author-archive corpora. Defines
  `cognify_author_archive_rows()` + `cognify_all_corpora()`.

- `oideachais/cognify_rules/author_archive_cross_corpus.py` (NEW): the
  5-rule cross-corpus edge population. Uses FalkorDB MERGE for
  idempotency.

- `oideachais/dagster_defs/assets/official_media/author_archive_kg_assets.py`
  (NEW): 3 new Dagster assets
  (`author_archive_cognify`, `author_archive_cross_edges`,
  `author_archive_kg_summary`) in the `author_archive_kg` group.

- `oideachais/notebooks/dashboards/author_archive/unified_dashboard.py`
  (NEW): the unified marimo dashboard with 4 tabs (Source provenance,
  UoG coursework, Cross-corpus KG, Credit usage).

### Spec deltas

- `author-archive-cross-corpus-kg/spec.md` — the 8 edge types + 5 rules

## Impact

- The user gets a single `oideachais_author_archive` knowledge graph
  spanning all 6 corpora.
- 8 edge types link the corpora; 5 deterministic rules populate them.
- The marimo dashboard renders the 4 most important views in one
  page.
- 95% saving on Firecrawl credits (preserved from Stage 0.5).

## Out of scope (deferred to Stage 4)

- Multi-target deployment (dev=DuckDB, staging=MotherDuck,
  prod=Garage S3 + Lakekeeper)
- `make_target.sh` runtime helper
- `oideachais/dlt_utils/target_factory.py` factory
