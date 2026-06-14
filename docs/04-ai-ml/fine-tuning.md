---
title: 'LLM Fine-Tuning — Unsloth, TRL, and LoRA/QLoRA: Reference & Skill Card'
domain: 'ai_ml'
status: 'stable'
description: 'Complete LLM fine-tuning reference — Unsloth (efficient fine-tuning with 70% VRAM reduction, 2x speedup), TRL (Supervised Fine-Tuning, DPO, GRPO for preference optimization), and LoRA/QLoRA (parameter-efficient fine-tuning with 99% parameter reduction, 4-bit quantization). Plus skill card for each with KCG context, integration with our stack (Dagster meaisínfhoghlaim assets, GGUF export, llama-swap serving, MacBook M4 48GB training).'
read_when:
  - fine-tuning a model
  - looking for documentation on this topic
  - choosing between SFT/DPO/GRPO
  - choosing between Unsloth/TRL/PEFT
updated: 2026-06-13
supersedes:
  - docs/ai-ml/unsloth.md
  - docs/ai-ml/trl.md
  - docs/ai-ml/lora-qlora.md
truth: sole
ccc_query_hints:
  - unsloth efficient llm fine-tuning
  - trl transformer reinforcement learning
  - trl dpo grpo preference optimization
  - lora qlora parameter efficient fine-tuning
  - peft huggingface adapter
---

# LLM Fine-Tuning — Unsloth, TRL, and LoRA/QLoRA: Reference & Skill Card

> **Merged from 3 canonical sources**:
> - `unsloth.md` (53 lines) — efficient fine-tuning library
> - `trl.md` (53 lines) — reinforcement learning fine-tuning
> - `lora-qlora.md` (53 lines) — parameter-efficient fine-tuning techniques
>
> All three cover complementary aspects of the same workflow: Unsloth provides the runtime, TRL provides the training algorithms (SFT, DPO, GRPO), and LoRA/QLoRA is the parameter-efficient technique that makes it all feasible on consumer hardware.

---

## Unsloth — Efficient LLM Fine-Tuning

### Overview

Unsloth is an open-source library for efficient LLM fine-tuning that achieves 70% VRAM reduction and 2x training speed compared to standard implementations. It supports LoRA, QLoRA, and full fine-tuning across Llama, Mistral, Gemma, Qwen, and other model families. Designed for consumer hardware — fine-tune 7B models on a single GPU.

### Why This Matters for Kings' College Galway

The project trains domain-specific models for Celtic language processing and educational content generation. Unsloth makes this feasible on the MacBook M4's 48 GB unified memory: fine-tuning a 7B Irish-language model with LoRA on curriculum-aligned text requires under 20 GB VRAM with Unsloth's optimisations, vs 40+ GB with standard libraries. The Dagster `model_conversion` job uses Unsloth for fine-tuning runs, and the fine-tuned GGUFs are served through llama-swap on the same hardware.

### Key Features

- **70% VRAM reduction** — Fine-tune 7B models on consumer GPUs
- **2x speedup** — Flash Attention and kernel optimisations
- **LoRA/QLoRA** — Parameter-efficient fine-tuning with 4-bit quantization
- **Multi-model** — Llama, Mistral, Gemma, Qwen, Phi, and more
- **GGUF export** — Export fine tuned models directly to GGUF format

### Installation

```bash
uv add unsloth
```

### Integration with Our Stack

Unsloth fine-tuning runs as Dagster assets in the `meaisínfhoghlaim/` stream. Fine-tuned models are exported to GGUF and served via llama-swap on the MacBook M4. The `model_conversion` Dagster job orchestrates the full HF → fine-tune → GGUF pipeline.

### Upstream

- **Repository**: <https://github.com/unslothai/unsloth>
- **Documentation**: <https://docs.unsloth.ai>
- **Latest**: v2024.12+ — multilingual support, flash attention v3, 4-bit optimisations

### Screenshot

Unsloth is a programmatic library. Training progress appears in terminal output with loss curves, token throughput, and VRAM usage. The `.agents/skills/unsloth/` directory documents fine-tuning workflows. Fine-tuned model quality is tracked in MLflow experiments with RAGAS evaluation scores.

---

## TRL — Transformer Reinforcement Learning (HuggingFace)

### Overview

