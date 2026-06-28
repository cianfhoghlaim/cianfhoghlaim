# P2-23 — huggingface (Phase 2, Agent-Platform)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** agent-platform

## TL;DR

HuggingFace is the **model hub** for the 11 OCR vision models + 4 text models that power the Cianfhoghlaim agent fleet. It's where new models are downloaded from (gguf/MLX formats) and where fine-tuned checkpoints are uploaded to for backup.

The canonical Cianfhoghlaim pattern: all model artifacts live in 2 places — HuggingFace Hub (public, versioned) and MLflow (local, private). HF is for the source-of-truth model releases; MLflow is for fine-tuned variants + tracking.

## Code

| Path | Purpose |
|:--|:--|
| `stacks/huggingface/` | (No local deploy — HF Hub is the cloud service) |
| `oideachais/ocr/models/registry.py` | HF model registry (11 vision + 4 text) |
| `oideachais/ocr/models/unsloth_finetune.py` | Downloads base models from HF Hub |
| `cognify/rules/huggingface_models.py` | Lists 15 active HF models |

**Canonical HF model registry** (`oideachais/ocr/models/registry.py`):

```python
HF_MODELS = {
    "vision": {
        "gemma-4-31b-it": "unsloth/gemma-4-31B-it-GGUF",
        "gemma-4-26b-a4b-it": "unsloth/gemma-4-26B-A4B-it-GGUF",
        "gemma-4-e4b-it": "unsloth/gemma-4-E4B-it-GGUF",
        "gemma-4-e2b-it": "unsloth/gemma-4-E2B-it-GGUF",
        "qwen3.6-27b": "unsloth/Qwen3.6-27B-Instruct-GGUF",
        "qwen3.6-27b-mlx-8bit": "unsloth/Qwen3.6-27B-Instruct-MLX-8bit",
        "qwen3.6-35b-a3b": "unsloth/Qwen3.6-35B-A3B-Instruct-GGUF",
        "qwen3.6-35b-a3b-mlx": "unsloth/Qwen3.6-35B-A3B-Instruct-UD-MLX-4bit",
        "glm-4.6v-flash": "unsloth/GLM-4.6V-Flash-GGUF",
        "phi-3-vision": "microsoft/Phi-3-vision-128k-instruct",
        "llava-1.6": "llava-hf/llava-1.6-mistral-7b-hf",
    },
    "text": {
        "qwen2.5-math-7b": "Qwen/Qwen2.5-Math-7B-Instruct-GGUF",
        "mistral-nemo-12b": "mistralai/Mistral-Nemo-Instruct-2407-GGUF",
        "llama-3.3-70b": "meta-llama/Llama-3.3-70B-Instruct-GGUF",
        "gaelic-tinyllama": "TinyLlama/TinyLlama-1.1B-Chat-v1.0-GGUF",
    }
}
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `HF_TOKEN` | `infisical://dev-baile/huggingface/token` | Locket |
| `HF_HUB_CACHE` | `/Users/cianmacandeisigh/.cache/huggingface` | per-host |
| `HF_DATASETS_CACHE` | `/Users/cianmacandeisigh/.cache/huggingface/datasets` | per-host |

## CCC anchors

`oideachais/ocr/models/registry.py` · `oideachais/ocr/models/unsloth_finetune.py` · `cognify/rules/huggingface_models.py`

Search terms: `"HF_MODELS"`, `"unsloth/"`, `"MLX"`, `"GGUF"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-08 | Initial HF model registry (3 models) |
| 2025-12 | Expanded to 11 vision + 4 text |
| 2026-04 | Migrated from raw llama-cpp to unsloth/MacX-omni for inference |
| 2026-05 | Added HF Spaces deployment for demo apps |

## Anti-patterns

1. Don't download models at runtime — pre-download via `huggingface-cli download`
2. Don't use `transformers` directly for inference — use `llama-cpp`, `mlx-omni`, or `unsloth`
3. Don't commit model weights to git — they're already in HF Hub
4. Don't use the free HF tier for production — use Pro ($9/mo) for higher rate limits

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Hub | HuggingFace Hub | Largest model ecosystem |
| Tier | Pro ($9/mo) | Higher rate limits for production |
| Inference | llama-cpp (GGUF) + mlx-omni (MLX) | Native formats per platform |
| Versioning | Git LFS on HF (for model cards) | Versioned model artifacts |
| Storage | HF Hub (not local) | No local disk bloat |
| Fine-tuned models | HF Hub (public) + MLflow (private) | Two-tier storage |

## Files to read next

`oideachais/ocr/models/registry.py` · `oideachais/ocr/models/unsloth_finetune.py` · `cognify/rules/huggingface_models.py` · `.agents/skills/huggingface/SKILL.md`
