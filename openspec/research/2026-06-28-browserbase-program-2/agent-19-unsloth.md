# Agent 19 — Unsloth (BrowserBase Program 2)

**Date:** 2026-06-28 22:10 UTC
**Program:** `2026-06-28-browserbase-program-2` (Wave 1, 25 parallel agents)
**Package:** Unsloth — fine-tuning library for LLMs
**Subagent:** research-platform (domain: ML/AI training)
**Budget used:** ~10 credits (Firecrawl only — BrowserBase sessions timed out)
**Prior art:** `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-32-unsloth.md` (read but not duplicated; updated below)

## TL;DR

Unsloth is the **canonical consumer-hardware fine-tuning framework** for the Cianfhoghlaim
OCR stack. Current upstream (2026-06-28): Unsloth 3.0+ now uses **`FastModel` /
`FastLanguageModel` / `FastVisionModel`** as the unified loader API, supports
**Gemma 4 (E2B/E4B/12B/26B-A4B/31B)**, **Qwen3.6 (27B + 35B-A3B)**, **MoE 12x
faster training**, **MTP speculative decoding (1.4-2.2x inference speedup)**,
**Dynamic 2.0 GGUFs** (SOTA Pareto frontier on KLD benchmarks), and **Unsloth
Studio** as the new cross-platform web UI (port 8888). Three critical upstream
patch categories affect our 11 OCR models: (1) Gemma-4 E2B/E4B `use_cache=False`
garbage logits (Unsloth fix), (2) Gemma-4 31B/26B `num_kv_shared_layers=0`
IndexError, (3) `train_on_responses_only` is now the documented accuracy
booster (+1% from QLoRA paper). Our `UnslothConfig.for_gaelic_ocr()` factory
in `cianfhoghlaim/ocr/training/training/unsloth_config.py:166` matches upstream
recommendations except we should **adopt `FastModel` (not `FastVisionModel`)**
and **add `train_on_responses_only` to `UnslothTrainer.train()`**.

## Code

| Path | Purpose |
|:--|:--|
| `cianfhoghlaim/ocr/training/training/unsloth_config.py` | Dataclass config (LoRA + Vision + Training) with 4 factory classmethods |
| `cianfhoghlaim/ocr/training/training/unsloth_trainer.py` | SFTTrainer wrapper around FastVisionModel + MLflow |
| `cianfhoghlaim/ocr/training/modal_finetune/modal_finetune/finetune_irish.py` | Modal-burst variant (FastVisionModel + LoRA + `save_pretrained_gguf`) |
| `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/irish_htr_dataset.py` | MNIST-style Irish HTR dataset generator (JSONL for Unsloth) |
| `cianfhoghlaim/ocr/_oideachais_src/vlm_finetune_comparison.py` | Multi-model fine-tune comparison pipeline |
| `cianfhoghlaim/scripts/_meaisinfhoghlaim/convert_hf_to_gguf.sh` | Pre-quantized GGUF cache (copy from unsloth HF repos) |

**Canonical Unsloth pattern from upstream docs (Gemma 4, June 2026):**

```python
from unsloth import FastModel          # NEW unified loader (supersedes FastVisionModel for Gemma 4)
import torch
from trl import SFTTrainer, SFTConfig

model, tokenizer = FastModel.from_pretrained(
    model_name = "unsloth/gemma-4-26B-A4B-it",
    max_seq_length = 8192,
    load_in_4bit = True,
    full_finetuning = False,
    # dtype=None,  # auto-detect (bf16 on M4)
)

# LoRA — note finetune_vision_layers / finetune_language_layers split
model = FastModel.get_peft_model(
    model,
    finetune_vision_layers     = False,   # Turn off for just text
    finetune_language_layers   = True,
    finetune_attention_modules = True,
    finetune_mlp_modules       = True,
    r = 16,                              # 16 for OCR; 64 for high-fidelity visual
    lora_alpha = 16,                     # α = r (recommended); α = 2r for aggressive
    lora_dropout = 0,                    # Unsloth-optimized at 0
    bias = "none",
    random_state = 3407,
    use_rslora = False,
    loftq_config = None,
)

# Use the gemma-4-thinking chat template (or "gemma-4" for non-thinking)
from unsloth.chat_templates import get_chat_template
tokenizer = get_chat_template(tokenizer, chat_template="gemma-4-thinking")

# Train
trainer = SFTTrainer(
    model=model, tokenizer=tokenizer, train_dataset=dataset,
    args=SFTConfig(
        per_device_train_batch_size=1, gradient_accumulation_steps=4,
        max_steps=60, learning_rate=2e-4,
        optim="adamw_8bit", lr_scheduler_type="linear", seed=3407,
        bf16=True, report_to="none",
    ),
)

# CRITICAL upstream-recommended accuracy booster (+1%):
from unsloth.chat_templates import train_on_responses_only
trainer = train_on_responses_only(
    trainer,
    instruction_part = "<|turn>user\n",
    response_part    = "<|turn>model\n",
)

trainer.train()

# Export to GGUF for llama-swap (5 quantization options + push_to_hub_gguf)
model.save_pretrained_gguf("./gemma-4-gaeilge", tokenizer, quantization_method="q4_k_m")
model.push_to_hub_gguf("cianmacandeisigh/gemma-4-gaeilge", tokenizer, quantization_method="q4_k_m")
```

