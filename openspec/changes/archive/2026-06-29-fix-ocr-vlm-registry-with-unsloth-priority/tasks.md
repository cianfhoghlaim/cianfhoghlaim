# Tasks: Fix OCR/VLM Registry + PDF Processing Pipeline

## Phase 1 — Create the v4 registry (the single source of truth)

- [ ] 1.1 Create `cianfhoghlaim/ocr/models/__init__.py` (the new v4 home)
- [ ] 1.2 Create `cianfhoghlaim/ocr/models/registry.py` (24-entry VISION_MODELS + CLASSICAL_OCR + TEXT_MODELS)
- [ ] 1.3 Create `cianfhoghlaim/ocr/models/vlm_finetune_comparison.py` (the corrected VLM_MODELS)
- [ ] 1.4 Create `cianfhoghlaim/ocr/models/llama_swap_config.yaml` (24-entry llama-swap profile)
- [ ] 1.5 Create `cianfhoghlaim/ocr/models/_previous_versions/` (snapshot the 4 legacy files here for regression comparison)

## Phase 2 — Fix the 3 wrong VLM_MODELS renames

- [ ] 2.1 In new `vlm_finetune_comparison.py`: revert `qwen2.5-vl-7b` → `qwen3-vl-8b` (`unsloth/Qwen3-VL-8B-Instruct-GGUF`, ~5 GB)
- [ ] 2.2 In new `vlm_finetune_comparison.py`: revert `qwen2.5-vl-72b` → `qwen3-vl-30b-a3b` (`unsloth/Qwen3-VL-30B-A3B-Instruct-GGUF`, MoE 31 B/3 B-active, ~18 GB)
- [ ] 2.3 In new `vlm_finetune_comparison.py`: revert `glm-4v-9b` → `glm-4.6v-flash` (`unsloth/GLM-4.6V-Flash-GGUF`, 10.3 B, 6 GB)
- [ ] 2.4 Update `litellm_model` map (L468-474) to use the new keys

## Phase 3 — Add the 6 missing vision families

- [ ] 3.1 Add Gemma 4 5-size ladder: `gemma-4-E2B`, `gemma-4-E4B`, `gemma-4-12B`, `gemma-4-26B-A4B`, `gemma-4-31B` (Unsloth GGUFs)
- [ ] 3.2 Add Qwen 3VL 4-size ladder: `qwen3-vl-4b`, `qwen3-vl-8b`, `qwen3-vl-30b-a3b`, `qwen3-vl-235b-a22b`
- [ ] 3.3 Add Qwen 3.6 2-size MTP ladder: `qwen3.6-27b-mtp`, `qwen3.6-35b-a3b-mtp`
- [ ] 3.4 Add GLM-4.6V Flash + GLM-4.6V full MoE: `glm-4.6v-flash`, `glm-4.6v-full`
- [ ] 3.5 Add Dots-OCR (`dots-ocr`), PaddleOCR-VL (`paddleocr-vl-1.6`), Molmo2 4 B/8 B, InternVL3_5 8 B
- [ ] 3.6 Add `ModelCapability.DIAGRAM` to the enum (for figure detection in PDF processing)

## Phase 4 — Fix the 4 wrong OCR_MODELS model_ids + UCCIX refresh

- [ ] 4.1 `allenai/olmOCR-7B-1025-preview` → `allenai/olmOCR-2-7B-1025` (real v2 ID)
- [ ] 4.2 `DeepSeek-OCR/DeepSeek-OCR` → `deepseek-ai/DeepSeek-OCR-2` (org is `deepseek-ai`, v2 superset)
- [ ] 4.3 `ibm-granite/granite-docling-base` → `ibm-granite/granite-docling-258M` (correct snapshot)
- [ ] 4.4 Keep `google/gemma-3-4b-it` as legacy; add Gemma 4 5-size ladder
- [ ] 4.5 Add `ReliableAI/UCCIX-Mistral-24B` (Nov 2025) as primary Irish-language model; mark `ReliableAI/UCCIX-Llama2-13B-Instruct` as `available=False` legacy

## Phase 5 — Add the Unsloth features field

- [ ] 5.1 Add `unsloth_features: list[str]` to `OCRModel` dataclass
- [ ] 5.2 Tag each entry: `["dynamic_2_0_gguf"]` for llama-3.2-11b-vision; `["mtp_speculative"]` for Qwen 3.6; `["moe_12x"]` for Gemma-4-26B-A4B, Qwen3-VL-30B-A3B, Qwen3.6-35B-A3B; `["imatrix"]` for Unsloth GGUFs

## Phase 6 — **NEW: 6-stage PDF processing pipeline** (the 7th spec)

