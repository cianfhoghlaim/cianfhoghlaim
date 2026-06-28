# Spec Delta: meaisinfhoghlaim-platform — Phase 4 (remove duplicate `agents/tools/` + fix 4 broken relative imports)

## ADDED Requirements

### Requirement: No duplicate agent-tools package across quadrants

The meaisínfhoghlaim quadrant MUST NOT contain a `tools/` package
that duplicates `sruth/oideachais/tools/`. The canonical home for
all Celtic-education agent tools (corpus search, curriculum search,
spatial query, statistics query, terminology, translation) is
`sruth/oideachais/tools/`, importable as
`from sruth.oideachais.tools.X import ...`.

Meaisínfhoghlaim agent code MUST import tools from the canonical
oideachais location (e.g.
`from sruth.oideachais.tools.curriculum_search import compare_curricula`),
NOT from a meaisínfhoghlaim-local `tools/` package
(e.g. `from sruth.meaisinfhoghlaim.tools.curriculum_search import ...`).

#### Scenario: A meaisínfhoghlaim agent file imports from a duplicate `agents/tools/` location

- **GIVEN** `sruth/meaisinfhoghlaim/agents/tools/` does not exist
  (verified via `ls sruth/meaisinfhoghlaim/agents/tools/`)
- **AND** `sruth/oideachais/tools/` exists as the canonical home
  (verified via `ls sruth/oideachais/tools/`)
- **WHEN** a meaisínfhoghlaim agent file imports from
  `from sruth.meaisinfhoghlaim.agents.tools.X import ...`
- **THEN** Python raises
  `ModuleNotFoundError: No module named 'sruth.meaisinfhoghlaim.agents.tools'`
- **AND** the import MUST be rewired to the canonical home
  `from sruth.oideachais.tools.X import ...`

#### Scenario: A future contributor adds a new tool to a meaisínfhoghlaim agent

- **GIVEN** a meaisínfhoghlaim agent file needs a new tool
- **WHEN** the contributor adds the import
- **THEN** the contributor MUST first check whether the canonical
  home `sruth/oideachais/tools/` already provides the needed symbol
  (verified via `PYTHONPATH=./sruth python3 -c "from sruth.oideachais.tools.X import <symbol>"`)
- **AND** the contributor MUST import from the canonical oideachais
  location, NOT create a new `sruth/meaisinfhoghlaim/agents/tools/` package
- **AND** if the symbol is NOT in the canonical home, the contributor
  MUST add the new tool to `sruth/oideachais/tools/`, NOT to a
  meaisínfhoghlaim-local duplicate

### Requirement: No broken relative tool imports in meaisínfhoghlaim agent files

The meaisínfhoghlaim `agents/` subtree MUST NOT contain any
`.py` file with a top-level (module-load-time) `from ..tools.X`
relative import. The path `sruth/meaisinfhoghlaim/tools/` does not
exist; any `from ..tools.X` import from a file under
`sruth/meaisinfhoghlaim/agents/` resolves to
`sruth/meaisinfhoghlaim/tools/X` and MUST raise
`ModuleNotFoundError` at module load time.

Every tool import in meaisínfhoghlaim agent code MUST be either:

1. An absolute cross-quadrant import from the canonical oideachais
   home (e.g. `from sruth.oideachais.tools.curriculum_search import ...`),
   OR
2. A relative import that resolves correctly within the same package
   (e.g. `from .tools.X import ...` if `sruth/meaisinfhoghlaim/agents/tools/`
   is the canonical home — but currently no such home exists, so
   option 1 is the only valid path).

#### Scenario: A meaisínfhoghlaim agent file uses `from ..tools.X` for a tool

- **GIVEN** a `.py` file under `sruth/meaisinfhoghlaim/agents/`
  (e.g. `agui_curriculum_agent.py:25`,
  `curriculum_comparison_agent.py:14`,
  `geospatial_agent.py:15`,
  `statistics_agent.py:15`)
- **AND** the file contains a top-level import
  `from ..tools.X import ...`
- **AND** `sruth/meaisinfhoghlaim/tools/` does not exist
  (verified via `ls sruth/meaisinfhoghlaim/tools/`)
- **WHEN** the file is imported by any caller
- **THEN** Python raises
  `ModuleNotFoundError: No module named 'sruth.meaisinfhoghlaim.tools'`
  at module load time (NOT at function call time)
- **AND** the import MUST be rewired to the absolute canonical path
  `from sruth.oideachais.tools.X import ...`

#### Scenario: A future contributor adds a new tool import to a meaisínfhoghlaim agent

- **GIVEN** a meaisínfhoghlaim `agents/*.py` file needs a new tool import
- **WHEN** the contributor adds the import
- **THEN** the contributor MUST first verify the target module
  exists via `ls <target-path>/X.py`
- **AND** the contributor MUST first verify the canonical symbol is
  importable via
  `PYTHONPATH=./sruth python3 -c "from sruth.oideachais.tools.X import <symbol>"`
- **AND** the import line MUST use the absolute canonical path
  `from sruth.oideachais.tools.X import ...`,
  NOT the broken relative path `from ..tools.X import ...`
