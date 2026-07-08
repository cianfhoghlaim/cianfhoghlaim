# Oideachais PDF Processing Capability

## Purpose

`oideachais-pdf-processing` is the 7th canonical capability of the
Cianfhoghlaim platform. It is the **end-to-end PDF processing
pipeline** that takes NCCA syllabus PDFs, SEC past paper PDFs, and
SEC marking-scheme PDFs and produces structured, chunked,
semantically-indexed records in the DuckLake lakehouse. It is the
bridge between the raw PDF ingestion (DLT + BAML extraction) and the
downstream marimo dashboards, gradio review UIs, and HF Spaces.

The corresponding source code lives at:

- `cianfhoghlaim/ocr/models/registry.py` — the 22-entry
  `VISION_MODELS` dict (Unsloth-first, no OpenAI/Anthropic) + the 6
  `CLASSICAL_OCR` Docker stacks + the 3 `TEXT_MODELS` for agents.
  This is the v4 canonical home for the OCR/VLM registry (per the
  v4 platform spec line 685).
- `cianfhoghlaim/ocr/evaluation/compare.py` — the OCR evaluation
  harness that iterates all `all_models()` × `all_classical_stacks()`
  × corpora.
- `cianfhoghlaim/dlt/sources/oideachais/curriculumonline_pdfs.py` +
  the 3 NCCA + SEC + Marking-scheme DLT sources — the raw PDF
  ingest.
- `cianfhoghlaim/orchestration/defs/2_materials/lc_extraction/lc5_assets.py`
  — the LC5 (Leaving Cert 5-subject) Dagster asset that drives the
  pipeline.
- `cianfhoghlaim/cocoindex/pdf_chunks.py` — the CocoIndex v1 App
  that produces the BGE-M3-embedded chunks table.
- `spaces/oideachais-pdf-review/` — the Gradio HF Space for human
  review of topic-validation flags.

This spec is the **PDF-specific extension** of:

- `oideachais-pipeline` (the general DLT + Dagster pipeline)
- `oideachais-baml-schemas` (the BAML extraction clients)
- `meaisinfhoghlaim-ocr-htr` (the 22-entry VISION_MODELS registry)
- `oideachais-marimo-dashboards` (the marimo visualisation layer)
- `oideachais-cocoindex-v1-migration` (the CocoIndex v1 embedding
  flow)
- `oideachais-semantic-search` (the LanceDB HNSW search layer)
- `celtic-asset-generation` (the parent asset-generation orchestrator)

## Background

The Irish + UK + pan-Celtic syllabus + exam paper + marking-scheme
corpus is the **largest structured-text source** in the lakehouse. As
of 2026-06-29, the corpus contains:

- **NCCA syllabi** (5 stages × 33+ subjects × ~80 pages each) ≈
  13,200 pages
- **SEC past papers** (LC + JC × 33 subjects × 30 years × 2 papers ×
  24 pages) ≈ 47,520 pages
- **SEC marking schemes** (parallel to past papers, often
  image-rich) ≈ 47,520 pages
- **Total: ~108,000 pages** of structured educational text

Manual processing of this corpus is impossible; the VLM registry +
BAML extraction + CocoIndex embedding is the only way to make it
queryable. The 6-stage pipeline MUST ensure:

1. **Diagram detection** — figures in chemistry/biology/geography
   papers are identified and cropped (Molmo2-8B pointing +
   Granite-Docling DocTags).
2. **Correct topic categorisation** — every question is matched to
   its NCCA syllabus topic (BAML `ExtractPastPaper` validates against
   `ExtractLeavingCertSyllabus`).
3. **Appropriate chunking** — chunks respect semantic boundaries
   (question blocks, marking points, learning outcomes, page breaks).
4. **Fada / tironian preservation** — Irish text retains diacritics
   through the entire pipeline (BAML `IrishContentQuality`).
5. **Marking-scheme alignment** — past paper questions are linked to
   their marking schemes via topic + question-number key.

For every PDF (syllabus / past paper / marking scheme), the pipeline
runs the following 6 stages in order:

**Stage 1 — OCR (VLM dispatch)**

- **Inputs:** raw PDF bytes from
  `stedding/ingest_queue/{ncca,examinations,curriculumonline}.ie/`
