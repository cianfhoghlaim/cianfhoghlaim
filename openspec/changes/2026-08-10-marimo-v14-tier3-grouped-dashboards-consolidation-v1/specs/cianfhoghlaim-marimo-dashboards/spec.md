## ADDED Requirements

### Requirement: Per-domain grouped dashboards consolidate the per-area sub-notebooks

The system SHALL provide one grouped marimo dashboard per domain (the
**Tier 3 consolidation pattern**), each surfacing the per-area
sub-notebooks as tabs. The grouped dashboards SHALL use the same
canonical 8-cell operator console + `mo.ui.tabs` + LLM tab + dual-mode
CLI pattern as the BIEP v3 jurisdiction dashboards.

The 6 grouped dashboards are:

| Grouped dashboard | Tab count | Consolidates | Domain |
|:--|--:|:--|:--|
| `notebooks/meaisin_ops_console.py` | 6 | 5 meaisin ops dashboards | Agent fleet ops |
| `notebooks/celtic_languages.py` | 7 | 7 Celtic languages dashboards | Celtic language pipeline |
| `notebooks/corpus_overview.py` | 4 | 8 corpus overview dashboards | BIEP + Leabharlann corpora |
| `notebooks/speedrun_mmo.py` | 5 | 8 speedrun MMO dashboards | Túatha educational MMO |
| `notebooks/academic_history.py` | 6 | 8 academic history dashboards | M.Sc. AI / Maths corpus |
| `notebooks/irish_law.py` | 6 | 6 Irish law dashboards | Irish legal corpus |

The canonical implementation SHALL live in the per-domain area_shim
module under `notebooks/_shared/area_shims/<domain>.py`.

#### Scenario: operator opens the meaisin_ops_console and picks the Ireland tab

- **GIVEN** the operator runs
  `marimo edit notebooks/meaisin_ops_console.py`
- **WHEN** the operator clicks the "Ireland" tab
- **THEN** the tab SHALL render the content of the legacy
  `60_meaisin_ireland_ops.py` notebook (per-cohort extraction
  completion % + lifecycle state + bilingual coverage + missing-
  subject audit)
- **AND** the underlying `@app.cell` SHALL call
  `notebooks/_shared/area_shims/meaisin.py:ireland_cohort_overview()`

#### Scenario: the legacy sub-notebooks are moved to `notebooks/legacy/v7_consolidation/`

- **WHEN** the operator runs `ls notebooks/legacy/v7_consolidation/`
- **THEN** the directory SHALL contain the 6 subdirectories
  (`meaisin/`, `celtic/`, `corpus/`, `speedrun/`, `academic/`,
  `irish_law/`)
- **AND** each subdirectory SHALL contain the legacy sub-notebooks
  moved via `git mv` (preserving git history)
- **AND** each subdirectory SHALL have a `DEPRECATED.md` redirect
  note pointing to the new grouped dashboard

#### Scenario: 1 LLM tab per grouped dashboard

- **WHEN** the operator opens any of the 6 grouped dashboards
- **THEN** the dashboard SHALL have an "Ask" tab (P3 — LLM chat via
  `mo.ui.chat(mo.ai.llm.openai(base_url=LITELLM_BASE_URL, ...))`)
  with 4 built-in prompts tailored to the domain (e.g. for the
  Celtic dashboard: "Translate the Gaois entry to English",
  "Find UD treebank sentences matching X", "List heritage sites in
  county Y", "Suggest a Celtic curriculum reading list for topic Z")

#### Scenario: dual-mode CLI per grouped dashboard

- **WHEN** the operator runs
  `python notebooks/meaisin_ops_console.py --tab ireland --output json`
- **THEN** the notebook SHALL exit 0 with a JSON payload describing
  the Ireland cohort state
- **AND** the operator SHALL be able to pipe the JSON into
  `mise run agents:audit` for CI consumption