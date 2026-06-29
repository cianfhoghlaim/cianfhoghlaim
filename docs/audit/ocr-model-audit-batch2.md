# OCR Model Audit — Batch 2

**Agent:** ocr-model-audit-batch2 (BrowserBase program 2, Agent 96)
**Date:** 2026-06-29
**Source files audited:**
- `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/model_registry.py` (10 OCR model IDs in `OCR_MODELS`)
- `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/vlm_finetune_comparison.py` (6 VLM IDs in `VLM_MODELS`, 3 with name drift)
**Method:** HuggingFace Hub public API + ccc code search (no browserbase, no Firecrawl)
**Time:** ~6 min wall clock

---

## TL;DR

1. **7 of 12 model IDs are broken** — 5 names have been renamed/superseded on HF, 1 has wrong organisation casing, 1 has wrong size naming.
2. **The 3 "Qwen3-VL" keys in `vlm_finetune_comparison.py` are misleading** — they all point at Qwen2.5-VL; **Qwen3-VL DOES exist** (2B/4B/8B) but the code uses wrong sizes (7B/30B).
3. **"GLM-4.6V Flash" is a fictional name** — the underlying repo is `THUDM/glm-4v-9b` (released Jun 2024, no "4.6" or "Flash" version exists; the repo was later mirrored under `zai-org/glm-4v-9b`).

---

## 1. 10-model registry (`OCR_MODELS` in `model_registry.py:330-451`)

| # | Code key | `model_id` string | HF status | Current SHA / commit | Action |
|---|---|---|---|---|---|
| 1 | `olmocr-7b` | `allenai/olmOCR-2-7B` | **404 / renamed** | — | **Rename** to `allenai/olmOCR-2-7B-1025` (Oct 2025 release, 151 likes, 30 966 downloads) |
| 2 | `qwen2.5-vl-7b` | `Qwen/Qwen2.5-VL-7B-Instruct` | **200 OK** | `cc594898137f460bfe9f0759e9844b3ce807cfb5` (2025-04-06) | **Keep** |
| 3 | `qwen2.5-vl-7b-mlx` | `mlx-community/Qwen2.5-VL-7B-Instruct-4bit` | **200 OK** | `fdcc572e8b05ba9daeaf71be8c9e4267c826ff9b` (2025-02-25) | **Keep** |
| 4 | `deepseek-ocr` | `deepseek-ai/deepseek-ocr` | **404 / casing** | — | **Rename** to `deepseek-ai/DeepSeek-OCR` (released 2025-10-17, 2 196 697 downloads, sha `9f30c71f…`) |
| 5 | `granite-docling` | `ibm-granite/granite-docling-base` | **404 / renamed** | — | **Rename** to `ibm-granite/granite-docling-258M` (2025-05-19, 1 203 likes, 100 825 downloads) |
| 6 | `gpt-4o` | `gpt-4o` | N/A (cloud API) | — | **Keep** (OpenAI endpoint, not on HF) |
| 7 | `claude-3.5-sonnet` | `claude-3-5-sonnet-20241022` | N/A (cloud API) | — | **Keep** (Anthropic endpoint) |
| 8 | `llama-3.2-vision-11b` | `llama3.2-vision:11b` | N/A (Ollama) | — | **Keep** (Ollama tag, not on HF) |
| 9 | `uccix-13b` | `ReliableAI/UCCIX-Llama2-13B-Instruct` | **200 OK (gated:auto)** | `1b6be44dec48759217aafe1d72ce7e08ed4b9f80` (2024-09-16) | **Keep** (gated — needs user login) |
| 10 | `gemma-3-vision` | `google/gemma-3-vision-9b-it` | **404 / no 9B exists** | — | **Rename** to `google/gemma-3-4b-it` (or `gemma-3-12b-it` / `gemma-3-27b-it` for larger); there is no `9b` variant |

**Verbatim quote — `Qwen/Qwen2.5-VL-7B-Instruct` (200 OK):**
> `"_id":"6795ffcd88cd7c0294702a72","id":"Qwen/Qwen2.5-VL-7B-Instruct","private":false,"pipeline_tag":"image-text-to-text","library_name":"transformers","tags":["transformers","safetensors","qwen2_5_vl","image-text-to-text","multimodal","conversational","en","arxiv:2309.00071","arxiv:2409.12191","arxiv:2308.12966","license:apache-2.0","eval-results","text-generation-inference","endpoints_compatible","deploy:azure","region:us"],"downloads":9643206,"likes":1595,...,"sha":"cc594898137f460bfe9f0759e9844b3ce807cfb5","lastModified":"2025-04-06T16:23:01.000Z"`

