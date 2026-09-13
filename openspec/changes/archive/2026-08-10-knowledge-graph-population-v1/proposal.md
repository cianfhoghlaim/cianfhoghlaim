# Proposal: Knowledge Graph Population + Bilingual Cross-Linguistic

**Change ID:** `2026-08-10-knowledge-graph-population-v1`
**Date:** 2026-08-10
**Author:** Build agent
**Status:** Draft

## Why

The 5-stage Irish education knowledge graph (Aistear → Primary → JC → SC → University) has been **architecturally complete but empty** since the 2026-08-15 centralized-registry change. Every per-stage cognify adapter exists (`scripts/graph_storage/cognify/cognee_integration/{aistear,primary,junior_cycle,senior_cycle,university}_cognify.py`) with full `EDGE_TYPES` + `STAGE_META` constants, but **only `cross_stage_cognify` has a `defs.yaml` registration**. The other 4 stages have no Dagster wrapper, so the daily `0 3 * * *` cron never materialises them.

This change:
1. Wires the 4 missing per-stage cognify adapters into Dagster (5-stage graph finally populates)
2. Activates the cross-stage `EDGE_DEFINITIONS` (the 8 hand-coded `BRIDGE` edges)
3. Migrates the 30 hard-coded `_PRE_LOADED` equivalences to Cognee dataset `british_isles_equivalences`
4. Adds 8 more equivalences (Scotland Nat 5/Higher/Adv Higher, Wales WJEC, NI CCEA, Jersey/Guernsey/IoM)
5. Wires the 9 ad-hoc `cognee_ingest*.py` scripts as Dagster sensors
6. Adds bilingual GA↔EN BAML extraction (`ExtractBilingualLearningOutcome` + `ExtractCrossLinguisticGA`)

## What changes

### Code (8 new + 5 modified)

| File | Status | What |
|---|---|---|
| `orchestration/defs/3_model_lifecycle/cognify/{aistear,primary,junior_cycle,senior_cycle,university}_cognify/defs.yaml` | **NEW ×5** | 5 sibling `defs.yaml` registrations (mirror `cross_stage_cognify`) |
| `orchestration/defs/3_model_lifecycle/cognify/sensors/{baml_schemas,dlt_sources,skills,agent_definitions,openspec,stacks_catalog,notebooks}_sensor.py` | **NEW ×7** | Sensor wrappers for the 7 `cognee_ingest_*.py` scripts |
| `scripts/migrate_cross_qual_to_cognee.py` | **NEW** | Loads 30 + 8 equivalences from `meaisinfhoghlaim/alignment/cross_qualification_subject_map.py` → Cognee dataset `british_isles_equivalences` |
| `orchestration/defs/3_model_lifecycle/cognify/sensors/defs.yaml` | **NEW** | Registers all 7 sensors |
| `scripts/graph_storage/cognify/cognee_integration/cross_stage_cognify.py` | modified | Iterates 8 `EDGE_DEFINITIONS` + calls BAML `ExtractCrossStageLink` |
| `baml_src/british_isles/ireland/education/_cross/cross_linguistic.baml` | modified | Adds `ExtractBilingualLearningOutcome` + `ExtractCrossLinguisticGA` with real prompts |
| `meaisinfhoghlaim/alignment/cross_qualification_subject_map.py` | modified | Adds 8 new equivalences (Scotland + Wales + NI + 3 Crown Dependencies) |
| `orchestration/automation/sync_schedules.py` | modified | Adds `cognee_<stage>_cognify_schedule` to the daily cron |

### Spec (2 spec deltas, +8 ADDED Requirements)

- `openspec/specs/cianfhoghlaim-cognify-knowledge-graph/spec.md` — 7 ADDED Requirements (5 per-stage cognify + cross-stage edges + cross-qual Cognee + 9 ingest sensors)
- `openspec/specs/centralized-model-registry/spec.md` — 1 ADDED Requirement (bilingual GA extraction)

### Openspec (this change)

- `openspec/changes/2026-08-10-knowledge-graph-population-v1/proposal.md` (this file)
- `openspec/changes/2026-08-10-knowledge-graph-population-v1/tasks.md`
- `openspec/changes/2026-08-10-knowledge-graph-population-v1/specs/cianfhoghlaim-cognify-knowledge-graph/spec.md` (delta)
- `openspec/changes/2026-08-10-knowledge-graph-population-v1/specs/centralized-model-registry/spec.md` (delta)

## Dependencies

- **Blocked by:** C1 (uses `md:cianfhoghlaim.ocr_results` table for cross-stage reasoning) — ✓ shipped
- **Blocked by:** Cognee service running (currently not running; will fail to materialize cognify assets until `docker compose up cognee` from `bonneagar/stacks/cognee/`)
- **Blocks:** C3 (uses bilingual cross-linguistic BAML functions); C5 (uses Cognee queries in CopilotKit actions)

## Success criteria

1. `openspec validate 2026-08-10-knowledge-graph-population-v1 --strict` returns 0 errors
2. The 5 new `defs.yaml` files load without error in `dagster asset list`
3. The 7 new sensor files register in the daily `0 3 * * *` cron
4. `mise run lint:registry` returns 0 hardcoded model strings
