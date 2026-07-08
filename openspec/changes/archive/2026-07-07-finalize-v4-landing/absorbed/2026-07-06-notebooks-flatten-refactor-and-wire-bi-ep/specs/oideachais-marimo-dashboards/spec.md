# Spec Delta: oideachais-marimo-dashboards

> Parent change: [../proposal.md](../../proposal.md)

## MODIFIED Requirements

### Requirement: 5-stage education dashboards

The system SHALL provide Marimo notebooks for each of the 5 educational
stages (Aistear, Primary, Junior Cycle, Senior Cycle, Tertiary), located
under `notebooks/07_educational_stages/` as
`01_aistear.py`, `02_primary.py`, `03_junior_cycle.py`,
`04_senior_cycle.py`, `05_tertiary.py`. The cross-domain dashboard
(formerly `dashboards/cross_domain.py`) is `06_cross_domain.py`. The
analysis-plan viewer (new in 2026-07-06) is `07_analysis_plan_viewer.py`.

#### Scenario: Aistear dashboard renders

- **GIVEN** the `notebooks/07_educational_stages/01_aistear.py` notebook
- **WHEN** the user runs `marimo edit 01_aistear.py` from any cwd
- **THEN** the notebook SHALL render with the Aistear theme data from
  the BIEP DuckLake lakehouse at `md:oideachais`
- **AND** `python 01_aistear.py --cycle aistear` SHALL also succeed
  (dual-mode: marimo + CLI)

#### Scenario: Analysis-plan viewer surfaces the 5 plan artifacts

- **GIVEN** the `notebooks/07_educational_stages/07_analysis_plan_viewer.py`
  notebook and the 5 `notebooks/analysis_plan/*.md` artifacts
- **WHEN** the user opens the notebook
- **THEN** the notebook SHALL display 5 tabs (Aistear / Primary /
  Junior Cycle / Senior Cycle / Tertiary) each rendering the
  corresponding `analysis_plan/<cycle>.md` content
- **AND** `python 07_analysis_plan_viewer.py --cycle senior_cycle`
  SHALL open only the Senior Cycle tab

### Requirement: Leabharlann full-stack demo

The system SHALL provide a Marimo notebook that visualises the
end-to-end leabharlann pipeline (1 UoG + 1 Zotero sample PDF →
BAML extraction → CocoIndex update → LanceDB insert → Cognee add →
DuckDB metadata write). The notebook lives at
`notebooks/04_biep_motherduck/08_leabharlann_full_stack_demo.py`.

#### Scenario: Full-stack demo renders

- **GIVEN** the `notebooks/04_biep_motherduck/08_leabharlann_full_stack_demo.py`
  notebook
- **WHEN** the user runs `marimo edit 08_leabharlann_full_stack_demo.py`
  from any cwd
- **THEN** the notebook SHALL render with the 5-step pipeline visualisation
  + the DuckDB result table for the last demo run
- **AND** `python 08_leabharlann_full_stack_demo.py` SHALL also succeed
  in CLI mode

### Requirement: Cross-domain + lakehouse + ducklake dashboards

The system SHALL provide cross-domain, lakehouse, and ducklake
explorer notebooks under
`notebooks/05_lakehouse_inspect/`. The four notebooks are:
`01_ducklake_explorer.py`, `02_lakehouse_inspector.py`,
`03_dlt_pipeline_overview.py`, `04_cocoindex_embedding_coverage.py`.

#### Scenario: DuckLake explorer renders

- **GIVEN** the `notebooks/05_lakehouse_inspect/01_ducklake_explorer.py`
  notebook
- **WHEN** the user runs `marimo edit 01_ducklake_explorer.py` from any cwd
- **THEN** the notebook SHALL render with the table list from DuckLake
  and an interactive SQL query interface

#### Scenario: Lakehouse inspector renders

- **GIVEN** the `notebooks/05_lakehouse_inspect/02_lakehouse_inspector.py`
  notebook
- **WHEN** the user runs `marimo edit 02_lakehouse_inspector.py`
- **THEN** the notebook SHALL display 6 tabs (Service health, Garage
  buckets, Iceberg namespaces, Lance tables, DuckLake console,
  Cross-flow search) against the
  `infrastructure/stacks/lakehouse/` stack

### Requirement: BIEP subject full-pipeline dashboard (parameterised)

