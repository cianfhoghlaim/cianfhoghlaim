# Spec Delta: oideachais-pipeline

## ADDED Requirements

### Requirement: Tripartite Data Landscape

The system SHALL model the Irish education data through
**three evidential sources** with distinct governance:

- **Pedagogical intent** — the NCCA curriculum (the "what
  should be taught")
- **Evidentiary truth** — SEC examination papers + marking
  schemes (the "what was actually assessed")
- **Temporal governance** — NCCA circulars (the "what changed
  and when")

#### Scenario: Cross-source query returns all three lenses

- **GIVEN** a Dagster asset materialises the
  `oideachais.education.ie.curriculum` table
- **WHEN** a marimo dashboard queries for the Junior Cycle
  Mathematics syllabus
- **THEN** the dashboard SHALL display the NCCA syllabus
  (pedagogical intent), the last 3 years of SEC exam papers
  (evidentiary truth), and any 2024-2025 NCCA circulars
  (temporal governance) side-by-side

### Requirement: Bilingual data strategy

The system SHALL support bilingual (English + Irish) data
through a **unified concept node** with separate
language-specific `HAS_FORM` edges. The concept node is the
canonical entity; the language-specific forms are edges
to the language-specific text.

#### Scenario: English query returns the canonical concept

- **GIVEN** a user queries "handwriting recognition for Irish"
- **WHEN** the RAG pipeline resolves the query to a
  `HandwritingRecognition` concept node
- **THEN** the result includes the English form
  ("handwriting recognition for Irish") + the Irish form
  ("aithint scribhneoireachta") + 1+ synonym layer (e.g.
  "OCR for Irish handwriting" → "OCR do scribhneoireacht
  Ghaeilge")

## REMOVED Requirements

(None.)
