# Status — `crypteolas`

> **Read this first if you are picking up work in this sub-package.**
> This document explains what was dropped, what shims remain, and what
> stubs are in place. The full refactor is documented in
> `openspec/changes/consolidate-external-libs-into-sruth/tuatha/`.

## What this package is

The `crypteolas` package is the Python data intelligence platform for
GitHub ingestion (issues, PRs, commits, workflows), DeFi protocol
research (TVL, funding rates, yields), semantic code search, knowledge
graph construction (Cognee + Graphiti + Memgraph + FalkorDB), and
interactive analysis (marimo notebooks). It is part of the `tuath` uv
workspace member. Import it as:

```python
from crypteolas.definitions import defs          # Dagster code-location
from crypteolas.api.main import app              # FastAPI backend
from crypteolas.cocoindex_flows import unified_search, code_search
from crypteolas.mcp_server import MCPServer      # stdio MCP server
```

## What was dropped during the consolidation

The standalone `crypteolas_formative_assessment/` carried a 22 MB
vendored copy of the DSPy library and two pairs of duplicate marimo
notebooks. All of the following have been removed; the canonical
survivor is the first item in each pair.

| Dropped | Kept | Why |
|:--|:--|:--|
| `dspy/` (whole tree, ~600 files, 22 MB) | — | Nothing actually imported from it. The vendored copy was dead weight. |
| `notebooks/01_github_explorer.py` | `notebooks/01_github_api_explorer.py` | The latter is the canonical 404-line GitHub API explorer. |
| `notebooks/04_defi_dashboard.py` | `notebooks/04_unified_dashboard.py` | The latter is the canonical combined dashboard. |
| `uv.lock` (per-member) | — | Root `uv.lock` is the single source of truth for the workspace. |
| `.tmp_dagster_home_*/` (ephemeral) | — | Was a leftover `dagster dev` scratch directory. |

## Broken imports that were rewritten

The standalone `crypteolas_formative_assessment/` had two classes of broken
imports. All have been rewritten.

### Class A: bare `crypteolas.*` references (rewritten to `tuatha.crypteolas.*`)

| Old import | New import |
|:--|:--|
| `from crypteolas.api.main import app` | `from tuatha.crypteolas.api.main import app` |
| `from crypteolas.agents.tools.X import Y` | `from tuatha.crypteolas.agents.tools.X import Y` |
| `from crypteolas.dlt_sources.X import Y` | `from tuatha.crypteolas.dlt_sources.X import Y` |
| `from crypteolas.cocoindex_flows.X import Y` | `from tuatha.crypteolas.cocoindex_flows.X import Y` |
| `from crypteolas.storage.X import Y` | `from tuatha.crypteolas.storage.X import Y` |
| `from crypteolas.knowledge_graph.X import Y` | `from tuatha.crypteolas.knowledge_graph.X import Y` |

58 import sites across 17 files were rewritten. The full list is in the
consolidation spec under `openspec/changes/consolidate-external-libs-into-sruth/tuatha/`.

### Class B: `sruth.crypteolas.*` and `sruth.shared.*` (replaced with shims)

| Old import | New import | Notes |
|:--|:--|:--|
| `from sruth.crypteolas.agents.agno.protocol_team import …` | `from tuatha.crypteolas.agents.agno.protocol_team import …` | Pure rewrite. |
| `from sruth.shared.agent_os.middleware import …` | `from tuatha.crypteolas._shims.agent_os.middleware import …` | Shim: `TinyAuthMiddleware`, `A2AAuthMiddleware` (basic starlette stubs). |
| `from sruth.shared.agent_os.config import init_config` | `from tuatha.crypteolas._shims.agent_os.config import init_config` | Shim: dataclass-based config. |
| `from sruth.shared.agent_os.a2a import call_agent` | `from tuatha.crypteolas._shims.agent_os.a2a import call_agent` | Shim: returns a placeholder response. |
| `from sruth.shared.dagster import LakeKeeperResource` | `from tuatha.crypteolas._shims.dagster import LakeKeeperResource` | Shim: `ConfigurableResource` stub. |
| `from sruth.shared.dagster.components.sruth_components import …` | `from tuatha.crypteolas._shims.dagster.components.sruth_components import …` | Shim: empty `Definitions` for all four component classes. |
| `from sruth.códeolas import chunk_code_file, detect_language` (in `agents/adk/architecture_agent.py`) | `from codeolas import chunk_code_file, detect_language` | Points at the new `sruth/tuatha/codeolas/` package. |

The `_shims/` package lives at `sruth/tuatha/crypteolas/_shims/`. Each shim
re-implements just enough of the original API to satisfy the import and
let the test suite load. Replace with real implementations as the
broader monorepo work progresses.

### Knowledge graph client compatibility modules

The test suite imports from four legacy module names that don't exist
in the source tree. Compatibility shims have been added so the tests can
load and be skipped cleanly:

