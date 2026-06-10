# GaBERT — Irish Language BERT Embedding Model

## Overview

GaBERT is a BERT-base model pre-trained specifically on Irish language text by Dublin City University (DCU) NLP group. It provides 768-dimensional embeddings optimised for Irish Gaelic, capturing the language's unique morphology (initial mutations, slender/broad consonant distinctions, VSO word order) that multilingual models often miss.

## Why This Matters for Kings' College Galway

Bilingual curriculum content requires embeddings that understand Irish language semantics natively — not just as a "Latin script" afterthought. When a student searches "difreáil" (differentiation) in Irish, GaBERT correctly associates it with calculus concepts, whereas English-trained models often miss this due to the word's different surface form. GaBERT is used alongside BGE-M3 in a two-stage retrieval pipeline: GaBERT for Irish-language queries, BGE-M3 for English and cross-lingual. This bilingual embedding strategy ensures Irish-medium students get the same search quality as English-medium students.

## Key Features

- **Irish-native** — Trained on Irish text corpora (blogs, news, government documents)
- **768 dimensions** — BERT-base architecture, compatible with standard tooling
- **Morphology-aware** — Handles Irish initial mutations (séimhiú, urú)
- **DCU NLP** — Developed by Ireland's leading NLP research group
- **WordPiece tokenization** — Irish-optimised vocabulary

## Installation

```bash
uv add transformers
# Model: DCU-NLP/bert-base-irish-cased-v1
```

## Integration with Our Stack

GaBERT is served locally via HuggingFace passthrough. The LiteLLM gateway exposes it as a custom embedding route for Irish-language queries. The model is cached in `stedding/huggingface/hub/` (~483 MB). Dagster assets use GaBERT for Irish-language curriculum indexing.

## Upstream

- **Model**: <https://huggingface.co/DCU-NLP/bert-base-irish-cased-v1>
- **Paper**: DCU NLP group — Irish BERT pre-training
- **Latest**: v1 — primary Irish BERT model used in Irish NLP research

## Screenshot

GaBERT is a model accessed via HuggingFace Transformers: `AutoModel.from_pretrained("DCU-NLP/bert-base-irish-cased-v1")`. Embedding quality is evaluated on Irish-language retrieval benchmarks. The model card on HuggingFace shows training data sources, evaluation metrics, and usage examples in Irish.
