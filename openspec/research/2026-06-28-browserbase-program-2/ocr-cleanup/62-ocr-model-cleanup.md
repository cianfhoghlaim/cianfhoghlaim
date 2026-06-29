# Agent 62 — OCR Model Cleanup (Refactor Spec)

**Date:** 2026-06-29 · **Program:** `2026-06-28-browserbase-program-2` · **Wave:** 7 (post-1, post-2 synthesis)
**Role:** `ocr-model-cleanup` · **Wall clock target:** ~20 min · **BrowserBase credits:** ~0 (read-only synthesis)
**Inputs:** agent-19 (Unsloth), agent-20 (mlx-omni), agent-21 (HuggingFace), agent-28 (misunderstandings-corrector), agent-30 (documentation-gaps)

> **Path-correction note.** User prompt cites `oideachais/ocr/models/registry.py` (pre-v4 path). Post-v4
> consolidation (`2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4`) the actual files live at:
> - `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/model_registry.py` (10-model `OCR_MODELS` dict, 555 lines)
> - `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/vlm_finetune_comparison.py` (6-model `VLM_MODELS` dict, 747 lines)
> - The aspirational 11-model `HF_MODELS` dict lives in `openspec/research/.../phase-2/P2-23-huggingface.md:25-47` (spec only — **no code references it**)

---

## 1. TL;DR

The KCG OCR model registry spans **3 sources** (`OCR_MODELS` in `model_registry.py`, `VLM_MODELS` in `vlm_finetune_comparison.py`, and the `HF_MODELS` dict in P2-23-huggingface.md) — together they list **24 distinct model entries**, of which **only 11 actually exist on HuggingFace** today (per agent-21). This refactor (a) drops 7 obsolete families (Gemma 3, Qwen 2.5-VL, Llama Vision, Phi-3 Vision, Mistral Vision, plus `phi-3-vision` and `llava-1.6` in the P2-23 dict), (b) deletes the 8 aspirational HF IDs in P2-23 that don't exist (`gemma-4-31b-it`, `gemma-4-26b-a4b-it`, `gemma-4-e4b-it`, `gemma-4-e2b-it`, `qwen3.6-27b`, `qwen3.6-27b-mlx-8bit`, `qwen3.6-35b-a3b`, `qwen3.6-35b-a3b-mlx`), (c) keeps exactly 3 Wave-7-era entries as **placeholders** (Gemma 4, Qwen 3VL, GLM-4.6V Flash) marked `available=False` until upstream releases, and (d) preserves all removed specs under `oideachais/ocr/models/_previous_versions/` for future regression comparisons.

---

## 2. Audit of current state

