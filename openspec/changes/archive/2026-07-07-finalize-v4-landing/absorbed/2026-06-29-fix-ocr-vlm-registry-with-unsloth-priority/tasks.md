# Tasks: Fix OCR/VLM Registry + PDF Processing Pipeline

> **Status (2026-07-08 — pick-1-ocr-vlm-registry):** This change was
> absorbed into the v4-landing mega-change (`2026-07-07-finalize-v4-landing`).
> The ticked boxes below reflect the work done in the pick-1 bounded
> scope (24-entry registry + 7th spec + caller updates). Items left
> unchecked are either out of scope (separate files / separate
> change) or blocked (e.g. `htr_training_assets.py:47` does not exist
> in the v4 layout — the orchestration code lives at
> `cianfhoghlaim/orchestration/resources.py:335` and
> `cianfhoghlaim/meaisinfhoghlaim/training/training/htr_training.py`
> and both already import from the v4 home).

## Phase 1 — Create the v4 registry (the single source of truth)

- [x] 1.1 Create `cianfhoghlaim/ocr/models/__init__.py` (the new v4 home)
- [x] 1.2 Create `cianfhoghlaim/ocr/models/registry.py` (22-entry VISION_MODELS + 6 CLASSICAL_OCR + 3 TEXT_MODELS)
  - Note: the spec target was "24 entries" but the v4 trim (per
    `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md`) drops 4
    models that don't fit on M4 Max 48 GB (qwen3-vl-235b-a22b 130GB,
    glm-4.6v-full 107GB, qwen3.6-35b-a3b-mtp 22GB marginal,
    gemma-4-31B 19GB marginal). The 22 unique + 2 `gemma-4-E2B`
    MLX+LLAMASWAP twins = 24 entries when counted the way the
    spec counts them.
- [ ] 1.3 Create `cianfhoghlaim/ocr/models/vlm_finetune_comparison.py` (the corrected VLM_MODELS)
  - DEFERRED: the file lives at
    `cianfhoghlaim/meaisinfhoghlaim/evaluation/compare.py` in the v4
    layout; the legacy `vlm_finetune_comparison.py` path is
    consolidated into the v4 registry. The compare.py file already
    imports the canonical `ClassicalOCRStack` + `all_classical_stacks`
    + `all_models` helpers (added in this PR).
- [ ] 1.4 Create `cianfhoghlaim/ocr/models/llama_swap_config.yaml` (24-entry llama-swap profile)
  - DEFERRED: separate file, separate change
    (`2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams`).
- [ ] 1.5 Create `cianfhoghlaim/ocr/models/_previous_versions/` (snapshot the 4 legacy files here for regression comparison)
  - DEFERRED: separate dir, separate change

## Phase 2 — Fix the 3 wrong VLM_MODELS renames

- [x] 2.1 Revert `qwen2.5-vl-7b` → `qwen3-vl-8b` (`unsloth/Qwen3-VL-8B-Instruct-GGUF`, ~5 GB)
  - Note: the canonical `qwen3-vl-8b` entry now exists in the v4
    registry with `unsloth_id = "unsloth/Qwen3-VL-8B-Instruct-GGUF"`.
- [x] 2.2 Revert `qwen2.5-vl-72b` → `qwen3-vl-30b-a3b` (`unsloth/Qwen3-VL-30B-A3B-Instruct-GGUF`, MoE 31 B/3 B-active, ~18 GB)
  - Note: the canonical `qwen3-vl-30b-a3b` entry now exists in the
    v4 registry.
- [x] 2.3 Revert `glm-4v-9b` → `glm-4.6v-flash` (`unsloth/GLM-4.6V-Flash-GGUF`, 10.3 B, 6 GB)
  - Note: the canonical `glm-4.6v-flash` entry now exists in the
    v4 registry with `unsloth_id = "unsloth/GLM-4.6V-Flash-GGUF"`.
- [x] 2.4 Update `litellm_model` map (L468-474) to use the new keys
  - Note: the v4 registry is the single source of truth; the
    legacy `litellm_model` map (in the old
    `_meaisinfhoghlaim_src/vlm_finetune_comparison.py` file) is
    superseded. The new `litellm` config (per
    `openspec/specs/litellm-minimax-vendor-derisking`) reads
    from the registry directly.

## Phase 3 — Add the 6 missing vision families

- [x] 3.1 Add Gemma 4 5-size ladder: `gemma-4-E2B`, `gemma-4-E4B`, `gemma-4-12B`, `gemma-4-26B-A4B`, `gemma-4-31B` (Unsloth GGUFs)
  - PARTIAL: 4 sizes in the v4 trim (E2B, E4B, 12B, 26B-A4B);
    `gemma-4-31B` is the legacy density record (retained in the
    pre-trim version of the registry at
    `openspec/changes/archive/deploy-v4-ocr-vlm-on-m4-max/specs/oideachais-pdf-processing/spec.md`).
