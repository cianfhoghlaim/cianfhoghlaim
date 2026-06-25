# Status — `codeolas`

> **Read this first if you are picking up work in this sub-package.**
> This document explains what was dropped during the consolidation into
> `tuatha/codeolas/`, what shims remain, and where the live entry points live.

## What this package is

The `codeolas` package is the publishable Python library for semantic code
search, knowledge graph construction, and documentation generation. It is
part of the `tuath` uv workspace member. Import it as:

```python
from codeolas import CodebaseAnalyzer
from codeolas.generators.changelog import ChangelogGenerator
from codeolas.mcp_server import MCPServer
```

## What was dropped during the consolidation

The prior standalone `códeolas_codebase_indexing/` carried a lot of internal
duplication and dead code. All of the following have been removed; the
canonical survivor is the first item in each pair.

| Dropped | Kept | Why |
|:--|:--|:--|
| `generators/arch_generator.py` | `generators/arch.py` | Byte-for-byte duplicate of `arch.py` |
| `storage/lance.py` | `storage/lance_catalog.py` | `lance_catalog.py` has the `EmbeddingModel` enum + dataclass-aware formatting |
| `flows/` (whole dir) | `cocoindex_flows/` | `cocoindex_flows/` is the registered CocoIndex flow variant |
| `pipelines/` (whole dir) | `dagster_assets/` | `dagster_assets/` imports from `cocoindex_flows` (the canonical one) |
| `mcp/` (whole dir) | `mcp_server/` | `mcp_server/tools.py` has the typed `Tool` dataclass registry |
| `agents/` (whole dir) | — | Every module was a stub raising `NotImplementedError` |
| `uv.lock` (per-member) | — | Root `uv.lock` is the single source of truth for the workspace |

## Broken imports that were rewritten

The standalone `códeolas_codebase_indexing/` had ~25 import sites pointing at
the non-existent `sruth.códeolas.*` and `sruth.shared.*` namespaces. All have
been rewritten to point at the new `codeolas.*` paths.

| Old import | New import |
|:--|:--|
| `from sruth.códeolas.core.X import Y` | `from codeolas.core.X import Y` |
| `from sruth.códeolas.chunking import Y` | `from codeolas.chunking import Y` |
| `from sruth.códeolas.storage.lance import X` | `from codeolas.storage.lance_catalog import X` |
| `from sruth.códeolas.search.X import Y` | `from codeolas.search.X import Y` |
| `from sruth.códeolas.graph.X import Y` | `from codeolas.graph.X import Y` |
| `from sruth.códeolas.generators.X import Y` | `from codeolas.generators.X import Y` |
| `from sruth.códeolas.mcp.server import main` | `from codeolas.mcp_server.server import main` |
| `from sruth.shared.storage import X` (in `storage/serial_executor.py`) | `from sruth.oideachais.core.storage.serial_executor import X` |
| `from sruth.shared.browser.core.llm_router import X` (in `reposwarm/generator.py`) | `from sruth.oideachais.http_utils.llm_router import X` (with `sruth_browser.llm_router` fallback) |
| `from sruth.shared.storage import get_executor` (in `reposwarm/cache.py`) | `from sruth.oideachais.core.storage.serial_executor import get_executor` |

## Deprecation shims (still emit `DeprecationWarning`)

Two modules are kept only as backwards-compatible shims and will be removed
in a future version:

- **`tuatha/codeolas/storage/serial_executor.py`** — re-exports
  `SerialDatabaseExecutor`, `get_executor`, `run_serial` from
  `oideachais.core.storage.serial_executor`. Update imports to the
  oideachais path.
- **`tuatha/codeolas/cocoindex_flows/transforms/treesitter_chunking.py`** —
  re-exports `chunk_code_file`, `detect_language`, `ChunkType`, `CodeChunk`,
  `EXTENSION_TO_LANGUAGE`, `LANGUAGE_EXTENSIONS` from
  `codeolas.chunking`. Update imports to the `codeolas.chunking` path.

## Stub implementations

- **`tuatha/codeolas/generators/changelog.py`** — `ChangelogGenerator` is a
  stub. It accepts the same constructor and method signature as the planned
  real implementation but returns a placeholder markdown string. A real
  implementation would shell out to `git log` and group commits by
  conventional-commit type. The stub is needed so
  `tests/test_generators.py::TestChangelogGeneration` and the
  `CodebaseAnalyzer.generate_changelog` call site can import successfully.

## Test fixes

- **`tests/test_research.py`** — no hard-coded path; no fix needed.
- **`tests/test_multilang_chunking.py`** — path was
  `codesola_root / "codeolas" / "core" / "analyzer.py"`; updated to
  `codesola_root / "core" / "analyzer.py"` (the package is no longer nested
  inside a parent `codeolas/` directory).
- **`tests/conftest.py`** — the `cianfhoghlaim_path` fixture hard-coded
  `/Users/cliste/dev/cianfhoghlaim`. Replaced with a read of
  `os.environ.get("CODEOLAS_REPO_PATH", os.getcwd())` so the test no longer
  assumes a specific machine layout.

## Entry points (in `pyproject.toml`)

- `codeolas` console script → `codeolas.cli:main`
- `codeolas-mcp` console script → `codeolas.mcp_server.server:main`
- Dagster code-location → `codeolas.dagster_assets.definitions:defs`

## Forgejo CI

The `.forgejo/workflows/{ci,release}.yaml` files inside this directory are
preserved as documentation/scaffolding but are **not auto-discovered** by
Forgejo (which only scans `.forgejo/workflows/*.yaml` at the repo root). The
ci.yaml `paths` filter is still updated to `tuatha/codeolas/**` so it would
work if promoted to the repo root. For now, run the tests locally with:

```bash
cd tuatha && uv run pytest codeolas/tests/ -v
```

## How to use

```python
# Python
from codeolas import CodebaseAnalyzer

analyzer = CodebaseAnalyzer("/path/to/repo")
await analyzer.index()
results = await analyzer.search("authentication logic")
```

```bash
# CLI
codeolas --help
codeolas index --repo /path/to/repo
codeolas search "database connection" --limit 10
codeolas-mcp  # starts the MCP server on stdio
```

```bash
# Dagster
cd tuatha && uv run dagster dev -m codeolas.dagster_assets.definitions
```