- **Action:** call `select_ocr_backend()` from
  `cianfhoghlaim/ocr/models/registry.py` to pick the optimal
  (model, backend) pair from `VISION_MODELS`
  - Small text-first PDFs (<5 MB) → `gemma-4-E2B` (MLX)
  - Dense syllabi (5–20 MB) → `gemma-4-26B-A4B` (llama-swap)
  - SEC exam papers (image-heavy) → `qwen3-vl-8b` (llama-swap)
  - Old scanned Gaelic texts (pre-1922) → `glm-4.6v-flash` (MLX)
  - Marking-scheme image-heavy → `molmo2-8b` (transformers)
- **Outputs:** `page_text` (per-page) + `page_image` (rendered as
  PNG, 200 DPI)
- **Sink:**
  `motherduck://oideachais.pdf_processing.{subject}.{year}.{paper}.ocr_pages`

**Stage 2 — Diagram detection (region segmentation)**

- **Inputs:** `page_image` from Stage 1
- **Action:** call `Granite-Docling-258M` for DocTags-based layout
  classification (figure / table / heading / paragraph) AND
  `Molmo2-8B` for figure-region pointing (returns bounding boxes)
- **Outputs:** `page_diagrams` (list of `{bbox, type, caption}` per
  page)
- **Sink:**
  `motherduck://oideachais.pdf_processing.{subject}.{year}.{paper}.diagrams`

**Stage 3 — BAML extraction (typed records)**

- **Inputs:** `page_text` from Stage 1 + `page_diagrams` from
  Stage 2
- **Action:** route through BAML clients per the schema type:
  - Syllabus → `ExtractLeavingCertSyllabus(page_text)` (BAML at
    `cianfhoghlaim/baml/education/lc_extraction/curriculum_syllabus.baml`)
  - Past paper → `ExtractExamPaperLayout(page_text)` (BAML at
    `cianfhoghlaim/baml/education/lc_extraction/exam_paper_layout.baml`)
  - **Marking scheme → `ExtractMarkingScheme(page_text)` (BAML at
    `cianfhoghlaim/baml/education/lc_extraction/marking_scheme.baml`)**
  - All clients go through `litellm.cianfhoghlaim.ie:4000` with
    `LitellmClient` (vendor-de-risked) → `minimax` fallback
- **Outputs:** typed BAML records (Pydantic-validated)
- **Sink:**
  `motherduck://oideachais.pdf_processing.{subject}.{year}.{paper}.extracted`

**Stage 4 — Topic validation (cross-reference to NCCA taxonomy)**

- **Inputs:** BAML records from Stage 3 + NCCA syllabus topics
- **Action:** for every `topic` field in a past paper question or
  marking point, fuzzy-match against the NCCA syllabus topic list
  (95% threshold on `name` field); reject mismatches and flag for
  human review
- **Outputs:** `validated_records` (BAML records with
  `topic_validated: bool` + `topic_match: str | None`)
- **Sink:**
  `motherduck://oideachais.pdf_processing.{subject}.{year}.{paper}.validated`

**Stage 5 — Semantic chunking (CocoIndex v1)**

- **Inputs:** `validated_records` from Stage 4 + `page_diagrams` from
  Stage 2
- **Action:** semantic chunker respects:
  - **Syllabus:** chunk by topic (one chunk per SyllabusTopic)
  - **Past paper:** chunk by question (one chunk per
    PastExamQuestion)
  - **Marking scheme:** chunk by marking point (one chunk per
    MarkingPoint)
  - **Diagrams:** one chunk per detected figure region (with caption
    as chunk text)
- **Chunk size:** 256-1024 tokens (within BGE-M3 sweet spot)
- **Embedder:** `BAAI/bge-m3` multilingual (1024-dim, 100+ batched)
- **Outputs:** `chunks` table (chunk_id, doc_id, chunk_type, text,
  embedding)
- **Sink:** `lancedb://oideachais.pdf_processing_chunks` (IVF_HNSW
  + FTS index)

**Stage 6 — Lakehouse + cognee cognify + Graphiti**

- **Inputs:** `chunks` from Stage 5 + `validated_records` from
  Stage 4
- **Action:** write to DuckLake + run Cognee cognify (entity
  extraction) + Graphiti episode append
- **Outputs:**
  `motherduck://oideachais.assets.official_documents.{syllabus|past_papers|marking_schemes}.{subject}.{year}.{paper}`
  + `cognee://oideachais.pdf_processing` dataset
- **Sink:** DuckLake (Parquet on Garage S3 + Postgres catalog) +
  Memgraph (KG) + LanceDB (vector)

## Requirements

### Requirement: 6-stage PDF processing pipeline

