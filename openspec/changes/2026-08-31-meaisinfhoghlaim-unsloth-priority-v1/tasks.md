# Tasks: meaisinfhoghlaim Unsloth-Priority Refactor v1

> 9 phases, ~15 tasks. All tasks MUST pass before `openspec archive`.

## Phase A — OpenSpec scaffolding (5 min)

- [ ] **A.1** Author `proposal.md` + `tasks.md` + `specs/meaisinfhoghlaim-ocr-htr/spec.md`
- [ ] **A.2** `openspec validate 2026-08-31-meaisinfhoghlaim-unsloth-priority-v1 --strict`

## Phase B — OCR ensemble (10 min)

- [ ] **B.1** `meaisinfhoghlaim/ocr/ensemble/__init__.py` — update module docstring to reference gemma4_vision
- [ ] **B.2** `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py` — update `_PATH_TO_BACKEND` (already done in Phase 1 cascade)

## Phase C — Backends (5 min)

- [ ] **C.1** `meaisinfhoghlaim/backends/scanned_detector.py` — default to gemma-4-26b-a4b-vision (already done in Phase 1 cascade)

## Phase D — Datasets (5 min)

- [ ] **D.1** `meaisinfhoghlaim/datasets/irish_processing.py` — re-order the 5-model chain (already done in Phase 1 cascade)

## Phase E — Training (10 min)

- [ ] **E.1** `meaisinfhoghlaim/training/modal_finetune/finetune_unsloth_local.py` — base model + checkpoint dir swap (already done in Phase 1 cascade)
- [ ] **E.2** `meaisinfhoghlaim/training/training/langfuse_callbacks.py` — model name key swap (already done in Phase 1 cascade)

## Phase F — Alignment (15 min)

- [ ] **F.1** Add `gemma4_opus_mt` alignment method to `meaisinfhoghlaim/alignment/`
- [ ] **F.2** Add Gemma 4 fallback to the 4 alignment methods (cross-frame, cross-archive, cross-nation, fuzzy)

## Phase G — Federated (10 min)

- [ ] **G.1** Add `get_optimal_for_federated()` helper to `meaisinfhoghlaim/federated/`
- [ ] **G.2** Add Gemma 4 fallback when Unsloth Studio is unreachable

## Phase H — Evaluation (10 min)

- [ ] **H.1** Add the Gemma 4 + MiniMax + gemini-3.5-flash comparison harness to `meaisinfhoghlaim/evaluation/`

## Phase I — Document factory (10 min)

- [ ] **I.1** Add Document AI (GCP) primary to `meaisinfhoghlaim/document_factory/`
- [ ] **I.2** Add Docling-serve (local opensource) fallback

## Phase J — Validation (5 min)

- [ ] **J.1** `mise run openspec:validate 2026-08-31-meaisinfhoghlaim-unsloth-priority-v1 --strict`
- [ ] **J.2** `mise run lint:registry` — 0 drift
- [ ] **J.3** `mise run cic:ocr:test` — 8 OCR backends tested

---

*Last updated by build subagent at 2026-08-31.*