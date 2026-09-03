# celtic-asset-generation Specification

## Purpose

`celtic-asset-generation` is a capability of the Cianfhoghlaim platform.
It runs **4 successive INDEPENDENT asset-generation pipelines** that turn
the official Irish curriculum documents into the visual + 3D assets the
agent fleet needs to render the educational MMO. The 4 pipelines are:

1. **Official documents** — `official_documents/{syllabus,exam_papers,marking_schemes}/`
   turn PDFs into structured records (extracted text + figures + tables).
2. **Subject assets** — `subject_assets/{chemistry_lab,geography_landscape,biology_specimens,physics_apparatus}/`
   generate per-subject visual assets (lab equipment photos, terrain tiles, specimen models, apparatus illustrations).
3. **Language assets** — `language_assets/{gaeilge,cymraeg,gaidhlig,gaelg,kernewek,brezhoneg}_assets.py`
   generate per-language visual + audio assets for the 6 Celtic languages.
4. **Exporters** — `exporters/{babylon,godot,unity,unreal}.py` export the
   generated assets into the 4 target game-engine formats.

The corresponding source code lives at `cianfhoghlaim/assets/asset_generation/`.
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
`cianfhoghlaim/dagster_defs/assets/celtic_assets.py` and
is exposed via the FastAPI `cianfhoghlaim/api/` endpoints.
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
  the `cianfhoghlaim.education.ie.primary.maths.outcomes`
  LanceDB table
- **AND** the Cognee cognify call builds the knowledge
  graph nodes
- **AND** the Graphiti episode is appended to the temporal
  KG
- **AND** the marimo dashboard at
  `https://cianfhoghlaim.cianfhoghlaim.ie/dashboards/
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
- **THEN** the syllabus extraction runs alone, writing to `ducklake://cianfhoghlaim.assets.official_documents.syllabus`
- **AND** subject_assets / language_assets / exporters do NOT trigger
- **AND** the four pipelines share no DAG dependencies

### Requirement: Asset Generation Source Schema Provisional (v4)

The asset generation source schema (`cianfhoghlaim/assets/asset_generation/{official_documents,subject_assets,language_assets,exporters}/`) SHALL be considered provisional — refactored after Plan 1 (Ireland + leabharlann) informs the best CocoIndex + DLT + DuckDB + DuckLake + Lance patterns for multi-nation + multi-language + multimodal processing. The system SHALL include a `README.md` at `cianfhoghlaim/assets/asset_generation/` that states this provisional status and lists the open refactor questions.

#### Scenario: Refactor notice

- **WHEN** a developer reads `cianfhoghlaim/assets/asset_generation/README.md`
- **THEN** the README states the schema is provisional and lists the open refactor questions
- **AND** the README cross-references `openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/proposal.md`

### Requirement: Purpose-section accuracy note (visibility)

The `celtic-asset-generation` spec's Purpose section SHALL carry an
explicit note that the "4 successive INDEPENDENT asset-generation
pipelines" description (`official_documents/`, `subject_assets/`,
`language_assets/`, `exporters/{babylon,godot,unity,unreal}`) at
`cianfhoghlaim/assets/asset_generation/` does not correspond to code
that exists in the live tree, and that the real, working asset
generation code lives at `tuatha/asset_generation/fibo/` instead. This
SHALL be a visible note, not a silent removal — a full rewrite or
deletion of the aspirational content is out of scope for this change
(see the "FIBO 2D educational diagram generation" requirement below
for what actually runs today).

#### Scenario: A developer reads the spec's Purpose section

- **GIVEN** a developer opens `openspec/specs/celtic-asset-generation/
  spec.md` looking for the real asset-generation code path
- **WHEN** they read the Purpose section
- **THEN** they find an explicit note directing them to
  `tuatha/asset_generation/fibo/` for the real, working pipeline
- **AND** the note does not claim the 4-pipeline / 6-Celtic-language /
  4-game-engine-exporter structure is implemented

### Requirement: FIBO 2D educational diagram generation (as-built)

The system SHALL generate 2D educational diagram assets via the FIBO
pipeline at `tuatha/asset_generation/fibo/` (Dagster assets in
`orchestration/defs/4_asset_generation/`), consisting of: (1)
`fibo_json_configs`, which turns curriculum concepts into FIBO JSON
generation configs; (2) `fibo_configs_from_syllabus_diagrams`, which
turns real diagrams detected by `ExtractSyllabusDiagram` in a subject's
official NCCA syllabus PDF into FIBO JSON configs — the docs-informed
alternative to `fibo_json_configs`' sample-concept fallback; and (3)
`generated_images`, which renders each config via `FiboResource`,
validates it with `ValidationResource` (a VLM-based scorer), and
refines up to `max_refinement_iterations` times before accepting the
result. Diagram content used as generation input SHALL trace back to a
real source PDF page — never a fabricated concept — whenever
`fibo_configs_from_syllabus_diagrams` is the config source.

#### Scenario: Real diagram detected and turned into a FIBO config

- **GIVEN** a subject's English-medium syllabus PDF contains a figure
  the text references (e.g. "Figure 3: Overview of Leaving Certificate
  Chemistry")
- **WHEN** `fibo_configs_from_syllabus_diagrams` runs for that subject
- **THEN** `ExtractSyllabusDiagram` returns ≥1 `SyllabusDiagram` record
  with a `page_number` and `source_pdf`
- **AND** the resulting FIBO config's `_metadata` carries that
  `diagram_id`, `source_pdf`, and `page_number` — traceable back to
  the real PDF page, not fabricated

#### Scenario: Subject with no English-medium syllabus is skipped, not fabricated

- **GIVEN** a subject (e.g. gaeilge) has no English-medium syllabus PDF
  in the corpus
- **WHEN** `fibo_configs_from_syllabus_diagrams` runs for that subject
- **THEN** the asset materialises with `configs_generated = 0`
- **AND** no FIBO config is fabricated from a sample/placeholder concept