| Shim | Real implementation |
|:--|:--|
| `sruth/tuatha/crypteolas/knowledge_graph/cognee_client.py` | Re-exports from `cognee/static_knowledge.py` + legacy aliases (`get_cognee_client` → `setup_cognee`, `add_document` → `add_protocol_knowledge`, etc.). |
| `sruth/tuatha/crypteolas/knowledge_graph/graphiti_client.py` | Re-exports from `graphiti/temporal_graph.py` + legacy aliases. |
| `sruth/tuatha/crypteolas/knowledge_graph/falkordb_client.py` | Stub: returns placeholder client + empty Cypher results. |
| `sruth/tuatha/crypteolas/knowledge_graph/memgraph_client.py` | Stub: returns placeholder client + empty query results. |

When the test suite is updated to import from the canonical module
names, these shims can be deleted.

## BAML client name resolution

`sruth/tuatha/baml_src/clients.baml` was renamed to `sruth/tuatha/baml_src/tuatha_clients.baml`
so that the two `baml_src/` directories (`sruth/tuatha/baml_src/` and
`sruth/tuatha/crypteolas/baml_src/`) can coexist without a filename collision.

The crypteolas `.baml` files defined clients with the same names as the
Celtic MMO's clients (`GPT4o`, `Claude`, etc.) but with different
configurations (different temperature, different `max_tokens`). To
resolve the client-name collision when both baml_src/ are merged into
a single `baml_client/` output, all crypteolas client names have been
prefixed with `Crypteolas`:

| Old client name | New client name |
|:--|:--|
| `GPT4o` | `CrypteolasGPT4o` |
| `GPT4oMini` | `CrypteolasGPT4oMini` |
| `Claude` | `CrypteolasClaude` |
| `ClaudeHaiku` | `CrypteolasClaudeHaiku` |
| `DeepSeek` | `CrypteolasDeepSeek` |
| `Qwen` | `CrypteolasQwen` |
| `DocumentAnalysis` | `CrypteolasDocumentAnalysis` |
| `FastExtraction` | `CrypteolasFastExtraction` |
| `CodeAnalysis` | `CrypteolasCodeAnalysis` |
| `RiskAssessment` | `CrypteolasRiskAssessment` |

All 25 `client X` references in the five crypteolas `.baml` files
(`code_analysis.baml`, `code_pattern_detection.baml`,
`crypto_extraction.baml`, `protocol_analysis.baml`,
`vulnerability_assessment.baml`) have been rewritten to use the
prefixed names.

## Cloudflare Workers (TODO)

`sruth/tuatha/crypteolas/wrangler.toml` is preserved with a `# TODO` comment
explaining that `workers/index.ts` does not yet exist. The wrangler
config is otherwise valid: the R2 buckets, KV namespaces, and the
`DEFAULT_PAYMENT_NETWORK = "cronos"` settings are all kept intact.
When the Workers code is added, it should live at
`sruth/tuatha/crypteolas/workers/index.ts` and serve the x402 payment
middleware + R2 proxy.

## Document relocation

All `*.md` documentation files have been moved to `sruth/tuatha/crypteolas/docs/`:

- `ARCHITECTURE.md` (25 KB)
- `CRYPTEOLAS_INTEGRATION_GUIDE.md` (26 KB)
- `"Crypteolas_ Federated Learning & Crypto Payments.md"` (39 KB)
- `DEVELOPMENT.md` (8 KB)
- `QUICKSTART.md` (4 KB)
- `README_EXPLORATION.md` (6 KB)
- `SETUP.md` (7 KB)

Update any links that pointed to the old root-level locations.

## Dagster integration

The `crypteolas` Dagster code-location is registered in the tuatha
workspace. Run it locally with:

```bash
cd tuatha && uv run dagster dev -m crypteolas.definitions
```

The three new `Definitions` registered for the `tuath` workspace are:

| Code-location | Entry-point module |
|:--|:--|
| `tuath` (Celtic MMO) | `dagster_assets.definitions` |
| `crypteolas` (this package) | `crypteolas.definitions` |
| `crypteolas_demo` (`sruth/tuatha/apps/crypteolas_demo/`) | `crypteolas_demo.definitions` |

## How to use

```python
# Dagster
from crypteolas.definitions import defs
print(len(defs.get_asset_graph().get_all_asset_keys()))

# FastAPI
from crypteolas.api.main import app
print(app.title)

# CocoIndex semantic search
from crypteolas.cocoindex_flows import unified_search, code_search

# MCP server (stdio)
from crypteolas.mcp_server import MCPServer
```

```bash
# Dagster
cd tuatha && uv run dagster dev -m crypteolas.definitions

# FastAPI
cd tuatha && uv run uvicorn crypteolas.api.main:app --port 8001

# MCP server
cd tuatha && uv run python -m crypteolas.mcp_server
```