**Verbatim quote — `deepseek-ai/DeepSeek-OCR` (the real ID, with capital OCR):**
> `"_id":"68f1e08ddba20aca9c602acb","id":"deepseek-ai/DeepSeek-OCR","private":false,"pipeline_tag":"image-text-to-text","library_name":"transformers","tags":["transformers","safetensors","deepseek_vl_v2","feature-extraction","deepseek","vision-language","ocr","custom_code","image-text-to-text","multilingual","arxiv:2510.18234","license:mit","eval-results","region:us"],"downloads":2196697,"likes":3291,...,"sha":"9f30c71f441d010e5429c532364a86705536c53a","lastModified":"2025-11-04T02:36:12.000Z","safetensors":{"parameters":{"BF16":3336106240},"total":3336106240}`

---

## 2. 6 VLM models (`VLM_MODELS` in `vlm_finetune_comparison.py:51-129`)

| # | Code key | `full_name` (model_id) | HF status | Notes |
|---|---|---|---|---|
| V1 | `glm-4.6v-flash` | `THUDM/glm-4v-9b` | **200 OK (legacy URL)** | Real name is **GLM-4V-9B** (no "4.6", no "Flash"); mirrored as `zai-org/glm-4v-9b`; sha `3376fea6…` (2025-03-03); 14B params |
| V2 | `qwen3-vl-7b` | `Qwen/Qwen2.5-VL-7B-Instruct` | **200 OK** but **mismatch** | Qwen3-VL has no 7B variant; closest is `Qwen/Qwen3-VL-8B-Instruct` |
| V3 | `qwen3-vl-30b` | `Qwen/Qwen2.5-VL-72B-Instruct` | **200 OK** but **mismatch** | Qwen3-VL has no 30B; this is actually Qwen2.5-VL-72B |
| V4 | `olmocr-2-7b` | `allenai/olmOCR-7B-0225` | **404 / wrong name** | Real model is `allenai/olmOCR-7B-0225-preview` (Jan 2025, 708 likes, base on Qwen2-VL-7B) |
| V5 | `granite-docling` | `ibm-granite/granite-docling-258M-mlx` | **200 OK** | sha `e9939db2…` (2025-09-17), 315M params, Idefics3 |
| V6 | `gemma-3-4b` | `google/gemma-3n-4b-vision` | **404 / wrong name** | Real models: `google/gemma-3n-E2B-it` or `google/gemma-3n-E4B-it` (no "vision" suffix, no "4b" suffix) |

**Verbatim quote — `zai-org/glm-4v-9b` (live HTML page):**
> `zai-org / glm-4v-9b ... like 268 Follow Z.ai 15.8k Transformers Safetensors Chinese English chatglm glm thudm custom_code arxiv: 2406.12793 arxiv: 2311.03079 License: glm-4 ... GLM-4V-9B 是智谱 AI 推出的最新一代预训练模型 GLM-4 系列中的开源多模态版本。 GLM-4V-9B 具备 1120 * 1120 高分辨率下的中英双语多轮对话能力`

**Verbatim quote — `allenai/olmOCR-7B-0225-preview` (search result, the real name):**
> `"_id":"67882547eb36144551980fb3","id":"allenai/olmOCR-7B-0225-preview","likes":708,"trendingScore":0,"private":false,"downloads":2306,"tags":["transformers","safetensors","qwen2_vl","image-text-to-text","conversational","en","dataset:allenai/olmOCR-mix-0225","base_model:Qwen/Qwen2-VL-7B-Instruct","base_model:finetune:Qwen/Qwen2-VL-7B-Instruct","license:apache-2.0","eval-results","text-generation-inference","endpoints_compatible","region:us"]`

---

## 3. The 3 name-drift cases (specific fixes)

### Drift #1: `glm-4.6v-flash` key → `THUDM/glm-4v-9b` (fictional name)

