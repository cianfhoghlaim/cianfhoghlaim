# cianfhoghlaim-marimo-dashboards — academic-history delta

## ADDED Requirements

### Requirement: Academic-history notebook group (8 notebooks)

The system SHALL provide 8 new marimo notebooks at
`notebooks/14_academic_history/`:

1. `01_uog_maths_corpus_overview.py` — corpus manifest + ingestion status
2. `02_module_syllabus_assessment_map.py` — personal notes + official
   module descriptors joined
3. `03_statistics_methods_lab.py` — ST311/ST312 interactive analysis
4. `04_numerical_analysis_lab.py` — interactive numerical methods
5. `05_nonlinear_systems_lab.py` — interactive phase portraits /
   bifurcation / chaos
6. `06_formulas_theorems_worked_solutions.py` — formula/theorem registry
7. `07_assignments_exams_answers.py` — assignments + exams + answers
8. `08_academic_history_chat.py` — chat prototype

All 8 notebooks SHALL follow the canonical KCG conventions:

- PEP 723 inline dependency block
- `marimo>=0.13.0`
- 5-panel Altair layout with health banner
- `mo.sql(engine=md:oideachais)` (or `ibis.duckdb.connect` per the
  `british-isles-education-pipeline` contract) for live queries
- Graceful local-DuckDB fallback when MotherDuck is unreachable
- CLI dual-mode (`--module-code`, `--module-title`, `--year`,
  `--limit` canonical flags via `nb_utils.cl_argument_parser()`)
- Openspec cross-reference footer
- No secrets in cells (use `@app.setup` + `load_dotenv()`)

#### Scenario: All 8 notebooks parse

- **WHEN** the operator runs
  `uv run marimo run --headless notebooks/14_academic_history/01_uog_maths_corpus_overview.py`
  (and the other 7)
- **THEN** each notebook SHALL render with 0 "Pending" cells after 5
  seconds
- **AND** each notebook SHALL be discoverable via
  `uv run cianfhoghlaim-marimo list 14_academic_history`

#### Scenario: Group registered in cli.py

- **WHEN** the operator runs `uv run cianfhoghlaim-marimo list`
- **THEN** the output SHALL include `14_academic_history` in the
  `GROUPS` tuple