## ADDED Requirements

### Requirement: 8-cell BIEP v3 surface consolidates into `mo.ui.tabs`

The system SHALL collapse the canonical 8-cell BIEP v3 operator console
(`_intro / _ibis_conn / _commands / _cohort_matrix / _drill_down /
_schedule / _asset_check_status / _dive_link`) into a single
`mo.ui.tabs` widget with 7 tabs (`Overview / Cohorts / Drill /
Schedule / Asset Checks / Dives / Activity`) on every BIEP v3
jurisdiction dashboard (notebooks 19, 20, 21, 22, 26, 27).

The canonical implementation SHALL live at
`notebooks/_shared/area_shims/biiep_v3_dashboard.py:
build_biep_v3_dashboard(jurisdiction, milestone, deferred=False)`.

#### Scenario: operator opens the Ireland dashboard and picks the Cohorts tab

- **GIVEN** the operator runs
  `marimo edit notebooks/19_ireland_pipeline_dashboard.py`
- **WHEN** the operator clicks the "Cohorts" tab
- **THEN** the tab SHALL render the 100-row Ireland cohort matrix
  (12 LC + 88 JC)
- **AND** the previous Overview tab SHALL not re-render
- **AND** the underlying `@app.cell _cohort_matrix(conn, mo)` SHALL
  re-run ONLY when the jurisdiction dropdown value changes

#### Scenario: the operator picks the Dives tab

- **WHEN** the operator clicks the "Dives" tab
- **THEN** the tab SHALL render the canonical MotherDuck Dives for
  the jurisdiction (`ireland_lc_syllabus_topics`,
  `ireland_jc_curriculum_topics`, `ireland_lc_daily_sync_flight`,
  `ireland_jc_daily_sync_flight`)
- **AND** the canonical DAG paths SHALL be referenced
  (`motherduck/dives/ireland_lc_syllabus_topics.py`)

### Requirement: LLM-assisted analysis tab via `mo.ui.chat` + `mo.ai.llm`

The system SHALL provide an LLM-assisted analysis tab on every BIEP v3
jurisdiction dashboard, wired via
`mo.ui.chat(mo.ai.llm.openai(base_url=LITELLM_BASE_URL,
model=model_for("text_llm", "default"), system_message=...), prompts=[...])`.

The `LITELLM_BASE_URL` constant SHALL be
`http://litellm.cianfhoghlaim.ie/v1` (the canonical LiteLLM OpenAI-
compatible base URL). The litellm proxy dispatches to either local
`llama-swap` models OR the `minimax-m3` token plan API per the
`centralized-model-registry` capability.

The canonical implementation SHALL live at
`notebooks/_shared/marimo_patterns.py:llm_chat_with_prompts()`.

#### Scenario: operator asks the LLM to summarise the marking scheme for Ireland LC Mathematics Higher EN 2024

- **GIVEN** the operator has selected Ireland LC Mathematics Higher EN
  2024 in the drill-down
- **WHEN** the operator clicks the "Ask BAML" tab and types
  "Summarise the marking scheme"
- **THEN** the notebook SHALL call
  `mo.ai.llm.openai(base_url="http://litellm.cianfhoghlaim.ie/v1",
  model="minimax-m3", system_message="You are an expert SEC
  Mathematics marker. Extract the 5 most-tested rubric keywords from
  the user's marking scheme snippet. Return as a numbered list.")`
  with the `BIEPV3Extract` extraction as context
- **AND** the LLM SHALL return a numbered list of 5 keywords
- **AND** the operator SHALL see the response in the chat widget

#### Scenario: litellm proxy is unreachable

- **WHEN** the litellm proxy at `http://litellm.cianfhoghlaim.ie/v1`
  is down
