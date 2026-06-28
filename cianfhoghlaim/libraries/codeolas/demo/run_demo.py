#!/usr/bin/env python3
"""
Códeolas - Code Analysis and Repository Intelligence Demo.

Demonstrates the complete flow:
1. Code indexing with tree-sitter (29 languages supported)
2. cAST chunking (syntax-aware code splitting)
3. Semantic search with LanceDB and BGE-M3 embeddings
4. Multi-hop research with convergence detection
5. Knowledge graph construction (40+ relationship types)
6. Reranking with Jina/Cohere/Aliyun APIs
7. Documentation generation (.arch.md files)
8. MCP server for Claude Code integration

Usage:
    cd sruth/códeolas
    python demo/run_demo.py
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any

# This demo uses mock data and requires no external dependencies
# All demonstrations are offline with pre-populated example data


# ============================================================================
# MOCK DATA FOR OFFLINE DEMO
# ============================================================================

MOCK_CODE_CHUNKS = [
    {
        "file_path": "src/auth/authentication.py",
        "name": "authenticate_user",
        "type": "function",
        "language": "Python",
        "start_line": 42,
        "end_line": 67,
        "code": "def authenticate_user(username: str, password: str) -> bool:\n    '''Authenticate user with credentials.'''\n    user = db.query(User).filter_by(username=username).first()\n    if user and verify_password(password, user.password_hash):\n        return True\n    return False",
        "exports": ["authenticate_user"],
        "imports": ["User", "db", "verify_password"],
    },
    {
        "file_path": "src/auth/middleware.py",
        "name": "AuthMiddleware",
        "type": "class",
        "language": "Python",
        "start_line": 10,
        "end_line": 45,
        "code": "class AuthMiddleware:\n    '''JWT authentication middleware.'''\n    def __init__(self, secret_key: str):\n        self.secret_key = secret_key\n\n    def process_request(self, request: Request) -> Response:\n        token = request.headers.get('Authorization')\n        if not token:\n            return Response(status=401)",
        "exports": ["AuthMiddleware"],
        "imports": ["Request", "Response"],
    },
    {
        "file_path": "src/database/connection.py",
        "name": "DatabaseConnection",
        "type": "class",
        "language": "Python",
        "start_line": 15,
        "end_line": 52,
        "code": "class DatabaseConnection:\n    '''Single-threaded database connection manager.'''\n    def __init__(self, db_path: str):\n        self.db_path = db_path\n        self._connection = None\n\n    def connect(self):\n        if not self._connection:\n            self._connection = duckdb.connect(self.db_path)\n        return self._connection",
        "exports": ["DatabaseConnection"],
        "imports": ["duckdb"],
    },
]

MOCK_SEARCH_RESULTS = [
    {
        "chunk": MOCK_CODE_CHUNKS[0],
        "score": 0.94,
        "highlights": ["authenticate_user", "password", "credentials"],
    },
    {
        "chunk": MOCK_CODE_CHUNKS[1],
        "score": 0.87,
        "highlights": ["AuthMiddleware", "JWT", "token"],
    },
]

MOCK_GRAPH_DATA = {
    "nodes": [
        {"id": "authenticate_user", "type": "function", "file": "src/auth/authentication.py"},
        {"id": "AuthMiddleware", "type": "class", "file": "src/auth/middleware.py"},
        {"id": "DatabaseConnection", "type": "class", "file": "src/database/connection.py"},
        {"id": "User", "type": "model", "file": "src/models/user.py"},
    ],
    "relationships": [
        {"from": "AuthMiddleware", "to": "authenticate_user", "type": "CALLS"},
        {"from": "authenticate_user", "to": "User", "type": "QUERIES"},
        {"from": "authenticate_user", "to": "DatabaseConnection", "type": "USES"},
    ],
}

SUPPORTED_LANGUAGES = [
    "Python", "JavaScript", "TypeScript", "Go", "Rust", "Java", "C++", "C",
    "C#", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "Clojure", "Elixir",
    "Erlang", "Haskell", "Lua", "Perl", "R", "MATLAB", "Shell", "SQL",
    "HTML", "CSS", "JSON", "YAML", "Markdown", "Dockerfile",
]

RELATIONSHIP_TYPES = [
    "IMPORTS", "EXPORTS", "CALLS", "INSTANTIATES", "INHERITS", "IMPLEMENTS",
    "QUERIES", "UPDATES", "DELETES", "CREATES", "READS", "WRITES",
    "CONTAINS", "REFERENCES", "ANNOTATES", "DECORATES", "WRAPS", "EXTENDS",
    "OVERRIDES", "EMITS", "LISTENS", "SUBSCRIBES", "PUBLISHES", "MUTATES",
    "VALIDATES", "TRANSFORMS", "SERIALIZES", "DESERIALIZES", "COMPONENT_OF",
    "CONFIGURATION_FOR", "TESTS", "MOCKS", "STUBS", "SPYS", "PROXIES",
    "ADAPTER", "BRIDGE", "FACADE", "STRATEGY", "FACTORY", "BUILDER",
]


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

async def demo_code_indexing():
    """Demonstrate code indexing capabilities."""
    print("\n" + "=" * 80)
    print("1. CODE INDEXING DEMO")
    print("=" * 80)

    print("\n--- Supported Languages (Tree-sitter parsers) ---")
    print(f"Total: {len(SUPPORTED_LANGUAGES)} languages")
    print("\n" + ", ".join(SUPPORTED_LANGUAGES[:15]) + ", ...")

    print("\n--- cAST Chunking Algorithm ---")
    print("""
