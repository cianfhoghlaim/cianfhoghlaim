---
title: 'Oideachais Pipeline Capability'
domain: 'architecture'
status: 'stable'
description: 'Celtic education curriculum pipeline processing Irish, UK, and pan-Celtic educational content with AI-enhanced learning experiences.'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/OIDEACHAIS_SPEC.md
ccc_query_hints:
  - oideachais pipeline capability
---

# Oideachais Pipeline Capability

## Overview

Celtic education curriculum pipeline processing Irish, UK, and pan-Celtic educational content with AI-enhanced learning experiences.

| Feature | Description |
|---------|-------------|
| DLT Ingestion | NCCA, SEC, UK curriculum sources |
| CocoIndex Transform | Embedding generation |
| Knowledge Graph | Prerequisite mapping in Memgraph |
| ADK Agents | Education-focused AI agents |

## Requirements

### Requirement: Curriculum Ingestion

The system SHALL ingest curriculum documents from multiple sources.

#### Scenario: Irish Curriculum
- **GIVEN** NCCA curriculum documents
- **WHEN** DLT pipeline runs
- **THEN** documents are extracted and stored in DuckDB

#### Scenario: UK Curriculum
- **GIVEN** UCAS, DfE, ONS datasets
- **WHEN** DLT pipeline runs
- **THEN** data is normalized and stored

#### Scenario: Exam Papers
- **GIVEN** SEC exam papers and marking schemes
- **WHEN** extraction pipeline runs
- **THEN** questions and answers are aligned

### Requirement: Embedding Generation

The system SHALL generate embeddings via CocoIndex for semantic search.

#### Scenario: Document Embeddings
- **GIVEN** curriculum documents
- **WHEN** CocoIndex flow runs
- **THEN** embeddings are stored in LanceDB with HNSW index

#### Scenario: Bilingual Embeddings
- **GIVEN** English and Irish content
- **WHEN** embedding flow runs
- **THEN** both languages are indexed with language tags

### Requirement: Knowledge Graph

The system SHALL maintain curriculum knowledge graph for prerequisites.

#### Scenario: Prerequisite Mapping
- **GIVEN** curriculum topics
- **WHEN** graph is built
- **THEN** prerequisite relationships are captured in Memgraph

#### Scenario: Topic Hierarchy
- **GIVEN** subject areas
- **WHEN** hierarchy is built
- **THEN** topics are organized by strand and level

### Requirement: Agent Integration

The system SHALL support ADK education agents.

#### Scenario: Curriculum Query
- **GIVEN** student query
- **WHEN** agent processes
- **THEN** curriculum-aware response is generated

#### Scenario: Assessment Help
- **GIVEN** exam question
- **WHEN** agent analyzes
- **THEN** marking scheme guidance is provided

## Components

| Component | Path | Purpose |
|-----------|------|---------|
| `dlt_sources/` | `sruth/oideachais/dlt_sources/` | Ireland, UK, Celtic, geospatial |
| `cocoindex_flows/` | `sruth/oideachais/cocoindex_flows/` | Embedding pipelines |
| `dagster_defs/` | `sruth/oideachais/dagster/` | Asset orchestration |
| `agents/` | `sruth/oideachais/agents/` | ADK education agents |
| `storage/` | `sruth/oideachais/storage/` | DuckDB, LanceDB, Memgraph |

## Constraints

From `.claude/CONSTRAINTS.md`:
- **DuckDB:** SINGLE_THREADED_ONLY (concurrent access = segfault/corruption)
- **LanceDB:** MVCC safe with SerialDatabaseExecutor
- **Embeddings:** Batch minimum 100 texts per API call
- **HNSW:** Drop indexes before bulk inserts >50 rows
- **Irish Language:** Use UCCIX or GaBERT models

## Implementation References

| Component | Path |
|-----------|------|
| Main Pipeline | `sruth/oideachais/` |
| Dagster Definitions | `sruth/oideachais/dagster/definitions.py` |

## Related Specs

- [curriculum-ingestion](../curriculum-ingestion/spec.md) - Document processing
- [bilingual-content](../bilingual-content/spec.md) - English/Irish management
- [knowledge-graph](../knowledge-graph/spec.md) - Prerequisite mapping
- [semantic-search](../semantic-search/spec.md) - Vector search
- [assessment-extraction](../assessment-extraction/spec.md) - Exam papers
