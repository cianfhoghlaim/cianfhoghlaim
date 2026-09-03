# P2-32 — unsloth (Phase 2, Agent-Platform, NEW per user request)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages — NEW per user request)
**Budget:** ~60 credits
**Subagent:** agent-platform

## TL;DR

Unsloth is the **fine-tuning library** for the 11 OCR vision models (Gemma 4 + Qwen3.6 + GLM-4.6V families). It achieves **70% VRAM reduction** + **2x speedup** vs vanilla HF Transformers, enabling fine-tuning of 27B models on the MacBook M4 Max (48 GB unified memory). It's the canonical "fine-tune on consumer hardware" pattern for the Irish-language OCR stack.

The canonical Cianfhoghlaim pattern uses Unsloth's `FastVisionModel` + `SFTTrainer` + a custom GAELIC-specific data collator for handling accented characters (sínte fada normalization).

## Code

| Path | Purpose |
|:--|:--|
| `oideachais/ocr/models/unsloth_finetune.py` | The Unsloth fine-tuning script |
| `oideachais/ocr/models/datasets/gaeilge_ocr.jsonl` | Irish-language OCR training data (JSONL) |
| `oideachais/ocr/models/datasets/irish_handwriting.jsonl` | Irish handwriting training data |
| `oideachais/ocr/evaluation/harness_unsloth.py` | Evaluation harness for Unsloth models |
| `cognify/rules/unsloth_register_to_mlflow.py` | Dagster asset for MLflow registration |

**Canonical Unsloth fine-tuning script** (`oideachais/ocr/models/unsloth_finetune.py`):

```python
from unsloth import FastVisionModel
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset
import torch

def finetune_irish_ocr(
    base_model: str = "unsloth/gemma-4-26B-A4B-it-GGUF",
    dataset_path: str = "oideachais/ocr/models/datasets/gaeilge_ocr.jsonl",
    epochs: int = 3,
    batch_size: int = 4,
    lr: float = 2e-4,
):
    """Fine-tune Gemma 4 26B on Irish OCR data via Unsloth + LoRA."""
    # 1. Load model with 4-bit quantization (QLoRA)
    model, tokenizer = FastVisionModel.from_pretrained(
        model_name=base_model,
        max_seq_length=2048,
        load_in_4bit=True,
        dtype=None,  # auto-detect (bf16 on M4)
    )
    # 2. Add LoRA adapters
    model = FastVisionModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_alpha=32,
        use_gradient_checkpointing="unsloth",
    )
    # 3. Load Irish OCR dataset
    dataset = load_dataset("json", data_files=dataset_path, split="train")
    # 4. Train
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=SFTConfig(
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=4,
            num_train_epochs=epochs,
            learning_rate=lr,
            fp16=False,
            bf16=True,  # M4 native
            optim="adamw_8bit",
            output_dir="./unsloth-irish-ocr",
            save_strategy="epoch",
            logging_steps=10,
        ),
    )
    trainer.train()
    # 4. Save GGUF quantization for llama-swap
    model.save_pretrained_gguf("./unsloth-irish-ocr-GGUF", tokenizer, quantization_method="q4_k_m")
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `UNSLOTH_CACHE_DIR` | `/Users/cianmacandeisigh/.cache/unsloth` | per-host |
| `UNSLOTH_DISABLE_AUTO_UPDATE` | `true` | per-host (avoid surprise updates) |
| `MLFLOW_TRACKING_URI` | (shared) | Locket |
| `HF_TOKEN` | `infisical://dev-baile/huggingface/token` | Locket |
| `WANDB_DISABLED` | `true` | per-host (we use Langfuse + MLflow) |

## CCC anchors

`oideachais/ocr/models/unsloth_finetune.py` · `oideachais/ocr/models/datasets/` · `cognify/rules/unsloth_register_to_mlflow.py` · `stacks/mlflow/`

Search terms: `"FastVisionModel"`, `"SFTTrainer"`, `"load_in_4bit=True"`, `"save_pretrained_gguf"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-Q4 | Initial Unsloth adoption (Gemma 2 OCR) |
| 2026-02 | Added Qwen2.5-VL + Gemma 3 support |
| 2026-04 | Added Irish-specific data collator (sínte fada normalization) |
| 2026-05 | Migrated to Gemma 4 + Qwen3.6 + GLM-4.6V families (11 models) |
| 2026-06 | Added GGUF quantization pipeline (for llama-swap local inference) |

## Anti-patterns

1. Don't use `load_in_4bit=False` — QLoRA is the whole point of Unsloth
2. Don't skip `use_gradient_checkpointing="unsloth"` — uses 30% less VRAM than vanilla
3. Don't fine-tune without LoRA — full FT on a 26B model needs >100GB VRAM
4. Don't use `optim="adamw_torch"` — `adamw_8bit` saves 40% memory
5. Don't skip GGUF export — without it, models can't be served via llama-swap
6. Don't train on the full leabharlann corpus (2,395 docs) — start with 100 doc subset
7. Don't use `dtype=torch.float16` on M-series — use `bf16` (native hardware support)

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Base model | Gemma 4 26B (QLoRA 4-bit) | Best multilingual support (Irish + Welsh + Scottish) |
| Quantization | 4-bit (QLoRA) | 70% VRAM reduction |
| LoRA rank | 16 | Balance accuracy + memory |
| Batch size | 4 × 4 gradient_accumulation = effective 16 | Stable gradients |
| Optimizer | adamw_8bit | Memory efficient |
| Dataset format | JSONL (image + transcription pairs) | Standard + tooling |
| Evaluation | CER + WER + manual review | Multilingual metrics |
| Export format | GGUF Q4_K_M | llama-swap consumption |

## Files to read next

`oideachais/ocr/models/unsloth_finetune.py` · `oideachais/ocr/models/datasets/gaeilge_ocr.jsonl` · `cognify/rules/unsloth_register_to_mlflow.py` · `.agents/skills/unsloth/SKILL.md`
