# Comprehensive LLM Fine-Tuning Reference

**Merged From:**
- `fine-tuning/Fine-tuning LLMs Guide _ Unsloth Documentation.md`
- `fine-tuning/LoRA Hyperparameters Guide _ Unsloth Documentation.md`
- `fine-tuning/Datasets Guide _ Unsloth Documentation.md`
- `fine-tuning/What Model Should I Use for Fine-tuning_ _ Unsloth Documentation.md`
- `fine-tuning/Unsloth Model Catalog _ Unsloth Documentation.md`
- `fine-tuning/Unsloth Models for Celtic Datasets.md`
- `fine-tuning/gpu_experiment_guide.md`
- `fine-tuning/Quantization-Aware Training (QAT) _ Unsloth Documentation.md`
- `fine-tuning/How to Run and Deploy LLMs on your iOS or Android Phone _ Unsloth Documentation.md`
- `fine-tuning/Ministral 3 - How to Run Guide _ Unsloth Documentation.md`
- `fine-tuning/Train a tiny model to generate 3D files (v2) through example diversification.md`
- `fine-tuning/We Got Claude to Fine-Tune an Open Source LLM.md`

---

## Table of Contents

1. [Introduction: Why Fine-Tune?](#introduction)
2. [Choosing a Base Model](#choosing-a-base-model)
3. [Dataset Preparation](#dataset-preparation)
4. [LoRA & QLoRA Hyperparameters](#lora--qlora-hyperparameters)
5. [Training Configuration & Execution](#training-configuration)
6. [Quantization-Aware Training (QAT)](#quantization-aware-training-qat)
7. [Reinforcement Learning: GRPO, DPO, KTO](#reinforcement-learning)
8. [Phone & Edge Deployment](#phone--edge-deployment)
9. [Model Catalog](#model-catalog)
10. [Celtic Languages: Strategy & GPU Guide](#celtic-languages-strategy)
11. [Case Studies](#case-studies)
12. [Hugging Face Skills: Agent-Driven Fine-Tuning](#hugging-face-skills)

---

## Introduction

Fine-tuning an LLM customizes its behavior, injects knowledge, and optimizes performance for specific domains/tasks. Examples:

- **GPT-4** was fine-tuned from a base model to create ChatGPT-4.
- **DeepSeek-R1-Distill-Llama-8B** is a fine-tuned Llama-3.1-8B using DeepSeek-R1 data (distillation).

With Unsloth, you can fine-tune for free on Colab, Kaggle, or locally with just 3GB VRAM.

### Fine-Tuning Misconceptions

Fine-tuning **can replicate all of RAG's capabilities**, but not vice versa. Claims that fine-tuning doesn't teach new knowledge or that RAG always outperforms fine-tuning are false.

### LoRA vs QLoRA vs Full Fine-Tuning

| Method | Precision | VRAM | Accuracy | Speed |
|--------|-----------|------|----------|-------|
| **QLoRA** | 4-bit | Lowest | Near LoRA w/ dynamic 4-bit | Slower |
| **LoRA** | 16-bit | Moderate | Best | Faster |
| **Full FT** | 16-bit | Highest | Reference | Varies |

**Recommendation:** Start with QLoRA using Unsloth dynamic 4-bit quants.

---

## Choosing a Base Model

### Instruct vs Base Models

**Instruct models** are pre-trained with built-in instructions, optimized for direct use with conversational chat templates (ChatML, ShareGPT). Best when you have:
- Less than 300 rows of data
- Need to preserve general instruction-following

**Base models** are original pre-trained versions without instruction tuning, compatible with Alpaca/Vicuna templates. Best when you have:
- 1,000+ rows of high-quality data
- Need maximum customization

### By Dataset Size

| Dataset Size | Recommended Approach |
|-------------|---------------------|
| <300 rows | Start with Instruct model |
| 300-1,000 rows | Either Instruct or Base |
| 1,000+ rows | Base model for maximum customization |

### Model Naming Convention

- `unsloth-bnb-4bit` — Unsloth dynamic 4-bit quants (more VRAM, higher accuracy)
- `bnb-4bit` — Standard BitsAndBytes 4-bit
- No suffix — Original 16-bit or 8-bit (may include chat template/tokenizer fixes)

### Model Selection by Domain

| Domain | Recommended Architecture | Key Models |
|--------|------------------------|------------|
| Code | Qwen Coder 2.5, Llama 3.1 | Qwen3-Coder-30B-A3B, Llama 3.1 8B |
| Multilingual (140+ langs) | Gemma 3 | Gemma 3 27B, 12B |
| Math & Reasoning | Qwen 2.5 Math, DeepSeek-R1 | Qwen2.5-Math-72B, QwQ-32B |
| Vision/Multimodal | Llama 3.2 Vision, Qwen2.5-VL | Qwen3-VL series, Pixtral |
| General Instruction | Llama 3.3, Ministral 3 | Llama 3.3 70B, Ministral 3 14B |
| Edge/Mobile | Phi-4, Qwen3 | Phi-4-14B, Qwen3-0.6B |

---

## Dataset Preparation

### Data Formats

| Format | Use Case | Structure |
|--------|----------|-----------|
| **Raw Corpus** | Continued pretraining | Plain text, no structure |
| **Alpaca** | Single-turn instruction tuning | `instruction`, `input`, `output` |
| **ShareGPT** | Multi-turn conversations | `conversations` with `from`/`value` |
| **ChatML** | Modern chat models | `messages` with `role`/`content` |
| **RLHF** | Preference training | Chosen/rejected pairs |

### Minimum Dataset Size

- **Absolute minimum:** 100 rows
- **Good results:** 1,000+ rows
- **Better results with more data**
- Quality > quantity — well-curated small datasets outperform noisy large ones

### Chat Templates in Unsloth

```python
from unsloth.chat_templates import get_chat_template, CHAT_TEMPLATES

# See all supported templates
print(list(CHAT_TEMPLATES.keys()))
# ['unsloth', 'zephyr', 'chatml', 'mistral', 'llama', 'gemma', 'gemma-3',
#  'llama-3', 'llama-3.1', 'llama-3.2', 'qwen-2.5', 'phi-4', ...]

# Apply template
tokenizer = get_chat_template(tokenizer, chat_template="gemma-3")

# Apply to dataset
def formatting_prompts_func(examples):
    convos = examples["conversations"]
    texts = [tokenizer.apply_chat_template(convo, tokenize=False, add_generation_prompt=False) for convo in convos]
    return {"text": texts}

dataset = dataset.map(formatting_prompts_func, batched=True)
```

### Vision Dataset Format

```python
conversation = [
    {"role": "user", "content": [
        {"type": "text", "text": instruction},
        {"type": "image", "image": image}
    ]},
    {"role": "assistant", "content": [
        {"type": "text", "text": answer}
    ]}
]
```

### Synthetic Data Generation

Use a larger model (Llama 3.3 70B, GPT-4o) to generate training data:

1. **Produce entirely new data** from scratch or existing datasets
2. **Diversify** your dataset to prevent overfitting
3. **Augment** existing data into correct format

Unsloth + Meta's free notebook auto-parses PDFs, websites, YouTube videos, generates QA pairs, cleans data, and fine-tunes with Llama 3.2.

### Alpaca Dataset Merging

`to_sharegpt` function merges CSV/Excel columns into single prompts:

```python
# Columns enclosed in {curly braces}
# Optional text in [[brackets]] for missing values
# Set conversation_extension for multi-turn from single-turn
```

### Training on Completions Only

The QLoRA paper shows training only on assistant outputs (masking user inputs) increases accuracy by ~1% for multi-turn conversational fine-tunes.

---

## LoRA & QLoRA Hyperparameters

### Learning Rate

- **Standard LoRA/QLoRA:** Start at `2e-4`
- **Reinforcement Learning (GRPO/DPO):** Start at `5e-6`
- **Full Fine-Tuning:** Lower values generally more appropriate

### Rank (r)

```python
r = 16  # Suggested: 8, 16, 32, 64, 128
```

- Higher rank = more memory, slower training, potentially higher accuracy on complex tasks
- Too high can cause overfitting
- For Celtic languages (complex morphology): r=64 or r=128
- Celtic recommendation: r=128 with lora_alpha=256

### Target Modules

```python
target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                  "gate_proj", "up_proj", "down_proj"]
```

**Always target ALL major linear layers** — both MLP and attention. Research shows this is crucial for matching full fine-tuning performance. Removing modules for memory savings is strongly discouraged.

**Performance ranking:**
1. QLoRA-All (best) — FFN/MLP + Attention
2. QLoRA-FFN only — `gate_proj`, `up_proj`, `down_proj`
3. QLoRA-Attention only — `q_proj`, `k_proj`, `v_proj`, `o_proj`

### LoRA Alpha

```python
lora_alpha = 16  # Recommendation: r or 2*r
```

- Controls the strength of fine-tuned adjustments
- Formula: `W_hat = W + (alpha/rank) * AB`
- Set `lora_alpha = 2 * lora_rank` or `lora_alpha = lora_rank`
- rsLoRA option: scales by `sqrt(rank)` — enable with `use_rslora = True`

### Batch Size & Gradient Accumulation

```python
per_device_train_batch_size = 2
gradient_accumulation_steps = 8
# Effective Batch Size = 2 * 8 = 16
```

Target Effective Batch Size of 16. If VRAM is tight, reduce batch_size and increase gradient_accumulation_steps.

Unsloth has specific bug fixes ensuring `batch_size=1/grad_acc=16` produces identical results to `batch_size=16/grad_acc=1`.

### Other Key Hyperparameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `lora_dropout` | 0 | Regularization; use 0.1 if overfitting |
| `bias` | "none" | Keep at "none" for speed |
| `use_gradient_checkpointing` | "unsloth" | 30% memory reduction for long context |
| `random_state` | 3407 | Seed for reproducibility |
| `use_rslora` | False | Rank-stabilized LoRA scaling |
| `loftq_config` | None | Advanced quantization init |
| `weight_decay` | 0.01 | Regularization; 0.01 or 0.1 for overfitting |

### Overfitting Solutions

Signs: training loss drops below 0.2

- Reduce learning rate or epochs
- Increase `weight_decay` (0.01-0.1)
- Increase `lora_dropout` (0.1)
- Increase batch size / gradient accumulation steps
- Expand dataset with quality data
- Enable evaluation early stopping
- LoRA alpha scaling (multiply alpha by 0.5)
- Weight averaging: `(base_model + fine-tuned) / 2`

### Underfitting Solutions

- Adjust learning rate (increase for short runs)
- Increase training epochs (monitor validation loss)
- Increase LoRA rank and alpha
- Use more domain-relevant dataset
- Decrease batch size to 1

---

## Training Configuration & Execution

### Basic Unsloth Setup

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.1-8B-Instruct-bnb-4bit",
    max_seq_length=2048,  # 2048 for testing, increase for production
    dtype=None,           # Auto-detect
    load_in_4bit=True,    # QLoRA
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=32,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)
```

### Training Arguments

```python
from transformers import TrainingArguments

training_args = TrainingArguments(
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    warmup_ratio=0.03,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    optim="adamw_8bit",
    weight_decay=0.01,
    lr_scheduler_type="cosine",
    seed=42,
)
```

### Saving Models

```python
# Save LoRA adapter (~100MB)
model.save_pretrained("models/my-lora")

# Push to Hugging Face
model.push_to_hub("username/my-model", token="hf_...")

# Export to GGUF
model.save_pretrained_gguf("my-model", tokenizer, quantization_method="q4_k_m")
```

### Evaluation

- **Manual:** Chat with the model to assess quality
- **Internal eval:** Enable evaluation in training args; set `evaluation_steps=100`
- **External:** Use EleutherAI lm-evaluation-harness
- **Split testing:** Reserve 20% of training data for evaluation
- Good training loss: 0.5 to 1.0 (varies by task)

---

## Quantization-Aware Training (QAT)

QAT simulates quantization during training to recover accuracy lost during post-training quantization.

### Recovery Rates

- **Recovers up to 70%** of lost accuracy
- **1-3% model performance improvement** on GPQA, MMLU Pro
- Gemma3-4B: +1.0% GPQA with 66.9% recovery
- Gemma3-12B: +2.1% BBH with 45.5% recovery

### How QAT Works

Instead of naive post-training quantization (PTQ), QAT simulates quantization by "fake quantizing" weights during training — rounding to quantized values while staying in high-precision dtype, then dequantizing.

### Usage

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen3-4B-Instruct-2507",
    load_in_16bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", ...],
    lora_alpha=32,
    qat_scheme="int4",  # Options: fp8-int4, fp8-fp8, int8-int4, int4
)

# After training, convert and save
from torchao.quantization import quantize_, QATConfig
quantize_(model, QATConfig(step="convert"))

model.save_pretrained_torchao(torchao_config=Int4WeightOnlyConfig())
```

### Export Options

- `Int4WeightOnlyConfig()` — 4-bit weights
- `Int8DynamicActivationInt8WeightConfig()` — 8-bit dynamic
- `Float8DynamicActivationFloat8WeightConfig(granularity=PerRow())` — Float8
- Direct ExecuTorch export for mobile deployment

---

## Reinforcement Learning

### GRPO (Group Relative Policy Optimization)

Used for creating reasoning models (like DeepSeek-R1).

**Workflow:**
1. Feed model a question
2. Model generates a group of outputs (4-8 different reasoning paths)
3. Reward function evaluates outputs (exact match, LLM-as-judge)
4. Model updates to favor paths leading to correct answers

**Hardware:** Unsloth enables GRPO on single 16GB-24GB GPU for Llama 3.2 3B or Qwen 2.5 7B.

### DPO (Direct Preference Optimization)

Trains on preference pairs (chosen vs rejected responses). Dataset requires exactly `chosen` and `rejected` columns, or a `prompt` column with the input.

### Training Methods

Hugging Face Skills supports all three: SFT, DPO, and GRPO.

---

## Phone & Edge Deployment

### Unsloth + PyTorch ExecuTorch + TorchAO

Deploy Qwen3-0.6B to iPhone 15 Pro and Pixel 8 at ~40 tokens/s.

### Step-by-Step

1. **Fine-tune with phone deployment flag:**

```python
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen3-0.6B",
    full_finetuning=True,
    qat_scheme="phone-deployment",  # Uses int8-int4 under the hood
)
```

2. **Convert to ExecuTorch `.pte` file** (~472MB for 0.6B)
3. **Deploy to iOS** via Xcode + etLLM app
4. **Deploy to Android** via ADB + executorchllamademo app

### iOS Requirements

- macOS with Xcode 15+
- Apple Developer Program (for Increased Memory Limit capability)
- Physical device: iPhone 15 Pro or later

### Android Requirements

- Java 17
- Android Command Line Tools (API 34, NDK 25)
- ADB for file transfer

### Supported Models for Phone

All Qwen 3 dense (0.6B-32B), Gemma 3 (270M-27B), Llama 3 (all), Qwen 2.5, Phi 4 Mini.

---

## Model Catalog

### Unsloth Dynamic GGUF & 4-bit Models

Available on Hugging Face under `unsloth/` namespace.

### DeepSeek Models
- DeepSeek-V3, DeepSeek-R1 (distills: 1.5B, 7B, 8B, 14B, 32B, 70B)

### Llama Models
- Llama 3.1 (8B, 70B), Llama 3.2 (1B, 3B, 11B Vision, 90B Vision), Llama 3.3 (70B), Llama 4

### Gemma Models
- Gemma 2 (2B, 9B, 27B), Gemma 3 (1B, 4B, 12B, 27B, 270M)

### Qwen Models
| Series | Sizes | Notes |
|--------|-------|-------|
| **Qwen3-VL** | 2B, 4B, 8B | Vision-Language, Instruct/Thinking |
| **Qwen3-Coder** | 30B-A3B, 480B-A35B | Code-specific MoE |
| **Qwen3-2507** | 30B-A3B, 235B-A22B | Next-gen, Instruct/Thinking |
| **Qwen 3** | 0.6B-235B-A22B | Dense + MoE |
| **Qwen 2.5** | 0.5B-72B | Instruct, Coder, VL variants |
| **QwQ** | 32B | Reasoning |
| **QVQ** | 72B | Vision-Reasoning |

### Mistral Models
- Ministral 3 (3B, 8B, 14B) — multimodal, 256K context, Instruct/Reasoning
- Mistral Large 3 (675B)

### Phi Models
- Phi-4 (14B), Phi-4 Mini

### Ministral 3 Specifics

**Instruct** variant: `temperature=0.15`, output length 16,384 tokens
**Reasoning** variant: `temperature=0.7, top_p=0.95`, output length 32,768 tokens
Max context: 262,144 tokens

---

## Celtic Languages Strategy

### Recommended Base Models for Celtic Fine-Tuning

| Model | Parameter Size | Celtic Viability | Primary Strength |
|-------|---------------|------------------|------------------|
| **Gemma 3** | 27B / 12B | Very High (140+ langs) | Native multilingual support |
| **Qwen 2.5** | 72B / 32B | High (broad language base) | Multilingual + Math |
| **Llama 3.3** | 70B | Medium (English-centric) | Instruction following |
| **Phi-4** | 14B | Low (English-centric) | Edge deployment |

### Goidelic Cluster (Irish, Scottish Gaelic, Manx)

**Primary Base:** Unsloth/Qwen2.5-14B-Instruct
**Alternative:** Llama-3.1-8B-Instruct

**Key Datasets:**
- **Irish:** CulturaX-ga, Qomhrá 30K (30,000 instruction pairs), Irish-BLiMP (1,020 minimal pairs), LC2024 (55 math reasoning)
- **Scottish Gaelic:** ARCOSG (POS-tagged), Corpas na Gàidhlig (70M+ words), Tobar an Dualchais (folklore audio)

**Training Config (Celtic-optimized):**
```python
r = 128, lora_alpha = 256, lora_dropout = 0.05
training_args: batch_size=4, gradient_accumulation=8, learning_rate=2e-5
epochs=3, weight_decay=0.01, warmup_ratio=0.03
```

**English-Pivoted Chain-of-Thought:**
Training LLMs to reason in English while responding in Irish achieves **28.33% improvement** in mathematical reasoning (Tran et al., UCC 2024). Model outputs English reasoning chains but produces Irish final answers.

### Brythonic Cluster (Welsh, Breton, Cornish)

**Base:** Unsloth/Llama-3.1-8B-Nemotron

**Key Datasets:**
- **Welsh:** CorCenCC (13.5M tokens), FreeTxt
- **Breton/Cornish:** Wikipedia dumps, An Drouizig resources, Korpus Kernewek

**Strategy:** Joint "Brythonic" training with Welsh as anchor (weight 0.6) + Breton (0.25) + Cornish (0.15) with interleaved batching.

### Synthetic Data for Low-Resource Languages

**Cold Start Pipeline:**
1. Generate CoT reasoning traces in English using DeepSeek-R1 or GPT-4o
2. Translate traces into target Celtic language (NLLB or fine-tuned Qwen)
3. Verify translations with Teacher-Student loop or human-in-the-loop

### GPU Cost Estimates

| Phase | Description | GPU | Hours | Cost |
|-------|-------------|-----|-------|------|
| Phase 1 | Goidelic (Irish + Gaelic CPT) | H100 | 35 | ~$138 |
| Phase 2 | Brythonic (Welsh + Breton/Cornish) | A100 | 40 | ~$100 |
| Phase 3 | Evaluation | L4 | 20 | ~$16 |
| **Total** | | | | **~$275** |

**Budget options:** A100 40GB only ($175), A10 longer training ($100)

### Unsloth Advantages for Celtic

1. **VRAM Efficiency:** 14B models on single A100 40GB (normally needs 80GB)
2. **Speed:** 2-3x faster via kernel optimizations
3. **Packing:** Removes padding tokens — 2-5x effective speedup for sparse Celtic datasets
4. **QLoRA:** 4-bit quantization with minimal quality loss

---

## Case Studies

### Case Study 1: CADMonkey — 3D File Generation

**Goal:** Fine-tune a tiny model (Gemma3-1B) to generate OpenSCAD code for 3D models.

**Key Lessons:**
- Scaling dataset **vertically** (more examples per object) outperformed horizontal scaling (more object types)
- Synthetic data with VLMs for verification (Qwen2.5-VL judges rendered outputs)
- Diversity of teacher models improved results
- 3 weekends, $500 in credits — replacing what would have cost 5 figures and 20 scientists 5 years ago

**Outcome:** 80% of generated code is syntactically correct; deployed on Modal (T4 GPU, ~2 cents/prompt), runs on Raspberry Pi.

### Case Study 2: Hugging Face Skills — Agent-Driven Fine-Tuning

Hugging Face Skills (`hf-llm-trainer`) enables Claude Code to autonomously:
1. Validate dataset format
2. Select appropriate hardware (t4-small for 0.6B)
3. Generate and submit training scripts
4. Monitor progress with Trackio
5. Push finished models to Hugging Face Hub

**Cost:** ~$0.30 for a Qwen3-0.6B fine-tune
**Hardware mapping:** t4-small (<1B), t4-medium/a10g-small (1-3B), a10g-large/a100-large (3-7B with LoRA)

**Installation for Claude Code:**
```bash
/plugin marketplace add huggingface/skills
/plugin install hf-llm-trainer@huggingface-skills
```

---

## Irish-BLiMP Benchmarks

| Model | Accuracy |
|-------|----------|
| Human Baseline | 90.1% |
| GPT-5 | 73.5% |
| Llama 3 70B | 67.8% |
| Random | 50.0% |

Even state-of-the-art LLMs rely on pattern recognition rather than true grammatical understanding for Irish — demonstrating the need for specialized fine-tuning.

---

## Cloud GPU Providers

- **RunPod** — H100, A100, A10, L4; good availability
- **Lambda Labs** — H100, A100; research-focused
- **Vast.ai** — marketplace model, variable pricing
- **Google Colab Pro+** — $50/month, A100, good for prototyping

---

## References

- Unsloth: https://github.com/unslothai/unsloth
- Unsloth Docs: https://docs.unsloth.ai
- Hugging Face Skills: https://github.com/huggingface/skills
- ExecuTorch: https://github.com/pytorch/executorch
- Qomhrá: https://huggingface.co/datasets/Qomhraiche/Qomhra-30K
- Irish-BLiMP: Irish linguistic minimal pairs benchmark
- LC2024: Leaving Certificate mathematical reasoning dataset