- **THEN** `mo.ui.chat` SHALL display a friendly error message
  ("LLM unavailable: litellm proxy is down — see
  https://litellm.cianfhoghlaim.ie")
- **AND** the operator SHALL be able to re-enable the chat when the
  proxy recovers (per marimo's reactive graph)

### Requirement: Dual-mode (marimo + CLI) unification per https://docs.marimo.io/guides/scripts/

The system SHALL ship every BIEP v3 jurisdiction dashboard with a
dual-mode (marimo + CLI) entrypoint, following the canonical pattern
documented at https://docs.marimo.io/guides/scripts/ and implemented
in `notebooks/10_biep_pipeline_lakehouse_07_subject_full_pipeline.py`.

The canonical CLI argparse SHALL be
`notebooks/_shared/marimo_patterns.py:cli_argparser_biep(notebook_name)`
with the canonical flags (`--milestone`, `--asset-check`,
`--cohort-kind`, `--jurisdiction`, `--output`).

#### Scenario: operator runs the Ireland dashboard as a CLI script to check the M1 asset checks

- **GIVEN** the operator has the 6 BIEP v3 jurisdiction dashboards
- **WHEN** the operator runs
  `python notebooks/19_ireland_pipeline_dashboard.py --milestone m1
  --asset-check documents_ingested`
- **THEN** the notebook SHALL exit 0 with a JSON payload
  `{"notebook": "19_ireland_pipeline_dashboard", "milestone": "m1",
  "asset_check": "documents_ingested", "status": "passed",
  "exit_code": 0}`
- **AND** the operator SHALL be able to pipe the JSON into
  `mise run biep:v3:gate --milestone=m1` for CI consumption

#### Scenario: operator runs the Ireland dashboard in marimo mode

- **WHEN** the operator runs
  `marimo edit notebooks/19_ireland_pipeline_dashboard.py`
- **THEN** the notebook SHALL open in the marimo editor with the
  tabbed 8-cell operator console visible
- **AND** no CLI mode SHALL be triggered (no `dagster asset check`
  subprocess is invoked)

#### Scenario: marimo scripts guide's `if __name__ == "__main__":` pattern is followed

- **WHEN** the operator reads
  `notebooks/19_ireland_pipeline_dashboard.py`
- **THEN** the bottom of the file SHALL contain the canonical pattern:
  ```python
  if __name__ == "__main__":
      import sys
      if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
          sys.exit(_cli_main())
      app.run()
  ```
- **AND** the file SHALL have a `_cli_main(argv) -> int` function that
  parses the CLI args + invokes the live `dagster asset check` via
  `subprocess.run([...], capture_output=True, text=True, timeout=120)`

### Requirement: RAGAS gauge widget (anywidget) for per-cohort visual score

The system SHALL provide a `RAGASGaugeWidget` (a `mo.ui.anywidget`)
that renders a per-cohort RAGAS score as a circular progress gauge
with a colour band (green ≥0.85 / yellow ≥0.70 / red <0.70) + a
sparkline of the last 10 RAGAS scores from the audit table.

The canonical implementation SHALL live at
`notebooks/_shared/ragas_gauge.py:RAGASGaugeWidget`.

#### Scenario: operator drills down on Ireland LC Mathematics Higher EN and sees the RAGAS gauge

- **WHEN** the operator selects the drill-down for Ireland LC
  Mathematics Higher EN
- **THEN** the dashboard SHALL render a `RAGASGaugeWidget` showing
  the current RAGAS score (e.g. 0.82) + the colour band (yellow,
  since 0.70 ≤ 0.82 < 0.85) + a sparkline of the last 10 scores from
  `md:cianfhoghlaim.education.ireland.leaving_cycle.audit`
- **AND** the widget SHALL be reactive — when the operator changes
  the drill-down subject, the gauge SHALL re-render with the new
  cohort's RAGAS score

#### Scenario: RAGAS score is below the threshold (fail)

- **WHEN** the cohort's RAGAS score is <0.70
- **THEN** the gauge SHALL render in red
- **AND** the sparkline SHALL visualise the downward trend
- **AND** the operator SHALL see a `mo.callout(kind="warn")` next
  to the gauge with the message
  "🎯 M1 gate: RAGAS score <0.70 — re-extraction required"

#### Scenario: RAGAS score is excellent (green)

- **WHEN** the cohort's RAGAS score is ≥0.85
- **THEN** the gauge SHALL render in green
- **AND** the operator SHALL see a `mo.callout(kind="info")` next
  to the gauge with the message
  "✅ Excellent RAGAS score — cohort passed the M1 gate"