Syntax-aware code splitting preserves:
  - Function/class boundaries
  - Import statements
  - Export declarations
  - Nesting hierarchy
  - Comment blocks

Example Python chunk:
  function: authenticate_user
  imports: [User, db, verify_password]
  exports: [authenticate_user]
  lines: 42-67
  parent: auth_module
    """)

    print("\n--- Sample Code Chunks ---")
    for chunk in MOCK_CODE_CHUNKS[:3]:
        print(f"\n  File: {chunk['file_path']}")
        print(f"  Name: {chunk['name']} ({chunk['type']})")
        print(f"  Lines: {chunk['start_line']}-{chunk['end_line']}")
        print(f"  Language: {chunk['language']}")
        print(f"  Imports: {', '.join(chunk['imports'][:3])}")
        print(f"  Exports: {', '.join(chunk['exports'])}")


async def demo_semantic_search():
    """Demonstrate semantic search."""
    print("\n" + "=" * 80)
    print("2. SEMANTIC SEARCH DEMO")
    print("=" * 80)

    query = "user authentication and password verification"
    print(f"\n--- Query: '{query}' ---")
    print("\n--- Search Results (BGE-M3 Embeddings) ---")

    for i, result in enumerate(MOCK_SEARCH_RESULTS, 1):
        chunk = result["chunk"]
        print(f"\n  Result {i}:")
        print(f"    File: {chunk['file_path']}")
        print(f"    Name: {chunk['name']}")
        print(f"    Type: {chunk['type']}")
        print(f"    Score: {result['score']:.3f}")
        print(f"    Highlights: {', '.join(result['highlights'])}")
        print(f"    Code Preview:")
        for line in chunk['code'].split('\n')[:3]:
            print(f"      {line}")

    print("\n--- Search Configuration ---")
    print("""
# Example: Semantic Search
from lancedb import connect
from codeolas import CodebaseAnalyzer

analyzer = CodebaseAnalyzer("/path/to/repo")
await analyzer.index()

