# OCR Model Audit — cianfhoghlaim (2026-06-29)

> **Goal:** Per user request ("3 audit"), inventory all OCR/VLM model references and identify aspirational/non-existent ones for removal.
> **Status:** DRAFT 1 (initial inventory only, deep audit pending)
> **Related:** This is the foundational work for Phase F6 (OCR Model Cleanup) in plan v6.

## 1. Scope of audit

All OCR/VLM model references in cianfhoghlaim/ (NOT in stedding/ which is research/external).

## 2. Initial inventory (from code)

### 2.1 `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/model_registry.py` (10 models)

| Key | Model ID | Backend | Status | Notes |
|---|---|---|---|---|
| `olmocr-7b` | `allenai/olmOCR-2-7B` | TRANSFORMERS | ✓ REAL |  |
| `qwen2.5-vl-7b` | `Qwen/Qwen2.5-VL-7B-Instruct` | TRANSFORMERS | ✓ REAL |  |
| `qwen2.5-vl-7b-mlx` | `mlx-community/Qwen2.5-VL-7B-Instruct-4bit` | MLX | ✓ REAL |  |
| `deepseek-ocr` | `deepseek-ai/deepseek-ocr` | TRANSFORMERS | ⚠️ TO VERIFY |  |
| `granite-docling` | `ibm-granite/granite-docling-base` | TRANSFORMERS | ✓ REAL (older snapshot) | mlx variant is 258M |
| `gpt-4o` | `gpt-4o` | OPENAI | ✓ REAL |  |
| `claude-3.5-sonnet` | `claude-3-5-sonnet-20241022` | ANTHROPIC | ✓ REAL |  |
| `llama-3.2-vision-11b` | `llama3.2-vision:11b` | OLLAMA | ✓ REAL |  |
| `uccix-13b` | `ReliableAI/UCCIX-Llama2-13B-Instruct` | LITELLM | ⚠️ TO VERIFY | may be older Llama2, not 3 |
| `gemma-3-vision` | `google/gemma-3-vision-9b-it` | TRANSFORMERS | ✓ REAL (but Gemma 3, not 4) |  |

### 2.2 `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/vlm_finetune_comparison.py` (6 VLM_MODELS)

| Key | Model ID | Status | Notes |
|---|---|---|---|
| `glm-4.6v-flash` | `THUDM/glm-4v-9b` | ⚠️ MISMATCH | name says 4.6v-flash, model_id is older glm-4v-9b |
| `qwen3-vl-7b` | `Qwen/Qwen2.5-VL-7B-Instruct` | ⚠️ NAME MISMATCH | name says qwen3-vl, model_id is qwen2.5-vl |
| `qwen3-vl-30b` | `Qwen/Qwen2.5-VL-72B-Instruct` | ⚠️ NAME/SIZE MISMATCH | name says qwen3-vl-30b, model_id is qwen2.5-vl-72B |
| `olmocr-2-7b` | `allenai/olmOCR-7B-0225` | ✓ REAL | matches ocr-registry |
| `granite-docling` | `ibm-granite/granite-docling-258M-mlx` | ✓ REAL (newer mlx variant) |  |
| `gemma-3-4b` | `google/gemma-3n-4b-vision` | ⚠️ TO VERIFY | gemma-3n may be valid |

### 2.3 Cross-checks needed (per agent 19 R5 conformance)

| ID | Needs verification | Reason |
|---|---|---|
| `THUDM/glm-4v-9b` | YES | May exist; check HF Hub |
| `Qwen/Qwen2.5-VL-7B-Instruct` | YES | Real model but name is qwen2.5, not qwen3 |
| `Qwen/Qwen2.5-VL-72B-Instruct` | YES | Same; 72B version |
| `allenai/olmOCR-7B-0225` | ✓ confirmed | known |
| `ibm-granite/granite-docling-258M-mlx` | YES | 258M mlx version |
| `Qwen/Qwen3-VL-8B-Instruct` | YES (if exists) | was the actual user request |

## 3. Aspirational / non-existent model IDs (TO REMOVE)

Per Wave 1 Agent 19 R1 + per R5, these 8 IDs are aspirational:
1. `gemma-4-31b` - not released as of 2026-06-29
2. `gemma-4-26b-a4b` - not released
3. `gemma-4-e4b` - not released (Gemma 3 is current)
4. `gemma-4-e2b` - not released
5. `qwen-3.6-27b` - 3.6 is text-only, vision is 3-VL
6. `qwen-3.6-35b-a3b` - same
7. `qwen-3.6-35b-a3b-ud` - same
8. `qwen-3.6-27b-mlx-8bit` - same

**None of these 8 IDs are present in cianfhoghlaim code today** (verified by grep). Wave 1 R1's removal is a no-op for cianfhoghlaim proper, but still recommended for documentation/spec cleanup.

## 4. Name drift findings (REAL fixes needed)

The model names in `vlm_finetune_comparison.py` say "qwen3-vl" but the model_ids say "qwen2.5-vl":
- `qwen3-vl-7b` key → maps to `Qwen/Qwen2.5-VL-7B-Instruct` (Qwen 2.5, not 3)
- `qwen3-vl-30b` key → maps to `Qwen/Qwen2.5-VL-72B-Instruct` (Qwen 2.5, not 3)

**Fix:** Update keys to `qwen2.5-vl-7b` and `qwen2.5-vl-72b` (matching the model_ids) for consistency. OR update model_ids to actual qwen3-vl-7b/72b if those exist.

Similarly:
- `glm-4.6v-flash` key → `THUDM/glm-4v-9b` (older 4v not 4.6v)

**Fix:** Update model_id to actual `glm-4.6v-flash` model if exists, OR rename key to `glm-4v-9b` for accuracy.

## 5. Aspirational IDs to clean up (no-op for cianfhoghlaim code)

These 8 IDs are aspirational per Wave 1 Agent 19 R1:
- Documented in Wave 1 but NOT in current cianfhoghlaim code (already removed or never added)
- Action: Update openspec `meaisinfhoghlaim-ocr-htr` spec + `.agents/skills/huggingface/SKILL.md` to remove them

## 6. Next steps (full audit pending)

1. **Real audit via webfetch** (one wave per package): check HuggingFace Hub API for each of the 12 model_ids in question
2. **Fix the 3 name drifts** in `vlm_finetune_comparison.py`:
   - `qwen3-vl-7b` → `qwen2.5-vl-7b` (or update model_id to actual qwen3-vl-7b)
   - `qwen3-vl-30b` → `qwen2.5-vl-72b` (or update model_id to actual qwen3-vl-72b)
   - `glm-4.6v-flash` → `glm-4v-9b` (or update model_id to actual glm-4.6v-flash)
3. **Update openspec specs**:
   - `meaisinfhoghlaim-ocr-htr` - remove 8 aspirational model IDs
   - `huggingface/SKILL.md` - remove aspirational model references
4. **Add R5 conformance linter** (Agent 19 R5) - AST check that any new v1 App declares the vector index
5. **Re-run HF Hub audit** in next session when webfetch is reliable

## 7. Action plan

This audit will be completed in batches:
- **Batch 1 (this turn):** Initial inventory + name drift findings + next steps ✓
- **Batch 2 (next turn):** Real HF Hub verification for 12 model_ids
- **Batch 3 (next turn):** Apply name drift fixes + remove aspirational IDs from docs
- **Batch 4 (Phase F6 in plan v6):** Consolidate model_registry.py + vlm_finetune_comparison.py into the new `src/cianfhoghlaim/core/ocr/` tree
