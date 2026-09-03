# Change: oideachais-v0-to-v1-migration

## Why

Round 9 of the multi-quadrant refactor plan. The
`sruth/oideachais/` subagent's deep-dive report (2026-06-24) identified:

- **10 v0 broken CocoIndex modules** in
  `sruth/oideachais/cocoindex_flows/`:
  `author_archive_embedding.py`, `curriculum_embedding.py`,
  `curriculum_translation.py`, `curriculum_specification_extraction.py`,
  `geospatial_indexing.py`, `learning_outcome_graph.py`,
  `ocr_embedding.py`, `pdf_embedding.py`,
  `research_embedding.py`, `site_analysis_embedding.py`
- The 10 v0 modules are guarded by `try/except` in
  `__init__.py` but live on disk unguarded; any direct import
  raises `ImportError` on `cocoindex==1.0.9`
- The `sruth/oideachais/cocoindex_flows/README.md` says "Migrate to v1
  (deferred)" for the 10 v0 modules — the deferral is now 6 weeks
  overdue
- The migration backlog was supposed to be completed by Q3-2026
  per `sruth/oideachais/REFACTORING.md` #6 — it's now Q3-2026
- 3 new skills are landing:
  `oideachais-leabharlann`, `oideachais-baml-schemas`,
  `oideachais-cocoindex-v1` (708 lines combined)

This change codifies the v0→v1 migration: move the 10 broken v0
modules to `_v0_archive/` (deprecation rather than migration;
the migration is too big to do in one commit), update the
`__init__.py` to remove the now-stale docstring reference to
`__init__.py`-level guard, and add the 3 new skills to the
`sruth/oideachais/AGENTS.md`.

## What Changes

### 1. `oideachais-cocoindex-v1-migration` spec (MODIFIED + ADDED)

1 MODIFIED Requirement ("V1 CocoIndex Apps") + 1 ADDED
Requirement ("V0 Archive") that codify the 11 v1 Apps + the
deprecation of the 10 v0 modules.

### 2. Refactor: 10 v0 modules → `_v0_archive/`

The 10 v0 broken modules move to
`sruth/oideachais/cocoindex_flows/_v0_archive/`. The directory is
created with a `__init__.py` documenting the deprecation:

```python
# sruth/oideachais/cocoindex_flows/_v0_archive/__init__.py
"""
v0 CocoIndex modules (DEPRECATED 2026-06-24).

These 10 modules were written against the removed v0 DSL
(@cocoindex.flow_def, FlowBuilder, DataScope, cocoindex.sources,
cocoindex.targets). They raise ImportError on cocoindex==1.0.9.

The 11 v1 Apps at oideachais.cocoindex_flows.* cover the equivalent
use cases (see oideachais-cocoindex-v1/SKILL.md). No v0 migration
is planned in this change; the modules are preserved for historical
reference only.
"""
```

The 10 v0 files (`author_archive_embedding.py`,
`curriculum_embedding.py`, `curriculum_translation.py`,
`curriculum_specification_extraction.py`, `geospatial_indexing.py`,
`learning_outcome_graph.py`, `ocr_embedding.py`, `pdf_embedding.py`,
`research_embedding.py`, `site_analysis_embedding.py`) move via
`git mv` and are kept on disk for historical reference.

### 3. Refactor: `__init__.py` cleanup

`sruth/oideachais/cocoindex_flows/__init__.py` currently says:

> The previous v0 code is preserved at `sruth/oideachais/cocoindex_flows/_v0_archive/`

This is misleading — `_v0_archive/` doesn't exist. The
deprecation directory is created in this change, so the
docstring becomes accurate.

### 4. Refactor: `cocoindex_flows/README.md` update

The v0/v1 status table in the README updates the 10 "Migrate to v1
(deferred)" rows to "DEPRECATED 2026-06-24, archived at
`_v0_archive/`".

### 5. 3 new skills land

- `.agents/skills/oideachais-leabharlann/SKILL.md` (186 lines)
- `.agents/skills/oideachais-baml-schemas/SKILL.md` (218 lines)
- `.agents/skills/oideachais-cocoindex-v1/SKILL.md` (304 lines)

### 6. 2 doc updates (1-line diffs each)

- `sruth/oideachais/AGENTS.md` — add 3 new skill entries to the Quick
  routing table
- `sruth/oideachais/STATUS.md` §3 — change "11 modules (11 v1 working
  + 11 v0 broken — only 5 of 11 v1 re-exported via try/except)" to
  "11 v1 Apps + 10 v0 DEPRECATED modules (archived at _v0_archive/)"

## Impact

- Affected specs: `oideachais-cocoindex-v1-migration` (1 MODIFIED + 1 ADDED)
- Affected skills: 3 new (oideachais-leabharlann, oideachais-baml-schemas, oideachais-cocoindex-v1)
- Affected code: 10 v0 modules move to `_v0_archive/`
- 1 commit + 1 archive commit per the established pattern

## Success criteria

- `from oideachais.cocoindex_flows.author_archive_embedding import ...`
  raises a `ModuleNotFoundError` (or similar) with a helpful
  message pointing at `_v0_archive/`
- `oideachais.cocoindex_flows.research_embedding` (the v0 file) is no
  longer importable; the v1 `research_embedding_v1` (or equivalent)
  is the canonical home
- 3 new skills exist with valid frontmatter
- `sruth/oideachais/cocoindex_flows/_v0_archive/__init__.py` documents the
  deprecation
- `sruth/oideachais/cocoindex_flows/README.md` v0/v1 status table is
  accurate
- `openspec validate oideachais-v0-to-v1-migration --strict` passes
- 1 commit + 1 archive commit land on `q3-2026-oideachais-consolidation`

## Out of scope (deferred to follow-on changes)

- The 50+ dlt source migration from `dlt_sources/{ireland,uk,crown_dependencies}/`
  to `dlt_sources/domains/education/{nation}/` — the
  `lateralise-dlt-sources-to-domains` change is in-flight per
  the openspec list
- The 3 graph backend consolidation
  (`cognee_integration/` + `graph/{cognee,falkordb,memgraph}/`) —
  a 2-week project per REFACTORING.md #8
- The BAML extraction wiring (the 4 Aistear + Primary + JC
  functions that are defined but not invoked) — a 1-week
  project per REFACTORING.md #1
