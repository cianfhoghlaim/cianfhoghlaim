## ADDED Requirements

### Requirement: CocoIndex → Marimo dataset analysis notebook

The system SHALL provide a dedicated `notebooks/10_biep_pipeline_lakehouse_01_dataset_analysis.py`
that demonstrates CocoIndex → Marimo integration.

The notebook uses:
- `cocoindex_query_api.search(query, top_k=5)` (from the FF.5 helper)
- `marimo_baml.ExtractSubjectFromChunk(chunk)` (from the FF.2 helper)
- The 4 stage Marimo dashboards

#### Scenario: The notebook reads from CocoIndex + extracts with BAML

- **WHEN** the operator runs the notebook
- **THEN** the notebook reads 100 chunks from the LC stage
  CocoIndex App + extracts the subject from each chunk via BAML
- **AND** the results are rendered as a `mo.ui.table`