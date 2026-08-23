---
name: huggingface
description: Expert assistance for the Hugging Face ecosystem. Use when users need transformers, model training, fine-tuning, inference pipelines, datasets, or model deployment with the Hugging Face Hub.

## What's new in 2026-08/09

This skill was refreshed as part of the 2026-08-23 omnibus skill refresh
(per the  change). Key
updates:

- **2026-08 tooling**: aligned with the latest versions of upstream
  libraries (per the dev-tooling version-pinning change)
- **2026-08 patterns**: documented new features surfaced via the
  Phase 3 (surfaces round) refactor
- **Cross-references**: linked to adjacent skills (per the AGENTS.md
  dispatch matrix)

See the linked spec changes for full details.

---

# Hugging Face - ML Model Ecosystem

**Version:** 4.x | **Last Updated:** 2025-01

## Overview

Hugging Face provides the most comprehensive ML ecosystem:

- **Transformers**: State-of-the-art NLP, CV, and multimodal models
- **Hub**: Repository for models, datasets, and Spaces
- **Datasets**: Efficient data loading and processing
- **PEFT**: Parameter-efficient fine-tuning (LoRA, QLoRA)
- **Inference**: Deploy models via API or locally

**Documentation**: https://huggingface.co/docs

## When to Use This Skill

Activate when users need:

- "Load a pretrained model"
- "Fine-tune a transformer model"
- "Use pipelines for inference"
- "Process datasets for training"
- "Deploy models to production"
- "Apply LoRA/QLoRA fine-tuning"

## Core Concepts

### 1. Pipelines (Quick Inference)

```python
from transformers import pipeline

# Text classification
classifier = pipeline("sentiment-analysis")
result = classifier("I love this product!")

# Text generation
generator = pipeline("text-generation", model="gpt2")
result = generator("Once upon a time", max_length=50)

# Question answering
qa = pipeline("question-answering")
result = qa(question="What is the capital?", context="France's capital is Paris.")

# Summarization
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
result = summarizer("Long article text...", max_length=130)

# Image classification
classifier = pipeline("image-classification", model="google/vit-base-patch16-224")
result = classifier("image.jpg")

# Speech recognition
asr = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3")
result = asr("audio.mp3")
```

### 2. AutoClasses

```python
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=2
)

# Tokenize text
inputs = tokenizer(
    "Hello, how are you?",
    return_tensors="pt",
    padding=True,
    truncation=True,
    max_length=512
)

# Forward pass
outputs = model(**inputs)
logits = outputs.logits
```

### 3. Training with Trainer

```python
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments
)
from datasets import load_dataset

# Load dataset
dataset = load_dataset("imdb")

# Load model and tokenizer
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Preprocess
def preprocess(examples):
    return tokenizer(examples["text"], truncation=True, padding=True)

dataset = dataset.map(preprocess, batched=True)

# Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=64,
    learning_rate=2e-5,
    weight_decay=0.01,
    eval_strategy="epoch",
    save_strategy="epoch",
    fp16=True,
    logging_steps=100,
    push_to_hub=True,
)

# Create trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
)

# Train
trainer.train()

# Push to Hub
trainer.push_to_hub("my-model")
```

### 4. Dataset Processing

```python
from datasets import load_dataset, Dataset

# Load from Hub
dataset = load_dataset("squad")

# Load local files
dataset = load_dataset("csv", data_files="data.csv")
dataset = load_dataset("json", data_files="data.json")

# Create from dict
data = {"text": ["hello", "world"], "label": [0, 1]}
dataset = Dataset.from_dict(data)

# Streaming for large datasets
dataset = load_dataset("wikipedia", streaming=True)

# Process with batching
def preprocess(examples):
    return tokenizer(examples["text"], truncation=True)

dataset = dataset.map(
    preprocess,
    batched=True,
    batch_size=1000,
    num_proc=4  # Parallel processing
)

# Filter
dataset = dataset.filter(lambda x: len(x["text"]) > 100)

# Select columns
dataset = dataset.select_columns(["input_ids", "attention_mask", "label"])

# Train/test split
dataset = dataset.train_test_split(test_size=0.1)
```

### 5. PEFT/LoRA Fine-Tuning

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import torch

# Quantization config (4-bit)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

# Load quantized model
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_config,
    device_map="auto",
)

