# `data-engineering-pipeline-documentation` capability spec

## Purpose

`data-engineering-pipeline-documentation` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives at `cianfhoghlaim/STATUS.md`, `cianfhoghlaim/REFACTORING.md`, the per-area READMEs in `cianfhoghlaim/{dlt_sources,cocoindex_flows,dagster_defs}/`, `baml_src/README.md`, the agent READMEs in `cianfhoghlaim/agents/{adk,agno}/README.md`, and the end-to-end stack overview at `docs/06-infrastructure/leabharlann-stack-overview.md`. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.

Single source of truth for the British Isles education data-engineering pipeline state, plus per-area READMEs that demystify the Lakehouse + Infisical + Locket + Komodo + Dagster + BAML + CocoIndex + Cognee + FalkorDB + Graphiti + LanceDB stack.
## Requirements
### Requirement: STATUS.md is the single source of truth
The system SHALL maintain `cianfhoghlaim/STATUS.md` as a single source of truth for the British Isles data-engineering pipeline state.

#### Scenario: BAML × dlt × Dagster × CocoIndex matrix
- **GIVEN** a user reads `cianfhoghlaim/STATUS.md`
- **WHEN** they look up the row for `baml_src/primary.baml`
- **THEN** the row SHALL list the matching dlt source file (e.g. `cianfhoghlaim/dlt_sources/ireland/primary.py`), the matching Dagster asset, the matching CocoIndex flow (v0 or v1), and the matching Cognee cognify pass

#### Scenario: Per-nation × per-cycle coverage
- **GIVEN** a user reads `cianfhoghlaim/STATUS.md`
- **WHEN** they look up the row for `England × Key Stage 4`
- **THEN** the row SHALL list the dlt source file, the BAML extractor (if any), the Dagster asset, and the embedding/cognify status

#### Scenario: CocoIndex v0 vs v1 status
- **GIVEN** a user reads `cianfhoghlaim/STATUS.md`
- **WHEN** they look up a CocoIndex flow
- **THEN** the row SHALL mark it as `working` (v1 on cocoindex==1.0.9), `broken_on_v1` (v0 not migrated), or `unwired` (no Dagster asset invokes it)

### Requirement: REFACTORING.md backlog
The system SHALL maintain `cianfhoghlaim/REFACTORING.md` as a refactor backlog with explicit `Status` per item.

#### Scenario: Item status tracking
- **GIVEN** a user reads `cianfhoghlaim/REFACTORING.md`
- **WHEN** they look up an item
- **THEN** the item SHALL have a `Status` field of `done`, `in_progress`, or `backlog`
- **AND** the item SHALL link to a tracking openspec change (where applicable)

#### Scenario: BAML-without-dlt gap
- **GIVEN** a user reads `cianfhoghlaim/REFACTORING.md`
- **WHEN** they look up the BAML-without-dlt gap
- **THEN** the row SHALL list the 4+ BAML functions defined in `baml_src/` but not invoked from any dlt `extraction_metadata` resource
- **AND** the row SHALL link to the queued openspec change for Feature 1

### Requirement: Per-area READMEs
The system SHALL maintain READMEs in each pipeline area, mapping source code to capabilities.

#### Scenario: dlt source README
- **GIVEN** a user reads `cianfhoghlaim/dlt_sources/uk/README.md`
- **WHEN** they look up `Northern Ireland × Key Stage 3`
- **THEN** the row SHALL list the dlt source filename, the BAML extractor (if any), the Dagster asset, the Cognee cognify pass (if any), and the source URL

#### Scenario: CocoIndex flow README
- **GIVEN** a user reads `cianfhoghlaim/cocoindex_flows/README.md`
- **WHEN** they look up the `leabharlann_embedding` flow
- **THEN** the row SHALL say it is v1, English-only, uses BGE-large-en-v1.5 (1024-d), and exposes the 3 v1 Apps + 3 `search_leabharlann_*` query handlers

#### Scenario: Dagster asset catalogue
- **GIVEN** a user reads `cianfhoghlaim/dagster_defs/assets/README.md`
- **WHEN** they look up the `leabharlann_assets` module
- **THEN** the row SHALL list the 7 assets, their group name (`leabharlann_ingestion`), their compute kinds (`dlt` × 3, `baml` × 1, `embedding` × 3), and their partition definitions

#### Scenario: BAML schema catalogue
- **GIVEN** a user reads `baml_src/README.md`
- **WHEN** they look up `baml_src/author_archive.baml`
- **THEN** the row SHALL list the 12 classes, the 4 extraction functions, the consumer pipelines, and the test coverage

### Requirement: Agent surface READMEs
The system SHALL maintain READMEs for the two agent surfaces.

#### Scenario: ADK agent surface
- **GIVEN** a user reads `cianfhoghlaim/agents/adk/README.md`
- **WHEN** they look up a specific agent
- **THEN** the row SHALL describe the agent's role + tools + integrations

#### Scenario: Agno agent surface
- **GIVEN** a user reads `cianfhoghlaim/agents/agno/README.md`
- **WHEN** they look up a specific sub-team
- **THEN** the row SHALL describe the team's role + sub-agents + integrations

### Requirement: End-to-end stack overview
The system SHALL maintain `docs/06-infrastructure/leabharlann-stack-overview.md` as the canonical end-to-end diagram and description.

