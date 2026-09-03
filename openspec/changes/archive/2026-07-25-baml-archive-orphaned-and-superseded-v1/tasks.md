# 2026-07-25-baml-archive-orphaned-and-superseded-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify Changes 1 + 2 merged on `feat/iac-ify-arm1-oci-control-plane`
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Move 15 BAML files

- [ ] `mkdir -p baml_src/british_isles/ireland/education/_legacy/{grading,web,pdfs}`
- [ ] `git mv baml_src/.../grading/chemistry_grading.baml baml_src/.../_legacy/grading/`
- [ ] `git mv baml_src/.../grading/computer_science_grading.baml baml_src/.../_legacy/grading/`
- [ ] `git mv baml_src/.../grading/english_grading.baml baml_src/.../_legacy/grading/`
- [ ] `git mv baml_src/.../grading/gaeilge_grading.baml baml_src/.../_legacy/grading/`
- [ ] `git mv baml_src/.../grading/geography_grading.baml baml_src/.../_legacy/grading/`
- [ ] `git mv baml_src/.../grading/mathematics_grading.baml baml_src/.../_legacy/grading/`
- [ ] `git mv baml_src/.../web/chemistry_web.baml baml_src/.../_legacy/web/`
- [ ] `git mv baml_src/.../web/computer_science_web.baml baml_src/.../_legacy/web/`
- [ ] `git mv baml_src/.../web/english_web.baml baml_src/.../_legacy/web/`
- [ ] `git mv baml_src/.../web/gaeilge_web.baml baml_src/.../_legacy/web/`
- [ ] `git mv baml_src/.../web/geography_web.baml baml_src/.../_legacy/web/`
- [ ] `git mv baml_src/.../web/mathematics_web.baml baml_src/.../_legacy/web/`
- [ ] `git mv baml_src/.../pdfs/leaving_cert_marking_scheme.baml baml_src/.../_legacy/pdfs/`
- [ ] `git mv baml_src/.../pdfs/leaving_cert_past_paper.baml baml_src/.../_legacy/pdfs/`
- [ ] `git mv baml_src/.../pdfs/leaving_cert_syllabus.baml baml_src/.../_legacy/pdfs/`

## Stage 2 — Create `_legacy/` package

- [ ] Create `baml_src/.../_legacy/__init__.baml` (empty re-export)
- [ ] Create `baml_src/.../_legacy/grading/README.md` with the REMOVED notice
- [ ] Create `baml_src/.../_legacy/web/README.md` with the REMOVED notice
  (explain the duplicate-function-name shadow bug)
- [ ] Create `baml_src/.../_legacy/pdfs/README.md` with the REMOVED notice
  (explain the `lc_extraction/` shadow collision)

## Stage 3 — BAML codegen validation

- [ ] `cd baml_src && uv run baml-cli generate` — must succeed cleanly
- [ ] `mise run baml:cli-test` (the CI gate from `2026-07-12-baml-cli-test-ci-gate-v1`) — must pass
- [ ] Verify no function-name conflicts (the `WebStudyPlan` shadow bug is resolved)

## Stage 4 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-07-25-baml-archive-orphaned-and-superseded-v1/specs/british-isles-education-pipeline/spec.md`
  with 3 `## REMOVED Requirements` sections
- [ ] Run `openspec validate 2026-07-25-baml-archive-orphaned-and-superseded-v1 --strict`
- [ ] Commit the change on a dedicated branch `openspec/2026-07-25-baml-archive-orphaned-and-superseded-v1`
- [ ] Open a PR on `origin/main` referencing this change
- [ ] Run `mise run lint:skills` — must remain 53/53
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-07-25-baml-archive-orphaned-and-superseded-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Update `docs/baml/_legacy-archive.md` with the migration notes
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol