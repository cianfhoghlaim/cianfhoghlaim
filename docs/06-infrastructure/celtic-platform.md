---
truth: partial
---

# Celtic Language Platform

## Irish EdTech, Celtic NLP Resources & Self-Hosting Infrastructure

### `README.md` — 01-celtic-language-ai-resources

# Celtic Language AI Resources

This directory consolidates research on AI/ML resources for Celtic languages available on HuggingFace and related platforms, including language models, datasets, translation systems, and speech technologies.

## Overview

The Celtic language AI ecosystem spans four major languages with varying levels of maturity:

| Language | LLMs | ASR | TTS | Translation | Datasets | Maturity |
|----------|------|-----|-----|-------------|----------|----------|
| **Irish (Gaeilge)** | 5+ | 7+ | 1 | 4+ | 10+ | High |
| **Welsh (Cymraeg)** | 2 | 7+ | 1 | 2+ | 8+ | High |
| **Scottish Gaelic** | 2+ | 0* | 0 | 4+ | 38+ | Medium |
| **Manx (Gaelg)** | 0 | 0 | 0-1 | 4 | 2-3 | Low |

*Scottish Gaelic ASR/TTS expected Q4 2025

## Documents in this Category

| Document | Focus | Key Resources |
|----------|-------|---------------|
| `irish-nlp-resources.md` | Irish (Gaeilge) models and datasets | UCCIX, gaBERT, Common Voice |
| `scottish-gaelic-resources.md` | Scottish Gaelic resources | GPT-2 WECHSEL, XLSum |
| `welsh-resources.md` | Welsh (Cymraeg) resources | Mistral-7B-Cymraeg, techiaith ASR |
| `unified-model-comparison.md` | Cross-language analysis and recommendations | All languages |

## Key Organizations

| Organization | Languages | Focus Areas |
|--------------|-----------|-------------|
| **DCU-NLP** (Dublin City University) | Irish | gaBERT, gaELECTRA, NLP research |
| **ReliableAI/ReML-AI** | Irish | UCCIX LLMs, benchmarks |
| **techiaith** (Bangor University) | Welsh | ASR, TTS, complete NLP pipeline |
| **BangorAI** | Welsh | LLMs, translation |
| **EdinburghNLP** | Scottish Gaelic | ASR, translation research |
| **Helsinki-NLP** | All Celtic | OPUS-MT translation models |
| **Facebook/Meta AI** | All | MMS, M2M100, XLM-R |
| **Mozilla Foundation** | All | Common Voice datasets |

## Quick Reference: Best-in-Class Models

