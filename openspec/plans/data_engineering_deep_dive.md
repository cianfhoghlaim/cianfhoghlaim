---
title: 'Data Engineering Deep Dive'
status: research
supersedes: []
superseded_by: [openspec/specs/oideachais-pipeline/spec.md, openspec/specs/data-pipeline/spec.md, docs/02-data-platform/data-architecture.md]
last_touched: 2026-06-13
---

# Data Engineering & Pipeline Deep Dive

This document provides a deep dive into the Data Engineering and Pipeline layers of the `education` workspace, focusing specifically on the `education/data_engineering/dlt_sources` and `education/data_engineering/dagster_defs` directories. It covers the architecture for cross-border curriculum scraping, standardization across different educational systems, and the pivotal role of `dlt` (data load tool).

## Architecture Overview

The data pipeline architecture follows a robust Extract, Load, Transform (ELT) pattern heavily orchestrated by **Dagster** and powered by **dlt** for extraction and loading. It is designed to harvest, standardize, and semantically align fragmented educational curriculums from across multiple nations (Ireland, England, Scotland, Wales, Northern Ireland).

The asset hierarchy in the pipeline follows this progression:
1. `curriculum.{nation}.pages`: Raw crawled web pages and documents.
2. `curriculum.{nation}.structured`: BAML-extracted structured data.
3. `curriculum.unified.outcomes`: Normalized learning outcomes.
4. `curriculum.unified.embeddings`: Vector embeddings for semantic search.
5. `curriculum.unified.alignments`: Cross-nation outcome alignments.

## Cross-Border Scraping, Indexing, and Standardizing

The pipeline elegantly manages the diversity of educational systems by centralizing unstructured scraping through `dlt` and applying structured standardization via domain-specific Pydantic models and BAML (an LLM-based structured data extraction tool).

### English Standardization (GCSE / A-Level)
For England, the pipeline targets the National Curriculum (gov.uk) and major exam boards (AQA, Edexcel, OCR).
- **Dagster Assets**: Assets like `england_national_curriculum` and `england_exam_boards` encapsulate the extraction logic.
- **Scraping Scope**: It scrapes Key Stages 1-5, GCSE subject content, and A-Level subject content, alongside PDF specification links from the respective exam boards.
- **Standardization**: Extracted content is pushed to a unified dataset. The data models handle the specific nomenclature of the English system (Key Stages, GCSE, A-Level) and align them into a standardized format (`CrossNationCurriculumSpec` and `CrossNationLearningOutcome`) via the unified BAML extraction step (`curriculum_structured_extraction`).

### Irish Standardization (Junior Cycle / Senior Cycle)
For Ireland, the curriculum is sourced from multiple origins: `curriculumonline.ie`, `ncca.ie`, and `examinations.ie`, plus CPD resources from `oide.ie`.
- **Subject-Centric Crawling**: The `curriculum_source.py` pipeline runs concurrent crawls across multiple sources for specific combinations of `(cycle, subject, language)`. It maps standard cycles (e.g., `junior_cycle`, `senior_cycle`) to their corresponding English and Irish (Gaeilge) URLs (e.g., `an-tsraith-shoisearach`).
- **Standardization Model**: `CurriculumDocument` (in `curriculum_document.py`) acts as the unified Pydantic model for Irish documents. It captures:
  - Subject, Level (`PRIMARY`, `JUNIOR_CYCLE`, `SENIOR_CYCLE`, `FURTHER_EDUCATION`), and Strand.
  - Language classification (`ENGLISH`, `IRISH`, `BILINGUAL`).
  - Extracted Learning Outcomes (`LearningOutcome` model with codes, text, and strands).
  - Completeness scoring based on weighted heuristics (Title, Subject, Content quality, Irish translation presence).
- **Deduplication**: Content is deduplicated across sources via SHA256 content hashing (`content_hash`). Provenance records track which sources provided the duplicate content (`source_provenance`).

### Unified Processing and Alignment
Once the raw pages are ingested from both English and Irish systems (as well as Scotland, Wales, and Northern Ireland), the pipeline performs:
1. **Structured Extraction**: Converts raw pages into `CrossNationCurriculumSpec` objects.
2. **Unified Embeddings**: Generates vector embeddings for the content using BGE-M3 (1024 dimensions) into **LanceDB** for high-performance semantic search.
3. **Outcome Alignments**: Computes semantic alignments between learning outcomes across nations using vector similarity and LLM reasoning (identifying equivalent outcomes, partial overlaps, and prerequisite relationships).

## The Role of `dlt` (data load tool)

`dlt` serves as the crucial bridge between unstructured web data and the structured data warehouse layer.

1. **Declarative Pipelines**: In `dlt_sources`, `dlt` is used to define declarative, Pythonic data pipelines. For example, the `curriculum_source` uses `@dlt.source` and `@dlt.resource` decorators to define resources like `curriculum_pages`, `source_provenance`, and `curriculum_pdfs`.
2. **Integration with Firecrawl**: `dlt` seamlessly wraps the `FirecrawlApp` logic, executing highly concurrent web scraping across multiple sites and converting the resulting HTML/Markdown into standardized Python dictionaries.
3. **Schema Inference and Typing**: `dlt` automatically infers schema types from the yielded dictionaries and handles the robust insertion logic (`write_disposition="merge"` based on primary keys like `content_hash`).
4. **Tie-in with Infrastructure Storage**: The pipelines defined in `dlt` explicitly target **DuckDB** as the analytical database (`destination="duckdb"`). This integrates directly with the infrastructure storage layer (Lakehouse pattern), where DuckDB files (e.g., `curriculum_unified.duckdb`) act as the high-performance local analytical store, enabling single-threaded but blazing-fast queries before the heavy embeddings are offloaded to **LanceDB**.
5. **Dagster Orchestration**: Through `DagsterDltResource`, Dagster seamlessly orchestrates these `dlt` pipelines within its asset graph, allowing complex dependencies (like waiting for `dlt` extraction to finish before running BAML extraction or LanceDB embedding generation) to be managed reliably.

In summary, the Data Engineering layer provides a sophisticated, multi-national data harmonization engine, heavily utilizing `dlt` to abstract the complexity of ingestion and DuckDB/LanceDB to manage the structured and semantic data workloads.