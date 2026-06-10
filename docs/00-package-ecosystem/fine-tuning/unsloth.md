# Unsloth — Efficient LLM Fine-Tuning

## Overview

Unsloth is an open-source library for efficient LLM fine-tuning that achieves 70% VRAM reduction and 2x training speed compared to standard implementations. It supports LoRA, QLoRA, and full fine-tuning across Llama, Mistral, Gemma, Qwen, and other model families. Designed for consumer hardware — fine-tune 7B models on a single GPU.

## Why This Matters for Kings' College Galway

The project trains domain-specific models for Celtic language processing and educational content generation. Unsloth makes this feasible on the MacBook M4's 48 GB unified memory: fine-tuning a 7B Irish-language model with LoRA on curriculum-aligned text requires under 20 GB VRAM with Unsloth's optimisations, vs 40+ GB with standard libraries. The Dagster `model_conversion` job uses Unsloth for fine-tuning runs, and the fine-tuned GGUFs are served through llama-swap on the same hardware.

## Key Features

- **70% VRAM reduction** — Fine-tune 7B models on consumer GPUs
- **2x speedup** — Flash Attention and kernel optimisations
- **LoRA/QLoRA** — Parameter-efficient fine-tuning with 4-bit quantization
- **Multi-model** — Llama, Mistral, Gemma, Qwen, Phi, and more
- **GGUF export** — Export fine-tuned models directly to GGUF format

## Installation

```bash
uv add unsloth
```

## Integration with Our Stack

Unsloth fine-tuning runs as Dagster assets in the `meaisínfhoghlaim/` stream. Fine-tuned models are exported to GGUF and served via llama-swap on the MacBook M4. The `model_conversion` Dagster job orchestrates the full HF → fine-tune → GGUF pipeline.

## Upstream

- **Repository**: <https://github.com/unslothai/unsloth>
- **Documentation**: <https://docs.unsloth.ai>
- **Latest**: v2024.12+ — multilingual support, flash attention v3, 4-bit optimisations

## Screenshot

Unsloth is a programmatic library. Training progress appears in terminal output with loss curves, token throughput, and VRAM usage. The `.agents/skills/unsloth/` directory documents fine-tuning workflows. Fine-tuned model quality is tracked in MLflow experiments with RAGAS evaluation scores.
