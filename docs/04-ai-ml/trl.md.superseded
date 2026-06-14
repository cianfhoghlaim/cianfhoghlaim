---
title: 'TRL — Transformer Reinforcement Learning (HuggingFace)'
domain: 'ai_ml'
status: 'stable'
description: 'TRL (Transformer Reinforcement Learning) is a HuggingFace library for fine-tuning language models with reinforcement learning. It supports SFT (Supervised Fine-Tuning), DPO (Direct Preference Optimization), GRPO (Group Relative Policy Optimization), and reward modeling — enabling'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/trl.md
ccc_query_hints:
  - trl — transformer reinforcement learning
---

# TRL — Transformer Reinforcement Learning (HuggingFace)

## Overview

TRL (Transformer Reinforcement Learning) is a HuggingFace library for fine-tuning language models with reinforcement learning. It supports SFT (Supervised Fine-Tuning), DPO (Direct Preference Optimization), GRPO (Group Relative Policy Optimization), and reward modeling — enabling alignment training on top of base models.

## Why This Matters for Kings' College Galway

Curriculum-aligned content requires models that not only generate factually correct text but also follow pedagogical best practices — appropriate difficulty level, encouraging tone, correct use of Irish/English bilingual transitions, and academic-rigour-appropriate hedging. TRL's DPO training uses RAGAS evaluation scores as preference signals: when the BAML extraction produces a high-faithfulness output, it serves as a "chosen" example; when it produces a hallucinated prerequisite, it serves as a "rejected" example. This preference optimisation directly improves extraction quality over successive fine-tuning runs.

## Key Features

- **SFT** — Supervised fine-tuning on curriculum-aligned datasets
- **DPO** — Direct preference optimisation using RAGAS scores as signals
- **GRPO** — Group relative policy optimisation for batch preference learning
- **Reward modeling** — Train reward models from human preference data
- **HuggingFace integration** — Seamless with `transformers`, `peft`, `datasets`

## Installation

```bash
uv add trl
```

## Integration with Our Stack

TRL training scripts live in `meaisínfhoghlaim/scripts/`. Training data comes from dlt-curated curriculum datasets. Fine-tuned models are exported to GGUF via Unsloth and served through llama-swap. MLflow tracks training metrics and model versions.

## Upstream

- **Repository**: <https://github.com/huggingface/trl>
- **Documentation**: <https://huggingface.co/docs/trl>
- **Latest**: v0.15.x (2025) — GRPO support, DPO improvements, HuggingFace Jobs integration

## Screenshot

TRL is a programmatic library. Training runs are logged to MLflow showing loss curves, reward scores, and preference accuracy. The HuggingFace model hub provides dataset and model versioning. Training scripts are version-controlled in the Forgejo repository.