**Canonical Qwen3.6 pattern (newer — uses MTP speculative decoding):**

```python
# Run inference with MTP (1.4-2.2x faster, NO accuracy loss)
./llama.cpp/llama-server \
  --model unsloth/Qwen3.6-35B-A3B-GGUF/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf \
  --mmproj unsloth/Qwen3.6-35B-A3B-GGUF/mmproj-F16.gguf \
  --alias "unsloth/Qwen3.6-35B-A3B" \
  --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.00 \
  --ctx-size 16384 --port 8001 \
  --spec-type draft-mtp --spec-draft-n-max 2     # ← MTP, recommended
```

## Env

| Env var | Value | Source | Notes |
|:--|:--|:--|:--|
| `UNSLOTH_CACHE_DIR` | `/Users/cianmacandeisigh/.cache/unsloth` | per-host | Cache for compiled kernels |
| `HF_HUB_CACHE` / `HF_HOME` | (defaults) | per-host | HF model cache (e.g. `~/.cache/huggingface/hub/`) |
| `JUPYTER_PORT` | `8888` | Docker | Jupyter inside unsloth/unsloth container |
| `JUPYTER_PASSWORD` | (random) | Locket | Set on first launch via `unsloth studio` |
| `SSH_KEY` | `~/.ssh/container_key.pub` | per-host | SSH public key for Docker container |
| `USER_PASSWORD` | (random) | Locket | Non-root `unsloth` user password (sudo-capable) |
| `MLFLOW_TRACKING_URI` | `mlruns` (local) / `http://mlflow.cianfhoghlaim.ie` (shared) | Locket | |
| `WANDB_DISABLED` | `true` | per-host | We use MLflow + Langfuse instead |
| `USE_LOCAL_SCRAPES` | `true` (default) | per-host | Cache fallback for OCR training data |
| `OLLAMA_HOST` | `http://127.0.0.1:11434` (local M4) | per-host | Test inference after GGUF export |

**Container CLI:** `unsloth studio -H 0.0.0.0 -p 8888` (then open `http://localhost:8888`)
**Docker run:**
```bash
docker run -d \
  -e JUPYTER_PASSWORD="$JUPYTER_PASSWORD" \
  -p 8888:8888 -p 8000:8000 -p 2222:22 \
  -v "$(pwd)/work:/workspace/work" \
  --device=nvidia.com/gpu=all \
  unsloth/unsloth
```

## CCC anchors

`cianfhoghlaim/ocr/training/training/unsloth_config.py:166` (`for_gaelic_ocr()`) ·
`cianfhoghlaim/ocr/training/training/unsloth_trainer.py:108` (`FastVisionModel.from_pretrained`) ·
`cianfhoghlaim/ocr/training/training/unsloth_trainer.py:121` (`get_peft_model` w/ vision split) ·
`cianfhoghlaim/ocr/training/training/unsloth_trainer.py:378` (`save_adapter`) ·
`cianfhoghlaim/ocr/training/training/unsloth_trainer.py:409` (`save_merged` → GGUF) ·
`cianfhoghlaim/ocr/training/modal_finetune/modal_finetune/finetune_irish.py:65` (Modal burst) ·
`openspec/changes/2026-06-28-browserbase-phase-2-decisions/specs/meaisinfhoghlaim-platform/spec.md:35` (canonical stack spec)

Search terms: `"FastVisionModel"`, `"save_pretrained_gguf"`, `"FastModel"`, `"train_on_responses_only"`, `"UnslothConfig"`, `"UnslothTrainer"`.

## Drift log

