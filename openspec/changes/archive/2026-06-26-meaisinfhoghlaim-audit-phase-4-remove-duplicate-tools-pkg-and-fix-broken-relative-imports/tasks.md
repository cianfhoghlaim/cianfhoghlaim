# Tasks: Round 11 Phase 4 — Remove duplicate `agents/tools/` from meaisínfhoghlaim + fix 4 broken relative imports

## Pre-flight

- [x] Confirmed `sruth/meaisinfhoghlaim/agents/tools/` is byte-for-byte identical to `sruth/oideachais/tools/` via SHA-256 of all 10 files (10/10 MATCH, 3,009 lines)
- [x] Confirmed 4 broken `from ..tools.X` imports in 4 agent files (verify via `grep -n "from \.\.tools\." sruth/meaisinfhoghlaim/agents/*.py`)
- [x] Confirmed canonical `sruth.oideachais.tools.X` modules export the exact symbols required (verified via direct `python3 -c "from ... import ..."` for all 3 modules)
- [x] Confirmed `sruth/meaisinfhoghlaim/tools/` does NOT exist (the path that `from ..tools.X` resolves to)
- [x] Confirmed cross-quadrant refs to `sruth.oideachais.tools` from meaisínfhoghlaim = 0 (no existing precedent, so no migration step needed)

## Implementation

- [ ] Create openspec change directory `openspec/changes/meaisinfhoghlaim-audit-phase-4-remove-duplicate-tools-pkg-and-fix-broken-relative-imports/`
- [ ] Write `proposal.md` (done)
- [ ] Write `tasks.md` (this file)
- [ ] Write `specs/meaisinfhoghlaim-platform/spec.md` delta with 2 ADDED Requirements (single-source `sruth/oideachais/tools/`; no-broken-relative-tool-imports)
- [ ] Run `openspec validate meaisinfhoghlaim-audit-phase-4-remove-duplicate-tools-pkg-and-fix-broken-relative-imports --strict` (must pass before commit)
- [ ] Move (git mv) `sruth/meaisinfhoghlaim/agents/tools/` to archive directory `openspec/changes/meaisinfhoghlaim-audit-phase-4-remove-duplicate-tools-pkg-and-fix-broken-relative-imports/archive/sruth/meaisinfhoghlaim/agents/tools/`
- [ ] Update 4 broken relative imports:
  - [ ] `sruth/meaisinfhoghlaim/agents/agui_curriculum_agent.py:25-28`: `from ..tools.curriculum_search import (compare_curricula, search_curriculum)` → `from sruth.oideachais.tools.curriculum_search import (compare_curricula, search_curriculum)`
  - [ ] `sruth/meaisinfhoghlaim/agents/curriculum_comparison_agent.py:14-19`: `from ..tools.curriculum_search import (compare_curricula, find_similar_content, get_learning_outcomes, search_curriculum)` → `from sruth.oideachais.tools.curriculum_search import (compare_curricula, find_similar_content, get_learning_outcomes, search_curriculum)`
  - [ ] `sruth/meaisinfhoghlaim/agents/geospatial_agent.py:15-20`: `from ..tools.spatial_query import (find_nearby_schools, get_area_statistics, get_deprivation_correlation, query_by_area)` → `from sruth.oideachais.tools.spatial_query import (find_nearby_schools, get_area_statistics, get_deprivation_correlation, query_by_area)`
  - [ ] `sruth/meaisinfhoghlaim/agents/statistics_agent.py:15-20`: `from ..tools.statistics_query import (compare_nations, get_trend, list_available_metrics, query_statistics)` → `from sruth.oideachais.tools.statistics_query import (compare_nations, get_trend, list_available_metrics, query_statistics)`
- [ ] Update `sruth/meaisinfhoghlaim/README.md` "Known issues" table — add 2 RESOLVED rows: (a) duplicate `agents/tools/` byte-identical to `oideachais/tools/`, (b) 4 broken `from ..tools.X` relative imports
- [ ] Verify post-state: `grep -rn "from \.\.tools\." sruth/meaisinfhoghlaim/agents/*.py` returns 0 hits
- [ ] Verify post-state: `ls sruth/meaisinfhoghlaim/agents/tools/` returns "No such file or directory"
- [ ] Verify post-state: `PYTHONPATH=./sruth ./.venv/bin/python -c "from sruth.meaisinfhoghlaim.agents.agui_curriculum_agent import agui_curriculum_agent"` (currently fails due to `agui_curriculum_agent.py:25-28` broken import + `__init__.py` chain → `agui_curriculum_agent` may still fail because of unrelated `from ..tools.curriculum_search` in __init__.py chain. If fails for an UNRELATED reason after our fix, that is out of scope.)
- [ ] Run `mise run lint:skills` (138/138 pass)

## Commit + push

- [ ] Stage only files for this phase: 4 agent file rewrites + 1 README.md update + 10 archive moves (via git mv into the archive subdir)
- [ ] **Do NOT stage**: pre-existing in-flight work in `.agents/skills/`, `.infisical.env`, `infrastructure/AGENTS.md`, ROOT `pyproject.toml`, `sruth/oideachais/notebooks/dashboards/education/all_nations.py`, `sruth/oideachais/celtic/duchas.py`, `sruth/oideachais/subjects/subjects/*`, `spaces/data-engineering`, `infrastructure/komodo/*`, `openspec/changes/add-open{chamber,claw}-*`, `infrastructure/stacks/open{chamber,claw}/`
- [ ] Commit 1: `refactor(meaisinfhoghlaim): round 11 phase 4 — remove duplicate agents/tools + fix 4 broken relative imports`
- [ ] Push to `q3-2026-oideachais-consolidation`
- [ ] Run `openspec archive meaisinfhoghlaim-audit-phase-4-remove-duplicate-tools-pkg-and-fix-broken-relative-imports --yes`
- [ ] Commit 2: `docs(openspec): apply Phase 4 spec delta to meaisinfhoghlaim-platform`
- [ ] Push to `q3-2026-oideachais-consolidation`
- [ ] Verify `git status` shows "up to date with origin"

## Post-archive

- [ ] Verify `openspec/specs/meaisinfhoghlaim-platform/spec.md` contains 2 new ADDED Requirements (no-duplicate-agent-tools-across-quadrants; no-broken-relative-tool-imports-in-meaisinfhoghlaim-agents)
- [ ] Verify `openspec/changes/meaisinfhoghlaim-audit-phase-4-remove-duplicate-tools-pkg-and-fix-broken-relative-imports/` no longer in `openspec list` output
- [ ] Verify `openspec list` shows the next pending change (likely a tuatha audit phase if continuing Round 11)
