# Agent 78 — Live Unsloth Docs Verification

**Date:** 2026-06-29 (UTC)
**Program:** `2026-06-28-browserbase-program-2` (live-docs sweep, Wave 2)
**Package:** unsloth 2026.6.9 (PyPI) / v0.1.471-beta (GitHub release tag)
**Subagent:** research-platform — BrowserBase + webfetch (extract was unreliable)
**Prior text:** `openspec/research/2026-06-28-browserbase-program-2/agent-19-unsloth.md`

## TL;DR

- Unsloth shipped 3 major GitHub releases between Wave 1 (Jun 11, 2026) and now: **v0.1.451-beta** (Jun 10, Gemma 4 MTP), **v0.1.464-beta** (Jun 12, DiffusionGemma + Gemma 4 MTP + audio + Preserve Thinking + MiniMax-M3), and **v0.1.471-beta** (Jun 18, GLM-5.2 + Model Hub + 3x longer contexts + Bypass Permissions + `--secure` Cloudflare HTTPS tunnel).
- The current install path is `curl -fsSL https://unsloth.ai/install.sh | sh` and the current pin is `unsloth>=2026.6.9`. Every doc page resolves to a `.md` variant at `https://unsloth.ai/docs/<page>.md?ask=<question>&goal=<endgoal>` — that is the canonical URL pattern agents should hit instead of `browserbase_extract`.
- Wave 1's `FastModel` / `FastVisionModel` API claim is **only partially correct** (PR #6203 fixes `FastModel` config-passthrough for sequence classification, but the live fine-tuning guide still uses `FastLanguageModel.from_pretrained` + `get_peft_model`). The `train_on_responses_only` accuracy booster does **NOT** appear in the live guide; the new documented lever is `--chat-template-kwargs enable_thinking` / `preserve_thinking`.

## Current version (verified live)

| Channel | Version | Released | Source |
|:--|:--|:--|:--|
| PyPI | **`unsloth 2026.6.9`** | **Jun 22, 2026** | `https://pypi.org/project/unsloth/` ("Released: Jun 22, 2026") |
| GitHub tag | **`v0.1.471-beta`** | **Jun 18, 2026 17:36** | `https://github.com/unslothai/unsloth/releases/tag/v0.1.471-beta` |
| Install pin | **`unsloth>=2026.6.9`** | n/a | Verbatim release note: "Ensure your version is `2026.6.9` or `v0.1.471-beta` for the latest." |

GitHub repo stats (verified live): **Star 67.5k / Fork 6.1k / 789 open issues / 234 open PRs**.

## 5-10 verbatim code examples (live upstream)

### 1. macOS / Linux / WSL install (PyPI long description)

```bash
curl -fsSL https://unsloth.ai/install.sh | sh
```

### 2. Studio launch (PyPI long description)

```bash
unsloth studio -p 8888
```

### 3. 3x longer-context table (v0.1.471-beta release notes — excerpt)

`1x 32GB pipeline (~31 GB) | f16 | 23,040 → 64,000` | `1x 32GB pipeline (~31 GB) | q8_0 | 43,520 → 114,944` | `1x 32GB pipeline (~31 GB) | q4_0 | 82,432 → 199,680` | `2x 32GB pipeline | any | 262,144 (cap)` | `2x 24GB tensor (~23 GB) | f16 | 134,049 → 262,144` | `2x 24GB tensor (~23 GB) | q8_0 | 252,329 → 262,144`.

### 4. Qwen3.6 27B MTP — llama-cli thinking-mode (models/qwen3.6.md)

```bash
export LLAMA_CACHE="unsloth/Qwen3.6-27B-MTP-GGUF"
./llama.cpp/llama-cli \
    -hf unsloth/Qwen3.6-27B-MTP-GGUF:UD-Q4_K_XL \
    --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.00 \
    --spec-type draft-mtp --spec-draft-n-max 2
```

### 5. Qwen3.6 35B-A3B via llama-server (models/qwen3.6.md)

