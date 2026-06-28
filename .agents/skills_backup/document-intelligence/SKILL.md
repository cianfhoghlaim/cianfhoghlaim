---
name: document-intelligence
description: Expert assistance for document AI with Vision-Language Models. Use when users need OCR, PDF extraction, table parsing, LaTeX recognition, Gaelic manuscript digitization, or fine-tuning VLMs with Unsloth.
---

# Document Intelligence & VLM Fine-Tuning

Comprehensive guide to Vision-Language Models, OCR systems, and document extraction pipelines.

## Overview

| Model | Params | LaTeX | Tables | Mac Support |
|-------|--------|-------|--------|-------------|
| **olmOCR-2-7B** | 7B | Excellent | Very Good | llama.cpp (GGUF) |
| **Qwen2.5-VL-7B** | 7B | Very Good | Excellent | MLX, llama.cpp |
| **Qwen3-VL-32B** | 32B | Excellent | Excellent | MLX (4-bit) |
| **DeepSeek-OCR** | 3B | 95% | Good | PyTorch/MPS |
| **Granite-Docling** | 258M | Good | Excellent | MLX native |
| **ColPali** | 3B | N/A | Visual | Retrieval only |

## When to Use This Skill

Activate when users need:

- "Extract text from scanned PDFs"
- "Process tables with VLMs"
- "Fine-tune Qwen-VL for document OCR"
- "Digitize historical manuscripts"
- "Build a document extraction pipeline"

## VLM vs Traditional OCR

| Approach | Processing | Output | Limitation |
|----------|-----------|--------|------------|
| **Traditional** | Detection → Recognition → Reconstruction | Disjointed boxes | Loses structure |
| **VLM** | Global visual understanding → Generation | Semantic text | Heavier compute |

**VLM Advantage:** Perceives images globally, understanding reading order and layout.

## Model Recommendations by Task

| Document Type | Primary Model | Fallback |
|---------------|---------------|----------|
| **Dense Text** | olmOCR-2-7B | Granite-Docling |
| **Mathematical** | DeepSeek-OCR | Qwen2.5-VL |
| **Tables/Structured** | Granite-Docling | PaddleOCR-VL |
| **Diagrams/Charts** | Qwen3-VL | ColPali |
| **Historical Manuscripts** | ColPali → Qwen2-VL | - |

## Model Deep Dives

### olmOCR-2-7B

Qwen2.5-VL fine-tune optimized for document transcription:
- Rigorous transcriber (no conversational filler)
- Accurate tables, LaTeX, reading order

```bash
python -m llama_cpp.server \
  --model olmOCR-2-7B-Q4_K_M.gguf \
  --clip_model_path mmproj-olmOCR-2-7B-vision.gguf \
  --n_gpu_layers 99 \
  --n_ctx 8192 \
  --port 8081
```

### DeepSeek-OCR

Vision-as-Compression architecture:
- SAM-base (local) + CLIP-large (global) encoder
- 1024x1024 → 256 vision tokens (10x compression)

```python
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
DTYPE = torch.bfloat16

model = AutoModel.from_pretrained(
    "deepseek-ai/DeepSeek-OCR",
    trust_remote_code=True,
    torch_dtype=DTYPE
).to(DEVICE)
```

### Granite-Docling

DocTags output format:
```xml
<document>
  <title>Chapter 1: Introduction</title>
  <table>
    <row><cell>Data 1</cell><cell>Data 2</cell></row>
  </table>
</document>
```

Install: `pip install "docling[mlx]"`

## ColPali: Visual Document Retrieval

Bypasses OCR for retrieval using late interaction:

```
Page → SigLIP Encoder → Patch Embeddings (32x32x128)
                                   ↓
Query → Gemma Encoder → Token Embeddings (Lx128)
                                   ↓
                  MaxSim → Similarity Map → Bounding Box
```

### MaxSim Localization

$$S(Q, D) = \sum_{j=1}^{N} \max_{i=1}^{M} (t_j \cdot p_i)$$

For each token, find the patch with highest similarity.

### Implementation

```python
from colpali_engine.models import ColQwen2Processor, ColQwen2

def generate_alignment_heatmap(image, text_query, model, processor):
    inputs = processor(text=[text_query], images=[image], return_tensors="pt")

    with torch.no_grad():
        out = model(**inputs)
        patch_embeddings = out.visual_embeddings  # [1, 1024, 128]
        query_embeddings = out.text_embeddings    # [1, L, 128]

    interaction = torch.einsum("bnd,bmd->bnm", query_embeddings, patch_embeddings)
    heatmap_flat = interaction.sum(dim=1).squeeze()

    side = int(np.sqrt(heatmap_flat.shape[0]))
    return heatmap_flat.view(side, side).cpu().numpy()
```

## Gaelic Heritage Digitization

### The Alignment Challenge

Historical collections contain:
- High-resolution manuscript images
- TEI-XML transcriptions (no coordinates)
- Page-level metadata only

### Gaelic Script Challenges

