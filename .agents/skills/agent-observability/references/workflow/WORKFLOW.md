# Workflow — End-to-End Documentation Cognition

Step-by-step workflow for processing documentation through the cognition pipeline: from raw `.md` files to a queryable knowledge graph with agent-accessible MCP endpoints.

## Overview

```
PHASE 1: INDEX     → CCC builds semantic code index
PHASE 2: INGEST    → Cognee ingests .md files by dataset
PHASE 3: COGNIFY   → Cognee builds knowledge graph (LLM processing)
PHASE 4: TEMPORAL  → Graphiti adds bi-temporal layer
PHASE 5: ANALYZE   → GraphRAG queries identify merge clusters
PHASE 6: CONSOLIDATE → Subagents merge scattered docs
PHASE 7: MONITOR   → Langfuse traces cost, Dozzle shows logs, Beszel monitors resources
```

## Phase 1: Index the Codebase (CCC)

```bash
# Incremental refresh (fast — recommended before every session)
bun run ccc:index

# Verify index is active
ls -lh .cocoindex_code/target_sqlite.db
# Expected: ~35 MB SQLite database

# Test search
bun run ccc:search "Cognee add cognify search API"
```

**Output**: Semantic code index covering all Python, TypeScript, BAML, Rust, and Go files.

## Phase 2: Ingest Documentation (Cognee)

```bash
# Ensure Cognee is running
docker ps --filter name=cognee --format "table {{.Names}}\t{{.Status}}"

# Ingest by dataset (parallel or sequential)
cd oideachais

for dir in docs/agents docs/bonneagar docs/data_engineering docs/meaisínfhoghlaim docs/web docs/context; do
  dataset=$(echo $dir | sed 's|docs/|docs-|')
  uv run python scripts/cognee_http_ingest.py "../$dir" "$dataset"
done
```

**Output**: All `.md` files loaded into Cognee's LanceDB vector store, organized by dataset.

## Phase 3: Cognify — Build Knowledge Graph

```bash
# Cognify all datasets at once (triggers LLM processing)
curl -X POST http://localhost:8100/api/v1/cognify \
  -H "Content-Type: application/json" \
  -d '{
    "datasets": [
      "docs-agents", "docs-bonneagar", "docs-data-eng",
      "docs-ml", "docs-web", "docs-context"
    ],
    "runInBackground": true
  }'

# Monitor cognify progress via Langfuse
# Check traces at https://langfuse.cianfhoghlaim.ie
```

**Output**: Knowledge graph in Neo4j — entities (tools, concepts, patterns) connected by relationships (implements, references, depends-on).

**Cost**: ~$6 for 2,242 documents with DeepSeek V4 Pro.

## Phase 4: Add Temporal Layer (Graphiti)

```bash
# Graphiti runs on the same Neo4j instance
# Temporal metadata is added automatically when Graphiti processes Cognee's output

# Query temporal state:
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "what were the prerequisite chains before the 2023 reform?"}'
```

**Output**: Bi-temporal metadata on all KG nodes — query curriculum data as it existed at any point in time.

## Phase 5: Analyze — Generate Consolidation Plan

```bash
# Find merge clusters via GraphRAG
curl -X POST http://localhost:8100/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "searchType": "GRAPH_COMPLETION",
    "query": "find groups of documents that discuss the same topics and should be merged into single comprehensive documents. Return file paths and suggested titles.",
    "datasets": ["docs-agents", "docs-bonneagar", "docs-data-eng", "docs-ml"]
  }'

# Find misplaced documents
curl -X POST http://localhost:8100/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "searchType": "INSIGHTS",
    "query": "identify documents that are in the wrong directory based on their content topic vs directory name"
  }'

# Generate topic summaries
curl -X POST http://localhost:8100/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "searchType": "SUMMARIES",
    "query": "what are the major themes and topic clusters across all documentation?"
  }'
```

**Output**: `CONSOLIDATION_PLAN.md` listing merge groups by topic cluster.

## Phase 6: Consolidate — Merge Scattered Docs

Subagents execute the plan:

```
Subagent 1: docs/agents/ + docs/context/
Subagent 2: docs/data_engineering/ + docs/bonneagar/
Subagent 3: docs/meaisínfhoghlaim/
Subagent 4: docs/web/
```

Each subagent:
1. Reads its section of CONSOLIDATION_PLAN.md
2. For each merge cluster: reads all source files, writes a single merged document
3. Adds "## Merged From" headers listing original files
4. Replaces original files with "MERGED INTO" stubs
5. Updates INDEX.md

## Phase 7: Monitor — Observe and Verify

### Langfuse — Trace All Cognition Operations

```
https://langfuse.cianfhoghlaim.ie
→ Traces → Filter by "cognee-cognify"
→ Shows: token counts, cost, latency per dataset
→ Shows: entity extraction quality, relationship confidence
```

### Dozzle — Real-Time Logs

```
https://dozzle.cianfhoghlaim.ie
→ Filter: container=cognee
→ Shows: ingestion progress, cognify status, LLM API errors
```

### Beszel — Resource Metrics

```
https://beszel.cianfhoghlaim.ie
→ CPU: monitor during cognify (LLM processing is CPU-bound)
→ Memory: Neo4j graph size grows with each cognify run
→ Disk: LanceDB index and Cognee data volume
```

### Verify with CCC

```bash
# After consolidation, re-index and search
bun run ccc:index
bun run ccc:search "comprehensive BAML guide"
bun run ccc:search "Pangolin deployment patterns"
```

## Automated Pipeline (Dagster)

The entire workflow can be automated as a Dagster job:

```python
from dagster import job

@job
def documentation_cognition_pipeline():
    docs_added = docs_added_to_cognee()  # Phase 2
    cognified = docs_cognified(docs_added)  # Phase 3
    temporal = graphiti_temporal_layer(cognified)  # Phase 4
    plan = generate_consolidation_plan(temporal)  # Phase 5
    merged = execute_merges(plan)  # Phase 6
    return merged

# Run via Dagster UI or CLI:
# uv run dagster job execute -m data_platform.dagster_defs.definitions \
#   -j documentation_cognition_pipeline
```

## Scheduled Runs

```bash
# Weekly: re-index codebase
0 2 * * 0  bun run ccc:index

# Monthly: re-cognify documentation (after doc changes accumulate)
0 3 1 * *  bun run turbo dagster:cognify-docs

# Daily: monitor cognition pipeline health
0 8 * * *  bun run turbo spec:validate
```