The system SHALL orchestrate a 6-stage PDF processing pipeline that
processes NCCA syllabus PDFs, SEC past paper PDFs, and SEC
marking-scheme PDFs through 6 ordered stages. The pipeline consumes
the 22-entry `VISION_MODELS` registry at
`cianfhoghlaim/ocr/models/registry.py` and the 6-entry
`CLASSICAL_OCR` Docker registry, and produces typed BAML records,
cocoindex-embedded chunks, and a DuckLake/MotherDuck/Graphiti KG
graph.

The 6 stages are: (1) OCR (VLM dispatch), (2) diagram detection
(Granite-Docling + Molmo2-8B pointing), (3) BAML extraction, (4)
topic validation (NCCA taxonomy fuzzy-match), (5) semantic chunking
(CocoIndex v1 + BGE-M3), (6) lakehouse + Cognee + Graphiti.

#### Scenario: A new NCCA mathematics syllabus lands

- **GIVEN** a new NCCA primary mathematics specification PDF is
  uploaded to `stedding/ingest_queue/ncca.ie/`
- **WHEN** the `pdf_processing_assets/asset_generation/official_documents/syllabus.py`
  Dagster asset materialises
- **THEN** Stage 1 calls `gemma-4-26B-A4B` (llama-swap, Unsloth
  GGUF) for OCR
- **AND** Stage 2 detects 8 figure regions (3 diagrams + 5 tables)
  via Granite-Docling
- **AND** Stage 3 calls `ExtractLeavingCertSyllabus` which returns
  12 `SyllabusTopic` records
- **AND** Stage 4 validates all 12 topics against the existing NCCA
  taxonomy (100% pass)
- **AND** Stage 5 chunks into 12 semantic chunks (1 per topic) + 8
  diagram chunks = 20 chunks
- **AND** Stage 6 writes to
  `ducklake://oideachais.assets.official_documents.syllabus.mathematics.2026`
  + embeds in LanceDB
- **AND** the marimo dashboard at `/dashboards/primary-maths` shows
  the new syllabus within 60 seconds

#### Scenario: An LC Irish past paper is processed

- **GIVEN** a 2024 LC Honours Irish past paper (24 pages,
  image-heavy, 8 questions)
- **WHEN** the `pdf_processing_assets/asset_generation/official_documents/past_paper.py`
  Dagster asset materialises
- **THEN** Stage 1 dispatches to `qwen3-vl-8b` (llama-swap, Unsloth
  GGUF) for OCR
- **AND** Stage 2 detects 2 figure regions (a poem extract + a
  historical map)
- **AND** Stage 3 calls `ExtractExamPaperLayout` which returns 8
  `PastExamQuestion` records (4 Roinn A + 4 Roinn B, 100 marks
  total)
- **AND** Stage 4 validates topics against the Irish syllabus
  (5/8 match "Litríocht", 3/8 match "Teanga Bheo", 0 mismatches)
- **AND** Stage 5 chunks into 8 question chunks + 2 figure chunks +
  4 marking-scheme-aligned chunks = 14 chunks
- **AND** Stage 6 writes to
  `ducklake://oideachais.assets.official_documents.past_papers.irish.2024.paper-1`
  + Cognee cognify creates 8 Question nodes + 2 Figure nodes + 12
  Topic reference edges

#### Scenario: A marking scheme is aligned to a past paper

- **GIVEN** a 2024 LC Maths marking scheme PDF (32 pages,
  partial-formula-image-heavy)
- **WHEN** the
  `pdf_processing_assets/asset_generation/official_documents/marking_scheme.py`
  Dagster asset materialises
- **THEN** Stage 1 dispatches to `molmo2-8b` (transformers) for OCR
  with formula-aware prompting
- **AND** Stage 2 detects 18 formula-image regions (LaTeX math
  expressions)
- **AND** Stage 3 calls `ExtractMarkingScheme` (BAML) which returns
  18 `MarkingPoint` records
- **AND** Stage 4 cross-references every
  `MarkingPoint.question_number` with the corresponding
  `PastExamQuestion.questionNumber` (16/18 match; 2 flagged for
  human review due to optional-question ambiguity)
- **AND** Stage 5 chunks into 18 marking-point chunks + 18 formula
  chunks = 36 chunks
- **AND** Stage 6 writes to
  `ducklake://oideachais.assets.official_documents.marking_schemes.mathematics.2024.paper-1`
  + Graphiti episode:
  `{"type": "marking_scheme", "subject": "mathematics", "year": 2024, "paper": "paper-1", "marking_points": 18}`