The system SHALL provide a single Marimo notebook at
`notebooks/04_biep_motherduck/07_subject_full_pipeline.py` that
executes the canonical 6-step BIEP pipeline (DLT → BAML
`ExtractCurriculumSyllabus` → BAML `ExtractExamPaperLayout` →
BAML `ExtractMarkingSchemeGuideline` → CocoIndex v1 embedding →
Cognee cognify) for any of the 6 Leaving Cert subjects
(`mathematics`, `applied_mathematics`, `english`, `gaeilge`,
`biology`, `chemistry`). The notebook SHALL replace the 8
previously-duplicated `<subject>_full_pipeline.py` stubs and
SHALL accept the same CLI flags: `--subject`, `--level`
(`higher|ordinary|foundation`), `--language` (`en|ga`),
`--year` (2017–2026).

#### Scenario: Default subjects render the full pipeline

- **GIVEN** the `07_subject_full_pipeline.py` notebook with the
  default subjects `["chemistry", "biology"]`
- **WHEN** the user runs `marimo edit 07_subject_full_pipeline.py`
- **THEN** the notebook SHALL render the 6-step pipeline output for
  both subjects side-by-side, with the live lakehouse row counts

#### Scenario: CLI invocation with custom flags

- **GIVEN** the `07_subject_full_pipeline.py` notebook
- **WHEN** the user runs
  `python 07_subject_full_pipeline.py --subject mathematics
  --level higher --language en --year 2024`
- **THEN** the CLI SHALL execute the same 6-step pipeline for
  `mathematics/higher/en/2024` against the live BIEP lakehouse
  and print a summary table to stdout

#### Scenario: Subject not in the 6-LC priority list

- **WHEN** the user passes `--subject french` (not in the BIEP v1
  subject list)
- **THEN** the CLI SHALL exit with code 2 and print
  `error: subject 'french' not in BIEP v1 priority list:
   [mathematics, applied_mathematics, english, gaeilge, biology, chemistry]`

### Requirement: Dev-env demo notebooks (6 tools)

The system SHALL provide 6 Marimo notebooks under
`notebooks/01_dev_env/` (one per
`cianfhoghlaim.agents.adk.tools.dev_env` tool): `01_ccc_search.py`,
`02_drift_detect.py`, `03_firecrawl_refactor_discover.py`,
`04_hf_best_model.py`, `05_openspec_list.py`, `06_mise_lint_skills.py`.
Each notebook SHALL load the `dev_env.py` tool module via an
**absolute path** computed from `__file__` (so the notebook runs
identically from any cwd), and SHALL expose CLI flags for the
underlying tool's parameters (`--query`, `--packages`, `--task`,
etc.) so the notebook can be invoked as a CLI script as well as
opened in `marimo edit`.

#### Scenario: Dev-env notebook loads from any cwd

- **GIVEN** the `notebooks/01_dev_env/01_ccc_search.py` notebook
- **WHEN** the user runs `cd /tmp && uv run <repo>/notebooks/01_dev_env/01_ccc_search.py
  --query "Dagster asset partition"`
- **THEN** the CLI SHALL compute the absolute path to
  `<repo>/cianfhoghlaim/agents/adk/tools/dev_env.py` (via
  `Path(__file__).resolve().parents[2] / "agents" / "adk" / "tools" / "dev_env.py"`)
- **AND** SHALL load the module without `FileNotFoundError`
- **AND** SHALL print the top 5 ccc search results to stdout

#### Scenario: Dev-env notebook in marimo edit mode

- **GIVEN** the `notebooks/01_dev_env/02_drift_detect.py` notebook
- **WHEN** the user runs `marimo edit 02_drift_detect.py` from any cwd
- **THEN** the notebook SHALL render with the same absolute-path
  import, and SHALL display the drift report as a marimo table

### Requirement: BIEP PDF processing + vision-model dashboards

The system SHALL provide the 6 BIEP PDF processing notebooks under
`notebooks/03_leaving_cert/12..16_*.py` (was `meaisinfhoghlaim/03_pdf_processing.py`
+ `dashboards/pdf_processing/*.py`) and the 6 vision-model notebooks
under `notebooks/02_vision_models/` (was `dashboards/leaving_cert/11..15_*.py`
+ new `01_vlm_dispatch.py`).

#### Scenario: PDF processing pipeline renders

- **GIVEN** the `notebooks/03_leaving_cert/12_pdf_processing.py` notebook
- **WHEN** the user runs `marimo edit 12_pdf_processing.py`
- **THEN** the notebook SHALL render the 6-stage pipeline view
  (OCR → Diagram detection → BAML extraction → Topic validation →
  Semantic chunking → Lakehouse + Cognee + Graphiti) for any
  (subject, year, paper) tuple from the BIEP MotherDuck + DuckLake
  lakehouse

#### Scenario: Vision model dispatch renders

