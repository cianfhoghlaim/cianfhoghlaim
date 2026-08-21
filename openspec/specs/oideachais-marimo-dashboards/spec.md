# oideachais-marimo-dashboards Specification

## Purpose
TBD - created by archiving change 2026-07-12-baml-cocoindex-tutorials-v1. Update Purpose after archive.
## Requirements
### Requirement: 5 new BAML+CocoIndex tutorial notebooks render in marimo edit + dual-mode CLI

The system SHALL provide 5 new marimo tutorial notebooks at
`notebooks/13_baml_cocoindex_tutorial/{01..05}_*.py`
covering the full BAML 0.223.0 + CocoIndex v1 + vision-model stack.
The 5 notebooks SHALL be CLI-discoverable via
`uv run cianfhoghlaim-marimo list 13_baml_cocoindex_tutorial` and
SHALL render in `marimo edit` mode without error. Each notebook SHALL
be dual-mode (marimo app + standalone CLI script via PEP 723 inline
dependency blocks).

The 5 notebooks are:
1. `01_baml_post_v4_syntax.py` — canonical post-v4 BAML 0.223.0 syntax
2. `02_qpack_8_subject_walkthrough.py` — the 8 `qpack_<subject>.baml` files
3. `03_education_pdf_vision_pipeline.py` — the vision+PDF pipeline with
   side-by-side `gemma-4-26B-A4B` vs `qwen3-vl-8b` comparison
4. `04_cocoindex_baml_integration.py` — the 3 real CocoIndex+BAML patterns
5. `05_post_v4_duplicate_audit_and_migration.py` — the 42-renames commit audit

#### Scenario: 5 tutorial files AST-parse + CLI-discoverable

- **GIVEN** the 5 follow-up tutorials exist at
  `notebooks/13_baml_cocoindex_tutorial/{01..05}_*.py`
- **WHEN** the user runs
  `python -c "import ast; ast.parse(open(f).read())"` for each
- **THEN** all 5 files parse without SyntaxError
- **AND** `uv run cianfhoghlaim-marimo list 13_baml_cocoindex_tutorial`
  returns exactly 5 entries

#### Scenario: Tutorial 3 has the side-by-side vision comparison cell

- **GIVEN** the `03_education_pdf_vision_pipeline.py` tutorial renders
- **WHEN** the user clicks the side-by-side cell
- **THEN** the cell calls `baml_sync.ExtractSyllabusDiagram` with
  `pointing_model="gemma-4-26B-A4B"` AND
  `pointing_model="qwen3-vl-8b"` on the same PDF
- **AND** the cell emits a marimo `mo.ui.table` showing both outputs
  side-by-side with the `match_confidence` Jaccard similarity

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

### Requirement: Phase 3 complete — per-subject interactive marimo study tools for the 6 BIEP v1 LC subjects

The system SHALL provide **6 per-subject interactive marimo study tools**
at `notebooks/12_subject_study_tools/<subject>.py` for
the 6 BIEP v1 LC subjects (Mathematics, Chemistry, Geography, Gaeilge,
English, Computer Science). These extend the 20 operator-facing
dashboards shipped by the Phase-1 + Phase-2 changes
(`2026-07-14-cianfhoghlaim-marimo-dashboards-v1` commit `44cabc151` and
`2026-07-15-cianfhoghlaim-marimo-dashboards-extension-v1` commit
`c536f7f79`) by adding a student-facing study tool surface.

Each Phase-3 study tool:

- Uses the PEP 723 inline dependency header (`# /// script` block)
  declaring `marimo>=0.13.0`, `duckdb>=1.0`, `pandas>=2.0`,
  `altair>=5.0`
- Connects to `md:oideachais` (MotherDuck + DuckLake) via
  `connect_biep_lakehouse()` with a graceful local-DuckDB fallback
- Falls back to a synthetic-data corpus when the lakehouse is
  unreachable (so notebooks render meaningfully offline)
- Invokes the per-subject `qpack_<subject>.baml` BAML functions
  (`Generate<Subj>FormativeItem`, `Generate<Subj>QuestPack`) via
  `from cianfhoghlaim.baml_client import b; b.<fn>(...)`, wrapped in
  try/except so the notebook renders offline
- Ships 5 study-tool cells per notebook (see below)

The 6 Phase-3 study tools are:

