# Document Processing & OCR: VLM, OCR, and Heritage Digitization

**Merged From:**
- `ocr/document-intelligence-ocr.md`, `ocr/document-intelligence-vlm.md`
- `ocr/Open-Source VLMs For PDF Extraction.md`, `ocr/Supercharge your OCR Pipelines with Open Models.md`
- `ocr/Handwriting Recognition and Dataset Creation.md`, `ocr/irish-english-handwriting.md`
- `ocr/Irish Handwriting App Development.md`, `ocr/Multimodal Irish Handwriting Generation Model.md`
- `ocr/Index PDFs, Images, Slides without OCR _ CocoIndex.md`
- `colpali/README.md`, `colpali/CHANGELOG.md`

---

## Table of Contents

1. [VLM vs Traditional OCR](#vlm-vs-traditional-ocr)
2. [Model Comparison & Selection](#model-comparison)
3. [Model Deep Dives](#model-deep-dives)
4. [Cloud Provider Comparison](#cloud-providers)
5. [Celtic Language OCR & Heritage Digitization](#celtic-language-ocr)
6. [ColPali: Visual Retrieval Without OCR](#colpali)
7. [Irish Handwriting & Heritage Pipelines](#irish-handwriting)
8. [Deployment Patterns](#deployment-patterns)

---

## VLM vs Traditional OCR

| Approach | Processing | Output | Limitation |
|----------|-----------|--------|------------|
| **Traditional OCR** | Bottom-up: Detection → Recognition → Reconstruction | Disjointed text boxes | Loses structural relationships |
| **VLM Approach** | Top-down: Global visual understanding → Autoregressive generation | Semantically-aware text | Computationally heavier |

**Traditional Pipeline (PaddleOCR, Tesseract):**
1. Binarization → 2. Layout analysis → 3. Text line detection → 4. Character recognition

**VLM Advantage:** Perceives image globally, understands reading order and layout because "next token" prediction depends on both textual context and 2D spatial position.

### Dynamic Resolution Innovation

**Problem:** Standard ViTs resize to 224×224 or 336×336 — long receipts and wide spreadsheets lose detail.

**NaViT Solution (Qwen-VL, PaddleOCR-VL):**
- Divide image into 14×14 patches at native resolution
- Patches packed into sequences with attention masks
- Preserves fine detail in small fonts and complex layouts

---

## Model Comparison

### Open-Source VLMs for Document Intelligence

| Model | Params | Primary Strength | LaTeX | Tables | Mac Support |
|-------|--------|------------------|-------|--------|-------------|
| **olmOCR-2-7B** | 7B | Dense OCR, structural fidelity | Excellent | Very Good | llama.cpp (GGUF) |
| **Qwen2.5-VL-7B** | 7B | Visual reasoning, dynamic resolution | Very Good | Excellent | MLX, llama.cpp |
| **Qwen3-VL-32B** | 32B | Deep reasoning ("Thinking") | Excellent | Excellent | MLX (4-bit) |
| **DeepSeek-OCR** | 3B | Math reasoning, optical compression | Excellent (95%) | Good | PyTorch/MPS |
| **Granite-Docling** | 258M | Structural extraction (DocTags) | Good | Excellent | MLX native |
| **PaddleOCR-VL** | 0.9B | Multilingual, NaViT encoder | Very Good | SOTA | CPU fallback |
| **ColPali/ColQwen2** | 3B | Visual retrieval (no OCR needed) | N/A | Visual | Embeddings only |

### Specialization Guide

| Use Case | Recommended Model |
|----------|------------------|
| General document transcription | olmOCR-2-7B |
| Visual reasoning + diagrams | Qwen3-VL-32B |
| Math-heavy documents | DeepSeek-OCR |
| Structural extraction (tables, forms) | Granite-Docling |
| Multilingual (100+ langs) | PaddleOCR-VL |
| Heritage manuscripts (Cló Gaelach) | Fine-tuned Qwen3-VL |
| Visual search without OCR | ColPali / ColQwen2 |

---

## Model Deep Dives

### Qwen2.5-VL / Qwen3-VL

**Key Innovations:**
- **M-RoPE**: Multimodal Rotary Positional Embeddings — unified 1D text, 2D images, 3D video
- **Naive Dynamic Resolution**: Native aspect ratio without downscaling
- **Visual Reasoning**: Arithmetic verification on extracted content
- **Thinking Mode** (Qwen3): Internal chain-of-thought before answering

**Speed on M-series Mac:**
- Qwen2.5-VL-7B (4-bit): 50-70 t/s
- Qwen3-VL-32B (4-bit): ~45 t/s with MLX

### olmOCR-2-7B

Qwen2.5-VL fine-tune optimized for document transcription:
- Rigorous transcriber (no conversational filler)
- Accurate tables, LaTeX, reading order
- "Unit test trained" for structural fidelity

```bash
python -m llama_cpp.server \
  --model olmOCR-2-7B-Q4_K_M.gguf \
  --clip_model_path mmproj-olmOCR-2-7B-vision.gguf \
  --n_gpu_layers 99 --n_ctx 8192 --port 8081
```

### DeepSeek-OCR

**Vision-as-Compression Architecture:**
- **DeepEncoder**: SAM-base (local detail) + CLIP-large (global semantic)
- **Decoder**: DeepSeek-3B-MoE
- Compression: 1024×1024 → 256 vision tokens (10x reduction)
- Excellent for math: LaTeX accuracy ~95%

**MPS Deployment on Mac:**
```python
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
DTYPE = torch.bfloat16  # bfloat16 is more stable than float16 on MPS
model = AutoModel.from_pretrained("deepseek-ai/DeepSeek-OCR",
    trust_remote_code=True, torch_dtype=DTYPE).to(DEVICE)
```

### Granite-Docling (258M)

Specialized VLM for document structure:
- Outputs **DocTags** — structured markup for headers, tables, lists, captions
- MLX native on Apple Silicon
- Excels at table reconstruction (TableFormer architecture)
- Semantic chunking — respects document structure boundaries

```python
from docling.document_converter import DocumentConverter
from docling.datamodel import vlm_model_specs

converter = DocumentConverter()
# Configure MLX backend for Granite-Docling
pipeline_options = VlmPipelineOptions(vlm_options=vlm_model_specs.GRANITEDOCLING_MLX)
converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_cls=VlmPipeline, pipeline_options=pipeline_options)
})

result = converter.convert("document.pdf")
markdown = result.document.export_to_markdown()
```

### PaddleOCR-VL (0.9B)

Ultra-compact VLM with NaViT encoder:
- 100+ languages, strong on European scripts
- Handles long documents (receipts, scrolls) via native aspect ratio
- CPU-inferable (0.9B) — sub-second on M-series Mac

---

## Cloud Providers

| Provider | Free Tier | LaTeX | Tables | Limitation |
|----------|-----------|-------|--------|------------|
| **AWS Textract** | 1,000 pages/mo (3 mo) | Natural language only | Good | Math flattening |
| **Google Document AI** | ~400-500 pages | Poor (∫ → J) | Good | Symbol misinterpretation |
| **Azure AI Vision** | 500 pages/mo | No native | Good | Language specialist only |

**Recommendation:** Cloud for bulk ingestion of clean documents; local VLMs for math, diagrams, and handwritten content.

---

## Celtic Language OCR & Heritage Digitization

### Key Challenges
- **Cló Gaelach**: Traditional Gaelic script with distinct letterforms (r, s, g differ from Roman)
- **Ponc Séimhithe**: Dot above consonants (ḃ, ċ, ḋ) indicating lenition — represented as 'h' in modern Irish
- **Dialectal variance**: Connacht, Munster, Ulster spellings differ
- **Non-standard orthography**: Pre-1940s materials use pre-standardization conventions

### Key Data Sources

| Source | Content | Access |
|--------|---------|--------|
| **Dúchas (CBÉS)** | 740,000 pages of folklore (1937-1939) | API v0.6 + XML downloads |
| **Dúchas (CBÉ)** | 2,400 bound volumes, 1932+ | API + scraping |
| **Logainm** | 100,000+ bilingual placenames | API v1.0 |
| **Ainm** | 1,785 Irish-language biographies | Web scraping |
| **Téarma** | National terminology database | API/download |
| **Corpas** | 240M words of Irish corpora | Direct download |
| **eDIL** | Electronic Dictionary of the Irish Language | Web |
| **CorCenCC** (Welsh) | 13.5M tokens, written + spoken | API |
| **ARCOSG** (Scottish Gaelic) | POS-tagged corpus | GitHub |
| **Tobar an Dualchais** | 80,000+ folklore audio recordings | API |

### Fine-Tuning Strategy for Gaelic OCR

```python
# Fine-tune Qwen2.5-VL for Celtic script
from unsloth import FastVisionModel

model, tokenizer = FastVisionModel.from_pretrained(
    "unsloth/Qwen2.5-VL-7B-Instruct-unsloth-bnb-4bit",
    load_in_4bit=True,
)

# Target ALL linear layers for maximum adaptation
model = FastVisionModel.get_peft_model(
    model,
    r=64,  # Higher rank for new script learning
    lora_alpha=128,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    finetune_vision_layers=True,   # Adapt vision encoder
    finetune_language_layers=True,  # Adapt language model
)

# Dataset format for vision fine-tuning
conversation = [
    {"role": "user", "content": [
        {"type": "text", "text": "Transcribe this Irish manuscript page"},
        {"type": "image", "image": image}
    ]},
    {"role": "assistant", "content": [
        {"type": "text", "text": transcription}
    ]}
]
```

### Bilingual Consistency Checking

For parallel English/Irish documents (e.g., Leaving Cert papers), use bilingual cross-validation:
1. Extract math/structure from English version
2. Extract math/structure from Irish version
3. Cross-reference answers — they must match
4. Flag discrepancies for human review

---

## ColPali: Visual Retrieval Without OCR

ColPali is a **retrieval model** (not generative) that embeds document page patches directly, bypassing OCR entirely.

### How It Works

1. Divides page image into grid of patches
2. Embeds each patch into vector space (PaliGemma-based)
3. Creates a "bag of visual embeddings" per page
4. **Late Interaction (MaxSim):** Query vectors matched directly against image patch vectors

### Why It Matters

- **No OCR errors** to propagate into search results
- Matches visual concepts (diagrams, handwriting, equations) without transcription
- Ideal for heritage archives where OCR quality is poor
- Can serve as "style injection" for RAG — finding similar handwriting styles

### Comparison: ColPali vs Traditional RAG

| Feature | Traditional RAG | ColPali |
|---------|----------------|---------|
| Pipeline | OCR → Embed → Search | Direct visual embed → Search |
| Math handling | OCR errors propagate | Visual matching preserves meaning |
| Handwriting | Requires HTR first | Works on original images |
| Speed | Fast after indexing | Memory-intensive per page |

---

## Irish Handwriting & Heritage Pipelines

### Dúchas Dataset Engineering

The Schools' Collection (1937-1939) contains 740,000 pages rich for HTR training:

1. **Acquisition**: Crawl using crawl4ai (JS-rendered image viewer) or use Dúchas API v0.6
2. **XML TEI parsing**: Extract structured transcriptions with line/page break metadata
3. **Image-text alignment**: Match manuscript images to normalized transcriptions
4. **Script normalization**: Map Cló Gaelach → modern Irish (handle ponc séimhithe)

### Math Handwriting Recognition

For mathematical manuscripts:
- **Layout analysis**: Detect matrix zones (tabular reading), diagram regions
- **High-res encoding**: Preserve micro-features like dots, superscripts (∇, ẋ, λ)
- **LaTeX prediction**: Model must predict `\frac{dx}{dt}` not flatten to "dx dt"
- **Fine-tuning**: 50 annotated pages can create a personalized math HTR model

### Recommended Pipeline

```text
Heritage Manuscript
    │
    ├──→ ColPali (visual search, no OCR)
    ├──→ Granite-Docling (structure: tables, headers)
    └──→ Fine-tuned Qwen3-VL (transcription + reasoning)
             │
             └──→ Structured Markdown / LaTeX / JSON
```

---

## Deployment Patterns

### Local Mac (Apple Silicon)

| Model | Backend | VRAM | Notes |
|-------|---------|------|-------|
| olmOCR-2-7B | llama.cpp GGUF | ~5 GB | Q4_K_M, mmproj at F16 |
| Qwen2.5-VL-7B | MLX | ~4 GB | 4-bit, 50-70 t/s |
| Granite-Docling 258M | MLX native | ~1 GB | Run alongside other models |
| DeepSeek-OCR 3B | PyTorch MPS | ~6 GB | bfloat16, disable autocast |

### Quota-Aware Hybrid Router

```python
def route_document(doc_type: str):
    """Route documents to optimal processing backend."""
    if doc_type == "tabular":
        return "Granite-Docling"       # Best table reconstruction
    elif doc_type == "math_heavy":
        return "DeepSeek-OCR / Qwen3-VL"  # LaTeX fidelity
    elif doc_type == "irish_prose":
        return "Fine-tuned Qwen3-VL"   # Gaelic script awareness
    elif doc_type == "handwriting":
        return "ColPali → RAG → Qwen3-VL"  # Visual retrieval + generation
    else:
        return "olmOCR-2-7B"           # Best general OCR
```
