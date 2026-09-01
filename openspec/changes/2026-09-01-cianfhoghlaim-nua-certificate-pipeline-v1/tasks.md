# Tasks — Cianfhoghlaim-Nua Certificate Pipeline v1

> 8 sections, 14 tasks. All tasks PASSED before
> `openspec archive 2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1 --yes`.

## Phase A — OpenSpec scaffolding (5 min)

- [x] **A.1** Author `proposal.md` + `tasks.md` + spec delta
- [x] **A.2** `uv run openspec validate 2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1 --strict` exits 0

## Phase B — Author the canonical certificate types (§1, 1 task)

- [x] **B.1** `meaisinfhoghlaim/certificate/types.py` (4 dataclasses)

## Phase C — Author the canonical certificate rubric (§2, 1 task)

- [x] **C.1** `meaisinfhoghlaim/certificate/rubric.py` (SSIM + 2 coverage checks)

## Phase D — Author the 7-stage pipeline (§3, 1 task)

- [x] **D.1** `meaisinfhoghlaim/certificate/pipeline.py` (7 stages + orchestrator + stdlib fallback)

## Phase E — Author the canonical certification BAML (§4, 1 task)

- [x] **E.1** `baml_src/british_isles/ireland/education/certification.baml` (3 enums + 2 classes + 1 function + 1 test)

## Phase F — Author the NCCA policy PDF placeholder (§5, 1 task)

- [x] **F.1** `data/ireland/ncca_policy/README.md`

## Phase G — Author the 7-test integration suite (§6, 1 task)

- [x] **G.1** `tests/test_phase7_certificate_pipeline.py` (7 tests)

## Phase H — Regenerate baml_client (§7, 1 task)

- [x] **H.1** `uv run baml-cli generate --from baml_src` (14 files)

## Phase I — Spec delta (§8, 1 task)

- [x] **I.1** `openspec/changes/2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1/specs/agent-memory-systems/spec.md` (2 ADDED Requirements)

---

*Last updated by build subagent at 2026-09-01.*