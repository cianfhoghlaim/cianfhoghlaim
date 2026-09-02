# Tasks — Cianfhoghlaim-Nua V7 Vernaculars v1

> 4 sections, 5 tasks. All tasks PASSED before
> `openspec archive 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-v1 --yes`.

## Phase A — OpenSpec scaffolding (5 min)

- [x] **A.1** Author `proposal.md` + `tasks.md` + spec delta
- [x] **A.2** `uv run openspec validate 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-v1 --strict` exits 0

## Phase B — Author the 7-vernacular BAML file (§1, 1 task)

- [x] **B.1** `baml_src/british_isles/_cross/vernacular_languages.baml` (VernacularLanguage enum + VernacularSubjectSpec class + 8 extraction functions + 2 tests)

## Phase C — Update the TranslationRequest.source_language description (§2, 1 task)

- [x] **C.1** `baml_src/british_isles/_cross/multi_nation_curriculum.baml` (update description to include 11 language codes)

## Phase D — Regenerate baml_client + spec delta (§3-§4, 2 tasks)

- [x] **D.1** `uv run baml-cli generate --from baml_src` — regenerated `baml_client/`
- [x] **D.2** Spec delta to `british-isles-education-pipeline` — 1 ADDED Requirement

---

*Last updated by build subagent at 2026-09-01.*