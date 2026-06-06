# Meaisínfhoghlaim (Machine Learning) - AI Agent Instructions

## Overview

Meaisínfhoghlaim (Irish: "machine learning") contains ML sources, trained models, and training notebooks for Celtic language education AI.

## Directory Structure

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `models/` | Trained and fine-tuned models | GGUF, LoRA adapters, checkpoints |
| `notebooks/` | Training and evaluation notebooks | Marimo, Jupyter |
| `stack.md` | ML technology stack documentation | Reference |

## Model Categories

### Language Models

| Model | Purpose | Size | Status |
|-------|---------|------|--------|
| UCCIX-Llama2-13B | Irish text generation | 13B | Reference |
| Llama-3.2-3B-Irish | Mobile Irish LLM | 3B | Training |
| Qwen2.5-Math-7B | Bilingual math reasoning | 7B | Reference |

### Embedding Models

| Model | Purpose | Dimensions |
|-------|---------|------------|
| GaBERT | Irish text embeddings | 768 |
| BGE-M3 | Multilingual embeddings | 1024 |
| ColPali | Visual document embeddings | 128 per patch |

### Speech Models

| Model | Purpose | Status |
|-------|---------|--------|
| Whisper-Irish | Irish ASR | Fine-tuning |
| MMS-1B | Multilingual TTS | Reference |
| wav2vec2-xlsr-irish | Irish speech recognition | Available |

### Vision-Language Models

| Model | Purpose | Status |
|-------|---------|--------|
| Qwen2-VL-7B | Document OCR | Fine-tuning |
| olmOCR-2-7B | Manuscript transcription | Reference |
| Granite-Docling | Table extraction | Reference |

## Critical Constraints

### Fine-Tuning Requirements

**MANDATORY:** Follow these constraints from `.claude/CONSTRAINTS.md`:

```python
# CORRECT: Unsloth with proper batch size
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.2-3B-Instruct-bnb-4bit",
    max_seq_length=8192,
    load_in_4bit=True,
)

# Apply LoRA with Irish-optimized settings
model = FastLanguageModel.get_peft_model(
    model,
    r=64,  # Higher rank for language adaptation
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=128,
)

# WRONG: Full fine-tuning without LoRA
# model.train()  # 10x more VRAM, slower
```

### Irish Language Data

- Irish is <0.1% of web content
- 20% model performance gap vs English
- Use specialized datasets: CC-100 Irish, Common Voice, UCCIX corpus

### Dataset Format

```json
{
  "conversations": [
    {
      "role": "user",
      "content": "Leaving Certificate Higher Level:\nDifferentiate f(x) = (3x^2+2)/(x-1). (25 marks)"
    },
    {
      "role": "assistant",
      "content": "<think>Apply quotient rule...</think>\n\n**Step 1: Apply Quotient Rule** (5 marks)\n$$f'(x) = ...$$"
    }
  ]
}
```

**Dataset Mix:** 60-70% LC problems + 20-30% general math + 10% Irish language

## Training Workflow

### 1. Data Preparation

```python
# notebooks/prepare_data.py
import datasets

# Load and filter Irish content
dataset = datasets.load_dataset("ReliableAI/Irish-English-Parallel-Collection")

# Format for training
def format_conversation(example):
    return {
        "messages": [
            {"role": "user", "content": example["english"]},
            {"role": "assistant", "content": example["irish"]}
        ]
    }

formatted = dataset.map(format_conversation)
formatted.save_to_disk("data/irish_parallel")
```

### 2. Fine-Tuning

```python
# notebooks/finetune_irish.py
from unsloth import FastLanguageModel
from trl import SFTTrainer

# Load base model
model, tokenizer = FastLanguageModel.from_pretrained(
    "unsloth/Llama-3.2-3B-Instruct-bnb-4bit",
    max_seq_length=4096,
    load_in_4bit=True,
)

# Apply LoRA
model = FastLanguageModel.get_peft_model(
    model,
    r=64,
    lora_alpha=128,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
)

# Train
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    max_seq_length=4096,
    dataset_num_proc=4,
)
trainer.train()

# Save
model.save_pretrained("models/llama-3.2-3b-irish-lora")
```