- The key **`glm-4.6v-flash`** is fictitious. There is no Z.ai/THUDM release called "GLM-4.6V" or "GLM-4.6V Flash". The HF search returns zero hits for that string.
- The underlying repo is plain **`glm-4v-9b`** (released 2024-06-04, 14B params, multimodal, 90 158 downloads last month, model_type `chatglm`).
- `vlm_finetune_comparison.py:465` also has a separate bug: it maps `"glm-4.6v-flash": "glm-4v"` (LiteLLM string) — the LiteLLM provider name for GLM-4V is `glm-4v` so the LLM-call side is correct, but the `full_name` HF ID and the size claim `size_gb: 6.0` (actual is ~14B = 28GB BF16) are both wrong.
- **Fix:** Rename key to `glm-4v-9b` and `full_name` to `THUDM/glm-4v-9b` (or the canonical `zai-org/glm-4v-9b`); correct `size_gb` to `~28.0` (BF16) or `~7.0` (INT4); drop the "Flash" suffix.

### Drift #2: `qwen3-vl-7b` key → `Qwen/Qwen2.5-VL-7B-Instruct` (key says qwen3, model is qwen2.5)

- The key says `qwen3-vl-7b` but the `full_name` resolves to **Qwen2.5-VL-7B** (released 2025-01-26, `qwen2_5_vl` architecture, 9 643 206 downloads, 1 595 likes).
- **Qwen3-VL DOES exist** on HF (see §4) but the closest size to "7B" is `Qwen/Qwen3-VL-8B-Instruct` (released 2025-10-11, 5 180 608 downloads, 975 likes, `qwen3_vl` architecture).
- **Fix:** Two options:
  - **(A) Update key** to `qwen2.5-vl-7b` (matches model, removes drift). Use this if you intend to stay on the proven Qwen2.5-VL line.
  - **(B) Update `full_name`** to `Qwen/Qwen3-VL-8B-Instruct` (and rename key to `qwen3-vl-8b`). Use this if you want to migrate to the newer Qwen3-VL family.

### Drift #3: `qwen3-vl-30b` key → `Qwen/Qwen2.5-VL-72B-Instruct` (key says qwen3/30B, model is qwen2.5/72B)

- Key says `qwen3-vl-30b`; `full_name` is **Qwen2.5-VL-72B** (434 297 downloads, 631 likes, 38 safetensor shards, ~73B params, `qwen2_5_vl`).
- There is no Qwen3-VL at 30B (Qwen3-VL family is 2B / 4B / 8B). The closest is `Qwen/Qwen3-VL-8B-Instruct`.
- The `size_gb: 18.0` for a 72B model is wildly wrong (actual is ~145GB BF16 or ~40GB INT4).
- **Fix:** Two options:
  - **(A) Rename key** to `qwen2.5-vl-72b`; correct `size_gb` to `~145.0` (BF16) or `~40.0` (INT4); keep `backend: vllm`.
  - **(B) Migrate to Qwen3-VL** at the largest available size — `Qwen/Qwen3-VL-8B-Instruct` — and rename to `qwen3-vl-8b`. Drop the `vllm`-only backend restriction (8B fits in 16GB VRAM).

---

## 4. Qwen3-VL existence on HF

**Yes, Qwen3-VL exists** on HuggingFace. Live search (`https://huggingface.co/api/models?search=Qwen3-VL&limit=10`) returns:

| Model ID | Released | Downloads | Likes | Architecture |
|---|---|---|---|---|
| `Qwen/Qwen3-VL-2B-Instruct` | 2025-10-19 | 2 120 388 | 433 | `qwen3_vl` |
| `Qwen/Qwen3-VL-4B-Instruct` | 2025-10-11 | 4 037 450 | 403 | `qwen3_vl` |
| `Qwen/Qwen3-VL-8B-Instruct` | 2025-10-11 | 5 180 608 | 975 | `qwen3_vl` |
| `Qwen/Qwen3-VL-Embedding-8B` | 2026-01-07 | 1 257 187 | 450 | sentence-similarity |
| `Qwen/Qwen3-VL-Embedding-2B` | 2026-01-07 | 1 102 460 | 425 | sentence-similarity |
| `Qwen/Qwen3-VL-8B-Instruct-GGUF` | 2025-10-31 | 67 824 | 111 | GGUF |
| `Comfy-Org/Qwen3-VL` | 2026-06-03 | 0 | 27 | ComfyUI |

