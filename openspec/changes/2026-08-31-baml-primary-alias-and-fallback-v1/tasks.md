# Tasks: BAML Primary Alias + Per-Function Fallback Chains v1

> 6 phases, ~15 tasks. All tasks MUST pass before `openspec archive`.

## Phase A — OpenSpec scaffolding (5 min)

- [ ] **A.1** Author `proposal.md` + `tasks.md` + `specs/centralized-model-registry/spec.md`
- [ ] **A.2** `openspec validate 2026-08-31-baml-primary-alias-and-fallback-v1 --strict` — passes 0 errors

## Phase B — mise.toml helpers (10 min)

- [ ] **B.1** Add `[tasks."baml:switch-primary"]` — one-liner `mise env set MODEL_BASE_URL ... MODEL_PRIMARY ...`
- [ ] **B.2** Add `[tasks."baml:list-models"]` — lists the 7 concrete clients + their resolved base_url + model

## Phase C — BAML template (15 min)

- [ ] **C.1** Author `baml_src/_shared/templates/primary_alias_with_fallback.baml` — the canonical fallback chain template

## Phase D — 4 canonical BIEP v3 extraction functions get fallback chains (20 min)

- [ ] **D.1** `baml_src/british_isles/_cross/biiep_v3_canonical.baml` — `ExtractCurriculumSyllabus` + `ExtractExamPaperLayout` + `ExtractMarkingSchemeGuideline` + `ExtractCrossLinguisticConcept` get `fallback "UnslothGemma4" "VertexGemini35Flash"`

## Phase E — 8 generic aliases get cleanup comments (10 min)

- [ ] **E.1** `baml_src/clients.baml` — 8 generic aliases (`Extractor`, `ExtractorFast`, etc.) get `# 2026-08-31: use Primary for new code` comments

## Phase F — CI gate (15 min)

- [ ] **F.1** Author `scripts/baml_audit_fallbacks.py` — fails if any non-exception BAML function is missing a `fallback` block
- [ ] **F.2** Add `[tasks."lint:baml-fallbacks"]` that runs the audit

## Phase G — Validation (5 min)

- [ ] **G.1** `mise run openspec:validate 2026-08-31-baml-primary-alias-and-fallback-v1 --strict`
- [ ] **G.2** `mise run baml:generate` (when the pre-existing personal_archive_extraction.baml parse error is resolved)
- [ ] **G.3** `uv run python scripts/baml_audit_fallbacks.py --strict` — 0 drift

## Phase H — Hand-off (5 min)

- [ ] **H.1** Notify Phase 5 (meaisinfhoghlaim Unsloth-priority) — the `Primary` alias is now wired + can be overridden per-function

---

*Last updated by build subagent at 2026-08-31.*