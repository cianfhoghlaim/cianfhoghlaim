# GitHub Intelligence

A unified GitHub data intelligence platform combining DLT, CocoIndex, Cognee, and Marimo for comprehensive repository analysis.

## Features

- **GitHub REST API Ingestion** - Issues, PRs, commits, workflows via DLT pipelines
- **Semantic Code Search** - Vector, FTS, and hybrid search with LanceDB
- **Knowledge Graphs** - Entity extraction and relationship mapping with Cognee + Memgraph
- **Interactive Analysis** - Marimo notebooks with ibis + DuckDB

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Intelligence                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ GitHub API  │    │ Code Index  │    │ Knowledge   │         │
│  │    (DLT)    │    │ (CocoIndex) │    │   Graph     │         │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘         │
│         │                  │                  │                 │
│         ▼                  ▼                  ▼                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   DuckDB    │    │   LanceDB   │    │  Memgraph   │         │
│  │ (Analytics) │    │  (Vectors)  │    │   (Graph)   │         │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│                            ▼                                    │
│                 ┌─────────────────────┐                        │
│                 │   Marimo Notebooks  │                        │
│                 │   (ibis + altair)   │                        │
│                 └─────────────────────┘                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install the project
pip install -e .
```

### 2. Configure Secrets

```bash
# Copy the example secrets file
cp .dlt/secrets.toml.example .dlt/secrets.toml

# Edit with your GitHub token
# Get one from: https://github.com/settings/tokens
```

**`.dlt/secrets.toml`:**
```toml
[sources.github_api]
access_token = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 3. Issue DLT License (Optional)

For dlthub transformations:

```bash
dlt license issue dlthub.transformation
dlt license info  # Verify
```

### 4. Start Memgraph (Optional)

For knowledge graph features:

```bash
# Linux/macOS
curl https://install.memgraph.com | sh

# Windows
iwr https://windows.memgraph.com | iex

# Access Memgraph Lab at http://localhost:3000
```

### 5. Run Notebooks

```bash
# GitHub API exploration
marimo edit notebooks/01_github_api_explorer.py

# Semantic code search
marimo edit notebooks/02_code_search.py

# Knowledge graph
marimo edit notebooks/03_knowledge_graph.py

# Unified dashboard
marimo edit notebooks/04_unified_dashboard.py
```

## Project Structure

```
github-intelligence/
├── pyproject.toml              # Project dependencies
├── README.md                   # This file
├── config/
│   ├── repos.yaml              # Repository configurations
│   └── .env.example            # Environment template
├── .dlt/
│   ├── config.toml             # DLT configuration
│   └── secrets.toml.example    # Secrets template
├── pipelines/
│   └── github_api/             # GitHub REST API pipeline
│       ├── source.py           # DLT source definition
│       ├── resources.py        # API resource configs
│       └── transformations.py  # ibis transformations
├── cocoindex/
│   ├── config.py               # Indexing configuration
│   ├── embeddings.py           # Embedding generation
│   ├── search.py               # LanceDB search
│   └── flows/
│       ├── code_indexing.py    # Code → vectors
│       └── docs_indexing.py    # Docs → vectors + graph
├── cognee/
│   ├── processor.py            # Cognee + Memgraph
│   ├── entity_extraction.py    # Entity/relationship extraction
│   └── cypher_queries.py       # Common Cypher queries
├── notebooks/
│   ├── 01_github_api_explorer.py
│   ├── 02_code_search.py
│   ├── 03_knowledge_graph.py
│   └── 04_unified_dashboard.py
└── shared/
    ├── duckdb_destination.py
    ├── lancedb_destination.py
    └── memgraph_client.py
```

## Usage

### GitHub API Pipeline

```python
from pipelines.github_api import make_github_source, run_github_pipeline

# Quick run
load_info = run_github_pipeline(
    owner="dlt-hub",
    repo="dlt",
    resources=["issues", "pull_requests"],
)

# Or create a custom source
import dlt

source = make_github_source(
    owner="dlt-hub",
    repo="dlt",
    resources=["issues", "commits", "workflow_runs"],
    days_back=30,
)

pipeline = dlt.pipeline(
    pipeline_name="my_github_pipeline",
    destination="duckdb",
    dataset_name="github_data",
)

load_info = pipeline.run(source)
```