| # | File | Subject | Per-subject qpack BAML |
|:--|:--|:--|:--|
| 01 | `mathematics.py` | Mathematics | `qpack_mathematics.baml` |
| 02 | `chemistry.py` | Chemistry | `qpack_chemistry.baml` |
| 03 | `geography.py` | Geography | `qpack_geography.baml` |
| 04 | `gaeilge.py` | Gaeilge | `qpack_gaeilge.baml` |
| 05 | `english.py` | English | `qpack_english.baml` |
| 06 | `computer_science.py` | Computer Science | `qpack_computer_science.baml` |

The 5 study-tool cells in each Phase-3 notebook are:

1. **Flashcards** — renders 10 flashcards generated from the
   per-subject NCCA learning outcomes
   (`cianfhoghlaim.leaving_cert.<subject>_topics`) with bilingual EN+GA
   front/back (Gaeilge: GA-front + GA-back).
2. **Practice questions** — three per-subject difficulty levels
   (1=easy, 3=medium, 5=hard) via the same per-subject BAML function
   `Generate<Subj>FormativeItem`.
3. **Mock exam** — queries the per-subject past exam paper ingestion
   (`cianfhoghlaim.leaving_cert.<subject>_papers`) and renders the
   per-year × per-level question count + avg-difficulty table.
4. **Study plan** — per-subject lectionary + per-student progress,
   synthesised from the per-subject topic frequency table
   (`cianfhoghlaim.leaving_cert.<subject>_topics`) with a `mastery_pct`
   column and `next_revision_days` column.
5. **Per-subject BAML function** — invokes the per-subject
   `Generate<Subj>QuestPack` directly from
   `qpack_<subject>.baml`, plus `Generate<Subj>FormativeItem` for a
   single-formative-item invocation (deferred for the quest pack —
   the full quest-pack BAML call needs the full syllabus +
   past_papers + marking_schemes inputs, which the pipeline runner
   provides).

#### Scenario: Mathematics study tool renders

- **GIVEN** `notebooks/12_subject_study_tools/mathematics.py`
- **WHEN** the user runs `marimo edit mathematics.py` (or
  `uv run cianfhoghlaim-marimo edit 12_subject_study_tools/mathematics`)
- **THEN** the notebook SHALL render with 5 study-tool cells
  (flashcards, practice questions, mock exam, study plan, BAML call)
- **AND** the flashcards SHALL be generated from
  `cianfhoghlaim.leaving_cert.mathematics_topics` with 10 NCCA-coded
  cards (LC-MATHS-LO-*)
- **AND** the BAML cell SHALL invoke
  `qpack_mathematics.baml::GenerateMathFormativeItem` wrapped in
  try/except (offline-friendly)

#### Scenario: Gaeilge study tool renders with Gaeilge-front flashcards

- **GIVEN** `notebooks/12_subject_study_tools/gaeilge.py`
- **WHEN** the user runs `marimo edit gaeilge.py`
- **THEN** the flashcards SHALL use Gaeilge front-side prompts (e.g.
  "Mínigh agus cuir i bhfeidhm LC-GAEL-LO-1.1 (Litríocht)") and
  Gaeilge back-side answers
- **AND** the practice questions SHALL be in Gaeilge

#### Scenario: CLI discovers all 6 Phase-3 study tools

- **GIVEN** the `GROUPS` tuple in
  `notebooks/cli.py` includes
  `"12_subject_study_tools"`
- **WHEN** the user runs
  `uv run cianfhoghlaim-marimo list 12_subject_study_tools`
- **THEN** the CLI SHALL list all 6 new study tools
  (`mathematics.py`, `chemistry.py`, `geography.py`, `gaeilge.py`,
  `english.py`, `computer_science.py`)
- **AND** each notebook SHALL AST-parse cleanly (verified by
  `python -c "import ast; ast.parse(open(...).read())"`)

#### Scenario: Existing 30+10+10=50 notebooks still AST-parse

- **WHEN** the 30 existing dashboards at
  `notebooks/10_marimo_dashboards/` (Phase 1) and
  `notebooks/11_marimo_dashboards_v2/` (Phase 2) plus the 20+
  BIEP / leaving_cert / semantic_search notebooks are AST-parsed
  after the new subdir is added