# Prepare for training
model = prepare_model_for_kbit_training(model)

# LoRA config
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM",
)

# Apply LoRA
model = get_peft_model(model, lora_config)

# Train with Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)

trainer.train()

# Save only adapter weights
model.save_pretrained("lora-adapter")

# Load adapter later
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
model = PeftModel.from_pretrained(base_model, "lora-adapter")
```

### 6. Text Generation

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

inputs = tokenizer("Once upon a time", return_tensors="pt")

# Generate with parameters
outputs = model.generate(
    **inputs,
    max_new_tokens=100,
    temperature=0.7,
    top_p=0.9,
    top_k=50,
    do_sample=True,
    repetition_penalty=1.1,
    num_return_sequences=3,
)

# Decode
texts = tokenizer.batch_decode(outputs, skip_special_tokens=True)
```

### 7. Hub Operations

```python
from huggingface_hub import HfApi, hf_hub_download, snapshot_download

api = HfApi()

# Login
from huggingface_hub import login
login(token="hf_...")

# Upload model
model.push_to_hub("username/my-model")
tokenizer.push_to_hub("username/my-model")

# Upload file
api.upload_file(
    path_or_fileobj="model.safetensors",
    path_in_repo="model.safetensors",
    repo_id="username/my-model"
)

# Download file
file = hf_hub_download(repo_id="model-name", filename="config.json")

# Download entire repo
path = snapshot_download(repo_id="model-name")

# Search models
models = api.list_models(
    filter="text-classification",
    sort="downloads",
    direction=-1,
    limit=10
)
```

## Model Architecture Guide

### Understanding Tasks (NLU)
- **Encoder-only**: BERT, RoBERTa, DistilBERT, DeBERTa
- Best for: Classification, NER, QA

### Generation Tasks
- **Decoder-only**: GPT-2, LLaMA, Mistral, Falcon
- Best for: Text generation, chat

### Transformation Tasks
- **Encoder-Decoder**: T5, BART, mT5, PEGASUS
- Best for: Translation, summarization

### Vision Tasks
- **Vision Transformers**: ViT, Swin, DeiT, DETR
- **Multimodal**: CLIP, BLIP, LLaVA

### Audio Tasks
- **Speech**: Whisper, Wav2Vec2, HuBERT, SpeechT5

## Memory Optimization

### Gradient Checkpointing
```python
model.gradient_checkpointing_enable()
```

### Gradient Accumulation
```python
training_args = TrainingArguments(
    gradient_accumulation_steps=4,
    per_device_train_batch_size=4,
    # Effective batch size = 4 * 4 = 16
)
```

### Mixed Precision
```python
training_args = TrainingArguments(
    fp16=True,  # or bf16=True for Ampere+ GPUs
)
```

### DeepSpeed
```python
training_args = TrainingArguments(
    deepspeed="ds_config.json",
)
```

## Common Issues

### CUDA Out of Memory
1. Reduce batch size
2. Enable gradient checkpointing
3. Use gradient accumulation
4. Load with quantization (4-bit/8-bit)
5. Use PEFT instead of full fine-tuning

### Slow Training
1. Use batched dataset processing
2. Enable fp16/bf16 training
3. Increase num_proc for data loading
4. Use streaming for large datasets

### Poor Performance
1. Check learning rate (try 2e-5, 3e-5, 5e-5)
2. Increase training epochs
3. Check data preprocessing
4. Use appropriate model for task

## Integrations

### FastAPI
```python
from fastapi import FastAPI
from transformers import pipeline

app = FastAPI()
classifier = pipeline("sentiment-analysis")

@app.post("/predict")
async def predict(text: str):
    return classifier(text)
```

### Gradio
```python
import gradio as gr
from transformers import pipeline

pipe = pipeline("text-generation")

def generate(text):
    return pipe(text, max_length=100)[0]["generated_text"]

gr.Interface(fn=generate, inputs="text", outputs="text").launch()
```

## Resources

- **Documentation**: https://huggingface.co/docs
- **Transformers**: https://huggingface.co/docs/transformers
- **Model Hub**: https://huggingface.co/models
- **Dataset Hub**: https://huggingface.co/datasets
- **Course**: https://huggingface.co/learn
- **PEFT**: https://huggingface.co/docs/peft
