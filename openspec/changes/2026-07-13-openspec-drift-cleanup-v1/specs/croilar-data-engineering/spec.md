# Spec Delta — croilar-data-engineering

This delta modifies existing requirements in the `croilar-data-engineering` capability (renamed `sruth.croilar.X` → `croilar.X` in canonical-positive scenarios + renamed `sruth.oideachais.X` → `oideachais.X`) and adds one new requirement to codify the v4 namespace convention.

## ADDED Requirements

### Requirement: Openspec spec text uses v4 namespace convention (no `sruth.X` drift)

The `croilar-data-engineering` capability spec SHALL use the v4 namespace convention throughout. Concretely:

1. **Canonical Python import paths** in scenarios SHALL use the v4 form:
   - `from croilar.dlt_utils.destinations import NAMESPACE` (NOT `from sruth.croilar.dlt_utils.destinations import NAMESPACE`)
   - `from croilar.pipelines.shared.r2_client import R2Client` (NOT `from sruth.croilar.pipelines.shared.r2_client import R2Client`)
   - `from croilar._shared.streams import ...` (NOT `from sruth.croilar._shared.streams import ...`)
   - `from croilar._shared.database import ...` (NOT `from sruth.croilar._shared.database import ...`)
   - `from oideachais.dlt_utils.destinations import with_namespace` (NOT `from sruth.oideachais.dlt_utils.destinations import with_namespace`)
2. **Historical refs** (e.g. the v3-era packaging fix at `e9e0fc7d2` that put `sruth/` on `sys.path` so `import sruth.oideachais` worked) SHALL be preserved verbatim — they document the v3 → v4 transition.
3. **The factory pattern** `oideachais.dlt_utils.destinations.with_namespace("croilar")` is the canonical way for the croilar quadrant to obtain its namespaced destination — SHALL be preserved.

#### Scenario: A spec contributor edits the croilar-data-engineering spec

- **GIVEN** a contributor wants to add a new scenario to the croilar-data-engineering spec at `openspec/specs/croilar-data-engineering/spec.md`
- **WHEN** the contributor writes a Python import statement in the scenario
- **THEN** the import SHALL use the v4 form `from croilar.<module> import <symbol>` (NOT `from sruth.croilar.<module> import <symbol>`)
- **AND** cross-quadrant imports SHALL use the v4 form `from oideachais.<module> import <symbol>` (NOT `from sruth.oideachais.<module> import <symbol>`)
- **AND** if the contributor wants to document the v3 → v4 transition (e.g. the pre-fix `import sruth.oideachais` behavior), they SHOULD use the parenthetical "(after the packaging fix at commit `e9e0fc7d2`)" form

#### Scenario: The canonical namespace factory still works

- **GIVEN** the `oideachais.dlt_utils.destinations.with_namespace("croilar")` factory
- **WHEN** the croilar quadrant imports `NAMESPACE` via `from croilar.dlt_utils.destinations import NAMESPACE`
- **THEN** `NAMESPACE == "croilar"`
- **AND** the value comes from the canonical `oideachais.dlt_utils.destinations.with_namespace("croilar")` factory
- **AND** the local fallback at `croilar/dlt_utils/destinations.py` (if it still exists) is dead code and MUST be removed (~88 lines of duplication)

#### Scenario: The R2Client remains importable from the canonical croilar location

- **GIVEN** the v4 `croilar.pipelines.shared.r2_client` module
- **WHEN** a consumer does `from croilar.pipelines.shared.r2_client import R2Client`
- **THEN** the import succeeds
- **AND** the canonical Stream registry remains importable from `croilar._shared.streams`
- **AND** `tests/test_database.py` remains importable from `croilar._shared.database`

#### Scenario: The openspec drift cleanup baseline is preserved

- **GIVEN** the `2026-07-13-openspec-drift-cleanup-v1` change has landed
- **WHEN** `grep -rE "sruth\.croilar\." openspec/specs/croilar-data-engineering/spec.md` runs
- **THEN** the count of `sruth.croilar.*` refs in canonical-positive contexts is 0
- **AND** the only remaining `sruth.*` ref is the historical `import sruth.oideachais` packaging-fix context on line 182 (preserved verbatim per the "historical refs SHALL be preserved" rule)
- **AND** `openspec validate croilar-data-engineering --strict` returns valid (the spec was already valid before this drift cleanup)