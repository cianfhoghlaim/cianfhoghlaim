# Códeolas Demo

Standalone demonstration of the Code Analysis and Repository Intelligence platform.

## Quick Start

```bash
cd sruth/tuatha/codeolas
python demo/run_demo.py
```

## What This Demo Demonstrates

### 1. Code Indexing
- **Tree-sitter parsers** for 29 programming languages
- **cAST chunking** (syntax-aware code splitting)
- Preserves function/class boundaries
- Extracts imports, exports, dependencies

### 2. Semantic Search
- **BGE-M3 embeddings** (1024 dimensions)
- **LanceDB** vector search
- Hybrid vector + keyword queries
- Filter by language, file type, symbol type

### 3. Multi-hop Research
- **Iterative search** with convergence detection
- Knowledge graph traversal
- Context-aware query refinement
- Automated synthesis of findings

### 4. Knowledge Graph
- **40+ relationship types** (IMPORTS, CALLS, INHERITS, etc.)
- Neo4j/Cypher support
- Code dependency visualization
- Impact analysis

### 5. Reranking
- **Jina API** (15-20% precision boost)
- **Cohere API** (12-18% precision boost)
- **Aliyun API** (10-15% precision boost)
- Optional: No reranking (faster)

### 6. Documentation Generation
- **.arch.md files** with architecture docs
- Auto-generated from code structure
- Includes data flow diagrams
- Relationship mappings

### 7. MCP Server
- **Claude Code integration** via JSON-RPC
- 6 tools for code search and research
- Real-time codebase exploration
- No API keys required

## Requirements

This demo uses mock data and requires minimal dependencies:

```bash
pip install httpx
```

For the full platform, install via pip:

```bash
pip install codeolas
```

## Demo Structure

```
demo/
├── __init__.py
├── run_demo.py       # Main demo script
└── README.md         # This file
```

## Running the Demo

The demo runs entirely offline with mock data.

```bash
# From the sruth/tuatha/codeolas directory
python demo/run_demo.py
```

The demo will showcase:
- All 10 major features
- Mock code chunks (Python, JavaScript, etc.)
- Example search results and graph queries
- CLI usage examples

## Full Platform Usage

To use códeolas with your own codebase:

### Installation

```bash
pip install codeolas
```

### Basic Usage

```python
from codeolas import CodebaseAnalyzer

# Initialize analyzer
analyzer = CodebaseAnalyzer("/path/to/repo")

# Index the repository
await analyzer.index()

# Semantic search
results = await analyzer.search("authentication logic")
for result in results:
    print(f"{result.chunk.file_path}:{result.chunk.start_line}")
    print(f"  {result.chunk.name} ({result.score:.2f})")

# Multi-hop research
research = await analyzer.deep_research(
    "How does the auth system work?",
    max_hops=3
)
print(research["synthesis"])

# Generate architecture docs
await analyzer.generate_arch_doc("ARCHITECTURE.md")
```

### CLI Commands

```bash
# Index a repository
codeolas index --repo /path/to/repo

# Search for code
codeolas search "database connection" --limit 10

# Deep research
codeolas research "How does authentication work?"

# Generate architecture docs
codeolas arch --output ARCHITECTURE.md

# Query knowledge graph
codeolas graph "MATCH (f:Function) RETURN f"

# Start MCP server
codeolas mcp
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  CodebaseAnalyzer                            │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Tree-sitter │      │ BGE-M3      │      │ Knowledge   │
│ Parsers     │      │ Embeddings  │      │ Graph       │
│             │      │             │      │             │
│ • 29 langs  │      │ • 1024 dim  │      │ • 40 types  │
│ • cAST      │      │ • LanceDB   │      │ • Neo4j     │
└─────────────┘      └─────────────┘      └─────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Search      │      │ Multi-hop   │      │ Reranking   │
│             │      │ Research    │      │             │
│ • Vector    │      │ • Converge  │      │ • Jina      │
│ • Keyword   │      │ • Traverse  │      │ • Cohere    │
└─────────────┘      └─────────────┘      └─────────────┘
```

## Critical Constraints

