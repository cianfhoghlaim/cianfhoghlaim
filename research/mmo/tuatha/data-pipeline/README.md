# Data Pipeline

This directory contains research on data ingestion, processing, and storage.

## Contents

- `dagster-orchestration.md` - Asset-based workflow patterns
- `dlt-ingestion.md` - Curriculum & blockchain data loading
- `cocoindex-embeddings.md` - Semantic code/document indexing
- `lancedb-vectors.md` - Vector storage for search
- `cognee-knowledge-graph.md` - Entity relationship graphs
- `federated-learning.md` - SyftBox + Flower FL architecture
- `celtic-data-sources.md` - Cultural archive APIs

## Architecture

```
Cultural Archives (Dúchas, Coflein, etc.)
    ↓ (DLT + Crawl4AI)
Raw Data (PDFs, JSON, Audio)
    ↓ (CocoIndex)
Embeddings (ColPali, Whisper)
    ↓ (LanceDB)
Vector Search
    ↓ (Cognee)
Knowledge Graph
    ↓ (Dagster Assets)
Game Content & Quests
```

## Cultural Data APIs

| Source | Region | API | Use Case |
|--------|--------|-----|----------|
| Dúchas.ie | Ireland | JSON v0.5 | Procedural quests |
| Tobar an Dualchais | Scotland | Partnership | Bardic audio |
| Coflein | Wales | OGC API | Real-world map |
| iMuseum | Isle of Man | Solr | Tutorial content |

## Federated Learning (Syft-Flower)

- Privacy-preserving Celtic OCR training
- Crowdsourced ASR for dialect preservation
- On-device Whisper fine-tuning
