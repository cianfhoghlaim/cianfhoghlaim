## MODIFIED Requirements

### Requirement: 24-model 4-backend v4 registry (replaces the legacy 10-model/6-backend)

The canonical OCR/VLM registry SHALL be `VISION_MODELS` with **24
entries** (per `cianfhoghlaim/meaisinfhoghlaim/models/registry.py`),
not the legacy `OCR_MODELS` (10 entries) + `VLM_MODELS` (6 entries).

The 4 backends SHALL be `litellm, mlx, transformers, llama-swap`
(NOT `openai, anthropic, ollama` — all cloud-API backends were
dropped in v4 per user request).

The 9 `ModelCapability` enum values are: `DENSE_OCR, GROUNDING,
TABLES, LATEX, REASONING, MATH, MULTILINGUAL, GAELIC, DIAGRAM` (the
new `DIAGRAM` was added 2026-06-29).

The 5-tier role ladder is: `tier1_heavy, tier2_medium, tier3_light,
specialist, legacy`.

#### Scenario: A consuming agent picks the v4 default for M4 Max 48 GB

- **WHEN** `get_default_for_m4_max()` is called from any Dagster asset / BAML function / notebook
- **THEN** the return value SHALL be `"gemma-4-26B-A4B"` (the 26.5B MoE / 4B active sweet-spot model)

#### Scenario: `select_ocr_backend()` routes PDFs by filename + language

- **WHEN** a chemistry syllabus PDF (name `SCSEC09_*_syllabus_*.pdf`) is passed to `select_ocr_backend(pdf_path)`
- **THEN** the returned model SHALL be `gemma-4-26B-A4B`
- **AND** an Irish-language PDF SHALL return `glm-4.6v-flash`
- **AND** a marking-scheme PDF SHALL return `molmo2-8b`

### Requirement: LC5 + Gemini pipelines use the v4 registry

The Leaving Certificate 5-subject pipeline and the Gemini 6-corpus pipeline SHALL route all PDF ingestion through `select_ocr_backend()` for the LC5 corpus and through `qwen3-vl-8b` for the Gemini corpus.

#### Scenario: The LC5 pipeline ingests a chemistry PDF

- **GIVEN** `cianfhoghlaim/leaving_certificate/chemistry/en/SC-Chemistry-Specification-EN.pdf` is encountered
- **WHEN** `leaving_cert_source._classify_pdf(pdf_path)` runs
- **THEN** `("gemma-4-26B-A4B", "syllabus", ...)` SHALL be returned

#### Scenario: The Gemini pipeline ingests 224 PDFs

- **WHEN** `gemini_corpus_source.gemini_documents()` runs over all 6 Gemini corpora
- **THEN** 224 rows SHALL be yielded (57+54+47+30+24+12; verified 2026-07-04)
- **AND** every PDF SHALL have `model_key="qwen3-vl-8b"` (the v4 workhorse for text-heavy PDFs)
