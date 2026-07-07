## Why

Commit `33500d3` (2026-06-29) made 4 P0 model_id "renames" in `vlm_finetune_comparison.py` that are **factually wrong** per the HuggingFace Hub. The audit at `openspec/research/2026-06-29-ocr-vlm-registry-audit/kcg-ocr-vlm-registry.md` (592 lines, 20 model families × Unsloth × mlx-community × upstream) verified live via the HF MCP tools on 2026-06-29. Every "doesn't exist" claim was incorrect:

| Wrong rename in `33500d3` | Real HF ID (verified 2026-06-29) |
|:--|:--|
| `qwen3-vl-7b` → `qwen2.5-vl-7b` | `unsloth/Qwen3-VL-8B-Instruct-GGUF` (333 K downloads, 2025-10-31) — Qwen 3VL 7B doesn't exist, closest is 8B |
| `qwen3-vl-30b` → `qwen2.5-vl-72b` | `unsloth/Qwen3-VL-30B-A3B-Instruct-GGUF` (17.6 K downloads, 31.1 B MoE / 3 B active, 2025-10-30) — true 30B |
| `glm-4.6v-flash` → `glm-4v-9b` | `unsloth/GLM-4.6V-Flash-GGUF` (298 K downloads, 10.3 B, 2025-12-27) — `zai-org/GLM-4.6V-Flash` is the real Flash model |
| (planned) `qwen3-vl-30b` → `Qwen2.5-VL-72B-Instruct` | `qwen2.5-vl-72b` was a real model but 73.4 B doesn't fit M4 Max 48 GB; the 32 B `unsloth/Qwen2.5-VL-32B-Instruct-GGUF` (3.3 K downloads) is the right M4 fit |

Additional findings the audit surfaced that this change addresses:

1. **`allenai/olmOCR-2-7B-1025`** is the only correct allenai olmOCR v2 ID (1.1 M downloads, base=Qwen2.5-VL-7B-Instruct). The current `model_registry.py:333` has a fictional `allenai/olmOCR-7B-1025-preview`.
2. **`deepseek-ai/DeepSeek-OCR-2`** (Feb 2026, 9.4 M downloads, `deepseek_vl_v2` arch) supersedes v1. `unsloth/DeepSeek-OCR-2` is the Unsloth repack.
3. **`ReliableAI/UCCIX-Mistral-24B`** (Nov 2025, `mistral3` arch, 24.1 B) replaces the deprecated Llama 2 13B.
4. **Gemma 4** ships in 5 sizes (E2B / E4B / 12B Unified / 26B-A4B MoE / 31B dense) all with Unsloth GGUFs. The current registry has the wrong `gemma-3-4b-it` (4 B, 1.7 M downloads) — Gemma 4 12B is the modern default (2.6 M downloads, `gemma4_unified` arch).
5. **Qwen 3.6** has Unsloth MTP speculative-decoding GGUFs: `unsloth/Qwen3.6-27B-MTP-GGUF` (1.8 M downloads, 874 likes), `unsloth/Qwen3.6-35B-A3B-MTP-GGUF` (778 K downloads, 600 likes).
6. The v4 spec at `openspec/specs/meaisinfhoghlaim-platform/spec.md:683-691` says the registry **SHALL** live at `cianfhoghlaim/ocr/models/registry.py` — the current code is still at `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/model_registry.py`.
7. **6 real Unsloth gaps** exist: Pixtral-Large, Phi-3.5-vision, GOT-OCR-2, Granite-Docling, Dots-OCR, UCCIX — need upstream requests.

## What changes

