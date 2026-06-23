---
name: peft
description: HuggingFace PEFT — LoRA, QLoRA, IA³, adapter merging, 4-bit quantisation. Use for parameter-efficient fine-tuning on the MacBook M4 48GB unified memory or any KCG fine-tuning workflow.
---

# PEFT — Parameter-Efficient Fine-Tuning

## When to use this skill

Use when you need to:

- "Fine-tune a 7B model on the M4 Mac without OOM"
- "Train a 4-bit quantised base + LoRA adapter (QLoRA)"
- "Merge a LoRA adapter back into the base model for serving"
- "Convert a LoRA adapter to GGUF for llama.cpp / llama-swap"
- "Use IA³ (Infused Adapter by Inhibiting and Amplifying
  Inner Activations) for ultra-low-memory fine-tuning"

## Overview

[PEFT](https://huggingface.co/docs/peft) is the HuggingFace
library for parameter-efficient fine-tuning. The canonical
methods:

| Method | Trainable params | Memory | Quality | Best for |
|:--|--:|:--|:--|:--|
| **LoRA** | 0.1-1% | Low | High | Most use cases |
| **QLoRA** | 0.1-1% | Very low (4-bit base) | High | M4 Mac, 13B+ models |
| **IA³** | 0.01% | Ultra-low | Decent | 70B+ models, edge deployment |
| **Adapter** | 1-5% | Medium | High | Older, less common |
| **Prefix tuning** | 0.1% | Low | Decent | Decoder-only models |

The KCG stack uses **QLoRA** as the canonical fine-tuning
method (works on M4 Mac 48GB for up to 13B models).

## LoRA basics

```python
from peft import LoraConfig, get_peft_model, TaskType
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("ReliableAI/UCCIX-Llama3.1-8B-Instruct")

config = LoraConfig(
    r=64,                # rank of the LoRA matrices
    lora_alpha=128,      # scaling factor (typically 2× r)
    lora_dropout=0.05,   # dropout for regularisation
    bias="none",         # don't train biases
    task_type=TaskType.CAUSAL_LM,
    target_modules=["q_proj", "v_proj"],  # or "all-linear" for full
)

model = get_peft_model(model, config)
model.print_trainable_parameters()
# trainable params: 16,384,000 || all params: 8,191,616,000 || trainable%: 0.2%
```

## QLoRA (4-bit base + LoRA)

The canonical KCG pattern for 7B-13B models on M4 Mac:

```python
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training


# 1. 4-bit quantisation config (bitsandbytes)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",  # NormalFloat4
    bnb_4bit_compute_dtype="bfloat16",
    bnb_4bit_use_double_quant=True,  # nested quantisation
)

# 2. Load the model in 4-bit
model = AutoModelForCausalLM.from_pretrained(
    "ReliableAI/UCCIX-Llama3.1-8B-Instruct",
    quantization_config=bnb_config,
    device_map="auto",  # auto-place layers on MPS / CUDA
)

# 3. Prepare for k-bit training (LoRA on top of 4-bit base)
model = prepare_model_for_kbit_training(
    model,
    use_gradient_checkpointing=True,  # saves more memory
)

# 4. LoRA adapter
lora_config = LoraConfig(
    r=64,
    lora_alpha=128,
    lora_dropout=0.05,
    target_modules="all-linear",  # target all linear layers
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)

# 5. Train (Unsloth wrapper for 2× speedup on M4)
from unsloth import FastLanguageModel
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="ReliableAI/UCCIX-Llama3.1-8B-Instruct",
    max_seq_length=2048,
    load_in_4bit=True,
    ...  # QLoRA config
)
```

## Adapter merging (post-training)

After training, merge the adapter back into the base model
for serving:

```python
from peft import PeftModel

# Load base + adapter
base = AutoModelForCausalLM.from_pretrained("ReliableAI/UCCIX-Llama3.1-8B-Instruct")
model = PeftModel.from_pretrained(base, "outputs/kcg-qlora-v1")

# Merge
merged = model.merge_and_unload()
merged.save_pretrained("outputs/kcg-merged-v1")
tokenizer.save_pretrained("outputs/kcg-merged-v1")
```

## GGUF conversion (for llama-swap / llama.cpp)

The KCG serving layer uses **llama-swap** which reads GGUF
quantised models. Convert the merged model:

```bash
# Convert merged HF model to GGUF
python -m llama_cpp.convert outputs/kcg-merged-v1 \
    --outfile outputs/kcg-merged-v1.gguf \
    --outtype q4_k_m  # 4-bit quant for serving
```

Or with Unsloth:

```python
model.save_pretrained_gguf("outputs/kcg-merged-v1", tokenizer, quantization_method="q4_k_m")
```

## IA³ (ultra-low-memory)

For 70B+ models or edge deployment, use IA³ (Infused Adapter
by Inhibiting and Amplifying Inner Activations):

```python
from peft import IA3Config, get_peft_model

config = IA3Config(
    target_modules=["k_proj", "v_proj", "down_proj"],
    feedforward_modules=["down_proj"],
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, config)
# trainable params: 0.01% (10x fewer than LoRA)
```

## KCG integration

- The `peft_qlora_finetune` Dagster asset uses QLoRA on
  `bunchloch` (M4 Mac, 48GB unified memory) for daily
  fine-tuning of 3B-7B models
- For 13B+ models, the asset dispatches to Modal H100 (see
  `.agents/skills/modal/SKILL.md`)
- The trained adapter is converted to GGUF and served via
  llama-swap at `bunchloch:8080`
- The RAGAS-as-DPO pattern (see `.agents/skills/trl/SKILL.md`)
  builds the preference dataset from BAML extractions
- All trained adapters are logged to MLflow + Langfuse for
  comparison

## Common pitfalls

- **Target modules**: different models have different
  attention module names. Use `target_modules="all-linear"`
  to be safe, or check the model's `modules.json` for the
  exact names
- **4-bit + bf16**: the compute dtype MUST be bfloat16
  (not float16) for numerical stability
- **prepare_model_for_kbit_training**: MUST be called
  before LoRA, otherwise the gradients won't flow
- **Adapter size**: a 64-rank LoRA adapter is ~100 MB; a
  16-rank adapter is ~25 MB. Use 16-rank for faster iteration

## Resources

- PEFT docs: <https://huggingface.co/docs/peft>
- QLoRA paper: <https://arxiv.org/abs/2305.14314>
- bitsandbytes: <https://github.com/TimDettmers/bitsandbytes>
- llama.cpp GGUF conversion: <https://github.com/ggerganov/llama.cpp>
- Unsloth (KCG canonical wrapper): <https://github.com/unslothai/unsloth>
- Related: `.agents/skills/unsloth/SKILL.md`,
  `.agents/skills/trl/SKILL.md`, `.agents/skills/modal/SKILL.md`,
  `.agents/skills/ragas/SKILL.md`
