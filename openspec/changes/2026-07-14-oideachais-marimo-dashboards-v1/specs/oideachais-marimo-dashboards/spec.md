## MODIFIED Requirements

### Requirement: BIEP Notebooks — ibis-first refactor of all 11 files

The system MUST guarantee that all 11 BIEP subject + leabharlann
notebooks under `ciolanza/notebooks/04_biep_motherduck/` use
`ibis.duckdb.connect()` as the canonical KCG entrypoint (per the
`wire-biep-notebooks-to-lakehouse` change spec). The system SHALL
reject any raw `duckdb.connect()` call or any `.fetchdf()` call
in these notebooks.

Additionally, the 10 follow-up marimo dashboards under
`ciolanza/notebooks/10_marimo_dashboards/{01..10}_*.py` SHALL be
shipped as a single named group, auto-discovered by the
`ciolanza-marimo` CLI, and pass the same per-notebook AST-parse
gate as the other 12 functional groups.

#### Scenario: ibis is the canonical entrypoint in all 11 BIEP notebooks

- **WHEN** the 11 BIEP notebooks are grepped
- **THEN** every `duckdb.connect(uri)` call SHALL be replaced by
  `ibis.duckdb.connect(uri)` (was 0; now ≥ 20 across 11 files)
- **AND** every `.fetchdf()` call SHALL be replaced by
  `.to_pandas()` (was 3; now 0)
- **AND** every `duckdb.sql("SET motherduck_token=...")` SHALL be
  removed (the ibis.duckdb.connect() URL form picks up the token
  automatically)
- **AND** the `ibis` skill SHALL be referenced in each notebook's
  `## KCG patterns used` docstring

#### Scenario: All 11 BIEP notebooks boot against the live lakehouse

- **WHEN** the lakehouse stack is up (per the upgrade-4-stacks-with-infisical
  change) AND the 11 BIEP notebooks are launched via `marimo run`
- **THEN** the ibis.duckdb.connect() connection SHALL succeed (or
  fall back to MotherDuck if the local lakehouse is unreachable)
- **AND** the first data cell SHALL complete within 10 seconds
  (returns 0-row DataFrames, not errors)
- **AND** the marimo reactive graph SHALL resolve without "Pending"
  cells after 5 seconds

#### Scenario: 10 follow-up oideachais marimo dashboards at notebooks/10_marimo_dashboards/0[1-9]_*.py + 10_*.py exist + AST-parse + render

- **GIVEN** the `ciolanza-marimo` CLI's GROUPS tuple has been
  extended with `"10_marimo_dashboards"` (added 2026-07-14 per
  openspec change `2026-07-14-oideachais-marimo-dashboards-v1`)
- **WHEN** the operator runs
      `uv run cianfhoghlaim-marimo list 10_marimo_dashboards`
- **THEN** the CLI SHALL return 10 dashboards (one per row)
- **AND** all 10 notebooks SHALL AST-parse cleanly
  (`ast.parse(open(f).read())` raises no SyntaxError)
- **AND** all 10 notebooks SHALL `python3 -m py_compile` cleanly
- **AND** the 10 dashboards SHALL be:
    1. `01_biep_corpus_overview.py` — covers R1 + R9 (BIEP corpus
       overview matrix)
    2. `02_cognee_knowledge_graph.py` — covers R2 (Cognee cognify
       cohort roll-up + `cognee.search()` box)
    3. `03_cross_archive_navigation.py` — covers R3 (BIEP ↔ leabharlann
       cross-archive navigation)
    4. `04_lakehouse_table_browser.py` — covers R3 (MotherDuck +
       DuckLake `SHOW TABLES` browser + `mo.sql` console)
    5. `05_baml_extraction_log_viewer.py` — covers R7 (per-function
       BAML call-count / latency / success / retry view)
    6. `06_per_subject_analytics.py` — covers R6 + R9 (per-subject
       composite roll-up via `ibis.duckdb.connect("md:oideachais")`)
    7. `07_gaeilge_language_coverage.py` — covers R2 (Irish GA
       coverage: fada-preservation, síneadh-fada, punctum-delens)
    8. `08_cocoindex_v1_conformance_dashboard.py` — covers R10
       (7-App CocoIndex v1 conformance audit)
    9. `09_agent_memory_dashboard.py` — covers R2 + R7 (Cognee +
       Graphiti + LanceDB + Letta cohort view)
    10. `10_dagster_asset_lineage.py` — covers R7 + R9 (Dagster
        asset success / duration / pending-reattempt view + sensor
        health banner)

#### Scenario: 1 MODIFIED spec delta for oideachais-marimo-dashboards is well-formed

- **WHEN** `openspec validate 2026-07-14-oideachais-marimo-dashboards-v1 --strict`
  is run
- **THEN** the validator SHALL report zero errors
- **AND** the spec delta SHALL appear in
  `openspec/changes/2026-07-14-oideachais-marimo-dashboards-v1/specs/oideachais-marimo-dashboards/spec.md`