- **THEN** every existing notebook SHALL AST-parse cleanly
  (the 8 pre-existing parse failures in
  `notebooks/04_biep_motherduck/0[1-9]_*.py` are owned by the BIEP
  MotherDuck notebooks workstream and are out of scope for this
  change)
- **AND** the 10+10 existing dashboards SHALL be unchanged
  (no file modifications to `notebooks/10_marimo_dashboards/` or
  `notebooks/11_marimo_dashboards_v2/`)

### Requirement: Canonical `ocr/` Python package

The system SHALL provide the canonical v4 OCR/VLM model
registry Python package at `ocr/` with the
following layout, per the v4 platform spec
(`openspec/specs/meaisinfhoghlaim-platform/spec.md` line 685)
and commit `0fceb8654`:

```text
ocr/
├── __init__.py           # re-exports the canonical symbols
└── models/
    ├── __init__.py       # re-exports + back-compat OCR_MODELS / VLM_MODELS aliases
    └── registry.py       # the 929-line canonical implementation
```

The canonical implementation SHALL export at minimum
`VISION_MODELS` (22 vision models) and `CLASSICAL_OCR`
(6 OCR backends) when
`from cianfhoghlaim.ocr.models.registry import VISION_MODELS, CLASSICAL_OCR`
is executed.

#### Scenario: Canonical import resolves

- **GIVEN** the `ocr/__init__.py`,
  `ocr/models/__init__.py`, and
  `ocr/models/registry.py` files exist on disk
  with content matching `HEAD` (commit `0fceb8654`)
- **WHEN** a Python process executes
  `from cianfhoghlaim.ocr.models.registry import VISION_MODELS, CLASSICAL_OCR`
- **THEN** the import SHALL succeed without
  `ModuleNotFoundError`
- **AND** `len(VISION_MODELS) >= 20` (the v4 spec requires
  ≥ 20 vision models; the current HEAD ships 22)
- **AND** `len(CLASSICAL_OCR) >= 4` (the v4 spec requires
  ≥ 4 classical OCR backends; the current HEAD ships 6)

#### Scenario: All 19 downstream consumers AST-parse

- **GIVEN** the 19 Python files under `cianfhoghlaim/` that
  reference `cianfhoghlaim.ocr.*`
  (cocoindex/, observability/, orchestration/, tests/_meaisinfhoghlaim/,
  and the meaisinfhoghlaim/ sub-package)
- **WHEN** each file is AST-parsed (`python -c "import ast;
  ast.parse(open('<file>').read())"`)
- **THEN** every file SHALL parse without syntax errors
- **AND** the 8 files with hard imports of
  `cianfhoghlaim.ocr.models.registry` SHALL execute their
  `import` statements without `ModuleNotFoundError`

#### Scenario: Back-compat shims re-export the canonical symbols

- **GIVEN** the parallel-agent back-compat shims at
  `meaisinfhoghlaim/ocr/__init__.py` and
  `meaisinfhoghlaim/models/{__init__,registry}.py`
  (each emitting a `DeprecationWarning`)
- **WHEN** a Python process executes
  `from cianfhoghlaim.meaisinfhoghlaim.models import VISION_MODELS`
- **THEN** the import SHALL emit the expected
  `DeprecationWarning` about the v4 canonical home
- **AND** the import SHALL return the same `VISION_MODELS` dict
  as `from cianfhoghlaim.ocr.models.registry import VISION_MODELS`
  (identity-equality, not just equality of contents)

#### Scenario: Test conformance — `test_ocr_vlm_registry.py`

- **GIVEN** the test file
  `tests/_meaisinfhoghlaim/test_ocr_vlm_registry.py`
- **WHEN** `pytest tests/_meaisinfhoghlaim/test_ocr_vlm_registry.py`
  is run
- **THEN** the `import` statements SHALL resolve
- **AND** the conformance assertions on `VISION_MODELS` (model
  count, required backends, Unsloth-first fallback chain) SHALL
  pass without `ModuleNotFoundError`

### Requirement: On-disk marimo notebook count is the canonical source of truth

The system SHALL consider the on-disk count of `.py` files at
`notebooks/**/*.py` (verified via
`ls notebooks/**/*.py | wc -l`) as the canonical
source of truth for all marimo notebook count claims in any
openspec change proposal or spec delta.

The on-disk count at this consolidation time (2026-07-17) is:

- **134 clean marimo notebooks** (excluding `__init__.py`,
  `__pycache__/*`, and `legacy/*`)
- **160 total `.py` files** (including `__init__.py` and
  `__pycache__/*` — the canonical raw count)

The per-group breakdown (clean count):

| Group | Count | Description |
|:--|--:|:--|
| `01_dev_env/` | 6 | dev-env demo tools (ccc search, drift detect, etc.) |
| `02_vision_models/` | 6 | vision model benchmarks |
| `03_leaving_cert/` | 23 | LC analysis + BIEP v1 per-subject notebooks |
| `04_biep_motherduck/` | 11 | BIEP motherduck + leabharlann full-stack demo |
| `05_lakehouse_inspect/` | 4 | DuckLake + lakehouse inspector |
| `06_observability/` | 3 | BAML drift + Irish extraction quality + Cognee KG |
| `07_educational_stages/` | 7 | Aistear → Tertiary + cross-domain + analysis_plan |
| `08_sources/` | 1 | sources loader |
| `09_official_media/` | 7 | fediverse + cross-archive + moderation |
| `10_cognify/` | 1 | cognify KG visualiser |
| `10_marimo_dashboards/` | 10 | v1 dashboards (Phase 1, shipped 2026-07-14) |
| `10_mmo/` | 2 | MMO mission control |
| `11_marimo_dashboards_v2/` | 10 | v2 dashboards (Phase 2, shipped 2026-07-15) |
| `11_speedrun/` | 9 | Tuatha speedrun tutorials |
| `12_ireland_law/` | 6 | Ireland law notebooks (PIAB + WRC + courts + …) |
| `12_semantic_search/` | 1 | cross-corpus LanceDB HNSW search |
| `12_subject_study_tools/` | 6 | v3 study tools (Phase 3, shipped 2026-07-16) |
| `13_baml_cocoindex_tutorial/` | 10 | BAML+CocoIndex tutorials (5 EN + 5 GA siblings) |
| `leaving_cert/` (root) | 7 | per-subject BIEP notebooks + bilingual comparison |
| `**/*.py` (root-level) | 2 | `01_overview_setup.py` + `ie_law_explorer.py` + `nb_utils.py` |
| `__init__.py` + `cli.py` | 2 | infrastructure (not marimo notebooks) |
| **Total (clean)** | **134** | marimo notebooks |

The 4 stale claims in the 4 source-change subdirs are historical
artifacts and SHALL NOT be retroactively updated (they live in
non-archived changes that have already shipped):

| Source change | Stale claim | Where |
|:--|:--|:--|
| `2026-07-14-cianfhoghlaim-marimo-dashboards-v1` | "11 BIEP notebooks" (refers to `04_biep_motherduck/` count, which IS accurate; the 10 v1 dashboards claim is also accurate) | spec.md Scenario 1 + Scenario 3 |
| `2026-07-15-cianfhoghlaim-marimo-dashboards-extension-v1` | "Existing 15+10=25 notebooks still AST-parse" | spec.md line 119-127 |
| `2026-07-16-biiep-v1-lc-per-subject-marimo-study-tools-v1` | "Existing 30+10+10=50 notebooks still AST-parse" | spec.md line 104-118 |
| `2026-07-12-baml-cocoindex-tutorials-v1` | "5 new BAML tutorials" (the 5 EN tutorials; the 5 GA siblings came from `2026-07-13-baml-cocoindex-tutorials-ga-v1`) | spec.md line 7-40 |

#### Scenario: `ls` returns the canonical on-disk count

- **WHEN** a developer runs
      `ls notebooks/**/*.py | wc -l`
- **THEN** the output SHALL be the canonical count (134 clean; 160
      raw)
- **AND** the on-disk breakdown per the table above SHALL be
      reproducible via `find cianfhoghlaim/notebooks -maxdepth 2 -type f -name "*.py" -not -path "*/__pycache__/*" -not -name "__init__.py" | wc -l`

#### Scenario: All existing marimo notebooks AST-parse

- **WHEN** the developer runs `python -c "import ast; ast.parse(open(f).read())"`
      for each of the 134 clean marimo notebooks
- **THEN** all 134 files SHALL parse without SyntaxError
- **AND** the breakdown per the table above SHALL hold

#### Scenario: Stale claim documentation

