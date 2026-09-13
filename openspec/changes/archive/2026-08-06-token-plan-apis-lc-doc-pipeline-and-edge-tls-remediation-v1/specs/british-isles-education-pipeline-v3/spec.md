## ADDED Requirements

### Requirement: Leaving Certificate corpus processing via token-plan APIs

The BIEP v3 pipeline SHALL process the staged Leaving Certificate corpus at
`leaving_certificate/` (13 subjects — applied_mathematics, biology,
business, chemistry, computer_science, english, french, gaeilge, geography,
history, mathematics, technology, ukrainian — each with `en/` and `ga/`
sub-corpora of syllabi, guideline material, specifications, and exam
papers) using the per-cohort 5-phase pattern (Ingestion → Extraction →
Embedding → ibis logging → Analytics):

- **Ingestion** MUST use a DLT filesystem source rooted at
  `leaving_certificate/<subject>/<lang>/` (files are already local;
  `USE_LOCAL_SCRAPES=true` semantics apply — no live scraping).
- **Extraction** MUST run the canonical lc6 BAML functions
  (`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`,
  `ExtractMarkingSchemeGuideline`, `ExtractCrossLinguisticConcept`) with
  MiniMax-M3 (token-plan direct endpoint) as the primary client and
  `qwen3.7-plus` (Qwen token plan) as the secondary cross-check client;
  disagreements between the two MUST be logged as Langfuse observations.
- **OCR fallback**: PDF rasterisation MUST prefer the local llama-swap
  `qwen3-vl-8b` path; pages below the OCR confidence threshold MAY be
  re-processed by the MiniMax-M3 multimodal endpoint.
- **Loading** MUST land rows in DuckLake tables under
  `cianfhoghlaim.leaving_cert.*` via the canonical
  `get_dlt_destination(use_ducklake=True)` destination.
- The resulting tables MUST be discoverable via `schema_introspect` /
  `schema_introspect_table` (per the existing BIEP v3 introspection
  requirement).

#### Scenario: New syllabus PDFs are dropped into the corpus

- **WHEN** new PDF files land under
  `leaving_certificate/chemistry/ga/`
- **AND** the LC Dagster asset for the chemistry cohort is materialised
- **THEN** the DLT filesystem source SHALL ingest only the new files
- **AND** the BAML extraction stage SHALL produce structured rows via the
  MiniMax-M3 token-plan endpoint
- **AND** the rows SHALL land in `cianfhoghlaim.leaving_cert.chemistry`

#### Scenario: Token-plan endpoint unavailable during extraction

- **WHEN** the MiniMax-M3 endpoint is unreachable during the extraction
  phase
- **THEN** the pipeline SHALL retry per the BAML client retry policy
- **AND** if retries are exhausted, SHALL fail the asset run with an
  explicit error (no silent data loss)
- **AND** the local `qwen3-vl-8b` OCR stage SHALL remain available so
  ingestion-stage outputs are preserved for re-extraction

#### Scenario: Cross-model disagreement is observable

- **WHEN** `qwen3.7-plus` produces an extraction that differs from the
  MiniMax-M3 primary for the same document section
- **THEN** the disagreement SHALL be recorded as a Langfuse observation at
  the configured `LANGFUSE_HOST`
- **AND** the primary (MiniMax-M3) value SHALL be the one loaded to
  DuckLake