| Date | Event | Source |
|:--|:--|:--|
| 2025-Q4 | Initial Unsloth adoption (Gemma 2 OCR) | git history |
| 2026-02 | Added Qwen2.5-VL + Gemma 3 support | `unsloth_config.py:142` |
| 2026-04 | Added Irish-specific data collator (sínte fada normalization) | `irish_htr_dataset.py` |
| 2026-05 | Migrated to Gemma 4 + Qwen3.6 + GLM-4.6V families (11 models) | research/P2-32 |
| 2026-06-02 | Upstream: Gemma 4 12B Unified release | `unsloth.ai/docs/models/gemma-4` |
| 2026-06-05 | Upstream: Gemma 4 QAT variants release | same |
| 2026-06-09 | Upstream: Gemma 4 MTP release (1.4-2.2x inference speedup) | `unsloth.ai/docs/models/mtp` |
| 2026-06-15 | Upstream: Qwen3.6 release (27B + 35B-A3B MoE) | `unsloth.ai/docs/models/qwen3.6` |
| 2026-06-21 | Upstream: MTP support merged in llama.cpp PR #22673 | same |
| 2026-06-25 | Upstream: Unsloth Studio public release (Mac/Win/Linux) | `unsloth.ai/docs/new/studio` |
| 2026-06-28 | Upstream: Dynamic 2.0 GGUF algorithm (SOTA Pareto KLD) | `unsloth.ai/docs/basics/unsloth-dynamic-2.0-ggufs` |
| 2026-06-28 | **Local:** This research + recommended `FastModel` + `train_on_responses_only` migration | this file |

## Anti-patterns

