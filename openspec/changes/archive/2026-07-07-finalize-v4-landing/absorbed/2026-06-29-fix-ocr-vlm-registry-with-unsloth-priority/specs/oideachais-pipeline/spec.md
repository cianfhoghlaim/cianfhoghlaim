# Spec Delta: oideachais-pipeline

## ADDED Requirements

### Requirement: Cross-reference the 6-stage PDF processing pipeline

The system SHALL cross-reference the new `oideachais-pdf-processing` capability spec (at `openspec/specs/oideachais-pdf-processing/spec.md`) as the canonical 6-stage PDF processing pipeline for NCCA syllabus + SEC past paper + SEC marking-scheme PDFs. The 6 stages are:

1. **OCR (VLM dispatch)** — `select_ocr_backend()` from `cianfhoghlaim/core/cocoindex/ocr_aware_flow.py`
2. **Diagram detection** — Granite-Docling + Molmo2-8B
3. **BAML extraction** — `ExtractLeavingCertSyllabus` + `ExtractPastPaper` + `ExtractMarkingScheme`
4. **Topic validation** — fuzzy-match against NCCA taxonomy
5. **Semantic chunking** — CocoIndex v1 + BGE-M3
6. **Lakehouse + Cognee + Graphiti** — DuckLake + KG + temporal

The 6-stage pipeline is implemented at `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/pdf_processing/` and replaces the existing 4 asset classes (`syllabus`, `past_papers`, `marking_schemes`, `examiner_reports`) in `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/education/leaving_cert.py` with the more granular 6-stage flow.

#### Scenario: A leaving_cert asset triggers the 6-stage pipeline

- **GIVEN** a 2024 LC Irish past paper PDF is uploaded to `stedding/ingest_queue/examinations.ie/`
- **WHEN** the `pdf_processing_past_paper` Dagster asset materialises
- **THEN** it dispatches to the 6-stage pipeline at `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/pdf_processing/pipeline.py`
- **AND** the 6 stages run in sequence with intermediate state written to `motherduck://oideachais.pdf_processing.{subject}.{year}.{paper}.*` tables