results = await analyzer.search(
    query="authentication logic",
    limit=10,
    filters={"language": "Python", "type": "function"},
)
    """)


async def demo_multihop_research():
    """Demonstrate multi-hop research."""
    print("\n" + "=" * 80)
    print("3. MULTI-HOP RESEARCH DEMO")
    print("=" * 80)

    query = "How does the authentication system handle JWT tokens and database connections?"

    print(f"\n--- Research Query: '{query}' ---")
    print("\n--- Multi-Hop Research Process ---")

    hops = [
        {
            "hop": 1,
            "query": "authentication system",
            "results": 5,
            "top_entities": ["authenticate_user", "AuthMiddleware"],
        },
        {
            "hop": 2,
            "query": "JWT token validation",
            "results": 3,
            "top_entities": ["JWTUtils", "TokenValidator"],
        },
        {
            "hop": 3,
            "query": "database connection management",
            "results": 4,
            "top_entities": ["DatabaseConnection", "ConnectionPool"],
        },
    ]

    for hop in hops:
        print(f"\n  Hop {hop['hop']}:")
        print(f"    Query: {hop['query']}")
        print(f"    Results: {hop['results']} chunks")
        print(f"    Top Entities: {', '.join(hop['top_entities'])}")

    print("\n--- Convergence Detection ---")
    print("  Converged after 3 hops (overlap > 50%)")
    print("  Final entities: 12 unique, 6 repeated")

    print("\n--- Synthesis ---")
    print("""
The authentication system uses JWT tokens for stateless authentication:
1. Tokens are validated in AuthMiddleware.process_request()
2. User credentials are verified via authenticate_user()
3. Database connections use single-threaded DatabaseConnection
4. No connection pooling (DuckDB constraint)

Files involved:
  - src/auth/authentication.py
  - src/auth/middleware.py
  - src/database/connection.py
    """)


async def demo_knowledge_graph():
    """Demonstrate knowledge graph construction."""
    print("\n" + "=" * 80)
    print("4. KNOWLEDGE GRAPH DEMO")
    print("=" * 80)

    print("\n--- Relationship Types (40+ supported) ---")
    print(f"Total: {len(RELATIONSHIP_TYPES)} relationship types")
    print("\n" + ", ".join(RELATIONSHIP_TYPES[:20]) + ", ...")

    print("\n--- Sample Graph Structure ---")
    graph = MOCK_GRAPH_DATA
    print("\nNodes:")
    for node in graph["nodes"][:4]:
        print(f"  - {node['id']} ({node['type']}) in {node['file']}")

    print("\nRelationships:")
    for rel in graph["relationships"][:4]:
        print(f"  - ({rel['from']}) -[{rel['type']}]-> ({rel['to']})")

    print("\n--- Cypher Query Examples ---")
    print("""
# Find all functions that authenticate users
MATCH (f:Function {name: 'authenticate_user'})
RETURN f.file_path, f.start_line, f.end_line

# Find classes that use authentication
MATCH (c:Class)-[:USES]->(a:Function)
WHERE a.name CONTAINS 'auth'
RETURN c.name, c.file_path

# Find call chains
MATCH path = (start:Function)-[:CALLS*]->(end:Function)
WHERE start.name = 'authenticate_user'
RETURN path
    """)


async def demo_reranking():
    """Demonstrate result reranking."""
    print("\n" + "=" * 80)
    print("5. RERANKING DEMO")
    print("=" * 80)

    print("\n--- Supported Reranking Providers ---")
    providers = [
        ("Jina", "15-20% precision boost", "https://api.jina.ai/v1/rerank"),
        ("Cohere", "12-18% precision boost", "https://api.cohere.ai/v1/rerank"),
        ("Aliyun", "10-15% precision boost", "https://dashscope.aliyuncs.com/api/v1"),
    ]

    for name, benefit, endpoint in providers:
        print(f"  {name:<10} {benefit:<25} {endpoint}")

    print("\n--- Reranking Process ---")
    print("""
Before Reranking:
  1. authenticate_user()          score: 0.87
  2. authenticate_admin()         score: 0.84
  3. verify_token()              score: 0.82
  4. hash_password()             score: 0.79

After Jina Reranking (query: "user login"):
  1. authenticate_user()          score: 0.94  (+0.07)
  2. verify_token()              score: 0.89  (+0.07)
  3. authenticate_admin()         score: 0.75  (-0.09)
  4. hash_password()             score: 0.68  (-0.11)
    """)


async def demo_documentation_generation():
    """Demonstrate .arch.md generation."""
    print("\n" + "=" * 80)
    print("6. DOCUMENTATION GENERATION DEMO")
    print("=" * 80)

    print("\n--- Generated .arch.md File ---")
    print("""