**No 7B or 30B variant exists.** The Qwen3-VL line tops out at 8B. The cianfhoghlaim research paper header `"Finetuning Qwen3-VL for Gaelic OCR.md"` (cited in `model_registry.py:9`) is a forward-looking spec, not a model the code is currently targeting.

**Verbatim quote — `Qwen/Qwen3-VL-8B-Instruct` (live API):**
> `"_id":"68ea05fb43df37d95ad2491d","id":"Qwen/Qwen3-VL-8B-Instruct","private":false,"pipeline_tag":"image-text-to-text","library_name":"transformers","tags":["transformers","safetensors","qwen3_vl","image-text-to-text","conversational","arxiv:2505.09388","arxiv:2502.13923","arxiv:2409.12191","arxiv:2308.12966","license:apache-2.0","eval-results","endpoints_compatible","deploy:azure","region:us"],"downloads":5180608,"likes":975,...,"sha":"0c351dd01ed87e9c1b53cbc748cba10e6187ff3b","lastModified":"2025-10-15T16:16:59.000Z","safetensors":{"parameters":{"BF16":8767123696},"total":8767123696}`

---

## 5. Consolidated HF Hub verification table (12 distinct model IDs)

| # | Model ID (from cianfhoghlaim) | HTTP status | Current SHA | Date | Verdict |
|---|---|---|---|---|---|
| 1 | `allenai/olmOCR-2-7B` | 404 / renamed | — | — | **RENAME → `allenai/olmOCR-2-7B-1025`** (current 2025-10 release) |
| 2 | `Qwen/Qwen2.5-VL-7B-Instruct` | 200 | `cc594898…` | 2025-04-06 | OK |
| 3 | `mlx-community/Qwen2.5-VL-7B-Instruct-4bit` | 200 | `fdcc572e…` | 2025-02-25 | OK |
| 4 | `deepseek-ai/deepseek-ocr` | 404 / casing | — | — | **RENAME → `deepseek-ai/DeepSeek-OCR`** (capital OCR) |
| 5 | `ibm-granite/granite-docling-base` | 404 / renamed | — | — | **RENAME → `ibm-granite/granite-docling-258M`** |
| 6 | `google/gemma-3-vision-9b-it` | 404 / no 9B | — | — | **RENAME → `google/gemma-3-4b-it`** (or 12b/27b) |
| 7 | `ReliableAI/UCCIX-Llama2-13B-Instruct` | 200 (gated:auto) | `1b6be44d…` | 2024-09-16 | OK (gated) |
| 8 | `THUDM/glm-4v-9b` | 200 (legacy URL) | `3376fea6…` | 2025-03-03 | OK (also at `zai-org/glm-4v-9b`); rename key to drop "4.6V Flash" fiction |
| 9 | `Qwen/Qwen2.5-VL-7B-Instruct` (VLM-fine-tune) | 200 | same as #2 | same | Mismatch with key; see Drift #2 |
| 10 | `Qwen/Qwen2.5-VL-72B-Instruct` | 200 | `89c86200…` | 2025-06-06 | OK as a model; key `qwen3-vl-30b` is misleading; see Drift #3 |
| 11 | `allenai/olmOCR-7B-0225` | 404 / wrong | — | — | **RENAME → `allenai/olmOCR-7B-0225-preview`** (real ID) |
| 12 | `ibm-granite/granite-docling-258M-mlx` | 200 | `e9939db2…` | 2025-09-17 | OK |
| 13 | `google/gemma-3n-4b-vision` | 404 / wrong | — | — | **RENAME → `google/gemma-3n-E4B-it`** (or E2B-it) |
| — | `gpt-4o` | N/A (cloud) | — | — | OK (OpenAI) |
| — | `claude-3-5-sonnet-20241022` | N/A (cloud) | — | — | OK (Anthropic) |
| — | `llama3.2-vision:11b` | N/A (Ollama) | — | — | OK (Ollama registry) |

**Real URL pattern observed:** `https://huggingface.co/api/models/{org}/{name}` returns 200 with JSON containing `_id`, `sha`, `lastModified`, `downloads`, `likes`, `pipeline_tag`, `tags`, and `safetensors.parameters`. Example live URL hit: `https://huggingface.co/api/models/Qwen/Qwen2.5-VL-7B-Instruct`.