| Feature | OCR Challenge |
|---------|---------------|
| Long 'r' (r rotunda), long 's' (s) | Resembles other letters |
| Punctum delens (b, c, d) | Few pixels alter meaning |
| Tironian note (7) | Often fails tokenization |
| Baseline drift | Adjacent lines touch |

### ColPali Alignment Pipeline

1. Parse TEI-XML into line units
2. Generate similarity maps per line
3. Upscale heatmaps to original resolution
4. Otsu threshold + morphological ops
5. Extract bounding boxes

## Fine-Tuning Qwen2-VL with Unsloth

### Why Unsloth?

| Benefit | Detail |
|---------|--------|
| Memory | 4-bit QLoRA with minimal loss |
| Speed | 2x faster via Triton kernels |
| VRAM | 7-8B model: ~6-7GB |

### Dataset Format (Crop-Based OCR)

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "image", "image": "file:///path/to/crop.jpg"},
        {"type": "text", "text": "Transcribe this line exactly."}
      ]
    },
    {
      "role": "assistant",
      "content": [
        {"type": "text", "text": "Agus do bhi an ri 7 na saighdiuiri..."}
      ]
    }
  ]
}
```

### Training Configuration

```python
from unsloth import FastVisionModel
from trl import SFTTrainer

model, tokenizer = FastVisionModel.from_pretrained(
    "unsloth/Qwen2-VL-7B-Instruct",
    load_in_4bit=True,
    max_seq_length=2048,
)

model = FastVisionModel.get_peft_model(
    model,
    finetune_vision_layers=True,   # Essential for domain adaptation
    finetune_language_layers=True,
    r=16,
    lora_alpha=16,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
)

training_args = TrainingArguments(
    output_dir="./domain-qwen-vl",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    num_train_epochs=3,
    optim="adamw_8bit",
    bf16=True,
)
```

### Handling Special Characters

```python
# Add Tironian note to tokenizer
tokenizer.add_tokens(['7'])
model.resize_token_embeddings(len(tokenizer))

# Initialize from semantic equivalent
with torch.no_grad():
    agus_ids = tokenizer.encode('agus', add_special_tokens=False)
    agus_embedding = model.get_input_embeddings().weight[agus_ids].mean(dim=0)
    model.get_input_embeddings().weight[-1] = agus_embedding
```

## Hardware Recommendations

| Hardware | Stack |
|----------|-------|
| **Mac M1/M2 (16GB)** | Granite-Docling (MLX), olmOCR (GGUF Q4) |
| **Mac M3/M4 (32GB+)** | + Qwen2.5-VL-7B (MLX 4-bit) |
| **Mac M3 Max (64GB+)** | + Qwen3-VL-32B (MLX 4-bit) |
| **RTX 3090** | Qwen2.5-VL-7B (vLLM), DeepSeek-OCR |
| **A100** | Qwen3-VL-72B, high-throughput batch |

## Evaluation Metrics

### Character Error Rate (CER)

```python
def calculate_cer(predictions, references):
    total_chars = 0
    total_errors = 0

    for pred, ref in zip(predictions, references):
        pred = unicodedata.normalize('NFC', pred)
        ref = unicodedata.normalize('NFC', ref)
        total_chars += len(ref)
        total_errors += editdistance.eval(pred, ref)

    return total_errors / total_chars
```

### Grounding IoU

$$\text{IoU} = \frac{\text{Area of Overlap}}{\text{Area of Union}}$$

Threshold: IoU > 0.5 is correct detection.

## Cost Analysis (10,000 Pages)

| Engine | Cost |
|--------|------|
| Granite-Docling (local) | ~$0.10 |
| Qwen2.5-VL (local) | ~$0.50 |
| olmOCR (local) | ~$0.30 |
| AWS Textract | ~$15.00 |
| Google Doc AI | ~$15.00 |

**Local inference = 100x cost reduction.**

## Pipeline Summary

```
DATA PREPARATION
├── Parse TEI-XML into line units
├── Handle special characters
└── Normalize Unicode (NFC)
         ↓
COLPALI ALIGNMENT
├── Generate similarity maps
├── Upscale heatmaps
└── Extract bounding boxes
         ↓
DATASET CREATION
├── Crop images using boxes
├── Format as JSONL
└── Pad extreme aspect ratios
         ↓
UNSLOTH FINE-TUNING
├── Load Qwen2-VL (4-bit)
├── Apply LoRA to vision + language
└── Train with VisionDataCollator
         ↓
DEPLOYMENT
├── Export to GGUF (llama.cpp)
└── Or serve via MLX (Apple Silicon)
```

## Resources

- **ColPali:** https://github.com/illuin-tech/colpali
- **Qwen2-VL:** https://huggingface.co/Qwen/Qwen2-VL-7B-Instruct
- **Unsloth:** https://github.com/unslothai/unsloth
- **olmOCR:** https://github.com/allenai/olmocr
- **Granite-Docling:** https://github.com/IBM/granite-docling
- **Duchas API:** https://docs.gaois.ie/en/data/duchas/v0.6/api
