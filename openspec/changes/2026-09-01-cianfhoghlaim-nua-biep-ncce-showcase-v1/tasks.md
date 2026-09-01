# Tasks — BIEP NCCE Showcase v1

> 7 sections, 12 tasks. All tasks MUST pass before
> `openspec archive 2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1 --yes`.

## Phase A — OpenSpec scaffolding (5 min)

- [x] **A.1** Author `proposal.md` + `tasks.md` + spec delta
- [x] **A.2** `uv run openspec validate 2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1 --strict` exits 0

## Phase B — Author the canonical NCCE BAML file (§1, 1 task)

- [x] **B.1** `baml_src/british_isles/uk_ncce/learning_graph.baml` (6 enums + 7 classes + 6 extractors + 1 pedagogy overlay + 4 tests)

## Phase C — Author the equivalencies BAML file (§2, 1 task)

- [x] **C.1** `baml_src/british_isles/uk_ncce/equivalencies.baml` (11 jurisdictions + 3 classes + 1 function + 1 test)

## Phase D — Lift the CocoIndex grid-aware converter (§3, 3 tasks)

- [x] **D.1** `cocoindex_flows/_shared/_docling_grid_segmenter.py`
- [x] **D.2** `cocoindex_flows/uk_ncce/learning_graphs_app.py`
- [x] **D.3** `cocoindex_flows/uk_ncce/__init__.py` + `README.md`

## Phase E — Lift the 11 NCCE learning-graph JSONs (§4, 1 task)

- [x] **E.1** Copied `data/bi_ep/learning_graphs/uk_ncce_*.json` (11 files)

## Phase F — Extend the Convex schema with NCCE tables (§5, 1 task)

- [x] **F.1** `web/packages/db/convex/schema.ts` — adds the `ncce_learning_graphs` table

## Phase G — Regenerate baml_client (§6, 1 task)

- [x] **G.1** `uv run baml-cli generate --from baml_src` — regenerated `baml_client/` (14 files)

## Phase H — Spec delta (§7, 1 task)

- [x] **H.1** `openspec/changes/2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1/specs/oicelais-pipeline/spec.md` — 3 ADDED Requirements

---

*Last updated by build subagent at 2026-09-01.*