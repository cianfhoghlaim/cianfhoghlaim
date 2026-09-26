# Change: 2026-10-08-tuatha-closed-loop-mmo-v1

## Why

The Tuatha British Isles Formative Assessment MMO spec describes
PixiJS realms + sprite banks + BAML quest packs but the closed-loop
demo isn't wired together. The operator can't:

1. Click "Mathematics Formative Session" in `bun dev`
2. See a Tuatha PixiJS realm render with the celtic-art window chrome
3. Have the 6-language asset pipeline (Plan 7) generate the realm assets
4. Have the Cognee entity-asset graph (Plan 6) link the NCCA learning
   outcomes to the visible sprites
5. Have the DuckLake bridge (Plan 5) make the realm's asset metadata
   queryable via SQL

This is **Plan 8 (the final plan)** of the convergence saga
(`openspec/plans/2026-10-01-convergence-saga-v1.md`). After this lands,
the saga is complete (8 of 8 plans done); Stage 8 (the fresh-slate
spec refactor) becomes the next work on a separate branch.

## What Changes

### Code — new (~4 files)
- `orchestration/defs/4_asset_generation/tuatha_realm_asset.py` — the per-subject realm Dagster asset (queries the asset table + builds the realm JSON)
- `tuatha/agents/realm_constructor_agent.py` — the ADK agent that builds realms (the 26th agent in the fleet)
- `notebooks/dashboards/tuatha_realm_demo.py` — the live demo surface
- `tuatha/agents/quest_pack_agent.py` — the ADK agent that generates BAML quest packs

### Spec materialised
- `openspec/specs/tuatha-closed-loop-mmo/spec.md` — 4 Requirements

### Reference surfaces
- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` — the existing umbrella spec (8 NCCA subjects + 14 subjects when NCCA-adjacent)
- `agents/workflows/_render_assets_node.py` — the shared Pillar 4 node (Plan 2)
- `orchestration/assets/ducklake_maintenance.py` — the Lakehouse bridge (Plan 5)
- `agents/meaisinfhoghlaim/media_intel/cognee_linker.py` — the Cognee linker (Plan 6)
- `baml_src/british_isles/_cross/asset_generation.baml` — the 6 Celtic asset functions (Plan 7)

## What this does NOT ship
- The actual PixiJS rendering (deferred to a follow-up; this PR ships the data + agent + asset wiring that feeds the renderer)
- The full 14-subject coverage (Mathematics only at launch; the other 7 NCCA + 6 NCCA-adjacent subjects are added incrementally)
- Live multi-player state (the spec mentions SpacetimeDB but that's a separate workstream)

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