1. ❌ **Don't use `dtype=torch.float16` on M-series** — use `bf16` (native hardware support, also `bf16=True` in SFTConfig).
2. ❌ **Don't use `load_in_4bit=False` for Gemma 4 26B-A4B MoE** — Unsloth docs explicitly say `load_in_16bit=True` works, but QLoRA is recommended for 31B (which needs 22GB VRAM).
3. ❌ **Don't use `optim="adamw_torch"`** — `adamw_8bit` saves ~40% memory; same accuracy.
4. ❌ **Don't skip `use_gradient_checkpointing="unsloth"`** — saves 30% more VRAM than `True` and supports extremely long context (262K tokens for Gemma 4 12B/26B/31B).
5. ❌ **Don't use `lora_dropout=0.1` by default** — Unsloth is optimized for `0`; use 0.1 only if overfitting (loss < 0.2).
6. ❌ **Don't skip `train_on_responses_only`** — QLoRA paper says +1% accuracy, especially on multi-turn Irish conversational data.
7. ❌ **Don't use `np.allclose()` to verify LoRA updates** — LoRA A is initialized with small Gaussian; use checksum/MD5 or `np.array_equal()`.
8. ❌ **Don't use target_modules = `["q_proj"]` only** — apply to all 7 major linear layers (`q/k/v/o_proj` + `gate/up/down_proj`).
9. ❌ **Don't mix chat templates between training and export** — most gibberish-on-Ollama reports trace to wrong `eos_token` or template.
10. ❌ **Don't use `random_state=42`** — Unsloth convention is `3407` (matches their notebooks, ensures reproducibility).
11. ❌ **Don't use `lora_alpha = r * 4` or higher** — heuristic is `α = r` (standard) or `α = 2r` (aggressive); above 2r destabilizes training.
12. ❌ **Don't use the wrong Gemma 4 chat template** — `gemma-4` for non-thinking, `gemma-4-thinking` for the 26B/31B; never mix both in one dataset.
13. ❌ **Don't ignore Gemma 4 E2B/E4B multimodal quirk** — loss of 13-15 is **NORMAL** (also happens on Gemma 3N, Llama Vision, Mistral vision).
14. ❌ **Don't use CUDA 13.2 with Qwen3.6** — produces gibberish; use <13.2 or 13.3+.

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Loader API | `FastModel` (new) over `FastVisionModel` | Upstream unified loader in 3.0+; FastVisionModel deprecated for Gemma 4 |
| Gemma 4 base model | `unsloth/gemma-4-26B-A4B-it` | Best speed/quality tradeoff; MoE w/ 4B active; 18GB VRAM (4-bit) fits M4 Max |
| Qwen3.6 base model | `unsloth/Qwen3.6-35B-A3B-GGUF` for inference; `unsloth/Qwen3.6-35B-A3B-it` for FT | 22GB VRAM (4-bit); 256K context; supports 201 languages incl. Irish |
| Quantization | QLoRA 4-bit (`load_in_4bit=True`) | 70% VRAM reduction; matches existing `for_gaelic_ocr()` |
| LoRA rank | `r=64` for vision OCR (current); `r=16` for text-only | r=64 captures Gaelic script nuance; r=16 is upstream default |
| LoRA alpha | `α = r` (standard) | Upstream recommendation; α/r = 1 |
| LoRA target_modules | `["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"]` | All 7 major linear layers (current code matches) |
| LoRA dropout | `0` | Unsloth optimized at 0 (current code matches) |
| Bias | `"none"` | Optimized path |
| Optimizer | `adamw_8bit` | 40% memory savings; same accuracy (current code matches) |
| Scheduler | `cosine` (vision), `linear` (text) | Standard pattern (current code matches) |
| `use_gradient_checkpointing` | `"unsloth"` | 30% extra VRAM savings (current code uses `True` — should change) |
| `random_state` | `3407` | Upstream convention (current uses `42` — should change) |
| `train_on_responses_only` | **YES** (always) | QLoRA paper: +1% accuracy on multi-turn (NOT yet in current trainer) |
| Vision layer FT | `finetune_vision_layers=True` for OCR; `False` for text-only | Current code defaults `True` (correct for OCR) |
| Full FT | `full_finetuning=False` (LoRA only) | Full 26B FT needs >100GB VRAM |
| Max seq length | `4096` for OCR (current); `8192` for long-context Gemma 4 | Matches each notebook |
| Batch size | `per_device_train_batch_size=2 × gradient_accumulation=4 = 16 effective` | Upstream recommended |
| Learning rate | `2e-4` | Upstream LoRA/QLoRA standard |
| Epochs | `1-3` | Upstream: >3 epochs risks overfitting on instruction data |
| Chat template (Gemma 4) | `gemma-4-thinking` (26B/31B), `gemma-4` (E2B/E4B) | Match base model variant |
| Chat template (Qwen3.6) | `qwen2.5` or built-in Qwen | Qwen3.6 uses Qwen2.5 template |
| Weight decay | `0.001` (current) — upstream says `0.01` | Consider bumping to 0.01 |
| Warmup steps | `5-10%` of total; current `100` (good) | Standard |
| Saving | `save_pretrained_gguf` then `push_to_hub_gguf` | Required for llama-swap local serving |
| GGUF quantization | `q4_k_m` (default), `UD-Q4_K_XL` (Dynamic 2.0) | `UD-Q4_K_XL` is SOTA Pareto on KLD |
| Export format | GGUF (not safetensors) | Required by llama.cpp + llama-swap |
| MTP (inference only) | `--spec-type draft-mtp --spec-draft-n-max 2` | 1.4-2.2x speedup; >2 hurts acceptance rate |
| Container runtime | Docker (NVIDIA Container Toolkit) | Blackwell-compatible; non-root user |
| Local dev (Mac) | `curl -fsSL https://unsloth.ai/install.sh \| sh` then `unsloth studio -H 0.0.0.0 -p 8888` | Native Apple Silicon |
| Cloud burst (>48 GB) | Modal A100 + `modal_unsloth.py` (already exists) | For 70B+ models |
| GGUF consumer | llama-swap (port 7777) on M4 Max | `gemma-3-vision` config already exists |

## §8 — Refactor opportunities (Unsloth patterns we could adopt)

These are the upstream-recommended patterns that our codebase could adopt to
match the current state of Unsloth 3.0+:

1. **Migrate `FastVisionModel` → `FastModel`** (`unsloth_trainer.py:108`,
   `unsloth_trainer.py:121`). Upstream unified loader in 3.0+ supports
   text+vision+audio without three different classes. Auto-handles Gemma 4
   multimodal vs text-only dispatch.

2. **Add `train_on_responses_only` to trainer** (`unsloth_trainer.py:278`,
   `train()` method). After SFTTrainer construction, wrap with
   `unsloth.chat_templates.train_on_responses_only(trainer, instruction_part,
   response_part)` to gain +1% accuracy on multi-turn Irish conversational data.
   Must be parameterised by chat template (different `instruction_part` /
   `response_part` for Gemma 4 vs Llama 3 vs Qwen 2.5).

