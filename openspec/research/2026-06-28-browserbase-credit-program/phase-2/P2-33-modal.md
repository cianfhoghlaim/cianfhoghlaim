# P2-33 — modal (Phase 2, Agent-Platform, NEW per user request)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages — NEW per user request)
**Budget:** ~60 credits
**Subagent:** agent-platform

## TL;DR

Modal is the **serverless GPU cloud** for burst ML training/inference (Unsloth fine-tuning jobs >5 minutes, or models too large for the M4 Max). The canonical Cianfhoghlaim pattern uses Modal as an **overflow compute layer** when the local M4 Max is saturated (or the model is >48 GB).

The 2 NEW Phase 2 prompts per user request: P2-32 unsloth (local) + P2-33 modal (cloud). Modal complements Unsloth — local for routine fine-tuning, cloud for burst capacity.

## Code

| Path | Purpose |
|:--|:--|
| `oideachais/agents/tuatha/modal_finetune.py` | Modal app for tuatha MMO asset generation |
| `oideachais/ocr/models/modal_unsloth.py` | Modal wrapper for Unsloth fine-tuning |
| `stacks/modal/` | (No local deploy — Modal is cloud-only) |
| `cognify/rules/modal_secrets.py` | Lists 3 Modal secrets |

**Canonical Modal app** (`oideachais/ocr/models/modal_unsloth.py`):

```python
import modal
from pathlib import Path

# Define a Modal image with Unsloth + CUDA
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git")
    .pip_install("torch==2.3.0", "transformers==4.41.0", "datasets==2.19.0")
)

app = modal.App("cianfhoghlaim-ocr-finetune", image=image)

# Persistent volume for model checkpoints
volume = modal.Volume.from_name("cianfhoghlaim-models", create_if_missing=True)

@app.function(
    gpu=modal.gpu.A100(count=1),  # or H100 for larger models
    timeout=60 * 60 * 4,  # 4 hours max
    volumes={"/models": volume},
    secrets=[modal.Secret.from_name("infisical-modal")],
)
def finetune_irish_ocr(
    base_model: str = "unsloth/gemma-4-26B-A4B-it",
    dataset_path: str = "oideachais/ocr/models/datasets/gaeilge_ocr.jsonl",
    epochs: int = 3,
):
    """Fine-tune an OCR model on Irish data with A100 GPU."""
    from unsloth import FastVisionModel
    from trl import SFTTrainer, SFTConfig

    # Load model + LoRA (same as local, but with CUDA)
    model, tokenizer = FastVisionModel.from_pretrained(
        model_name=base_model,
        max_seq_length=2048,
        load_in_4bit=True,
    )
    model = FastVisionModel.get_peft_model(
        model, r=16, target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_alpha=32,
    )

    from datasets import load_dataset
    dataset = load_dataset("json", data_files=dataset_path, split="train")

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=SFTConfig(
            per_device_train_batch_size=4,
            num_train_epochs=epochs,
            learning_rate=2e-4,
            bf16=True,
            optim="adamw_8bit",
            output_dir="/models/unsloth-irish-ocr",
        ),
    )
    trainer.train()
    model.save_pretrained_gguf("/models/unsloth-irish-ocr-GGUF", tokenizer, quantization_method="q4_k_m")
    volume.commit()
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `MODAL_TOKEN_ID` | `infisical://dev-baile/modal/token_id` | Locket |
| `MODAL_TOKEN_SECRET` | `infisical://dev-baile/modal/token_secret` | Locket |
| `INFISICAL_TOKEN_ID` | `infisical://dev-baile/infisical/universal_auth_client_id` | Locket |
| `INFISICAL_TOKEN_SECRET` | `infisical://dev-baile/infisical/universal_auth_client_secret` | Locket |

## CCC anchors

`oideachais/agents/tuatha/modal_finetune.py` · `oideachais/ocr/models/modal_unsloth.py` · `cognify/rules/modal_secrets.py`

Search terms: `"modal.App"`, `"modal.gpu.A100"`, `"modal.Volume"`, `"modal.Secret.from_name"`.

## Drift log

| Date | Event |
|--:|:--|
| 2026-04 | Initial Modal adoption (tuatha asset generation) |
| 2026-06 | Wired Modal to Infisical for secrets |

## Anti-patterns

1. Don't use Modal for routine fine-tuning (use Unsloth locally on M4 Max) — only for burst capacity
2. Don't run Modal apps on the free tier — use the $30/mo Pro tier for higher GPU quotas
3. Don't skip the `volume.commit()` call — without it, trained models are lost on app shutdown
4. Don't hardcode secrets in Modal apps — use `modal.Secret.from_name`
5. Don't use Modal for production inference (latency) — use llama-swap locally

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Use case | Burst training (Unsloth on cloud GPU) | Local M4 Max has 48 GB cap |
| GPU | A100 (40 GB) for 7B-26B; H100 (80 GB) for 70B | Match model size |
| Region | us-east-1 | Closest to Lakehouse (Garage S3) |
| Secrets | Infisical Universal Auth (via modal.Secret.from_name) | Same secret store as local |
| Volume | Persistent (cianfhoghlaim-models) | Survives app shutdowns |
| Cost | Pro tier ($30/mo base + GPU usage) | ~$1-3/hr for A100 |

## Files to read next

`oideachais/agents/tuatha/modal_finetune.py` · `oideachais/ocr/models/modal_unsloth.py` · `cognify/rules/modal_secrets.py` · `.agents/skills/modal/SKILL.md`
