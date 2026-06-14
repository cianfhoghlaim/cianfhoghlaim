---
title: 'ColPali — Visual Late-Interaction Document Retrieval'
domain: 'agents'
status: 'stable'
description: 'ColPali (Contextualized Late Interaction over PaliGemma) is a vision-language model for document retrieval that operates directly on document images rather than extracted text. It uses late interaction — comparing query and document patch embeddings at a fine-grained level — to r'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/colpali.md
ccc_query_hints:
  - colpali — visual late-interaction docume
truth: partial

---

# ColPali — Visual Late-Interaction Document Retrieval

## Overview

ColPali (Contextualized Late Interaction over PaliGemma) is a vision-language model for document retrieval that operates directly on document images rather than extracted text. It uses late interaction — comparing query and document patch embeddings at a fine-grained level — to retrieve relevant pages from scanned documents without OCR pre-processing.

## Why This Matters for Kings' College Galway

Historical Leaving Cert exam papers (pre-2010) are scanned images with complex layouts: mathematical equations, diagrams, bilingual Irish/English text, and handwritten annotations. Traditional text-based retrieval requires OCR first, and OCR errors cascade into retrieval failures. ColPali bypasses OCR entirely — it embeds the visual appearance of each page and retrieves based on visual-semantic similarity. This means a query for "trigonometric identity proof" finds the correct exam paper page even if the OCR mangled the equation, because ColPali matches the visual structure of equations, not the extracted text.

## Key Features

- **Vision-native retrieval** — Operates on document images directly
- **Late interaction** — Fine-grained patch-level comparison for high accuracy
- **OCR-free** — No text extraction needed before retrieval
- **Multi-page** — Retrieve relevant pages from multi-page document scans
- **PaliGemma backbone** — Built on Google's vision-language model

## Installation

```bash
uv add colpali-engine
# Model: vidore/colpali-v1.3
```

## Integration with Our Stack

ColPali is used for visual document retrieval in the exam paper pipeline. The model is served locally via HuggingFace passthrough and cached in `stedding/huggingface/hub/` (~108 MB). The `vision` LiteLLM alias routes image-based queries to ColPali for document page retrieval before text extraction via Docling/OLMOCR.

## Upstream

- **Repository**: <https://github.com/illuin-tech/colpali>
- **Model**: <https://huggingface.co/vidore/colpali-v1.3>
- **Latest**: v1.3 (2025) — improved late interaction, PaliGemma backbone, multi-page support

## Screenshot

ColPali is a model accessed via Python. Retrieval results show document page images ranked by relevance score. The Vidore benchmark evaluates ColPali against text-based retrievers on document understanding tasks. The model's visual retrieval capability is demonstrated by matching queries to equation-heavy exam pages where text-based search fails.
