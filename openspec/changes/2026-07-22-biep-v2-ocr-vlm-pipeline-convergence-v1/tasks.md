# 2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify Changes 1 + 2 merged on `origin/main`
- [ ] Verify the 6-subject BIEP v1 + JC + England pipelines still pass
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`
- [ ] Verify the Unstract + Docling-serve stacks are running:
  `docker compose -f bonneagar/stacks/unstract/compose.yaml -f sidecar.yaml up -d`
  `docker compose -f bonneagar/stacks/docling-serve/compose.yaml up -d`

## Stage 1 — OCR/VLM registry extension

- [ ] Edit `meaisinfhoghlaim/models/registry.py`:
  - Add `ModelBackend.DOCLING = "docling"` enum value
  - Add `ModelBackend.UNSTRACT = "unstract"` enum value
  - Add 2 new `ModelCapability` enum values: `UNISTRUCT_WORKFLOW`, `DOCLING_LAYOUT`
  - Add 2 new `VISION_MODELS` entries: `unstract-api`, `docling-serve`
- [ ] Run `mise run registry:lint` — must report 26 models / 6 backends
- [ ] Run `mise run registry:audit` — verify against the live HuggingFace Hub

## Stage 2 — BAML clients extension

- [ ] Edit `baml_src/clients.baml` — add the `Docling` and `Unstract` clients
  (per the proposal's section 2)
- [ ] Run `baml-cli generate` to regenerate the Python + TS clients
- [ ] Run `baml-cli test clients_docling` with a DocTags XML fixture
- [ ] Run `baml-cli test clients_unstract` with a Unstract JSON fixture

## Stage 3 — Ensemble extractor

- [ ] Create `meaisinfhoghlaim/ocr/ensemble/__init__.py`
- [ ] Create `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py`:
  - Class `EnsembledExtractor` with the `extract()` API
  - Async run of the 4 paths via `asyncio.gather()` (or `anyio`)
  - Per-path DuckLake landing in
    `cianfhoghlaim.education.british_isles.<jurisdiction>.<scope>.<subject>.<path>`
  - RAGAS voting via `ragas.metrics.faithfulness` + `answer_relevance` + `context_precision`
- [ ] Create the `EnsembleResult` Pydantic model
- [ ] Unit test: `mise run py:test meaisinfhoghlaim/ocr/ensemble/`
- [ ] Integration test with a real NCCA JC PDF: `mise run py:test_integration jc_mathematics_en`

## Stage 4 — Dagster asset + RAGAS harness

- [ ] Create `orchestration/defs/2_materials/ocr_comparison/ensemble_comparison/biiep_ocr_ensemble.py`
  - Dagster asset `biiep_ocr_ensemble` that calls `EnsembledExtractor.extract()`
  - Asset metadata: `row_count` + `ragas_consensus_score`
  - Asset check: `ragas_score >= 0.70` (production-grade threshold)
- [ ] Update the existing `defs.yaml` in
  `orchestration/defs/2_materials/ocr_comparison/ensemble_comparison/` to add the new asset
- [ ] Create `meaisinfhoghlaim/evaluation/__init__.py`
- [ ] Create `meaisinfhoghlaim/evaluation/ragas_biiep_ensemble.py`:
  - Registers the `biiep_extraction_consensus` RAGAS metric
  - Logs to MLflow experiment `biiep_v2`
  - Provides a CLI: `mise run ragas:biiep:ensemble --pdf=path/to.pdf`
- [ ] Run `mise run ragas:biiep:ensemble --dry-run` to verify the metric is registered

## Stage 5 — Unstract workflows

- [ ] Create `bonneagar/stacks/unstract/workflow_data/aqa_gcse_spec.json` —
  AQA GCSE spec extraction workflow (documented JSON Schema output, prompt template)
- [ ] Create `bonneagar/stacks/unstract/workflow_data/ncca_jc_cba.json` —
  NCCA JC CBA descriptor extraction workflow
- [ ] Create `bonneagar/stacks/unstract/workflow_data/sec_lc_marking.json` —
  SEC LC marking scheme extraction workflow
- [ ] For each workflow, create a sibling `prompt_studio.json` companion documenting
  the prompt template + the JSON output schema
- [ ] Run `mise run unstract:upload-workflows` to upload all 3 to the Unstract deployment

## Stage 6 — Spec delta commits + validation

- [ ] Run `openspec validate 2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1 --strict`
- [ ] Commit the change on a dedicated branch `openspec/2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1`
- [ ] Open a PR on `origin/main` referencing this change
- [ ] Run `mise run lint:skills` — must remain 53/53
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Update `docs/research/biiep_v2_ocr_ensemble_status.md` with the now-green status
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol
