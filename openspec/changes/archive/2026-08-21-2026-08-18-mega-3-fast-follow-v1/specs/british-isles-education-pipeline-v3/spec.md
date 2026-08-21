## ADDED Requirements

### Requirement: 4-path OCR ensemble BAML → CocoIndex wire

The system SHALL wire the 4-path OCR ensemble BAML function
(`Run4PathEnsemble`) into the `ensembled_extraction` CocoIndex App at
`cocoindex_flows/british_isles/england/education/ensembled_extraction.py`
using the `spawn` + `await` BAML pattern (BEP-034).

The 4 paths are: BAML (`ExtractAQAQualSpec`) + Unstract
(`RunUnstractWorkflow`) + qwen3-vl-8b (`ConcurrentRunLLM`) + gemma-4
(`ExtractGemma4Vision`). Each path runs as a `spawn` block; the
ensemble uses `catch_all` to degrade gracefully on any single path
failure.

#### Scenario: The 4-path ensemble runs concurrently with graceful degradation

- **GIVEN** a NCCA PDF for one of the 3 England awarding bodies
- **WHEN** the `ensembled_extraction` CocoIndex App runs
- **THEN** the 4 paths run concurrently as `spawn` blocks
- **AND** any path that fails is caught by `catch_all` and returns a
  `PathOutput { path: "<name>", schema_valid: false }` (so the
  ensemble never aborts)
- **AND** the RAGAS vote (per the existing `EnsembleConsensus`
  class) selects the best path

#### Scenario: The baml tour notebook demonstrates the 5 lc6 functions

- **GIVEN** the `notebooks/00_baml_tour.py` educative notebook
- **WHEN** an operator opens the notebook via `marimo edit 00_baml_tour`
- **THEN** the notebook demonstrates every BAML feature used by the
  BIEP v3 jurisdiction dashboards (the 5 lc6 functions, the
  qpack_template, the cross-linguistic concept extraction, the
  syllabus diagram extraction)
- **AND** each cell has a `@app.cell(hide_code=True)` prose intro
  (the E1 pattern from `00_marimo_patterns_tour.py`)