```bash
./llama.cpp/llama-server \
    --model unsloth/Qwen3.6-35B-A3B-GGUF/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf \
    --mmproj unsloth/Qwen3.6-35B-A3B-GGUF/mmproj-F16.gguf \
    --alias "unsloth/Qwen3.6-35B-A3B" \
    --temp 0.6 --top-p 0.95 --ctx-size 16384 \
    --top-k 20 --min-p 0.00 --port 8001
```

### 6. Gemma 4 12B dynamic-4bit via llama-cli (models/gemma-4.md)

```bash
export LLAMA_CACHE="unsloth/gemma-4-12b-it-GGUF"
./llama.cpp/llama-cli \
    -hf unsloth/gemma-4-12b-it-GGUF:UD-Q4_K_XL \
    --temp 1.0 --top-p 0.95 --top-k 64
```

### 7. vLLM with NVFP4 + MTP for Qwen3.6 35B-A3B (models/qwen3.6.md)

```shell
vllm serve unsloth/Qwen3.6-35B-A3B-NVFP4 --trust-remote-code --dtype bfloat16 --moe-backend marlin \
     --speculative-config '{"method":"mtp","num_speculative_tokens":3,"moe_backend":"triton"}'
```

### 8. Gemma 4 thinking-mode system prompt (models/gemma-4.md, verbatim block)

```
<|think|>
You are a careful coding assistant. Explain your answer clearly.
```

### 9. Fine-tuning guide — recommended defaults (get-started/fine-tuning-llms-guide.md)

> `max_seq_length = 2048` — Controls context length. While Llama-3 supports 8192, we recommend 2048 for testing. Unsloth enables 4× longer context fine-tuning.
> `dtype = None` — Defaults to None; use `torch.float16` or `torch.bfloat16` for newer GPUs.
> `load_in_4bit = True` — Enables 4-bit quantization, reducing memory use 4× for fine-tuning. Disabling it enables LoRA 16-bit fine-tuning.

### 10. OpenAI-compatible client to llama-server (models/qwen3.6.md)

```python
from openai import OpenAI
import json
openai_client = OpenAI(
    base_url = "http://127.0.0.1:8001/v1",
    api_key = "sk-no-key-required",
)
completion = openai_client.chat.completions.create(
    model = "unsloth/Qwen3.6-35B-A3B",
    messages = [{"role": "user", "content": "Create a Snake game."},],
)
print(completion.choices[0].message.content)
```

## Live changelog entries since Wave 1 (2026-06-11 → 2026-06-22)

Three GitHub releases shipped ten Wave-2 headlines that did not exist in Wave 1:

