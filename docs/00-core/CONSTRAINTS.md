---
title: 'Critical Constraints'
domain: 'core'
status: 'stable'
description: 'Mandatory constraints every AI agent must follow. Violations cause data corruption, performance degradation, or system failures.'
read_when:
  - before writing any data-pipeline or storage code
  - when in doubt about a database or embedding operation
updated: '2026-06-13'
supersedes: []
ccc_query_hints:
  - duckdb single threaded
  - lancedb mvcc
  - embedding batch size
  - irish language model
  - zero absolute namespaces
---

# Critical Constraints

**MANDATORY:** All AI agents MUST follow these constraints. Violations cause
data corruption, performance degradation, or system failures.

For the full project identity, quadrant map, and routing rules, see
[`docs/00-core/CLAUDE.md`](./CLAUDE.md). This file is the constraint list only.

## 1. Database Constraints

### 1.1 DuckDB: SINGLE_THREADED_ONLY

**Severity:** CRITICAL — Violation causes segfault / data corruption.

**Rule:** All DuckDB operations must go through a single-threaded executor.
Never attempt concurrent reads or writes.

**Implementation:**
```python
# CORRECT: Single-threaded executor pattern
from concurrent.futures import ThreadPoolExecutor

class SerialDatabaseExecutor:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=1)

    def run(self, fn, *args, **kwargs):
        future = self._executor.submit(fn, *args, **kwargs)
        return future.result()

# WRONG: Direct concurrent access
# conn1.execute("SELECT * FROM table")  # Thread 1
# conn2.execute("INSERT INTO table")    # Thread 2 — CRASH!
```

**Symptoms of Violation:**
- Segmentation fault
- "database is locked" errors
- Corrupted `.duckdb` files
- Inconsistent query results

### 1.2 LanceDB: MVCC with Serial Wrapper

**Severity:** HIGH — Violation causes data loss or duplicates.

**Rule:** LanceDB handles multi-process via MVCC; within each process use
`SerialDatabaseExecutor`.

**Architecture layers:**
1. **Python Layer:** `SerialDatabaseExecutor` (single-threaded queue)
2. **Rust Layer:** MVCC coordination, automatic conflict resolution

**Implementation:**
```python
# CORRECT: use merge_insert for idempotency
table.merge_insert("id")  # Handles conflicts via MVCC
```

### 1.3 HNSW Index Lifecycle

**Rule:** Drop HNSW indexes for any bulk insert >50 rows; rebuild after.

```python
# CORRECT: drop → insert → rebuild
table.drop_index("vector_idx")
table.add(data)  # bulk insert
table.create_index(num_partitions=...)
```

### 1.4 DuckLake + Iceberg + MotherDuck

- **Writes** go to DuckLake (Parquet on Garage S3, Postgres catalog).
- **Reads** go to MotherDuck (`md:oideachais`).
- **Long-tail catalogue** lives in Apache Iceberg via Lakekeeper (not written to today).
- See `docs/02-data-platform/storage-mental-model.md`.

### 1.5 Path / Namespace Rules

- **Zero absolute namespaces inside `oideachais/`** — never import
  `oideachais.data_platform.*` or `oideachais.middleware.*` from
  within `oideachais/`. Use relative imports.
  - Enforced by `oideachais/tests/sources/test_cross_namespace.py`.

## 2. Embedding Performance Constraints

### 2.1 Batching: MANDATORY (100× performance difference)

| Scenario | Time |
|---|---|
| Unbatched 1,000 texts | ~100 s |
| Batched 1,000 texts | ~1 s |

**Minimum batch size:** 100 embeddings per API call.

### 2.2 HNSW Index Management

- Drop indexes before bulk inserts >50 rows (20× speedup).
- Recreate after batch complete.
- Monitor memory usage; >4 GB per process is a yellow flag.

### 2.3 Performance Thresholds

| Metric | Threshold | Action if Exceeded |
|---|---|---|
| Embedding batch | < 100 | Increase batch size |
| DB operations/sec | > 10 | Check for concurrent access |
| Index rebuild time | > 60 s | Pre-drop index |
| OCR per page | > 5 s | Check model selection |
| Memory per process | > 4 GB | Review batch sizes |

## 3. BAML Schema Validation

**MANDATORY:** schema validation before every LLM call. Use type-safe
extraction for curriculum documents. Test schemas in `baml_src/` before
production use.

The LLM stack hierarchy is: `BAML (structured extraction in DE) → litellm
(routing) → ADK/AGNO (agent orchestration) → ccc cocoindex-code (semantic
index over the codebase) → Cognee (knowledge graph)`. See
[`docs/04-ai-ml/llm-stack-hierarchy.md`](../04-ai-ml/llm-stack-hierarchy.md).

## 4. Irish Language Processing

- Irish is <0.1% of web content (~20% model performance gap).
- Use specialized models: **UCCIX-Llama2-13B-Instruct**, **GaBERT**,
  **Qwen2.5-Math**.
- Handle dialects: Connacht, Munster, Ulster, Standard.

## 5. Source Asset-Key Contract

Every source in `oideachais/sources.yaml` has id `{nation}.{domain}.{entity}`
and an `asset_key: [{nation}, {domain}, ...]`. The 43 sources span 8
nations (ie, ni, en, sct, wls, iom, jey, ggy) × 4 domains (education,
medicine, law, statistics) + the `site_analysis` sidecar domain. See
[`docs/02-data-platform/cross-domain-registry.md`](../02-data-platform/cross-domain-registry.md).

## 6. Browser Automation Decision Tree

| Need | First choice | Second | Third |
|---|---|---|---|
| Scrape (paid) | `firecrawl` MCP | `sruth-browser` selfhosted | `Firecrawl` API |
| Scrape (free) | `sruth-browser` selfhosted | Crawl4AI | `firecrawl` MCP (with own key) |
| Interact (form/login) | `browserbase` MCP | `Stagehand` selfhosted | `skyvern` selfhosted |
| LLM-driven page description | `oideachais/site_analysis/` (BAML `SiteAnalysis` schema) | `firecrawl` MCP `extract` | manual agent loop |

In test mode (`USE_LOCAL_SCRAPES=true`) every call routes through the
`oideachais/site_analysis/_stubs/` fixture so the asset graph is
exercisable without a live browser. See
[`docs/03-agents/browser-automation.md`](../03-agents/browser-automation.md).

## 7. Constraint Checklist

Before any data operation:
- [ ] Using `SerialDatabaseExecutor` for DuckDB?
- [ ] Batch size ≥ 100 for embeddings?
- [ ] HNSW indexes dropped for bulk > 50 rows?
- [ ] BAML schema validated for LLM extraction?
- [ ] Irish content using specialized model (UCCIX / GaBERT)?
- [ ] Deduplication applied to multi-result queries?
- [ ] Cross-namespace check passes (`oideachais/tests/sources/test_cross_namespace.py`)?
- [ ] Path stale-ref check passes (`bun run validate-docs`)?
