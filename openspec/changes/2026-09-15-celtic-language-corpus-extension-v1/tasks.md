# Tasks: Celtic Language Corpus Extension

## Stage 0 — Pre-flight
- [ ] T0.1 — Confirm change 1 (Celtic Mythology Content System) is merged
- [ ] T0.2 — Create the new spec dirs

## Stage 1 — 4 new DLT source groups
- [ ] T1.1 — Create `dlt/language/scots/`
- [ ] T1.2 — Create `dlt/language/cornish/`
- [ ] T1.3 — Create `dlt/language/manx/`
- [ ] T1.4 — Create `dlt/language/corpas_cc_gaelic/`
- [ ] T1.5 — Run all 4 `mise run dlt:*` and verify ingest

## Stage 2 — .vrt parser helper
- [ ] T2.1 — Create `dlt/language/_shared/vrt_parser.py`
- [ ] T2.2 — Add unit tests
- [ ] T2.3 — Verify existing Corpas CC uses the new parser

## Stage 3 — OntoLex-Lemon cognify edges
- [ ] T3.1 — Add `cognateOf`, `translationOf`, `hasCognateIn` edge types
- [ ] T3.2 — Create `notebooks/_shared/cognate.py`
- [ ] T3.3 — Run `mise run cognee:cognify`

## Stage 4 — CEFR BAML functions
- [ ] T4.1 — Create `baml/celtic/corpus.baml` with 5 functions
- [ ] T4.2 — Run `baml-cli generate`

## Stage 5 — CEFR CocoIndex + Dagster
- [ ] T5.1 — Create `cocoindex_flows/biep_parity/cefr_embedding.py`
- [ ] T5.2 — Create `orchestration/defs/2_materials/cefr_assets.py`
- [ ] T5.3 — Run `mise run biep:v3:cefr`

## Stage 6 — CEFR Marimo dashboards
- [ ] T6.1 — Create `notebooks/35_celtic_corpus_dashboard.py`
- [ ] T6.2 — Create `notebooks/36_cefr_readiness_dashboard.py`
- [ ] T6.3 — Create `notebooks/_shared/cefr_scoring.py`
- [ ] T6.4 — Run `mise run notebook:cefr`

## Stage 7 — CEFR Learner Analytics Agent
- [ ] T7.1 — Create `cefr_learner_analytics_agent.py`
- [ ] T7.2 — Register in `AGENT_REGISTRY`
- [ ] T7.3 — Run `mise run agents:smoke`

## Stage 8 — Validation + handoff
- [ ] T8.1 — Run `mise run lint:skills`
- [ ] T8.2 — Run `openspec validate 2026-09-15-celtic-language-corpus-extension-v1 --strict`
- [ ] T8.3 — Run `mise run sync:all`
- [ ] T8.4 — Update `.agents/skills/celtic-language-pipeline/SKILL.md`
- [ ] T8.5 — Update `.agents/skills/cefr-learner-analytics/SKILL.md`