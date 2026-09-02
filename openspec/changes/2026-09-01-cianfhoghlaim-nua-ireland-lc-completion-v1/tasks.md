# Tasks — Cianfhoghlaim-Nua Ireland LC Completion v1

> 6 sections, 12 tasks. All tasks PASSED before
> `openspec archive 2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1 --yes`.

## Phase A — OpenSpec scaffolding (5 min)

- [x] **A.1** Author `proposal.md` + `tasks.md` + spec delta
- [x] **A.2** `uv run openspec validate 2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1 --strict` exits 0

## Phase B — Author the 8 NCCA-adjacent + physics BAML files (§1, 8 tasks)

- [x] **B.1** `baml_src/british_isles/ireland/education/marking/accounting_marking.baml`
- [x] **B.2** `baml_src/british_isles/ireland/education/marking/business_marking.baml`
- [x] **B.3** `baml_src/british_isles/ireland/education/marking/french_marking.baml`
- [x] **B.4** `baml_src/british_isles/ireland/education/marking/history_marking.baml`
- [x] **B.5** `baml_src/british_isles/ireland/education/marking/art_marking.baml`
- [x] **B.6** `baml_src/british_isles/ireland/education/marking/music_marking.baml`
- [x] **B.7** `baml_src/british_isles/ireland/education/marking/applied_mathematics_marking.baml`
- [x] **B.8** `baml_src/british_isles/ireland/education/marking/physics_marking.baml`

## Phase C — Extend the CocoIndex LC factory (§2, 1 task)

- [x] **C.1** `cocoindex_flows/biep_parity/ireland_lc_factory.py` — add 8 `LCSubjectConfig` entries

## Phase D — Create the 16 Convex subject tables (§3, 4 tasks)

- [x] **D.1** 14 `.ts` + 14 `.types.ts` lifted from archive + applied_mathematics created
- [x] **D.2** `web/apps/cianfhoghlaim-nua/convex/lc/index.ts` (re-exports)
- [x] **D.3** `web/apps/cianfhoghlaim-nua/convex/schema.ts` (defines the 8 new tables + the 7 existing tables)
- [x] **D.4** All 8 subject tables verified importable

## Phase E — Create the 2 missing CocoIndex early-years Apps (§4, 3 tasks)

- [x] **E.1** `cocoindex_flows/british_isles/ireland/education/aistear_embedding.py`
- [x] **E.2** `cocoindex_flows/british_isles/ireland/education/primary_embedding.py`
- [x] **E.3** Both flows have bilingual EN/GA fields (always bilingual per operator direction)

## Phase F — Regenerate baml_client (§5, 1 task)

- [x] **F.1** `uv run baml-cli generate --from baml_src` — regenerated `baml_client/`

## Phase G — Spec delta (§6, 1 task)

- [x] **G.1** `openspec/changes/2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1/specs/british-isles-education-pipeline/spec.md` (2 ADDED Requirements)

---

*Last updated by build subagent at 2026-09-01.*