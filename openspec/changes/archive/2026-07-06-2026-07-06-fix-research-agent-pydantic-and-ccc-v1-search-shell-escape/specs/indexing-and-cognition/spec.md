# Spec Delta — `indexing-and-cognition`

## ADDED Requirements

### Requirement: `bun run ccc:v1:search` SHALL return parseable JSON

The canonical CCC v1 search command SHALL return a JSON array of result chunks on stdout, parseable by `json.loads`, and SHALL exit with code 0.

#### Scenario: Substring search returns JSON

- **WHEN** the user runs `bun run ccc:v1:search "LANCE_DB" --limit 3`
- **THEN** the command SHALL exit with code 0
- **AND** stdout SHALL be a JSON array of dicts each with `file_path`, `line_no`, `snippet`, `relevance`
- **AND** the command SHALL NOT raise `SyntaxError` from the bun shell-escape wrapper

#### Scenario: Semantic search returns JSON

- **WHEN** the user runs `bun run ccc:v1:search "embedding similarity" --semantic --limit 5`
- **THEN** the command SHALL exit with code 0 within 10 seconds (subsequent calls; first call may take 5-10s for BGE-M3 model load)
- **AND** stdout SHALL be a JSON array ranked by vector distance

#### Scenario: Graceful fallback when canonical module is unavailable

- **WHEN** `from cianfhoghlaim.cocoindex.codebase_indexing import search_codebase` raises `ImportError` (e.g. missing `chunking.languages` sub-module in the v4 tree)
- **THEN** the wrapper SHALL fall back to a direct LanceDB query at `.cocoindex_code/lancedb/codebase_chunks.lance`
- **AND** SHALL write a `# module_import_failed: <reason>` comment to stderr (NOT stdout, so JSON parsing is unaffected)
- **AND** SHALL still return JSON on stdout

#### Scenario: ADK `ccc_search` tool delegates to the canonical wrapper

- **WHEN** the ADK `ccc_search` tool is called with `query="LANCE_DB"`, `limit=5`
- **THEN** the tool SHALL invoke `uv run python scripts/ccc_v1_search.py "LANCE_DB" --limit 15`
- **AND** SHALL NOT raise any error
- **AND** SHALL return up to 5 structured chunks