# src/auth/ - Authentication Module

## Purpose
User authentication and authorization using JWT tokens.

## Architecture
```
src/auth/
├── authentication.py      # User authentication logic
├── middleware.py          # JWT request middleware
└── token.py               # Token generation/validation
```

## Key Components

### authenticate_user(username, password) -> bool
Verifies user credentials against database.
- **File**: authentication.py:42-67
- **Dependencies**: User, DatabaseConnection
- **Used by**: AuthMiddleware, login_endpoint

### AuthMiddleware
JWT authentication middleware for protected endpoints.
- **File**: middleware.py:10-45
- **Methods**: process_request(), validate_token()
- **Used by**: FastAPI router

## Data Flow
```
Request -> AuthMiddleware.process_request()
        -> authenticate_user()
        -> DatabaseConnection.query(User)
        -> JWT token generation
```

## Relationships
- **CALLS**: DatabaseConnection, verify_password
- **USED BY**: API endpoints, WebSocket handlers
- **CONFIGURATION**: JWT_SECRET_KEY, TOKEN_EXPIRY
    """)


async def demo_mcp_server():
    """Demonstrate MCP server for Claude Code."""
    print("\n" + "=" * 80)
    print("7. MCP SERVER DEMO")
    print("=" * 80)

    print("\n--- Available MCP Tools ---")
    tools = [
        ("codeolas_search", "Search code semantically", "query: string, limit: int"),
        ("codeolas_research", "Multi-hop code research", "query: string, max_hops: int"),
        ("codeolas_graph_query", "Query knowledge graph", "cypher: string"),
        ("codeolas_get_chunk", "Get code chunk by ID", "chunk_id: string"),
        ("codeolas_list_files", "List indexed files", "filter: dict"),
        ("codeolas_generate_docs", "Generate .arch.md", "file_path: string"),
    ]

    print(f"{'Tool':<30} {'Description':<30} {'Parameters'}")
    print("-" * 80)
    for tool, desc, params in tools:
        print(f"{tool:<30} {desc:<30} {params}")

    print("\n--- Claude Code Integration ---")
    print("""
# In Claude Code, invoke via MCP:

User: "Search for authentication logic"
Claude: [Calls codeolas_search(query="authentication")]
  Found 5 results:
  - authenticate_user() in src/auth/authentication.py
  - AuthMiddleware in src/auth/middleware.py
  ...

User: "How does the auth system work?"
Claude: [Calls codeolas_research(query="auth system flow")]
  [Multi-hop research with graph traversal]
  Synthesis: The auth system uses JWT tokens...
    """)


async def demo_critical_constraints():
    """Demonstrate critical performance constraints."""
    print("\n" + "=" * 80)
    print("8. CRITICAL CONSTRAINTS DEMO")
    print("=" * 80)

    print("\n--- DuckDB Single-Threaded Access ---")
    print("""
CONSTRAINT: DuckDB MUST use single-threaded access
IMPACT: Prevents segfaults and corruption

Solution: SerialDatabaseExecutor
  executor = SerialDatabaseExecutor()
  result = await executor.execute(query)
    """)

    print("\n--- Embedding Batch Minimum ---")
    print("""
CONSTRAINT: Embeddings MUST be batched (min 100)
IMPACT: 100x performance difference

Unbatched 1000 texts: ~100s
Batched 1000 texts:   ~1s

Solution: BatchProcessor
  batcher = BatchProcessor(min_batch_size=100)
  embeddings = await batcher.process(texts)
    """)

    print("\n--- HNSW Index Management ---")
    print("""
CONSTRAINT: Drop indexes before bulk inserts >50 rows
IMPACT: 20x speedup for bulk operations

