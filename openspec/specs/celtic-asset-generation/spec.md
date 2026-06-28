# celtic-asset-generation Specification

## Purpose
TBD - created by archiving change sync-skills-from-docs-round-8. Update Purpose after archive.
## Requirements
### Requirement: Five-stage Celtic asset generation pipeline

The `celtic-asset-generation` skill SHALL orchestrate a
5-stage pipeline for every Celtic language asset. Each
asset (a NCCA specification, an SEC exam paper, a Dúchas
handwriting sample, a Tuatha quest NPC, etc.) flows
through the 5 stages:

1. **BAML extraction** — schema-validated LLM extraction
   of typed records (`MarkingPoint`, `LearningOutcome`,
   `CircularMetadata`, `SiteAnalysis`, etc.)
2. **CocoIndex v1 embedding** — incremental embedding with
   `@coco.fn(memo=True)` + BGE-large-en-v1.5 in 100+
   batches
3. **Cognee cognify** — knowledge graph construction with
   8 canonical relationship types
4. **Graphiti temporal memory** — bi-temporal KG
   (Graphiti + FalkorDB)
5. **LanceDB vector** — IVF_HNSW + FTS indexes for
   semantic search

The pipeline runs in
`sruth/oideachais/dagster_defs/assets/celtic_assets.py` and
is exposed via the FastAPI `sruth/oideachais/api/` endpoints.
The skill body at
`.agents/skills/celtic-asset-generation/SKILL.md`
documents the canonical 5-stage flow; the deep-dive
references live at
`.agents/skills/celtic-asset-generation/references/`.

#### Scenario: A new NCCA specification lands

- **GIVEN** a new NCCA primary mathematics specification
  PDF is uploaded to `stedding/ingest_queue/`
- **WHEN** the `celtic_assets_primary_maths` Dagster asset
  materialises
- **THEN** the DLT source ingests the PDF and the BAML
  extraction calls `ExtractLearningOutcome` (BGE + GLM-4.6
  fallback) to extract typed outcomes
- **AND** the CocoIndex v1 flow embeds each outcome in
  the `oideachais.education.ie.primary.maths.outcomes`
  LanceDB table
- **AND** the Cognee cognify call builds the knowledge
  graph nodes
- **AND** the Graphiti episode is appended to the temporal
  KG
- **AND** the marimo dashboard at
  `https://oideachais.cianfhoghlaim.ie/dashboards/
  primary-maths` shows the new outcomes

#### Scenario: A bilingual asset needs Irish + English forms

- **GIVEN** an asset has both English and Irish content
  (e.g. a NCCA specification)
- **WHEN** the BAML extraction runs
- **THEN** the `BilingualText` class is populated with
  both `name_en` and `name_ga`
- **AND** the unified concept node is created in the KG
- **AND** the language-specific forms are attached via
  `HAS_FORM` edges (with dialect handling: Connacht /
  Munster / Ulster)

### Requirement: VLM backbone (Bolmo / Molmo2 / Qwen3-VL)

The `celtic-asset-generation` skill SHALL use the
**Bolmo** + **Molmo2** vision-language models (AllenAI,
2025) as the canonical VLM backbone for document
extraction. For on-device Apple Silicon inference, the
**Qwen3-VL** family (fine-tuned via Unsloth) is the
fallback (see `.agents/skills/irish-llm-on-device/`).

The 2 canonical VLM papers
(`references/papers/bolmo.pdf` and
`references/papers/molmo2-tech-report.pdf`) are kept as
long-form references in the skill.

#### Scenario: A new document is ingested

- **GIVEN** a new PDF (NCCA, SEC, Dúchas, etc.) needs
  extraction
- **WHEN** the BAML extraction calls
  `ExtractCurriculumSpecification(pdf_text, pdf_images)`
- **THEN** the VLM backbone processes the document:
  - High-throughput / batched → Molmo2 (deployed on the
    `bunchloch` M4 Max or a Modal GPU)
  - On-device Apple Silicon → Qwen3-VL (MLX-quantised)
- **AND** the typed extraction is returned to the BAML
  client

### Requirement: 4 Successive Independent Asset Gen Pipelines (v4)

The system SHALL organise educational asset generation under 4 successive INDEPENDENT pipelines at `cianfhoghlaim/assets/asset_generation/`:

1. `official_documents/` — extracts assets from syllabus + exam papers + marking schemes (BAML + CocoIndex OCR-aware)
2. `subject_assets/` — generates subject-specific 3D assets (chemistry lab equipment + geography landscape + biology specimens + physics apparatus) via Qwen-Image-2512 / Z-Image-Turbo / FLUX.2-klein-9B
3. `language_assets/` — generates language-specific assets (gaeilge + cymraeg + gaidhlig + gaelg + kernewek + brezhoneg) via teanglann + gaois
4. `exporters/` — exports to Babylon.js + Godot + Unity + Unreal via crypteolas pipelines

Each pipeline is independently runnable from Dagster — they are NOT chained as a single pipeline.

#### Scenario: Independent activation

- **WHEN** Dagster materialises `assets/asset_generation/official_documents/syllabus.py`
- **THEN** the syllabus extraction runs alone, writing to `ducklake://oideachais.assets.official_documents.syllabus`
- **AND** subject_assets / language_assets / exporters do NOT trigger
- **AND** the four pipelines share no DAG dependencies

### Requirement: Asset Generation Source Schema Provisional (v4)

The asset generation source schema (`cianfhoghlaim/assets/asset_generation/{official_documents,subject_assets,language_assets,exporters}/`) SHALL be considered provisional — refactored after Plan 1 (Ireland + leabharlann) informs the best CocoIndex + DLT + DuckDB + DuckLake + Lance patterns for multi-nation + multi-language + multimodal processing. The system SHALL include a `README.md` at `cianfhoghlaim/assets/asset_generation/` that states this provisional status and lists the open refactor questions.

#### Scenario: Refactor notice

- **WHEN** a developer reads `cianfhoghlaim/assets/asset_generation/README.md`
- **THEN** the README states the schema is provisional and lists the open refactor questions
- **AND** the README cross-references `openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/proposal.md`