### Code Indexing

```python
from cocoindex.config import CodeIndexingConfig
from cocoindex.flows.code_indexing import CodeIndexingFlow

config = CodeIndexingConfig(
    repo_owner="dlt-hub",
    repo_name="dlt",
    included_patterns=["*.py", "*.md"],
)

flow = CodeIndexingFlow(config)
num_chunks = flow.index_directory("./path/to/repo")

# Search
results = flow.search("how to create a pipeline", limit=10)
```

### Semantic Search

```python
from cocoindex.search import LanceDBSearch

search = LanceDBSearch(
    db_uri="./data/github_intelligence.lancedb",
    table_name="dlt_hub_dlt_code",
)

# Vector search
results = search.vector_search("create pipeline", limit=10)

# Full-text search
results = search.fts_search("dlt.pipeline", limit=10)

# Hybrid search with reranking
results = search.hybrid_search("incremental loading", limit=10, reranker="rrf")
```

### Knowledge Graph

```python
from cognee.processor import CogneeMemgraphProcessor

processor = CogneeMemgraphProcessor()

# Process documents
await processor.process_documents([
    {"content": "...", "filename": "doc1.md"},
    {"content": "...", "filename": "doc2.md"},
])

# Search
results = await processor.search("What is DLT?")

# Run Cypher queries
entities = processor.run_cypher("""
    MATCH (e:Entity)-[r:RELATIONSHIP]->(related)
    WHERE e.value CONTAINS 'Pipeline'
    RETURN e.value, r.predicate, related.value
    LIMIT 10
""")
```

## Configuration

### Repository Configuration (`config/repos.yaml`)

```yaml
repositories:
  dlt-hub:
    owner: dlt-hub
    repo: dlt
    git_ref: devel
    included_patterns:
      - "*.py"
      - "*.md"
    index_code: true
    index_docs: true
    api_resources:
      - issues
      - pull_requests
      - commits
```

### Environment Variables

```bash
# GitHub
GITHUB_ACCESS_TOKEN=ghp_xxx

# LLM (for Cognee)
LLM_API_KEY=sk-xxx
LLM_MODEL=openai/gpt-4o-mini

# Memgraph
GRAPH_DATABASE_URL=bolt://localhost:7687

# Databases
DUCKDB_PATH=./data/github_intelligence.duckdb
LANCEDB_URI=./data/github_intelligence.lancedb
```

## Patterns & Best Practices

This project follows patterns from:

| Source | Pattern |
|--------|---------|
| [small-data-sf-2025](https://github.com/dlt-hub/small-data-sf-2025) | RESTAPIConfig, dlthub transformations, marimo integration |
| [dlt_lance.py](https://lancedb.github.io/lancedb/) | LanceDB adapter, hybrid search, rerankers |
| [dlt_cognee_memgraph.py](https://github.com/cognee-ai/cognee) | Cognee processor, Memgraph integration |
| [multi_github_code_indexing](https://cocoindex.io) | CocoIndex flows, tree-sitter chunking |
| [docs_to_knowledge_graph](https://cocoindex.io) | Entity extraction, graph schema |

## Resources

- [DLT Documentation](https://dlthub.com/docs)
- [LanceDB Documentation](https://lancedb.github.io/lancedb/)
- [CocoIndex Documentation](https://cocoindex.io)
- [Cognee Documentation](https://github.com/cognee-ai/cognee)
- [Memgraph Documentation](https://memgraph.com/docs)
- [Marimo Documentation](https://docs.marimo.io)
- [Ibis Documentation](https://ibis-project.org/docs)

## Future Extensions

- [ ] Crawl4AI for website scraping
- [ ] PDF processing with Marker
- [ ] Cloudflare R2 storage
- [ ] Dagster orchestration
- [ ] FalkorDB as alternative graph backend

## License

This project uses patterns from Apache 2.0 licensed projects (dlt, CocoIndex).