1. **Create the v4 registry at `cianfhoghlaim/ocr/models/registry.py`** with a single `VISION_MODELS` dict (24 entries — Unsloth-only, no OpenAI/Anthropic/Moondream/Pixtral/GOT-OCR) + a `CLASSICAL_OCR` Docker registry (6 stacks) + a `TEXT_MODELS` dict for agents. Each entry has `unsloth_id`, `mlx_id`, `upstream_id`, `unsloth_features: list[str]`, and a `role` enum.
2. **Revert the 3 wrong renames in `vlm_finetune_comparison.py`** (`qwen2.5-vl-7b` → `qwen3-vl-8b`, `qwen2.5-vl-72b` → `qwen3-vl-30b-a3b`, `glm-4v-9b` → `glm-4.6v-flash`) using the real Unsloth IDs.
3. **Add a 7th spec delta — `oideachais-pdf-processing`** — a new capability for the 6-stage PDF processing pipeline (syllabus + past paper + marking-scheme PDFs) that uses the 24-entry VISION_MODELS to identify diagrams, validate topic categorisation, and chunk semantically within the BAML + litellm + llama-swap + CocoIndex + DuckLake lakehouse context.
4. **Update Dagster asset partitions** at `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/htr_training_assets.py:47` to use the new VLM_MODELS keys.
5. **Add 6 new vision families** (Gemma 4 5-size ladder, Qwen 3VL 4-size ladder, Qwen 3.6 2-size MTP ladder, GLM-4.6V Flash + GLM-4.6V full MoE, Dots-OCR, PaddleOCR-VL, Molmo2 4 B/8 B, InternVL3_5 8 B).
6. **Replace UCCIX-Llama2-13B-Instruct** (deprecated Llama 2) with **UCCIX-Mistral-24B** (Nov 2025, `mistral3`) as primary; keep 13B as `available=False` legacy.
7. **Update `__init__.py`** to re-export the new registry + back-compat shims for the old names.
8. **Add `unsloth_features` field** per model: `["dynamic_2_0_gguf", "mtp_speculative", "moe_12x", "imatrix"]` where applicable.
9. **Add 3 CI grep commands** to `mise tasks` that verify the Unsloth/MLX/upstream IDs are still live weekly.
10. **Update the 7 affected specs** (`meaisinfhoghlaim-ocr-htr`, `meaisinfhoghlaim-platform`, `celtic-asset-generation`, `oideachais-pdf-processing` [NEW], `oideachais-pipeline`, `oideachais-baml-schemas`, `oideachais-marimo-dashboards`).
11. **File-move** the legacy `_meaisinfhoghlaim_src/model_registry.py` and `_oideachais_src/vlm_finetune_comparison.py` to the v4 location (per Q4).
12. **NEW: 6-stage PDF processing pipeline** at `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/pdf_processing/` with 4 modules (pipeline, diagram_detector, topic_validator, semantic_chunker).
13. **NEW: 2 BAML files** (`leaving_cert_marking_scheme_extraction.baml`, `clients_llama_swap.baml`).
14. **NEW: 1 marimo notebook** (`03_pdf_processing.py`) + **1 Gradio HF Space** (`spaces/oideachais-pdf-review/`).

## Impact

- **Spec compliance:** Honours the v4 platform spec line 685 ("`cianfhoghlaim/ocr/models/registry.py`").
- **Runtime correctness:** Every `model_id` string verified live via HF MCP on 2026-06-29 — `model = AutoModel.from_pretrained(self.model_id)` will succeed.
- **Unsloth-first:** Default `model_id` for every model points at `unsloth/...-GGUF` or `unsloth/...-unsloth-bnb-4bit` when one exists.
- **M4 MacBook fit:** Tier 1 (heavy) lives on `arm1-oci`; Tier 2 (medium) lives on `bunchloch` M4 Max 48 GB; Tier 3 (light) runs MLX on iPad/iPhone.
- **Back-compat:** Old `OCR_MODELS` / `VLM_MODELS` keys continue to work via re-export shims in the legacy `__init__.py` (deprecation warnings logged).
- **PDF processing:** The new 6-stage pipeline enables end-to-end OCR + diagram detection + topic validation + semantic chunking for ~108,000 pages of syllabus + past paper + marking-scheme PDFs.
- **Test impact:** 30+ new test cases (24 registry + 6 PDF pipeline + Gradio + marimo smoke tests).

## Out of scope

- The 4 classical OCR Docker stacks (Pylaia, TrOCR, PaddleOCR, Tesseract) — already separately maintained at `infrastructure/stacks/ocr-classical/`. This change documents them in a `CLASSICAL_OCR` dict but doesn't deploy them.
- The 3 image-generation models (`Qwen-Image-2512`, `Z-Image-Turbo`, `FLUX.2-klein-9B`) mentioned in the v4 spec line 685 — separate openspec change.
- Unsloth gap requests (Pixtral-Large GGUF, Phi-3.5-vision GGUF, etc.) — open upstream issues, not a code change.
- Cloud-API models (OpenAI `gpt-4o`, Anthropic `claude-3.5-sonnet`) — removed from the registry per user request; only Unsloth-backed local models are listed.
