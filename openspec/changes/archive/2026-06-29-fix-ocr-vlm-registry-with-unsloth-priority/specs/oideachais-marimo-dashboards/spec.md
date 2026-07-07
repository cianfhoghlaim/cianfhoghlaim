# Spec Delta: oideachais-marimo-dashboards

## ADDED Requirements

### Requirement: 1 new marimo notebook for PDF processing

The system SHALL provide a new marimo notebook at `cianfhoghlaim/notebooks/meaisinfhoghlaim/marimo/03_pdf_processing.py` that visualises the 6-stage PDF processing pipeline state for any (subject, year, paper) tuple from the `pdf_processing` DuckLake table.

The notebook SHALL include:
- A sidebar selector for `(subject, year, paper)` from the DuckLake `pdf_processing` table
- Stage 1 status: per-page OCR confidence + image preview
- Stage 2 status: per-page diagram detection with bounding-box overlay
- Stage 3 status: BAML extraction preview (first 3 records per stage)
- Stage 4 status: topic validation pass/fail rate + mismatched records
- Stage 5 status: chunk count per type + BGE-M3 embedding UMAP projection
- Stage 6 status: lakehouse row count + Cognee KG node count + Graphiti episode count

The notebook is served at `/dashboards/pdf-processing` on the FastAPI app and is also deployable as a Cloudflare Worker via the `marimo-on-Cloudflare-Workers-+-Container` pattern documented in this spec.

#### Scenario: A teacher opens the PDF processing dashboard

- **GIVEN** a 2024 LC Irish paper-1 has been processed (14 chunks, 2 figures, 8 questions)
- **WHEN** a teacher navigates to `/dashboards/pdf-processing?subject=irish&year=2024&paper=paper-1`
- **THEN** the marimo notebook renders with all 6 stage statuses
- **AND** the teacher can click on any figure to see the bbox overlay + caption
- **AND** the teacher can click on any chunk to see its BGE-M3 embedding + nearest neighbours
