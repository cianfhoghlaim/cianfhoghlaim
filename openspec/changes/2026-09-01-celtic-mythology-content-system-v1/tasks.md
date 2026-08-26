# Tasks: Celtic Mythology Content System

## Stage 0 — Pre-flight
- [ ] T0.1 — Verify `mise run lint:registry` passes
- [ ] T0.2 — Verify `openspec list --specs` returns ≥90 specs
- [ ] T0.3 — Confirm parent changes (rename + BIEP v3) are merged
- [ ] T0.4 — Create the new spec dir `openspec/specs/celtic-mythology-content-system/`

## Stage 1 — BAML schema authoring (the SSOT)
- [ ] T1.1 — Create `baml/celtic/mythology.baml` with 8 functions: `ExtractCelticDeity`, `ExtractGeis`, `ExtractOghamInscription`, `ExtractHeroCycle`, `ExtractPentElementalAffinity`, `ExtractMythologyQuest`, `BuildGameAssetFromLO`, `ComposeMythologyNarrative`
- [ ] T1.2 — Create `baml/celtic/irish_history.baml` with 6 functions: `ExtractIrishDynasty`, `ExtractProvincialKingdom`, `ExtractTimelineEvent`, `ExtractHighKing`, `ExtractFomoriansBattle`, `ExtractNormanImpact`
- [ ] T1.3 — Create `baml/celtic/geography_curriculum.baml` with 4 functions: `ExtractLCGeographyOutcome`, `ExtractALevelGeographyTopic`, `ExtractCfEGeographyArea`, `ExtractWJECGeographyTheme`
- [ ] T1.4 — Run `baml-cli generate`
- [ ] T1.5 — Verify `mise run lint:registry` passes

## Stage 2 — CocoIndex v1 embedding App
- [ ] T2.1 — Create `cocoindex_flows/biep_parity/mythology_embedding.py` (R1-R4)
- [ ] T2.2 — Create `cocoindex_flows/biep_parity/irish_history_embedding.py` (R1-R4)
- [ ] T2.3 — Run `mise run biep:v3:cocoindex-build`

## Stage 3 — Dagster asset layer
- [ ] T3.1 — Create `orchestration/defs/2_materials/mythology_assets.py`
- [ ] T3.2 — Create `orchestration/defs/2_materials/irish_history_assets.py`
- [ ] T3.3 — Register both modules in `orchestration/defs/2_materials/__init__.py`
- [ ] T3.4 — Run `mise run biep:v3:mythology`

## Stage 4 — Marimo notebooks
- [ ] T4.1 — Create `notebooks/30_mythology_dashboard.py`
- [ ] T4.2 — Create `notebooks/31_irish_history_timeline.py`
- [ ] T4.3 — Create `notebooks/32_british_isles_map.py`
- [ ] T4.4 — Create `notebooks/33_educational_geography.py`
- [ ] T4.5 — Run `mise run notebook:mythology`

## Stage 5 — GeoAI + DuckDB helpers
- [ ] T5.1 — Create `notebooks/_shared/geoai.py` (12 GeoAI ops)
- [ ] T5.2 — Create `notebooks/_shared/geo.py`
- [ ] T5.3 — Create `notebooks/_shared/curriculum.py`
- [ ] T5.4 — Run `mise run notebook:geoai-test`

## Stage 6 — Educational agents
- [ ] T6.1 — Create `agents/meaisinfhoghlaim/educational/celtic_mythology_agent.py`
- [ ] T6.2 — Create `agents/meaisinfhoghlaim/educational/irish_history_agent.py`
- [ ] T6.3 — Create `agents/meaisinfhoghlaim/educational/educational_geography_agent.py`
- [ ] T6.4 — Register all 3 agents in `AGENT_REGISTRY`
- [ ] T6.5 — Run `mise run agents:smoke`

## Stage 7 — Fibo enablement
- [ ] T7.1 — Flip `local/image/fibo: true` in `deployment-choice.yaml`
- [ ] T7.2 — Create `bonneagar/stacks/fibo-server/` (6-file GOLD_STANDARD)
- [ ] T7.3 — Add `fibo-server` Komodo procedure
- [ ] T7.4 — Run `mise run cic:stack-doctor`

## Stage 8 — Validation + handoff
- [ ] T8.1 — Run `mise run lint:skills`
- [ ] T8.2 — Run `mise run lint:drift-docs`
- [ ] T8.3 — Run `openspec validate 2026-09-01-celtic-mythology-content-system-v1 --strict`
- [ ] T8.4 — Run `mise run sync:all`
- [ ] T8.5 — Update `.agents/skills/celtic-mythology-content-system/SKILL.md`
- [ ] T8.6 — Update `.agents/skills/centralized-registry/SKILL.md`