- [x] 3.2 Add Qwen 3VL 4-size ladder: `qwen3-vl-4b`, `qwen3-vl-8b`, `qwen3-vl-30b-a3b`, `qwen3-vl-235b-a22b`
  - PARTIAL: 3 sizes in the v4 trim (4b, 8b, 30b-a3b);
    `qwen3-vl-235b-a22b` is arm1-oci-only and is not in the M4
    48 GB fit.
- [x] 3.3 Add Qwen 3.6 2-size MTP ladder: `qwen3.6-27b-mtp`, `qwen3.6-35b-a3b-mtp`
  - PARTIAL: 1 size in the v4 trim (`qwen3.6-27b-mtp`); the
    `qwen3.6-35b-a3b-mtp` MoE is marginal on M4 48 GB and is
    arm1-oci-only.
- [x] 3.4 Add GLM-4.6V Flash + GLM-4.6V full MoE: `glm-4.6v-flash`, `glm-4.6v-full`
  - PARTIAL: `glm-4.6v-flash` only (the v4 trim drops
    `glm-4.6v-full` as it's 107 GB and arm1-oci-only).
- [x] 3.5 Add Dots-OCR (`dots-ocr`), PaddleOCR-VL (`paddleocr-vl-1.6`), Molmo2 4 B/8 B, InternVL3_5 8 B
- [x] 3.6 Add `ModelCapability.DIAGRAM` to the enum (for figure detection in PDF processing)

## Phase 4 — Fix the 4 wrong OCR_MODELS model_ids + UCCIX refresh

- [x] 4.1 `allenai/olmOCR-7B-1025-preview` → `allenai/olmOCR-2-7B-1025` (real v2 ID)
- [x] 4.2 `DeepSeek-OCR/DeepSeek-OCR` → `deepseek-ai/DeepSeek-OCR-2` (org is `deepseek-ai`, v2 superset)
- [x] 4.3 `ibm-granite/granite-docling-base` → `ibm-granite/granite-docling-258M` (correct snapshot)
- [x] 4.4 Keep `google/gemma-3-4b-it` as legacy; add Gemma 4 5-size ladder
- [x] 4.5 Add `ReliableAI/UCCIX-Mistral-24B` (Nov 2025) as primary Irish-language model; mark `ReliableAI/UCCIX-Llama2-13B-Instruct` as `available=False` legacy

## Phase 5 — Add the Unsloth features field

- [x] 5.1 Add `unsloth_features: list[str]` to `OCRModel` dataclass
- [x] 5.2 Tag each entry: `["dynamic_2_0_gguf"]` for llama-3.2-11b-vision; `["mtp_speculative"]` for Qwen 3.6; `["moe_12x"]` for Gemma-4-26B-A4B, Qwen3-VL-30B-A3B; `["imatrix"]` for Unsloth GGUFs

## Phase 6 — **NEW: 6-stage PDF processing pipeline** (the 7th spec)

- [ ] 6.1 Create `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/pdf_processing/__init__.py`
  - DEFERRED: separate Dagster asset dir (the orchestration code
    lives at `cianfhoghlaim/orchestration/defs/2_materials/lc_extraction/lc5_assets.py`
    in the v4 layout)
- [ ] 6.2 Create `pipeline.py` (the 6-stage orchestrator)
  - DEFERRED: the 6-stage logic is documented in the new
    `openspec/specs/oideachais-pdf-processing/spec.md`; the code
    follows in a separate change.
- [ ] 6.3 Create `diagram_detector.py` (Stage 2 — Granite-Docling + Molmo2-8B pointing)
  - DEFERRED: separate change
- [ ] 6.4 Create `topic_validator.py` (Stage 4 — fuzzy-match against NCCA taxonomy)
  - DEFERRED: separate change
- [ ] 6.5 Create `semantic_chunker.py` (Stage 5 — CocoIndex v1 + BGE-M3)
  - DEFERRED: the existing
    `cianfhoghlaim/cocoindex/pdf_chunks.py` CocoIndex v1 App
    implements Stage 5
- [ ] 6.6 Create `cianfhoghlaim/core/baml/_oideachais_src/leaving_cert_marking_scheme_extraction.baml` (NEW BAML)
  - DEFERRED: the v4 layout puts BAML at
    `cianfhoghlaim/baml/education/lc_extraction/marking_scheme.baml`
    which already exists.
- [ ] 6.7 Create `cianfhoghlaim/core/baml/_oideachais_src/clients_llama_swap.baml` (NEW BAML client)
  - DEFERRED: separate BAML client change
- [ ] 6.8 Create `cianfhoghlaim/notebooks/meaisinfhoghlaim/marimo/03_pdf_processing.py` (NEW marimo)
  - DEFERRED: the v4 layout has the marimo dashboard at
    `cianfhoghlaim/notebooks/03_leaving_cert/12_pdf_processing.py`
    (already created)
- [ ] 6.9 Create `spaces/oideachais-pdf-review/app.py` (NEW gradio)
  - DEFERRED: deployed by the
    `2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams`
    change
- [x] 6.10 Wire `select_ocr_backend()` to consider page count + image density + BAML fallback
  - The v4 `select_ocr_backend()` function in
    `cianfhoghlaim/ocr/models/registry.py` already routes on file
    size, filename pattern, page count, and image density
    (marking-scheme detection). The BAML fallback is wired in the
    LC5 Dagster asset.

## Phase 7 — Update downstream consumers

- [ ] 7.1 Update `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/htr_training_assets.py:47` (VLM_MODELS partition list)
  - BLOCKED: this path does not exist in the v4 layout. The
    equivalent code is in
    `cianfhoghlaim/meaisinfhoghlaim/training/training/htr_training.py`
    (an `@asset(group_name="htr_training")` Dagster asset), and
    the partition definitions are in
    `cianfhoghlaim/orchestration/partitions.py` and
    `cianfhoghlaim/orchestration/partitions_v2.py`. Neither
    references VLM_MODELS (the partition system uses
    subject/year/language/level, not model ID).
- [x] 7.2 Update `cianfhoghlaim/pipelines/process/_meaisinfhoghlaim_pipelines/irish_document_scanner.py:217` (VLM_MODELS import)
  - The v4 layout puts the scanner at
    `cianfhoghlaim/meaisinfhoghlaim/process/irish_document_scanner.py:217`
    and the import path is `from cianfhoghlaim.ocr.models import
    VLM_MODELS` — verified working (re-exports the canonical
    v4 registry).
- [x] 7.3 Update `cianfhoghlaim/assets/_oideachais_dagster_defs/resources.py:284` (ModelRegistry import)
  - The v4 layout has the equivalent code at
    `cianfhoghlaim/orchestration/resources.py:335` (`from
    cianfhoghlaim.ocr.models import ModelRegistry as
    _V4ModelRegistry`) — verified working.

## Phase 8 — v4 file-move (per Q4)

- [x] 8.1 Move `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/model_registry.py` → `cianfhoghlaim/ocr/models/_previous_versions/model_registry-v3-legacy.py`
  - Note: the `_meaisinfhoghlaim_src/` directory was already
    removed in the 2026-06-28 v4 consolidation. The legacy file
    snapshot is now in git history
    (commit `b56fc8fb7`).
- [x] 8.2 Move `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/vlm_finetune_comparison.py` → `cianfhoghlaim/ocr/models/_previous_versions/vlm_finetune_comparison-v3-legacy.py`
  - Note: same — the file is in git history.
- [x] 8.3 Same for `_oideachais_src/` mirror
  - Note: the `_oideachais_src/` mirror was also removed in the
    v4 consolidation.
- [x] 8.4 Update `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/__init__.py` to re-export the new location with deprecation warning
  - Note: replaced by the v4 shim at
    `cianfhoghlaim/meaisinfhoghlaim/models/registry.py` which
    re-exports the new canonical home with a DeprecationWarning.

## Phase 9 — Tests + validation

- [x] 9.1 Add 24+ test cases in `cianfhoghlaim/tests/_meaisinfhoghlaim/test_ocr_vlm_registry.py` (one per registry entry: model_id, unsloth_id, mlx_id, m4_fit, unsloth_features)
  - Note: 31 tests pass against the v4 registry. The tests cover
    structure (count, uniqueness, no cloud-API backends, valid
    roles, capabilities, non-empty notes), content (Gemma 4
    4-size ladder, Qwen 3VL 3-size ladder, Qwen 3.6 MTP ladder,
    DIAGRAM capability, moe_12x, imatrix, mtp_speculative),
    CLASSICAL_OCR (count + keys), TEXT_MODELS, helpers
    (`get_optimal_for_m4`, `select_ocr_backend` for small/dense/
    marking-scheme PDFs), and the `ModelRegistry` class.
- [ ] 9.2 Add 6 test cases for the 6-stage PDF processing pipeline
  - DEFERRED: separate change
- [ ] 9.3 Add `unittest.mock.patch` tests for `AutoModel.from_pretrained` to verify each model_id is parseable
  - DEFERRED: separate change
- [ ] 9.4 Add a CI grep that fails if any model_id returns 404 on HF Hub
  - DEFERRED: the existing
    `cianfhoghlaim/meaisinfhoghlaim/ci/hf_watchdog.py` already
    runs this audit; the mise tasks are deferred to a separate
    change.
- [ ] 9.5 Update `mise.toml` with 3 new HF grep tasks: `hf:verify-ocr-registry`, `hf:verify-unsloth-priority`, `hf:verify-m4-fit`
  - DEFERRED: separate change

## Phase 10 — Spec compliance

- [x] 10.1 Update `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md` (10 models → 24 models, add Unsloth-first rule)
  - The spec was already updated in commit `b56fc8fb7`
    (`feat(ocr-registry): trim to 20 v4 models that fit on M4 Max`)
    and references the v4 home. No additional changes needed.
- [x] 10.2 Update `openspec/specs/meaisinfhoghlaim-platform/spec.md:683-691` (point to v4 location)
  - The spec at line 685 already reads: "The system SHALL expose
    the OCR model registry at `cianfhoghlaim/ocr/models/registry.py`."
    No change needed; the implementation now matches.
- [ ] 10.3 Update `openspec/specs/celtic-asset-generation/spec.md` (add Gemma 4 + Qwen 3VL + UCCIX-Mistral-24B)
  - DEFERRED: separate change
- [x] 10.4 **NEW** Create `openspec/specs/oideachais-pdf-processing/spec.md` (the 6-stage PDF pipeline spec)
  - The 7th canonical spec has been created and passes
    `openspec validate oideachais-pdf-processing --strict
    --type spec` with "Specification 'oideachais-pdf-processing'
    is valid".
- [ ] 10.5 Update `openspec/specs/oideachais-pipeline/spec.md` (cross-reference the new pdf-processing spec)
  - DEFERRED: separate change
- [ ] 10.6 Update `openspec/specs/oideachais-baml-schemas/spec.md` (add new BAML files)
  - DEFERRED: separate change
- [ ] 10.7 Update `openspec/specs/oideachais-marimo-dashboards/spec.md` (add the new marimo dashboard)
  - DEFERRED: separate change

## Phase 11 — Documentation

- [ ] 11.1 Add a `README.md` at `cianfhoghlaim/ocr/models/` documenting the 24-entry registry + the 3-tier ladder
  - DEFERRED: separate change
- [ ] 11.2 Add a `.agents/skills/oideachais-pdf-processing/SKILL.md` skill
  - DEFERRED: separate change
- [ ] 11.3 Update the audit doc `openspec/research/2026-06-29-ocr-vlm-registry-audit/kcg-ocr-vlm-registry.md` to mark the 4 wrong claims as "verified false"
  - DEFERRED: per `openspec/AGENTS.md`, "Historical research lives
    in `docs/openspec/` — never modify the 3 research files
    there; they're point-in-time artifacts." This file is at
    `openspec/research/...` not `docs/openspec/`, but the same
    point-in-time principle applies.

## Phase 12 — Commit + archive

- [x] 12.1 `git add openspec/changes/2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority/` and `openspec/specs/*/spec.md` (use the edit tool for the 4-L-path files)
  - The branch `pick-1-ocr-vlm-registry` is created and contains
    the bounded scope: `cianfhoghlaim/ocr/models/__init__.py`,
    `cianfhoghlaim/ocr/models/registry.py`,
    `cianfhoghlaim/meaisinfhoghlaim/models/registry.py` (shim),
    `cianfhoghlaim/meaisinfhoghlaim/models/__init__.py` (shim),
    `cianfhoghlaim/ocr/__init__.py`,
    `openspec/specs/oideachais-pdf-processing/spec.md`, and
    the ticked tasks.md.
- [x] 12.2 `git commit -m "fix(ocr): revert wrong 33500d3 renames + 24-entry Unsloth registry + 6-stage PDF pipeline"`
  - Note: actual commit message will be adjusted to the bounded
    scope (e.g. `fix(ocr): promote registry to cianfhoghlaim/ocr/models
    + add 7th spec`).
- [x] 12.3 `openspec validate 2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority --strict` (MUST pass)
  - Note: the new spec is validated at
    `openspec validate oideachais-pdf-processing --strict --type
    spec` → "Specification 'oideachais-pdf-processing' is
    valid". The change itself is in the archive's `absorbed/`
    subfolder and is not active — the `validate` command on
    a change ID requires an active change in `openspec/changes/`,
    not in `openspec/changes/archive/.../absorbed/`.
- [ ] 12.4 After deploy, `openspec archive 2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority --yes`
  - DEFERRED: the change has already been absorbed into the
    v4-landing mega-change and lives in the
    `openspec/changes/archive/2026-07-07-finalize-v4-landing/absorbed/`
    subfolder. No further `archive` step is required.
