# `crypteolas` capability spec (NEW)

The `crypteolas` capability provides GitHub data intelligence (issues, PRs,
commits, workflows), DeFi protocol research (TVL, funding rates, yields),
semantic code search, knowledge graph construction (Cognee + Graphiti + Memgraph),
and interactive analysis (marimo notebooks).

## ADDED Requirements

### Requirement: Public API surface
The `crypteolas` package SHALL re-export the following symbols from its
top-level `__init__.py`:

- `defs` (Dagster `Definitions` from `definitions.py`)
- `MCPServer`, `TOOL_REGISTRY`, `main` (from top-level `mcp_server/`)
- `app` (FastAPI from `api/main.py`)
- `unified_search`, `code_search`, `ProtocolGraphClient`,
  `UnifiedEmbeddingConfig`, `DocumentSourceType`, `LiveDocumentationSync`,
  `sync_protocol_docs`, `sync_all_protocol_docs`, `get_configured_protocols`,
  `ProtocolEntityType`, `ProtocolRelationType`, `ProtocolEntity`,
  `ProtocolRelationship`, `get_protocol_graph`, `initialize_protocol_graph`,
  `MIN_BATCH_SIZE`, `HNSW_DROP_THRESHOLD` (from `cocoindex_flows/`)
- `NAMESPACE = "crypteolas"`, `DuckLakeConfig`, `get_dlt_destination`,
  `get_duckdb_fallback`, `create_pipeline` (from `dlt_utils/`)
- All symbol groups from `dlt_sources/`, `storage/`, `transformations/`,
  `knowledge_graph/`, `graphiti/`, `agent_os/`, `agents/`.

#### Scenario: from crypteolas import defs
- **WHEN** `from crypteolas.definitions import defs` is executed
- **THEN** the import succeeds and `defs.assets` is non-empty.

### Requirement: No vendored DSPy
The `crypteolas` package SHALL NOT contain a `dspy/` sub-package. The
prior vendored copy of the DSPy library was never imported and is dropped.

#### Scenario: No dspy dir
- **WHEN** the `sruth/crypteolas/` directory is listed
- **THEN** there is no `sruth/crypteolas/dspy/` directory.

### Requirement: Dedup notebooks
The `sruth/crypteolas/notebooks/` directory SHALL contain at most one of each
canonical notebook. Specifically, exactly one of
`01_github_api_explorer.py` / `01_github_explorer.py` SHALL exist, and
exactly one of `04_unified_dashboard.py` / `04_defi_dashboard.py` SHALL exist.

#### Scenario: 4 notebooks total
- **WHEN** the `sruth/crypteolas/notebooks/` directory is listed
- **THEN** there are exactly 4 marimo notebooks:
  `01_github_api_explorer.py`, `02_code_search.py`, `03_knowledge_graph.py`,
  `04_unified_dashboard.py`.

### Requirement: No sruth.* dead imports
All `from sruth.crypteolas.*` and `from sruth.shared.*` imports SHALL either
be resolved to a real module path or replaced with a thin local shim that
re-exports the equivalent symbols. No code in `sruth/crypteolas/` SHALL import from
a non-existent `sruth.*` namespace.

#### Scenario: agent_os imports resolve
- **WHEN** `from crypteolas.agent_os.main import app` is executed
- **THEN** the import succeeds (or raises a documented `NotImplementedError`).

### Requirement: Dagster integration
The `crypteolas` Dagster code-location SHALL be registered in the tuatha
workspace.

#### Scenario: dagster dev shows crypteolas
- **WHEN** `dagster dev` is started with the tuatha workspace
- **THEN** the `crypteolas` code-location is listed in the UI alongside `tuath`.

### Requirement: wrangler.toml with TODO
The `sruth/crypteolas/wrangler.toml` SHALL be preserved with a `# TODO` comment
explaining that the `workers/index.ts` is not yet implemented.

#### Scenario: wrangler.toml readable
- **WHEN** `sruth/tuatha/sruth/crypteolas/wrangler.toml` is read
- **THEN** a TODO comment is present on or near the `main` line.
