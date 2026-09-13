# Tasks: Ogham Celtic Stones Pipeline

## Stage 0 — Pre-flight
- [ ] T0.1 — Confirm change 1 (Celtic Mythology Content System) is merged
- [ ] T0.2 — Create the new spec dir `openspec/specs/ogham-celtic-stones-pipeline/`

## Stage 1 — DLT sources
- [ ] T1.1 — Create `dlt/language/cisp/__init__.py` + `cisp.py` + `tests/`
- [ ] T1.2 — Create `dlt/language/megalithic_portal/__init__.py` + `megalithic_portal.py` + `tests/`
- [ ] T1.3 — Run `mise run dlt:cisp` and verify ≥1,200 stones ingested
- [ ] T1.4 — Run `mise run dlt:megalithic` and verify ≥30,000 sites ingested

## Stage 2 — BAML extractors (extend from change 1)
- [ ] T2.1 — Add `ExtractCISPStone` + `ExtractOghamInscription` to `baml/celtic/mythology.baml`
- [ ] T2.2 — Run `baml-cli generate`

## Stage 3 — Convex schema
- [ ] T3.1 — Add `ogham_stones.ts`
- [ ] T3.2 — Add `anam_particles.ts`
- [ ] T3.3 — Add `stone_visits.ts`
- [ ] T3.4 — Run `mise run convex:dev`

## Stage 4 — CocoIndex v1 embedding App
- [ ] T4.1 — Create `cocoindex/biep_parity/ogham_stones_embedding.py`
- [ ] T4.2 — Run `mise run biep:v3:cocoindex-build`

## Stage 5 — Dagster asset layer
- [ ] T5.1 — Create `orchestration/defs/2_materials/ogham_stones_assets.py`
- [ ] T5.2 — Run `mise run biep:v3:ogham`

## Stage 6 — Spatial grid utility
- [ ] T6.1 — Create `notebooks/_shared/spatial_grid.py`
- [ ] T6.2 — Add 12 unit tests for the spatial grid
- [ ] T6.3 — Run `mise run lint:notebooks`

## Stage 7 — Ogham Stone Agent
- [ ] T7.1 — Create `agents/meaisinfhoghlaim/educational/ogham_stone_agent.py`
- [ ] T7.2 — Register in `AGENT_REGISTRY` with `litellm_routing_key="ogham"`
- [ ] T7.3 — Run `mise run agents:smoke`

## Stage 8 — Marimo dashboard
- [ ] T8.1 — Create `notebooks/34_ogham_stones_dashboard.py`
- [ ] T8.2 — Run `mise run notebook:ogham`

## Stage 9 — Validation + handoff
- [ ] T9.1 — Run `mise run lint:skills`
- [ ] T9.2 — Run `openspec validate 2026-09-08-ogham-celtic-stones-pipeline-v1 --strict`
- [ ] T9.3 — Run `mise run sync:all`
- [ ] T9.4 — Update `.agents/skills/ogham-celtic-stones-pipeline/SKILL.md`