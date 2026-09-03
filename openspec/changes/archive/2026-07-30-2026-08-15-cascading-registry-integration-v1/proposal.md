# 2026-08-15-cascading-registry-integration-v1

## Why

The `2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`
change (archived) introduced 4 canonical artifacts:

1. `MODEL_REGISTRY` at `meaisinfhoghlaim/models/model_registry.py` (52 entries / 7 families)
2. `notebooks/_shared/schema.py` (5 introspection helpers)
3. `notebooks/00_control_panel.py` (the 5-tab marimo control panel)
4. `deployment-choice.yaml` (the canonical enablement file)

Plus 4 supporting artifacts:

5. `scripts/registry_audit.py` + `mise run lint:registry` (drift detector)
6. `agents/adk/litellm_agent.py` (LiteLlm wrapper + `litellm_model("minimax")`)
7. `orchestration/defs/2_materials/_base/jurisdiction_assets_base.py` + 10 subclasses
8. 3 CocoIndex factories (`european_nations/_factory.py`, `biep_parity/ireland_lc_factory.py`, `biep_parity/bi_factory.py`)

A cascading-effects audit identified **12+ downstream artifacts** that need
to be updated to consume these new canonical surfaces:

- 10 of 14 OpenCode subagents don't include `centralized-registry` in their `skill_filter`
- `orchestration/definitions.py` doesn't import the 10 `JurisdictionAssetsBase` subclasses
- `web/hono-api/src/index.ts` doesn't mount the control-panel endpoints
- 23 marimo dashboards (17 BIEP + 6 BIEP v3) don't reference the new registry
- `opencode.json` provider.minimax has hardcoded URL instead of canonical LiteLLM gateway
- `mise run lint` doesn't include `lint:registry` as a CI gate
- `orchestration/defs/sync_assets.py` doesn't surface the registry drift count
- 12+ openspec specs reference the old model registry / schema patterns

This change updates each of these to consume the new canonical surfaces.

## What Changes

### A. OpenCode subagent wiring (`opencode.json`)

Add `centralized-registry` to the `skill_filter` of all 10 subagents that
have a non-empty skill_filter (data-platform, infrastructure,
agent-platform, frontend-apps, research, notebooks, baml, dagster, mise,
proposal-author). Update `provider.minimax.options.baseURL` to point at
the canonical LiteLLM gateway `https://litellm.cianfhoghlaim.ie`.

### B. Dagster definitions wiring (`orchestration/definitions.py`)

Add a new "Jurisdiction-level ingestion assets" section that imports
the 10 `JurisdictionAssetsBase` subclasses from
`orchestration/defs/2_materials/_base/<jurisdiction>_assets.py` and adds
their 10 `<jurisdiction>_documents_ingested` assets to the `Definitions`.

### C. Hono API router (`web/hono-api/src/index.ts`)

Mount the new control-panel routes from `web/hono-api/control-panel/index.ts`
at `/api/control-panel/*` via `app.route("/api/control-panel", controlPanelApp)`.

### D. 3 new CocoIndex factory L3 Component `defs.yaml` files

Create:
- `orchestration/defs/3_model_lifecycle/cocoindex_v1/european_nations_factory/defs.yaml`
- `orchestration/defs/3_model_lifecycle/cocoindex_v1/ireland_lc_factory/defs.yaml`
- `orchestration/defs/3_model_lifecycle/cocoindex_v1/biep_parity_factory/defs.yaml`

Each wires the corresponding factory module + documents the factory
pattern (40 + 11 + 8 Apps emitted by module import time).

### E. `mise run lint` CI gate

Update `[tasks.lint]` in `mise.toml` to chain `lint:skills` +
`lint:registry` + `ruff check` (so `mise run lint` includes the
centralized-registry drift detection).

### F. `sync_assets.py` (orchestration sync_health)

Add a `_get_registry_drift_count()` helper + the `registry_drift_count`
metadata field + the `registry_drift_alert` sensor.

### G. 12 cascading openspec spec deltas

Update 12 specs to cross-reference the new artifacts:

| Spec | Cross-reference |
|---|---|
| `meaisin-24-ocr-models` | `MODEL_REGISTRY.filter(family="ocr_vision")` |
| `meaisinfhoghlaim-ocr-htr` | (already updated) |
| `meaisinfhoghlaim-platform` | Update "canonical home" note |
| `agent-registry` | Add `MODEL_REGISTRY.resolve()` for each agent |
| `agent-platform-cluster` | (already updated) |
| `indexing-and-cognition` | Add `centralized-registry` skill to registry surface |
| `dagster-5-layer-component-architecture` | Reference the 10 subclasses |
| `agentic-frontend-frameworks` | Add the 5th web surface |
| `british-isles-education-pipeline[-v3]` | Reference the schema capture |
| `cianfhoghlaim-pipeline` | Reference `list_dlt_sources()` |
| `agent-observability` | Add `lint:registry` to observability stack |
| `motherduck-connections` | Add the 5th surface to inventory |

### H. 23 marimo dashboards

Migrate 23 BIEP / BIEP v3 dashboard notebooks to use the 5 schema
helpers (added via cascading `_DEFAULT_LLM` + `_REGISTRY_SUMMARY` constants).

### I. AGENTS.md updates

Add the `centralized-registry` skill row to:
- `agents/tuatha/AGENTS.md` (already done in this round)
- `agents/meaisinfhoghlaim/AGENTS.md`
- `spaces/_common/AGENTS.md`

## Capabilities

### New Capabilities

None — this change is a cascading integration of the 3 specs already
shipped by the prior change.

### Modified Capabilities

See section G above for the 12 spec deltas.

## Impact

- `opencode.json` — updated (10 subagents + provider.minimax)
- `orchestration/definitions.py` — updated (10 jurisdiction assets wired)
- `web/hono-api/src/index.ts` — updated (control-panel routes mounted)
- `mise.toml` — updated (lint:registry in lint chain)
- `orchestration/defs/sync_assets.py` — updated (registry drift count)
- 23 marimo dashboards — updated (cascading constants)
- 3 CocoIndex factory L3 Component `defs.yaml` files — created
- 12 openspec specs — spec deltas updated
- 3 AGENTS.md files — registry row added

Net file changes: ~50 files modified + 3 created.

## Quality gates

- `mise run lint` must include `lint:registry` (CI gate)
- `mise run lint:registry --strict` must exit 0
- `dagster:dev` must load the 10 new jurisdiction assets
- The web UI control panel (`localhost:3000/control-panel`) must show
  all 5 tabs populated with real data from the Python bridge

## Dependencies

`Blocked by: 2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`
(the foundational change that introduced the 4 canonical artifacts
+ 4 supporting artifacts)

`Blocked by (soft): #142 BAML TypeScript codegen` (deferred — the
baml.toml declaration is correct; the Node tool is missing)
