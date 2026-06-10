# KCG_SUMMARY: Historical Document Analysis — Multi-Modal Deep Learning Pipeline

## What It Is
A multi-modal deep learning research repository for analysing historical documents and parsing manuscripts into structured JSON format. Built for the Cairo Genizah project, it combines OCR (Google Cloud Vision, Doctr, Unstructured), multi-modal embeddings (NOMIC, CLIP), search indexing (Elasticsearch), and graph database storage (Neo4j). The pipeline handles document ingestion, OCR, embedding generation, and indexing across multiple institutions' collections (Cambridge, Princeton, Manchester, Oxford).

## Why This Matters for Kings' College Galway
This repository demonstrates an end-to-end pipeline for historical document digitisation at scale — the exact workflow needed for Irish manuscript collections. For Kings' College Galway's **teanga** platform, it provides the technical patterns for: preprocessing historical Irish-language documents, generating multi-modal embeddings that work across scripts (Latin, Gaelic type, Ogham), building searchable indices of student-transcribed materials, and creating a linked data graph connecting Irish manuscripts, placenames, and people. The multi-step OCR pipeline is directly applicable to the 1937-39 Schools' Collection, where Irish-language handwriting recognition presents unique challenges.

## Key Patterns Preserved
- `readme.md` — Full project architecture, data pipeline structure, OCR service docs, embedding models, and institutional acknowledgements
- `src/datasets/indexing/bibliography/README.md` — Bibliography indexing module documentation
- `src/datasets/indexing/sql/README.md` — SQL indexing module documentation

## Source Files
Full source code was removed on 2026-06-06. The original repository is at github.com/AIStream-Peelout/historical-document-analysis. This skeleton preserves the pipeline architecture and data flow descriptions.

## What Was Removed
- Python source code (data pipeline, OCR services, embedding models, indexing scripts)
- Document model definitions (GenizahDocument, GemaraDocument, BibliographyDocument)
- Elasticsearch index configuration and bulk insert scripts
- Multi-modal embedding model code (NOMIC, CLIP)
- SQL database schemas
- Requirements and environment files
- GCP integration and credential management code
- Weights & Biases experiment tracking