- **GIVEN** the `notebooks/02_vision_models/01_vlm_dispatch.py` notebook
  (new in this change)
- **WHEN** the user runs `marimo edit 01_vlm_dispatch.py`
- **THEN** the notebook SHALL walk the
  `leaving_certificate/<subject>/{en,ga}/` corpus and display the
  VLM dispatch table (which of the 5 OCR backends is chosen per PDF
  + the reason). Default subjects: `[chemistry, mathematics]`.

#### Scenario: PDF extraction quality renders

- **GIVEN** the `notebooks/03_leaving_cert/13_pdf_extraction_quality.py` notebook
- **WHEN** the user runs `marimo edit 13_pdf_extraction_quality.py`
- **THEN** the notebook SHALL display the per-(subject, model, page)
  WER / CER / fada-preservation matrix

### Requirement: Dual-mode notebook (marimo + CLI)

Every refactored notebook under `notebooks/{01..10}_*/` SHALL
support two execution modes:

1. **`marimo edit <nb>.py`** — the reactive UI, opened in the marimo
   editor (cwd-independent).
2. **`python <nb>.py` or `uv run <nb>.py`** — the CLI mode, which
   parses the BIEP canonical flags (`--subject`, `--level`,
   `--language`, `--year`) via `nb_utils.cl_argument_parser()` and
   prints the same data to stdout.

The CLI mode SHALL NOT require `marimo edit` to be running.
The CLI mode SHALL use the same `nb_utils.connect_biep_lakehouse()`
helper for the DuckDB/MotherDuck attach (avoiding the duplicated
`try: connect("md:oideachais") except: connect(":memory:")` pattern
that appears in 12+ notebooks today).

#### Scenario: BIEP dashboard runs as a CLI script

- **GIVEN** the `notebooks/04_biep_motherduck/01_curriculum_educator.py` notebook
- **WHEN** the user runs
  `python 01_curriculum_educator.py --subject chemistry --level higher --year 2025`
- **THEN** the CLI SHALL attach to `md:oideachais` (MotherDuck)
- **AND** SHALL print the cycle-by-cycle + subject-by-subject row
  counts to stdout
- **AND** SHALL exit 0

#### Scenario: BIEP dashboard runs in marimo edit

- **GIVEN** the `notebooks/04_biep_motherduck/01_curriculum_educator.py` notebook
- **WHEN** the user runs `marimo edit 01_curriculum_educator.py`
- **THEN** the notebook SHALL render the same query results in the
  marimo UI (table + altair chart), driven by the user-selected
  dropdowns

## REMOVED Requirements

### Requirement: 8 subject_full_pipeline stub files

**Reason**: The 8 duplicated `<subject>_full_pipeline.py` files
(`applied_mathematics_full_pipeline.py`, `biology_full_pipeline.py`,
`business_full_pipeline.py`, `chemistry_full_pipeline.py`,
`computer_science_full_pipeline.py`, `french_full_pipeline.py`,
`physics_full_pipeline.py`, plus the `leabharlann_full_pipeline.py`
variant — all 108 LOC, differing only in the subject name)
constitute copy-paste duplication that has drifted (the v4
`baml.ExtractCurriculumSyllabus` rename was never applied to all 8).

**Migration**: All 8 stubs are deleted by this change and replaced
by a single parameterised `notebooks/04_biep_motherduck/07_subject_full_pipeline.py`
that loops over the 6 BIEP subjects (see `Requirement: BIEP subject
full-pipeline dashboard (parameterised)` above).

## Cross-references

- [`openspec/specs/oideachais-marimo-dashboards/spec.md`](../../specs/oideachais-marimo-dashboards/spec.md)
  (the capability spec this delta modifies)
- [`.agents/skills/marimo/SKILL.md`](../../../.agents/skills/marimo/SKILL.md)
  (the canonical marimo skill — covers `marimo edit`, `marimo run`,
  PEP 723 inline deps, and the `@app.cell(column=N)` multi-column pattern)
- [`.agents/skills/motherduck/SKILL.md`](../../../.agents/skills/motherduck/SKILL.md)
  (the MotherDuck `md:oideachais` connection contract)
- [`.agents/skills/build-notebook/SKILL.md`](../../../.agents/skills/build-notebook/SKILL.md)
  (the analysis_plan → marimo notebook assembly workflow)
- [`openspec/changes/2026-07-06-british-isles-education-pipeline-v1/`](../../2026-07-06-british-isles-education-pipeline-v1/)
  (the BIEP v1 contract — the 6 subjects + the lakehouse schema
  that the new notebooks consume)