TRL (Transformer Reinforcement Learning) is a HuggingFace library for fine-tuning language models with reinforcement learning. It supports SFT (Supervised Fine-Tuning), DPO (Direct Preference Optimization), GRPO (Group Relative Policy Optimization), and reward modeling — enabling alignment training on top of base models.

### Why This Matters for Kings' College Galway

Curriculum-aligned content requires models that not only generate factually correct text but also follow pedagogical best practices — appropriate difficulty level, encouraging tone, correct use of Irish/English bilingual transitions, and academic-rigour-appropriate hedging. TRL's DPO training uses RAGAS evaluation scores as preference signals: when the BAML extraction produces a high-faithfulness output, it serves as a "chosen" example; when it produces a hallucinated prerequisite, it serves as a "rejected" example. This preference optimisation directly improves extraction quality over successive fine-tuning runs.

### Key Features

- **SFT** — Supervised fine-tuning on curriculum-aligned datasets
- **DPO** — Direct preference optimisation using RAGAS scores as signals
- **GRPO** — Group relative policy optimisation for batch preference learning
- **Reward modeling** — Train reward models from human preference data
- **HuggingFace integration** — Seamless with `transformers`, `peft`, `datasets`

### Installation

```bash
uv add trl
```

### Integration with Our Stack

TRL training scripts live in `meaisínfhoghlaim/scripts/`. Training data comes from dlt-curated curriculum datasets. Fine-tuned models are exported to GGUF via Unsloth and served through llama-swap. MLflow tracks training metrics and model versions.

### Upstream

- **Repository**: <https://github.com/huggingface/trl>
- **Documentation**: <https://huggingface.co/docs/trl>
- **Latest**: v0.15.x (2025) — GRPO support, DPO improvements, HuggingFace Jobs integration

### Screenshot

TRL is a programmatic library. Training runs are logged to MLflow showing loss curves, reward scores, and preference accuracy. The HuggingFace model hub provides dataset and model versioning. Training scripts are version-controlled in the Forgejo repository.

---

## LoRA / QLoRA — Parameter-Efficient Fine-Tuning

### Overview

LoRA (Low-Rank Adaptation) and QLoRA (Quantized LoRA) are parameter-efficient fine-tuning techniques that reduce the number of trainable parameters by 99%+ while maintaining model quality. LoRA adds small trainable rank-decomposition matrices to attention layers; QLoRA adds 4-bit quantization on top. Both are implemented via HuggingFace's PEFT library.

### Why This Matters for Kings' College Galway

The MacBook M4's 48 GB unified memory is the primary training hardware. Full fine-tuning of a 7B model requires ~55 GB — impossible on 48 GB. LoRA fine-tuning requires ~16 GB — comfortable. QLoRA reduces this to ~8 GB — room to spare for batch processing. This hardware constraint directly determines the training strategy: all fine-tuned models in the project use LoRA/QLoRA adapters merged into the base model weights, producing GGUFs that are computationally identical to full fine-tunes but trainable on consumer hardware.

### Key Features

- **99% parameter reduction** — Train <1% of model parameters
- **QLoRA 4-bit** — 4-bit NormalFloat quantization for further memory reduction
- **Adapter merging** — Merge LoRA weights into base model for inference
- **PEFT integration** — HuggingFace's standard API via `peft` library
- **Multi-model support** — Llama, Qwen, Gemma, Mistral, and more

### Installation

```bash
uv add peft bitsandbytes
```

### Integration with Our Stack

LoRA/QLoRA is the default fine-tuning method in Unsloth and TRL training scripts. Adapters are trained on the MacBook M4 and merged into GGUF models for llama-swap serving. The `meaisínfhoghlaim/scripts/convert_hf_to_gguf.sh` script handles adapter merging during model conversion.

### Upstream

- **LoRA paper**: <https://arxiv.org/abs/2106.09685>
- **QLoRA paper**: <https://arxiv.org/abs/2305.14314>
- **PEFT library**: <https://github.com/huggingface/peft>

### Screenshot

LoRA/QLoRA are techniques, not standalone tools. Training metrics appear in Unsloth/TRL output showing adapter size (typically 10-50 MB for a 7B model), training loss, and VRAM usage. The `peft` library provides adapter loading/saving APIs. Merged models are functionally identical to full fine-tunes at inference time.
