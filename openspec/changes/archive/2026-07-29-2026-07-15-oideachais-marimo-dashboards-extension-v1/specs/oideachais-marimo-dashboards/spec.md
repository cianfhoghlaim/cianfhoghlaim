# Spec Delta: cianfhoghlaim-marimo-dashboards

> Parent change: [../proposal.md](../../proposal.md)

## ADDED Requirements

### Requirement: Phase 2 — 10 additional marimo dashboards (leabharlann corpus + university extraction + cross-archive edges + K-12 → university pipeline coverage)

The system SHALL provide **10 additional marimo dashboards** at
`notebooks/11_marimo_dashboards_v2/0[1-9]_*.py` +
`10_*.py`. These extend the 10 dashboards shipped by
`2026-07-14-cianfhoghlaim-marimo-dashboards-v1` (commit `44cabc151`).
Each Phase-2 dashboard:

- Uses the PEP 723 inline dependency header (`# /// script` block)
  declaring `marimo>=0.13.0`, `duckdb>=1.0`, `pandas>=2.0`,
  `altair>=5.0`
- Connects to `md:oideachais` (MotherDuck + DuckLake) with a graceful
  local-DuckDB fallback (`connect_biep_lakehouse()`-style)
- Falls back to a synthetic-data corpus when the lakehouse is
  unreachable (so notebooks render meaningfully offline)
- Renders 4-5 altair charts (heatmap, stacked bar, pie, violin/box,
  line, area) plus a health banner
- Is discoverable via `uv run cianfhoghlaim-marimo list
  11_marimo_dashboards_v2` (the `GROUPS` tuple in
  `notebooks/cli.py` MUST include
  `"11_marimo_dashboards_v2"`)

The 10 Phase-2 dashboards are:

| # | File | Coverage |
|:--|:--|:--|
| 01 | `01_leabharlann_corpus_overview.py` | leabharlann corpus overview (216 docs × 6 subdirs) |
| 02 | `02_leabharlann_subdir_matrix.py` | 6-subdir × language × year-quadrant matrix + top-12 topic pairs |
| 03 | `03_bge_m3_embedding_coverage.py` | BAAI/bge-m3 1024-d embedder coverage per subdir |
| 04 | `04_university_institution_matrix.py` | 13 HEIs (8 universities + 4 TUs + 1 college) |
| 05 | `05_qqi_nfq_ladder.py` | 8 QQI FET awards × 13 HEIs ladder matrix + NFQ distribution |
| 06 | `06_biep_leabharlann_edges.py` | BIEP ↔ leabharlann cross-archive Cognee edges |
| 07 | `07_biep_official_media_edges.py` | BIEP ↔ official-media (5 resolvers) edges |
| 08 | `08_leabharlann_culture_heritage_edges.py` | leabharlann ↔ culture-heritage (5 datasets) edges |
| 09 | `09_k12_university_pipeline_matrix.py` | 5-stage × 3-level × 13-HEI pipeline matrix |
| 10 | `10_year_level_coverage.py` | 5-stage × 10-year × bilingual coverage |

#### Scenario: Leabharlann corpus overview renders

- **GIVEN** the `notebooks/11_marimo_dashboards_v2/01_leabharlann_corpus_overview.py` notebook
- **WHEN** the user runs `marimo edit 01_leabharlann_corpus_overview.py`
- **THEN** the notebook SHALL render with 5 panels (per-subdir doc
  count, language pie, file-size violin, per-year trend, health
  banner)
- **AND** each panel SHALL show a live or synthetic-data fallback for
  the 6 leabharlann subdirs (`ollscoil_na_gaillimhe`, `gaeilge`,
  `mata`, `aigne`, `gemini_deep_research`, `zotero`)

#### Scenario: University institution matrix renders

- **GIVEN** the `notebooks/11_marimo_dashboards_v2/04_university_institution_matrix.py` notebook
- **WHEN** the user runs `marimo edit 04_university_institution_matrix.py`
- **THEN** the notebook SHALL render with 5 panels (institution-type
  distribution pie, institution × NFQ-max heatmap, CAO coverage bar,
  NUI constituent membership bar, health banner)
- **AND** it SHALL cover the 13 canonical Irish HEIs (UCD, UCG, UCC,
  UL, MU, TCD, DCU, RCSI, ATU, TUS, SETU, MTU, MIC) loaded from
  `dlt/british_isles/ireland/education/subjects/hei.json`

#### Scenario: QQI NFQ ladder renders

- **GIVEN** the `notebooks/11_marimo_dashboards_v2/05_qqi_nfq_ladder.py` notebook
- **WHEN** the user runs `marimo edit 05_qqi_nfq_ladder.py`
- **THEN** the notebook SHALL render with 5 panels (QQI × HEI ladder
  matrix heatmap, NFQ distribution, ladder density by NFQ, per-HEI
  ladder coverage, health banner)