### Requirement: 3 BAML clients for PDF processing

The system SHALL use the 3 existing BAML clients for PDF processing
extraction. The 3 clients are:

1. **`LitellmClient`** (default) — `deepseek/deepseek-chat` via
   `litellm.cianfhoghlaim.ie:4000`
2. **`Extractor`** — `minimax` via LiteLLM gateway with 3-key
   rotation (vendor-de-risked; used as the canonical Irish-language
   path)
3. **`ExtractEnStrong`** — `gpt-4o-mini` via LiteLLM (only used as
   fallback for non-Irish content)

For VL tasks (figure captioning, diagram pointing), the
`qwen3-vl-8b` Unsloth GGUF is invoked directly via llama-swap (not
through the BAML clients).

#### Scenario: A BAML extraction routes through LitellmClient for text

- **GIVEN** Stage 3 needs to extract a SyllabusTopic from
  `page_text`
- **WHEN** `b.ExtractLeavingCertSyllabus(page_text)` is called
- **THEN** the `LitellmClient` routes to `deepseek/deepseek-chat` via
  `http://litellm.cianfhoghlaim.ie:4000/v1/chat/completions`
- **AND** the response is parsed into a `SyllabusTopic` Pydantic
  record
- **AND** the record is written to the `extracted` table

#### Scenario: Figure captioning routes through llama-swap for VL

- **GIVEN** Stage 2 needs to caption a detected figure region
- **WHEN** `qwen3-vl-8b` is called via
  `http://llama-swap:8080/v1/chat/completions`
- **THEN** the VLM returns a 1-sentence caption in the requested
  language (Irish or English)
- **AND** the caption is written to the `page_diagrams` table

### Requirement: 3 VLM-specific processing tasks

The system SHALL use the 22-entry `VISION_MODELS` registry (per
`meaisinfhoghlaim-ocr-htr/spec.md`) to handle 3 VLM-specific tasks
in the PDF processing pipeline. The 3 tasks are:

- **Task A — Figure region detection** (Granite-Docling + Molmo2-8B)
- **Task B — Figure captioning** (Qwen3-VL 8B or Gemma 4 12B)
- **Task C — Marking-scheme formula OCR** (DeepSeek-OCR-2 or
  Qwen3-VL 8B)

Each task MUST dispatch to a model with the corresponding
`ModelCapability.DIAGRAM` tag (see `meaisinfhoghlaim-ocr-htr/spec.md`
and `cianfhoghlaim/ocr/models/registry.py`).

#### Scenario: A chemistry paper with 6 organic-chemistry diagrams

- **GIVEN** a 2024 LC Chemistry paper page 7 with 6
  organic-chemistry diagrams
- **WHEN** Stage 2 + Stage 3 run on this page
- **THEN** Granite-Docling classifies 6 figure regions + 1 table
  region + 1 heading region
