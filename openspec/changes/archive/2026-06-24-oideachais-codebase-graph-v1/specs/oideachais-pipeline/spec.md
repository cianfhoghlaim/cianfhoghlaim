# Spec Delta: oideachais-pipeline

## ADDED Requirements

### Requirement: V1 codebase indexer (codebase_chunks + codebase_code_graph)

The system SHALL run a v1-native CocoIndex App for codebase indexing,
producing both an embedded chunk table and a code-graph table. The
App uses:

- 29+ language detection (port from `codeolas/chunking/languages.py`
  to `oideachais/cocoindex_flows/chunking/languages.py`)
- `localfs.walk_dir(repo_root, live=True, refresh_interval=60s)` for
  the source
- `RecursiveSplitter` with `detect_code_language` for chunking
- `SentenceTransformerEmbedder("BAAI/bge-m3")` for embedding
- `lancedb.mount_table_target(...)` for the chunk + graph outputs

The 3 Dagster assets in `oideachais/dagster_defs/assets/codebase_assets.py`
(group_name="codebase"):

1. `codebase_chunks` — chunked + embedded source files
   (`codebase_chunks` LanceDB table)
2. `codebase_code_graph` — AST-extracted code graph (7 node types +
   7 edge types in 2 LanceDB tables `codebase_graph` +
   `codebase_graph_edges`)
3. `codebase_architecture_docs` — `.arch.md` generation
   (deferred to a later round)

The 7 node types: `FILE`, `FUNCTION`, `CLASS`, `METHOD`, `MODULE`,
`INTERFACE`, `VARIABLE`. The 7 edge types: `CONTAINS`, `IMPORTS`,
`CALLS`, `EXTENDS`, `IMPLEMENTS`, `USES`, `DEFINES`. 11 languages
have Tree-sitter AST node type mappings: Python, TypeScript,
JavaScript, TSX, JSX, Rust, Go, Java, Kotlin, Ruby, Swift.

#### Scenario: A developer queries the codebase semantically

- **GIVEN** the `codebase_chunks` Dagster asset has materialised
- **WHEN** a developer runs `bun run ccc:v1:search "SpacetimeDB
  table"`
- **THEN** the v1 App runs the BGE-M3 embedding over the query
  string, returns the top-10 chunks from the `codebase_chunks`
  LanceDB table (filtered by `language = "rust"` if requested),
  and the chunks' file paths + line numbers are returned

#### Scenario: A developer queries the code graph (Cypher-like)

- **GIVEN** the `codebase_code_graph` Dagster asset has materialised
- **WHEN** a developer runs `search_code_graph(file_path="oideachais/dagster_defs/")`
- **THEN** the v1 App reads the `codebase_graph` LanceDB table and
  returns the 10 most relevant CodeNode dicts (file_path matches the
  glob, with optional `node_type` filter)

#### Scenario: A new language is added to the language table

- **GIVEN** a developer adds a new language (e.g. `dart` with `.dart`
  extension) to `oideachais/cocoindex_flows/chunking/languages.py`
- **WHEN** the `codebase_chunks` Dagster asset re-materialises
- **THEN** `.dart` files are now chunked using the recursive splitter
  with `language="dart"`
- **AND** the `languages` metadata includes `dart`

## REMOVED Requirements

(None.)
