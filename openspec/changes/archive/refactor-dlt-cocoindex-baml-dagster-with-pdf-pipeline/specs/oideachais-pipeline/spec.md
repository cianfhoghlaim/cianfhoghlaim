## MODIFIED Requirements
### Requirement: baml/ files MUST NOT have duplicate enum definitions (MUST enforce canonical single definition per the baml-reorganize-by-cluster change)

The system MUST enforce that no duplicate enum definitions exist across
the 60+ BAML files. The 5 NCCA stage BAML files and the 8 qpack
subject files SHALL have no duplicate enum definitions.
#### Scenario: A new subject asset references a shared enum

- **GIVEN** the canonical `LeavingCertSubject` enum defined in
  `baml/education/_shared/education_level.baml`
- **WHEN** `baml/education/subjects/qpack_mathematics.baml` uses
  `LeavingCertSubject::LC_MATHS`
- **THEN** the reference MUST resolve via the shared enum
- **AND** no duplicate definition SHALL exist in qpack_mathematics.baml

### Requirement: dlt/ source files use canonical cianfhoghlaim.dlt.* paths

All 200+ `.py` files in `dlt/` SHALL use the canonical
`cianfhoghlaim.dlt.*` import paths. The legacy `dlt_sources.*`
namespace (used pre-v4) SHALL NOT appear in any dlt/, dagster/, or
cocoindex/ file.

#### Scenario: A dlt source imports a helper

- **WHEN** `dlt/british_isles/scotland/law/legislation.py` needs the
  legislation crawler helper
- **THEN** it MUST use `from cianfhoghlaim.dlt.law._legislation_helper
  import _crawl_legislation` (not the legacy `from dlt_sources.law...`)

### Requirement: dagster assets are organised by domain

The 65+ dagster asset files SHALL be organised under
`dagster/assets/by_domain/` by domain (education, law, medicine,
filesystem, api, language, official_media, portfolio, site_analysis,
statistics). Backward-compat re-exports SHALL preserve the old top-level
paths for one release.

#### Scenario: A developer adds a new subject asset

- **WHEN** a new NCCA subject (e.g. ukrainian) is added
- **THEN** the developer MUST create `dagster/assets/by_domain/education/
  ukrainian_assets.py` (NOT `dagster/assets/ukrainian_assets.py`)
- **AND** the legacy `dagster/assets/ukrainian_assets.py` SHALL be
  created as a backward-compat re-export from the by_domain/ path

### Requirement: The 6-asset per-subject pattern MUST be enforced for all 11 LC subjects

For each of the 11 NCCA LC subjects, the dagster asset group MUST
contain 6 assets following the
`{subject}_syllabus_raw / structured / quest_pack / embedding /
cognify / dashboard` pattern.

#### Scenario: Materialise the english asset group

- **WHEN** `dagster asset materialize --select "english_*"` is run
- **THEN** all 6 english assets MUST materialise in order:
  raw (DLT ingest) → structured (BAML extract) → quest_pack
  (BAML generate) → embedding (CocoIndex) → cognify (Cognee) →
  dashboard (marimo)
- **AND** the asset_graph MUST include english_syllabus_raw,
  english_syllabus_structured, english_quest_pack,
  english_embedding, english_cognify, english_dashboard

### Requirement: PDF processing pipeline MUST handle all 133 leaving_certificate/ PDFs (MUST produce all 7 DuckLake output tables)

The system MUST process all 133 leaving_certificate/ PDFs through
the 8-asset pattern. The pipeline in
`dagster/assets/by_domain/pdf_processing.py` SHALL produce all 7
output tables in DuckLake.

#### Scenario: Process the maths subject

- **WHEN** `dagster asset materialize --select "pdf_processing_*"` is run
- **THEN** all 133 PDFs (11 subjects × 2 languages × 3 levels) MUST
  be processed
- **AND** 7 valid output tables MUST be written to DuckLake:
  pdf_documents, pdf_ocr_results, pdf_baml_extractions,
  pdf_cocoindex_embeddings, pdf_cognify_graph, pdf_ragas_eval,
  pdf_irish_quality

### Requirement: 5 OCR model comparison for PDF extraction

The PDF processing pipeline SHALL compare 5 OCR models (deepseekocr,
docling, marker, pymupdf4llm, unstructured) on the 133 leaving_certificate/
PDFs. The comparison metrics (extraction_accuracy, runtime,
fada_preservation) SHALL be written to a Ragas evaluation notebook
in `notebooks/dashboards/pdf_processing/`.

#### Scenario: Compare OCR models on mathematics

- **WHEN** `notebooks/dashboards/pdf_processing/pdf_ocr_model_comparison.py`
  is run
- **THEN** a 5-model comparison table MUST be produced with
  extraction_accuracy (per subject), runtime (per PDF), and
  fada_preservation_rate (per page)
- **AND** the comparison MUST show all 5 OCR models ranked by
  fada_preservation_rate (the canonical Irish-content metric)