- **AND** Molmo2-8B returns 6 bounding boxes for the diagrams
- **AND** Qwen3-VL 8B captions each diagram in 1 sentence (Irish:
  "Léaráid de mhóilín meatáin"; English: "Diagram of a methane
  molecule")
- **AND** the captions are stored in `page_diagrams` with
  `caption_en` and `caption_ga` fields

#### Scenario: A maths marking scheme with 18 LaTeX formulas

- **GIVEN** a 2024 LC Maths marking scheme page 12 with 18 LaTeX
  formula images
- **WHEN** Stage 1 + Stage 2 run on this page
- **THEN** Stage 1 dispatches to `molmo2-8b` (transformers) for OCR
  with formula-aware prompting
- **AND** Stage 2 dispatches to `deepseek-ocr-2` (the v2 superset;
  `deepseek_vl_v2` arch) for the LaTeX formula OCR
- **AND** all 18 formulas are extracted as `MarkingPoint.latex`
  fields

### Requirement: Marimo dashboard for processed PDFs

The system SHALL provide a marimo notebook at
`cianfhoghlaim/notebooks/03_leaving_cert/12_pdf_processing.py` that
visualises the 6-stage pipeline state for any `(subject, year,
paper)` tuple. The notebook SHALL include a sidebar selector for
`(subject, year, paper)` from the DuckLake `pdf_processing` table
and a status panel for each of the 6 stages.

The notebook SHALL include:
- A sidebar selector for `(subject, year, paper)` from the DuckLake
  `pdf_processing` table
- Stage 1 status: per-page OCR confidence + image preview
- Stage 2 status: per-page diagram detection with bounding-box
  overlay
- Stage 3 status: BAML extraction preview (first 3 records per
  stage)
- Stage 4 status: topic validation pass/fail rate + mismatched
  records
- Stage 5 status: chunk count per type + BGE-M3 embedding UMAP
  projection
- Stage 6 status: lakehouse row count + Cognee KG node count +
  Graphiti episode count

#### Scenario: A teacher opens the PDF processing dashboard

- **GIVEN** a 2024 LC Irish paper-1 has been processed (14 chunks,
  2 figures, 8 questions)
- **WHEN** a teacher navigates to
  `/dashboards/pdf-processing?subject=irish&year=2024&paper=paper-1`
- **THEN** the marimo notebook renders with all 6 stage statuses
- **AND** the teacher can click on any figure to see the bbox
  overlay + caption
- **AND** the teacher can click on any chunk to see its BGE-M3
  embedding + nearest neighbours

### Requirement: Gradio interface for human review

The system SHALL provide a Gradio interface at
`spaces/oideachais-pdf-review/` (HF Space, deployable via the
`spaces-cicd-pipeline` spec) that allows human reviewers to approve
/ reject topic validations flagged in Stage 4, correct
mis-categorised questions, add notes to marking-scheme ambiguities,
and export validated records back to the lakehouse. The Gradio
interface MUST be backed by `unsloth/gemma-3-4b-it-GGUF` for the
in-app "suggested correction" feature and
`unsloth/gemma-4-26B-A4B-it-GGUF` for the in-app "explain why this
is mis-categorised" feature.

#### Scenario: A reviewer corrects a mis-categorised question

- **GIVEN** Stage 4 flagged 2 past paper questions as
  mis-categorised
- **WHEN** a reviewer opens the Gradio interface
- **THEN** the interface shows the 2 flagged questions with the
  suggested correct topic
- **AND** the reviewer can accept / override the suggestion
- **AND** the corrected record is written back to
  `motherduck://oideachais.pdf_processing.{subject}.{year}.{paper}.validated`
- **AND** the next Dagster materialisation includes the corrected
  records

### Requirement: VLM dispatch via `select_ocr_backend()`

The system SHALL wire the 6-stage PDF processing pipeline to the
canonical `select_ocr_backend()` function at
`cianfhoghlaim/ocr/models/registry.py:select_ocr_backend` for
Stage 1. The function MUST consider PDF size (existing heuristic),
filename pattern (existing: SEC / examination / leaving_cert), page
count (single-page PDFs → `gemma-4-E2B`; multi-page >10 →
`qwen3-vl-8b`), image density (high image-to-text ratio →
`molmo2-8b` for diagram pointing), and BAML fallback (if the VLM
extraction fails, fall back to classical OCR (Docling-serve) then
to text-only BAML).

#### Scenario: A 50-page marking scheme is processed

- **GIVEN** a 50-page marking scheme (image-heavy,
  partial-formula)
- **WHEN** `select_ocr_backend()` is called
- **THEN** it dispatches to `qwen3-vl-8b` (Unsloth GGUF) for Stage 1
- **AND** `molmo2-8b` for Stage 2 (figure pointing)
- **AND** `deepseek-ocr-2` for Stage 3 (formula OCR)
- **AND** the 3 models run in parallel via asyncio (within the
  50-page corpus)

## Cross-references

- `oideachais-pipeline/spec.md` — the parent DLT + Dagster pipeline
- `oideachais-baml-schemas/spec.md` — the BAML extraction clients
- `oideachais-marimo-dashboards/spec.md` — the marimo visualisation
  layer
- `oideachais-cocoindex-v1-migration/spec.md` — the CocoIndex v1
  embedding flow
- `oideachais-semantic-search/spec.md` — the LanceDB HNSW search
  layer
- `celtic-asset-generation/spec.md` — the parent asset-generation
  orchestrator
- `meaisinfhoghlaim-ocr-htr/spec.md` — the 22-entry VISION_MODELS
  registry
- `spaces-cicd-pipeline/spec.md` — the HF Space deployer
- `openspec/research/2026-06-29-ocr-vlm-registry-audit/kcg-ocr-vlm-registry.md`
  — the 22-model HF audit
- `.agents/skills/celtic-asset-generation/SKILL.md` — the
  asset-generation skill
- `.agents/skills/agent-observability/SKILL.md` — the Langfuse +
  MLflow trace layer for the 6 stages
- `cianfhoghlaim/agents/meaisinfhoghlaim/AGENTS.md` — the 12-agent
  fleet that consumes the processed PDFs
