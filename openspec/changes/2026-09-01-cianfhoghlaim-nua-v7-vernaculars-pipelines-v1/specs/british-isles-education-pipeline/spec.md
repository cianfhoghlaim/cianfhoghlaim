## ADDED Requirements

### Requirement: The 7 vernacular BAML extraction functions MUST each be wired to a complete end-to-end pipeline

The Cianfhoghlaim british-isles-education-pipeline capability MUST
wire each of the 7 `Extract<Vernacular>SubjectSpec` BAML functions
(declared in the
`2026-09-01-cianfhoghlaim-nua-v7-vernaculars-v1` change) to a
complete end-to-end pipeline spanning all 5 platform layers:

  1. DLT source         (raw ingestion)
  2. CocoIndex v1 App   (embedding)
  3. Convex table       (reactive materialisation)
  4. Hono route         (CopilotKit action surface)
  5. Dagster asset      (orchestrator)

Each of the 7 vernaculars MUST have all 5 layers:

| Vernacular         | BAML function                       | DLT source file                                                          | CocoIndex App                      | Hono route                |
| ------------------ | ----------------------------------- | ------------------------------------------------------------------------ | ---------------------------------- | ------------------------- |
| Welsh (CY)         | `ExtractWelshSubjectSpec`           | `dlt_sources/education/wales/british_isles/welsh_vernacular.py`          | `vernacular_welsh_embedding`       | `/api/copilotkit/vernacular/welsh` |
| Scottish Gaelic (GD) | `ExtractScottishGaelicSubjectSpec` | `dlt_sources/education/scotland/british_isles/scottish_gaelic_vernacular.py` | `vernacular_scottish_gaelic_embedding` | `/api/copilotkit/vernacular/scottish_gaelic` |
| Breton (BR)        | `ExtractBretonSubjectSpec`          | `dlt_sources/breton_cornish/british_isles/breton_vernacular.py`          | `vernacular_breton_embedding`      | `/api/copilotkit/vernacular/breton` |
| Cornish (KW)       | `ExtractCornishSubjectSpec`         | `dlt_sources/breton_cornish/british_isles/cornish_vernacular.py`         | `vernacular_cornish_embedding`     | `/api/copilotkit/vernacular/cornish` |
| Manx (GV)          | `ExtractManxSubjectSpec`            | `dlt_sources/education/isle_of_man/british_isles/manx_vernacular.py`     | `vernacular_manx_embedding`        | `/api/copilotkit/vernacular/manx` |
| Jersey French (FR_JE) | `ExtractJerseyFrenchSubjectSpec` | `dlt_sources/education/jersey/british_isles/jersey_french_vernacular.py` | `vernacular_jersey_french_embedding` | `/api/copilotkit/vernacular/jersey_french` |
| Guernsey French (FR_GG) | `ExtractGuernseyFrenchSubjectSpec` | `dlt_sources/education/guernsey/british_isles/guernsey_french_vernacular.py` | `vernacular_guernsey_french_embedding` | `/api/copilotkit/vernacular/guernsey_french` |

Plus the Ulster Scots (SCO, NI) companion:

| Vernacular       | BAML function                    | Convex companion                | Hono route                       |
| ---------------- | -------------------------------- | ------------------------------- | -------------------------------- |
| Ulster Scots (SCO) | `ExtractUlsterScotsSubjectSpec` | `web/packages/db/convex/vernacular/ulster_scots.ts` | `/api/copilotkit/vernacular/ulster_scots` |

The Convex `vernacular_documents` table (13th table of
`web/packages/db/convex/schema.ts`) MUST index each row by:
  - vernacular
  - jurisdiction
  - subject_slug
  - vernacular + jurisdiction (composite)
  - vernacular + subject_slug (composite)

#### Scenario: A school queries the Welsh syllabus via the Phase 14 Hono route

- **WHEN** a Welsh-medium school calls
  `POST /api/copilotkit/vernacular/welsh/extract_subject_spec` with
  `{ subject_slug: "mathematics", stage: "gcse", pdf_text: "...",
  source_url: "https://www.wjec.co.uk/qualifications/mathematics-gcse" }`
- **THEN** the Hono route delegates to
  `b.ExtractWelshSubjectSpec(...)` (via the Convex
  `vernacular_documents` table or the Dagster
  `welsh_vernacular_extractions` asset)
- **AND** a single `VernacularSubjectSpec` row lands in the Convex
  `vernacular_documents` table within seconds
