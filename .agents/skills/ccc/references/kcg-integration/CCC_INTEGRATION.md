# CCC & CocoIndex Integration — Codebase Semantic Search

How CocoIndex Code (CCC) and the CocoIndex framework provide semantic code search and data transformation pipelines for the Kings' College Galway project.

## CCC — CocoIndex Code

CCC provides semantic code search over the entire polyglot monorepo. It uses CocoIndex flows to build a vector index of all source files, enabling agents to search by meaning rather than text matching.

### Current Setup

```bash
# Check if index exists
ls -la .cocoindex_code/target_sqlite.db  # 35+ MB index database

# Index the codebase (incremental — only changed files)
bun run ccc:index

# Search by meaning
bun run ccc:search "Dagster asset partition definition"
bun run ccc:search "Pangolin private resource Traefik label"
bun run ccc:search "BAML extraction function"
```

### MCP Server

```json
{
  "mcp": {
    "cocoindex-code": {
      "type": "local",
      "command": ["ccc", "mcp"]
    }
  }
}
```

This exposes the `cocoindex-code_search` tool to all agents, which is the **primary code discovery tool** — per the AGENTS.md instruction: "always use ccc before grep/find."

### Index Update Policy

```bash
# Manual incremental refresh (fast — only indexes changed files)
bun run ccc:index

# Full rebuild (slow — re-indexes entire codebase)
bun run ccc:init  # Clears existing index
bun run ccc:index  # Full build from scratch

# Scheduled re-index (via turbo.json)
bun run turbo ccc:index
```

### Search API

```python
# Programmatic search via CCC CLI
import subprocess

def ccc_search(query: str, limit: int = 5) -> list[dict]:
    result = subprocess.run(
        ["bun", "run", "ccc:search", query, "--limit", str(limit)],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)
```

### Per-Agent Indexing

Each agent can trigger re-indexing for its domain before searching, ensuring fresh results:

```
# Agent workflow:
1. ccc:index          # Refresh index (incremental, fast)
2. ccc:search "..."   # Search with current index
```

## CocoIndex Flow Examples

The `docs/data_engineering/cocoindex/` directory contains 25+ example flows:

### Text Embedding with LanceDB

From `cocoindex/text_embedding_lancedb/`:

```python
from cocoindex import Flow, TextEmbedding, LanceDB

flow = Flow("text_embedding")
    .source(TextEmbedding.from_markdown("./docs/**/*.md"))
    .transform(LanceDB("curriculum_embeddings"))

flow.run()
```

### Document Knowledge Graph

From `cocoindex/docs_to_knowledge_graph/`:

```python
flow = Flow("docs_kg")
    .source(DocumentSource("./docs/**/*.md"))
    .transform(LLMExtraction(
        model="deepseek-v4-pro",
        schema=KnowledgeGraphSchema,
    ))
    .sink(Neo4jSink("bolt://localhost:7687"))
```

### Code Embedding

From `cocoindex/code_embedding/`:

```python
flow = Flow("code_index")
    .source(CodeSource("./**/*.py", chunker="tree-sitter"))
    .transform(TextEmbedding("code-embeddings"))
    .sink(LanceDBSink("./.cocoindex_code"))
```

### Multi-Format Indexing with ColPali

From `cocoindex/multi_format_indexing/`:

```python
flow = Flow("visual_docs")
    .source(MultiFormatSource("./docs/**/*.{pdf,png,jpg}"))
    .transform(ColPaliEmbedding())
    .sink(QdrantSink("http://localhost:6333"))
```

## CCC + Cognee Workflow

```
┌─────────────────┐     ┌─────────────────┐
│       CCC       │     │     Cognee       │
│ (code search)   │     │  (docs cognition) │
├─────────────────┤     ├─────────────────┤
│ Source: code    │     │ Source: .md docs │
│ Index: SQLite   │     │ Graph: Neo4j     │
│ Search: vector  │     │ Search: GraphRAG │
│ MCP: ccc mcp    │     │ MCP: cognee-mcp  │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
            ┌────────▼────────┐
            │   Agent Query   │
            │ "find how BAML  │
            │  extraction is  │
            │  implemented"   │
            └────────┬────────┘
                     │
         ┌───────────┼───────────┐
         ▼                       ▼
    CCC returns            Cognee returns
    code files             documentation
    (implementation)       (architecture, patterns)
```

## Index File Structure

The `.cocoindex_code/` directory:

```
.cocoindex_code/
├── cocoindex.db          # Flow state (incremental tracking)
├── settings.yml          # Index configuration
└── target_sqlite.db      # Semantic search index (~35 MB)
                          # Contains vector embeddings for all source files
                          # Queryable via ccc search or SQLite
```

## Performance Notes

| Operation | Scope | Time |
|:--|:--|:--|
| `ccc:index` (incremental) | Changed files only | <10s |
| `ccc:index` (full rebuild) | Entire monorepo | ~2-5 min |
| `ccc:search` | Semantic query | <1s |
| `ccc mcp` server | Continuous | Background |

## Related Documentation

- **CocoIndex Flows**: `docs/data_engineering/cocoindex/` — 25 example flows
- **CocoIndex API Research**: `docs/data_engineering/cocoindex/cocoindex-api-research.md`
- **CCC Skill**: `.agents/skills/ccc/SKILL.md` — Agent usage guide
- **AGENTS.md**: Root instruction — "always use ccc before grep/find"