- [ ] 6.1 Create `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/pdf_processing/__init__.py`
- [ ] 6.2 Create `pipeline.py` (the 6-stage orchestrator)
- [ ] 6.3 Create `diagram_detector.py` (Stage 2 — Granite-Docling + Molmo2-8B pointing)
- [ ] 6.4 Create `topic_validator.py` (Stage 4 — fuzzy-match against NCCA taxonomy)
- [ ] 6.5 Create `semantic_chunker.py` (Stage 5 — CocoIndex v1 + BGE-M3)
- [ ] 6.6 Create `cianfhoghlaim/core/baml/_oideachais_src/leaving_cert_marking_scheme_extraction.baml` (NEW BAML)
- [ ] 6.7 Create `cianfhoghlaim/core/baml/_oideachais_src/clients_llama_swap.baml` (NEW BAML client)
- [ ] 6.8 Create `cianfhoghlaim/notebooks/meaisinfhoghlaim/marimo/03_pdf_processing.py` (NEW marimo)
- [ ] 6.9 Create `spaces/oideachais-pdf-review/app.py` (NEW gradio)
- [ ] 6.10 Wire `select_ocr_backend()` to consider page count + image density + BAML fallback

## Phase 7 — Update downstream consumers

- [ ] 7.1 Update `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/htr_training_assets.py:47` (VLM_MODELS partition list)
- [ ] 7.2 Update `cianfhoghlaim/pipelines/process/_meaisinfhoghlaim_pipelines/irish_document_scanner.py:217` (VLM_MODELS import)
- [ ] 7.3 Update `cianfhoghlaim/assets/_oideachais_dagster_defs/resources.py:284` (ModelRegistry import)

## Phase 8 — v4 file-move (per Q4)

- [ ] 8.1 Move `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/model_registry.py` → `cianfhoghlaim/ocr/models/_previous_versions/model_registry-v3-legacy.py`
- [ ] 8.2 Move `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/vlm_finetune_comparison.py` → `cianfhoghlaim/ocr/models/_previous_versions/vlm_finetune_comparison-v3-legacy.py`
- [ ] 8.3 Same for `_oideachais_src/` mirror
- [ ] 8.4 Update `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/__init__.py` to re-export the new location with deprecation warning

## Phase 9 — Tests + validation

- [ ] 9.1 Add 24+ test cases in `cianfhoghlaim/tests/_meaisinfhoghlaim/test_ocr_vlm_registry.py` (one per registry entry: model_id, unsloth_id, mlx_id, m4_fit, unsloth_features)
- [ ] 9.2 Add 6 test cases for the 6-stage PDF processing pipeline
- [ ] 9.3 Add `unittest.mock.patch` tests for `AutoModel.from_pretrained` to verify each model_id is parseable
- [ ] 9.4 Add a CI grep that fails if any model_id returns 404 on HF Hub
- [ ] 9.5 Update `mise.toml` with 3 new HF grep tasks: `hf:verify-ocr-registry`, `hf:verify-unsloth-priority`, `hf:verify-m4-fit`

## Phase 10 — Spec compliance

- [ ] 10.1 Update `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md` (10 models → 24 models, add Unsloth-first rule)
- [ ] 10.2 Update `openspec/specs/meaisinfhoghlaim-platform/spec.md:683-691` (point to v4 location)
- [ ] 10.3 Update `openspec/specs/celtic-asset-generation/spec.md` (add Gemma 4 + Qwen 3VL + UCCIX-Mistral-24B)
- [ ] 10.4 **NEW** Create `openspec/specs/oideachais-pdf-processing/spec.md` (the 6-stage PDF pipeline spec)
- [ ] 10.5 Update `openspec/specs/oideachais-pipeline/spec.md` (cross-reference the new pdf-processing spec)
- [ ] 10.6 Update `openspec/specs/oideachais-baml-schemas/spec.md` (add new BAML files)
- [ ] 10.7 Update `openspec/specs/oideachais-marimo-dashboards/spec.md` (add the new marimo dashboard)

## Phase 11 — Documentation

- [ ] 11.1 Add a `README.md` at `cianfhoghlaim/ocr/models/` documenting the 24-entry registry + the 3-tier ladder
- [ ] 11.2 Add a `.agents/skills/oideachais-pdf-processing/SKILL.md` skill
- [ ] 11.3 Update the audit doc `openspec/research/2026-06-29-ocr-vlm-registry-audit/kcg-ocr-vlm-registry.md` to mark the 4 wrong claims as "verified false"

## Phase 12 — Commit + archive

- [ ] 12.1 `git add openspec/changes/2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority/` and `openspec/specs/*/spec.md` (use the edit tool for the 4-L-path files)
- [ ] 12.2 `git commit -m "fix(ocr): revert wrong 33500d3 renames + 24-entry Unsloth registry + 6-stage PDF pipeline"`
- [ ] 12.3 `openspec validate 2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority --strict` (MUST pass)
- [ ] 12.4 After deploy, `openspec archive 2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority --yes`