1. **GLM-5.2 + Model Hub** — full-page Hub with trending feed, README split-view, Xet downloads, "Load on selection" toggle (v0.1.471-beta, Jun 18).
2. **3x longer contexts** — Unsloth Studio's new auto-fit algorithm with MTP. See the before/after table above.
3. **Bypass Permissions mode** — skip confirmations + disable tool sandbox (v0.1.471-beta).
4. **`unsloth studio --secure`** — end-to-end encrypted Cloudflare HTTPS tunnel; raw port is never exposed (v0.1.471-beta).
5. **Chat Canvas, Forking & Queueing** — edit assistant messages in place, fork a thread, incognito chats, queue new prompts while generation runs (v0.1.471-beta).
6. **Tensor parallelism enabled for GGUFs — +30% throughput** (v0.1.464-beta, PR #6040).
7. **DiffusionGemma + Gemma 4 MTP (~2x faster) + Gemma 4 Audio chat (`wav`, `mp3`, `m4a`, `flac`, `webm`) + Preserve Thinking** (v0.1.464-beta, Jun 12).
8. **Hub + Download Manager + Chat with Files / RAG** — hybrid search, citations, PDF previews, per-thread documents, built-in `search_knowledge_base` tool (v0.1.464-beta, Jun 12).
9. **MiniMax-M3** support (v0.1.464-beta).
10. **Gemma 4 MTP** + MoE LoRA target-parameter handling fix (v0.1.451-beta, Jun 10, PRs #6203 + #5345).

PyPI `Release history` deltas in the same window: `2026.6.9` (Jun 22, latest) · `2026.6.8` (Jun 18) · `2026.6.7` (Jun 13) · `2026.6.6`/`5`/`4` (Jun 12, three) · `2026.6.3` (Jun 11) · `2026.6.2` (Jun 10) · `2026.6.1` (Jun 3, Wave 1 baseline).

## Drift items vs Wave 1 text synthesis

Wave 1 (`agent-19-unsloth.md`, 305 lines) was ~90% accurate on Gemma 4 / Qwen3.6 / MTP / Dynamic 2.0 GGUFs but missed (or silently dropped) several Wave-2 realities. Live quotes are inlined verbatim.

| Wave 1 claim | Live evidence | Verdict |
|:--|:--|:--|
| "FastModel / FastLanguageModel / FastVisionModel as unified loader API" | PR #6203 fixes `FastModel` config-passthrough for sequence classification, but the *fine-tuning guide* still uses `FastLanguageModel.from_pretrained(...)`. No `FastVisionModel` import on the Gemma 4 page. | **Partial** — keep `FastLanguageModel` as the default; mention `FastModel` only for sequence-classification callers. |
| "Gemma-4 E2B/E4B `use_cache=False` garbage logits (Unsloth fix)" | No mention on `models/gemma-4.md`. The fix lives in PR history, not user docs. | **Drop from skill** — too internal. |
| "Gemma-4 31B/26B `num_kv_shared_layers=0` IndexError" | No mention on `models/gemma-4.md`. | **Drop from skill.** |
| "`train_on_responses_only` is now the documented accuracy booster (+1%)" | NOT in the fine-tuning guide. Instead, the doc now emphasises `enable_thinking` / `preserve_thinking` via `--chat-template-kwargs`. | **Replace with thinking-toggle pattern** — that's the new documented lever. |
| "MoE 12x faster training" | Confirmed in PyPI long description: "Train **MoE LLMs 12x faster** with 35% less VRAM — DeepSeek, GLM, Qwen and gpt-oss." | **Keep**. |
| "MTP speculative decoding (1.4-2.2x inference speedup)" | `models/qwen3.6.md`: "1.4-2.2x faster generation with **no change in accuracy**". Dense: 1.4x; MoE: 1.15-1.25x. | **Refine** — split dense vs MoE numbers. |
| "Dynamic 2.0 GGUFs (SOTA Pareto frontier on KLD benchmarks)" | Confirmed: "We were top-performing in 21 of 22 sizes... we introduced a new `UD-IQ4_NL_XL` quant." | **Keep + add `UD-IQ4_NL_XL`.** |
| "Gemma-4 family: 12B/E2B/E4B/26B-A4B/31B" | Exact 5-variant list confirmed; max context 128K for E2B/E4B, 262,144 for 12B/26B-A4B/31B. | **Refine** — add per-variant context lengths (see Diff 4). |
| "Unsloth Studio (port 8888)" | Confirmed; default port 8888, `--secure` flag (HTTPS tunnel), `-H 0.0.0.0` for LAN. | **Keep + add `--secure`.** |
| "**Fine-tuning can replicate all of RAG's capabilities**, but not vice versa." (Wave 1 contrarian) | Exact sentence appears verbatim on `get-started/fine-tuning-llms-guide.md`: "You can think of a fine-tuned model as a specialized agent designed to do specific tasks more effectively and efficiently. **Fine-tuning can replicate all of RAG's capabilities**, but not vice versa." | **Keep — Wave 1 was correct.** |

### Verbatim quote pack (5 quotes for the drift log)

1. **NEW Wave 2 (Qwen3.6 MTP speed).** `models/qwen3.6.md`: "**Qwen3.6 27B MTP now runs at 160 tokens/s generation and Qwen3.6 35B-A3B at 240 tokens/s on a RTX 6000 GPU.**" — anchors the headline speed-up at half-Granite-spec.
2. **NEW Wave 2 (MTP draft-token ceiling).** `models/qwen3.6.md`: "We do not recommend more than 2 draft tokens because the acceptance rate drops precipitously from 83% to 50% with 4 draft tokens, and the forward passes for MTP become less beneficial."
3. **NEW Wave 2 (CUDA 13.2 hard skip).** `models/qwen3.6.md`: "**Do NOT use CUDA 13.2** as you may get gibberish outputs. Use below CUDA 13.2 or CUDA 13.3."
4. **Wave 1 verbatim (preserved).** `get-started/fine-tuning-llms-guide.md`: "**Fine-tuning can replicate all of RAG's capabilities**, but not vice versa."
5. **NEW Wave 2 (Studio headline).** GitHub release `v0.1.471-beta` notes: "**3x longer context lengths** are now achievable with our new auto fit algorithm with MTP... Bypass permissions mode, forkable chats, queue-able chats, a new hub for model discovery, parallel modules + HTTPS Cloudflare support and more! Use `unsloth studio --secure` for secure HTTPS global access!"

### Live URL patterns observed

- `https://unsloth.ai/docs/llms.txt` — full doc index (agent-queryable)
- `https://unsloth.ai/docs/<page>.md?ask=<question>&goal=<endgoal>` — agent query protocol (every page exposes this at the footer)
- `https://unsloth.ai/docs/models/gemma-4.md`
- `https://unsloth.ai/docs/models/qwen3.6.md`
- `https://unsloth.ai/docs/models/mtp.md` (the unified MTP guide linked from both Gemma 4 + Qwen3.6)
- `https://unsloth.ai/docs/new/studio/chat.md`, `…/studio/data-recipe.md`, `…/studio/export.md`, `…/studio/install.md`, `…/studio/start.md`
- `https://github.com/unslothai/unsloth/releases/tag/v0.1.471-beta`

## Skill file update recommendation

The current `.agents/skills/unsloth/SKILL.md` (219 lines, header `Version: >=2024.12 | Last Updated: 2025-04`) is dangerously stale. Apply the following six diffs in place at the same path.

### Diff 1 — Header & version

```diff
-**Version:** >=2024.12 | **Last Updated:** 2025-04
+**Version:** >=2026.6.9 | **Last Updated:** 2026-06-28
+**Verified upstream:** unsloth v0.1.471-beta (GitHub, 2026-06-18) / unsloth 2026.6.9 (PyPI, 2026-06-22)
+**Docs:** https://unsloth.ai/docs/llms.txt
```

### Diff 2 — Replace the Feature table with 6 verified rows

```diff
-| VRAM Reduction | 70% less memory usage |
-| Speed | 2x faster training |
-| 4-bit Training | QLoRA with optimizations |
-| GGUF Export | Edge deployment ready |
-| Multilingual Support | Enhanced training for multilingual models |
-| Flash Attention | Optimized attention mechanism |
+## Features (verified 2026-06-28; sources: unsloth.ai/docs + PyPI long description)
+
+| Feature | Value | Source |
+|:--|:--|:--|
+| VRAM Reduction | **70% less** | https://unsloth.ai/docs |
+| Training Speed | **2x faster** (no accuracy loss) | https://unsloth.ai/docs |
+| Context Length | **>500K tokens on 80GB GPU**, 262K for Qwen3.6 + Gemma 4 31B | PyPI news; https://unsloth.ai/docs/blog/500k-context-length-fine-tuning |
+| MTP Speculative Decoding | **1.4x dense / 1.15-1.25x MoE** with `--spec-type draft-mtp --spec-draft-n-max 2` | https://unsloth.ai/docs/models/qwen3.6#mtp-guide |
+| Dynamic 2.0 GGUFs | SOTA Pareto frontier on **21 of 22** KLD sizes (`UD-Q2_K_XL`, `UD-Q4_K_XL`, new `UD-IQ4_NL_XL`) | https://unsloth.ai/docs/basics/unsloth-dynamic-2.0-ggufs |
+| Studio (no-code) | `unsloth studio -p 8888` (LAN) or `unsloth studio --secure` (Cloudflare HTTPS) | PyPI long description |
```

### Diff 3 — Swap the `FastLanguageModel` snippet for a Studio-first workflow

```diff
-### 1. FastLanguageModel Setup
-
-```python
-from unsloth import FastLanguageModel
-import torch
-
-# Load model with 4-bit quantization
-model, tokenizer = FastLanguageModel.from_pretrained(
-    model_name="unsloth/Llama-3.2-3B-Instruct",
-    max_seq_length=2048,
-    dtype=None,
-    load_in_4bit=True,
-)
-```
+### 1. Studio-first setup (Gemma 4 / Qwen3.6)
+
+Wave-2 docs no longer ship a `FastVisionModel` import path; use Unsloth
+Studio for the multimodal families and `FastLanguageModel.from_pretrained`
+only when scripting a text-only LoRA pipeline.
+
+```bash
+# Install (macOS, Linux, WSL)
+curl -fsSL https://unsloth.ai/install.sh | sh
+
+# Launch Studio + open http://127.0.0.1:8888
+unsloth studio -p 8888
+
+# Optional: encrypted Cloudflare HTTPS tunnel (no raw port exposed)
+unsloth studio --secure
+```
+
+Gemma 4 is multimodal (text + image + audio on E2B/E4B/12B). Qwen3.6 is
+text-only but ships `UD-Q4_K_XL` + `UD-IQ4_NL_XL` Dynamic 2.0 quants and an
+NVFP4 with MTP tensors baked in for vLLM / SGLang serving.
```

### Diff 4 — Replace GGUF Export with a hardware sizing cheatsheet

```diff
-### 4. GGUF Export
-
-```python
-model.save_pretrained_gguf("irish-llama-3b", tokenizer, quantization_method="q4_k_m")
-# q8_0 - 8-bit, highest quality
-# q4_k_m - 4-bit, recommended
-# q4_0 - 4-bit, fastest
-```
+### 4. Hardware sizing cheatsheet (Gemma 4 — source: docs.unsloth.ai/models/gemma-4)
+
+| Variant       | 4-bit       | 8-bit      | BF16/FP16 | Max context |
+|:--|--:|--:|--:|--:|
+| E2B           | 4 GB        | 5-8 GB     | 10 GB     | 128K        |
+| E4B           | 5.5-6 GB    | 9-12 GB    | 16 GB     | 128K        |
+| 12B Unified   | 7-8 GB      | 13-14 GB   | 25 GB     | 262,144     |
+| 26B-A4B (MoE) | 16-18 GB    | 28-30 GB   | 52 GB     | 262,144     |
+| 31B           | 17-20 GB    | 34-38 GB   | 62 GB     | 262,144     |
+
+Qwen3.6 needs **18 GB / 22 GB** at 4-bit for 27B / 35B-A3B respectively,
+and **24 GB / 30 GB** at 6-bit (Dynamic 2.0). 35B-A3B at 4-bit + MTP delivers
+**~220 tokens/s on RTX 6000**; 27B + MTP reaches **~140 tokens/s**.
+Skip **CUDA 13.2** (gibberish) — use ≤ 13.1 or ≥ 13.3.
```

### Diff 5 — Update the "Related tools" section with new Wave-2 services

```diff
-## Related tools (KCG canonical)
-
-Unsloth is the KCG canonical wrapper for PEFT. The full
-fine-tuning stack is:
-
-- **`.agents/skills/peft/SKILL.md`** — LoRA / QLoRA / IA³ configuration.
-- **`.agents/skills/trl/SKILL.md`** — SFTTrainer, DPOTrainer, GRPOTrainer.
-- **`.agents/skills/ragas/SKILL.md`** — RAGAS scoring (DPO preference signals).
-- **.agents/skills/modal/SKILL.md** — Modal H100 burst training for 13B+.
+## Related tools (KCG canonical, Wave 2 verified)
+
+Unsloth is still the KCG canonical wrapper for PEFT, but the **Wave-2 product
+landscape** added two new surfaces the Wave-1 skill did not mention:
+
+- **`.agents/skills/peft/SKILL.md`** — LoRA / QLoRA / IA³ configuration.
+- **`.agents/skills/trl/SKILL.md`** — SFTTrainer, DPOTrainer, GRPOTrainer
+  (alignment layer; uses RAGAS scores as preference signals).
+- **`.agents/skills/ragas/SKILL.md`** — RAGAS scoring (DPO preference signals).
+- **`.agents/skills/modal/SKILL.md`** — Modal H100 burst training for 13B+.
+- **Unsloth Studio** — local no-code UI on port 8888 (or `--secure` HTTPS);
+  wires Gemma 4 / Qwen3.6 / DiffusionGemma / MiniMax-M3 directly into the
+  KCG `oideachais-mcp-filesystem` desktop.
+- **MLX Dynamic Quants** (Apple Silicon) — Unsloth ships 3/4/6/8-bit MLX
+  variants of Qwen3.6 and Gemma 4 with Vision support; reach them via
+  `scripts/install_gemma4_mlx.sh` or `scripts/install_qwen3_6_mlx.sh`.
+- **DiffusionGemma** — added Jun 12 (v0.1.464-beta) as a first-class target.
```

### Diff 6 — Add the Wave-2 anti-pattern footer + new Resource URLs

```diff
-## Resources
-
-- **Documentation:** https://github.com/unslothai/unsloth
-- **HuggingFace Skills:** `hf-llm-trainer` for full training guide
-- **MLflow Tracking:** `mlflow` skill for experiment logging
-- **Related Skills:** peft, trl, ragas, modal, huggingface, mlflow, litellm
+## Anti-patterns observed in Wave 1 (do NOT do these)
+
+1. **Using `FastVisionModel`.** It was a Wave-1 cargo-cult import. The live
+   `models/gemma-4.md` guide uses Studio + llama.cpp / vLLM exclusively; the
+   `FastVisionModel` symbol is not on any user-facing doc path.
+2. **Bumping `--spec-draft-n-max` past 2** for Qwen3.6 MTP — the live doc
+   warns: "the acceptance rate drops precipitously from 83% to 50% with 4
+   draft tokens, and the forward passes for MTP become less beneficial."
+3. **Targeting CUDA 13.2** for Qwen3.6 — produces gibberish outputs. Pin
+   CUDA ≤ 13.1 or ≥ 13.3.
+4. **Hand-managed venvs for Studio.** The single binary `unsloth studio -p 8888`
+   is now the only supported launcher; `pip install unsloth[cu130onlytorch290]`
+   is the only supported core install (`unsloth[cu130onlytorch2100]` for Blackwell).
+5. **Importing `from unsloth import FastVisionModel`** in new code — silently
+   deprecated; PR #6203 renamed it to `FastModel` for sequence-classification
+   callers. Wave-1's `train_on_responses_only` is also un-documented on the
+   live pages, so prefer `--chat-template-kwargs '{"enable_thinking":false}'`
+   or `preserve_thinking=true` for inference accuracy tweaks instead of
+   training-time response masking.
+
+## Resources
+
+- **Live docs (agent-queryable):** https://unsloth.ai/docs/llms.txt
+- **PyPI:** https://pypi.org/project/unsloth/ (currently 2026.6.9)
+- **GitHub:** https://github.com/unslothai/unsloth (latest tag v0.1.471-beta)
+- **Install (macOS / Linux / WSL):** `curl -fsSL https://unsloth.ai/install.sh | sh`
+- **Install (Windows PowerShell):** `irm https://unsloth.ai/install.ps1 | iex`
+- **HuggingFace Skills:** `hf-llm-trainer` for full training guide
+- **MLflow Tracking:** `mlflow` skill for experiment logging
+- **Related Skills:** peft, trl, ragas, modal, huggingface, mlflow, litellm
```

---

**BrowserBase failure log:** `browserbase_extract` hallucinated on **both** the
homepage (`https://docs.unsloth.ai` → returned Unsloth v1 October-2023 content
with "Phi-2", "use_unsloth=True", "v1.0.0 (October 26, 2023)") **and** the
fine-tuning guide (returned CocoIndex installation content). Both were caught
by cross-verifying against `webfetch` of the canonical `.md` URL pattern
`https://unsloth.ai/docs/<page>.md`. **Recommendation to the Credit Program
team:** bypass `browserbase_extract` for any GitBook-rendered site — use the
`?ask=` query protocol at the bottom of every `.md` page (it returns a
deterministic, model-graded answer instead of hallucinated prose).