#### Scenario: How a leabharlann PDF flows
- **GIVEN** a user reads `docs/06-infrastructure/leabharlann-stack-overview.md`
- **WHEN** they read the "How a leabharlann PDF flows through the stack" section
- **THEN** the section SHALL describe the 5 stages: (1) Komodo + Infisical + Locket secret injection, (2) dlt filesystem scan with SHA-256 dedup, (3) BAML structured extraction, (4) CocoIndex v1 incremental embedding to LanceDB, (5) Cognee cognify + FalkorDB + Graphiti cross-archive knowledge graph

#### Scenario: Stack layer diagram
- **GIVEN** a user reads `docs/06-infrastructure/leabharlann-stack-overview.md`
- **WHEN** they look at the stack diagram
- **THEN** the diagram SHALL label the 4 layers (source trees, control plane, storage, machine learning) and the 5 integration points (dlt, BAML, CocoIndex, Cognee, LanceDB)

### Requirement: Canonical spec SHALL list 9 files
The system SHALL maintain the 9 documentation files listed in the canonical `data-engineering-pipeline-documentation` spec: `cianfhoghlaim/STATUS.md`, `cianfhoghlaim/REFACTORING.md`, `cianfhoghlaim/dlt_sources/uk/README.md`, `cianfhoghlaim/dlt_sources/ireland/README.md`, `cianfhoghlaim/cocoindex_flows/README.md`, `cianfhoghlaim/dagster_defs/assets/README.md`, `baml_src/README.md`, `cianfhoghlaim/agents/{adk,agno}/README.md`, and `docs/06-infrastructure/leabharlann-stack-overview.md`.

#### Scenario: All 9 files exist
- **GIVEN** a user checks the documentation surface
- **WHEN** they list the 9 files
- **THEN** each file SHALL exist and be non-empty

### Requirement: Data engineering pipeline documentation router skill

The data engineering pipeline documentation capability MUST be discoverable via a single router skill at `.agents/skills/data-engineering-pipeline-documentation/SKILL.md`. The router SHALL list the 4 canonical docs (STATUS.md, REFACTORING.md, the quadrant README, the per-area READMEs), the 4 status columns in STATUS.md, the 5-stage Celtic asset generation pipeline, and the 4 kinds of "what changed" notes.

#### Scenario: Agent finds the documentation router

- **WHEN** an agent searches for "STATUS.md", "REFACTORING.md", "BAML × dlt × Dagster matrix", or "pipeline status"
- **THEN** the loader matches `.agents/skills/data-engineering-pipeline-documentation/SKILL.md`
- **AND** the skill points at the canonical docs without duplicating their content

### Requirement: NEW — Single-repo + bonneagar/ subdir reality

The data-engineering pipeline documentation SHALL reflect the v7
single-repo + bonneagar-subdir reality:
- The repo root IS the Python package (post-v7 flatten)
- The IaC is at `bonneagar/` (NOT a separate repo)
- `leabharlann` is the only remaining separately-managed repo
  (NOT part of this repo)

#### Scenario: Docs reflect v7 reality

- **WHEN** a developer reads `README.md` or `AGENTS.md`
- **THEN** the "Repository constellation" section SHALL list
  exactly 2 repos: cianfhoghlaim + leabharlann
- **AND** it SHALL mention that the IaC lives at `bonneagar/` in
  this repo
- **AND** it SHALL NOT claim bonneagar is a separate GitHub repo

### Requirement: STATUS.md + REFACTORING.md entries for the 3 mega-change artifacts

The system SHALL add 3 entries to `STATUS.md` + 3 entries to
`REFACTORING.md` documenting the new artifacts:

1. `centralized-model-registry` — `STATUS.md` entry:
   "70 models registered in `MODEL_REGISTRY` (was 22 OCR/VLM only);
   32 hardcoded `gemini-2.0-flash` sites replaced with
   `MODEL_REGISTRY.resolve(...)`; LiteLLM config regenerated from
   the registry; 96 Pydantic duplicates removed."

2. `centralized-schema-registry` — `STATUS.md` entry:
   "BAML TypeScript codegen activated (`baml_client_ts/`); 96
   hand-written Pydantic duplicates replaced with BAML-generated
   types; bi-ep.gen.ts rewritten from BAML TS (was 671 LOC of
   DuckDB-introspection-derived Zod); `notebooks/_shared/schema.py`
   exposes `schema_introspect()` for every BIEP table."

3. `deployment-control-panel` — `STATUS.md` entry:
   "Marimo notebook `notebooks/00_control_panel.py` + web UI
   `web/apps/cianfhoghlaim-web/control-panel/` + CLI
   `scripts/cianfhoghlaim-cli.ts` + `deployment-choice.yaml` (the
   single enablement file). 5 tabs × 5 routes × 8 subcommands."

#### Scenario: STATUS.md has 3 new entries

- **GIVEN** the 3 mega-change artifacts shipped
- **WHEN** the operator reads `STATUS.md`
- **THEN** the file contains 3 new entries documenting the artifacts

## Merged from

- `data-engineering-space` (the HuggingFace Space `spaces/data-engineering/` requirements were merged into this spec on 2026-07-06)