### 3. Export to GGUF

```python
# Export for local inference
model.save_pretrained_gguf(
    "models/llama-3.2-3b-irish",
    tokenizer,
    quantization_method="q4_k_m"
)
```

### 4. Evaluation

```python
# notebooks/evaluate.py
def calculate_cer(predictions, references):
    """Character Error Rate for Irish text."""
    import editdistance
    import unicodedata

    total_chars = 0
    total_errors = 0

    for pred, ref in zip(predictions, references):
        pred = unicodedata.normalize('NFC', pred)
        ref = unicodedata.normalize('NFC', ref)
        total_chars += len(ref)
        total_errors += editdistance.eval(pred, ref)

    return total_errors / total_chars
```

## Model Selection Guide

### By Use Case

| Task | Model | Why |
|------|-------|-----|
| Irish text generation | UCCIX-Llama2-13B | +12% Irish accuracy |
| Math reasoning | Qwen2.5-Math-7B | Bilingual math |
| Mobile deployment | Llama-3.2-3B-Irish | 2GB footprint |
| Document OCR | olmOCR-2-7B | Accurate tables/LaTeX |
| Irish embeddings | GaBERT | Domain-specific |
| Speech recognition | wav2vec2-xlsr-irish | Best Irish WER |

### By Hardware

| Hardware | Max Model Size | Recommended |
|----------|---------------|-------------|
| iPhone 14/15 (6GB) | ~2GB | Llama-3.2-3B Q4 |
| iPhone Pro (8GB) | ~3GB | Llama-3.2-3B Q6 |
| Mac M1/M2 (16GB) | ~7GB | Qwen2.5-7B Q4 |
| Mac M3 Max (64GB+) | ~32GB | Qwen3-VL-32B Q4 |
| RTX 3090 (24GB) | ~13GB | UCCIX-13B |

## Notebook Organization

```
notebooks/
├── data_preparation/     # Dataset loading and formatting
├── fine_tuning/         # Training scripts
├── evaluation/          # Model evaluation
├── inference/           # Inference examples
└── experiments/         # Research experiments
```

## MLflow Integration

Track experiments with MLflow:

```python
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("irish-llm-finetuning")

with mlflow.start_run():
    mlflow.log_params({
        "model": "llama-3.2-3b",
        "lora_r": 64,
        "learning_rate": 2e-4,
    })

    # Train...

    mlflow.log_metrics({
        "cer": 0.15,
        "perplexity": 12.5,
    })

    mlflow.log_artifact("models/llama-3.2-3b-irish-lora")
```

## Catalog Structure (TODO)

```
catalog/
├── models.yaml    # Model registry
├── sources.yaml   # Data source registry
└── experiments/   # Experiment logs
```

Example `models.yaml`:
```yaml
models:
  - id: llama-3.2-3b-irish-v1
    base: unsloth/Llama-3.2-3B-Instruct-bnb-4bit
    type: text-generation
    languages: [irish, english]
    status: trained
    metrics:
      cer: 0.15
      perplexity: 12.5
    artifacts:
      - models/llama-3.2-3b-irish-lora
      - models/llama-3.2-3b-irish.Q4_K_M.gguf
```

## Best Practices

1. **Always use Unsloth for fine-tuning:**
   - 70% VRAM reduction
   - 2x training speedup
   - Native GGUF export

2. **Batch embeddings:**
   - Minimum 100 texts per call
   - Use provider batch limits

3. **Validate Irish output:**
   - Use CER (Character Error Rate)
   - Normalize Unicode (NFC)
   - Check dialect consistency

4. **Track experiments:**
   - Log all runs to MLflow
   - Version datasets
   - Save checkpoints

5. **Test on Irish-specific benchmarks:**
   - Common Voice Irish
   - UCCIX evaluation set
   - Leaving Cert sample papers

## Resources

- **Unsloth:** https://github.com/unslothai/unsloth
- **UCCIX:** https://huggingface.co/ReliableAI/UCCIX-Llama2-13B
- **GaBERT:** https://huggingface.co/DCU-NLP/bert-base-irish-cased-v1
- **MLflow:** https://mlflow.org
- **Common Voice Irish:** https://commonvoice.mozilla.org/ga
