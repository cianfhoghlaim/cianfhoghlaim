# Proposal: Delete dead `_shared/{observability,agents,mcp,embeddings}` subdirs (round 11 croilar phase 3)

## Context

The `sruth/croilar/_shared/` package contains 6 sub-modules + 3 top-level
modules (`streams.py`, `config/`, `database/`). The 4 subdirs in scope here
are dead code — they were written for the old Aleyum agent framework but
were never wired into the new Croílár Stream-registry-driven architecture
(round 11 phase 0 / commit `6186d70da` + the croilar-aleyum-to-streams-cleanup-v1
openspec change).

| Subdir | Lines | Production callers in `sruth/croilar/` | Verdict |
|---|--:|---|---|
| `observability/` (tracing.py + __init__.py) | 451 + 30 = 481 | zero — only `__init__.py` + the module itself reference these symbols | DELETE |
| `agents/` (router.py + __init__.py) | 338 + 34 = 372 | zero — only `__init__.py` + the module itself | DELETE |
| `mcp/` (gateway.py + __init__.py) | 393 + 26 = 419 | zero — only `__init__.py` + the module itself | DELETE |
| `embeddings/` (batcher.py + __init__.py) | 111 + 13 = 124 | zero — only `__init__.py` + the module itself | DELETE |
| `database/` (110 lines) | 110 | tests/test_database.py + (importer-search shows) | KEEP |
| `config/` (paths.py + settings.py + __init__.py = 180 lines) | 180 | 7 files (dagster_assets + pipelines + tests) | KEEP |
| `streams.py` (244 lines) | 244 | dagster_assets/dlt_assets.py + tests | KEEP |

**Proof of dead-code status**: The top-level `sruth/croilar/_shared/__init__.py`
has these lines:

```python
# Aleyum/Croílár-specific exports
# (populated as modules are implemented — see _shared/{agents,observability,...})
# from .mcp import MCPGateway
# from .agents import AgentRouter, select_framework
# from .observability import AleyumTracer
```

The 3 sibling imports are commented out — proving that even the package
author never wired them into the top-level surface. The 4 subdirs exist but
are unreachable from any active code path.

**Cross-quadrant impact check**: The canonical surfaces for all 4 modules
already exist elsewhere in the monorepo:

- `observability/` → `sruth/oideachais/observability/` (the `AleyumTracer`-equivalent lives at `sruth/oideachais/observability/unified_tracer.py` + `agent_tracing.py`, wired into the agent-observability skill)
- `agents/` → `sruth/meaisinfhoghlaim/agents/` (the canonical 12-agent fleet — see the `agent-fleet-orchestration` skill)
- `mcp/` → `sruth/oideachais/mcp/filesystem/` (the canonical MCP server surface)
- `embeddings/` → `sruth/codeolas/core/embeddings.py` (the canonical `get_embedding_service(...)` factory — see the `embedding-pipeline` skill for batch patterns)

So the 4 subdirs are not just dead in croilar — they are shadow implementations
of canonical surfaces that already exist in other quadrants.

## Proposal

Delete the 4 dead subdirs + update the 2 affected importers:

1. **Delete** `sruth/croilar/_shared/observability/` (2 files, 481 lines).
2. **Delete** `sruth/croilar/_shared/agents/` (2 files, 372 lines).
3. **Delete** `sruth/croilar/_shared/mcp/` (2 files, 419 lines).
4. **Delete** `sruth/croilar/_shared/embeddings/` (2 files, 124 lines).
5. **Patch** `sruth/croilar/_shared/__init__.py` (lines 1-15 docstring + lines
   42-44 commented-out sibling imports) — remove the "embeddings, MCP
   gateway, agent orchestration, and observability" docstring clause + remove
   the 3 commented-out sibling import lines.

After this change, `sruth/croilar/_shared/` contains only:
- `__init__.py` (92 → 88 lines after docstring trim)
- `streams.py` (244 lines)
- `config/__init__.py` + `paths.py` + `settings.py` (180 lines)
- `database/__init__.py` (110 lines)

The pre-existing 3 broken test assertions in `tests/test_smoke.py` +
`tests/dlt_assets/test_spotify_soundcloud_labels.py` documented at
`sruth/croilar/README.md` Known issues row #3 are out of scope.

## Affected surfaces

- 9 files deleted (8 in 4 subdirs + 3 commented-out lines in `__init__.py`)
- 1396 lines deleted (481 + 372 + 419 + 124)
- 0 lines added
- 1 spec delta added to `croilar-data-engineering`

## No backwards compatibility

Per round 11 conventions, no `try/except ImportError` fallback shims, no
`__getattr__` lazy imports, no deprecation warnings. Delete outright. If a
caller is discovered post-merge, the canonical replacement is documented in
the `## Cross-quadrant impact check` table above.