---
name: trl
description: HuggingFace TRL — SFT (SFTTrainer), DPO (DPOTrainer), GRPO (GRPOTrainer), reward modeling (RewardTrainer). Use for preference optimization, alignment training, and the RAGAS-as-DPO-preference-signal pattern in the KCG curriculum pipeline.
---

# TRL — Transformer Reinforcement Learning

## When to use this skill

Use when you need to:

- "Fine-tune a 7B model on a curriculum dataset with SFT"
- "Align a model with DPO using RAGAS scores as preference
  signals"
- "Train a model with GRPO (group-relative policy optimization)
  on the Irish curriculum"
- "Train a reward model on the KCG quality assessment labels"
- "Run multi-GPU TRL training on Modal H100"

## Overview

[TRL](https://huggingface.co/docs/trl) is the HuggingFace
library for aligning LLMs with reinforcement learning. The
canonical trainers:

| Trainer | Use case |
|:--|:--|
| `SFTTrainer` | Supervised fine-tuning on a text dataset (the "standard" fine-tune) |
| `DPOTrainer` | Direct Preference Optimization — use pairs of (chosen, rejected) |
| `GRPOTrainer` | Group-Relative Policy Optimization (RLHF without a reward model) |
| `RewardTrainer` | Train a reward model on quality labels |
| `PPOTrainer` | Proximal Policy Optimization (classic RLHF) |

## KCG integration

The KCG curriculum pipeline uses TRL in two places:

1. **SFT** — fine-tune the UCCIX-Llama base model on
   BAML-extracted Irish curriculum (5k-50k examples).
   Unsloth is the wrapper for fast training on M4 Mac.

2. **DPO with RAGAS-as-preference-signal** — for each
   BAML extraction, RAGAS scores the output (faithfulness,
   answer-relevancy, etc.). High-scoring examples become
   "chosen"; low-scoring become "rejected". DPOTrainer
   aligns the model to prefer the high-scoring outputs.

The RAGAS-as-DPO pattern is wired via a Dagster asset:
`sruth/meaisinfhoghlaim/dagster_assets/trl_dpo_training.py`.

## SFTTrainer (supised fine-tuning)

```python
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "ReliableAI/UCCIX-Llama3.1-8B-Instruct",
    load_in_4bit=True,  # bitsandbytes 4-bit quant for QLoRA
)
tokenizer = AutoTokenizer.from_pretrained("ReliableAI/UCCIX-Llama3.1-8B-Instruct")

dataset = load_dataset("oideachais/irish-curriculum-5k", split="train")

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    peft_config=LoraConfig(r=64, lora_alpha=128, lora_dropout=0.05),
    args=SFTConfig(
        output_dir="./kcg-sft",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        bf16=True,
        logging_steps=10,
    ),
)
trainer.train()
```

## DPOTrainer (RAGAS-as-preference-signal pattern)

```python
from trl import DPOTrainer, DPOConfig
from datasets import Dataset

# Build the preference dataset
# "chosen" = high-RAGAS-score, "rejected" = low-RAGAS-score
preference_data = []
for baml_output in baml_outputs:
    ragas_scores = compute_ragas_scores(baml_output)
    if ragas_scores.faithfulness >= 0.8:
        chosen = baml_output.extraction
    else:
        chosen = None
    if ragas_scores.faithfulness < 0.5:
        rejected = baml_output.extraction
    else:
        rejected = None
    if chosen and rejected:
        preference_data.append({
            "prompt": baml_output.prompt,
            "chosen": chosen,
            "rejected": rejected,
        })

dataset = Dataset.from_list(preference_data)

trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,  # the SFT-tuned base for KL divergence
    train_dataset=dataset,
    args=DPOConfig(
        output_dir="./kcg-dpo",
        beta=0.1,  # KL penalty
        num_train_epochs=2,
        per_device_train_batch_size=2,
        learning_rate=5e-5,
    ),
)
trainer.train()
```

## GRPOTrainer (group-relative policy optimization)

GRPOTrainer is the modern RLHF approach (no separate reward
model required). The model itself generates the reward
via a verifier function.

```python
from trl import GRPOTrainer, GRPOConfig


def verifier(samples: list[str], **kwargs) -> list[float]:
    """Score each generated sample via RAGAS."""
    return [compute_ragas_score(s, kwargs["reference"]).faithfulness for s in samples]


trainer = GRPOTrainer(
    model=model,
    reward_funcs=verifier,
    train_dataset=dataset,
    args=GRPOConfig(
        output_dir="./kcg-grpo",
        num_train_epochs=2,
        per_device_train_batch_size=2,
        learning_rate=1e-5,
    ),
)
trainer.train()
```

## RewardTrainer (reward model)

```python
from trl import RewardTrainer, RewardConfig


def to_preference_dataset(quality_labels: list[QualityLabel]) -> Dataset:
    return Dataset.from_list([
        {
            "input": label.text,
            "chosen": label.good_output,
            "rejected": label.bad_output,
        }
        for label in quality_labels
    ])


trainer = RewardTrainer(
    model=AutoModelForSequenceClassification.from_pretrained("ReliableAI/UCCIX-Llama3.1-8B-Instruct", num_labels=1),
    train_dataset=to_preference_dataset(quality_labels),
    args=RewardConfig(output_dir="./kcg-reward", num_train_epochs=2),
)
trainer.train()
```

## KCG production pipeline

The Dagster asset `trl_dpo_training` runs the full pipeline:

1. BAML extraction produces 1000+ examples
2. RAGAS scores each example
3. Preference dataset is built (chosen / rejected pairs)
4. DPOTrainer aligns the model
5. Adapter is saved to MLflow + Langfuse
6. Adapter is served via llama-swap

The asset runs weekly on Modal H100 (see
`.agents/skills/modal/SKILL.md`) for cost efficiency.

## Multi-GPU training

For 13B+ models, use FSDP or DeepSpeed via Accelerate:

```bash
accelerate launch --config_file=fsdp_config.yaml trl_dpo_train.py
```

```yaml
# fsdp_config.yaml
compute_environment: LOCAL_MACHINE
distributed_type: FSDP
fsdp_config:
  fsdp_auto_wrap_policy: TRANSFORMER_BASED_WRAP
  fsdp_transformer_layer_cls_to_wrap: LlamaDecoderLayer
  fsdp_sharding_strategy: FULL_SHARD
mixed_precision: bf16
num_machines: 1
num_processes: 8  # 8× A100/H100
```

## Resources

- TRL docs: <https://huggingface.co/docs/trl>
- DPOTrainer: <https://huggingface.co/docs/trl/dpo_trainer>
- GRPOTrainer: <https://huggingface.co/docs/trl/grpo_trainer>
- RAGAS: <https://docs.ragas.io/>
- Related: `.agents/skills/unsloth/SKILL.md` (Unsloth wrapper),
  `.agents/skills/peft/SKILL.md` (LoRA / QLoRA),
  `.agents/skills/ragas/SKILL.md` (RAGAS scoring),
  `.agents/skills/modal/SKILL.md` (burst GPU training)
