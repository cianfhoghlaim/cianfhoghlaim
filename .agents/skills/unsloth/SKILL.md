---
name: unsloth
description: Efficient LLM fine-tuning with 70% VRAM reduction and 2x speedup. Essential for training Irish language models on consumer hardware.
---

# Unsloth

**Version:** >=2026.6.9 | **Last Updated:** 2026-06-28
**Verified upstream:** unsloth v0.1.471-beta (GitHub, 2026-06-18) / unsloth 2026.6.9 (PyPI, 2026-06-22)
**Docs:** https://unsloth.ai/docs/llms.txt

## Overview

Unsloth enables efficient fine-tuning of large language models with dramatically reduced memory requirements, making it possible to train Irish language models on consumer GPUs.

| Feature | Description |
|---------|-------------|
| VRAM Reduction | 70% less memory usage |
| Speed | 2x faster training |
| 4-bit Training | QLoRA with optimizations |
| GGUF Export | Edge deployment ready |
| Multilingual Support | Enhanced training for multilingual models |
| Flash Attention | Optimized attention mechanism |

## When to Use This Skill

Activate when users need:

- "Fine-tune Irish language model"
- "Train model with limited GPU memory"
- "Export model to GGUF for Ollama"
- "Reduce training time for LLM"
- "Run SFT/DPO training efficiently"

## Project Integration

### Research References (taighde/)

| Directory | Relevant Documents |
|-----------|-------------------|
| `taighde/meaisinfhoghlaim/` | Training guides, LoRA configs |
| `taighde_teanga/` | Irish NLP datasets |

### ML Model Dependencies (agents/meaisinfhoghlaim/)

| Model | Usage |
|-------|-------|
| UCCIX-Llama2-13B | Irish text generation |
| Llama-3.2-3B | Base for Irish fine-tuning |
| Qwen2.5-Math-7B | Math reasoning |

## Core Concepts

### 1. FastLanguageModel Setup

```python
from unsloth import FastLanguageModel
import torch

# Load model with 4-bit quantization
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.2-3B-Instruct",
    max_seq_length=2048,
    dtype=None,  # Auto-detect
    load_in_4bit=True,  # 70% VRAM reduction
)
```

### 2. LoRA Configuration

```python
# Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r=64,  # Rank - higher = more capacity
    lora_alpha=128,  # Scaling factor
    lora_dropout=0.05,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    bias="none",
    use_gradient_checkpointing="unsloth",  # Essential for long contexts
    random_state=42,
)
```

### 3. SFT Training

```python
from trl import SFTTrainer
from transformers import TrainingArguments

# Irish curriculum dataset
dataset = load_dataset("cianfhoghlaim/irish-curriculum-qa")

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        num_train_epochs=3,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=10,
        output_dir="outputs",
        optim="adamw_8bit",
        seed=42,
    ),
)

trainer.train()
```

### 4. GGUF Export

```python
# Save to GGUF for Ollama/llama.cpp
model.save_pretrained_gguf(
    "irish-llama-3b",
    tokenizer,
    quantization_method="q4_k_m"  # Good quality/size balance
)

# Alternative quantization methods:
# q8_0 - 8-bit, highest quality
# q4_k_m - 4-bit, recommended
# q4_0 - 4-bit, fastest
```

## Cianfhoghlaim-Specific Usage

### Irish Language Fine-Tuning

```python
from datasets import load_dataset

# Load Irish curriculum Q&A dataset
def format_irish_qa(example):
    return {
        "text": f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
Is cúntóir oideachais Gaeilge tú. Freagraigh i nGaeilge.
<|eot_id|><|start_header_id|>user<|end_header_id|>
{example['question']}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
{example['answer']}<|eot_id|>"""
    }

dataset = load_dataset("cianfhoghlaim/irish-qa").map(format_irish_qa)

# Train with Irish-specific settings
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset["train"],
    args=TrainingArguments(
        learning_rate=5e-5,  # Lower LR for Irish
        num_train_epochs=5,  # More epochs for low-resource
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
    ),
)
```

### MLflow Integration

```python
import mlflow

mlflow.set_tracking_uri("http://mlflow.cianfhoghlaim.ie")
mlflow.set_experiment("irish-llm-training")

with mlflow.start_run():
    mlflow.log_params({
        "model": "Llama-3.2-3B",
        "rank": 64,
        "alpha": 128,
        "dataset": "irish-curriculum-qa"
    })

    trainer.train()

    mlflow.log_metrics({
        "train_loss": trainer.state.log_history[-1]["loss"],
        "epochs": 3
    })
```

## Best Practices

1. **Use gradient checkpointing** - Enables longer contexts
2. **Start with lower learning rate for Irish** - Low-resource language
3. **More epochs for Irish** - Compensate for limited data
4. **Export to GGUF** - Deploy with Ollama for inference

## Related tools (KCG canonical)

Unsloth is the KCG canonical wrapper for PEFT. The full
fine-tuning stack is:

- **`.agents/skills/peft/SKILL.md`** — LoRA / QLoRA / IA³
  configuration (the base technology Unsloth wraps)
- **`.agents/skills/trl/SKILL.md`** — SFTTrainer, DPOTrainer,
  GRPOTrainer (the alignment layer; uses RAGAS scores as
  preference signals)
- **`.agents/skills/ragas/SKILL.md`** — RAGAS scoring (the
  source of DPO preference signals)
- **`.agents/skills/modal/SKILL.md`** — Modal H100 burst
  training for 13B+ models

## Resources

- **Documentation:** https://github.com/unslothai/unsloth
- **HuggingFace Skills:** `hf-llm-trainer` for full training guide
- **MLflow Tracking:** `mlflow` skill for experiment logging
- **Related Skills:** peft, trl, ragas, modal, huggingface, mlflow, litellm