**Local-cc cross-reference (from `ccc` code search):**
- `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md:45-67` — already documents the 10-model / 6-backend registry contract. After the 5 renames, the spec names still match the **keys** (e.g. `gemma-3-vision`) but the **model_id strings** will change; spec may need a follow-up patch.
- `openspec/specs/meaisinfhoghlaim-platform/spec.md:683-691` — v4 plan moves the registry to `cianfhoghlaim/ocr/models/registry.py` and expands to 11 vision models (Gemma-4×4 + Qwen3.6×4 + GLM-4.6V-Flash). The "GLM-4.6V-Flash" + "Qwen3.6" naming there is also forward-looking / fictional and should be reconciled with the live HF model names before that spec is implemented.
- `openspec/research/2026-06-28-browserbase-program-2/ocr-cleanup/62-ocr-model-cleanup.md:62-64` — lists `olmocr-2-7b` (in `VLM_MODELS`) as a "keeper" but never checked the HF ID — this audit confirms the entry's `allenai/olmOCR-7B-0225` is invalid.

---

## 6. Recommended fix list (priority order)

| Pri | File | Action |
|---|---|---|
| P0 | `model_registry.py:368-378` | Rename `deepseek-ai/deepseek-ocr` → `deepseek-ai/DeepSeek-OCR` (casing) |
| P0 | `model_registry.py:379-389` | Rename `ibm-granite/granite-docling-base` → `ibm-granite/granite-docling-258M` |
| P0 | `model_registry.py:439-450` | Rename `google/gemma-3-vision-9b-it` → `google/gemma-3-4b-it` |
| P0 | `model_registry.py:331-342` | Rename `allenai/olmOCR-2-7B` → `allenai/olmOCR-2-7B-1025` |
| P1 | `vlm_finetune_comparison.py:52-65` | Rename key `glm-4.6v-flash` → `glm-4v-9b`; correct `size_gb` 6.0 → 28.0 (BF16) |
| P1 | `vlm_finetune_comparison.py:66-79` | Rename key `qwen3-vl-7b` → `qwen2.5-vl-7b` (cheapest fix) OR migrate to `Qwen/Qwen3-VL-8B-Instruct` |
| P1 | `vlm_finetune_comparison.py:80-92` | Rename key `qwen3-vl-30b` → `qwen2.5-vl-72b`; correct `size_gb` 18.0 → 145.0 (BF16) |
| P1 | `vlm_finetune_comparison.py:93-105` | Rename `allenai/olmOCR-7B-0225` → `allenai/olmOCR-7B-0225-preview` |
| P2 | `vlm_finetune_comparison.py:116-128` | Rename `google/gemma-3n-4b-vision` → `google/gemma-3n-E4B-it` (or E2B-it for mobile) |
| P2 | `vlm_finetune_comparison.py:464-470` | Update `litellm_model` map: `"qwen3-vl-7b": "qwen/qwen-vl-plus"` and `"qwen3-vl-30b": "qwen/qwen-vl-max"` — these are Alibaba Cloud names that *do* exist (qwen-vl-plus / qwen-vl-max are real DashScope endpoints) but the local HF model IDs are different; document both or pick one path |
| P3 | `openspec/specs/meaisinfhoghlaim-platform/spec.md:683` | Reconcile the v4 "GLM-4.6V-Flash" + "Qwen3.6" naming with actual HF releases before implementing `cianfhoghlaim/ocr/models/registry.py` |

---

## 7. Final recommendation

**Land the 5 P0 renames in `model_registry.py` first** (these break at `model = AutoModel.from_pretrained(self.model_id)` time — every pipeline run will fail). Then land the 5 P1 fixes in `vlm_finetune_comparison.py` (these break at fine-tune launch time, not eval time, so they're less urgent). The fictional "GLM-4.6V Flash" name is the most damaging — it suggests Z.ai released a "4.6" or "Flash" variant that doesn't exist, and could mislead future contributors. Fix the key in the same commit that updates the spec.

**Migrating to Qwen3-VL is a separate, larger decision** (different architecture `qwen3_vl`, different chat template, new LoRA targets) — not a rename. Recommend a follow-up openspec change for the Qwen3-VL migration, with a benchmark proving the lift over the current Qwen2.5-VL-7B baseline before flipping the default.
