---
domain: standards
title: Project Conventions
description: Consolidated project standards, constraints, and specifications for the Cianfhoghlaim platform — naming conventions, technology constraints, database safety, embedding performance, Irish language requirements, and BAML schema validation.
updated: 2026-06-06
merged_from:
  - docs/context/00-core/PROJECT_SPEC.md
  - docs/context/00-core/CONSTRAINTS.md
  - docs/context/08-examples/OIDEACHAIS_SPEC.md
ccc_query_hints:
  - project conventions standards
  - database constraints duckdb single threaded
  - embeddings batching mandatory
  - irish language models uccix gabert
  - baml schema validation
  - naming conventions
---

# Project Conventions

## Table of Contents

1. [Project Identity & Scope](#project-identity--scope)
2. [Naming Conventions](#naming-conventions)
3. [Technology Constraints](#technology-constraints)
4. [Database Safety](#database-safety)
5. [Embedding Performance](#embedding-performance)
6. [BAML Schema Validation](#baml-schema-validation)
7. [Irish Language Processing](#irish-language-processing)
8. [Performance Thresholds](#performance-thresholds)
9. [Directory Map](#directory-map)
10. [Constraint Checklist](#constraint-checklist)
11. [Oideachais Pipeline Spec](#oideachais-pipeline-spec)

---

## Project Identity & Scope

**Cianfhoghlaim** (Irish: "deep learning"): Celtic language education platform with AI-powered tools for Irish curriculum. Bilingual focus on English/Irish with pan-Celtic language support (Welsh, Scottish Gaelic, Manx).

### Capability Areas

| Area | Capabilities |
|------|-------------|
| **Education Platform** | curriculum-ingestion, bilingual-content, knowledge-graph, semantic-search, assessment-extraction, oideachais-pipeline |
| **Dagger Modules** | dagger-ci, dagger-gitops, dagger-forgejo, dagger-komodo, dagger-cloudflare, dagger-blockchain |
| **Developer Tooling** | beads-issue-tracking, chunkhound-code-search |
| **Infrastructure** | 25+ storage and utility Docker stacks |

### Technology Stack

| Layer | Technology |
|-------|------------|
| Document Ingestion | ColPali, DeepSeek-OCR, Granite-Docling |
| Knowledge Base | FalkorDB + Qdrant |
| Temporal Reasoning | Graphiti (bi-temporal) |
| ETL Orchestration | CocoIndex, Dagster, DLT |
| Structured Extraction | BAML |
| RAG Retrieval | BGE-M3 + ColPali |
| Generation | Qwen2.5-Math-7B, UCCIX |
| Frontend | TanStack Start + Cloudflare |
| Durable Execution | Restate, DBOS |
| BI Semantic Layer | Cube, Rill |

---

## Naming Conventions

- **Capabilities**: kebab-case (`curriculum-ingestion`, `bilingual-content`)
- **Changes**: Prefix with action (`add-`, `update-`, `remove-`, `refactor-`)
- **Dagster assets**: Lowercase with underscores, noun-based (`daily_active_users`, `customer_churn_predictions`)
- **Irish names for core concepts**: `sruth` (flow), `bonneagar` (infrastructure)
- **English for technical implementation**
- **Bilingual support** in all user-facing content

### Requirement Language

- **SHALL** for normative requirements
- **SHOULD** for recommendations
- **MAY** for optional features

---

## Technology Constraints

All implementations MUST respect the following:

### Database Safety

| Constraint | Severity | Rule |
|------------|----------|------|
| **DuckDB SINGLE_THREADED** | CRITICAL | All operations through SerialDatabaseExecutor |
| **LanceDB MVCC safe** | HIGH | Within process: single-threaded; Between processes: MVCC + conflict resolution |
| **NEVER concurrent DB ops** | CRITICAL | Parsing parallelized, storage single-threaded |

### Embedding Performance

| Constraint | Severity | Rule |
|------------|----------|------|
| **Batching MANDATORY** | CRITICAL | Minimum 100 texts per API call (100x faster) |
| **HNSW index management** | HIGH | Drop before bulk inserts >50 rows; Recreate after |
| **Minimum batch size** | CRITICAL | 100 embeddings per API call |

### BAML Schema Validation

| Constraint | Severity | Rule |
|------------|----------|------|
| **SCHEMA_VALIDATION_REQUIRED** | MEDIUM | Before all LLM extraction calls |
| **Type-safe extraction** | MEDIUM | For all curriculum documents |
| **Test schemas first** | MEDIUM | In `baml_src/` before production use |

### Irish Language Processing

| Constraint | Severity | Rule |
|------------|----------|------|
| **SPECIALIZED_REQUIRED** | HIGH | Use UCCIX or GaBERT (20% accuracy gap with generic models) |
| **Dialect handling** | MEDIUM | Normalize dialects or preserve based on use case |

---

## Database Safety

### DuckDB: SINGLE_THREADED_ONLY

**Violation causes**: Segfault, data corruption, "database is locked", inconsistent queries.

```python
# CORRECT: Single-threaded executor
class SerialDatabaseExecutor:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=1)

    def run(self, fn, *args, **kwargs):
        future = self._executor.submit(fn, *args, **kwargs)
        return future.result()
```

### LanceDB: MVCC with Serial Wrapper

**Architecture:**
1. **Python Layer**: SerialDatabaseExecutor (single-threaded queue)
2. **Rust Layer**: MVCC coordination, automatic conflict resolution
3. **Always deduplicate** multi-result queries (fragmentation can cause duplicates before compaction)

---

## Embedding Performance

### Batching Numbers

| Operation | Unbatched | Batched | Gain |
|-----------|-----------|---------|------|
| 1000 texts | 100s | 1s | 100x |
| API calls | 1000 | 10 | Rate limit friendly |

```python
# CORRECT: Batch embeddings
def embed_texts(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_embeddings = client.embed(batch)
        embeddings.extend(batch_embeddings)
    return embeddings
```

### HNSW Index Management

| Rows | Strategy | Speedup |
|------|----------|---------|
| <50 | Keep index | 1x |
| 50-1000 | Drop/recreate | 10x |
| >1000 | Drop/recreate | 20x |

---

## BAML Schema Validation

All LLM extractions must use validated BAML schemas:

```baml
class MarkingPoint {
  correct_answer: string
  marks_awarded: int
  valid_alternatives: string[]
}

function ExtractMarks(text: string) -> MarkingPoint[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Extract marking points from: {{ text }}
    {{ ctx.output_format }}
  "#
}
```

**Validation Checklist:**
- [ ] Schema defined in `baml_src/`
- [ ] Types match expected output
- [ ] Tested with sample documents
- [ ] Error handling for validation failures

---

## Irish Language Processing

### Model Priority

1. **UCCIX-Llama2-13B-Instruct**: +12% over LLaMA 2-70B on Irish
2. **GaBERT**: Irish-specific BERT embeddings
3. **Qwen2.5-Math-7B**: Native multilingual with Irish support

```python
# CORRECT: Use specialized model
irish_model = OpenAILike(id="uccix-13b", base_url="https://api.uccix.ie/v1/")
```

### Dialect Handling

| Dialect | Region | Key Differences |
|---------|--------|-----------------|
| Connacht | West | Default standard |
| Munster | South | Different verb forms |
| Ulster | North | `Amharc` vs `Feach` |
| Standard | Official | Curriculum default |

---

## Performance Thresholds

| Metric | Threshold | Action if Exceeded |
|--------|-----------|-------------------|
| Embedding batch | <100 | Increase batch size |
| DB operations/sec | >10 | Check for concurrent access |
| Index rebuild time | >60s | Pre-drop index |
| OCR per page | >5s | Check model selection |
| Memory per process | >4GB | Review batch sizes |

---

## Directory Map

| Directory | Purpose |
|-----------|---------|
| `sruth/` | Data pipelines (códeolas, gaois, tionscnamh, tuath, oideachas) |
| `bonneagar/` | Infrastructure stacks (Docker Compose, deployment) |
| `agents/` | AI agent frameworks (Agno, ADK, Stagehand) |
| `baml_src/` | BAML schemas for type-safe LLM extraction |
| `.agents/skills/` | 63 agent skills |

---

## Constraint Checklist

Before any data operation:
- [ ] Using SerialDatabaseExecutor for DuckDB?
- [ ] Batch size >= 100 for embeddings?
- [ ] HNSW indexes dropped for bulk >50 rows?
- [ ] BAML schema validated?
- [ ] Irish content using specialized models?
- [ ] Deduplication applied to multi-result queries?

## Modification Rules

- **NEVER**: Remove SerialDatabaseProvider wrapper from database code
- **NEVER**: Add concurrent database operations
- **NEVER**: Skip BAML schema validation for LLM extractions
- **NEVER**: Process embeddings without batching
- **ALWAYS**: Check existing skills before implementing features
- **ALWAYS**: Use uv for all Python operations
- **ALWAYS**: Batch embeddings (min: 100, max: provider_limit)
- **ALWAYS**: Drop HNSW indexes for bulk inserts >50 rows

## Error Recovery

### Database Corruption
1. Stop all processes
2. Restore from backup
3. Verify single-threaded access
4. Restart with SerialDatabaseExecutor

### Embedding Timeout
1. Reduce batch size to 50
2. Add retry with exponential backoff
3. Check API rate limits
4. Consider local model

### Index Rebuild Failure
1. Drop all indexes
2. Vacuum database
3. Recreate indexes one at a time
4. Monitor memory usage

---

## Oideachais Pipeline Spec

### Requirements

| Requirement | Description |
|-------------|-------------|
| Curriculum Ingestion | SHALL ingest from NCCA, SEC, UK curriculum sources via DLT pipelines |
| Embedding Generation | SHALL generate embeddings via CocoIndex for semantic search, bilingual |
| Knowledge Graph | SHALL maintain curriculum knowledge graph with prerequisite relationships |
| Agent Integration | SHALL support ADK education agents for curriculum queries |

### Components

| Component | Path | Purpose |
|-----------|------|---------|
| `dlt_sources/` | `sruth/oideachais/dlt_sources/` | Ireland, UK, Celtic, geospatial sources |
| `cocoindex_flows/` | `sruth/oideachais/cocoindex_flows/` | Embedding pipelines |
| `dagster_defs/` | `sruth/oideachais/dagster/` | Asset orchestration |
| `agents/` | `sruth/oideachais/agents/` | ADK education agents |
| `storage/` | `sruth/oideachais/storage/` | DuckDB, LanceDB, Memgraph |

### Scenario Format

```markdown
#### Scenario: Descriptive name
- **GIVEN** initial context
- **WHEN** action occurs
- **THEN** expected result
```

### File Locations
- Specs: `openspec/specs/<capability>/spec.md`
- Changes: `openspec/changes/<change-id>/`
- Archives: `openspec/changes/archive/YYYY-MM-DD-<change-id>/`

### Review Process
1. Create proposal in `changes/<change-id>/`
2. Validate with `openspec validate <change-id> --strict`
3. Request review
4. Implement after approval
5. Archive after deployment