3. **Add `use_rslora` + `loftq_config` to LoRAConfig** (`unsloth_config.py:30`).
   Currently `use_rslora=False` and `loftq_config=None` are hardcoded in
   `unsloth_trainer.py:132-133`. Expose them as `LoRAConfig` fields so users
   can opt into rank-stabilized LoRA or LoftQ initialisation.

4. **Adopt upstream `random_state=3407` convention** (`unsloth_config.py:103`
   hardcodes `seed=42`; should match upstream notebooks `3407` for
   reproducibility when comparing against published Unsloth benchmarks).

5. **Add `QAT` model variants to config** (`UnslothConfig.for_gaelic_ocr()`).
   Gemma 4 QAT (`unsloth/gemma-4-26B-A4B-it-QAT-GGUF`) reduces memory ~3x
   while preserving quality — relevant for low-spec edge devices.

6. **Add `MTP` (Multi-Token Prediction) inference helper**. New
   `unsloth/ocr/training/inference/llama_server_mtp.py` wrapper that calls
   `llama-server` with `--spec-type draft-mtp --spec-draft-n-max 2` for
   Qwen3.6 / Gemma 4 MTP GGUFs (1.4-2.2x inference speedup, zero accuracy loss).

7. **Add `UnslothVisionDataCollator` integration** (upstream class from
   `unsloth.trainer`). Current code uses default TRL collator;
   `UnslothVisionDataCollator(model, processor)` enables
   `train_on_responses_only`-equivalent for VLMs.

8. **Promote `unsloth.Dynamic 2.0` GGUF as default export**. Our code uses
   `q4_k_m`; upstream recommends `UD-Q4_K_XL` (SOTA Pareto on KLD benchmark,
   `q4_k_m`-class size, better accuracy). Add `--quantization-method ud-q4_k_xl`
   option to `save_merged()`.

9. **Migrate vision fine-tuning booleans to FastModel API**.
   `unsloth_trainer.py:122-127` passes `finetune_vision_layers`,
   `finetune_language_layers`, `finetune_attention_modules`,
   `finetune_mlp_modules` — these are now first-class on `FastModel.get_peft_model`
   (current code already correct; just verify against v3 API docs).

10. **Add `Unsloth Studio` invocation as backup training path**.
    `unsloth studio -H 0.0.0.0 -p 8888` exposes a web UI; could be packaged as
    a Mise task `mise run unsloth:studio` for non-CLI users.

11. **Replace `seed=42` with `seed=3407` in `unsloth_config.py:103`** + bump
    `weight_decay` from `0.001` to upstream-recommended `0.01`.

12. **Add `Gemma 4 multimodal loss-curve normalisation`** to evaluation harness.
    Upstream docs warn: "E2B/E4B loss of 13-15 is NORMAL"; our
    `evaluation/harness_unsloth.py` (not yet located) likely flags this as
    a failure. Add `EXPECTED_LOSS_BY_MODEL: dict[str, tuple[float, float]]`.

13. **Pre-cache `unsloth/unsloth` Docker image** in Mise/CI. Image is 13.1 GB;
    pulling on every Modal job costs ~5 min. `mise run unsloth:pull` task.

14. **Replace `target_modules=List[str]` with `target_modules="all-linear"`**
    option (new in upstream). Upstream says `all-linear` matches or beats
    explicit list for most models; saves boilerplate.

15. **Use `curated_max_pixels` formula from new Gemma 4 docs**. Current code uses
    `min_pixels=256*28*28` (200,704) and `max_pixels=1280*28*28` (1,003,520) —
    matches upstream default, good. Document this in `VisionConfig` docstring
    to explain the `28*28` Qwen-VL image factor.

## Files to read next

- `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-32-unsloth.md` (prior art, 131 lines)
- `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-33-modal.md` (Modal-burst variant, `modal_unsloth.py`)
- `openspec/changes/2026-06-28-browserbase-phase-2-decisions/specs/meaisinfhoghlaim-platform/spec.md` (canonical stack spec)
- `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md` (10 OCR models across 6 backends)
- `.agents/skills/unsloth/SKILL.md` (skill canonical docs)
- `unsloth.ai/docs/models/gemma-4/train` (training guide — 178 lines, copied verbatim above)
- `unsloth.ai/docs/models/qwen3.6#mtp-guide` (MTP speculative decoding)
- `unsloth.ai/docs/get-started/fine-tuning-llms-guide/lora-hyperparameters-guide` (canonical LoRA defaults)
- `hub.docker.com/r/unsloth/unsloth` (Docker image, 13.1 GB, Blackwell-compatible)