## MODIFIED Requirements

### Requirement: BIEP Subject + BIEP v2 Notebooks — ibis-first wiring to local lakehouse

The system SHALL require the 6 BIEP subject marimo notebooks
(Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science)
under `cianfhoghlaim/notebooks/04_biep_motherduck/` AND the **4 new BIEP v2
cross-jurisdiction notebooks** (00_overview, 01_junior_cycle_explorer,
02_england_explorer, 03_ocr_ensemble_audit) under
`cianfhoghlaim/notebooks/04_biep_v2/` to default to the local
`bunchloch-infra` lakehouse via the `ibis.duckdb.connect()` +
`ibis.lancedb.connect()` entrypoints. The 6 subject notebooks MUST use
the per-subject `ducklake_<subject>` database name. The 4 BIEP v2
notebooks MUST use the unified `ducklake_oideachais` database name.

The system SHALL reject any raw `duckdb.connect()` call in any of these
10 notebooks per the ibis-first contract.

#### Scenario: 4 BIEP v2 notebooks obey the ibis-first contract

- **GIVEN** the lakehouse stack (Garage + Lakekeeper + Lance) is up per
  the `2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1` change
- **WHEN** the operator runs
  `marimo run cianfhoghlaim/notebooks/04_biep_v2/03_ocr_ensemble_audit.py`
- **THEN** the notebook's first data cell SHALL execute
      `conn = ibis.duckdb.connect("md:oideachais")`
- **AND** it SHALL resolve
      `lance = ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")`
- **AND** every data query SHALL be expressed as an ibis expression
  rather than raw SQL strings
- **AND** the 8-panel audit trail (PDF + Docling + Unstract + 2 VLM
  responses + RAGAS score + final BAML Pydantic + Langfuse trace link)
  renders against the live ensemble asset
