## ADDED Requirements

### Requirement: `sync_health.py` dashboard consolidates the 10 sync layer sub-notebooks

The system SHALL provide a single `notebooks/sync_health.py`
grouped marimo dashboard that surfaces the 11 sync layers (paths +
ccc + cognee + skills + mcp + dagster + baml + stacks + agents +
notebooks + drfit-docs) as 10 tabs in a `mo.ui.tabs` widget.

The 10 tabs are:

| Tab | Source |
|:--|:--|
| **Overview** | The 11-layer status grid (from the legacy
  `24_deployment_control_panel.py` logic) |
| **Paths** | The `sync:paths` layer (drift detection on repo paths) |
| **CCC** | The `sync:ccc` layer (CocoIndex code semantic search) |
| **Cognee** | The `sync:cognee` layer (knowledge graph sync) |
| **Skills** | The `sync:skills` layer (.agents/skills/ validation) |
| **MCP** | The `sync:mcp` layer (14 MCP servers health) |
| **Dagster** | The `sync:dagster` layer (Dagster asset sync) |
| **BAML** | The `sync:baml` layer (BAML schema sync) |
| **Stacks** | The `sync:stacks` layer (89 Docker Compose stacks) |
| **Agents** | The `sync:agents` layer (12-agent fleet sync) |
| **Notebooks** | The `sync:notebooks` layer (60+ marimo notebooks sync) |

The canonical implementation SHALL live at
`notebooks/sync_health.py` and SHALL consume the 11 per-layer
overview helpers in
`notebooks/_shared/area_shims/sync_health.py`.

#### Scenario: operator opens the sync_health dashboard and sees the Overview grid

- **GIVEN** the operator runs
  `marimo edit notebooks/sync_health.py`
- **WHEN** the notebook loads
- **THEN** the Overview tab SHALL render a `mo.callout(grid)` showing
  the 11 sync layer statuses (paths / ccc / cognee / skills / mcp /
  dagster / baml / stacks / agents / notebooks / drfit-docs) with
  pass/fail/info counts
- **AND** the operator SHALL see the most recent
  `stedding/sync-reports/all-<date>.md` mtime

#### Scenario: operator clicks the BAML tab

- **WHEN** the operator clicks the "BAML" tab
- **THEN** the tab SHALL render the BAML sync health (the
  `baml_schemas` Cognee cluster population + the 838 BAML classes +
  the 7 clusters per the `baml-sync-loop` capability)
- **AND** the underlying `@app.cell` SHALL call
  `notebooks/_shared/area_shims/sync_health.py:baml_sync_overview()`

#### Scenario: operator clicks the Stacks tab

- **WHEN** the operator clicks the "Stacks" tab
- **THEN** the tab SHALL render the 89 Docker Compose stacks
  validation status (the `stacks-sync-loop` capability)
- **AND** the underlying `@app.cell` SHALL call
  `notebooks/_shared/area_shims/sync_health.py:stacks_sync_overview()`

#### Scenario: operator uses the LLM tab to ask about sync health

- **WHEN** the operator clicks the "Ask" tab (P3 — LLM chat) and
  types "Which sync layers are failing?"
- **THEN** the notebook SHALL call
  `mo.ai.llm.openai(base_url="http://litellm.cianfhoghlaim.ie/v1",
  model="minimax-m3", system_message="You are the cianfhoghlaim sync
  health assistant. You have access to the 11 sync layer statuses.
  When the user asks about a sync layer, refer to the
  `stedding/sync-reports/all-<date>.md` file.")` with the most recent
  sync report as context
- **AND** the LLM SHALL return a list of the failing sync layers with
  remediation suggestions

#### Scenario: the 10 legacy sub-notebooks are moved to `notebooks/legacy/v7_consolidation/sync/`

- **WHEN** the operator runs `ls notebooks/legacy/v7_consolidation/sync/`
- **THEN** the directory SHALL contain the 10 legacy sub-notebooks
  moved via `git mv`
- **AND** the directory SHALL have a `DEPRECATED.md` redirect note
  pointing to the new `notebooks/sync_health.py` dashboard