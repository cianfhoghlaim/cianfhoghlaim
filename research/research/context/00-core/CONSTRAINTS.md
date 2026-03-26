# Critical Constraints

**MANDATORY:** All AI agents MUST follow these constraints. Violations cause data corruption, performance degradation, or system failures.

## Database Constraints

### DuckDB: SINGLE_THREADED_ONLY

**Severity:** CRITICAL - Violation causes segfault/data corruption

**Rule:** All DuckDB operations must go through a single-threaded executor. Never attempt concurrent reads or writes.

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
# conn2.execute("INSERT INTO table")    # Thread 2 - CRASH!
```

**Symptoms of Violation:**
- Segmentation fault
- "database is locked" errors
- Corrupted `.duckdb` files
- Inconsistent query results

### LanceDB: MVCC with Serial Wrapper

**Severity:** HIGH - Violation causes data loss or duplicates

**Rule:** LanceDB handles multi-process via MVCC, but within each process use SerialDatabaseExecutor.

**Architecture Layers:**
1. **Python Layer:** SerialDatabaseExecutor (single-threaded queue)
2. **Rust Layer:** MVCC coordination, automatic conflict resolution

**Implementation:**
```python
# CORRECT: Use merge_insert for idempotency
table.merge_insert("id")  # Handles conflicts via MVCC

# CORRECT: Deduplicate multi-result queries
results = table.search().where(condition).to_list()
results = _deduplicate_by_id(results)  # Required for correctness

# WRONG: Assume query results are unique without deduplication
results = table.search().where(condition).to_list()  # May have duplicates!
```

**Fragmentation Behavior:**
- Each `merge_insert` creates a new fragment
- Compaction occurs at 100 operations
- Queries may return duplicates before compaction
- Always deduplicate multi-result queries

## Embedding Constraints

### Batching: MANDATORY

**Severity:** CRITICAL - Violation causes 100x performance degradation

**Rule:** NEVER process embeddings one at a time. Always batch minimum 100 texts.

**Performance Numbers:**
| Operation | Unbatched | Batched | Constraint |
|-----------|-----------|---------|------------|
| 1000 texts | 100s | 1s | 100x speedup |
| API calls | 1000 | 10 | Rate limit friendly |
| Memory | High | Low | Efficient batching |

**Implementation:**
```python
# CORRECT: Batch embeddings
def embed_texts(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_embeddings = client.embed(batch)
        embeddings.extend(batch_embeddings)
    return embeddings

# WRONG: Single-text embedding in loop
for text in texts:
    embedding = client.embed([text])  # 100x slower!
```

### HNSW Index Management

**Severity:** HIGH - Violation causes 20x slowdown for bulk operations

**Rule:** DROP HNSW indexes before bulk inserts >50 rows, RECREATE after.

**Implementation:**
```python
# CORRECT: Drop index for bulk insert
if len(new_rows) > 50:
    table.drop_index("vector_idx")  # Remove HNSW
    table.add(new_rows)
    table.create_index("vector_idx", index_type="IVF_HNSW")  # Recreate

# WRONG: Insert with index (slow for bulk)
table.add(large_batch)  # 20x slower with index!
```

**Thresholds:**
| Rows | Strategy | Speedup |
|------|----------|---------|
| <50 | Keep index | 1x |
| 50-1000 | Drop/recreate | 10x |
| >1000 | Drop/recreate | 20x |

## BAML Constraints

### Schema Validation: REQUIRED

**Severity:** MEDIUM - Violation causes type errors and extraction failures

**Rule:** All LLM extractions must use validated BAML schemas.

**Implementation:**
```baml
// CORRECT: Defined schema with validation
class MarkingPoint {
  correct_answer: string
  marks_awarded: int
  valid_alternatives: string[]
}

function ExtractMarks(text: string) -> MarkingPoint[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Extract marking points from:
    {{ text }}
    {{ ctx.output_format }}
  "#
}

// WRONG: Unstructured extraction
# result = llm.complete("Extract the marks from: " + text)
```

**Validation Checklist:**
- [ ] Schema defined in `baml_src/`
- [ ] Types match expected output
- [ ] Tested with sample documents
- [ ] Error handling for validation failures

## Irish Language Constraints

### Model Selection: SPECIALIZED_REQUIRED

**Severity:** HIGH - Violation causes 20% accuracy loss

**Rule:** Use Irish-specialized models for Irish content.

**Model Priority:**
1. **UCCIX-Llama2-13B-Instruct**: +12% over LLaMA 2-70B on Irish
2. **GaBERT**: Irish-specific BERT embeddings
3. **Qwen2.5-Math-7B**: Native multilingual with Irish support

**Implementation:**
```python
# CORRECT: Use specialized model
irish_model = OpenAILike(
    id="uccix-13b",
    base_url="https://api.uccix.ie/v1/",
)

# WRONG: Use generic model for Irish
# generic_model = "gpt-4"  # 20% accuracy loss on Irish
```

### Dialect Handling

**Rule:** Normalize dialects or preserve based on use case.

| Dialect | Region | Key Differences |
|---------|--------|-----------------|
| Connacht | West | Default standard |
| Munster | South | Different verb forms |
| Ulster | North | `Amharc` vs `Feach` |
| Standard | Official | Curriculum default |

## Performance Thresholds

### Critical Numbers

| Metric | Threshold | Action if Exceeded |
|--------|-----------|-------------------|
| Embedding batch | <100 | Increase batch size |
| DB operations/sec | >10 | Check for concurrent access |
| Index rebuild time | >60s | Pre-drop index |
| OCR per page | >5s | Check model selection |
| Memory per process | >4GB | Review batch sizes |

### Optimization Triggers

Only add complexity when:
- Batch size <100 causes rate limits
- Single-thread bottleneck proven with profiling
- Concurrent access required (use LanceDB, not DuckDB)
- Irish accuracy <80% (switch to UCCIX)

## Validation Commands

```bash
# Check database health
python -c "import duckdb; conn = duckdb.connect(':memory:'); print('DuckDB OK')"

# Verify embedding batching
uv run python -c "
from chunkhound.providers.embeddings import embed_texts
texts = ['test'] * 100
embeddings = embed_texts(texts)
print(f'Embedded {len(embeddings)} texts')
"

# Test BAML schema
uv run baml test --filter curriculum

# Verify Irish model access
curl -X POST https://api.uccix.ie/v1/completions \
  -H "Authorization: Bearer $UCCIX_API_KEY" \
  -d '{"prompt": "Dia duit", "max_tokens": 10}'
```

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

## Constraint Checklist

Before any data operation:
- [ ] Using SerialDatabaseExecutor for DuckDB?
- [ ] Batch size ≥100 for embeddings?
- [ ] HNSW indexes dropped for bulk >50 rows?
- [ ] BAML schema validated?
- [ ] Irish content using specialized models?
- [ ] Deduplication applied to multi-result queries?
