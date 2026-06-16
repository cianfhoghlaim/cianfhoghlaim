# Meaisínfhoghlaim Platform Capability

## Purpose

`meaisinfhoghlaim-platform` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at `meaisinfhoghlaim/`
(the AI/ML quadrant, 15K+ LOC, 10 sub-packages, registered as a
top-level uv workspace member with the ASCII wheel name
`meaisinfhoghlaim`). See `docs/00_index.md` for the quadrant map and
`docs/00-core/CLAUDE.md` for the project identity.

This is the first openspec spec for the meaisinfhoghlaim quadrant.

## Background

The meaisinfhoghlaim quadrant houses the AI/ML services that feed the
curriculum knowledge graph consumed by `oideachais/` and the
dashboards in `croilar/apps/portal/`. The 10 sub-packages are:

- `agents/` — 12 specialised agents (Root, Curriculum, Translation,
  Corpus, Geospatial, Statistics, Research, Curriculum Comparison,
  Bunchloch Research, AG-UI Curriculum, Site Analysis, etc.)
- `ocr/` — 10 OCR models across 6 backends (Pylaia, VLM, TrOCR,
  PaddleOCR, Tesseract, dots.ocr)
- `language/` — 6 Celtic-language subdirs (`brezhoneg/`, `cymraeg/`,
  `gaeilge/`, `gaelg/`, `gaidhlig/`, `kernowek/`) + a `cognates.yaml`
  cross-Celtic cognate database
- `pipelines/` — 7 ML pipelines (Canuint audio slicer, dialect
  classifier, Irish document scanner, LLM router, transcript aligner,
  VLM bridge)
- `alignment/` — 7 alignment modules (aligner, canuint exporter,
  character interpolator, colpali aligner, dataset generator, export,
  Irish G2P, quality)
- `evaluation/` — RAGAS evaluation pipeline + run_evaluation driver
- `quality/` — 3 content quality modules (canuint validator,
  completeness, content quality)
- `catalog/` — `models.yaml` (ML model registry) + `sources.yaml` (Celtic
  data sources registry)
- `services/` — 3 FastAPI services (agent_fastapi, celery_worker,
  pipeline_fastapi)
- `scripts/` — utility scripts (e.g. dataset generation)

The meaisinfhoghlaim quadrant is registered in the root `dg.toml` as
a Dagster code-location with 4 heartbeat assets in the
`meaisin_heartbeat` group (added in commit `6afe63dac`, Phase 0.2 of
`lateralise-british-isles-domains`).

## Requirements

### Requirement: 10 sub-packages

The system SHALL declare 10 sub-packages in
`meaisinfhoghlaim/pyproject.toml [tool.hatch.build.targets.wheel].packages`:
`agents`, `ocr`, `language`, `pipelines`, `alignment`, `evaluation`,
`quality`, `catalog`, `scripts`, `services`.

#### Scenario: Sub-packages import

- **GIVEN** the venv is installed via `uv sync`
- **WHEN** a user runs `uv run python -c "from meaisinfhoghlaim.agents import curriculum_agent"`
- **THEN** the import succeeds

### Requirement: 4 heartbeat assets

The system SHALL register 4 heartbeat assets in the
`meaisin_heartbeat` Dagster group that import-test each meaisín
sub-package.

#### Scenario: Heartbeat assets pass

- **GIVEN** the meaisinfhoghlaim code-location is loaded
- **WHEN** the 4 heartbeat assets materialise
- **THEN** all 4 succeed (smoke test that `agents/curriculum_agent`,
  `pipelines/dialect_classifier`, `pipelines/transcript_aligner`,
  `pipelines/irish_document_scanner` import cleanly)

### Requirement: Dagster code-location registration

The system SHALL register meaisinfhoghlaim as a Dagster code-location in
the root `dg.toml`.

#### Scenario: Code-location loads

- **GIVEN** the root `dg.toml` is configured with the meaisinfhoghlaim
  code-location
- **WHEN** `dg dev` starts the Dagster UI
- **THEN** the meaisinfhoghlaim code-location appears in the UI
  with the 4 heartbeat assets

### Requirement: Cross-quadrant ingestion from oideachais DuckLake

The system SHALL ingest from the oideachais DuckLake catalog via the
`oideachais.dagster_defs` package.

#### Scenario: Lakehouse to meaisinfhoghlaim ingest

- **GIVEN** the oideachais leabharlann sources have materialised in
  DuckLake
- **WHEN** a meaisinfhoghlaim agent (e.g. `corpus_agent`) is invoked
- **THEN** the agent reads the leabharlann rows from DuckLake
- **AND** the agent returns the top-N similar chunks via the
  BGE-large-en-v1.5 embedding model

### Requirement: Celtic-language model catalog

The system SHALL maintain a Celtic-language model catalog at
`meaisinfhoghlaim/catalog/models.yaml` (UCCIX-Llama2-13B-Instruct,
Llama-3.2-3B-Irish, gaBERT, gaHealth, etc.).

#### Scenario: Model catalog is valid YAML

- **GIVEN** the `meaisinfhoghlaim/catalog/models.yaml` file
- **WHEN** the file is loaded via `yaml.safe_load()`
- **THEN** the file parses without errors
- **AND** each model entry has `id`, `name`, `type`, `base`,
  `languages`, `status`, and `huggingface` fields

## Known issues (from `meaisinfhoghlaim/README.md`)

| # | Issue | Tracked in | Severity |
|--:|:--|:--|:--|
| 1 | Most sub-packages are stubs; the 4 heartbeats are the first real assets | the 10 sub-packages | high |
| 2 | No `[tool.uv.sources]` block; sibling workspace members are not declared as local-path dependencies | `meaisinfhoghlaim/pyproject.toml` | high — blocks cross-quadrant imports |
| 3 | The 6 Celtic-language subdirs are stubs | the 6 subdirs | medium |
| 4 | No production dagster code-location (only the 4 heartbeats) | `meaisinfhoghlaim/dagster_defs/assets/healthchecks.py` | medium |
| 5 | The `baml_src → scéimre` rename was deferred per `lateralise-british-isles-domains` | the AGENTS.md | low — deferred |

## Cross-references

- [`meaisinfhoghlaim/`](../../meaisinfhoghlaim/) (the AI/ML quadrant)
- [`meaisinfhoghlaim/README.md`](../../meaisinfhoghlaim/README.md) (the status table + known issues)
- [`meaisinfhoghlaim/AGENTS.md`](../../meaisinfhoghlaim/AGENTS.md) (the developer-quick-reference)
- [`meaisinfhoghlaim/pyproject.toml`](../../meaisinfhoghlaim/pyproject.toml) (the uv workspace member)
- [`dg.toml`](../../dg.toml) (the root Dagster code-location config)
- [`openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md`](meaisinfhoghlaim-agent-frameworks/spec.md) (the 12 agents)
- [`openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md`](meaisinfhoghlaim-ocr-htr/spec.md) (the 10 OCR models)
