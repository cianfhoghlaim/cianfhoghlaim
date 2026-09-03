# Infrastructure — Supporting Stacks for the Cognition Pipeline

How Lakehouse, LakeFS, Dozzle, and Beszel support the documentation cognition pipeline with storage, versioning, logging, and monitoring.

## Lakehouse — Unified Data Storage

**Stack**: `infrastructure/stacks/lakehouse/`  
**Ports**: 3900-3904 (Garage S3), 8181 (Lakekeeper), 8182 (Lance Namespace)

### Role in the Cognition Pipeline

The lakehouse provides the storage backend for all cognition data:

| Data Type | Storage | Format |
|:--|:--|:--|
| Raw `.md` files | Garage S3 `docs/` bucket | Markdown text |
| Cognee vectors | LanceDB → Lance Namespace → Iceberg | Lance columnar |
| Knowledge graph | Neo4j (graphiti stack) | Property graph |
| Trace data | Langfuse (Postgres + ClickHouse) | Relational + columnar |
| Cognition metrics | Prometheus (monitoring stack) | Time-series |

### Why Lakehouse Matters

- **Single namespace**: All cognition data queryable through one Iceberg catalog — DuckDB can query both structured curriculum data AND Cognee's vector indexes through the Lance Namespace bridge
- **Time travel**: Iceberg snapshots let you query "what was in Cognee's knowledge graph after last month's cognify run?"
- **ACID transactions**: Concurrent writes from Dagster (cognify jobs) and reads from the web app (GraphRAG queries) without conflicts

### Deployment

```bash
cd infrastructure/stacks/lakehouse
docker compose up -d
# Services: garage, lakekeeper, lance-namespace, postgres
```

## Dozzle — Container Log Monitoring

**Stack**: `infrastructure/stacks/dozzle/`  
**Port**: varies (8080 in stack, Pangolin-routed)

### Role in the Cognition Pipeline

Dozzle provides real-time log visibility for all cognition containers:

| Container | What to Monitor |
|:--|:--|
| `cognee` | Ingestion progress, cognify status, LLM API errors |
| `graphiti-neo4j-1` | Graph database health, memory pressure |
| `falkordb` | Redis memory, connection errors |
| `langfuse-*` | Trace ingestion, ClickHouse write pressure |

### Key Log Patterns to Watch

```
# Cognee ingestion progress
[cognee] Ingesting 540 files → dataset 'docs-ml'
[cognee] [####----] 270/540 (50%)

# Cognify status
[cognee] Entity extraction started: 2,242 documents
[cognee] Relationship inference: 8,476 edges created
[cognee] Cognify complete: 12.3s, 847,000 tokens, $4.23 cost

# LLM API errors
[cognee] LLMAPIKeyNotSetError — check DEEPSEEK_API_KEY
[cognee] RateLimitError — reduce concurrent cognify batches
```

## Beszel — Server Metrics Dashboard

**Stack**: `infrastructure/stacks/beszel/`  
**Port**: 8090

### Role in the Cognition Pipeline

Beszel monitors resource utilization across all 3 physical hosts during cognition operations:

| Host | Monitored Resources | Why It Matters |
|:--|:--|:--|
| `cax41-hetzner` (32 GB) | Memory, CPU | Neo4j + FalkorDB + Langfuse run here; KG build is memory-intensive |
| `arm1-oci` (24 GB) | CPU, Disk | Lakehouse + LakeFS + Dozzle run here; S3 I/O during cognify |
| `bunchloch` (48 GB unified) | Memory, GPU | Cognee + Graphiti run here; LLM processing uses unified memory |

### Alerts to Configure

```
ALERT: bunchloch_memory > 40GB
  → Neo4j + Cognee + LLM model competing for unified memory
  → Action: Reduce concurrent cognify batches

ALERT: hetzner_disk > 80%
  → LanceDB vector indexes growing
  → Action: Prune old indexes, increase disk

ALERT: arm1_cpu > 90% sustained 5min
  → Lakehouse S3 operations saturating CPU
  → Action: Throttle concurrent data writes
```

## Combined Health Check

```bash
#!/bin/bash
# Check all cognition pipeline components

echo "=== Cognition Pipeline Health ==="

# Cognee
curl -s -o /dev/null -w "Cognee:    %{http_code}\n" http://localhost:8100/docs

# Neo4j (via Graphiti stack)
curl -s -o /dev/null -w "Neo4j:     %{http_code}\n" http://localhost:7474

# FalkorDB
curl -s -o /dev/null -w "FalkorDB:  %{http_code}\n" http://localhost:6379

# Lakehouse (Garage S3)
curl -s -o /dev/null -w "Garage:    %{http_code}\n" http://localhost:3900

# LakeFS
curl -s -o /dev/null -w "LakeFS:    %{http_code}\n" http://localhost:8000/health

# Dozzle
curl -s -o /dev/null -w "Dozzle:    %{http_code}\n" http://localhost:7070

# Beszel
curl -s -o /dev/null -w "Beszel:    %{http_code}\n" http://localhost:8090

# CCC index
ls -lh .cocoindex_code/target_sqlite.db | awk '{print "CCC:       " $5 " index"}'

echo "================================"
```
