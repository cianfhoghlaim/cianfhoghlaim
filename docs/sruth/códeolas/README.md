# Códeolas - Code Analysis and Repository Intelligence

[![PyPI](https://img.shields.io/pypi/v/codeolas)](https://pypi.org/project/codeolas/)
[![Python](https://img.shields.io/pypi/pyversions/codeolas)](https://pypi.org/project/codeolas/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A comprehensive library for semantic code search, knowledge graph construction,
and documentation generation. Part of the [Cianfhoghlaim](../../README.md) platform.

## Features

- **cAST Chunking** - Syntax-aware code splitting (29 languages via Tree-sitter)
- **Semantic Search** - LanceDB vector search with BGE-M3 embeddings
- **Multi-hop Research** - Iterative search with convergence detection
- **Reranking** - Jina/Cohere/Aliyun API integration (15-20% precision boost)
- **Knowledge Graph** - 40+ relationship types for code analysis
- **MCP Server** - Claude Code integration via JSON-RPC
- **Doc Generation** - .arch.md and changelog generation

## Installation

```bash
pip install codeolas

# With all optional dependencies
pip install codeolas[all]

# From Forgejo Packages
pip install --index-url https://git.cianfhoghlaim.ie/api/packages/cianfhoghlaim/pypi/simple codeolas
```

## Quick Start

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
research = await analyzer.deep_research("How does the auth system work?")
print(research["synthesis"])

# Generate architecture docs
await analyzer.generate_arch_doc("ARCHITECTURE.md")
```

## CLI Usage

```bash
# Index a repository
codeolas index --repo /path/to/repo

# Search for code
codeolas search "database connection" --limit 10

# Deep research
codeolas research "How does authentication work?"

# Generate architecture docs
codeolas arch --output ARCHITECTURE.md

# Start MCP server
codeolas mcp
```

## Package Structure

```
codeolas/
├── core/                 # Core functionality
│   ├── analyzer.py       # Main CodebaseAnalyzer API
│   ├── chunking.py       # cAST algorithm
│   ├── embeddings.py     # BGE-M3 embeddings
│   ├── entities.py       # Entity deduplication
│   ├── config.py         # Configuration
│   └── types.py          # 40+ relationship types
├── search/               # Search capabilities
│   ├── multihop.py       # Multi-hop research
│   └── reranker.py       # Result reranking
├── graph/                # Knowledge graph
│   ├── builder.py        # Graph construction
│   └── queries.py        # Cypher queries
├── generators/           # Documentation
│   ├── arch.py           # .arch.md generation
│   └── changelog.py      # Changelog generation
├── storage/              # Storage backends
│   ├── lance.py          # LanceDB integration
│   └── serial_executor.py # Single-threaded safety
└── mcp/                  # MCP server
    ├── server.py         # JSON-RPC server
    └── tools.py          # Tool definitions
```

## Configuration

Environment variables:

```bash
# Repository
CODEOLAS_REPO_PATH=/path/to/repo

# LanceDB storage
LANCEDB_URI=./storage/data/lancedb
LANCEDB_TABLE_PREFIX=codeolas_

# Embedding model
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIMENSION=1024

# Reranking (optional)
RERANK_PROVIDER=jina  # jina, cohere, aliyun, or none
RERANK_API_KEY=your-api-key

# Memgraph (optional)
MEMGRAPH_URI=bolt://localhost:7687
```

## Critical Constraints

| Constraint | Rule | Impact |
|------------|------|--------|
| **DuckDB** | SINGLE-THREADED ONLY | Use SerialDatabaseExecutor |
| **Embeddings** | BATCH MINIMUM 100 | 100x performance difference |
| **HNSW Index** | DROP before bulk >50 rows | 20x speedup |

## Development

```bash
# Clone and install
git clone https://git.cianfhoghlaim.ie/cianfhoghlaim/sruth.git
cd sruth/códeolas

# Install with dev dependencies
uv sync --all-extras

# Run tests
uv run pytest tests/ -v

# Run linting
uv run ruff check codeolas/

# Build package
uv build
```

## Related Projects

- **crypteolas** - Crypto protocol analysis (imports codeolas for code intelligence)
- **oideachas** - Education curriculum processing
- **tuath** - Community content management

## License

MIT License - see [LICENSE](LICENSE) for details.
