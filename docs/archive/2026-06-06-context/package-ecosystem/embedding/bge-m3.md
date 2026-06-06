# BGE-M3 — Multilingual Embedding Model

## Overview

BGE-M3 (BAAI General Embedding — Multilingual, Multi-Granularity, Multi-Function) is a 1024-dimensional embedding model by BAAI that supports 100+ languages, multiple granularities (sentence to document), and both dense and sparse retrieval. It is the primary embedding model for the curriculum semantic search system.

## Why This Matters for Kings' College Galway

The curriculum platform needs embeddings that work across Irish and English text with equal accuracy. BGE-M3's multilingual training (100+ languages including Irish via Latin-script transfer) and its dual dense+sparse retrieval architecture make it ideal for curriculum search: dense vectors capture semantic similarity ("calculus" ≈ "differentiation"), and sparse vectors capture exact terminology matching ("teorim Phíotagarásach" ≈ "Pythagoras' theorem"). The 1024d embeddings provide a strong accuracy/efficiency tradeoff for the million-document curriculum corpus.

## Key Features

- **100+ languages** — Multilingual embedding with strong cross-lingual transfer
- **1024 dimensions** — Efficient storage with high retrieval accuracy
- **Multi-granularity** — Sentence, paragraph, and document-level embeddings
- **Dense + sparse** — Hybrid retrieval with both semantic and lexical matching
- **BGE family** — Part of BAAI's flagship embedding model series

## Installation

```bash
uv add sentence-transformers
# Model downloads automatically on first use:
# from sentence_transformers import SentenceTransformer
# model = SentenceTransformer("BAAI/bge-m3")
```

## Integration with Our Stack

BGE-M3 is served locally via HuggingFace passthrough in the LiteLLM gateway's `embedding-curriculum` alias. Embeddings are stored in LanceDB and Qdrant. The model is cached in `stedding/huggingface/hub/` (4.3 GB). Dagster assets use it for curriculum document indexing.

## Upstream

- **Model**: <https://huggingface.co/BAAI/bge-m3>
- **Paper**: <https://arxiv.org/abs/2402.03216>
- **Latest**: BGE-M3 v1 (2024) — flagship multilingual embedding model from BAAI

## Screenshot

BGE-M3 is a model, not an application. Usage is via Python: `model.encode(["text in Irish", "text in English"])` returns 1024d numpy arrays. The embedding quality is evaluated by RAGAS context precision/recall metrics. LanceDB's data viewer shows vector collections with embedding dimensions.