### Irish (Gaeilge)
- **LLM:** [UCCIX-Llama2-13B-Instruct](https://huggingface.co/ReliableAI/UCCIX-Llama2-13B-Instruct) - First open-source Irish LLM
- **Encoder:** [gaBERT](https://huggingface.co/DCU-NLP/bert-base-irish-cased-v1) - Best for NLP tasks
- **ASR:** [wav2vec2-large-xlsr-53-irish](https://huggingface.co/cpierse/wav2vec2-large-xlsr-53-irish)
- **Translation:** [opus-mt-en-ga](https://huggingface.co/Helsinki-NLP/opus-mt-en-ga)
- **Demo:** https://aine.chat

### Welsh (Cymraeg)
- **LLM:** [Mistral-7B-Cymraeg-Welsh-v2](https://huggingface.co/BangorAI/Mistral-7B-Cymraeg-Welsh-v2)
- **ASR:** [wav2vec2-xlsr-ft-cy](https://huggingface.co/techiaith/wav2vec2-xlsr-ft-cy) - 6.04% WER (4.05% with KenLM)
- **Collections:** https://huggingface.co/collections/techiaith/
- **Demo:** https://demo.bangor.ai

### Scottish Gaelic
- **LLM:** [gpt2-wechsel-scottish-gaelic](https://huggingface.co/benjamin/gpt2-wechsel-scottish-gaelic)
- **Translation:** [opus-mt-synthetic-en-gd](https://huggingface.co/Helsinki-NLP/opus-mt-synthetic-en-gd)
- **Dataset:** [XLSum](https://huggingface.co/datasets/csebuetnlp/xlsum) (2.31k BBC articles)

### Manx (Gaelg)
- **Translation:** [opus-mt-en-gv](https://huggingface.co/Helsinki-NLP/opus-mt-en-gv) (BLEU: 70.1)
- **Language ID:** [lang-id-voxlingua107-ecapa](https://huggingface.co/speechbrain/lang-id-voxlingua107-ecapa)
- **Dataset:** [OPUS Corpus](https://opus.nlpl.eu/) (Tatoeba)

## Data Availability

| Language | Text Tokens | Primary Sources |
|----------|-------------|-----------------|
| **Welsh** | 179M+ | CC-100, OSCAR, MADLAD-400 |
| **Irish** | 108M+ | CC-100, OSCAR, CulturaX |
| **Scottish Gaelic** | 22M | CC-100, mC4, GlotCC |
| **Manx** | Limited | OPUS Tatoeba |

## Research Gaps

### Universal Gaps
- Named Entity Recognition (NER) - Limited across all languages
- Sentiment Analysis - No dedicated models found
- Evaluation Benchmarks - No Celtic GLUE-equivalent

### Language-Specific Gaps
- **Irish:** No Whisper fine-tuned models
- **Scottish Gaelic:** No public ASR/TTS models (in development)
- **Welsh:** No dedicated NER model
- **Manx:** Everything except translation

## Cross-References

This category extends and connects to:
- **Category 02 (Multimodal Document Intelligence)** - Celtic OCR/VLM models
- **Category 03 (AI-Native Data Pipelines)** - Integration with dlt/Dagster pipelines
- **Main Research:** `../../organized/02-multimodal-document-intelligence/`

## ISO Language Codes

| Language | ISO 639-1 | ISO 639-2/3 | Locale | Script |
|----------|-----------|-------------|--------|--------|
| Irish | ga | gle | ga-IE | Latn |
| Scottish Gaelic | gd | gla | gd-GB | Latn |
| Welsh | cy | cym | cy-GB | Latn |
| Manx | gv | glv | gv-IM | Latn |

## Source Files Consolidated

- `CELTIC_LANGUAGES_AI_RESOURCES.md` - Cross-language comparison
- `irish_gaeilge_huggingface_resources.md` - Irish-specific resources
- `scottish_gaelic_huggingface_resources.md` - Scottish Gaelic resources
- `welsh-huggingface-resources.md` - Welsh resources


---

### `bilingual-ml-architecture.md` — 01-celtic-language-ai-resources

# Technical Architecture for a Bilingual Irish/English Mathematics Education System

Building an AI tutoring system for Irish Leaving Certificate mathematics that processes **8,000+ pages** of bilingual curriculum documents requires careful orchestration of cutting-edge tools across document processing, fine-tuning, RAG, and deployment. The recommended architecture combines **Qwen2.5-VL** for multimodal understanding, **ColPali** for visual document retrieval, **BAML** for structured extraction, and **Qwen2.5-Math-7B** fine-tuned via **Unsloth**—deployable within days on Modal or consumer hardware.

---

## Document processing pipeline delivers 95% LaTeX extraction accuracy

The document ingestion layer must handle mathematical equations, geometric diagrams, tables from marking schemes, and bilingual Irish/English text. Five tools emerged as viable candidates, each with distinct strengths:

**DeepSeek-OCR** (3B parameters, MIT licensed) achieves approximately **95% formula recognition accuracy** and excels at converting mathematical content to LaTeX. Its revolutionary "vision-as-compression" technology recovers 600-1000+ text tokens from just 64-100 vision tokens, enabling processing speeds of ~2,500 tokens/second on A100 GPUs—roughly **200,000 pages per day**. However, Irish language support remains unconfirmed in official documentation.

**Qwen2.5-VL and Qwen3-VL** from Alibaba offer the most compelling multilingual capabilities, supporting **32 languages** including "most European languages." The models excel at document understanding benchmarks (DocVQA), handle tables and charts well, and produce structured JSON output—ideal for marking scheme extraction. Available in sizes from 2B to 235B parameters, the **7B variant** offers optimal balance for this use case. Qwen3 explicitly includes Irish among its 119 supported languages.

**Granite-Docling** from IBM provides a remarkably lightweight alternative at only **258M parameters**, purpose-built for document conversion with enhanced equation recognition and excellent table structure preservation. Its DocTags format captures all page elements with positional information, and it integrates directly with LangChain and LlamaIndex.

| Tool | LaTeX Extraction | Diagrams | Tables | Irish Support | Model Size |
|------|-----------------|----------|--------|---------------|------------|
| DeepSeek-OCR | Excellent (95%) | Good | Very Good | Unconfirmed | 3B |
| Qwen2.5-VL | Very Good | Excellent | Excellent | Likely (European) | 2B-235B |
| Granite-Docling | Good | Good | Excellent | Experimental | 258M |
| ColPali | N/A (retrieval) | Excellent | Good (visual) | Visual-based | 3B |
| Unstract | Depends on LLM | Depends | Good | Depends | Orchestration |

**ColPali** represents a paradigm shift—rather than OCR-based extraction, it creates **multi-vector embeddings directly from document page images** using PaliGemma-3B and ColBERT late-interaction mechanisms. This bypasses traditional text extraction entirely, achieving **0.81 nDCG@5** on the ViDoRe benchmark versus 0.66 for traditional pipelines. For exam papers with geometric diagrams, ColPali retrieves relevant pages visually, then Qwen2.5-VL extracts the actual content.

The recommended pipeline chains these tools: **ColPali** for visual retrieval → **Qwen2.5-VL-7B** or **DeepSeek-OCR** for content extraction → **Granite-Docling** for structured table processing → **BAML** for schema-enforced output.

---

## Fine-tuning Qwen2.5-Math-7B with Unsloth requires only 6-7GB VRAM

The mathematics tutoring model should be fine-tuned on Leaving Certificate exam papers paired with marking schemes. **Qwen2.5-Math-7B-Instruct** emerges as the optimal base model, achieving **85.3% on the MATH benchmark** with Tool-Integrated Reasoning and solving up to 21/30 AIME problems when combined with reward model sampling.

**Unsloth** (docs.unsloth.ai) provides 2x faster training with 70% less VRAM compared to standard HuggingFace approaches. For a 7-8B model using QLoRA 4-bit quantization, fine-tuning requires only **~6-7GB VRAM**—achievable on consumer RTX 3060 or higher. The framework supports all major math models including DeepSeek-R1 distillations, Qwen2.5-Math variants, and Phi-4 Reasoning.

**DeepSeek-Math-V2** (November 2025) achieves gold-level performance on IMO 2025 and near-perfect scores on Putnam 2024, but its massive size (based on V3.2-Exp-Base) makes it impractical for fine-tuning. Instead, **DeepSeek-R1-Distill-Qwen-7B** offers excellent reasoning capabilities at manageable scale through knowledge distillation.

### Training data structure for exam preparation

The optimal format uses ShareGPT/ChatML structure with explicit chain-of-thought reasoning and marking scheme alignment:

```json
{
  "conversations": [
    {
      "role": "user",
      "content": "Leaving Certificate Higher Level, Paper 1:\nDifferentiate f(x) = (3x²+2)/(x-1) and find stationary points. (25 marks)"
    },
    {
      "role": "assistant",
      "content": "<think>Apply quotient rule, find where f'(x)=0...</think>\n\n**Step 1: Apply Quotient Rule** (5 marks)\n$$f'(x) = \\frac{6x(x-1) - (3x^2+2)(1)}{(x-1)^2}$$\n...\nFinal Answer: \\boxed{\\left(1 \\pm \\frac{\\sqrt{15}}{3}, y\\right)}"
    }
  ]
}
```

Critical hyperparameters for mathematical reasoning include higher LoRA rank (**r=64-128** vs typical 16-32), lower learning rates (**1e-5 to 5e-5**), and longer sequence lengths (4096+ tokens for multi-step solutions). Dataset mixing should combine 60-70% Leaving Certificate problems with 20-30% general mathematics (GSM8K, MATH benchmark samples) to prevent catastrophic forgetting.

---

## Irish language integration through UCCIX and Qwen3 native support

Irish presents unique challenges as a low-resource language with <0.1% of web content. Two paths enable bilingual support:

**UCCIX models** from University College Cork represent the state-of-the-art for Irish LLMs. The **UCCIX-Llama2-13B-Instruct** was trained on ~520M Irish tokens with vocabulary expansion to include native Irish tokens, outperforming LLaMA 2-70B on Irish tasks by up to 12%. The newer **UCCIX-Llama3.1-70B-Instruct** (December 2024) builds on LLaMA 3.1's improved architecture. These models can serve as teacher models for knowledge distillation or provide the expanded Irish tokenizer for fine-tuning other models.

**GaBERT** (DCU-NLP) offers Irish-specific BERT embeddings trained on 7.9M Irish sentences, useful for preprocessing and classification tasks. It outperforms multilingual BERT by +3.7 LAS on dependency parsing.

**Qwen3** explicitly lists Irish among its 119 supported languages, trained on 36 trillion tokens with Irish appearing alongside Welsh and Scottish Gaelic in its embedding space. This makes Qwen3-based models the most promising for native bilingual support without requiring extensive Irish-specific fine-tuning.

The **IRLBench benchmark** (May 2025) reveals a persistent ~20% performance gap between English and Irish on identical exam questions—best models achieve 55.8% Irish versus 76.2% English. Language fidelity remains problematic, with models producing valid Irish less than 80% of the time. Plan for Irish output verification and consider translation fallback strategies.

### Recommended multilingual approach

1. Use **Qwen2.5-Math-7B** as base (native Irish support)
2. Merge UCCIX tokenizer additions if Irish performance is insufficient
3. Include bilingual training examples with explicit Irish terminology
4. Validate outputs against Irish-BLiMP benchmark (1,020 minimal pairs)
5. Consider UCCIX as fallback generator for Irish-only responses

---

## RAG architecture combines ColPali visual retrieval with BGE-M3 embeddings

For 8,000+ curriculum pages, the retrieval system must handle mathematical notation, geometric diagrams, and bilingual content efficiently. **CocoIndex** provides the document indexing backbone with incremental processing—only re-computing affected portions when sources or logic change.

**BGE-M3** (BAAI) serves as the primary embedding model with three retrieval modes: dense semantic embeddings, learned sparse representations (outperforming BM25), and ColBERT-style multi-vector retrieval. It supports **100+ languages** with 8,192 token context length—critical for long mathematical documents. For optimal Irish support, combine with **LaBSE** embeddings which cover 109 languages including Irish and demonstrate superior performance on Irish classification tasks.

**ColPali** should operate alongside traditional embeddings for hybrid retrieval. ColQwen2.5-v0.2 (based on Qwen2.5-VL-3B) supports 29+ languages and eliminates OCR errors for equation-heavy pages. The tradeoff: ColPali produces 10-100x more vectors per document (1,024 patches per page), requiring token pooling for storage efficiency.

For the vector database, **Qdrant** (self-hosted or cloud) offers the best combination of features for this use case:
- Advanced payload filtering for metadata (exam year, topic, difficulty, language)
- Native multi-vector support for ColPali embeddings
- Hybrid search combining sparse and dense retrieval
- Highest RPS and lowest latency in benchmarks

### Chunking strategy for mathematical content

Standard semantic chunking fails around equations because mathematical notation creates semantic dissimilarity with surrounding explanatory text. The **semantic double-pass merging** algorithm addresses this:

1. First pass: Standard semantic chunking
2. Second pass: If chunks 1 and 3 are semantically similar but chunk 2 (equation) differs, merge all three

Configure chunk sizes of **1000-2000 tokens** with 200-500 overlap, using separators that respect LaTeX boundaries: `["\\n\\n", "\\n", ".", "$$", "\\["]`. Never split inside LaTeX environments.

---

## Deployment on Modal enables scale-to-zero with sub-second cold starts

**Modal** provides optimal serverless deployment for fine-tuned models with per-second GPU billing and automatic scaling. Key pricing for math tutoring workloads:

| GPU | Price/Hour | VRAM | Best For |
|-----|-----------|------|----------|
| NVIDIA T4 | $0.59 | 16GB | Development/testing |
| NVIDIA L4 | $0.80 | 24GB | 7B models quantized |
| NVIDIA A10 | $1.10 | 24GB | 7B-13B production |
| NVIDIA A100 40GB | $2.10 | 40GB | 13B-70B models |

Modal's Rust-based container stack achieves **<1 second cold starts**, critical for conversational tutoring where users expect immediate responses. Unsloth-trained models export directly to GGUF, vLLM, or native formats for deployment.

**Consumer hardware** remains viable for development and small-scale deployment. An **RTX 4090** (24GB, ~$1,800) runs 7B models at ~50 tokens/second with Q4_K_M quantization, or 13B models at 30-40 t/s. The RTX 3090 achieves similar performance at lower cost (~$1,500 used).

For inference engines, **vLLM** with PagedAttention provides 2-4x faster throughput than standard approaches and integrates well with Modal deployments. Implement **KV caching** (built into vLLM) plus **semantic response caching** for common math problems—research shows 50-90% GPU cost reduction with proper caching.

**Latency targets** for educational chatbots: Time-to-First-Token under **2 seconds**, token generation at **20-50 tokens/second minimum**. Studies show users lose patience after 3 seconds of waiting. Always use streaming responses.

---

## BAML enforces schema compliance for structured exam paper extraction

**BAML** (BoundaryML) is a domain-specific language for building reliable AI workflows with structured outputs, perfectly suited for extracting questions, marks, and topics from exam papers. Its Schema-Aligned Parsing works even without native tool-calling APIs, handling markdown in JSON and chain-of-thought reasoning.

```baml
class MathQuestion {
  number string
  text string @description("Full question in original language")  
  text_irish string?
  marks int
  topic "Algebra" | "Geometry" | "Calculus" | "Statistics"
  marking_criteria MarkingCriterion[]
  requires_diagram bool
}

function ExtractExamPaper(document: pdf) -> ParsedExam {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Extract all questions from this Leaving Certificate exam paper.
    Identify marks, topics, and any diagrams required.
    {{ document }}
    {{ ctx.output_format }}
  "#
}
```

BAML generates type-safe clients for Python and TypeScript, enabling compile-time verification of extraction schemas. The VSCode playground provides parallel test execution for iterating on extraction prompts. Native multimodal support handles PDFs, images, and audio inputs directly.

---

## Complete architecture recommendation

```
┌─────────────────────────────────────────────────────────────────┐
│                 DOCUMENT INGESTION (CocoIndex)                  │
│  PDF Sources → Language Detection → Content Routing             │
│  ├── Text/Equations → DeepSeek-OCR → LaTeX extraction          │
│  ├── Diagrams → ColPali → Visual embeddings                     │
│  └── Tables → Granite-Docling → Structured extraction          │
│  ↓                                                              │
│  BAML Structured Extraction → Metadata + JSON                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 KNOWLEDGE BASE (Qdrant)                         │
│  ├── text_chunks: BGE-M3 embeddings (dense + sparse)           │
│  ├── visual_pages: ColPali multi-vector embeddings             │
│  └── Payload filtering: {language, level, topic, year}         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 RAG RETRIEVAL (LlamaIndex)                      │
│  Query → Language detection → Hybrid search → Reranking        │
│  Return: Relevant questions + marking schemes + diagrams        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 GENERATION (Fine-tuned Model)                   │
│  Qwen2.5-Math-7B fine-tuned via Unsloth on LC exam data        │
│  BAML functions for step-by-step solutions, bilingual output   │
│  Deployment: Modal (serverless) or vLLM (self-hosted)          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Rapid prototyping roadmap achieves demo in 3 days

**Days 1-3 (Foundation):**
- Set up BAML project with exam paper schemas
- Create PDF extraction pipeline: PyMuPDF4LLM + BAML
- Initialize ChromaDB for vector storage (upgrade to Qdrant later)
- Build Streamlit chat interface
- Single exam paper end-to-end demo

**Week 1 (Core RAG):**
- Integrate LlamaIndex with vector store
- Implement topic-filtered retrieval
- Add step-by-step solution generation
- Basic Irish language support via Qwen3

**Week 2 (Enhancement):**
- Multi-modal diagram handling with ColPali
- Marking scheme integration for grading
- Practice test generation from topic pools
- Fine-tune Qwen2.5-Math-7B with Unsloth on collected data

**Weeks 3-4 (Production):**
- Deploy to Modal with autoscaling
- Implement response caching
- Bilingual output verification
- Evaluation against IRLBench

---

## Conclusion: Achievable innovation with open-source tools

This architecture leverages entirely open-source or commercially permissive models—Qwen (Apache 2.0), DeepSeek-OCR (MIT), BAML (Apache 2.0), Granite-Docling (MIT)—while addressing the unique challenges of mathematical notation, geometric diagrams, and Irish language support. 

The combination of **ColPali for visual retrieval** and **Qwen2.5-VL for content extraction** represents the cutting edge for document understanding, while **Unsloth-powered fine-tuning** of **Qwen2.5-Math-7B** enables domain adaptation at minimal cost (6-7GB VRAM). Irish language capabilities come from Qwen3's native support supplemented by UCCIX model techniques when higher accuracy is needed.

Total infrastructure cost for an MVP: **~$100-300/month** on Modal with free credits, or near-zero for development on consumer RTX hardware. The prototype-focused approach—BAML + LlamaIndex + Streamlit—enables functional demos within days, with full bilingual tutoring capability achievable in 2-4 weeks.

---

### `irish-nlp-resources.md` — 01-celtic-language-ai-resources

# Irish (Gaeilge) Language AI Resources

## Overview

**ISO Codes:** ga (639-1), gle (639-2/3), Locale: ga-IE
**Speakers:** ~1.85 million (2022 census)
**Maturity Level:** High - Most developed Celtic language AI ecosystem

---

## 1. Language Models

### 1.1 UCCIX - Irish-eXcellence LLM (2024)

The first and most advanced open-source Irish LLM.

| Property | Value |
|----------|-------|
| **Base Model** | Llama 2-13B / Llama 3.1-70B |
| **Irish Tokens** | ~520M |
| **Performance** | Up to 12% improvement over larger models |

**HuggingFace Models:**
- **Pre-trained:** https://huggingface.co/ReliableAI/UCCIX-Llama2-13B
- **Instruction-tuned:** https://huggingface.co/ReliableAI/UCCIX-Llama2-13B-Instruct
- **Llama 3.1 70B:** https://huggingface.co/ReliableAI/UCCIX-Llama3.1-70B-Instruct-19122024

**Resources:**
- Live Demo: https://aine.chat
- Paper: https://arxiv.org/abs/2405.13010
- GitHub: https://github.com/ReML-AI/UCCIX

### 1.2 gaBERT - Irish BERT Model

Best performing encoder model for Irish NLP tasks.

| Property | Value |
|----------|-------|
| **Training Data** | 7.9M Irish sentences |
| **Architecture** | BERT-base (cased) |
| **Organization** | DCU-NLP |

**HuggingFace:** https://huggingface.co/DCU-NLP/bert-base-irish-cased-v1

**Usage:**
```python
from transformers import AutoModel, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("DCU-NLP/bert-base-irish-cased-v1")
model = AutoModel.from_pretrained("DCU-NLP/bert-base-irish-cased-v1")
```

### 1.3 gaELECTRA

| Property | Value |
|----------|-------|
| **Training Data** | 7.9M Irish sentences |
| **Architecture** | ELECTRA-base |

**HuggingFace:** https://huggingface.co/DCU-NLP/electra-base-irish-cased-generator-v1

### 1.4 BERTreach - Irish RoBERTa

| Property | Value |
|----------|-------|
| **Training Data** | 47M tokens |
| **Architecture** | RoBERTa |
| **License** | Apache-2.0 |

**HuggingFace:** https://huggingface.co/jimregan/BERTreach

---

## 2. Datasets

### 2.1 Text Corpora

| Dataset | Size | Source | URL |
|---------|------|--------|-----|
| **CC-100** | 108M tokens | CommonCrawl | https://huggingface.co/datasets/statmt/cc100 |
| **OSCAR** | Multi-version | CommonCrawl | https://huggingface.co/datasets/oscar-corpus/OSCAR-2301 |
| **CulturaX** | 6.3T tokens (167 langs) | Mixed | https://huggingface.co/datasets/uonlp/CulturaX |
| **Irish-English Parallel** | Parallel corpus | UCCIX project | https://huggingface.co/datasets/ReliableAI/Irish-English-Parallel-Collection |

**Loading CC-100 Irish:**
```python
from datasets import load_dataset
irish_data = load_dataset("statmt/cc100", "ga")
```

### 2.2 Speech Datasets

| Dataset | Content | URL |
|---------|---------|-----|
| **Common Voice** | Crowdsourced speech + transcriptions | Multiple versions (9.0-19.0) |
| **Tatoeba-Speech-Irish** | Synthetic audio (2h 39m) | https://huggingface.co/datasets/ymoslem/Tatoeba-Speech-Irish |
| **XTREME-S** | Multilingual speech benchmark | https://huggingface.co/datasets/google/xtreme_s |

**Loading Common Voice:**
```python
from datasets import load_dataset
cv = load_dataset("mozilla-foundation/common_voice_13_0", "ga")
```

### 2.3 Benchmarks

| Benchmark | Type | Availability |
|-----------|------|--------------|
| **IrishQA** | Question Answering | GitHub (UCCIX repo) |
| **Irish MT-bench** | LLM Evaluation | GitHub (UCCIX repo) |

---

## 3. Translation Models

### 3.1 Helsinki-NLP OPUS-MT

| Direction | URL | License |
|-----------|-----|---------|
| **English → Irish** | https://huggingface.co/Helsinki-NLP/opus-mt-en-ga | CC-BY 4.0 |
| **Irish → English** | https://huggingface.co/Helsinki-NLP/opus-mt-ga-en | CC-BY 4.0 |

**Usage:**
```python
from transformers import MarianMTModel, MarianTokenizer

model_name = "Helsinki-NLP/opus-mt-en-ga"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

text = "Hello, how are you?"
translated = model.generate(**tokenizer(text, return_tensors="pt"))
print(tokenizer.decode(translated[0], skip_special_tokens=True))
```

### 3.2 Multilingual Translation

| Model | Parameters | Languages | URL |
|-------|------------|-----------|-----|
| **M2M100** | 418M / 1.2B | 100 (9,900 pairs) | https://huggingface.co/facebook/m2m100_418M |
| **SMaLL-100** | 0.3B | 10K+ pairs | https://huggingface.co/alirezamsh/small100 |

---

## 4. Speech Recognition (ASR)

### 4.1 Wav2Vec2 Models

| Model | Base | Training Data | URL |
|-------|------|---------------|-----|
| **wav2vec2-large-xlsr-53-irish** | XLSR-53 | Common Voice | https://huggingface.co/cpierse/wav2vec2-large-xlsr-53-irish |
| **wav2vec2-large-xls-r-1b-ga-ie** | XLS-R 1B | CV 8.0 + Living Irish | https://huggingface.co/Aditya3107/wav2vec2-large-xls-r-1b-ga-ie |
| **wav2vec2-large-xls-r-1b-Irish** | XLS-R 1B | Common Voice | https://huggingface.co/kingabzpro/wav2vec2-large-xls-r-1b-Irish |
| **wav2vec2-large-xlsr-irish-basic** | XLSR | Common Voice | https://huggingface.co/jimregan/wav2vec2-large-xlsr-irish-basic |

**Usage:**
```python
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

processor = Wav2Vec2Processor.from_pretrained("cpierse/wav2vec2-large-xlsr-53-irish")
model = Wav2Vec2ForCTC.from_pretrained("cpierse/wav2vec2-large-xlsr-53-irish")
```

### 4.2 Facebook MMS (Massively Multilingual Speech)

| Model | Languages | Irish Code | URL |
|-------|-----------|------------|-----|
| **mms-1b-all** | 1162 | ga/gle | https://huggingface.co/facebook/mms-1b-all |
| **mms-1b-l1107** | 1107 | ga/gle | https://huggingface.co/facebook/mms-1b-l1107 |
| **mms-1b-fl102** | 102 | ga/gle | https://huggingface.co/facebook/mms-1b-fl102 |

**Usage:**
```python
from transformers import Wav2Vec2ForCTC, AutoProcessor

processor = AutoProcessor.from_pretrained("facebook/mms-1b-all")
model = Wav2Vec2ForCTC.from_pretrained("facebook/mms-1b-all", target_lang="gle", ignore_mismatched_sizes=True)
```

---

## 5. Text-to-Speech (TTS)

### 5.1 Facebook MMS-TTS

| Property | Value |
|----------|-------|
| **Languages** | 1107+ |
| **Architecture** | VITS |
| **Irish Model** | facebook/mms-tts-gle |

**HuggingFace:** https://huggingface.co/facebook/mms-tts

**Language Coverage:** https://dl.fbaipublicfiles.com/mms/misc/language_coverage_mms.html

---

## 6. Other NLP Resources

### 6.1 Multilingual Models Supporting Irish

| Model | Languages | URL |
|-------|-----------|-----|
| **XLM-RoBERTa** | 100 | https://huggingface.co/FacebookAI/xlm-roberta-base |
| **LaBSE** | 109 | https://huggingface.co/setu4993/LaBSE |

### 6.2 NER Models (jimregan)

- `jimregan/bert-base-irish-cased-v1-finetuned-ner`
- `jimregan/electra-base-irish-cased-discriminator-v1-finetuned-ner`

### 6.3 Collections

- **Irish-English Speech Translation:** https://huggingface.co/collections/ymoslem/irish-english-speech-translation-datasets-665dd9e8fbaa279db3474ca0

---

## 7. Research Gaps & Opportunities

| Gap | Status | Opportunity |
|-----|--------|-------------|
| **Whisper fine-tuning** | Not found | High-impact contribution |
| **NER datasets** | Limited | Create annotated corpus |
| **Sentiment analysis** | Not found | Build dataset from social media |
| **IrishQA on HuggingFace** | GitHub only | Upload to Hub |

---

## 8. Integration Examples

### 8.1 With dlt Pipeline

```python
import dlt
from transformers import pipeline

# Irish-English translation pipeline
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-ga-en")

@dlt.resource
def translate_irish_documents(docs: list[str]):
    for doc in docs:
        translation = translator(doc)[0]['translation_text']
        yield {
            "original": doc,
            "translated": translation
        }
```

### 8.2 With BAML Schema

```baml
function TranslateToIrish(text: string) -> string {
  client OpenAI
  prompt #"
    Translate the following English text to Irish (Gaeilge).
    Use modern standard Irish (An Caighdeán Oifigiúil).

    Text: {{ text }}

    Irish translation:
  "#
}
```

---

## References

- UCCIX Paper: https://arxiv.org/abs/2405.13010
- gaBERT Paper: https://arxiv.org/abs/2107.12930
- Irish-BERT GitHub: https://github.com/jbrry/Irish-BERT
- MMS Language Coverage: https://dl.fbaipublicfiles.com/mms/misc/language_coverage_mms.html


---

### `scottish-gaelic-resources.md` — 01-celtic-language-ai-resources

# Scottish Gaelic AI Resources

## Overview

**ISO Codes:** gd (639-1), gla (639-2/3), Locale: gd-GB
**Speakers:** ~69,700 (2011 census)
**Maturity Level:** Medium - Strong datasets, limited dedicated models

---

## 1. Language Models

### 1.1 GPT-2 WECHSEL Scottish Gaelic

The primary dedicated Scottish Gaelic language model.

| Property | Value |
|----------|-------|
| **Model** | `benjamin/gpt2-wechsel-scottish-gaelic` |
| **Architecture** | GPT-2 with WECHSEL transfer learning |
| **Perplexity** | 16.43 (vs 19.53 from scratch) |
| **Efficiency** | 64x less training effort |
| **License** | MIT |

**HuggingFace:** https://huggingface.co/benjamin/gpt2-wechsel-scottish-gaelic

**Usage:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("benjamin/gpt2-wechsel-scottish-gaelic")
model = AutoModelForCausalLM.from_pretrained("benjamin/gpt2-wechsel-scottish-gaelic")

input_text = "Tha an latha"
input_ids = tokenizer(input_text, return_tensors="pt").input_ids
outputs = model.generate(input_ids, max_length=50, do_sample=True)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

**References:**
- WECHSEL Paper: https://aclanthology.org/2022.naacl-main.293/
- GitHub: https://github.com/CPJKU/wechsel

### 1.2 XLM-RoBERTa POS Tagging

| Property | Value |
|----------|-------|
| **Model** | `wietsedv/xlm-roberta-base-ft-udpos28-gd` |
| **Task** | Part-of-Speech Tagging |
| **Training** | Universal Dependencies v2.8 |
| **License** | Apache 2.0 |

**HuggingFace:** https://huggingface.co/wietsedv/xlm-roberta-base-ft-udpos28-gd

### 1.3 Multilingual Models with Scottish Gaelic Support

| Model | Parameters | Languages | Scottish Gaelic Support |
|-------|------------|-----------|------------------------|
| **mT5** | Various | 101 | Included via mC4 |
| **M2M100** | 418M/1.2B | 100 | Language code: `gd` |
| **NLLB-200** | 600M-3.3B | 200 | Language code: `gla_Latn` |
| **SMALL-100** | 0.3B | 101 | Included |

---

## 2. Datasets

### 2.1 Text Corpora

| Dataset | Size | Source | URL |
|---------|------|--------|-----|
| **CC-100** | 22M tokens | CommonCrawl | https://huggingface.co/datasets/statmt/cc100 |
| **GlotCC-V1** | 18.8k rows | Web crawl | https://huggingface.co/datasets/cis-lmu/GlotCC-V1 |
| **mC4** | Included | CommonCrawl | https://huggingface.co/datasets/legacy-datasets/mc4 |

**Loading CC-100:**
```python
from datasets import load_dataset
gd_data = load_dataset("statmt/cc100", "gd")
```

### 2.2 Summarization & Parallel Corpora

| Dataset | Content | Size | URL |
|---------|---------|------|-----|
| **XLSum** | BBC articles | 2.31k rows | https://huggingface.co/datasets/csebuetnlp/xlsum |
| **Tatoeba MT** | Translation pairs | Various | https://huggingface.co/datasets/Helsinki-NLP/tatoeba_mt |
| **OPUS-100** | Parallel corpus | Various | https://huggingface.co/datasets/Helsinki-NLP/opus-100 |
| **FLORES-200** | Evaluation | 3001 sentences | https://huggingface.co/datasets/facebook/flores |

**Loading XLSum:**
```python
from datasets import load_dataset
xlsum_gd = load_dataset("csebuetnlp/xlsum", "scottish_gaelic")
```

### 2.3 Linguistic Resources

| Dataset | Content | URL |
|---------|---------|-----|
| **Universal Dependencies** | Treebank annotation | https://huggingface.co/datasets/universal-dependencies/universal_dependencies |
| **ARCOSG** | Annotated Reference Corpus | University of Edinburgh DataShare |
| **Corpas na Gaidhlig** | 30M words | University of Glasgow |

### 2.4 Speech Datasets

| Dataset | Status | Notes |
|---------|--------|-------|
| **Common Voice** | Available via Mozilla Data Collective | Previously on HuggingFace |
| **DASG Audio Archive** | External | Cluas ri Claisneachd |

---

## 3. Translation Models

### 3.1 OPUS-MT Synthetic English-Scottish Gaelic

Best dedicated translation model for Scottish Gaelic.

| Property | Value |
|----------|-------|
| **Model** | `Helsinki-NLP/opus-mt-synthetic-en-gd` |
| **ChrF Score** | 51.10 |
| **COMET Score** | 78.04 |
| **Training** | GPT-4o forward-translated Europarl |
| **License** | CC-BY-4.0 |

**HuggingFace:** https://huggingface.co/Helsinki-NLP/opus-mt-synthetic-en-gd

**Usage:**
```python
from transformers import MarianMTModel, MarianTokenizer

model_name = "Helsinki-NLP/opus-mt-synthetic-en-gd"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

text = "Hello, how are you today?"
translated = model.generate(**tokenizer(text, return_tensors="pt"))
print(tokenizer.decode(translated[0], skip_special_tokens=True))
```

### 3.2 Multilingual Translation Models

| Model | Parameters | Downloads | URL |
|-------|------------|-----------|-----|
| **M2M100-418M** | 418M | 849k/month | https://huggingface.co/facebook/m2m100_418M |
| **M2M100-1.2B** | 1.2B | - | https://huggingface.co/facebook/m2m100_1.2B |
| **SMALL-100** | 0.3B | 6.5k/month | https://huggingface.co/alirezamsh/small100 |
| **NLLB-200-3.3B** | 3.3B | - | https://huggingface.co/facebook/nllb-200-3.3B |

**Using M2M100:**
```python
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

tokenizer.src_lang = "en"
encoded = tokenizer("Hello, this is a test.", return_tensors="pt")
generated_tokens = model.generate(
    **encoded,
    forced_bos_token_id=tokenizer.get_lang_id("gd")
)
print(tokenizer.decode(generated_tokens[0], skip_special_tokens=True))
```

---

## 4. Speech Recognition (ASR)

### 4.1 Current Status

**No publicly available dedicated ASR models found on HuggingFace.**

### 4.2 Research Progress

| Achievement | Performance | Source |
|------------|-------------|--------|
| **Best WER (2025)** | 12.8% | Interspeech 2025 paper |
| **Whisper-Turbo fine-tuned** | 19.0% WER | Research (unpublished) |
| **Historical Kaldi** | 26.30% WER | University of Edinburgh |

### 4.3 Upcoming Development

| Initiative | Timeline | Details |
|-----------|----------|---------|
| **Scottish Government Funded** | Q4 2025 | Speech-to-text API |
| **University of Edinburgh** | 2025 | £225,000 funding for LLM development |

**Data Sources for Future Development:**
- 30 million words from Corpas na Gaidhlig
- DASG's Cluas ri Claisneachd audio archive

### 4.4 Fine-Tuning Base Models

For ASR development, consider fine-tuning:

| Model | URL | Notes |
|-------|-----|-------|
| **Whisper Large-v3** | https://huggingface.co/openai/whisper-large-v3 | Best baseline |
| **Wav2Vec2-XLSR-53** | https://huggingface.co/facebook/wav2vec2-large-xlsr-53 | Cross-lingual |
| **MMS-1B** | https://huggingface.co/facebook/mms-1b-all | 1162 languages |

---

## 5. Key Organizations

| Organization | Focus | Resources |
|--------------|-------|-----------|
| **EdinburghNLP** | ASR, translation research | https://huggingface.co/EdinburghNLP |
| **Helsinki-NLP** | Translation models | OPUS-MT project |
| **University of Edinburgh** | LLM development | £225k government funding |
| **National Library of Scotland** | Historical documents | https://huggingface.co/NationalLibraryOfScotland |

---

## 6. External Resources

### 6.1 Non-HuggingFace Corpora

| Resource | Content | Access |
|----------|---------|--------|
| **ARCOSG** | Annotated Reference Corpus | Edinburgh DataShare |
| **Corpas na Gaidhlig** | 30M words | University of Glasgow |
| **DASG** | Digital Archive | https://dasg.ac.uk/ |
| **Scottish Gaelic Wikipedia** | General text | Wikipedia dump |
| **Sketch Engine** | Text corpora | Subscription required |

### 6.2 Browse Resources

- **Models:** https://huggingface.co/models?language=gd
- **Datasets:** https://huggingface.co/datasets?language=language:gla

---

## 7. Research Gaps & Opportunities

| Gap | Status | Priority |
|-----|--------|----------|
| **Fine-tuned ASR models** | In development | High |
| **TTS models** | Not available | High |
| **Dedicated BERT model** | Not available | Medium |
| **NER datasets** | Limited | Medium |
| **Question answering** | Not available | Medium |

---

## 8. Integration Examples

### 8.1 With dlt Pipeline

```python
import dlt
from transformers import pipeline

# Scottish Gaelic translation pipeline
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-synthetic-en-gd")

@dlt.resource
def translate_to_scottish_gaelic(texts: list[str]):
    for text in texts:
        translation = translator(text)[0]['translation_text']
        yield {
            "original": text,
            "scottish_gaelic": translation
        }
```

### 8.2 Summarization with XLSum

```python
from datasets import load_dataset
from transformers import pipeline

# Load Scottish Gaelic summarization data
xlsum_gd = load_dataset("csebuetnlp/xlsum", "scottish_gaelic", split="train")

# Use for training or evaluation
for article in xlsum_gd:
    print(f"Title: {article['title']}")
    print(f"Summary: {article['summary']}")
    print(f"URL: {article['url']}")
```

---

## References

- WECHSEL Paper: https://aclanthology.org/2022.naacl-main.293/
- Scottish Gaelic ASR Guide (2025): https://arxiv.org/abs/2506.04915
- OPUS-MT Synthetic Paper: ArXiv 2505.14423
- University of Edinburgh Initiative: https://www.ed.ac.uk/news/2023/ai-initiative-gives-gaelic-a-foothold-in-the-digit


---

### `unified-model-comparison.md` — 01-celtic-language-ai-resources

# Celtic Language AI - Unified Model Comparison

## Executive Summary

This document provides a cross-language comparison of AI/ML resources for Celtic languages, enabling informed technology selection for multilingual Celtic projects.

---

## 1. Maturity Comparison

### 1.1 Overall Resource Availability

| Language | LLMs | ASR | TTS | Translation | Datasets | Maturity |
|----------|------|-----|-----|-------------|----------|----------|
| **Irish (Gaeilge)** | 5+ | 7+ | 1 | 4+ | 10+ | High |
| **Welsh (Cymraeg)** | 2 | 7+ | 1 | 2+ | 8+ | High |
| **Scottish Gaelic** | 2+ | 0* | 0 | 4+ | 38+ | Medium |
| **Manx (Gaelg)** | 0 | 0 | 0-1 | 4 | 2-3 | Low |

*Scottish Gaelic ASR/TTS expected Q4 2025

### 1.2 Feature Matrix

| Feature | Irish | Scottish Gaelic | Welsh | Manx |
|---------|-------|-----------------|-------|------|
| **Dedicated LLM** | UCCIX (13B, 70B) | GPT-2 WECHSEL | Mistral 7B | None |
| **BERT-style** | gaBERT, gaELECTRA | XLM-R only | None | None |
| **Fine-tuned ASR** | 7+ models | In development | 7+ models | None |
| **TTS** | MMS | None | MMS | Unconfirmed |
| **Dedicated Translation** | OPUS-MT | OPUS-MT synthetic | Mistral translate | OPUS-MT |

---

## 2. Best-in-Class Models by Task

### 2.1 Language Models (LLMs)

| Language | Best Model | Parameters | URL |
|----------|------------|------------|-----|
| **Irish** | UCCIX-Llama2-13B-Instruct | 13B | https://huggingface.co/ReliableAI/UCCIX-Llama2-13B-Instruct |
| **Irish (Large)** | UCCIX-Llama3.1-70B-Instruct | 70B | https://huggingface.co/ReliableAI/UCCIX-Llama3.1-70B-Instruct-19122024 |
| **Welsh** | Mistral-7B-Cymraeg-Welsh-v2 | 7B | https://huggingface.co/BangorAI/Mistral-7B-Cymraeg-Welsh-v2 |
| **Scottish Gaelic** | gpt2-wechsel-scottish-gaelic | 124M | https://huggingface.co/benjamin/gpt2-wechsel-scottish-gaelic |
| **Manx** | None available | - | Use multilingual models |

### 2.2 Encoder Models

| Language | Best Model | Training Data | URL |
|----------|------------|---------------|-----|
| **Irish** | gaBERT | 7.9M sentences | https://huggingface.co/DCU-NLP/bert-base-irish-cased-v1 |
| **Irish (Alternative)** | gaELECTRA | 7.9M sentences | https://huggingface.co/DCU-NLP/electra-base-irish-cased-generator-v1 |
| **Others** | XLM-RoBERTa | Multilingual | https://huggingface.co/FacebookAI/xlm-roberta-base |

### 2.3 Speech Recognition (ASR)

| Language | Best Model | WER | URL |
|----------|------------|-----|-----|
| **Welsh** | wav2vec2-xlsr-ft-cy | 4.05% (with KenLM) | https://huggingface.co/techiaith/wav2vec2-xlsr-ft-cy |
| **Irish** | wav2vec2-large-xlsr-53-irish | Not reported | https://huggingface.co/cpierse/wav2vec2-large-xlsr-53-irish |
| **Scottish Gaelic** | None public | 12.8% (research) | Expected Q4 2025 |
| **Manx** | None | - | - |

### 2.4 Text-to-Speech (TTS)

| Language | Best Model | Architecture | URL |
|----------|------------|--------------|-----|
| **Irish** | mms-tts-gle | VITS | https://huggingface.co/facebook/mms-tts-gle |
| **Welsh** | mms-tts-cym | VITS | https://huggingface.co/facebook/mms-tts-cym |
| **Scottish Gaelic** | None | - | Check MMS coverage |
| **Manx** | Unconfirmed | - | Check MMS coverage |

### 2.5 Translation

| Direction | Best Model | Performance | URL |
|-----------|------------|-------------|-----|
| **English → Irish** | opus-mt-en-ga | CC-BY 4.0 | https://huggingface.co/Helsinki-NLP/opus-mt-en-ga |
| **Irish → English** | opus-mt-ga-en | CC-BY 4.0 | https://huggingface.co/Helsinki-NLP/opus-mt-ga-en |
| **English → Welsh** | mistral-7b-english-welsh-translate | Gov docs | https://huggingface.co/AndreasThinks/mistral-7b-english-welsh-translate |
| **English → Scottish Gaelic** | opus-mt-synthetic-en-gd | ChrF: 51.10 | https://huggingface.co/Helsinki-NLP/opus-mt-synthetic-en-gd |
| **English → Manx** | opus-mt-en-gv | BLEU: 70.1 | https://huggingface.co/Helsinki-NLP/opus-mt-en-gv |
| **Manx → English** | opus-mt-gv-en | BLEU: 38.9 | https://huggingface.co/Helsinki-NLP/opus-mt-gv-en |
| **All Celtic** | m2m100_418M | 100 languages | https://huggingface.co/facebook/m2m100_418M |

---

## 3. Data Availability

### 3.1 Text Corpora Size

| Language | CC-100 Tokens | Other Sources |
|----------|---------------|---------------|
| **Welsh** | 179M | MADLAD-400, OSCAR |
| **Irish** | 108M | CulturaX, OSCAR |
| **Scottish Gaelic** | 22M | GlotCC, mC4 |
| **Manx** | Unknown | OPUS Tatoeba (limited) |

### 3.2 Dataset Count on HuggingFace

| Language | Datasets | Notable |
|----------|----------|---------|
| **Scottish Gaelic** | 38+ | Highest count |
| **Irish** | 10+ | Parallel corpora |
| **Welsh** | 8+ | Speech focus |
| **Manx** | 2-3 | Translation only |

---

## 4. Multilingual Model Coverage

### 4.1 Models Supporting All Celtic Languages

| Model | Languages | Celtic Support | URL |
|-------|-----------|----------------|-----|
| **M2M100-418M** | 100 | ga, gd, cy, gv | https://huggingface.co/facebook/m2m100_418M |
| **SMALL-100** | 101 | ga, gd, cy, gv | https://huggingface.co/alirezamsh/small100 |
| **NLLB-200** | 200 | ga, gd, cy | https://huggingface.co/facebook/nllb-200-3.3B |
| **XLM-RoBERTa** | 100 | ga, gd, cy | https://huggingface.co/FacebookAI/xlm-roberta-base |
| **MMS-ASR** | 1162 | ga (confirmed) | https://huggingface.co/facebook/mms-1b-all |

### 4.2 Celtic-Specific Multilingual

| Model | Languages | Direction | URL |
|-------|-----------|-----------|-----|
| **opus-mt-en-cel** | 6 Celtic | en → Celtic | https://huggingface.co/Helsinki-NLP/opus-mt-en-cel |
| **opus-mt-cel-en** | 6 Celtic | Celtic → en | https://huggingface.co/Helsinki-NLP/opus-mt-cel-en |

---

## 5. Key Organizations

| Organization | Languages | Focus Areas |
|--------------|-----------|-------------|
| **DCU-NLP** | Irish | gaBERT, gaELECTRA, NLP research |
| **ReliableAI/ReML-AI** | Irish | UCCIX LLMs, benchmarks |
| **techiaith** | Welsh | ASR, TTS, complete NLP pipeline |
| **BangorAI** | Welsh | LLMs, translation |
| **EdinburghNLP** | Scottish Gaelic | ASR, translation research |
| **Helsinki-NLP** | All Celtic | OPUS-MT translation models |
| **Facebook/Meta AI** | All | MMS, M2M100, XLM-R |
| **Mozilla Foundation** | All | Common Voice datasets |

---

## 6. Research Gaps

### 6.1 Universal Gaps (All Languages)

| Gap | Status | Impact |
|-----|--------|--------|
| **NER** | Limited across all | High |
| **Sentiment Analysis** | No dedicated models | High |
| **Evaluation Benchmarks** | No Celtic GLUE | Medium |
| **Question Answering** | Irish only (IrishQA) | Medium |

### 6.2 Language-Specific Gaps

| Language | Critical Gaps |
|----------|---------------|
| **Irish** | Whisper fine-tuned, sentiment |
| **Scottish Gaelic** | Public ASR/TTS (in development) |
| **Welsh** | Dedicated NER, sentiment |
| **Manx** | Everything except translation |

---

## 7. Performance Benchmarks

### 7.1 ASR Performance (WER)

| Language | Model | WER | Notes |
|----------|-------|-----|-------|
| **Welsh** | wav2vec2-xlsr-ft-cy | 4.05% | With KenLM |
| **Welsh** | wav2vec2-xlsr-ft-cy | 6.04% | Without LM |
| **Welsh** | whisper-large-v3-ft-verbatim | 28.99% | Spontaneous |
| **Scottish Gaelic** | Research model | 12.8% | Unpublished |
| **Irish** | wav2vec2-large-xlsr-53-irish | - | Not reported |

### 7.2 Translation Performance

| Direction | Model | BLEU | ChrF |
|-----------|-------|------|------|
| **en → gv (Manx)** | opus-mt-en-gv | 70.1 | 0.885 |
| **gv → en (Manx)** | opus-mt-gv-en | 38.9 | 0.668 |
| **en → gd (Scottish)** | opus-mt-synthetic-en-gd | - | 51.10 |

---

## 8. Technology Selection Guide

### 8.1 By Use Case

| Use Case | Irish | Welsh | Scottish Gaelic | Manx |
|----------|-------|-------|-----------------|------|
| **Chatbot/Assistant** | UCCIX | Mistral-7B-Cymraeg | GPT-2 WECHSEL | M2M100 |
| **Document Analysis** | gaBERT | XLM-R | XLM-R | XLM-R |
| **Speech-to-Text** | wav2vec2-xlsr-irish | wav2vec2-xlsr-ft-cy | Fine-tune Whisper | None |
| **Text-to-Speech** | MMS-TTS | MMS-TTS | Check MMS | Check MMS |
| **Translation** | OPUS-MT | Mistral translate | OPUS-MT synthetic | OPUS-MT |

### 8.2 By Resource Constraints

| Constraint | Recommendation |
|------------|----------------|
| **Low compute** | SMALL-100 (translation), GPT-2 (generation) |
| **Medium compute** | wav2vec2 (ASR), M2M100-418M (translation) |
| **High compute** | UCCIX-70B (Irish), Whisper Large (ASR) |
| **Offline/Edge** | whisper-base-cpp (Welsh), GGUF models |

---

## 9. Quick Reference Links

### 9.1 Demos

| Language | Demo | URL |
|----------|------|-----|
| **Irish** | Aine Chat | https://aine.chat |
| **Welsh** | BangorAI Demo | https://demo.bangor.ai |

### 9.2 Collections

| Organization | Collection | URL |
|--------------|------------|-----|
| **techiaith** | ASR Models | https://huggingface.co/collections/techiaith/speech-recognition-models-660552d87de27e9581013dcf |
| **techiaith** | ASR Datasets | https://huggingface.co/collections/techiaith/speech-recognition-datasets-672df8ffb3f7da8ed8294ce2 |

### 9.3 Browse by Language

| Language | Models | Datasets |
|----------|--------|----------|
| **Irish** | https://huggingface.co/models?language=ga | https://huggingface.co/datasets?language=language:gle |
| **Scottish Gaelic** | https://huggingface.co/models?language=gd | https://huggingface.co/datasets?language=language:gla |
| **Welsh** | https://huggingface.co/models?language=cy | https://huggingface.co/datasets?language=language:cym |
| **Manx** | - | https://huggingface.co/datasets?language=language:glv |

---

## 10. ISO Language Codes Reference

| Language | ISO 639-1 | ISO 639-2/3 | Locale | Script |
|----------|-----------|-------------|--------|--------|
| Irish | ga | gle | ga-IE | Latn |
| Scottish Gaelic | gd | gla | gd-GB | Latn |
| Welsh | cy | cym | cy-GB | Latn |
| Manx | gv | glv | gv-IM | Latn |

---

## Cross-References

This document consolidates and cross-references:
- `irish-nlp-resources.md` - Detailed Irish resources
- `scottish-gaelic-resources.md` - Detailed Scottish Gaelic resources
- `welsh-resources.md` - Detailed Welsh resources
- Main research Category 02 (Multimodal Document Intelligence) - Celtic OCR/VLM
- Main research Category 03 (AI-Native Data Pipelines) - Integration patterns


---

### `welsh-resources.md` — 01-celtic-language-ai-resources

# Welsh (Cymraeg) AI Resources

## Overview

**ISO Codes:** cy (639-1), cym (639-2/3), Locale: cy-GB
**Speakers:** ~884,300 (2021 census)
**Maturity Level:** High - Strong ASR ecosystem, active LLM development

---

## 1. Language Models

### 1.1 Mistral-7B-Cymraeg-Welsh-v2

The primary Welsh LLM, bilingual Welsh-English.

| Property | Value |
|----------|-------|
| **Model** | `BangorAI/Mistral-7B-Cymraeg-Welsh-v2` |
| **Parameters** | 7B |
| **Base** | Mistral-7B-v0.1 |
| **Training** | MADLAD-400 dataset, 2 epochs |
| **Fine-tuning** | yahma/alpaca-cleaned (Welsh + English) |

**HuggingFace:** https://huggingface.co/BangorAI/Mistral-7B-Cymraeg-Welsh-v2

**Demo:** https://demo.bangor.ai

**Usage:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("BangorAI/Mistral-7B-Cymraeg-Welsh-v2")
tokenizer = AutoTokenizer.from_pretrained("BangorAI/Mistral-7B-Cymraeg-Welsh-v2")

# Welsh system prompt for Welsh responses
system_prompt = "Rydych chi'n gynorthwyydd AI sy'n siarad Cymraeg."
```

### 1.2 Base Model

| Model | Purpose | URL |
|-------|---------|-----|
| **mistral-7b-cy-epoch-2** | Pre-training base | https://huggingface.co/BangorAI/mistral-7b-cy-epoch-2 |

---

## 2. Speech Recognition (ASR)

Welsh has the most comprehensive ASR ecosystem among Celtic languages, primarily from techiaith (Bangor University).

### 2.1 wav2vec2 Models

#### Primary Model: wav2vec2-xlsr-ft-cy

| Property | Value |
|----------|-------|
| **Model** | `techiaith/wav2vec2-xlsr-ft-cy` |
| **WER** | 6.04% (4.05% with KenLM) |
| **Base** | Facebook XLSR-53 |
| **Training** | Common Voice + OSCAR |

**HuggingFace:** https://huggingface.co/techiaith/wav2vec2-xlsr-ft-cy

**Usage:**
```python
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch

processor = Wav2Vec2Processor.from_pretrained("techiaith/wav2vec2-xlsr-ft-cy")
model = Wav2Vec2ForCTC.from_pretrained("techiaith/wav2vec2-xlsr-ft-cy")

# Process audio
inputs = processor(audio_array, sampling_rate=16000, return_tensors="pt")
with torch.no_grad():
    logits = model(**inputs).logits
predicted_ids = torch.argmax(logits, dim=-1)
transcription = processor.decode(predicted_ids[0])
```

#### Other wav2vec2 Models

| Model | Training | URL |
|-------|----------|-----|
| **wav2vec2-base-cy** | 4000 hours (25% Welsh) | https://huggingface.co/techiaith/wav2vec2-base-cy |
| **wav2vec2-xlsr-53-ft-cy-en** | Bilingual Welsh-English | https://huggingface.co/techiaith/wav2vec2-xlsr-53-ft-cy-en |

### 2.2 Whisper Models

| Model | Use Case | WER | URL |
|-------|----------|-----|-----|
| **whisper-large-v3-ft-verbatim-cy-en** | Spontaneous speech | 28.99% | https://huggingface.co/techiaith/whisper-large-v3-ft-verbatim-cy-en |
| **whisper-large-v3-ft-commonvoice-cy-en** | Read speech | - | https://huggingface.co/techiaith/whisper-large-v3-ft-commonvoice-cy-en |
| **whisper-base-ft-verbatim-cy-en-cpp** | Offline/mobile | - | https://huggingface.co/techiaith/whisper-base-ft-verbatim-cy-en-cpp |
| **whisper-large-v3-ft-verbatim-cy-en-ct2** | CTranslate2 optimized | - | https://huggingface.co/techiaith/whisper-large-v3-ft-verbatim-cy-en-ct2 |

### 2.3 Model Selection Guide

| Use Case | Recommended Model |
|----------|------------------|
| **Read/planned speech** | wav2vec2-xlsr-ft-cy |
| **Spontaneous speech** | whisper-large-v3-ft-verbatim-cy-en |
| **Offline/mobile** | whisper-base-ft-verbatim-cy-en-cpp |
| **Fast inference** | whisper-large-v3-ft-verbatim-cy-en-ct2 |
| **Bilingual audio** | wav2vec2-xlsr-53-ft-cy-en |

---

## 3. Text-to-Speech (TTS)

### 3.1 Facebook MMS-TTS Welsh

| Property | Value |
|----------|-------|
| **Model** | `facebook/mms-tts-cym` |
| **Architecture** | VITS |
| **Languages** | Part of 1107+ language coverage |

**HuggingFace:** https://huggingface.co/facebook/mms-tts-cym

**Usage:**
```python
from transformers import VitsModel, AutoTokenizer
import torch

model = VitsModel.from_pretrained("facebook/mms-tts-cym")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-cym")

text = "Bore da, sut ydych chi heddiw?"
inputs = tokenizer(text, return_tensors="pt")

with torch.no_grad():
    output = model(**inputs).waveform

# output contains the synthesized audio waveform
```

---

## 4. Translation Models

### 4.1 Dedicated Welsh Translation

| Property | Value |
|----------|-------|
| **Model** | `AndreasThinks/mistral-7b-english-welsh-translate` |
| **Type** | Bidirectional English-Welsh |
| **Specialization** | Government documents |
| **Format** | Also available in GGUF |

**HuggingFace:** https://huggingface.co/AndreasThinks/mistral-7b-english-welsh-translate

**Usage:**
```python
# Use Alpaca instruction format
instruction = "Translate the text from English to Welsh."
input_text = "The meeting will take place tomorrow."
```

### 4.2 Multilingual Translation

| Model | Welsh Support | URL |
|-------|---------------|-----|
| **M2M100-418M** | Language code: `cy` | https://huggingface.co/facebook/m2m100_418M |
| **Helsinki-NLP OPUS-MT** | en-cy, cy-en pairs | https://huggingface.co/Helsinki-NLP |

---

## 5. Other NLP Models

### 5.1 Punctuation Prediction

| Property | Value |
|----------|-------|
| **Model** | `techiaith/fullstop-welsh-punctuation-prediction` |
| **Purpose** | Restore punctuation in ASR output |

**HuggingFace:** https://huggingface.co/techiaith/fullstop-welsh-punctuation-prediction

---

## 6. Datasets

### 6.1 Text Corpora

| Dataset | Size | Source | URL |
|---------|------|--------|-----|
| **CC-100** | 179M tokens | CommonCrawl | https://huggingface.co/datasets/statmt/cc100 |
| **OSCAR** | Multi-version | CommonCrawl | https://huggingface.co/datasets/oscar-corpus/OSCAR-2301 |
| **MADLAD-400** | 419 languages | CommonCrawl | https://huggingface.co/datasets/allenai/MADLAD-400 |
| **Welsh Texts** | Historical | National Library of Wales | https://huggingface.co/datasets/openai/welsh-texts |

**Loading CC-100 Welsh:**
```python
from datasets import load_dataset
welsh_data = load_dataset("statmt/cc100", "cy")
```

### 6.2 Speech Datasets

| Dataset | Content | URL |
|---------|---------|-----|
| **Common Voice (techiaith)** | 50/50 Welsh-English | https://huggingface.co/datasets/techiaith/commonvoice_16_1_en_cy |
| **CommonVoice 18** | Welsh + English | https://huggingface.co/datasets/techiaith/commonvoice_18_0_cy_en |
| **Banc Trawsgrifiadau Bangor** | 48+ hours spontaneous speech | techiaith collection |
| **Lleisiau Arfor** | Spontaneous speech | techiaith collection |

### 6.3 Collections

| Collection | Content | URL |
|------------|---------|-----|
| **Speech Recognition Datasets** | Training + evaluation | https://huggingface.co/collections/techiaith/speech-recognition-datasets-672df8ffb3f7da8ed8294ce2 |
| **Speech Recognition Models** | All ASR models | https://huggingface.co/collections/techiaith/speech-recognition-models-660552d87de27e9581013dcf |

---

## 7. Key Organizations

### 7.1 techiaith (Bangor University)

**URL:** https://huggingface.co/techiaith

Primary Welsh AI resource developer - self-funded research unit.

**Focus Areas:**
- Speech Recognition
- Machine Translation
- Speech-to-Text
- Punctuation Prediction

**Portal:** https://techiaith.cymru/?lang=en

### 7.2 BangorAI

**URL:** https://huggingface.co/BangorAI

**Focus:** Welsh LLMs and bilingual models

**Models:** 21 models on HuggingFace

**Demo:** https://demo.bangor.ai

---

## 8. External Resources

### 8.1 GitHub Repositories

| Repository | Purpose | URL |
|------------|---------|-----|
| **docker-huggingface-stt-cy** | Welsh ASR Docker | https://github.com/techiaith/docker-huggingface-stt-cy |
| **spacy-wales-en-ner-model** | Wales-specific NER | https://github.com/techiaith/spacy-wales-en-ner-model |
| **lecsicon-cymraeg-bangor** | Welsh lexicon | https://github.com/techiaith/lecsicon-cymraeg-bangor |

### 8.2 Welsh Government Resources

| Resource | Purpose |
|----------|---------|
| **Cymraeg 2050** | Language strategy |
| **SENTimental** | Sentiment data collection tool |

---

## 9. Research Gaps & Opportunities

| Gap | Status | Priority |
|-----|--------|----------|
| **Named Entity Recognition** | External tools only | High |
| **Sentiment Analysis** | No dedicated model | High |
| **Word Embeddings** | Research exists, not on HF | Medium |
| **Evaluation Benchmarks** | No Welsh GLUE equivalent | Medium |

### 9.1 NER Alternatives

Welsh NER tools exist outside HuggingFace:
- Welsh Natural Language Toolkit (WNLT/WNLT2)
- Bangor University's NER tools (spaCy-based)
- National Library of Wales' 'Cymrie' tool

---

## 10. Integration Examples

### 10.1 Complete ASR Pipeline

```python
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
import librosa

# Load model
processor = Wav2Vec2Processor.from_pretrained("techiaith/wav2vec2-xlsr-ft-cy")
model = Wav2Vec2ForCTC.from_pretrained("techiaith/wav2vec2-xlsr-ft-cy")

# Load and process audio
audio, sr = librosa.load("welsh_audio.wav", sr=16000)
inputs = processor(audio, sampling_rate=16000, return_tensors="pt")

# Transcribe
with torch.no_grad():
    logits = model(**inputs).logits
predicted_ids = torch.argmax(logits, dim=-1)
transcription = processor.decode(predicted_ids[0])

print(f"Transcription: {transcription}")
```

### 10.2 TTS Generation

```python
from transformers import VitsModel, AutoTokenizer
import soundfile as sf

model = VitsModel.from_pretrained("facebook/mms-tts-cym")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-cym")

text = "Croeso i Gymru. Mae'n dda gen i gwrdd a chi."
inputs = tokenizer(text, return_tensors="pt")

with torch.no_grad():
    output = model(**inputs).waveform

# Save audio
sf.write("output.wav", output.squeeze().numpy(), 16000)
```

### 10.3 With dlt Pipeline

```python
import dlt
from transformers import pipeline

# Welsh speech-to-text pipeline
asr = pipeline("automatic-speech-recognition", model="techiaith/wav2vec2-xlsr-ft-cy")

@dlt.resource
def transcribe_welsh_audio(audio_paths: list[str]):
    for path in audio_paths:
        result = asr(path)
        yield {
            "audio_path": path,
            "transcription": result["text"]
        }
```

---

## References

- techiaith Portal: https://techiaith.cymru/?lang=en
- BangorAI Demo: https://demo.bangor.ai
- Welsh Word Embeddings Research: https://mdpi.com/2076-3417/11/15/6896/htm
- MMS Language Coverage: https://dl.fbaipublicfiles.com/mms/misc/language_coverage_mms.html


---

### `README.md` — 01-irish-edtech-platform

# Irish EdTech Platform Architecture

This directory consolidates research on building a comprehensive bilingual (Irish/English) educational technology platform for the Irish Leaving Certificate curriculum.

## Overview

The Irish education system presents a complex data landscape with three distinct governance structures:
- **NCCA** (National Council for Curriculum and Assessment): Defines pedagogical intent via curriculumonline.ie
- **SEC** (State Examinations Commission): Provides evidentiary truth via examinations.ie
- **Department of Education**: Manages temporal governance via circulars

## Documents in this Category

### Core Architecture Documents

| Document | Focus | Key Technologies |
|----------|-------|------------------|
| `data-architecture.md` | Knowledge graphs, ontologies, BAML schemas | FalkorDB, Cognee, Graphiti, CocoIndex |
| `frontend-stack.md` | Edge-native UI, WebAssembly, visualizations | TanStack Start, Marimo, Cloudflare, Deck.gl |
| `ai-ml-pipeline.md` | Document processing, model fine-tuning, RAG | Qwen2.5-VL, ColPali, Unsloth, BAML |
| `subject-implementations.md` | Per-subject technical blueprints | BAML schemas, assessment logic |

## Key Architectural Decisions

### 1. Schema-First Design
- BAML for type-safe LLM extraction
- Polymorphic schemas handling diverse content (prose, poetry, marking schemes)
- Unified concept nodes with dual-language properties

### 2. Temporal Knowledge Graphs
- Graphiti for bi-temporal data (valid time + transaction time)
- Policy supersession tracking for circulars
- Syllabus version management

### 3. Edge-Native Computing
- Browser-based computation via WebAssembly (Marimo, DuckDB)
- Cloudflare Workers for global distribution
- Durable Objects for session state

### 4. Bilingual Architecture
- Irish as first-class citizen in all schemas
- Dialectal variation support (Connacht, Munster, Ulster)
- UCCIX models for Irish language support

## Source Files Consolidated

This category merges content from:
- `BAML Schemas for Irish Education.md`
- `Building Bilingual EdTech Platform.md`
- `Backend Strategy For Educational Tutoring System.md`
- `Leaving Certificate Material App.md`
- `Leaving Certificate Subject Analysis Plan.md`
- `irish-english-education.md`
- `Educational Website Tech Stack.md`

## Quick Reference

### Curriculum Structure
```
Subject (e.g., Mathematics)
├── Cycle (Junior/Senior)
│   ├── Strand (e.g., Algebra)
│   │   ├── Topic (e.g., Equations)
│   │   │   └── Learning Outcome
│   │   └── Assessment Items
│   │       ├── Exam Questions
│   │       └── Marking Schemes (Scales 10A-D)
```

### Technology Stack Summary
```
Document Ingestion: ColPali → Qwen2.5-VL → Granite-Docling → BAML
Knowledge Base: FalkorDB + Qdrant (hybrid vector/graph)
RAG Retrieval: BGE-M3 embeddings + ColPali visual retrieval
Generation: Qwen2.5-Math-7B (fine-tuned via Unsloth)
Frontend: TanStack Start + Marimo WASM + Cloudflare Edge
```

### Assessment Logic by Subject Group
| Subject Group | Assessment Model | Key Edge Types |
|--------------|------------------|----------------|
| Mathematics | Step-based (Scale 10C) | :PREREQUISITE, :ASSESSES |
| Sciences | Diagram + Taxonomy | :FLOWS_TO, :INTERACTS |
| Humanities | SRP Count + Argument | :CAUSED, :LOCATED_AT |
| Languages | PCLM Rubric | :EXPLORES, :TRANSLATES |
| Business | Exact Layout/Values | :DEBITS, :STRUCTURED_AS |


---

### `ai-ml-pipeline.md` — 01-irish-edtech-platform

# AI/ML Pipeline for Irish Education Platform

## Executive Summary

This document details the machine learning architecture for processing 8,000+ pages of bilingual curriculum documents, including document understanding, model fine-tuning, and retrieval-augmented generation (RAG) for an Irish Leaving Certificate tutoring system.

---

## 1. Document Processing Pipeline

### 1.1 Tool Comparison

| Tool | LaTeX Extraction | Diagrams | Tables | Irish Support | Model Size |
|------|-----------------|----------|--------|---------------|------------|
| DeepSeek-OCR | Excellent (95%) | Good | Very Good | Unconfirmed | 3B |
| Qwen2.5-VL | Very Good | Excellent | Excellent | Likely (European) | 2B-235B |
| Qwen3-VL | Very Good | Excellent | Excellent | Native (119 langs) | Various |
| Granite-Docling | Good | Good | Excellent | Experimental | 258M |
| ColPali | N/A (retrieval) | Excellent | Good (visual) | Visual-based | 3B |

### 1.2 Recommended Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                 DOCUMENT INGESTION (CocoIndex)                  │
│  PDF Sources → Language Detection → Content Routing             │
│  ├── Text/Equations → DeepSeek-OCR → LaTeX extraction          │
│  ├── Diagrams → ColPali → Visual embeddings                     │
│  └── Tables → Granite-Docling → Structured extraction          │
│  ↓                                                              │
│  BAML Structured Extraction → Metadata + JSON                   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 DeepSeek-OCR Capabilities

- **95% formula recognition accuracy**
- Vision-as-compression: 600-1000+ text tokens from 64-100 vision tokens
- Processing speed: ~2,500 tokens/second on A100 (~200,000 pages/day)
- MIT licensed (3B parameters)

### 1.4 ColPali: Visual Document Retrieval

Revolutionary approach bypassing OCR entirely:
- Multi-vector embeddings directly from page images
- PaliGemma-3B + ColBERT late-interaction
- **0.81 nDCG@5** vs 0.66 for traditional pipelines
- Ideal for geometry diagrams in exam papers

---

## 2. Fine-Tuning Strategy

### 2.1 Base Model Selection

**Qwen2.5-Math-7B-Instruct** (recommended):
- 85.3% on MATH benchmark with Tool-Integrated Reasoning
- Solves 21/30 AIME problems with reward model sampling
- Native multilingual support including Irish

**Alternatives**:
- DeepSeek-R1-Distill-Qwen-7B: Excellent reasoning via knowledge distillation
- DeepSeek-Math-V2: IMO gold-level (but too large for fine-tuning)

### 2.2 Unsloth Training Framework

**Advantages**:
- 2x faster training, 70% less VRAM
- 7-8B model with QLoRA 4-bit: **~6-7GB VRAM**
- Achievable on consumer RTX 3060+

**Critical Hyperparameters**:
| Parameter | Math Reasoning Value | Standard Value |
|-----------|---------------------|----------------|
| LoRA rank | 64-128 | 16-32 |
| Learning rate | 1e-5 to 5e-5 | 1e-4 to 5e-4 |
| Sequence length | 4096+ tokens | 2048 |

### 2.3 Training Data Format

```json
{
  "conversations": [
    {
      "role": "user",
      "content": "Leaving Certificate Higher Level, Paper 1:\nDifferentiate f(x) = (3x²+2)/(x-1) and find stationary points. (25 marks)"
    },
    {
      "role": "assistant",
      "content": "<think>Apply quotient rule, find where f'(x)=0...</think>\n\n**Step 1: Apply Quotient Rule** (5 marks)\n$$f'(x) = \\frac{6x(x-1) - (3x^2+2)(1)}{(x-1)^2}$$\n...\nFinal Answer: \\boxed{\\left(1 \\pm \\frac{\\sqrt{15}}{3}, y\\right)}"
    }
  ]
}
```

**Dataset Mixing**:
- 60-70% Leaving Certificate problems
- 20-30% general mathematics (GSM8K, MATH benchmark)
- Prevents catastrophic forgetting

---

## 3. Irish Language Integration

### 3.1 The Challenge

- Irish: <0.1% of web content (low-resource language)
- ~20% performance gap between English and Irish on identical questions
- Language fidelity: models produce valid Irish <80% of the time

### 3.2 UCCIX Models (University College Cork)

**UCCIX-Llama2-13B-Instruct**:
- Trained on ~520M Irish tokens
- Vocabulary expansion for native Irish tokens
- Outperforms LLaMA 2-70B on Irish tasks by +12%

**UCCIX-Llama3.1-70B-Instruct** (December 2024):
- Latest architecture with improved Irish capabilities
- Useful as teacher model for distillation

### 3.3 GaBERT (DCU-NLP)

- Irish-specific BERT embeddings
- Trained on 7.9M Irish sentences
- +3.7 LAS improvement on dependency parsing
- Useful for preprocessing and classification

### 3.4 Recommended Multilingual Approach

1. Use **Qwen2.5-Math-7B** as base (native Irish support)
2. Merge UCCIX tokenizer additions if needed
3. Include bilingual training examples with Irish terminology
4. Validate outputs against Irish-BLiMP benchmark (1,020 minimal pairs)
5. UCCIX fallback for Irish-only responses

---

## 4. RAG Architecture

### 4.1 Embedding Models

**BGE-M3** (BAAI) - Primary:
- Three retrieval modes: dense, sparse, multi-vector
- 100+ languages, 8,192 token context
- Outperforms BM25 with learned sparse representations

**LaBSE** - Irish Supplement:
- 109 languages including Irish
- Superior performance on Irish classification tasks

### 4.2 Hybrid Retrieval Strategy

```
Query → Language Detection
    ↓
┌──────────────────────────────────────┐
│ BGE-M3 Dense + Sparse Embeddings     │
│ ColPali Visual Page Embeddings       │
│ Payload Filtering (year, topic, lang)│
└──────────────────────────────────────┘
    ↓
Reranking → Top-K Results
    ↓
Context Assembly for LLM
```

### 4.3 ColPali Integration

**ColQwen2.5-v0.2** (based on Qwen2.5-VL-3B):
- 29+ languages
- Eliminates OCR errors for equation-heavy pages
- Trade-off: 10-100x more vectors per document (1,024 patches/page)
- Use token pooling for storage efficiency

### 4.4 Vector Database: Qdrant

**Why Qdrant**:
- Advanced payload filtering for metadata
- Native multi-vector support for ColPali
- Hybrid sparse + dense search
- Highest RPS and lowest latency in benchmarks

### 4.5 Chunking Strategy for Math

Standard semantic chunking fails around equations. Use **semantic double-pass merging**:

1. First pass: Standard semantic chunking
2. Second pass: If chunks 1 and 3 similar but chunk 2 (equation) differs, merge all three

**Configuration**:
- Chunk size: 1000-2000 tokens
- Overlap: 200-500 tokens
- Separators: `["\n\n", "\n", ".", "$$", "\\["]`
- Never split inside LaTeX environments

---

## 5. BAML Schema Enforcement

### 5.1 Exam Paper Extraction Schema

```baml
class MathQuestion {
  number: string
  text: string @description("Full question in original language")
  text_irish: string?
  marks: int
  topic: "Algebra" | "Geometry" | "Calculus" | "Statistics"
  marking_criteria: MarkingCriterion[]
  requires_diagram: bool
}

function ExtractExamPaper(document: pdf) -> ParsedExam {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Extract all questions from this Leaving Certificate exam paper.
    Identify marks, topics, and any diagrams required.
    {{ document }}
    {{ ctx.output_format }}
  "#
}
```

### 5.2 Benefits of BAML

- Type-safe clients for Python and TypeScript
- Compile-time verification of extraction schemas
- VSCode playground for parallel prompt testing
- Native multimodal support (PDFs, images, audio)

---

## 6. Deployment Architecture

### 6.1 Modal Serverless (Recommended)

| GPU | Price/Hour | VRAM | Best For |
|-----|-----------|------|----------|
| NVIDIA T4 | $0.59 | 16GB | Development/testing |
| NVIDIA L4 | $0.80 | 24GB | 7B models quantized |
| NVIDIA A10 | $1.10 | 24GB | 7B-13B production |
| NVIDIA A100 40GB | $2.10 | 40GB | 13B-70B models |

**Advantages**:
- <1 second cold starts (Rust-based container stack)
- Per-second billing with scale-to-zero
- Direct Unsloth export to GGUF/vLLM

### 6.2 Consumer Hardware Option

**RTX 4090** (~$1,800):
- 7B models at ~50 tokens/second (Q4_K_M)
- 13B models at 30-40 t/s

**RTX 3090** (~$1,500 used):
- Similar performance at lower cost

### 6.3 Inference Optimization

**vLLM with PagedAttention**:
- 2-4x faster throughput
- Built-in KV caching

**Response Caching**:
- Semantic cache for common math problems
- 50-90% GPU cost reduction

**Latency Targets**:
- Time-to-First-Token: <2 seconds
- Token generation: 20-50 tokens/second minimum
- Always use streaming responses

---

## 7. Evaluation Framework

### 7.1 IRLBench (Irish Language)

- Reveals ~20% performance gap English vs Irish
- Best models: 55.8% Irish vs 76.2% English
- Use for Irish output validation

### 7.2 Irish-BLiMP Benchmark

- 1,020 minimal pairs for grammaticality
- Essential for validating Irish language generation

### 7.3 MLflow + Ragas Integration

```python
import mlflow
from ragas import evaluate

# Track experiments
with mlflow.start_run():
    mlflow.log_params({"model": "qwen2.5-math-7b", "lora_r": 64})

    # LLM-as-judge evaluation
    result = evaluate(
        dataset=leaving_cert_test_set,
        metrics=[faithfulness, answer_relevancy, context_precision]
    )
    mlflow.log_metrics(result)
```

---

## 8. Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                 DOCUMENT INGESTION (CocoIndex)                  │
│  PDF Sources → Language Detection → Content Routing             │
│  ├── Text/Equations → DeepSeek-OCR → LaTeX extraction          │
│  ├── Diagrams → ColPali → Visual embeddings                     │
│  └── Tables → Granite-Docling → Structured extraction          │
│  ↓                                                              │
│  BAML Structured Extraction → Metadata + JSON                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 KNOWLEDGE BASE (Qdrant)                         │
│  ├── text_chunks: BGE-M3 embeddings (dense + sparse)           │
│  ├── visual_pages: ColPali multi-vector embeddings             │
│  └── Payload filtering: {language, level, topic, year}         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 RAG RETRIEVAL (LlamaIndex)                      │
│  Query → Language detection → Hybrid search → Reranking        │
│  Return: Relevant questions + marking schemes + diagrams        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 GENERATION (Fine-tuned Model)                   │
│  Qwen2.5-Math-7B fine-tuned via Unsloth on LC exam data        │
│  BAML functions for step-by-step solutions, bilingual output   │
│  Deployment: Modal (serverless) or vLLM (self-hosted)          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Rapid Prototyping Roadmap

### Days 1-3 (Foundation)
- Set up BAML project with exam paper schemas
- PDF extraction: PyMuPDF4LLM + BAML
- ChromaDB for initial vector storage
- Streamlit chat interface
- Single exam paper end-to-end demo

### Week 1 (Core RAG)
- LlamaIndex integration
- Topic-filtered retrieval
- Step-by-step solution generation
- Basic Irish via Qwen3

### Week 2 (Enhancement)
- ColPali for diagram handling
- Marking scheme integration
- Practice test generation
- Fine-tune Qwen2.5-Math-7B with Unsloth

### Weeks 3-4 (Production)
- Deploy to Modal with autoscaling
- Response caching
- Bilingual output verification
- IRLBench evaluation

---

## 10. Cost Analysis

### MVP Infrastructure (~$100-300/month on Modal)

| Component | Cost |
|-----------|------|
| Modal compute (with free credits) | $100-200 |
| Qdrant Cloud (small tier) | $25 |
| Storage (R2/S3) | $10-20 |
| API calls (BAML extraction) | $50-100 |

### Development Hardware (One-Time)

| Option | Cost |
|--------|------|
| RTX 4090 | ~$1,800 |
| RTX 3090 (used) | ~$1,500 |
| M2 Max MacBook | ~$3,000 |

Near-zero ongoing cost for development on consumer hardware.


---

### `data-architecture.md` — 01-irish-edtech-platform

# Data Architecture for Irish Education Platform

## Executive Summary

This document consolidates the data engineering strategy for building a semantic knowledge graph tailored to the Irish education system. The architecture utilizes **BAML** for structured extraction, **CocoIndex** for high-velocity ETL pipelines, **Cognee** for ontological enforcement, **Graphiti** for temporal reasoning, and **FalkorDB** for graph persistence.

---

## 1. The Tripartite Data Landscape

### 1.1 NCCA Domain: Pedagogical Intent
- **Source**: curriculumonline.ie, ncca.ie
- **Primary Unit**: Specification documents
- **Challenge**: Non-hierarchical structures (e.g., Junior Cycle Science has "Unifying Strands" operating transversely across "Contextual Strands")
- **BAML Requirement**: Extract semantic vectors from qualitative "Features of Quality" rubrics

### 1.2 SEC Domain: Evidentiary Truth
- **Source**: examinations.ie
- **Primary Unit**: Examination Papers, Marking Schemes, Chief Examiner Reports
- **Challenge**: Extreme granularity - marking schemes contain conditional logic ("deduct 1 mark for arithmetic slip")
- **BAML Requirement**: Parse conditional statements into executable validation rules

### 1.3 Department of Education Domain: Temporal Governance
- **Source**: gov.ie, circulars.gov.ie
- **Primary Unit**: Circular Letters
- **Challenge**: Temporal validity - policies supersede previous mandates
- **Graphiti Requirement**: Model SUPERSEDES relationships as temporal edges

---

## 2. Core Ontology Design

### 2.1 Entity Metamodel

```
EducationalNode (root)
├── CurriculumSpecification
├── PedagogicalUnit (Strand, Area of Practice)
├── LearningOutcome
├── AssessmentInstrument (Exam Question, CBA)
├── EvidenceLogic (Marking criteria)
└── PolicyDirective (Circular)
```

### 2.2 Key Relationship Types

| Edge Type | Semantics | Temporal |
|-----------|-----------|----------|
| `ASSESSES` | Question → LearningOutcome (weighted by similarity) | No |
| `DEFINES_QUALITY` | Rubric → PedagogicalUnit | No |
| `SUPERSEDES` | Circular → Circular | Yes (Graphiti) |
| `PREREQUISITE` | Topic → Topic | No |
| `EVIDENCES_DIFFICULTY` | ExaminerComment → LearningOutcome | Yes |

### 2.3 RDF/OWL Ontology (Cognee)

```turtle
@prefix maths: <http://www.mathstutor.ie/ontology/curriculum#>.

# Core Classes
maths:Cycle a owl:Class ; rdfs:subClassOf maths:EducationalEntity.
maths:Strand a owl:Class ; rdfs:subClassOf maths:EducationalEntity.
maths:Topic a owl:Class ; rdfs:subClassOf maths:EducationalEntity.
maths:LearningOutcome a owl:Class ; rdfs:subClassOf maths:EducationalEntity.

# Level Stratification (Higher includes Ordinary)
maths:validForLevel a owl:ObjectProperty ;
    rdfs:domain maths:LearningOutcome ;
    rdfs:range maths:Level.
maths:includesOutcome a owl:TransitiveProperty.
```

---

## 3. BAML Schema Specifications

### 3.1 Primary Curriculum (Integrated Structure)

```baml
enum PrimaryStage {
  Stage1_JuniorSeniorInfants
  Stage2_FirstSecondClass
  Stage3_ThirdFourthClass
  Stage4_FifthSixthClass
}

class CompetencyLink {
  competency_name: string @description("e.g., 'Being a Digital Learner'")
  context: string @description("How this outcome supports the competency")
}

class PrimaryLearningOutcome {
  id: string?
  text: string
  element: string @description("e.g., 'Communicating', 'Understanding'")
  progression_continuum: string?
  key_competencies: CompetencyLink[]
}
```

### 3.2 Junior Cycle Science (Transverse Links)

```baml
class ScienceOutcome {
  id: string @description("e.g., 'CW4', 'NoS1'")
  strand_type: "Contextual" | "Unifying"
  strand_name: string
  text: string
  action_verb: string @description("Bloom's taxonomy verb")
  keywords: string[]
}

class TransverseLink {
  source_outcome_id: string
  target_nos_id: string @description("Nature of Science outcome ID")
  strength: "High" | "Medium" | "Low"
}
```

### 3.3 Senior Cycle Marking Schemes (Logic Gates)

```baml
class PenaltyRule {
  type: string @description("'Arithmetic Slip', 'Chemical Error'")
  deduction: float
  scope: string @description("'per occurrence', 'max -3'")
}

class MarkingPoint {
  correct_answer: string
  marks_awarded: int
  valid_alternatives: string[]
  mandatory_keywords: string[]
  examiner_notes: string?
}

class QuestionPartSchema {
  part_id: string @description("e.g., '(b)(ii)'")
  total_marks: int
  marking_points: MarkingPoint[]
  penalties: PenaltyRule[]
}
```

### 3.4 Qualitative Rubrics (Arts & Humanities)

```baml
enum AchievementLevel {
  Exceptional
  AboveExpectations
  InLineWithExpectations
  YetToMeetExpectations
}

class RubricDescriptor {
  level: AchievementLevel
  text: string @description("Full descriptive paragraph")
  key_qualities: string[] @description("'comprehensive analysis'")
  negative_indicators: string[] @description("'limited understanding'")
}
```

### 3.5 Policy Circulars (Temporal Metadata)

```baml
enum CircularStatus {
  NewPolicy
  Amendment
  Repeal
  Clarification
}

class CircularMetadata {
  circular_id: string @description("e.g., '0003/2018'")
  title: string
  issue_date: string
  effective_date: string
  status: CircularStatus
  linked_circulars: LinkedCircular[]
  domains_affected: string[]
}
```

---

## 4. Temporal Dynamics with Graphiti

### 4.1 Bi-Temporal Data Model

Every edge tracks two time dimensions:
- **Valid Time** (`valid_at`, `invalid_at`): When the fact is true in the real world
- **Transaction Time** (`created_at`, `expired_at`): When the system recorded the fact

### 4.2 Syllabus Versioning Example

```cypher
// Topic valid from 1990-2015
(:Topic {name: "Matrices"}) -[:PART_OF {
  valid_at: "1990-01-01",
  invalid_at: "2015-01-01"
}]-> (:Curriculum {name: "Leaving Cert"})
```

**Query Logic**: Filter edges where `now()` falls within validity window. Use "Time Travel" for historical queries.

### 4.3 Student Mastery Tracking

```cypher
// Dynamic mastery with decay
(:Student) -[:HAS_MASTERY {
  valid_at: "2024-03-15",
  confidence: 0.85
}]-> (:Topic {name: "Complex Numbers"})
```

**Spaced Repetition**: Analyze `valid_at` timestamps to implement forgetting curve optimization.

---

## 5. Pipeline Orchestration (CocoIndex)

### 5.1 Flow Strategy by Source Type

| Flow | Source | Frequency | BAML Strategy | Graphiti Action |
|------|--------|-----------|---------------|-----------------|
| CurriculumFlow | curriculumonline.ie | Annual | ExtractPrimaryFramework | Upsert (Stable) |
| EvidenceFlow | examinations.ie | Annual bursts | ExtractMarkingScheme | Append Episodes |
| PolicyFlow | gov.ie | Weekly | ExtractCircularMeta | Temporal Patching |

### 5.2 Custom FalkorDB Connector

```python
@cocoindex.op.target_connector(spec_cls=FalkorDBTargetSpec)
class FalkorDBConnector:
    @staticmethod
    def mutate(batch):
        client = FalkorDB(host=spec.host, port=spec.port)
        graph = client.select_graph(spec.graph_name)

        for item in batch:
            query = """
            MERGE (q:Question {id: $id})
            SET q.text = $text, q.embedding = $embedding
            """
            graph.query(query, params=item.dict())
```

### 5.3 Incremental Processing

CocoIndex's `FlowLiveUpdater` monitors source directories:
- Computes file hashes to detect changes
- Triggers flow only for changed files
- Enables near real-time updates during exam season

---

## 6. FalkorDB Schema and Indexing

### 6.1 Node Labels
- `Topic`: Abstract mathematical/curricular concepts
- `Question`: Specific assessment items
- `MarkingScheme`: Grading logic
- `Student`: User entities

### 6.2 Index Strategy

```cypher
// Vector index for similarity search
CALL db.idx.vector.createNodeIndex('Question', 'embedding', 'FLOAT32', 6, 'L2')

// Full-text index for keyword search
CALL db.idx.fulltext.createNodeIndex('Question', 'text')

// Constraint for data integrity
GRAPH.CONSTRAINT CREATE MathsGraph ON (q:Question) ASSERT q.id IS UNIQUE
```

### 6.3 Hybrid GraphRAG Query

```cypher
// Step 1: Vector similarity
CALL db.idx.vector.queryNodes('Question', 'embedding', $vec, 5)
YIELD node AS similar_question

// Step 2: Graph traversal
MATCH (similar_question)-[:ASSESSES]->(topic:Topic)

// Step 3: Aggregate context
RETURN similar_question.text, topic.definition
```

---

## 7. Cross-Subject Architecture

### 7.1 Unified Graph with Namespace Partitioning

All subjects in one graph enables interdisciplinary queries:
- `:History:Event` linked to `:Biology:Organism` (e.g., Famine → Potato Blight)
- Labels prefixed by subject for efficient filtering

### 7.2 Bridge Nodes (Curriculum Common Concepts)

Concepts appearing in multiple subjects:
- "Statistics" (Math, Biology, Geography)
- "Energy" (Physics, Chemistry, Biology)

Create `SAME_AS` edges or merge into super-nodes for transfer learning.

### 7.3 Subject-Specific Requirements

| Subject Group | Ontology Model | Key Edge Types | Assessment Logic |
|--------------|----------------|----------------|------------------|
| Mathematics | Derivation Tree | :PREREQUISITE | Step-based (Scale) |
| Sciences | Taxonomy & System | :FLOWS_TO, :INTERACTS | Keyword/Hit-Count |
| Humanities | Causal & Spatial | :CAUSED, :LOCATED_AT | SRP Count |
| Languages | Thematic Web | :EXPLORES, :TRANSLATES | Rubric (PCLM) |
| Business | Transaction Graph | :DEBITS, :CREDITS | Exact Layout |

---

## 8. Bilingual Data Strategy

### 8.1 Unified Concept Node

```json
{
  "concept_id": "PYTHAG_THEOREM",
  "name_en": "Theorem of Pythagoras",
  "name_ga": "Teoirim Pythagoras",
  "definition_en": "The square of the hypotenuse...",
  "definition_ga": "An chearnóg ar an taobhagán..."
}
```

### 8.2 Dialect Handling

```cypher
(:Word {lemma: "Look"}) -[:HAS_FORM]-> (:Form {text: "Féach", dialect: "Standard"})
(:Word {lemma: "Look"}) -[:HAS_FORM]-> (:Form {text: "Amharc", dialect: "Ulster"})
```

### 8.3 Translation Synonym Layer

```python
SYNONYM_MAP = {
    "emotion": ["mothúchán", "mothú"],
    "contrast": ["codarsnacht"],
    "life": ["saol"]
}
```

---

## 9. Implementation Roadmap

1. **Phase 1**: Define `.owl` ontology and `.baml` schemas (data contract)
2. **Phase 2**: Build CocoIndex flow for static curriculum PDFs
3. **Phase 3**: Process exam paper archive (Questions → Topics)
4. **Phase 4**: Activate Graphiti temporal layer
5. **Phase 5**: Deploy API for student queries and mastery tracking


---

### `frontend-stack.md` — 01-irish-edtech-platform

# Frontend Stack for Irish Education Platform

## Executive Summary

This document details the edge-native, browser-first architecture for the Irish Leaving Certificate educational platform. The approach shifts computation from centralized servers to the client (WebAssembly) and network edge (Cloudflare), providing instant-start environments, reactive visualizations, and seamless bilingual support.

---

## 1. Architectural Philosophy: Edge-Native Shift

### 1.1 Traditional vs. Proposed Model

| Layer | Traditional (Server-Centric) | Proposed (Edge-Native) |
|-------|------------------------------|------------------------|
| Frontend | Vue.js / React (Node.js) | **TanStack Start** (Edge-rendered) |
| Compute | Bare Metal / Firecracker VMs | **Cloudflare Workers** |
| State | Redis / MongoDB | **Durable Objects** |
| Runtime (Light) | MicroVMs per user | **Marimo WebAssembly** |
| Runtime (Heavy) | MicroVMs | **Self-Hosted Coder** |
| Transport | WebSocket/SSH tunnels | **Durable Objects WebSockets** |

### 1.2 Cost-Performance Advantage

- **Marimo WASM**: Zero server cost for math/Python computation
- **Edge Rendering**: Sub-50ms TTFB from nearest Cloudflare PoP
- **Offline Capability**: Students in rural Ireland can work without connectivity
- **Browser Sandbox**: Isolation by design, no complex iptables configuration

---

## 2. TanStack Start: The Meta-Framework

### 2.1 Why TanStack Start

- **Full-Stack Type Safety**: TypeScript end-to-end
- **Server-Side Rendering with Streaming**: Progressive enhancement for slow connections
- **File-System Routing**: Matches curriculum hierarchy naturally
- **Server Functions**: API endpoints defined alongside UI code

### 2.2 Isomorphic Rendering for Education

```
Student Request (Rural Kerry)
    ↓
Cloudflare Edge (Dublin PoP)
    ↓
Stream HTML immediately (text, definitions, syllabus)
    ↓
Student starts reading
    ↓
JavaScript hydrates (WebGL simulations load)
    ↓
Full interactivity available
```

### 2.3 Type-Safe Syllabus Modeling

```typescript
// Syllabus schema enforced at build time
interface SyllabusNode {
  id: string;           // e.g., "CHEM_1.1"
  subject: Subject;
  strand: string;
  topic: string;
  learning_outcomes: LearningOutcome[];
}

interface Experiment {
  chemicals: Chemical[];
  safety_precautions: string[];
  procedure_steps: Step[];
}
```

Build fails if developer omits mandatory fields like `safety_precautions`.

---

## 3. Bilingual Routing and Localization

### 3.1 URL-Level Internationalization

```
/en/calculus/derivatives
/ga/calcalas/díorthaigh
```

### 3.2 Implementation Strategy

1. **Middleware Detection**: Cloudflare Worker inspects `Accept-Language` header
2. **Streaming Resources**: Load only current language segment (not entire JSON blob)
3. **Terminology Mapping**: KV store for glossary (`"Integer" → "Slánuimhir"`)

### 3.3 Real-Time Bilingual Toggling

Durable Objects broadcast language state changes:
```json
{ "action": "set_lang", "lang": "ga" }
```
All connected clients update UI labels and glossary terms instantly.

---

## 4. Marimo & WebAssembly: Browser-Based Computation

### 4.1 Why Marimo

- **Reactive Notebooks**: Change `x`, and `y = x²` updates instantly
- **No Hidden State**: Enforced dataflow graph (unlike Jupyter)
- **WebAssembly Export**: Full Python environment in static HTML/Wasm bundle

### 4.2 Pedagogical Advantages

**Complex Numbers Visualization**:
- Slider controls θ (argument) and r (modulus)
- Vector rotates on Argand Diagram in real-time
- Python code runs in browser via Pyodide
- Zero server cost

### 4.3 Integration with TanStack Start

```typescript
// Embed Marimo as iframe or web component
// Static assets served from Cloudflare R2

// Communication via PostMessage
window.parent.postMessage({
  type: "TASK_COMPLETE",
  taskId: "calc_deriv",
  payload: { result: 24 }
});
```

---

## 5. Cloudflare Edge Infrastructure

### 5.1 Workers for API Logic

- Replace monolithic Node.js "Foreman"
- Server functions execute at nearest PoP
- Sub-50ms latency for Dublin students

### 5.2 Durable Objects for State

```typescript
export class LabSession implements DurableObject {
  sessions: Map<string, WebSocket>;

  async handleSession(ws: WebSocket) {
    ws.accept();
    ws.addEventListener("message", async (msg) => {
      const event = JSON.parse(msg.data);
      if (event.type === "TASK_SUBMIT") {
        await this.gradeTask(event.payload);
      }
    });
  }
}
```

**Use Cases**:
- WebSocket termination for classroom collaboration
- Teacher broadcast to student Marimo instances
- Presence tracking and telemetry
- Code persistence with automatic resume

### 5.3 Edge-Native Authentication

- **Cloudflare Access** + custom JWT in Worker
- Tokens validated at edge (unauthenticated requests never reach backend)
- GitHub OAuth with profile storage

---

## 6. Heavy Compute: Self-Hosted Coder

### 6.1 When to Use Coder (vs. Marimo)

| Content Type | Solution | Cost |
|-------------|----------|------|
| Math visualization, basic Python | Marimo WASM | $0 |
| Web server hosting, databases | Coder | Server time |
| Embedded systems projects | Coder | Server time |

### 6.2 Coder Template for LCCS

```terraform
resource "coder_agent" "main" {
  arch = "amd64"
  os = "linux"
  startup_script = <<EOT
    # Irish language aliases
    echo "alias liosta='ls -la'" >> /home/coder/.bashrc
    python3 -m http.server 8080 &
  EOT
}

resource "docker_container" "workspace" {
  image = "ghcr.io/leaving-cert/lccs-env:latest"
}
```

### 6.3 Secure Integration

- **Cloudflare Tunnel**: Expose Coder workspaces without public ports
- **OIDC Token Hand-off**: Automatic student login
- **Iframe Embedding**: Coder IDE inside TanStack dashboard

---

## 7. Visualization Libraries

### 7.1 Geography: DuckDB + Deck.gl

**DuckDB Wasm** runs in web worker:
```sql
SELECT * FROM electoral_divisions
WHERE population_density < 10
AND dependency_ratio > 50
```

**Deck.gl** renders results via WebGPU:
- Choropleth maps with smooth color interpolation
- 3D building extrusion for urban analysis
- 60fps on student laptops

### 7.2 Chemistry: MathBox.js + R3F

**MathBox.js** for "3Blue1Brown" aesthetic:
- Render probability density functions (orbitals)
- Transition from Bohr model to Schrödinger model
- Glowing, translucent clouds via custom shaders

**React Three Fiber** for virtual lab:
- 3D burette and conical flask
- Fluid dynamics with Beer's Law shader
- pH-dependent color interpolation

### 7.3 Math: Mafs for Interactive Graphs

```jsx
<Mafs>
  <Coordinates.Cartesian />
  <Plot.OfX y={(x) => Math.sin(x)} />
</Mafs>
```

- Drag variables, see real-time graph updates
- Tight coupling with particle simulations

### 7.4 Geography Maps: MapLibre GL JS

- Vector tile rendering for OS-style topographic maps
- Terrain-RGB for 3D tilt (slope and aspect analysis)
- Essential for Geographical Investigation skills

---

## 8. Subject-Specific Implementations

### 8.1 Chemistry Visualizations

| Syllabus Topic | Technology | Implementation |
|---------------|------------|----------------|
| Atomic Structure | MathBox.js | Orbital probability clouds |
| Bonding | 3Dmol.js | VSEPR shapes, bond angles |
| Equilibrium | R3F + Mafs | Particle sim + live Kc graph |
| Titration | R3F | Virtual lab with fluid shaders |

### 8.2 Geography Tools

| Syllabus Topic | Technology | Implementation |
|---------------|------------|----------------|
| Plate Tectonics | React-Globe.gl | GeoJSON plate boundaries |
| Landforms | Babylon.js | Procedural terrain erosion |
| Demographics | DuckDB + Deck.gl | Census SQL queries |
| Urban Zones | Deck.gl PolygonLayer | 3D land value extrusion |

### 8.3 English Digital Humanities

| Feature | Technology | Implementation |
|---------|------------|----------------|
| Sentiment Analysis | Compromise.js | "Mood Graph" per chapter |
| Character Networks | D3.js | Force-directed relationship graph |
| Annotation | TipTap/ProseMirror | Thematic tagging with persistence |

---

## 9. Pedagogical UX Patterns

### 9.1 Dual Coding (Mayer's Principles)

Text and simulation side-by-side:
```
┌──────────────────┬──────────────────┐
│  Syllabus Text   │   WebGL Canvas   │
│  (scrollable)    │   (synchronized) │
└──────────────────┴──────────────────┘
```

As student scrolls text about "Alkanes", 3D viewer morphs molecule to match.

### 9.2 Scaffolded Interactivity

1. **Observe**: Animation runs automatically
2. **Explore**: Controls unlock for manipulation
3. **Predict**: Simulation pauses, student must predict outcome
4. **Verify**: Simulation resumes, confirms or corrects

### 9.3 AI-Assisted Bilingual Feedback

Using Cloudflare Workers AI (Llama 3):
```
Prompt: "Analyze this Python code. Reply in Irish."
Response: "Maith thú! D'úsáid tú lúb 'for' i gceart..."
```

---

## 10. Progressive Web App Features

### 10.1 Offline Capability

- Service workers cache Marimo WASM bundles
- Students continue math lessons without internet
- Critical for rural Ireland with poor broadband

### 10.2 Virtual Field Notebook (Geography GI)

- PWA section works offline
- Input river width, velocity, bedload size in field
- Auto-sync generates scatter graphs when online

---

## 11. Security and Scalability

### 11.1 Attack Surface

| Architecture | Attack Surface |
|-------------|----------------|
| Server VMs | Root daemon, iptables misconfig |
| Marimo WASM | Student's browser sandbox only |
| Coder | Container escape (mitigated by gVisor) |

### 11.2 Scalability Profile

- **Frontend/WASM**: Infinite scale on Cloudflare CDN
- **Durable Objects**: Auto-distributed globally
- **Coder**: Only ~20% of syllabus needs heavy compute

### 11.3 Cost Analysis

| Component | Monthly Cost |
|-----------|-------------|
| Cloudflare Workers/Pages | $5-20 |
| Durable Objects | Negligible (text sync) |
| Self-hosted Coder | $10-20 |
| **Total** | ~$50/month |

---

## 12. Implementation Roadmap

### Phase 1: Core Framework (Weeks 1-4)
- Initialize TanStack Start project
- PostgreSQL + Drizzle ORM setup
- Implement type-safe syllabus schema

### Phase 2: Geospatial Engine (Weeks 5-10)
- ETL pipelines for CSO/Eurostat → GeoParquet
- DuckDB Wasm integration
- Deck.gl component library

### Phase 3: Science Simulations (Weeks 11-16)
- MathBox.js orbital visualizers
- React Three Fiber virtual lab
- Mafs dynamic graphing

### Phase 4: Content & Accessibility (Weeks 17-24)
- Populate Leaving Cert content
- WCAG 2.1 AA audit
- Keyboard navigation for WebGL


---

### `subject-implementations.md` — 01-irish-edtech-platform

# Subject-Specific Implementations

## Executive Summary

This document provides technical blueprints for implementing AI tutoring across all Leaving Certificate subjects, extending the core mathematics architecture to handle the diverse assessment models, data modalities, and pedagogical requirements of 30+ subjects.

---

## 1. Assessment Logic by Subject Group

| Subject Group | Ontology Model | Key Edge Types | Assessment Logic | Data Modality |
|--------------|----------------|----------------|------------------|---------------|
| **Mathematics** | Derivation Tree | :PREREQUISITE | Step-based (Scale 10C) | Text + Symbolic |
| **Sciences** | Taxonomy & System | :FLOWS_TO, :INTERACTS | Keyword/Hit-Count | Text + Diagram |
| **Humanities** | Causal & Spatial | :CAUSED, :LOCATED_AT | SRP Count / Argument | Text + Map + Image |
| **Languages** | Thematic Web | :EXPLORES, :TRANSLATES | Rubric (PCLM) | Text + Audio |
| **Business** | Transaction Graph | :DEBITS, :CREDITS | Exact Layout / Values | Text + Table |

---

## 2. Experimental Sciences

### 2.1 Physics: Mathematical-Empirical Bridge

**Cross-Graph Dependencies**:
- Physics concepts require Math prerequisites
- Example: "Velocity-Time Graphs" `:REQUIRES_MATH_CONCEPT` → "The Line"

```cypher
(:Topic {name: "Linear Motion", subject: "Physics"})
  -[:REQUIRES_MATH_CONCEPT]->
(:Topic {name: "Slope", subject: "Maths"})
```

**Diagnostic Logic**: When student fails Physics question, traverse edge to check Math mastery. Diagnose as Math error if prerequisite mastery is low.

**BAML Extension for Dimensional Analysis**:
```baml
class PhysicsValue {
  magnitude: float
  unit: string @description("SI Unit, derived from context")
  dimension: string @description("e.g., Length, Time, Force")
}

class PhysicsQuestion {
  given_values: PhysicsValue[]
  required_value_dimension: string
}
```

Enables "Dimensional Consistency Checks" on AI-generated answers.

### 2.2 Biology: Taxonomical and Systemic Graph

**New Edge Types**:
```cypher
(:Organelle {name: "Mitochondria"}) -[:PART_OF]-> (:Process {name: "Respiration"})
(:Process {name: "Respiration"}) -[:PRODUCES]-> (:Molecule {name: "ATP"})
```

**Query Logic**: "Trace the pathway" queries vs "Find similar" queries.

**Visual Data Ingestion**:
1. Diagram Segmentation: Identify line art regions
2. Multimodal Labeling: Generate textual descriptions
3. Embedding: Store descriptions alongside question text

### 2.3 Chemistry: Syntax of Matter

**Chemical Markup**:
- SMILES strings for organic molecules (e.g., Benzene: `C1=CC=CC=C1`)
- Enables substructure searching

**Family Structure**:
```cypher
(:Family {name: "Alcohols"}) -[:CONTAINS]-> (:Molecule {name: "Ethanol"})
(:Molecule {name: "Ethanol"}) -[:UNDERGOES]-> (:Reaction {name: "Oxidation"})
```

### 2.4 Agricultural Science: Applied Integration

**Project Support (25% of grade)**:
- Graphiti tracks project state over months
- Episodes: Draft introduction → Data results → Conclusion
- "Time Travel" allows critiquing conclusion based on earlier data

---

## 3. Humanities

### 3.1 History: Bi-Temporal Causal Graph

**Double Timeline**:
1. **Historical Time**: When event occurred (1916)
2. **Curriculum Time**: When topic added to syllabus

```cypher
(:Event {name: "Easter Rising", real_world_timestamp: "1916-04-24"})
```

**Causal Edge Types**:
- `:CONTRIBUTED_TO`
- `:TRIGGERED`
- `:LONG_TERM_CAUSE`

**Multiperspectivity**:
```cypher
(:Event {name: "Anglo-Irish Treaty"})
  <-[:PERSPECTIVE_ON]- (:Perspective {name: "Pro-Treaty"})
  <-[:PERSPECTIVE_ON]- (:Perspective {name: "Anti-Treaty"})
```

**Essay Evaluation**: Check if student references both perspectives.

**Research Study Report (RSR)**:
- Ingest primary source documents
- "Source Evaluation Engine" detects reliability and bias
- Specialized vector index for historiographical terms

### 3.2 Geography: Geospatial Knowledge Graph

**FalkorDB Geospatial Indexing**:
```cypher
(:CaseStudy {name: "Greater Dublin Area", lat: 53.3498, lng: -6.2603})
```

**Spatial Queries**: "Compare peripheral region (West) with core region (East)"

**SRP (Significant Relevant Point) Logic**:
- Marking: 2 marks per SRP
- BAML extracts SRPs from marking schemes
- Grading: Semantic Hit Count (sentence similarity to valid SRPs)

**OS Map Analysis**:
1. CV model identifies features (Post Offices, Contours)
2. Pixel coordinates → Grid coordinates mapping
3. Grid reference validation

### 3.3 Classical Studies

Uses History patterns with:
- Ancient timeline (BCE dates)
- Literary analysis edges from English

---

## 4. Languages

### 4.1 Gaeilge (Irish)

**Audio Processing Pipeline**:
```
Student Audio Recording
    ↓
Whisper (Irish dialect fine-tuned: Connacht, Munster, Ulster)
    ↓
Transcription Analysis:
  - Fluency (pauses, speech rate)
  - Vocabulary (Saibhreas) against "Rich Vocabulary" NodeSet
  - Grammar (Tuiseal Ginideach)
    ↓
Timestamped Error Feedback
```

**Dialectal Modeling**:
```cypher
(:Word {lemma: "Look"}) -[:HAS_FORM]-> (:Form {text: "Féach", dialect: "Standard"})
(:Word {lemma: "Look"}) -[:HAS_FORM]-> (:Form {text: "Amharc", dialect: "Ulster"})
```

Prevents "False Negative" grading for valid dialectal variations.

### 4.2 English

**PCLM Grading Architecture**:
| Component | Weight | Analysis Method |
|-----------|--------|-----------------|
| Purpose | 30% | Vector similarity (Essay ↔ Question) |
| Coherence | 30% | Discourse analysis (transitions, structure) |
| Language | 30% | Lexical diversity score |
| Mechanics | 10% | Spelling/grammar check |

**Comparative Study (Three Texts)**:
```cypher
(:Text {title: "Philadelphia, Here I Come!"}) -[:EXPLORES]-> (:Theme {name: "Isolation"})
(:Text {title: "Shawshank Redemption"}) -[:EXPLORES]-> (:Theme {name: "Hope"})
```

**Synthesis Engine**: Retrieve nodes from multiple texts, identify Contrast/Similarity edges.

### 4.3 Modern Foreign Languages (French, German, Spanish)

**Dynamic Question Generation**:
1. Scrape current news (e.g., Le Monde)
2. BAML extraction
3. Generate "Leaving Cert Style" questions from learned patterns

**Difficulty-Indexed Corpus**: Target-language texts indexed by reading level.

---

## 5. Business Group

### 5.1 Accounting: Double-Entry Graph

```cypher
(:Account {name: "Bank"})
(:Account {name: "Sales"})
// Transaction: Debit Bank, Credit Sales
(:Account {name: "Bank"}) -[:DEBIT {amount: 100}]-> (:Transaction {id: "TX001"})
(:Account {name: "Sales"}) -[:CREDIT {amount: 100}]-> (:Transaction {id: "TX001"})
```

**Balance Validation**: If Sum(Debits) != Sum(Credits), traverse graph to find error origin.

**Table Extraction**: BAML must preserve row/column structure for cell-by-cell grading.

### 5.2 Business: Structured Long Answer

**State-Explain-Example Pattern**:
```
"Delegation is assigning duties." → State (2 marks)
"This reduces manager workload." → Explain (2 marks)
"e.g., Manager asks supervisor to do roster." → Example (1 mark)
```

**Backend Logic**: Parse paragraph into three components, award marks per component.

### 5.3 Economics

Uses Accounting patterns with:
- Economic indicator tracking (temporal)
- Policy impact modeling (causal edges)

---

## 6. English/Irish Literature Data Model

### 6.1 Poet Rotation Matrix (English)

27 poets tracked across 23 years:
- **High-Frequency**: Dickinson, Yeats (recent clusters)
- **Odd-Year Cycle**: Hopkins (2021, 2019, 2017, 2013, 2011)
- **Dormant**: Larkin (last seen 2007), Montague (last seen 2007)

**Recency Score**:
$$\text{Recency Score} = \sum \frac{1}{\text{CurrentYear} - \text{ExamYear}}$$

### 6.2 Stylistic Taxonomy

| Poet | Style Keywords |
|------|---------------|
| Bishop | Analytical, Rarely Emotional, Harsh Realities |
| Dickinson | Beautiful vs Horrific, Darker Aspects, Intrigue |
| Keats | Sensuous Beauty, Melancholy |
| Yeats | Intellectual vs Emotional, Tension, Real vs Ideal |
| Rich | Power and Powerlessness, Social Concerns |

### 6.3 Irish Prose (Character-Centric)

**Hurlamboc**:
- Focus: Character "Lisín"
- Themes: Control, Self-Deception
- Tags: `caithréim` (triumph), `i gceannas` (in control)

**Cáca Milis**:
- Focus: Paul (disability), Catherine (cruelty)
- Themes: Disability, Reader Response
- Question style: Argumentative ("nach dtuilleann mórán trua")

### 6.4 Irish Poetry (A/B/C Structure)

```json
{
  "poem": "Géibheann",
  "year": 2021,
  "parts": {
    "A": "Codarsnacht i saol an ainmhí",
    "B": "Teideal oiriúnach?",
    "C": "Saol agus saothar an fhile"
  }
}
```

**Part Types**:
- A: Thematic/Descriptive
- B: Technical/Emotional (Mothúchán)
- C: Biographical

---

## 7. Universal BAML Schema

### 7.1 Polymorphic Assessment Item

```baml
enum SubjectType {
  Math
  Science
  Language
  Humanities
  Business
}

class AssessmentItem {
  id: string
  year: int
  level: "Higher" | "Ordinary"
  subject: SubjectType
  strand_ref: string
  topic_tags: string[]

  // Polymorphic Content
  text_content: string?
  image_assets: ImageAsset[]?
  audio_assets: AudioAsset[]?
  table_data: TableData?

  marking_scheme_ref: string
}

class ImageAsset {
  url: string
  description: string @description("Alt-text from Vision Model")
  type: "Map" | "Diagram" | "Photo" | "Chart"
}
```

### 7.2 Coursework Brief Extraction

```baml
class ProjectBrief {
  subject: string
  year: int
  title: string
  constraints: Constraint[]
}

class Constraint {
  type: "word_count" | "source_count" | "section_required"
  value: string
  description: string
}
```

Validate student submission against constraints before semantic grading.

---

## 8. Cross-Subject Intelligence

### 8.1 Bridge Nodes (Common Concepts)

Concepts appearing in multiple subjects:
- "Statistics" (Math, Biology, Geography)
- "Energy" (Physics, Chemistry, Biology)
- "Causation" (History, Science, Business)

```cypher
(:Physics:Energy) -[:SAME_AS]-> (:Biology:Energy)
```

**Transfer Learning**: Mastery in Physics "Energy" implies higher probability of competence in Biology "Energy".

### 8.2 Cognitive Load Balancing

Track session duration and error rates per subject:
```cypher
(:Student) -[:STUDIES {
  duration_minutes: 40,
  error_rate: 0.35,
  cognitive_load: "HIGH"
}]-> (:Math:Topic)
```

Recommend switching subjects when error rates spike.

### 8.3 Spaced Repetition Priority

When multiple topics due for review:
1. Calculate exam weightings from syllabus
2. Prioritize by percentage contribution to grade
3. Example: Calculus (15% of Math) beats Genetics (5% of Biology)

---

## 9. Cocoindex Flow Router

```python
# Subject-specific processing flows
def route_document(doc):
    subject = classify_subject(doc)

    if subject == "Math":
        return Flow_Math  # OCR → BAML (LaTeX) → FalkorDB
    elif subject in ["Irish", "English", "French"]:
        return Flow_Language  # OCR → Audio Transcribe → BAML (PCLM)
    elif subject in ["Biology", "Geography"]:
        return Flow_Visual  # OCR → Layout Analysis → Vision Model → BAML
    else:
        return Flow_Standard
```

Ensures compute-heavy resources (Vision Models) only invoked when necessary.

---

## 10. Implementation Priorities

### Phase 1: Core Subjects
1. Mathematics (pilot)
2. English (high volume)
3. Irish (bilingual complexity)

### Phase 2: STEM Expansion
4. Physics (Math dependencies)
5. Chemistry (symbolic notation)
6. Biology (visual content)

### Phase 3: Humanities
7. History (temporal reasoning)
8. Geography (geospatial)

### Phase 4: Remaining Subjects
9. Business/Accounting
10. Modern Languages
11. Applied subjects

---

## 11. Subject-Specific Tech Stack Summary

| Subject | BAML Focus | Visualization | Special Requirements |
|---------|-----------|---------------|---------------------|
| Mathematics | LaTeX, Formulas | MathBox.js, Mafs | Step-based grading |
| Physics | Units, Dimensions | R3F simulations | Math cross-references |
| Chemistry | SMILES, Reactions | 3Dmol.js, MolStar | Equation balancing |
| Biology | Taxonomies, Diagrams | D3.js hierarchy | Diagram segmentation |
| History | Timelines, Causation | Timeline.js | Bi-temporal queries |
| Geography | SRPs, Maps | Deck.gl, MapLibre | Geospatial indexing |
| English | PCLM rubrics | D3.js networks | Sentiment analysis |
| Irish | Dialects, Audio | Waveform viz | Whisper fine-tuning |
| Accounting | Tables, Ledgers | React Tables | Double-entry validation |


---

### `bunchloch.md` — 01-selfhosting

# Bunchloch Infrastructure Stack

Bunchloch is the integrated self-hosted infrastructure platform for the hackathon project. It combines container orchestration, zero-trust networking, Git/package hosting, and secrets management into a cohesive stack.

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         BUNCHLOCH STACK                                     │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1PASSWORD CONNECT (Secrets Foundation)                              │   │
│  │  - op-connect-api (8080)                                            │   │
│  │  - op-connect-sync (8081)                                           │   │
│  │  Provides: Centralized secret storage and retrieval                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              │ Secrets via API                             │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ LOCKET (Secrets Sidecar)                                            │   │
│  │  - Provider: op-connect                                             │   │
│  │  - Mode: watch (continuous sync)                                    │   │
│  │  - Output: /run/secrets/locket/* (tmpfs)                           │   │
│  │  Provides: Secure secrets injection into containers                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│              ┌───────────────┼───────────────┐                             │
│              ▼               ▼               ▼                              │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────┐              │
│  │ PANGOLIN      │  │ KOMODO        │  │ FORGEJO           │              │
│  │ (Networking)  │  │ (Containers)  │  │ (Git/Packages)    │              │
│  └───────────────┘  └───────────────┘  └───────────────────┘              │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

## Component Directory Structure

```
infrastructure/bunchloch/
├── README.md                    # This file
├── authentication/              # Standalone auth testing
│   └── docker-compose.yml       # Pocket ID + TinyAuth + Traefik
├── automation/                  # Ansible orchestration
│   ├── compose.yaml             # Ansible Execution Environment
│   ├── SETUP.md
│   └── ansible/
│       ├── inventory/
│       │   └── komodo.yml       # Server definitions
│       └── playbooks/
│           ├── komodo.yml       # Periphery deployment
│           └── periphery.yml    # With Locket integration
├── forgejo/                     # Git + Package Registry
│   ├── compose.yaml
│   └── README.md
├── komodo/                      # Container Orchestration
│   ├── komodo-core/
│   │   ├── mongo.compose.yaml   # Core + MongoDB + Periphery
│   │   └── compose.env
│   └── periphery/
│       └── compose.yaml         # Remote periphery agents
└── pangolin/                    # Zero-Trust Networking
    ├── pangolin-core/
    │   ├── compose.yaml
    │   └── config/
    │       ├── config.yml
    │       ├── traefik/
    │       └── middleware-manager/
    ├── newt/                    # Tunnel agents
    │   └── compose.yaml
    └── olm/                     # Lightweight tunnel client
        └── compose.yaml
```

## Service Relationships

### 1. 1Password Connect → Locket → All Services

**Flow:** 1Password vaults → Connect API → Locket sidecar → Service secrets

1Password Connect provides the centralized secret store. Locket runs as a sidecar container in each stack that needs secrets, watching template files and writing decrypted values to tmpfs volumes.

**Key secrets managed:**
- Database credentials (PostgreSQL, MongoDB)
- Server secrets (JWT, passkeys)
- API tokens (Newt ID, Newt secret)
- OAuth credentials

### 2. Komodo (Container Orchestration)

**Components:**
- **Komodo Core** (port 9120): Web UI and API for managing containers
- **MongoDB**: State database for Komodo
- **Periphery**: Agent deployed on each server to manage Docker

**Architecture:**
- Core runs centrally with outbound-only mode (secure by default)
- Periphery agents connect TO Core (no inbound ports needed)
- Communication secured via passkeys

**Key Features:**
- Stack deployment (Docker Compose stacks)
- Container lifecycle management
- Multi-server orchestration
- GitOps integration (webhooks)

### 3. Pangolin (Zero-Trust Reverse Proxy)

**Core Components:**
- **Pangolin** (port 3001): Identity-aware proxy engine
- **Gerbil** (port 51820/UDP): WireGuard tunnel controller
- **Traefik** (ports 80, 443): Dynamic load balancer
- **Middleware Manager** (port 3456): Traefik rules UI

**Authentication:**
- **Pocket ID** (port 1411): Passkey-based OIDC provider
- **TinyAuth** (port 3000): Forward authentication middleware

**Tunnel Agents:**
- **Newt**: Connects local services to Pangolin
- **OLM**: Lightweight tunnel client for remote sites

**Network Flow:**
```
External Request → Traefik → TinyAuth (auth) → Gerbil (tunnel) → Service
```

### 4. Forgejo (Git & Package Registry)

**Services:**
- PostgreSQL: Git repository database
- Forgejo (ports 3000 HTTP, 2222 SSH): Git server

**Features:**
- Git repositories (GitHub alternative)
- PyPI package registry
- Container registry (OCI)
- CI/CD with Forgejo Actions

**Package URLs:**
- PyPI: `http://forgejo:3000/api/packages/{owner}/pypi`
- Install: `pip install --index-url http://forgejo:3000/api/packages/{owner}/pypi/simple {pkg}`

### 5. Ansible Automation

**Purpose:** Automate Periphery deployment across servers

**Execution Environment:**
- Image: `ghcr.io/bpbradley/ansible/komodo-ee:latest`
- Integrated with 1Password Connect for vault secrets
- SSH access to target servers

**Playbooks:**
- `komodo.yml`: Deploy/update Komodo periphery
- `periphery.yml`: Periphery with Locket integration

## Startup Order

For full stack deployment, services should start in this order:

1. **1Password Connect** - Secrets foundation (must be running first)
2. **Locket sidecars** - Wait for Connect to be healthy
3. **PostgreSQL** (Pangolin & Forgejo) - Database initialization
4. **MongoDB** (Komodo) - State storage
5. **Pangolin services** - Depends on Locket & PostgreSQL
6. **Komodo Core** - Depends on MongoDB
7. **Forgejo** - Depends on PostgreSQL
8. **Newt/OLM tunnels** - Depends on Pangolin network
9. **Komodo Periphery** - Depends on Core

## Quick Start

### 1. Start Secrets (Required First)
```bash
cd infrastructure/stacks/secrets/onepassword
docker compose up -d
```

### 2. Start Pangolin Core
```bash
cd infrastructure/bunchloch/pangolin/pangolin-core
docker compose up -d
```

### 3. Start Komodo Core
```bash
cd infrastructure/bunchloch/komodo/komodo-core
docker compose up -d
```

### 4. Start Forgejo
```bash
cd infrastructure/bunchloch/forgejo
docker compose up -d
```

### 5. Deploy Remote Periphery (via Ansible)
```bash
cd infrastructure/bunchloch/automation
docker compose run --rm ansible ansible-playbook playbooks/komodo.yml
```

## Networks

| Network | Type | Services |
|---------|------|----------|
| `pangolin` | bridge | Pangolin, Gerbil, Traefik, auth services |
| `forgejo_network` | bridge | Forgejo, PostgreSQL |
| `default` | bridge | Komodo Core, MongoDB, Periphery |

## Ports Reference

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| 1Password API | 8080 | HTTP | Secret retrieval |
| 1Password Sync | 8081 | HTTP | Credential sync |
| Komodo Core | 9120 | TCP/WSS | Cluster control |
| Pangolin | 3001 | HTTP | Identity proxy |
| Gerbil | 51820 | UDP | WireGuard tunnel |
| Traefik | 80, 443 | TCP | HTTP/S routing |
| Pocket ID | 1411 | HTTP | OIDC provider |
| TinyAuth | 3000 | HTTP | Forward auth |
| Forgejo HTTP | 3000 | HTTP | Git web UI |
| Forgejo SSH | 2222 | SSH | Git clone |

## Related Documentation

- **Komodo**: `/research/infrastructure/komodo/`
- **Pangolin**: `/research/infrastructure/pangolin/`
- **Dagger Deployment**: `/dagger/README.md`
- **OpenSpec Infrastructure Specs**: `/openspec/specs/komodo-infrastructure/`


---

### `comparing-approaches-pangolin-registration-komodo-deployment.md` — 01-selfhosting

Comparing Approaches for Pangolin

Registration after Komodo Deployment

Deploying   a   containerized   service   with  Komodo  and   then   registering   it   with  Pangolin  (a   tunneled

reverse   proxy)   can   be   achieved   via   three   main   methods.   Many   in   the   self-hosting   community   are

interested in seamless  Komodo + Pangolin integration

1

. Below, we compare the three approaches

side-by-side and evaluate them on key criteria:

•

Approach 1: Komodo Post-Deploy Shell Script calling the Pangolin API

•

Approach 2: Komodo Action (TypeScript SDK) to call Pangolin programmatically

•

Approach 3: Komodo Procedure combining deployment & Pangolin registration in one

workflow

Comparison of Registration Methods

Criterion

Approach 1 – Post-

Approach 2 – TypeScript

Approach 3 – Komodo

Deploy Shell Script

SDK Action

Procedure Workflow

Minimal – uses shell/

Integration

OS script outside

with

Komodo’s TS API. Not

TypeScript &

directly in TS code, so

CI/CD

extra glue needed to

invoke it.

High – fully in TypeScript.

Use Komodo’s TS SDK and

Pangolin’s TS client in one

code flow, fitting well into

Node.js automation

2

.

Moderate – implemented

within Komodo’s UI/

engine (Procedure +

possibly a TS Action). Less

external code; can be

triggered via Komodo

(button, webhook) or via

Komodo API.

Good – Komodo tracks

each step in a Procedure.

Basic – must parse

Robust – leverage try/

Deployment and

script exit codes/logs

catch and logging in TS.

registration steps have

manually. Limited

Can programmatically

statuses; failures halt the

Error

visibility in Komodo

react to failures (e.g. retry

procedure. Console

Handling &

UI (unless captured

or rollback). If run in an

output from an Action or

Observability

as a Komodo “Repo”

external process, logs go

script is visible in

run)

3

. Errors could

to CI pipeline; if as a

Komodo’s logs. Less

be missed if script

Komodo Action, console

flexible branching on

fails silently.

logs appear in Komodo UI.

error (unless coded in the

Action), but clear success/

failure reporting.

1

Criterion

Approach 1 – Post-

Approach 2 – TypeScript

Approach 3 – Komodo

Deploy Shell Script

SDK Action

Procedure Workflow

Security &

Secret

Management

Flexibility &

Reusability

Requires careful

handling of Pangolin

API token. Likely

stored as a Komodo

secret variable or on

the host. Can inject

the token into the

script’s env via

Komodo’s secret

interpolation

(keeping it hidden

from logs/users)

4

5

. The script will

use a scoped

Pangolin API key

(with minimal

permissions) for

safety

6

.

Fair – A shell script

can be written to

handle different

services if it accepts

parameters (e.g.

service name,

domain). However,

you must attach or

invoke this script for

each deployment. It’s

not inherently

reusable across

many stacks unless

manually

orchestrated (e.g. a

separate script call in

CI for each service).

Needs Pangolin token in

the app environment (e.g.

an env var or secret in CI).

If running as Komodo

Action, Komodo’s API

doesn’t expose secret

values easily

7

, so you

might resort to passing it

as a plain variable or

config file. External TS

code can load the token

from a vault or env. In all

cases, use Pangolin’s

scoped API key for least

privilege

8

.

High – Code can be

designed to deploy

multiple services and

register each in a loop, or

be called with parameters

for different services/

environments. The TS SDK

and Pangolin client allow

building a generic

deployment function. Easy

to integrate into existing

automation workflows or

pipelines for multiple

stacks.

Can leverage Komodo’s

built-in secrets

management. For

example, store the

Pangolin API token as a

secret variable in

Komodo (or in a

periphery agent’s config)

and interpolate it into the

registration step securely

5

. The Procedure’s

custom Action or script

can read it without

exposing it in logs.

Overall secure, as the

token stays within

Komodo/Pangolin

systems.

Good – The Procedure

can define a generic

workflow (e.g. deploy a

stack then register it). You

can potentially use

wildcards or patterns to

target multiple stacks in

one procedure stage

9

10

. For multiple

environments, you might

create one procedure per

environment or use

Komodo tags to select

targets. Reusability is

decent, though updating

the workflow (e.g. adding

a step) means editing the

procedure in Komodo (or

its TOML config).

2

Criterion

Approach 1 – Post-

Approach 2 – TypeScript

Approach 3 – Komodo

Deploy Shell Script

SDK Action

Procedure Workflow

Maintenance

& Scalability

Script logic is

separate from

Centralized code – easy to

It’s visual and declarative

Workflow is maintained in

Komodo’s configuration.

Komodo, so updates

maintain in one place (e.g.

(stages/actions defined in

require editing the

a Node project or within

UI or TOML) – easier to

script (in a repo or on

Komodo Action). New

manage for ops teams

each host). If you

Pangolin features or API

not wanting to dive into

have many services,

changes can be handled

code. Updating it (e.g. to

you’ll need to ensure

by updating the TS client

change how registration

each uses the latest

or code logic. Scales well:

is done) means editing

script version.

one script can orchestrate

the procedure’s steps or

Scaling to many

any number of

the embedded Action

deployments could

deployments/registrations

code. For many services,

mean managing

sequentially or in parallel.

the Procedure approach

many script triggers.

However, running a large

scales by grouping

On the plus side, the

number of deployments

operations (e.g. “deploy

script is simple and

via one process may

all stacks with tag X, then

environment-

require careful coding

register each”) but

agnostic, but that

(async handling, rate

complex logic may be

also means Komodo

limiting calls to Pangolin,

harder to express.

doesn’t “know” about

etc.).

it.

Komodo itself handles

the parallelism/

sequencing for you

11

.

Approach 1: Post-Deploy Shell Script calling Pangolin API

This   method   relies   on   a   shell   script   (or   similar)   executed   after   Komodo   deploys   the   container.   For

example, one might configure a Komodo Repo resource that contains a script and run it on the target
. The script would use an HTTP client (e.g.  curl  or a small program) to call

server post-deployment

3

Pangolin’s   Integration   API   and   register   the   new   service.   Pangolin’s   REST   API   supports  all   the

operations   available   in   its   UI  (including   creating   “sites”   for   new   services)

12

,   so   the   script   can

automate exposing the service.

Ease   of   Integration:  This   approach   is   relatively  low-level.   It   does   not   integrate   with   Komodo’s

TypeScript SDK at all – it’s an external step. If you already use TypeScript-based automation, invoking a

separate shell script adds a layer of complexity. You might trigger the script via a CI pipeline or Komodo

webhook, but the logic lives outside of your TypeScript code. This makes the flow less cohesive if your

deployment logic is otherwise in code.

Error Handling & Observability: With a post-deploy script, error handling is mostly manual. The script

should   exit   with   non-zero   status   on   failure   so   that   whatever   triggers   it   can   detect   the   error.

Observability is limited: you may need to log to a file or stdout and then inspect those logs. If run via

Komodo’s   Repo   mechanism,   Komodo   will   capture   the   output   and   status   (as   it   does   for   any   script

execution on a server)

3

, which helps centralize logs. However, you won’t have structured, high-level

error info – just whatever the script prints. There’s no built-in retry or complex logic unless you code it

into the shell script.

3

Security & Secret Management: The script needs the Pangolin API key to authenticate with Pangolin.

Storing and passing this secret is a concern. Komodo allows defining secure variables that won’t appear

in logs or UIs
. You can store the Pangolin token as a Komodo secret and inject it into the script’s
environment (e.g. via  [[TOKEN_NAME]]  interpolation in the Repo execution config). Another security

4

best practice is to use Pangolin’s scoped API keys – e.g., a key restricted to creating a specific site or

operating within one organization

13

. That way, even if the key is exposed, its misuse is limited. One

advantage of running a script on the Komodo periphery agent is that you can keep the secret local to

that server. Komodo supports mounting a secret config on the periphery so that the token is available

only on that host and never sent over the network

5

. This approach can thus be made secure, but it

requires conscious setup of secrets management.

Flexibility   &   Reusability:  The   shell   script   approach   can   be   as   flexible   as   you   make   it,   but   it’s   not

inherently modular. You might write the script to accept arguments (like service name, internal URL,

desired domain) so it can register any service. This makes it somewhat reusable across multiple services

or environments – you’d just call it with different parameters. Still, you need to arrange for it to run after

each deployment. If you have 10 services, you’ll either run the same script 10 times (with different args)

or have 10 nearly identical scripts configured. There’s no built-in loop or multi-target capability (unlike

Komodo’s   Procedure,   which   can   target   multiple   resources   with   one   action   stage

9

).   So,   reuse   is

possible but not automatic – you must orchestrate it.

Maintenance & Scalability:  A standalone script is easy to understand in isolation, but maintaining it

across many services or over time can be cumbersome. If Pangolin’s API changes or you need to add

new features (say, setting up access controls or health checks via API), you’ll update the script and

ensure all deployments use the new version. In a small setup, this is fine; in a large environment, you

might end up with configuration drift if each service had its own copy. Scaling out means making sure

every   deployed   stack   triggers   the   script   –   possibly   via   CI   jobs   or   webhooks.   There   isn’t   a   central

“controller” besides your external automation. On the plus side, this decoupling means Komodo itself

remains unaware of Pangolin, so Komodo updates won’t affect the script. But overall, as you scale the

burden is on you to consistently apply the script everywhere.

Approach 2: Using Komodo Actions via TypeScript SDK

This approach uses Komodo’s TypeScript capabilities (either through the Komodo Action resource or an

external script using the Komodo SDK) to perform the Pangolin registration in code. Komodo provides a

TypeScript   client/SDK   (published   on   NPM)   that   you   can   use   to   script   operations

2

.   We   assume

Pangolin also has a TypeScript client (generated from its OpenAPI), which lets you call Pangolin’s API

from Node.js instead of using raw HTTP calls. Essentially, you’d write a  TypeScript script  that does:

deploy the Docker Compose stack via Komodo’s API, then call Pangolin’s API to register the service. This script

could run externally (e.g. as part of a Node.js application or CI pipeline) or potentially as a Komodo

Action (Komodo can run user-defined TS code within its UI)

2

.

Ease of Integration: For anyone already automating with TypeScript, this method is very natural. You

can orchestrate everything in one language and process. The Komodo TS client gives you programmatic
control of deployments (e.g.  komodoClient.deployStack(stackConfig) ), and right after that you
can   invoke   Pangolin’s   registration   (e.g.   pangolinClient.createSite({...}) ).   Because   Komodo

Actions   run   with   an   already-authenticated   client

2

,   if   you   execute   this   within   Komodo’s   Action

framework you don’t even need to handle Komodo API keys. If running externally, you’d use an API key

for Komodo as well. In summary, this approach cleanly fits into CI/CD pipelines or custom deployment

scripts. No context-switching to bash scripts – everything stays in code, which improves maintainability.

4

Error Handling & Observability: Using a high-level language like TypeScript means you can implement

robust error handling. For example, you can catch errors from the Komodo deployment call or the

Pangolin API call and decide how to respond – maybe retry the Pangolin registration a few times if it

fails, or roll back the deployment if registration fails. You can log detailed messages or even send alerts

from the code. If this runs in a CI system or as a CLI, you’ll see the output in the job logs. If run as a
Komodo Action (triggered via Komodo’s UI or API), any   console.log   output or thrown error will

appear in Komodo’s interface for that Action run. This gives  better observability  than a silent shell

script – you have one place (the script’s output or Komodo’s Action logs) to check what happened at

each step.

Security & Secret Management: In a TS program, you will need to supply the Pangolin API token to the

code. Typically, this is done via environment variables or a secrets store integrated with your CI (for

external runs). That can be quite secure if your CI has proper secret masking. If you execute the code

inside Komodo (as an Action), accessing secrets is a bit trickier. Komodo’s API does not return secret

values   even   to   admin   users
,   which   means   your   Action   script   can’t   simply   call
komodoClient.readSecret("PANGOLIN_TOKEN")  unless you stored it as a non-secret variable (not

7

recommended).   A   workaround   is   to   pass   the   token   in   via   configuration:   for   instance,   store   it

unencrypted as a normal variable in Komodo (only visible to admins) or read it from a mounted config

file. These are not ideal, so many would prefer to run this TS code in an external context where your
secret management is under your control. In both cases, using Pangolin’s scoped API keys remains

important – you give the script a minimally privileged token

8

. The advantage here is that no token

touches any disk in plain text (it’s in memory in the Node process), and if using Komodo Action, you

avoid   network   transmission   of   the   token   by   possibly   having   it   in   Komodo’s   config.   Overall,   the   TS

approach can be made as secure as your secret storage practices allow.

Flexibility & Reusability:  This method shines in flexibility. As a developer, you can abstract the logic
into functions – e.g. a function  deployAndExpose(stackConfig, pangolinOptions)  that you call

for each service. Your script can read configuration files or accept input (like a list of services to deploy).

This makes it easy to extend to multiple environments or dozens of services. If you need to target

different Pangolin instances (say dev vs prod Pangolin servers), your code can handle that with different

API   endpoints   or   tokens   per   environment.   Essentially,   you   have  full   programming   capabilities,   so

loops, conditionals, and dynamic adjustments are all on the table. Reusing this across projects is as

simple as sharing the script or packaging it as a small CLI tool. Compared to Approach 1, there’s less

manual per-service setup – you could deploy N services by calling your function N times, or by iterating

through a config. The integration in a single script also means you don’t forget the Pangolin registration

step; it’s part of the defined workflow every time.

Maintenance   &   Scalability:  With   everything   in   code,   maintenance   becomes   a   standard   software

development   task.   You   keep   the   deployment+registration   script   in   version   control.   If   Pangolin’s   API

changes (for example, they introduce a new required field for creating a site), you update your TS client

or API calls in one place. If Komodo’s SDK updates, you update your dependency. There’s a bit of an

implicit dependency on two APIs (Komodo and Pangolin), but both are stable and versioned. As your

infrastructure   grows,   this   approach   scales:   you   can   incorporate   threading   or   asynchronous   calls   to

handle multiple deployments in parallel, or integrate backoff and rate limiting if needed. One thing to

consider   is  observability   at   scale  –   if   you   deploy   many   services   at   once   via   code,   make   sure   to

structure logs or use a monitoring system to track each deployment’s status. Overall, this approach is

highly maintainable  for those comfortable with coding, since it centralizes the logic and leverages

familiar development workflows (linting, testing, etc.). It reduces the “snowflake” configurations on each

Komodo instance in favor of one orchestrator script.

5

Approach 3: Komodo Procedure (Deployment + Pangolin

Registration Workflow)

Komodo’s Procedure resource offers a way to chain multiple actions into a repeatable workflow

14

. In

this approach, you create a Procedure that encapsulates the deployment of the stack and the Pangolin

registration as a single process. For example, the Procedure could have Stage 1 with a  DeployStack

execution,   and   Stage   2   with   a   custom  Action  (TypeScript   script)   or   a  RunRepo  execution   that   calls

Pangolin.   Komodo   will   ensure   Stage   1   completes   successfully   before   moving   to   Stage   2

15

.   This

effectively bundles the two steps so that end-users (or automated triggers) can execute one Procedure

and   accomplish   both   tasks.   It’s   a   more  declarative/orchestrated  approach,   living   inside   Komodo’s

environment.

Ease   of   Integration   with   TypeScript   &   Automation:  This   method   is  integrated   into   Komodo’s

ecosystem rather than an external script. You might still write some TypeScript (for the Pangolin call) as

an  Action  within the procedure, but that code is managed in Komodo’s UI and stored in Komodo’s

database. If your goal is to have everything automated via code, you can trigger the Procedure via

Komodo’s API or webhooks. From an automation perspective, it’s one API call (like “run procedure X”) to

deploy and register, which is convenient. It’s not as flexible as writing your own TS script from scratch,

but   Komodo’s   design   makes   it   pretty   straightforward   to   integrate   –   especially   if   you   already   use

Komodo’s UI or GitOps sync. In TypeScript terms, you might not be writing a full external program, but

the Action in Stage 2 is indeed TypeScript, so you still have the power of TS for the Pangolin API call if

needed

16

. Overall, it’s a middle-ground: less coding overall (because Komodo handles the deploy step

with a built-in action), but also less custom-tailored than Approach 2. It fits well if you want a low-code

solution that’s still programmable.

Error Handling & Observability: Komodo’s Procedure gives you a clear view of each stage’s outcome. If

the stack deployment fails (Stage 1), the Procedure will stop and you’ll see that failure in the Komodo UI

(and any configured alerts). This prevents moving on to Pangolin registration if the container didn’t

come up. If the custom Pangolin registration step (Stage 2) fails, that too is logged and marked as

failed, and the Procedure overall is marked failed. However, handling errors within the Pangolin step

may   require   writing   defensive   code   in   the   Action   –   e.g.   catching   an   error   from   Pangolin’s   API   and

deciding   to   retry   or   abort   gracefully.   You   could   even   use   the   TS   Action   to   roll   back   the   stack   if

registration   fails   (by   calling   Komodo’s   API   to   remove   the   stack),   though   that   adds   complexity.

Observability is quite good: all logs from the Action (like API responses or debug info) can be printed to

Komodo’s console and viewed in the UI. Each execution of the Procedure is recorded, so you have a

history of deployments and registrations in one place. What you sacrifice is some flexibility in error

handling logic (since the Procedure is mostly linear). But for most cases (where you just need “deploy,

then register”), the transactional nature of a Procedure is sufficient and nicely visible.

Security & Secret Management: Since the Procedure runs entirely within Komodo’s domain, you can

take   advantage   of   Komodo’s   secret   management   for   passing   the   Pangolin   API   token.   A   common

pattern would be: store the Pangolin token as a secret variable in Komodo Core (or as a periphery

secret on the agent if you want it tied to a specific host)

17

5

. In the Procedure’s Action script (the

Pangolin registration step), you can inject this token. One way is to define an environment variable for
the Action execution like  PANGOLIN_TOKEN=[[MY_PANGOLIN_TOKEN_SECRET]] . Then in the TS code,
read   it   via   Deno.env.get('PANGOLIN_TOKEN')   or   similar   (Komodo’s   Action   uses   Deno,   which

supports secure env access). This keeps the secret out of code and logs. Because the token lives in

Komodo, it’s protected by Komodo’s access controls (only admins can modify secrets, and values aren’t

shown)

4

. The Pangolin API key should still be scoped to limit its powers

13

. The benefit here is you’re

not   spreading   the   secret   to   external   systems   –   it’s   only   in   Komodo   and   Pangolin.   Also,   if   using   a

6

periphery agent secret, the token doesn’t even traverse the network: Komodo’s core doesn’t see it, only

the agent on the Pangolin host does

5

. Overall, Approach 3 can be very secure with the proper secret

configuration.

Flexibility & Reusability:  The Procedure approach is  highly reusable within the Komodo context.

Once you create a procedure (say “Deploy and Expose Service”), you or your team can run it any time,

and it will do the same steps reliably. If it’s parameterized by naming conventions or tags, you could use

one procedure to handle multiple services. For example, Komodo supports wildcard patterns for batch

actions

9

  – you could have the procedure’s deploy step target a family of stacks (like all stacks in a

project). However, this might be more static than writing a loop in code. You may end up creating a

separate procedure per service group or per environment to tailor the Pangolin settings (e.g. different

domain   names   per   environment).   Reusability   across   multiple   environments   is   possible:   you   might

define identical procedures in each Komodo instance (dev, staging, prod) if you run separate Komodo

servers, or one procedure that deploys to different servers based on input. Komodo doesn’t currently

allow arbitrary user input into procedures at runtime, so you rely on pre-defined configurations. In

practice, you might maintain the procedure definition as code (Komodo allows exporting resources as

TOML) and deploy that to each environment’s Komodo via GitOps

18

. This is a bit heavy, but it ensures

consistency. In summary, for teams that live in the Komodo UI, this approach is very convenient and

reusable; for those who prefer code, it’s another config to manage (less flexible than pure code, but

more structured).

Maintenance & Scalability: Maintaining a Komodo procedure is mostly about updating the workflow

when   necessary.   If   your   deployment   process   changes   (say   Komodo   gets   a   new   deploy   feature   or

Pangolin adds a new required field), you’d edit the Procedure: possibly updating the Action’s TS code or

the execution parameters. This can be done in the Komodo UI or via editing the TOML in a Git repo if

using   Resource   Sync.   It’s   a   bit   more   of   a   configuration   management   task   than   a   coding   task.   One

potential downside is that if you have many procedures (e.g. one per service or per team), updating all

of them could be effort – although you could script that with Komodo’s API if needed. In terms of

scalability,   Komodo’s   procedure   can   orchestrate   multiple   actions   in   parallel,   which   is   a   plus   for

deploying many services at once. You could, for instance, have a stage that registers multiple services in

Pangolin   concurrently   if   they   are   independent.   The   sequential   stage   design   ensures   that   you   don’t

overload Pangolin or Komodo unintentionally – you can control how much runs at once. The scaling

limit will be what Komodo and Pangolin can handle, but those are quite robust for moderate loads. One

consideration:   procedures   reside   in   the   Komodo   service,   so   if   Komodo   is   down   or   busy,   your

deployment+expose workflow is unavailable. An external script (Approach 2) might be decoupled and

run from elsewhere. But assuming Komodo is your central orchestration tool, having the procedure

defined there is logical. Maintenance is simplified by the fact that  the process is documented and

versioned in Komodo, not scattered across scripts. It aligns with a GitOps philosophy if you export the

config  –  you  treat  the  deployment  workflow  as  declarative  config,  which  can  be  very  clean  as  your

infrastructure scales.

Recommendations: Choosing the Right Approach

Each approach has its merits, and the best choice can depend on your team’s skills and the environment

in which you’re operating. Here are some guidelines for when to use each:

•

Use   Approach   1   (Post-Deploy   Script)  if   you   need   a  quick,   ad-hoc   solution  or   have   a   very

simple environment. This works well for a one-off integration or a scenario where you don’t want

to invest in coding. For example, if you’ve already deployed a service via Komodo and just need

to call Pangolin’s API once, writing a small shell script might be fastest. It’s also viable when you

7

cannot modify the Komodo instance much (no custom actions) – e.g., in a restricted environment

where you can only deploy stacks and run basic scripts. However, for long-term and multiple

services, this method gets harder to manage. Treat it as a simple glue for straightforward cases

or prototyping.

•

Use Approach 2 (TypeScript SDK & Actions) if you desire a robust, code-driven workflow and

have the resources to maintain a script or application. This is ideal for teams who already employ

TypeScript   for   infrastructure   automation   or   CI/CD.   For   instance,   in   a   continuous   deployment

pipeline,   you   can   incorporate   this   script   to   automatically   deploy   a   new   service   version   and

update Pangolin. It offers the best control over error handling and logic. Choose this when you

need to integrate with other systems as well – e.g., update a database or call another API as part

of deployment – since it’s easy to extend the script. Also, if you plan to open-source or share your

deployment tool, a TypeScript CLI could be more accessible to others than a Komodo-specific

procedure. In short, Approach 2 is best for maximum flexibility and integration into existing

dev   workflows.   Just   ensure   you   are   comfortable   managing   API   keys   and   that   you   test   the

automation thoroughly.

•

Use   Approach   3   (Komodo   Procedure)  if   you   want   a  streamlined,   “low-code”   pipeline

maintained largely within Komodo’s interface. This is great for operator-centric scenarios: for
example, if you have an ops team that prefers using Komodo’s GUI to trigger deployments, a

one-click procedure that does everything is very attractive. It’s also a good choice when you

foresee using the same deployment+registration pattern frequently – you set it up once and

anyone can reuse it. If you value having the deployment audit trail and configuration in one

place (Komodo’s database) rather than spread across external scripts, this approach delivers that

cohesion. Additionally, if you plan to leverage Komodo’s webhook triggers (e.g., auto-deploy on

git push)

19

, a procedure can be the target of a webhook, thereby achieving a full GitOps style

automation with Pangolin steps included. Go with Approach 3 when consistency, security, and

ease of use by multiple team members  is a priority, and when you’re okay with the slight

rigidity of a predefined workflow. It may require a bit more upfront setup in Komodo, but once in

place, it’s very scalable for routine use.

In many cases, you might even combine approaches. For example, you could use a Komodo Procedure

(Approach 3) and trigger it via an external TS script (Approach 2) for the best of both – the heavy lifting

defined in Komodo, but orchestrated as part of a larger code-driven pipeline. However, if we consider

each   in   isolation,   the   recommendations   above   should   help   you   pick   the   method   that   fits   your

circumstances:

•

Small-scale or exploratory deployment: Approach 1 for simplicity.

•

CI-integrated, code-centric deployment: Approach 2 for control and power.

•

Team-oriented, repeatable operations: Approach 3 for consistency and safety.

By evaluating these dimensions – integration, error handling, security, flexibility, and maintainability –

you can select the approach that aligns with your needs. In summary,  Approach 2  often appeals to

developers looking for a programmable solution, Approach 3 appeals to DevOps/SRE folks looking for a

reliable push-button workflow, and  Approach 1 is there for quick fixes or very simple use cases. Each

can achieve the end goal of  deploying Compose stacks via Komodo and exposing them through

Pangolin, but with trade-offs in effort and complexity as outlined above.

Sources:

•

Komodo Documentation – Resource Types (Procedures, Actions, Repo, etc.)

20

3

8

•

Komodo Documentation – Using Variables and Secrets

4

5

•

Pangolin Release Notes – Integration API availability and usage

12

•

Community Discussion – Interest in Komodo–Pangolin integration

1

1

6

8

12

13

19

Pangolin 1.4.0: Auto-provisioning IdP users and integration API now available for

everyone! : r/selfhosted

https://www.reddit.com/r/selfhosted/comments/1klp8sq/pangolin_140_autoprovisioning_idp_users_and/

2

3

14

15

16

20

Resources | Komodo

https://komo.do/docs/resources

4

5

7

17

Variables and Secrets | Komodo

https://komo.do/docs/resources/variables

9

10

11

18

Procedures and Actions | Komodo

https://komo.do/docs/resources/procedures

9



---

### `hosting-litellm-pangolin-public-vs-private-access-models.md` — 01-selfhosting

Hosting LiteLLM on Pangolin: Public vs. Private

Access Models

Public Access via Pangolin Domain (Open Endpoint)

In this model, you expose the LiteLLM server over the internet through Pangolin’s reverse proxy and

domain routing. Pangolin will handle HTTPS termination (via Let’s Encrypt) and route requests to your

LiteLLM instance running on the VPS. This allows third-party integrations (e.g. Hugging Face tools or

remote apps) to call your LiteLLM endpoint without any VPN client. Key steps and configurations:

•

Domain   &   DNS   Setup:  Point   a   domain   or   subdomain   to   the   Pangolin   server.   If   self-hosting
Pangolin,   configure   a   wildcard   DNS   (e.g.   *.example.com )   to   your   VPS’s   IP

.   If   using

1

Pangolin   Cloud,   you   can   skip   custom   DNS   by   using   Pangolin’s   provided   domains   (like
*.hostlocal.app   or   *.tunneled.to )

.   Ensure   TCP   port  80  (for   Let’s   Encrypt   HTTP

2

validation)  and  443  (for  HTTPS  traffic)   are   open   on   the   VPS

3

  –   Pangolin   will   automatically

obtain and renew TLS certificates for your domain.

•

Add Pangolin Resource (Reverse Proxy): In the Pangolin dashboard, navigate to Resources >

Add Resource
. Provide a descriptive Name for the service and select Type: HTTP/HTTPS. Set
the  Domain  to your chosen hostname (e.g.   litellm.example.com ) which users will access

4

5

. Specify the Target as the LiteLLM service’s address on the private site – this is the IP/port
where  LiteLLM  runs  on  your  VPS  (for  example,   127.0.0.1:4000   if  LiteLLM  listens  on  port

4000)

5

. Pangolin’s tunnel will route incoming domain traffic to this target.

•

TLS & Reverse Proxy Configuration:  Pangolin uses Traefik under the hood to proxy HTTP(S)

traffic. When you added the resource with a domain, Pangolin automatically set up a secure

HTTPS endpoint. Traefik listens on port 443 with a Let’s Encrypt certificate resolver
, so all
traffic to  https://litellm.example.com  will be encrypted. No manual TLS setup is needed

6

beyond   providing   your   email/domain   during   Pangolin   install   (the   installer   handles   certificate

issuance

7

).

•

Access Control (Public Endpoint):  By default, Pangolin is an identity-aware proxy, meaning it

can require login or PIN for access. Since this endpoint is intended for programmatic use by third

parties,   you   likely   want   it   open   without   interactive   auth.   Pangolin   supports  Allow   Rules  to

bypass authentication

8

. In the Access Control settings, create an allow-rule for this resource

(or set the resource’s access to “public”) so that requests skip any login/PIN requirements

8

.

This effectively makes the domain publicly accessible to anyone (or anyone who knows a secret

API key your LiteLLM might require). Make sure to secure the LiteLLM API itself (e.g. via an API

token or key) if you want to restrict usage, because with public access the endpoint is reachable

by the internet at large.

Configuration Example: For instance, suppose your Pangolin site is named “VPS-Site” and LiteLLM runs

on port 4000 on that VPS. You could configure a resource as follows:

•

Domain: api.example.com  (CNAME or A record pointed to Pangolin’s IP/domain)

1

•

•

Resource Type: HTTP (Pangolin proxies via TLS on port 443)
Target: 127.0.0.1:4000  on VPS-Site (LiteLLM’s local endpoint)

5

•

Access Control: Allow (no auth required, using a rule to bypass Pangolin login)

8

Once set up, external clients can reach the LiteLLM server at   https://api.example.com   without

needing any VPN or special client. Pangolin’s reverse proxy will forward the HTTPS requests through its

tunnel to the LiteLLM service on the VPS.

Public Access Use Cases:  This approach is ideal when you need to integrate LiteLLM with external

services or provide an API endpoint for customers/partners. It prioritizes ease of access – users just hit

a standard HTTPS URL – and Pangolin still provides security through TLS and optional identity checks.

However, since the service is exposed to the internet, you should harden it (use API keys or rate limiting

in LiteLLM) to prevent abuse. This model is slightly less restrictive than the VPN-only approach, trading a

bit of attack surface for simplicity of access.

Private Access via Pangolin Olm VPN (Restricted Endpoint)

In this model, the LiteLLM service is not exposed on any public domain. Instead, it’s accessible only to

authenticated   team   members   through   Pangolin’s   Olm   VPN   client.   Olm   (Pangolin’s   WireGuard-based

client)   creates   a   secure   tunnel   into   your   Pangolin   network,   so   only   users   with   the   proper   Olm

credentials can reach LiteLLM. The service remains invisible to the open internet, greatly enhancing

security

9

. To set this up, you will use Site Resources (internal resources) in Pangolin:

•

Enable Client Access on the Site: Ensure your Pangolin site (the VPS) accepts client connections.
When running the Pangolin agent ( newt ) on the VPS, use the   --accept-clients   flag (or

enable the equivalent setting in Pangolin)

9

. In this mode, Newt runs entirely in userspace

without   creating   a   local   network   interface,   and   Pangolin   will   route   client   traffic   for   specific

resources you define. This means the VPS doesn’t act as a full VPN gateway; it only exposes the

ports you explicitly configure for Olm clients. (No root privileges or OS-level networking changes

are needed on the VPS in this mode

9

.)

•

Define a Site Resource for LiteLLM: In the Pangolin dashboard, go to Resources and switch to

the Site Resources view

10

. Click Add Resource and choose TCP (since LiteLLM’s API runs over

HTTP/TCP). Set a  Local Port  that Olm clients will use to connect (this can be the same as the
LiteLLM port or an arbitrary port not in use – e.g.  4000  for clarity)
. Then specify the Target
address  as the LiteLLM service’s local address on the site (for example,   127.0.0.1:4000   if

11

LiteLLM is listening on localhost:4000)

12

. This tells Pangolin to forward traffic from the site’s

VPN interface (on that local port) to the actual service. Save the resource configuration.

•

Client Connection with Olm: Next, add a Pangolin  Client (in the Pangolin UI under  Clients) to

generate   an   Olm   ID   and   secret   for   each   team   member   or   system   that   needs   access.   Team

members   will   install   the   Olm   client   and   configure   it   with   the   provided  ID,  secret,   and   the
. When an authorized user runs  olm --
Pangolin endpoint (your Pangolin server’s URL)
id   <client-id>   --secret   <secret>   --endpoint   https://<pangolin-server>   on

13

14

their machine

15

, Olm registers and establishes a WireGuard tunnel to the Pangolin network.

Once   the   Olm   VPN   is   connected,   the   user’s   system   is   virtually   inside   the   Pangolin   private

network.

•

Access LiteLLM via the VPN: When connected via Olm, the user can reach the LiteLLM service

using   the  site’s   virtual   IP   and   the   configured   port.   Pangolin   assigns   each   site   a   virtual   IP

2

(visible in the Pangolin dashboard, often in a range like 100.64.x.x or 100.90.x.x) for the VPN
tunnel. For example, if your site’s VPN IP is   100.90.128.0   and you mapped LiteLLM to port
4000 ,   the   user   would   access   http://100.90.128.0:4000   to   hit   the   LiteLLM   API

16

.

Pangolin will route that request through the WireGuard tunnel directly to the LiteLLM service on

the VPS. Only clients who have connected with a valid Olm configuration (ID/secret) can reach

this address – anyone not on the Pangolin VPN cannot even see or connect to the service

9

.

No public DNS or TLS setup is required here, since the service is not exposed via a public domain. All

traffic  is  end-to-end  encrypted  at  the  WireGuard  layer.  (If  needed,  you  could  still  run  HTTPS  on  the

LiteLLM service itself for double encryption, but it’s typically not necessary because the VPN provides

secure transport.)

Configuration Example:  Suppose LiteLLM runs on port 4000. In  Site Resources  you add:  Type:  TCP,
Port:  4000,  Target: 127.0.0.1:4000
. After connecting with Olm, a team member can use the
LiteLLM API by targeting the site’s IP (e.g.   100.90.128.0:4000 ) in their HTTP client. The Pangolin

11

newt agent will forward that to the real localhost:4000 on the VPS. This approach is  ideal for secure

internal access without exposing services to the public internet

9

17

.

Private   Access   Use   Cases:  This   VPN-gated   model   is   suited   for  internal   tools   and   sensitive
applications. It provides strong security – the LiteLLM server is effectively air-gapped from the internet,

accessible only to authenticated VPN clients. Use this when the LLM service is for your team or company

only,   or   when   compliance/security   policies   forbid   exposing   an   endpoint   publicly.   The   trade-off   is

convenience:   each   user   must   run   the   Olm   client   (or   be   on   the   Pangolin   network)   to   connect.   This

method isn’t feasible for third-party services that can’t run a VPN client, but it’s perfect for developers

and team members who can run Olm on their laptops or servers to gain access.

Comparison of Public vs. Private Models

Security: The private (Olm) model offers the highest security since the LiteLLM endpoint is invisible to

the internet – only users with VPN credentials can reach it

9

. This greatly reduces attack surface. The

public domain model is less restrictive: anyone can reach the endpoint URL, so you rely on application-

level security (API keys, auth tokens, or Pangolin’s access rules) to protect it. Pangolin can still secure the

public model with SSL and optional login/SSO, but fundamentally it’s reachable from anywhere, which

requires more vigilance (e.g. monitoring and rate-limiting) compared to a VPN-restricted service.

Simplicity & User Convenience: The public access model is simpler for clients/integrations – no special

software is needed to connect, just standard HTTPS requests. It’s ideal for integrating with external

tools or services that expect a normal web endpoint. Domain and TLS setup is mostly automated by

Pangolin (especially with wildcard DNS or Pangolin’s cloud domains), so configuration is straightforward

5

3

. The private model, on the other hand, requires extra steps for each user (installing/configuring

the Olm VPN client and connecting before use). This added complexity means it’s best for known users

who can be instructed to use the VPN. In summary,  Olm is not necessary  when you want an easily

accessible public API, but  Olm becomes essential  when you need to restrict access to trusted users

only – it’s the difference between an open service and one that lives behind a secure VPN barrier.

Performance:  Both   methods   utilize   Pangolin’s   efficient   WireGuard   tunneling,   but   there   are   minor

differences. With public access, the client’s requests come in over HTTPS to the Pangolin server (or

cloud   node)   and   then   traverse   the   WireGuard   tunnel   to   the   site.   With   Olm,   the   client   itself   is   on

WireGuard  –  effectively,  traffic  goes  through  the   VPN   tunnel   directly.   In  practice,   the  overhead   and

latency are comparable. Olm’s tunnel might add a tiny constant latency (due to encryption/decryption

3

on the client side), whereas the public model adds latency on Pangolin’s reverse proxy handling. These

differences   are   usually   negligible   –   WireGuard   is   very   fast,   and   Pangolin’s   proxy   is   optimized   for

performance. If using Pangolin Cloud, the public model can even route users to the nearest Pangolin

node for improved latency, whereas Olm may route you through a specific region – but unless your

users are globally distributed, this is a small factor. For most use cases, both approaches can handle

real-time LLM traffic well, and throughput is more constrained by the LLM processing speed or network

bandwidth than by Pangolin itself.

Use Cases and When to Use Which: Use the public domain approach when you need to expose an

API endpoint for integration with external services, webhooks, or client applications that cannot easily

use a VPN. For example, if you want to plug your LiteLLM service into a cloud workflow (Hugging Face

pipeline, external web app, etc.), a public HTTPS URL is the way to go – Olm isn’t feasible in those

scenarios. On the other hand, choose the private/Olm approach for in-house or development setups

where security trumps convenience: e.g. an internal LLM tool for your team, or a staging server that

only developers should access. In those cases, running the Olm client to access the service is a non-

issue for users, and you avoid exposing any endpoint to the internet. It’s also possible to start private

and later move to public if needed – Pangolin is flexible. You could even mix models: keep the service

private for most users, but create a public resource for specific purposes (with strict rules or limited

scope) when necessary. The key takeaway is that Olm is necessary only when you deliberately want

to keep a service private to your Pangolin network, and it’s overkill if your goal is to offer a public-

facing service. Pangolin’s domain routing gives you the option to go either way: open and accessible, or

closed and VPN-gated, depending on your needs for security vs. accessibility.

References:  The   configurations   above   are   based   on   Pangolin’s   official   documentation   and   usage

guides. For instance, Pangolin’s docs outline how to add an HTTPS  Resource  with a custom domain,

pointing to a private service’s IP:port and controlling access

18

. Pangolin will automate TLS via Let’s

Encrypt as long as DNS is configured and ports 80/443 are open

3

. For the private model, Pangolin’s

Client Resources  feature is designed specifically to “expose internal services to your remote clients

securely” over the Olm VPN

19

, with no public proxying. The internal resource method is highlighted as

ideal for “services without exposing them to the public internet”

9

  – only Olm-connected clients can

reach the defined port

17

. By comparing these two setups, you can choose the appropriate balance of

security and convenience for hosting your LiteLLM server.

1

2

Domains - Pangolin Docs

https://docs.pangolin.net/manage/domains

3

DNS & Networking - Pangolin Docs

https://docs.pangolin.net/self-host/dns-and-networking

4

5

7

18

Pangolin (CE) | DigitalOcean Documentation

https://docs.digitalocean.com/products/marketplace/catalog/pangolin-ce/

6

Raw TCP & UDP - Pangolin Docs

https://docs.pangolin.net/manage/resources/tcp-udp-resources

8

Rules - Pangolin Docs

https://docs.pangolin.net/manage/access-control/rules

9

10

11

12

16

17

19

Client Resources - Pangolin Docs

https://docs.pangolin.net/manage/resources/client-resources

13

14

15

Configure Client - Pangolin Docs

https://docs.pangolin.net/manage/clients/configure-client

4



---

## Original Sources

- `01-celtic-language-ai-resources/` (README.md, bilingual-ml-architecture.md, irish-nlp-resources.md, scottish-gaelic-resources.md, unified-model-comparison.md, welsh-resources.md)
- `01-irish-edtech-platform/` (README.md, ai-ml-pipeline.md, data-architecture.md, frontend-stack.md, subject-implementations.md)
- `01-selfhosting/` (bunchloch.md, comparing-approaches-pangolin-registration-komodo-deployment.md, hosting-litellm-pangolin-public-vs-private-access-models.md)
