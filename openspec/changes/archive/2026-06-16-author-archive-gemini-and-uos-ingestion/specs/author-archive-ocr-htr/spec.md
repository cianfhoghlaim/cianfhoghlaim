# Spec Delta — `author-archive-ocr-htr` (new capability)

## Purpose

`author-archive-ocr-htr` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives at `oideachais/ocr/author_archive_ocr.py`. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.

OCR and HTR (handwritten text recognition) for the personal-archive scanned pages and Apple `.pages` files. Routes pages to the right back-end (Pylaia for Irish HTR, TrOCR for printed Latin, VLM for equations) and emits structured `HandwrittenEquation` rows for the equations table.

## ADDED Requirements

### Requirement: Page-Level OCR Dispatch
The system SHALL dispatch each scanned page to the correct OCR back-end based on its `language` and `equation_density` signals.

#### Scenario: Pylaia for Irish
- **GIVEN** a page from a UoG `irish/` document (`.pages` or scanned PDF)
- **WHEN** the page is dispatched
- **THEN** the Pylaia HTR model (`oideachais/ocr/pylaia_comparison.py`) SHALL be invoked
- **AND** the returned text SHALL be stored in the `author_archive.handwritten_ocr` DuckDB table with `backend="pylaia"`

#### Scenario: TrOCR for English
- **GIVEN** a page from a UoG `education/`, `mata/`, or `past/` document
- **WHEN** the page is dispatched
- **THEN** the TrOCR model SHALL be invoked (graceful fallback to PaddleOCR if not on the workstation)
- **AND** the returned text SHALL be stored with `backend="trocr"` (or `"paddleocr"` as fallback)

#### Scenario: VLM for equations
- **GIVEN** a page whose `equation_density` (count of `=`, `∫`, `∑`, `∂` symbols) is above a threshold (default 5)
- **WHEN** the page is dispatched
- **THEN** the VLM back-end (Gemini Vision via LiteLLM, see `oideachais/agents/baml_integration.py`) SHALL be invoked
- **AND** the returned LaTeX + Verbatim pair SHALL populate the `HandwrittenEquation` row for the equations index

### Requirement: Handwritten Equation Index
The system SHALL embed the extracted `HandwrittenEquation` rows into a dedicated LanceDB table `author_archive_equations` for similarity search.

#### Scenario: Equation search
- **GIVEN** the `author_archive_equations_index` Dagster asset has materialised
- **WHEN** the user runs `search_author_archive("integral of x^2 from 0 to 1")` with `artifact_kind="equation"`
- **THEN** the top 10 most similar `HandwrittenEquation` rows SHALL be returned
- **AND** each result SHALL include `file_path`, `verbatim`, `latex`, `confidence`, and the similarity score

### Requirement: Graceful Degradation
The system SHALL NOT fail an entire asset materialisation when an OCR back-end is unavailable.

#### Scenario: Back-end missing
- **GIVEN** Pylaia / TrOCR / VLM is not on the workstation
- **WHEN** the OCR runner attempts to dispatch a page
- **THEN** the runner SHALL log a warning via `structlog` (`ocr_backend_unavailable`)
- **AND** the row SHALL be emitted with `text=""`, `latex=""`, `confidence=0.0`, `backend="unavailable"`
- **AND** the BAML `ExtractHandwrittenEquations` function SHALL return an empty list (per `author-archive-baml-extraction` spec)
- **AND** the asset materialisation SHALL succeed

## MODIFIED Requirements

*(None.)*

## REMOVED Requirements

*(None.)*
