# Meaisínfhoghlaim — Machine Learning Research Index

Consolidated AI/ML research for Celtic language education, model serving, and agent systems.

## Consolidated Reference Documents

| Document | Covers | Source Files |
|----------|--------|-------------|
| **[fine-tuning-reference.md](fine-tuning-reference.md)** | LLM fine-tuning: Unsloth, LoRA/QLoRA, QAT, GRPO, datasets, Celtic GPU strategy, phone deployment | `fine-tuning/` (12 files) |
| **[celtic/CELTIC_LANGUAGES_AI_RESOURCES.md](celtic/CELTIC_LANGUAGES_AI_RESOURCES.md)** | Irish, Welsh, Scottish Gaelic, Manx: models, datasets, ASR, TTS, translation, benchmarks | `celtic/` (21 files) |
| **[celtic/irish_bilingual_dataset_research.md](celtic/irish_bilingual_dataset_research.md)** | Gaois Research Group: scraping Irish-English bilingual data (API, GitHub, crawl4ai) | Standalone (1,173 lines) |
| **[model-serving-guide.md](model-serving-guide.md)** | GGUF, llama.cpp, MLX-LM, Llama-Swap, LiteLLM, quantization, Apple Silicon reference | `models/` (17 files) |
| **[document-processing-reference.md](document-processing-reference.md)** | OCR, VLM, Docling, ColPali, DeepSeek-OCR, Gaelic heritage digitization | `ocr/` (9), `colpali/` (3) |
| **[agent-patterns-reference.md](agent-patterns-reference.md)** | Google ADK, MCP, agentic tutoring, browser automation, knowledge memory, Gemini API | `agents/` (11) + top-level files |
| **[ai-ml-systems-consolidated.md](ai-ml-systems-consolidated.md)** | Comprehensive AI/ML architecture: compute tiers, BAML, Cognee vs CocoIndex, doc processing, LiteLLM | Existing (1,798+ lines) |

## Topical Quick Links

### Fine-Tuning
- [Fine-Tuning Reference](fine-tuning-reference.md) — Unsloth, LoRA, QLoRA, QAT, GRPO, Celtic GPU guide

### Celtic Languages
- [Celtic Language AI Resources](celtic/CELTIC_LANGUAGES_AI_RESOURCES.md) — All 4 languages, models, datasets
- [Irish Bilingual Dataset Research](celtic/irish_bilingual_dataset_research.md) — Gaois scraping guide

### Model Serving & Inference
- [Model Serving Guide](model-serving-guide.md) — GGUF, llama.cpp, MLX-LM, Llama-Swap, LiteLLM

### Document Processing & OCR
- [Document Processing Reference](document-processing-reference.md) — VLMs, OCR, ColPali, heritage digitization

### Agent Systems
- [Agent Patterns Reference](agent-patterns-reference.md) — ADK, MCP, tutoring, browser automation

### Architecture & Infrastructure
- [AI/ML Systems Consolidated](ai-ml-systems-consolidated.md) — Full architecture blueprint
- [AI Compute Allocation Strategy](ai-compute-allocation-strategy.md) — Tiered compute model

### Observability
- [Langfuse Guide](langfuse-guide.md) — LLM observability (119K)
- [MLflow LLM Guide](mlflow-llm-guide.md) — ML lifecycle management
- [LiteLLM Comprehensive Guide](litellm-comprehensive-guide.md) — Multi-provider gateway

### Other
- [HuggingFace Design Patterns](huggingface-design-patterns-analysis.md) — HF API patterns
- [Neuro-Symbolic Translation](Neuro-Symbolic%20Translation%20Model%20Training.md) — Translation model training
- [Federated RAG Tutorial](Federated%20RAG%20Tutorial_%20Build%20Privacy-Preserving%20LLM%20Systems%20in%20Python%20%E2%AC%A9OpenMined.md) — Privacy-preserving RAG

## Directory Structure

```
docs/meaisínfhoghlaim/
├── INDEX.md                              ← You are here
├── fine-tuning-reference.md              ← MEGA-MERGE: All Unsloth/ft content
├── model-serving-guide.md                ← MEGA-MERGE: GGUF, MLX, llama.cpp
├── document-processing-reference.md      ← MEGA-MERGE: OCR, VLM, ColPali
├── agent-patterns-reference.md           ← MEGA-MERGE: ADK, MCP, agents
├── ai-ml-systems-consolidated.md         ← Legacy: comprehensive architecture
├── celtic/
│   ├── CELTIC_LANGUAGES_AI_RESOURCES.md  ← MEGA-MERGE: All Celtic AI resources
│   ├── irish_bilingual_dataset_research.md ← Preserved: Gaois scraping guide
│   └── *.md                              ← Stubs → CELTIC_LANGUAGES_AI_RESOURCES.md
├── fine-tuning/*.md                      ← Stubs → fine-tuning-reference.md
├── models/*.md                           ← Stubs → model-serving-guide.md
├── ocr/*.md                              ← Stubs → document-processing-reference.md
├── agents/*.md                           ← Stubs → agent-patterns-reference.md
├── colpali/*.md                          ← Stubs → document-processing-reference.md
├── audio/*.md                            ← Stubs
└── [top-level research files]            ← Preserved individual docs
```

## Related Skills

Tool-specific documentation lives in `.agents/skills/`:

| Tool | Skill | Purpose |
|------|-------|---------|
| Agno | `agno/` | Multi-agent orchestration |
| Dagster | `dagster/` | Data pipeline orchestration |
| DLT | `dlt/` | Data load tool pipelines |
| HuggingFace | `model-trainer/` | Cloud GPU training |
| LiteLLM | `litellm/` | LLM gateway |
| MLflow | `mlflow/` | ML lifecycle |
| Unsloth | `unsloth/` | Efficient fine-tuning |
| LanceDB | `lancedb/` | Vector database |
| Cognee | `cognee/` | Knowledge graph memory |