- **AND** the `vernacular_welsh_embedding` CocoIndex App fires and
  ingests the row's text into the LanceDB table
  `cianhoghlaim.british_isles.wl.welsh.chunks`
- **AND** the `welsh_vernacular_documents_ingested`,
  `welsh_vernacular_extractions`, and `welsh_vernacular_embeddings`
  Dagster assets all materialise cleanly

#### Scenario: A Phase 14 test smoke-checks all 5 layers for all 7 vernaculars

- **WHEN** `uv run pytest tests/test_phase14_vernacular_pipelines.py` runs
- **THEN** the test suite verifies:
  1. All 8 BAML `Extract<Vernacular>SubjectSpec` functions are
     reachable from `baml_client.baml_client.sync_client.b`
  2. All 7 `@dlt.source(name="<lang>_vernacular")` DLT sources
     importable from `dlt_sources.<jurisdiction_path>`
  3. All 7 `vernacular_<lang>_embedding` CocoIndex v1 Apps are
     registered at import time in
     `cocoindex_flows.vernacular.vernacular_factory`
  4. The Convex `vernacular_documents` schema is well-formed and
     indexes by (vernacular, jurisdiction, subject)
  5. The Hono `_vernacular_factory.ts` exposes the 8 expected
     routes (7 + Ulster Scots)
  6. All 7 `orchestration.defs.2_materials.vernacular.<lang>_assets`
     modules import cleanly with 5 assets each registered

### Requirement: The CocoIndex `vernacular_<lang>_embedding` Apps MUST use the shared `LANCE_DB` + `EMBEDDER`

The 7 vernacular CocoIndex v1 Apps MUST reuse the shared
`LANCE_DB` + `EMBEDDER` ContextKeys from
`cocoindex_flows._shared._lifespan` (per the
`2026-08-15-centralized-schema-registry-and-deployment-control-panel-v1`
change). One embedder model (`BAAI/bge-m3`, 1024-d) shared across
all 7 Apps.

#### Scenario: A swap of the embedder model auto-re-embeds all 7 vernacular tables

- **WHEN** an operator changes `CIANFHOGHLAIM_EMBED_MODEL` from
  `BAAI/bge-m3` to `BAAI/bge-large-en-v1.5`
- **THEN** all 7 `vernacular_<lang>_embedding` Apps detect the
  embedder change (via `detect_change=True` on the `EMBEDDER`
  ContextKey) and re-embed their chunks within the live-update
  window
- **AND** the 7 LanceDB tables
  (`cianhoghlaim.british_isles.<jurisdiction>.<vernacular>.chunks`)
  are brought into the new model

### Requirement: The Phase 14 Convex `vernacular_documents` row MUST always carry the bilingual trio

Every row in `vernacular_documents` MUST carry three canonical
display-name fields per row:

  - `display_name`     — in the vernacular language
  - `display_name_en`  — English translation
  - `display_name_ga`  — Irish (Gaeilge) translation

This enforces the always-bilingual invariant across the 7
vernaculars (per the operator's direction at 2026-09-01). The
`VernacularSubjectSpec.display_name_en` + `.display_name_ga` BAML
fields are the canonical source.

#### Scenario: A Manx school queries the Manx syllabus

- **WHEN** a Manx (Gaelg)-medium school queries
  `vernacular_documents` rows for `vernacular='manx'`
- **THEN** they receive rows with the bilingual trio:
  `display_name` in Manx (Gaelg) + `display_name_en` in English +
  `display_name_ga` in Irish (Gaeilge)
- **AND** not just the bare vernacular name alone

### Requirement: The 7 Dagster assets MUST be importable without `from __future__ import annotations`

The 7 vernacular asset modules MUST NOT use
`from __future__ import annotations`. Dagster 1.13.x's
`_validate_context_type_hint` does not resolve forward-reference
strings and the asset decorator would otherwise reject the
`AssetExecutionContext` annotation at module-load time.

#### Scenario: A developer imports a Phase 14 vernacular asset module

- **WHEN** a developer imports
  `orchestration.defs.2_materials.vernacular.welsh_assets`
- **THEN** the module loads cleanly and registers
  `welsh_vernacular_documents_ingested`,
  `welsh_vernacular_extractions`, and
  `welsh_vernacular_embeddings` as Dagster assets
- **AND** the
  `_validate_context_type_hint` runtime check does not raise a
  `DagsterInvalidDefinitionError`