### DuckDB Single-Threaded Access
```python
# WRONG: Concurrent access causes segfault
with ThreadPoolExecutor() as executor:
    executor.map(execute_query, queries)

# RIGHT: Use SerialDatabaseExecutor
from codeolas.storage import SerialDatabaseExecutor

executor = SerialDatabaseExecutor()
result = await executor.execute(query)
```

### Embedding Batch Minimum
```python
# WRONG: Unbatched (100x slower)
for text in texts:
    embedding = embed(text)  # ~100s for 1000 texts

# RIGHT: Batched
embeddings = embed_batch(texts, batch_size=100)  # ~1s for 1000 texts
```

### HNSW Index Management
```python
if row_count > 50:
    table.drop_index("vector_idx")
    table.add(embeddings)
    table.create_index("vector_idx", type="IVF_HNSW")
```

## Supported Languages

Tree-sitter parsers for 29 languages:

**Popular**: Python, JavaScript, TypeScript, Go, Rust, Java, C++, C, C#
**Web**: HTML, CSS, JSON, YAML, Markdown, Dockerfile
**Data**: SQL, R, MATLAB
**Scripting**: Ruby, PHP, Swift, Kotlin, Scala, Shell
**Functional**: Haskell, Clojure, Elixir, Erlang, Lua

## Relationship Types

40+ relationship types for knowledge graph:

**Code**: IMPORTS, EXPORTS, CALLS, INSTANTIATES
**OO**: INHERITS, IMPLEMENTS, OVERRIDES, EXTENDS
**Data**: QUERIES, UPDATES, DELETES, CREATES, READS, WRITES
**Arch**: CONTAINS, REFERENCES, COMPONENT_OF, CONFIGURATION_FOR
**Async**: EMITS, LISTENS, SUBSCRIBES, PUBLISHES
**Utils**: VALIDATES, TRANSFORMS, SERIALIZES, DESERIALIZES
**Patterns**: ADAPTER, BRIDGE, FACADE, STRATEGY, FACTORY, BUILDER
**Testing**: TESTS, MOCKS, STUBS, SPYS, PROXIES

## MCP Server Tools

When using the MCP server with Claude Code:

1. **codeolas_search** - Search code semantically
2. **codeolas_research** - Multi-hop code research
3. **codeolas_graph_query** - Query knowledge graph
4. **codeolas_get_chunk** - Get code chunk by ID
5. **codeolas_list_files** - List indexed files
6. **codeolas_generate_docs** - Generate .arch.md

Example usage in Claude Code:

```
User: "Search for authentication logic"
Claude: [Calls codeolas_search(query="authentication")]
  Found 5 results in src/auth/

User: "How does the auth system work?"
Claude: [Calls codeolas_research(query="auth system flow")]
  Synthesis: The auth system uses JWT tokens...
```

## Performance

**Typical Repository Statistics**

| Size | Files | Index Time | Query Latency |
|------|-------|------------|---------------|
| Small | <1k | 2s | 50ms |
| Medium | 1k-10k | 15s | 150ms |
| Large | 10k-100k | 2m | 500ms |
| Huge | >100k | 10m | 1.5s |

**Memory Usage**

Repository: 10k files, 500k chunks
- Embeddings: 2GB (BGE-M3, 1024 dim, float32)
- Metadata: 500MB
- Total: ~2.5GB

**Storage Requirements**

- Vectors: 4KB per chunk (1024 * 4 bytes)
- Metadata: 1KB per chunk
- Total: ~5KB per chunk

Example: 100k chunks = 500MB storage

## Related Projects

- **crypteolas** - Crypto protocol analysis (uses códeolas for code intelligence)
- **oideachas** - Education curriculum processing
- **tuath** - Community content management

## Support

For issues or questions:
- Main README: [sruth/tuatha/codeolas/README.md](../README.md)
- Tuath workspace README: [../../README.md](../../README.md)
- PyPI: https://pypi.org/project/codeolas/
- Forgejo: https://git.cianfhoghlaim.ie/cianfhoghlaim/sruth

## License

MIT License - see [LICENSE](../LICENSE) for details.