- **GIVEN** a developer reads the 4 source-change spec deltas at
      `openspec/changes/2026-07-{12,14,15,16}-{...}/specs/cianfhoghlaim-marimo-dashboards/spec.md`
- **WHEN** they cross-reference the claims against the canonical
      on-disk count
- **THEN** the cross-reference table above SHALL be the source of
      truth (the source-change spec deltas are historical artifacts)

### Requirement: 4 stage Marimo dashboards (one per stage)

The system SHALL provide 4 stage Marimo dashboards that mirror the
BAML + CocoIndex + ADK stage planes:

- `notebooks/19_ireland_pipeline_dashboard.py` (Leaving Cycle, existing)
- `notebooks/19_junior_cycle_pipeline_dashboard.py` (Junior Cycle, new)
- `notebooks/20_england_alevel_pipeline_dashboard.py` (A-Level, new)
- `notebooks/20_england_gcse_pipeline_dashboard.py` (GCSE, new)

Each dashboard uses the canonical
`build_biep_v3_dashboard(jurisdiction=..., milestone=...)` helper.

#### Scenario: Each stage dashboard exists and uses the canonical helper

- **WHEN** the operator runs `grep -l "build_biep_v3_dashboard" notebooks/*.py`
- **THEN** the output includes all 4 stage dashboards + the 7 tier dashboards

### Requirement: biiep_v3_dashboard_v2 collapse

The system SHALL collapse the 7 tier dashboards into 1 canonical helper
+ 7 thin wrappers (per Phase 2).

The helper is at `notebooks/_shared/biiep_v3_dashboard_v2.py` and
exposes `build_biep_v3_dashboard(jurisdiction=..., milestone=...)`.

#### Scenario: All 7 tier dashboards use the canonical helper

- **WHEN** `mise run lint:marimo-tier-dashboard-collapse` runs
- **THEN** all 7 tier dashboards MUST use the canonical
  `build_biep_v3_dashboard` helper (no hand-written 8-cell operator
  consoles)

### Requirement: PEP 723 template collapse

The system SHALL collapse the 201 PEP 723 inline metadata blocks
into 1 canonical template + 201 thin imports.

The template is at `notebooks/_shared/_pep723_template.py` and
includes the canonical 9 dependencies.

#### Scenario: All 201 notebooks use the canonical template

- **WHEN** `mise run lint:marimo-pep723-template` runs
- **THEN** all 201 notebooks MUST import from
  `notebooks._shared._pep723_template` (no hand-written PEP 723
  blocks)

### Requirement: Marimo `mo.ui.chat` streaming adoption

The system SHALL adopt `mo.ui.chat(..., streaming=True)` for all 6
BIEP v3 jurisdiction dashboards + the 4 stage dashboards (10 total).

The streaming chat uses the BAML `b.Extract*` functions via
`marimo_baml.py` (per the 2026-08-18-mega-3-fast-follow-v1 change FF.2).

#### Scenario: Every dashboard exposes a streaming chat

- **WHEN** the operator opens any of the 10 BIEP v3 dashboards
- **THEN** the dashboard exposes a `mo.ui.chat(..., streaming=True)`
  cell that streams responses from the BAML extraction functions

### Requirement: Marimo `mo.ui.anywidget` for the RAGAS gauge

The system SHALL use `mo.ui.anywidget(RAGASGaugeWidget(...))` for the
RAGAS gauge widget (per the canonical `notebooks/_shared/ragas_gauge.py`
+ the marimo patterns tour).

The widget is rendered at the top-right corner of every dashboard and
shows the RAGAS ensemble score for the current stage.

#### Scenario: Every dashboard renders a RAGAS gauge

- **WHEN** `grep -l "RAGASGaugeWidget" notebooks/*.py` runs
- **THEN** the output includes all 10 dashboards + the canonical
  `00_marimo_patterns_tour.py`

### Requirement: Marimo `mo.ui.dictionary` for the schema introspection

The system SHALL use `mo.ui.dictionary(...)` to render the schema
introspection results (per `notebooks/_shared/schema.py`) in the
BIEP v3 dashboards.

#### Scenario: The schema dictionary is rendered

- **GIVEN** a BIEP v3 dashboard
- **WHEN** the operator clicks the "Schema" tab
- **THEN** the dashboard renders a `mo.ui.dictionary` with the
  schema introspection results (table names, column names, types)

