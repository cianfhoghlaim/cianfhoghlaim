# Tasks — Cianfhoghlaim-Nua V7 Vernaculars Pipelines v1

> 7 sections, 25 tasks. All tasks PASSED before
> `openspec archive 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1 --yes`.

## Phase A — OpenSpec scaffolding (5 min)

- [x] **A.1** Author `proposal.md` + `tasks.md` + spec delta
- [x] **A.2** `uv run openspec validate 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1 --strict` exits 0

## Phase B — Author the 7 DLT sources (§1, 7 tasks)

- [x] **B.1** `dlt_sources/education/wales/british_isles/welsh_vernacular.py` (CY)
- [x] **B.2** `dlt_sources/education/scotland/british_isles/scottish_gaelic_vernacular.py` (GD)
- [x] **B.3** `dlt_sources/education/isle_of_man/british_isles/manx_vernacular.py` (GV)
- [x] **B.4** `dlt_sources/education/jersey/british_isles/jersey_french_vernacular.py` (FR_JE)
- [x] **B.5** `dlt_sources/education/guernsey/british_isles/guernsey_french_vernacular.py` (FR_GG)
- [x] **B.6** `dlt_sources/breton_cornish/british_isles/breton_vernacular.py` (BR — new parent package)
- [x] **B.7** `dlt_sources/breton_cornish/british_isles/cornish_vernacular.py` (KW)

## Phase C — Author the 7 CocoIndex apps (§2, 8 tasks)

- [x] **C.1** `cocoindex_flows/vernacular/vernacular_factory.py` (the canonical factory)
- [x] **C.2** `cocoindex_flows/vernacular/welsh_embedding.py`
- [x] **C.3** `cocoindex_flows/vernacular/scottish_gaelic_embedding.py`
- [x] **C.4** `cocoindex_flows/vernacular/breton_embedding.py`
- [x] **C.5** `cocoindex_flows/vernacular/cornish_embedding.py`
- [x] **C.6** `cocoindex_flows/vernacular/manx_embedding.py`
- [x] **C.7** `cocoindex_flows/vernacular/jersey_french_embedding.py`
- [x] **C.8** `cocoindex_flows/vernacular/guernsey_french_embedding.py`

## Phase D — Add Convex `vernacular_documents` table + sibling files (§3, 9 tasks)

- [x] **D.1** `web/packages/db/convex/schema.ts` — added 13th table `vernacular_documents` (indexed by vernacular, jurisdiction, subject)
- [x] **D.2** `web/packages/db/convex/vernacular/welsh.ts`
- [x] **D.3** `web/packages/db/convex/vernacular/scottish_gaelic.ts`
- [x] **D.4** `web/packages/db/convex/vernacular/breton.ts`
- [x] **D.5** `web/packages/db/convex/vernacular/cornish.ts`
- [x] **D.6** `web/packages/db/convex/vernacular/manx.ts`
- [x] **D.7** `web/packages/db/convex/vernacular/jersey_french.ts`
- [x] **D.8** `web/packages/db/convex/vernacular/guernsey_french.ts`
- [x] **D.9** `web/packages/db/convex/vernacular/ulster_scots.ts`

## Phase E — Author the 8 Hono routes (§4, 10 tasks)

- [x] **E.1** `web/hono-api/src/routes/copilotkit/vernacular/_vernacular_factory.ts`
- [x] **E.2-§E.9** 8 sibling route files
- [x] **E.10** `web/hono-api/src/index.ts` mount update

## Phase F — Author the 7 Dagster orchestrator assets (§5, 7 tasks)

- [x] **F.1** `orchestration/defs/2_materials/vernacular/welsh_assets.py`
- [x] **F.2** `orchestration/defs/2_materials/vernacular/scottish_gaelic_assets.py`
- [x] **F.3** `orchestration/defs/2_materials/vernacular/breton_assets.py`
- [x] **F.4** `orchestration/defs/2_materials/vernacular/cornish_assets.py`
- [x] **F.5** `orchestration/defs/2_materials/vernacular/manx_assets.py`
- [x] **F.6** `orchestration/defs/2_materials/vernacular/jersey_french_assets.py`
- [x] **F.7** `orchestration/defs/2_materials/vernacular/guernsey_french_assets.py`

## Phase G — Tests (§6, 1 task)

- [x] **G.1** `tests/test_phase14_vernacular_pipelines.py` — 8 functions reachable, 7 DLT sources, 7 CocoIndex apps, Convex schema, Hono routes, 7 Dagster assets

## Phase H — Spec delta (§7, 1 task)

- [x] **H.1** Spec delta to `british-isles-education-pipeline` — 1 ADDED Requirement

---

*Last updated by Phase 14 build subagent at 2026-09-01.*
