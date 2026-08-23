# cianfhoghlaim-tertiary-marimo Specification

## Purpose

3 sibling marimo dashboards providing visual parity with the BIEP
SEC exam-papers explorer (`notebooks/10_biep_pipeline_lakehouse_06_exam_papers_explorer.py`).
Each notebook has 8 tabs (Health / Filters / Materials / URL
Health / Heatmap / Recent / Lance Search / SQL Console) and uses
`mo.sql(engine=md:cianfhoghlaim)` primary + local DuckDB fallback.

## Requirements

### Requirement: 3 sibling notebooks, 8 tabs each

The system SHALL provide:

| Notebook | URL mount | Primary tables |
|---|---|---|
| `notebooks/12_uog_exam_papers.py` (supersedes `11_uog_exam_papers.py` from the WS1 lift) | `/dashboards/university-exam-papers` | `uog_exam_papers`, `uog_exam_lo_map` |
| `notebooks/13_nui_federation.py` | `/dashboards/nui-federation` | `nui_members`, `nui_constituent_circulars`, `nui_archive` |
| `notebooks/14_uog_students_union.py` | `/dashboards/uog-students-union` | `uog_students_union_documents`, `uog_su_class_rep_handbooks` |

#### Scenario: Tab 3 (Materials) renders the right records

- **GIVEN** the DuckLake `nui_members` table has 4 rows
- **WHEN** the user opens tab 3 of `13_nui_federation.py`
- **THEN** the table displays all 4 NUI member universities in a
  paginated marimo `mo.ui.table` widget

### Requirement: ibis-first entrypoint (per BIEP)

Per the `cianfhoghlaim-biep-notebooks-wire-to-local-lakehouse`
rule, every notebook SHALL use `import ibis` + `ibis.duckdb.connect(uri)`
instead of raw `duckdb.connect()`.

#### Scenario: Zero raw `duckdb.connect()` calls

- **WHEN** the 3 new notebooks are grepped
- **THEN** `grep -c "duckdb\\.connect" notebooks/1{2,3,4}_*.py`
  returns `0`
- **AND** every data cell resolves through an ibis DataFrame

### Requirement: PEP 723 inline dependency blocks

Per the `cianfhoghlaim-marimo-dashboards` spec, every notebook
SHALL ship with a PEP 723 `# /// script … # ///` header so
`uv run notebook.py` works without `pyproject.toml`.

#### Scenario: A reviewer runs `uv run notebooks/13_nui_federation.py`

- **GIVEN** the reviewer has the cianfhoghlaim repo cloned
- **WHEN** they execute `uv run notebooks/13_nui_federation.py`
- **THEN** marimo starts on port 8080 (or the configured port)
- **AND** the notebook renders with the 8 tabs

### Requirement: MLflow experiment name per notebook

Each notebook SHALL lazily bootstrap an MLflow experiment so
reviews can track which queries are slow / error-prone.

#### Scenario: Notebook 13 emits an experiment entry

- **GIVEN** a reviewer runs `13_nui_federation.py`
- **WHEN** tab 5 (Heatmap) is loaded
- **THEN** MLflow experiment `cianfhoghlaim-nui-federation`
  receives the query latency (`nui_members_view_ms=…`)