- **AND** it SHALL cover the 8+ canonical QQI FET awards
  (`5M2787` Software Development, `5M5028` Computer Science,
  `5M2061` Laboratory Techniques, `5M18396` Nursing Studies,
  `5M3782` General Nursing, `5M2102` Business Studies,
  `5M0820` Social Care, `5M2094` Early Childhood Care & Education)

#### Scenario: Cross-archive edge dashboards render

- **GIVEN** any of `06_biep_leabharlann_edges.py`,
  `07_biep_official_media_edges.py`,
  `08_leabharlann_culture_heritage_edges.py`
- **WHEN** the user runs `marimo edit 06_biep_leabharlann_edges.py`
- **THEN** the notebook SHALL render with 5 panels (subject ×
  subdir / resolver / dataset matrix, edge-type distribution,
  top-15 strongest edges, language parity, health banner)
- **AND** it SHALL consume the canonical cognify cross-archive edge
  tables (`cianfhoghlaim.leabharlann.lc_join`,
  `cianfhoghlaim.official_media.subject_match`,
  `cianfhoghlaim.culture_heritage.leabharlann_match`)

#### Scenario: K-12 → university pipeline matrix renders

- **GIVEN** `09_k12_university_pipeline_matrix.py` or
  `10_year_level_coverage.py`
- **WHEN** the user runs `marimo edit 09_k12_university_pipeline_matrix.py`
- **THEN** the notebook SHALL render with 5 panels (stage × level
  heatmap, stage × next-pipeline-destination heatmap, per-stage
  depth bar, enrolment funnel, health banner)
- **AND** it SHALL cover the 5 educational stages (`aistear`,
  `primary`, `junior_cycle`, `senior_cycle`, `tertiary`) and the
  10-year window (2017-2026) plus the 3 LC levels (foundation,
  ordinary, higher)

#### Scenario: CLI discovers all 10 Phase-2 dashboards

- **GIVEN** the `GROUPS` tuple in
  `notebooks/cli.py` includes
  `"11_marimo_dashboards_v2"`
- **WHEN** the user runs `uv run cianfhoghlaim-marimo list
  11_marimo_dashboards_v2`
- **THEN** the CLI SHALL list all 10 new dashboards
  (`01_leabharlann_corpus_overview.py` through
  `10_year_level_coverage.py`)
- **AND** each notebook SHALL AST-parse cleanly (verified by
  `python -c "import ast; ast.parse(open(...).read())"`)

#### Scenario: Existing 15+10=25 notebooks still AST-parse

- **WHEN** the 10 existing dashboards at
  `notebooks/10_marimo_dashboards/` and the 15 BIEP / leaving_cert /
  semantic_search notebooks are AST-parsed after the new subdir is
  added
- **THEN** every existing notebook SHALL AST-parse cleanly
- **AND** the existing 10 dashboards SHALL be unchanged
  (no file modifications to `notebooks/10_marimo_dashboards/`)

## Cross-references

- [`openspec/specs/cianfhoghlaim-marimo-dashboards/spec.md`](../../specs/cianfhoghlaim-marimo-dashboards/spec.md)
  (the capability spec this delta modifies — the 10 prior requirements
  ship the 10 Phase-1 dashboards from commit `44cabc151`)
- [`openspec/changes/2026-07-14-cianfhoghlaim-marimo-dashboards-v1/`](../../2026-07-14-cianfhoghlaim-marimo-dashboards-v1/)
  (the Phase-1 change that shipped the 10 prior dashboards — this
  Phase-2 change extends them)
- [`.agents/skills/marimo/SKILL.md`](../../../.agents/skills/marimo/SKILL.md)
  (the canonical marimo skill — PEP 723 inline deps, `@app.cell(column=N)`)
- [`.agents/skills/motherduck/SKILL.md`](../../../.agents/skills/motherduck/SKILL.md)
  (the MotherDuck `md:oideachais` connection contract)
- [`.agents/skills/cianfhoghlaim-cocoindex-v1/SKILL.md`](../../../.agents/skills/cianfhoghlaim-cocoindex-v1/SKILL.md)
  (the BAAI/bge-m3 1024-d embedder contract for the embedding coverage dashboard)
- [`openspec/specs/cianfhoghlaim-leabharlann/spec.md`](../../specs/cianfhoghlaim-leabharlann/spec.md)
  (the leabharlann corpus pipeline that the leabharlann dashboards consume)
- [`openspec/specs/cianfhoghlaim-university-deep-extraction/spec.md`](../../specs/cianfhoghlaim-university-deep-extraction/spec.md)
  (the university / QQI extraction that the university dashboards consume)
- [`openspec/specs/cianfhoghlaim-cognify-knowledge-graph/spec.md`](../../specs/cianfhoghlaim-cognify-knowledge-graph/spec.md)
  (the cognify cross-archive pass that produces the edge tables consumed
  by the 06-08 cross-archive edge dashboards)
- [`openspec/specs/cianfhoghlaim-pipeline/spec.md`](../../specs/cianfhoghlaim-pipeline/spec.md)
  (the 5-stage Celtic education pipeline that the 09-10 dashboards
  visualise)