# Proposal: Round 11 Phase 4 — Remove duplicate `agents/tools/` from meaisínfhoghlaim + fix 4 broken relative imports

## Why

Round 11 audit of `sruth/meaisinfhoghlaim/` (after Phases 1-3 fixed 3 typos,
1 stale `sruth/oideachas/` AGENTS.md reference, 3 dead stub modules, 4 stale
duplicate DLT sources, 1 broken `..core.utils` import, and 2 dead resource
modules in `pipelines/`) uncovered a SECOND `tools/` package that is a
byte-for-byte duplicate of the canonical `sruth/oideachais/tools/`, plus 4
agent files with broken `from ..tools.X` relative imports that would raise
`ModuleNotFoundError` at module load time.

This is the last concrete audit finding in the meaisínfhoghlaim quadrant
before pivoting to `sruth/tuatha/` (changes #9-11) and `sruth/croilar/`
(changes #12-14).

## What changes

### 1. DELETE `sruth/meaisinfhoghlaim/agents/tools/`

10 files (3,009 lines), all byte-for-byte identical to the canonical
`sruth/oideachais/tools/`:

| File | Lines | SHA-256 (truncated) | Match? |
|:--|--:|:--|:--|
| `__init__.py` | 120 | `b70e801e5c3f` | MATCH |
| `corpus_search.py` | 362 | `a5306fc8c17c` | MATCH |
| `corpus_tools.py` | 220 | `58d0136ad133` | MATCH |
| `curriculum_search.py` | 312 | `bd3a13aed077` | MATCH |
| `curriculum_tools.py` | 456 | `82cef0a3f77c` | MATCH |
| `geospatial_tools.py` | 235 | `ee4a60efb5e6` | MATCH |
| `spatial_query.py` | 355 | `952e31dcf1d9` | MATCH |
| `statistics_query.py` | 334 | `2e14963f49ae` | MATCH |
| `terminology.py` | 338 | `6db99f29c458` | MATCH |
| `translation_tools.py` | 277 | `3b1a41d6e906` | MATCH |
| **Total** | **3,009** | — | 10/10 |

### 2. FIX 4 broken `from ..tools.X` relative imports

The 4 imports resolve to `sruth/meaisinfhoghlaim/tools/` (2 dots up = one
level above `agents/`), which does not exist. They will raise
`ModuleNotFoundError: No module named 'sruth.meaisinfhoghlaim.tools'` at
module load time, not just at function call time:

| File | Line | Current | Replacement |
|:--|--:|:--|:--|
| `agui_curriculum_agent.py` | 25 | `from ..tools.curriculum_search import ...` | `from sruth.oideachais.tools.curriculum_search import ...` |
| `curriculum_comparison_agent.py` | 14 | `from ..tools.curriculum_search import ...` | `from sruth.oideachais.tools.curriculum_search import ...` |
| `geospatial_agent.py` | 15 | `from ..tools.spatial_query import ...` | `from sruth.oideachais.tools.spatial_query import ...` |
| `statistics_agent.py` | 15 | `from ..tools.statistics_query import ...` | `from sruth.oideachais.tools.statistics_query import ...` |

Canonical homes already export the exact symbols required:

| Symbol | Verified importable from canonical |
|:--|:--|
| `compare_curricula`, `search_curriculum`, `find_similar_content`, `get_learning_outcomes` | `sruth.oideachais.tools.curriculum_search` (312 lines, byte-identical) |
| `find_nearby_schools`, `get_area_statistics`, `get_deprivation_correlation`, `query_by_area` | `sruth.oideachais.tools.spatial_query` (355 lines, byte-identical) |
| `compare_nations`, `get_trend`, `list_available_metrics`, `query_statistics` | `sruth.oideachais.tools.statistics_query` (334 lines, byte-identical) |

## Out of scope (deferred to other changes)

- `sruth/crypteolas/agents/adk/*.py` 4 broken `from ..tools.X` imports —
  this is the **crypteolas** quadrant, not meaisínfhoghlaim. Tracked
  separately under `tuatha` (changes #9-11).
- `sruth/tuatha/agents/mcp_server/server.py:23-33` 2 broken
  `from ..tools.X` imports — already documented as a known broken-import
  bug in the `tuatha-mcp-server-tools` skill.
- `sruth/meaisinfhoghlaim/agents/bunchloch_research_agent.py` (both
  copies at `agents/` and at `sruth/oideachais/agents/adk/`) — these
  files have broken `from sruth.shared.X` lazy imports INSIDE `try/except`
  blocks. The modules themselves load; the functions would fail only when
  called. Spec mandates the agents remain (`meaisinfhoghlaim-platform`
  spec section "Agent + OCR thin-shim canonicalisation" requirement line
  230 + `meaisinfhoghlaim-sruth-debt-migration` archive task 38). The
  `sruth-debt-migration` change already migrated lines 94,201 (per
  archived `tasks.md:38`). Out of scope.

## Impact

- **Net deletion**: 3,009 lines (the entire duplicate `tools/` package).
- **Files touched**: 4 (the 4 broken-import agent files).
- **Net source lines removed**: ~3,005 (3,009 deletion − 4 trivial line
  rewrites with same symbol names).
- **No spec deletion**: meaisínfhoghlaim-platform spec retains the
  "Agent + OCR thin-shim canonicalisation" requirement — only the source
  path of canonical tools changes (`agents/tools/` → `oideachais/tools/`).
- **Build risk**: low. The 4 broken imports are at module-load time, so
  no meaisínfhoghlaim agent file imports cleanly today. After the fix,
  the 4 agents gain a clean import path through the canonical
  oideachais-tools surface.
