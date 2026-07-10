# Spec Delta — meaisinfhoghlaim-platform

This delta modifies existing requirements in the `meaisinfhoghlaim-platform` capability (renamed `sruth.<quadrant>.X` → `<quadrant>.X` in canonical-positive scenarios + renamed `dagster_defs` → `orchestration`) and adds one new requirement to codify the v4 namespace convention.

## MODIFIED Requirements

### Requirement: Lakehouse ingest uses the v4 `orchestration/` namespace

The system SHALL ingest from the oideachais DuckLake catalog via the
`oideachais.orchestration` package (formerly `oideachais.dagster_defs`).

#### Scenario: Lakehouse-to-meaisinfhoghlaim ingest routes through `oideachais.orchestration`

- **GIVEN** the v4 Dagster orchestration tree at `cianfhoghlaim/orchestration/` containing `defs/`, `definitions.py`, `components/`, `defs.yaml`
- **WHEN** a meaisinfhoghlaim consumer wants to ingest from the oideachais DuckLake catalog
- **THEN** the consumer MUST import via `from oideachais.orchestration.definitions import defs` (the v4 path)
- **AND** the legacy `from oideachais.dagster_defs.definitions import defs` path MUST raise `ModuleNotFoundError`

## ADDED Requirements

### Requirement: Openspec spec text uses v4 namespace convention (no `sruth.X` drift)

The `meaisinfhoghlaim-platform` capability spec SHALL use the v4 namespace convention throughout. Concretely:

1. **Canonical Python import paths** in scenarios SHALL use the v4 form: `from <quadrant>.<module> import <symbol>` (e.g. `from oideachais.core.utils import CircuitBreaker`, `from oideachais.tools.curriculum_search import compare_curricula`) — NOT `from sruth.oideachais.<module> import <symbol>`. The `sruth.oideachais.*` and `sruth.meaisinfhoghlaim.*` namespaces no longer exist post-v4.
2. **Negative-test scenarios** for phantom-duplicate imports (e.g. `ModuleNotFoundError: No module named 'meaisinfhoghlaim.agents.tools'`) SHALL retain their `sruth.<quadrant>.<phantom>` references — these are intentional checks that the codebase doesn't import from non-existent module paths. Renaming them would defeat the test logic.
3. **Typo-test scenarios** for the `sruth.oideachas` (Irish nominative, single 's') typo SHALL retain their `sruth.oideachas` references — these are intentional checks for the non-existent typo'd package path.
4. **Stale-subpath refs** SHALL be renamed to their v4 equivalents: `oideachais.dagster_defs.X` → `oideachais.orchestration.defs.X`.

#### Scenario: A spec contributor edits the meaisinfhoghlaim-platform spec

- **GIVEN** a contributor wants to add a new scenario to the meaisinfhoghlaim-platform spec at `openspec/specs/meaisinfhoghlaim-platform/spec.md`
- **WHEN** the contributor writes a Python import statement in the scenario
- **THEN** the import SHALL use the v4 form `from oideachais.<module> import <symbol>` (NOT `from sruth.oideachais.<module> import <symbol>`)
- **AND** the import SHALL use the v4 form `from meaisinfhoghlaim.<module> import <symbol>` (NOT `from sruth.meaisinfhoghlaim.<module> import <symbol>`)
- **AND** the contributor SHALL use `oideachais.orchestration.X` for Dagster references (NOT `oideachais.dagster_defs.X`)
- **AND** if the contributor wants to test for a phantom-duplicate import (e.g. `ModuleNotFoundError` for a non-existent module), they SHOULD keep the `sruth.<quadrant>.<phantom>` form in the test scenario

#### Scenario: The openspec drift cleanup baseline is preserved

- **GIVEN** the `2026-07-13-openspec-drift-cleanup-v1` change has landed
- **WHEN** `grep -rE "sruth\.oideachais\.|sruth\.meaisinfhoghlaim\." openspec/specs/meaisinfhoghlaim-platform/spec.md` runs
- **THEN** the count of `sruth.<quadrant>.*` refs in canonical-positive contexts is 0
- **AND** the remaining `sruth.*` refs (if any) are:
  - 4 `sruth.oideachas` typo-test refs in the "No stale `sruth.oideachas` path references" Requirement (lines 258-282) — KEEP
  - Phantom-duplicate negative-test refs in the "no duplicate agent-tools" + "no broken relative tool imports" + "no pre-split multi-source DLT file" Requirements — KEEP
- **AND** `oideachais.dagster_defs` count is 0 (all renamed to `oideachais.orchestration` per line 111 + the ADDED Requirement)
- **AND** `openspec validate meaisinfhoghlaim-platform --strict` returns the same 3 pre-existing errors as HEAD `54c21dd52` (Requirements outside main section, not new errors introduced by this drift cleanup)