if row_count > 50:
    table.drop_index("vector_idx")
    table.add(embeddings)
    table.create_index("vector_idx", type="IVF_HNSW")
    """)


async def demo_performance_metrics():
    """Show performance metrics."""
    print("\n" + "=" * 80)
    print("9. PERFORMANCE METRICS DEMO")
    print("=" * 80)

    print("\n--- Typical Repository Statistics ---")
    repo_sizes = [
        ("Small", "<1k files", "2s", "50ms"),
        ("Medium", "1k-10k files", "15s", "150ms"),
        ("Large", "10k-100k files", "2m", "500ms"),
        ("Huge", ">100k files", "10m", "1.5s"),
    ]

    print(f"{'Size':<12} {'Files':<15} {'Index Time':<12} {'Query Latency':<15}")
    print("-" * 80)
    for size, files, index_time, query_latency in repo_sizes:
        print(f"{size:<12} {files:<15} {index_time:<12} {query_latency:<15}")

    print("\n--- Memory Usage ---")
    print("""
Repository: 10k files, 500k chunks
Embeddings: BGE-M3 (1024 dim, float32)
Memory:     2GB for vectors + 500MB metadata
    """)

    print("\n--- Storage Requirements ---")
    print("""
LanceDB Storage:
  - Vectors: 4KB per chunk (1024 * 4 bytes)
  - Metadata: 1KB per chunk
  - Total: ~5KB per chunk

Example:
  100k chunks = 500MB storage
  1M chunks = 5GB storage
    """)


async def demo_cli_usage():
    """Show CLI usage examples."""
    print("\n" + "=" * 80)
    print("10. CLI USAGE DEMO")
    print("=" * 80)

    print("\n--- Available Commands ---")
    commands = [
        ("codeolas index", "Index a repository", "codeolas index --repo /path/to/repo"),
        ("codeolas search", "Search code", "codeolas search 'authentication' --limit 10"),
        ("codeolas research", "Deep research", "codeolas research 'How does auth work?'"),
        ("codeolas arch", "Generate .arch.md", "codeolas arch --output ARCHITECTURE.md"),
        ("codeolas graph", "Query graph", "codeolas graph 'MATCH (f:Function) RETURN f'"),
        ("codeolas mcp", "Start MCP server", "codeolas mcp --port 3000"),
    ]

    print(f"{'Command':<20} {'Description':<25} {'Example'}")
    print("-" * 80)
    for cmd, desc, example in commands:
        print(f"{cmd:<20} {desc:<25} {example}")

    print("\n--- Example Workflow ---")
    print("""
# Index a repository
codeolas index --repo /path/to/project

# Search for code
codeolas search "database connection" --limit 5

# Deep research
codeolas research "How does the payment system work?"

# Generate architecture docs
codeolas arch --output ARCHITECTURE.md

# Start MCP server for Claude Code
codeolas mcp
    """)


async def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("CÓDEOLAS - CODE ANALYSIS AND REPOSITORY INTELLIGENCE")
    print("Semantic Code Search, Knowledge Graphs, and Documentation Generation")
    print("=" * 80)
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Demo Mode: Offline (using mock data)")

    try:
        await demo_code_indexing()
        await demo_semantic_search()
        await demo_multihop_research()
        await demo_knowledge_graph()
        await demo_reranking()
        await demo_documentation_generation()
        await demo_mcp_server()
        await demo_critical_constraints()
        await demo_performance_metrics()
        await demo_cli_usage()

        print("\n" + "=" * 80)
        print("DEMO COMPLETE")
        print("=" * 80)

        print("\n--- Next Steps ---")
        print("\nTo install códeolas:")
        print("  pip install codeolas")
        print("\nTo index a repository:")
        print("  codeolas index --repo /path/to/repo")
        print("\nTo search code:")
        print("  codeolas search 'authentication logic' --limit 10")
        print("\nFor deep research:")
        print("  codeolas research 'How does the auth system work?'")
        print("\nTo generate architecture docs:")
        print("  codeolas arch --output ARCHITECTURE.md")
        print("\nTo use as MCP server:")
        print("  codeolas mcp")
        print("\nTo import in Python:")
        print("  from codeolas import CodebaseAnalyzer")
        print("  analyzer = CodebaseAnalyzer('/path/to/repo')")
        print("  await analyzer.index()")
        print("  results = await analyzer.search('database connection')")

    except Exception as e:
        print(f"\n[!] Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
