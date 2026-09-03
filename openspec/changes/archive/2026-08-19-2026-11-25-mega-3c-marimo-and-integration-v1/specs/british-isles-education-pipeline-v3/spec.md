## ADDED Requirements

### Requirement: BIEP v3 lineage viewer SSE streaming

The system SHALL expose a Server-Sent Events (SSE) streaming endpoint
at `/api/lineage/stream` that streams BAML `@@stream.done` outputs
from the 5 lc6 extraction functions to the BIEP v3 lineage viewer
in real-time (per the 2026-08-26-mega-3a-baml-and-adk-v1 change
D.7).

#### Scenario: SSE endpoint streams BAML extraction progress

- **GIVEN** the operator starts a BAML extraction pipeline for an NCCA PDF
- **WHEN** the lineage viewer opens `/api/lineage/stream?source_pdf=<path>`
- **THEN** the endpoint streams `data: { stage: "extract_curriculum",
  status: "in_progress", progress: 0.25 }` events as the extraction progresses

### Requirement: Marimo `mo.ui.code_editor` for the BAML prompt editor

The system SHALL use `mo.ui.code_editor(...)` to allow the operator
to edit the BAML extraction prompt at runtime.

#### Scenario: The operator edits the prompt

- **GIVEN** a BIEP v3 dashboard
- **WHEN** the operator clicks the "Edit Prompt" button
- **THEN** the dashboard renders a `mo.ui.code_editor` with the
  current BAML prompt + a "Save" button

### Requirement: Marimo `mo.ui.table` for the lineage view

The system SHALL use `mo.ui.table(...)` to display the lineage
metadata in a tabular form (per the lineage viewer requirement).

#### Scenario: The lineage table renders

- **GIVEN** a BAML extraction has produced 100 lineage rows
- **WHEN** the lineage viewer opens
- **THEN** the dashboard renders a `mo.ui.table` with the 100 rows

### Requirement: Marimo `mo.ui.slider` for the RAGAS threshold tuner

The system SHALL use `mo.ui.slider(...)` to allow the operator to
tune the RAGAS threshold (per the 4 stage dashboard adoption).

#### Scenario: The operator tunes the threshold

- **GIVEN** a BIEP v3 dashboard
- **WHEN** the operator clicks the "Tune Threshold" button
- **THEN** the dashboard renders a `mo.ui.slider` with the current
  threshold + a "Save" button