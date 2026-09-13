## ADDED Requirements

### Requirement: Dagster Skill Currency

The system SHALL keep the Dagster skill aligned with the installed
library and document the per-jurisdiction orchestrator architecture
(JurisdictionAssetsBase ABC + 10 jurisdiction shims).

#### Scenario: Dagster library version is documented

- **WHEN** any developer runs `uv run pytest tests/dagster/`
- **THEN** `uv pip show dagster` reports version ≥ 1.0
- **AND** `.agents/skills/dagster/SKILL.md` documents the asset +
  asset_check counts matching reality (≥100 @asset, ≥30 @asset_check)

#### Scenario: Per-jurisdiction shim count is stable

- **WHEN** any developer runs `uv run pytest tests/dagster/`
- **THEN** `orchestration/defs/2_materials/_base/` contains ≥ 8
  `*_assets.py` shim files (one per jurisdiction)

#### Scenario: JurisdictionAssetsBase ABC exists

- **WHEN** the per-jurisdiction shim pattern is in use
- **THEN** `orchestration/defs/2_materials/_base/jurisdiction_assets_base.py`
  exists and defines the canonical `JurisdictionAssetsBase` ABC

#### Scenario: Lost factory is documented

- **WHEN** any developer runs `uv run pytest tests/dagster/`
- **THEN** `test_build_jurisdiction_assets_factory_missing` passes
  (the file does NOT exist; this test is informational and documents
  that the Phase 17.1 factory pattern is still pending restoration)

#### Scenario: dg CLI is available

- **WHEN** `uv run dg --version` is executed
- **THEN** it either succeeds (showing `dg X.Y.Z`) or is silently skipped
- **AND** if it fails, the test is marked xfail with reason
  "`dg` CLI not installed; install via `pip install dagster-dg-cli`"
