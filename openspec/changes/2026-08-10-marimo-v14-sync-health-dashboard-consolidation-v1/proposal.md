# Change: Sync health dashboard consolidation (marimo v14)

## Why

The 10 sync layer dashboards under `notebooks/` fragment the
cianfhoghlaim sync surface:

- `14_dev_env_tools_*.py` (5 dev_env tools dashboards)
- `15_observability_*.py` (3 observability dashboards)
- `25_dagster_sync_dashboard.py`
- `26_baml_sync_dashboard.py`
- `27_stacks_sync_dashboard.py`
- `28_dlt_sync_dashboard.py`
- `29_agents_sync_dashboard.py`
- `30_notebooks_sync_dashboard.py`

This fragmentation makes it hard for operators to find the right
sync dashboard, hard to verify all 11 sync layers are healthy, and
hard to surface the LLM-assisted "ask about sync health" feature
across the entire sync surface.

Following the same pattern as the BIEP lakehouse explorer
consolidation (`10_biep_pipeline_lakehouse_06_exam_papers_explorer.py`
already uses 8 tabs) + the Tier 3 grouped dashboards (the
`2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1`
change), this change consolidates the 10 sync dashboards into 1
`sync_health.py` dashboard with 10 tabs (one per sync layer).

## What changes

- **1 new grouped marimo dashboard**:
  `notebooks/sync_health.py` — 10 tabs: Dev Env Tools /
  Observability / Dagster / BAML / Stacks / DLT / Agents / Notebooks
  / Cognee / CCC.
- **10 old sync sub-notebooks deprecated** — moved to
  `notebooks/legacy/v7_consolidation/sync/`.
- **1 new area_shim module**:
  `notebooks/_shared/area_shims/sync_health.py` — the 10 per-tab
  overview helpers.
- **1 new `mise.toml` task** — `biep:v3:marimo:sync:dev`.
- **1 ADDED Requirement** to
  `openspec/specs/cianfhoghlaim-marimo-dashboards/spec.md`.

## Out of scope

- The 17 Tier 1+2 BIEP v3 dashboards (already in
  `2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1`).
- The 6 Tier 3 grouped dashboards (already in
  `2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1`).
- The 4 Tier 4 legacy notebooks (`notebooks/legacy/*` +
  `ie_law_explorer.py`).
- Cross-repo changes (`leabharlann/` is a read-only consumer).

## Dependencies

```markdown
## Dependencies

`Blocked by (soft): 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1`
(the 3 helper modules — `marimo_patterns.py`,
`area_shims/biiep_v3_dashboard.py`, `ragas_gauge.py` — are required
inputs for the sync_health dashboard).

`Affected repos: cianfhoghlaim`
```

## Impact

- **Affected specs**: `cianfhoghlaim-marimo-dashboards` (1 ADDED
  Requirement).
- **Affected code/config**:
  - 1 new grouped dashboard (~600 LOC)
  - 1 new area_shim module (~120 LOC)
  - 10 old sync sub-notebooks moved to
    `notebooks/legacy/v7_consolidation/sync/`
  - `mise.toml` adds 1 `biep:v3:marimo:sync:dev` task
- **LOC saved**: ~500+ LOC (consolidation of the 10 sync sub-notebooks).
- **No secret values written to disk**: all `infisical://dev-baile/...`
  refs hydrated by mise + Locket.

## Cross-references

- `openspec/specs/cianfhoghlaim-marimo-dashboards/spec.md` — the
  capability this change extends (1 ADDED Requirement)
- `openspec/specs/knowledge-sync-loop/spec.md` — the 11-layer sync
  architecture (the `sync_health.py` dashboard surfaces this)
- `openspec/changes/2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1/`
  — the 3 helper modules this change depends on
- `openspec/specs/baml-sync-loop/spec.md` — the BAML sync layer (the
  BAML tab surfaces this)
- `openspec/specs/dlt-sync-loop/spec.md` — the DLT sync layer (the
  DLT tab surfaces this)
- `openspec/specs/stacks-sync-loop/spec.md` — the stacks sync layer
  (the Stacks tab surfaces this)
- `openspec/specs/agents-sync/spec.md` — the agents sync layer (the
  Agents tab surfaces this)
- `openspec/specs/notebooks-sync-loop/spec.md` — the notebooks sync
  layer (the Notebooks tab surfaces this)
- `openspec/specs/dagster-asset-sync/spec.md` — the Dagster asset
  sync layer (the Dagster tab surfaces this)
- `.agents/skills/knowledge-sync-loop/SKILL.md` — the knowledge sync
  loop skill (the dashboard surfaces all 11 layers)