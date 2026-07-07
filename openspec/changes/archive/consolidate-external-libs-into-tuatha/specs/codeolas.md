# `codeolas` capability spec (NEW)

The `codeolas` capability provides semantic code search, knowledge graph
construction, and documentation generation over a Python codebase.

## ADDED Requirements

### Requirement: Public API surface
The `codeolas` package SHALL re-export the following symbols from its top-level
`__init__.py`:

- `CodebaseAnalyzer`, `Config`, `get_config` (from `core/`)
- `EmbeddingService`, `get_embedding_service` (from `core/`)
- `EntityExtractor`, `deduplicate_entities` (from `core/`)
- `SourceRange`, `SearchResult`, `GraphNode`, `GraphEdge` (from `core/types.py`)
- `ChunkType`, `CodeChunk`, `NodeType`, `EdgeType`, `RelationshipType` (from `core/types.py`)
- `chunk_code_file`, `detect_language`, `get_extensions_for_language`,
  `get_supported_languages`, `EXTENSION_TO_LANGUAGE`, `LANGUAGE_EXTENSIONS`
  (from `chunking/`)
- `LanceCatalog`, `LanceCatalogConfig`, `get_lance_catalog` (from `storage/lance_catalog.py`)
- `multihop_search`, `expand_semantic_neighborhood`, `rerank_results` (from `search/`)
- `GraphBuilder`, `GraphQueries` (from `graph/`)
- `ArchitectureSection`, `ArchDocument`, `ArchGenerator`, `generate_arch_docs` (from `generators/arch.py`)
- `RepoSwarmGenerator`, `RepoType`, `GenerationConfig`, `CacheConfig`,
  `RepoTypeDetector`, `ArchDocCache` (from `generators/reposwarm/`)
- `MCPServer`, `main` (from `mcp_server/`)

#### Scenario: `from codeolas import CodebaseAnalyzer`
- **WHEN** `from codeolas import CodebaseAnalyzer` is executed
- **THEN** the import succeeds without error.

### Requirement: No internal duplication
The `codeolas` package SHALL NOT contain two near-identical implementations of
the same concept. Specifically, the package SHALL NOT contain both
`flows/` and `cocoindex_flows/`, both `pipelines/` and `dagster_assets/`, both
`mcp/` and `mcp_server/`, both `arch.py` and `arch_generator.py`, or both
`lance.py` and `lance_catalog.py`.

#### Scenario: No dup dirs
- **WHEN** the `codeolas/` directory is listed
- **THEN** exactly one of each pair above exists, and the dropped variant is
  documented in `STATUS.md`.

### Requirement: No dead agents tree
The `codeolas` package SHALL NOT contain an `agents/` sub-package, as all
modules in the prior `agents/` tree were stubs raising `NotImplementedError`.

#### Scenario: No agents dir
- **WHEN** the `codeolas/` directory is listed
- **THEN** there is no `codeolas/agents/` directory.

### Requirement: Working CLI
The `codeolas` console script SHALL be importable and runnable.

#### Scenario: codeolas --help
- **WHEN** `codeolas --help` is executed
- **THEN** the help text from `codeolas/cli.py` is printed without error.

### Requirement: Working MCP server
The `codeolas-mcp` console script SHALL be importable and runnable.

#### Scenario: codeolas-mcp --help
- **WHEN** `codeolas-mcp --help` is executed
- **THEN** the MCP server starts (or prints its help) without error.

### Requirement: Working Dagster integration
The `codeolas` Dagster code-location SHALL be registered in the workspace.

#### Scenario: dagster dev loads codeolas
- **WHEN** `dagster dev` is started with the tuatha workspace
- **THEN** the `codeolas` code-location is listed in the UI.