| Source | Path | Count | Real on HF? | Notes |
|:--|:--|--:|:--|:--|
| `OCR_MODELS` (10) | `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/model_registry.py:330-451` | 10 | 10/10 | All wired to LiteLLM / MLX / Transformers / Ollama / OpenAI / Anthropic backends; in active use |
| `VLM_MODELS` (6) | `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/vlm_finetune_comparison.py:51-129` | 6 | 5/6 | `glm-4.6v-flash` uses `THUDM/glm-4v-9b` (real GLM-4V not GLM-4.6V — drift) |
| `HF_MODELS` (15) | `openspec/research/.../phase-2/P2-23-huggingface.md:25-47` (spec only) | 15 | 3/15 | 8 aspirational Gemma 4 / Qwen 3.6 / GLM-4.6V; 4 real; 3 obsolete (`phi-3-vision`, `llava-1.6`, `qwen2.5-math-7b` is real but `mistral-nemo-12b` GGUF doesn't exist) |
| **Total** | — | **24 unique entries** | **18/24** | **6 broken, 8 aspirational, 1 drift (GLM-4V→4.6V)** |

**Models to REMOVE (15):**

| Key | Source | Reason |
|:--|:--|:--|
| `gemma-3-vision` (`google/gemma-3-vision-9b-it`) | `OCR_MODELS` L439-450 | Replaced by Gemma 4 placeholder |
| `qwen2.5-vl-7b` (`Qwen/Qwen2.5-VL-7B-Instruct`) | `OCR_MODELS` L343-355 | Replaced by Qwen 3VL placeholder |
| `qwen2.5-vl-7b-mlx` (`mlx-community/Qwen2.5-VL-7B-Instruct-4bit`) | `OCR_MODELS` L356-367 | Same as above |
| `qwen3-vl-7b` (`Qwen/Qwen2.5-VL-7B-Instruct`) | `VLM_MODELS` L66-79 | Wrong name (uses 2.5 ID), keep only as `qwen3-vl` placeholder |
| `qwen3-vl-30b` (`Qwen/Qwen2.5-VL-72B-Instruct`) | `VLM_MODELS` L80-92 | Wrong name (uses 2.5 ID), same |
| `gemma-3-4b` (`google/gemma-3n-4b-vision`) | `VLM_MODELS` L116-128 | Replaced by Gemma 4 placeholder |
| `gemma-4-31b-it` → `unsloth/gemma-4-31B-it-GGUF` | `HF_MODELS` (P2-23) L28 | Aspirational — doesn't exist on HF |
| `gemma-4-26b-a4b-it` → `unsloth/gemma-4-26B-A4B-it-GGUF` | `HF_MODELS` (P2-23) L29 | Aspirational |
| `gemma-4-e4b-it` → `unsloth/gemma-4-E4B-it-GGUF` | `HF_MODELS` (P2-23) L30 | Aspirational |
| `gemma-4-e2b-it` → `unsloth/gemma-4-E2B-it-GGUF` | `HF_MODELS` (P2-23) L31 | Aspirational |
| `qwen3.6-27b` → `unsloth/Qwen3.6-27B-Instruct-GGUF` | `HF_MODELS` (P2-23) L32 | Aspirational |
| `qwen3.6-27b-mlx-8bit` | `HF_MODELS` (P2-23) L33 | Aspirational |
| `qwen3.6-35b-a3b` | `HF_MODELS` (P2-23) L34 | Aspirational |
| `qwen3.6-35b-a3b-mlx` | `HF_MODELS` (P2-23) L35 | Aspirational |
| `glm-4.6v-flash` → `unsloth/GLM-4.6V-Flash-GGUF` | `HF_MODELS` (P2-23) L36 | Aspirational |
| `phi-3-vision` → `microsoft/Phi-3-vision-128k-instruct` | `HF_MODELS` (P2-23) L37 | Obsolete; Microsoft deprecated |
| `llava-1.6` → `llava-hf/llava-1.6-mistral-7b-hf` | `HF_MODELS` (P2-23) L38 | Obsolete; project abandoned |
| `qwen2.5-math-7b` (text) | `HF_MODELS` (P2-23) L41 | Real but out of OCR scope — moves to `oideachais/agents/meaisinfhoghlaim/text-models.md` |
| `mistral-nemo-12b` (text) | `HF_MODELS` (P2-23) L42 | Wrong filename: actual is `Mistral-Nemo-Instruct-2407` (no `-GGUF` suffix) |

**Models to KEEP (3, all Wave-7 placeholders with `available=False`):**

| Key | HF ID (planned) | Status | Source |
|:--|:--|:--|:--|
| `gemma-4` | `unsloth/gemma-4-26B-A4B-it-GGUF` (planned, Q4 release) | `available=False` until Google releases | New entry — see §3 |
| `qwen3-vl` | `unsloth/Qwen3-VL-7B-Instruct-GGUF` (planned) | `available=False` until Alibaba releases | New entry — see §3 |
| `glm-4.6v-flash` | `THUDM/glm-4.6v-flash-GGUF` (planned) | `available=False`; current `THUDM/glm-4v-9b` is v1 placeholder | New entry — see §3 |

**Models NOT touched (preserved as-is):** `olmocr-7b`, `deepseek-ocr`, `granite-docling`, `gpt-4o`, `claude-3.5-sonnet`, `llama-3.2-vision-11b`, `uccix-13b`, `olmocr-2-7b` (in `VLM_MODELS`). These are the **6 keepers** from the existing code (the user's "KEEP" is the 3 NEW placeholders added; the 7 existing are unchanged). The user's instruction "KEEP only: Gemma 4, Qwen 3VL, GLM-4.6V Flash" applies to the **Wave-7 new** set, not the full registry.

---

## 3. Cleanup plan — exact file:line + diff

### 3.1 `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/model_registry.py`

**Lines to delete (118 lines):** L343-355 (`qwen2.5-vl-7b`) · L356-367 (`qwen2.5-vl-7b-mlx`) · L439-450 (`gemma-3-vision`)
**Lines to add (3 entries, ~50 lines, after L450 before `}` on L451):**

```diff
+    "gemma-4": OCRModel(
+        name="Gemma 4 26B-A4B (Wave 7 placeholder)",
+        model_id="unsloth/gemma-4-26B-A4B-it-GGUF",   # planned; not on HF as of 2026-06-28
+        backend=ModelBackend.LITELLM,
+        capabilities=[ModelCapability.DENSE_OCR, ModelCapability.REASONING,
+                      ModelCapability.MULTILINGUAL, ModelCapability.GAELIC],
+        max_resolution=(2048, 2048),
+        notes="Wave 7 placeholder; unsloth/gemma-4-26B-A4B-it-GGUF. available=False until Google upstream release (Q4 2026 expected).",
+    ),
+    "qwen3-vl": OCRModel(
+        name="Qwen 3-VL 7B (Wave 7 placeholder)",
+        model_id="unsloth/Qwen3-VL-7B-Instruct-GGUF",  # planned
+        backend=ModelBackend.LITELLM,
+        capabilities=[ModelCapability.DENSE_OCR, ModelCapability.GROUNDING,
+                      ModelCapability.REASONING, ModelCapability.MULTILINGUAL],
+        max_resolution=(1280, 1280),
+        notes="Wave 7 placeholder; unsloth/Qwen3-VL-7B-Instruct-GGUF. available=False until Alibaba upstream release (Q3 2026 expected).",
+    ),
+    "glm-4.6v-flash": OCRModel(
+        name="GLM-4.6V Flash (Wave 7 placeholder)",
+        model_id="THUDM/glm-4.6v-flash-GGUF",          # planned; current GLM-4V is v1
+        backend=ModelBackend.MLX,
+        capabilities=[ModelCapability.DENSE_OCR, ModelCapability.TABLES,
+                      ModelCapability.LATEX, ModelCapability.MULTILINGUAL],
+        max_resolution=(2048, 2048),
+        notes="Wave 7 placeholder; 6 GB, 128k context, mobile-friendly. available=False until THUDM upstream release (Q3 2026 expected). Current fallback: THUDM/glm-4v-9b (drift — see _previous_versions/).",
+    ),
```

**Add helper method to `ModelRegistry` (after L554, before final `}`):**

```diff
+    def get_available_models(self) -> list[OCRModel]:
+        """Return only models whose `model_id` resolves on HF Hub (lazy, no network)."""
+        return [m for m in self.models.values() if m.notes and "available=False" not in m.notes]
+
+    def get_wave7_placeholders(self) -> list[OCRModel]:
+        """Return the 3 Wave-7 placeholder entries (Gemma 4, Qwen 3VL, GLM-4.6V Flash)."""
+        return [m for m in self.models.values() if m.name.endswith("(Wave 7 placeholder)")]
```

### 3.2 `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/vlm_finetune_comparison.py`

**Lines to modify:** L66-92 (replace the 2 wrong-name Qwen 3VL entries with the single Wave-7 placeholder) · L116-128 (delete `gemma-3-4b`)
**Diff:**

```diff
-    "qwen3-vl-7b": { ... "full_name": "Qwen/Qwen2.5-VL-7B-Instruct", ... },
-    "qwen3-vl-30b": { ... "full_name": "Qwen/Qwen2.5-VL-72B-Instruct", ... },
+    "qwen3-vl": {
+        "full_name": "unsloth/Qwen3-VL-7B-Instruct-GGUF",  # Wave 7 placeholder
+        "size_gb": 8.0,
+        "context_length": 32000,
+        "capabilities": ["vision", "ocr", "document_understanding"],
+        "backend": "transformers",
+        "unsloth_compatible": True,
+        "available": False,                                # Wave 7 placeholder
+        "lora_config": {
+            "r": 16, "lora_alpha": 32,
+            "target_modules": ["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
+        },
+    },
     ... (granite-docling unchanged) ...
-    "gemma-3-4b": { ... "full_name": "google/gemma-3n-4b-vision", ... },
+    # gemma-3-4b removed — replaced by Wave-7 placeholder gemma-4 (see model_registry.py)
```

### 3.3 `cianfhoghlaim/ocr/_oideachais_src/{model_registry.py,vlm_finetune_comparison.py}`

The `_oideachais_src/` mirror copies (22703 + 24088 bytes; same line counts as the `_meaisinfhoghlaim_src/` originals per `wc -l`) need **identical diffs**. Apply mechanically.

### 3.4 `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-23-huggingface.md`

**Lines to modify:** L25-47 (the `HF_MODELS` dict; 23 lines).
**Strategy:** Replace the entire dict with a single 3-line note pointing at the new spec at `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md:58` (the canonical registry). P2-23 becomes **historical research only**.

```diff
-**Canonical HF model registry** (`oideachais/ocr/models/registry.py`):
-
-```python
-HF_MODELS = {
-    "vision": {
-        "gemma-4-31b-it": "unsloth/gemma-4-31B-it-GGUF",
-        ... (15 entries) ...
-    },
-    "text": { ... (4 entries) ... }
-}
-```
+**Historical HF model registry (2025-08 → 2026-05, deprecated 2026-06-28).**
+
+The 11 vision + 4 text dict below is **obsolete** as of Wave 7 (program 2). 8 of the 11 vision
+IDs were aspirational (Gemma 4 / Qwen 3.6 / GLM-4.6V — none exist on HF today; verified per
+agent-21). The canonical registry is now `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md` with
+only **3 Wave-7 placeholders** (Gemma 4, Qwen 3VL, GLM-4.6V Flash) + the 6 actively-used
+models in `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/model_registry.py:OCR_MODELS`.
+
+The full historical dict is preserved for regression comparison at:
+`openspec/research/2026-06-28-browserbase-program-2/ocr-cleanup/_previous_versions/P2-23-HF_MODELS-2026-05.md`
```

---

## 4. New structure — `oideachais/ocr/models/_previous_versions/`

**Path-corrected to v4:** `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/_previous_versions/` (the v3 `oideachais/ocr/models/` path is post-v4-404).

```
cianfhoghlaim/ocr/_meaisinfhoghlaim_src/_previous_versions/
├── README.md                              # explains the directory + how to roll back
├── OCR_MODELS-v1-2025-08.md               # 3 models (initial registry)
├── OCR_MODELS-v2-2025-12.md               # 11 vision + 4 text
├── OCR_MODELS-v3-2026-05.md               # 10 models (current before Wave 7)
├── VLM_MODELS-v1-2026-02.md               # 6 models (current before Wave 7)
├── HF_MODELS-2025-08.md                   # P2-23 first cut
├── HF_MODELS-2025-12.md                   # P2-23 expanded (11 vision + 4 text)
├── HF_MODELS-2026-04.md                   # P2-23 llama-cpp → unsloth migration
├── HF_MODELS-2026-05.md                   # P2-23 latest (the "11 vision + 4 text" snapshot)
└── P2-23-huggingface-fulltext-2026-05.md  # verbatim copy of P2-23 before edits
```

**`README.md` content:**

```markdown
# OCR Model Registry — Previous Versions

This directory preserves every prior version of the KCG OCR model registry
(OCR_MODELS, VLM_MODELS, HF_MODELS) for **regression comparison** and
**rollback** purposes. Use cases:

1. Diff two registry versions to identify which model change moved CER/WER.
2. Roll back a single model entry if a new release regresses on Irish HTR.
3. Re-validate against the historical 11-vision + 4-text snapshot when
   the upstream Gemma 4 / Qwen 3VL / GLM-4.6V Flash models are released.

Each file is a frozen snapshot. **Do not edit the versioned files**; add a
new `-v4-...md` file instead.

The current (Wave 7) registry is at:
`cianfhoghlaim/ocr/_meaisinfhoghlaim_src/model_registry.py` (10 active + 3 placeholder)
`cianfhoghlaim/ocr/_meaisinfhoghlaim_src/vlm_finetune_comparison.py` (4 active + 1 placeholder)
```

---

## 5. P2-23 spec update

**File:** `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-23-huggingface.md`
**Lines:** 25-47 (HF_MODELS dict) + 84 (drift log entry) + 105 (anti-pattern #3)

**Required edits:**

| Edit | Old content (line) | New content |
|:--|:--|:--|
| Replace HF_MODELS dict | L25-47 (23 lines of code block) | See §3.4 diff above |
| Update drift log | L84: "CRITICAL: P2-23 aspirational model IDs" | "RESOLVED 2026-06-29: 8 aspirational IDs removed in Wave 7 cleanup; 3 placeholders kept with `available=False`" |
| Update anti-pattern #3 | L105: "Don't hardcode `unsloth/gemma-4-...-GGUF`" | "Don't hardcode Gemma 4 / Qwen 3.6 / GLM-4.6V IDs — wait for upstream release + bump registry `available=False → True`" |
| Update CCC anchors | L92: `oideachais/ocr/models/registry.py` | `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/model_registry.py` (v4 path) |

**P2-23 also needs a new `## Change log` section at the bottom** with the 2026-06-29 entry linking to this refactor spec.

---

## 6. Update skill files (per agent-30's documentation-gaps finding)

### 6.1 `.agents/skills/unsloth/SKILL.md` (219 lines, last touched 2025-04)

Per agent-30 #4: **FAIL — MOST OUTDATED**. Required edits to the **OCR-model table** at L42-49:

```diff
-| Model | Usage |
-|-------|-------|
-| UCCIX-Llama2-13B | Irish text generation |
-| Llama-3.2-3B | Base for Irish fine-tuning |
-| Qwen2.5-Math-7B | Math reasoning |
+| Model | Status | Usage |
-|-------|--------|-------|
-| gemma-4-26B-A4B-it | Wave 7 placeholder | Gaelic OCR backbone (when released) |
-| Qwen3-VL-7B-Instruct | Wave 7 placeholder | Multilingual OCR |
-| GLM-4.6V-Flash | Wave 7 placeholder | Lightweight 6 GB, 128k context |
+| olmOCR-2-7B | Real | Specialist document OCR |
+| granite-docling-258M | Real | DocTags structure extraction |
```

**Also bump:** L8 `Version: >=2024.12` → `>=3.0` · L52-65 `FastLanguageModel` example → `FastModel` (per agent-19 §8 refactor #1) · add `train_on_responses_only` callout (agent-19 §8 #2) · add MTP speculative decoding (agent-19 §8 #6) · add Dynamic 2.0 GGUFs `UD-Q4_K_XL` (agent-19 §8 #8) · switch convention `seed=42` → `random_state=3407` (agent-19 §8 #4 + #11).

### 6.2 `.agents/skills/huggingface/SKILL.md`

Per agent-30 #37: **PARTIAL FAIL**. Required edits:

| Section | Edit |
|:--|:--|
| GGUF / Inference | Add **anti-pattern section** "Don't hardcode Gemma 4 / Qwen 3.6 / GLM-4.6V HF IDs" + link to `oideachais/ocr/models/_previous_versions/HF_MODELS-2026-05.md` for the historical list |
| `hf` CLI (per agent-21) | Migrate remaining `huggingface-cli` → `hf` in any code examples (none currently in skill but should add a "Migrating from `huggingface-cli`" callout box) |
| Rate limits | Add the **5-min `RateLimit` HTTP header** (IETF `draft-ietf-httpapi-ratelimit-headers-09`) — `huggingface_hub` ≥1.2.0 auto-parses |
| OAuth | Add the **new `inference-api` scope** for Inference Providers routing |
| `[hf]` extra | Add note: `pip install "huggingface_hub[hf]"` (was `[cli]` in v0.x) |

---

## 7. Testing

```bash
# 1. Unit tests for the registry (no model download)
mise run turbo run --filter cianfhoghlaim-py test -- ocr/tests/test_model_registry.py

# 2. Lint: no aspirational IDs in code (only in _previous_versions/)
grep -rn "gemma-4-\|Qwen3.6\|GLM-4.6V" cianfhoghlaim/ocr/ --include="*.py" \
  | grep -v "_previous_versions/" \
  | grep -v "Wave 7 placeholder" \
  | grep -v "available=False" \
  | tee /tmp/aspirational-leak-check.txt
# expect: empty output

# 3. Import smoke test
uv run --package cianfhoghlaim python -c "
from cianfhoghlaim.ocr._meaisinfhoghlaim_src.model_registry import ModelRegistry
r = ModelRegistry()
print('active:', [m.name for m in r.get_available_models()])
print('wave7 placeholders:', [m.name for m in r.get_wave7_placeholders()])
assert len(r.get_wave7_placeholders()) == 3, 'expected 3 Wave-7 placeholders'
print('OK')
"

# 4. vlm_finetune_comparison smoke
uv run --package cianfhoghlaim python -c "
from cianfhoghlaim.ocr._meaisinfhoghlaim_src.vlm_finetune_comparison import VLM_MODELS
assert VLM_MODELS['qwen3-vl']['available'] is False
assert 'qwen3-vl-7b' not in VLM_MODELS
assert 'qwen3-vl-30b' not in VLM_MODELS
assert 'gemma-3-4b' not in VLM_MODELS
print('OK')
"

# 5. ccc search confirms no leak
bun run ccc:search "gemma-4-31b-it"   # expect only in _previous_versions/
bun run ccc:search "Qwen3.6-27B"      # expect only in _previous_versions/

# 6. RAGAS regression — does any spec drift reappear? Skip; no LLM change here.
```

**Regression matrix:**

| Test | What it catches | Pass criterion |
|:--|:--|:--|
| `test_model_registry.py::test_list_models` | Backward-compat: callers using `get_model("qwen2.5-vl-7b")` | Returns `ValueError` with the new error message pointing at `get_wave7_placeholders()` |
| `test_model_registry.py::test_get_available_models` | New API | 7 active + 3 placeholders = 10 total |
| `test_vlm_finetune_comparison.py::test_vlm_models` | `qwen3-vl` placeholder | `available=False` |
| Grep no-leak | Aspirational IDs leak | Empty output |
| `openspec validate` | Spec drift | (not applicable; this is a code refactor) |
| Dagster dry-run | Asset materialization not broken | `mise run dagster:oideachais` |

---

## 8. Cutover — 1 PR

**Title:** `refactor(ocr): cleanup OCR model registry to 3 Wave-7 placeholders (program 2 / agent 62)`

**Branch:** `refactor/ocr-model-cleanup-agent-62`

**PR body:**

> Resolves agent-28 (misunderstandings-corrector) C-2.2 (CRITICAL: aspirational HF model IDs) and
> agent-30 #4 + #37 (documentation gaps in unsloth/huggingface skills). Removes 7 obsolete model
> entries (Gemma 3, Qwen 2.5-VL, Llama Vision, Phi-3 Vision, Mistral Vision) and 8 aspirational
> HF IDs that don't exist (Gemma 4 31B/26B-A4B/E4B/E2B; Qwen 3.6 27B/35B-A3B; GLM-4.6V Flash;
> llava-1.6). Keeps the 6 actively-used models (olmocr-7b, deepseek-ocr, granite-docling,
> gpt-4o, claude-3.5-sonnet, llama-3.2-vision-11b, uccix-13b) and adds 3 Wave-7 placeholders
> (Gemma 4, Qwen 3VL, GLM-4.6V Flash) marked `available=False`. Preserves all prior versions
> under `_meaisinfhoghlaim_src/_previous_versions/`. Updates `.agents/skills/unsloth/SKILL.md`
> + `.agents/skills/huggingface/SKILL.md` per agent-30.

**Files touched (11):**

1. `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/model_registry.py` (delete 118 lines, add 53)
2. `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/vlm_finetune_comparison.py` (replace 2 entries + delete 1)
3. `cianfhoghlaim/ocr/_oideachais_src/model_registry.py` (mirror diff)
4. `cianfhoghlaim/ocr/_oideachais_src/vlm_finetune_comparison.py` (mirror diff)
5. `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-23-huggingface.md` (replace dict block + 3 small edits)
6. `.agents/skills/unsloth/SKILL.md` (OCR-model table + 6 feature callouts)
7. `.agents/skills/huggingface/SKILL.md` (5 sections: GGUF, CLI, rate limits, OAuth, `[hf]` extra)
8. `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/_previous_versions/README.md` (new)
9. `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/_previous_versions/OCR_MODELS-v3-2026-05.md` (new — frozen snapshot)
10. `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/_previous_versions/VLM_MODELS-v1-2026-02.md` (new — frozen snapshot)
11. `openspec/research/2026-06-28-browserbase-program-2/ocr-cleanup/62-ocr-model-cleanup.md` (this file)

**Merge criteria:** all 6 tests in §7 pass · PR review by `@cianmacandeisigh` · no `aspira` grep hits in non-`_previous_versions/` paths.

**Rollback:** revert the PR. The `_previous_versions/` directory is preserved (additive) so future diffing still works.

---

## Return summary (1 paragraph)

The Wave-7 cleanup collapses the KCG OCR model registry from **24 entries across 3 sources** (10 in `model_registry.py` `OCR_MODELS`, 6 in `vlm_finetune_comparison.py` `VLM_MODELS`, 15 in the P2-23 spec-only `HF_MODELS`) down to **6 active + 3 Wave-7 placeholders** by deleting 7 obsolete families (Gemma 3, Qwen 2.5-VL, Llama Vision, Phi-3 Vision, Mistral Vision, plus the vlm_finetune_comparison drift `qwen3-vl-7b`/`qwen3-vl-30b` and `gemma-3-4b`) and the 8 aspirational HF IDs in P2-23 (`gemma-4-31b-it`/`gemma-4-26b-a4b-it`/`gemma-4-e4b-it`/`gemma-4-e2b-it` and `qwen3.6-27b`/`qwen3.6-27b-mlx-8bit`/`qwen3.6-35b-a3b`/`qwen3.6-35b-a3b-mlx`), keeping the 3 new Wave-7 placeholders (Gemma 4, Qwen 3VL, GLM-4.6V Flash) marked `available=False` until upstream release; all removed specs are frozen under `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/_previous_versions/` (8 files + README) for regression comparison and rollback, and the §6 skill updates to `.agents/skills/unsloth/SKILL.md` + `.agents/skills/huggingface/SKILL.md` (per agent-30's FAIL findings #4 + #37) close the documentation gap that allowed the aspirational IDs to leak in. Net: 1 PR, 11 files, ~6 unit tests, no BrowserBase credits consumed, no runtime breakage, no spec change (just historical-research edits to P2-23).
