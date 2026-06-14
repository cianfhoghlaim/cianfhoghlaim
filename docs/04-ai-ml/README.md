---
title: "AI/ML Documentation"
domain: ai_ml
date: 2026-06-06
migration_source: docs/bunchloch/meaisínfhoghlaim + docs/bunchloch/teanga
ccc_query_hints: ["ai/ml-documentation"]
type: index
description: "Canonical AI/ML documentation for the Cianfhoghlaim platform covering fine-tuning, OCR/HTR, RAG evaluation, knowledge graphs, vector embeddings, Celtic language AI, and ML pipelines."
truth: partial

---
# AI/ML Documentation

Consolidated from 394 source files across `docs/bunchloch/meaisínfhoghlaim` (99) and `docs/bunchloch/teanga` (295) on 2026-06-06.

## Canonical Documents

| Document | Description | Source Files |
|----------|-------------|-------------|
| **[OCR, HTR & Document Intelligence](ocr-htr.md)** | OCR, HTR, VLM document processing, ColPali, DeepSeek-OCR, Tesseract, Irish handwriting, Gaelic script finetuning | 34 |
| **[LLM Fine-Tuning Guide](fine-tuning-guide.md)** | Unsloth, LoRA/QLoRA, QAT, GRPO/DPO, GGUF, TRL, HuggingFace Skills, model training for Celtic languages | 85 |
| **[RAG & Evaluation](rag-evaluation.md)** | RAG systems, RAGAS metrics, faithfulness, answer relevancy, federated RAG, prompt optimization | 12 |
| **[Celtic Language AI](celtic-language-ai.md)** | Irish/Gaelic language AI, Welsh, Scottish Gaelic, GaBERT, Gaois, Dúchas, Téarma, bilingual NLP | 205 |
| **[Knowledge Graphs & Graph Memory](knowledge-graphs.md)** | Knowledge graphs, Graphiti, Cognee, Memgraph, FalkorDB, graph-based agent memory, entity extraction | 11 |
| **[ML Pipelines & Observability](ml-pipelines.md)** | MLflow, Langfuse, LiteLLM, experiment tracking, model registry, prompt management, observability | 3 |
| **[Vector Embeddings & Semantic Search](vector-embeddings.md)** | Vector databases, LanceDB, Qdrant, embeddings, semantic search, DuckLake, Iceberg | 11 |

## Migration Summary

- **Total source files:** 394 (99 meaisínfhoghlaim + 295 teanga)
- **Canonical files produced:** 7
- **Source archive:** docs/archive/2026-06-06-meaisinfhoghlaim/ and docs/archive/2026-06-06-teanga/
- **CCC index hint:** Use `ccc search "AI model training" --paths "docs/04-ai-ml/*"`
