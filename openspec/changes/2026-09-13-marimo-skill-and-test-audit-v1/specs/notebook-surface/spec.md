## ADDED Requirements

### Requirement: Marimo Notebook Surface Inventory

The system SHALL keep the Marimo skill aligned with the actual notebook
count and document which notebooks are present vs lost (Phase 16-29 disaster).

#### Scenario: Marimo library version is documented

- **WHEN** any developer runs `uv run pytest tests/marimo/`
- **THEN** `uv pip show marimo` reports version ≥ 0.20
- **AND** `.agents/skills/marimo/SKILL.md` documents the notebook count
  matching reality (≥50 notebooks)

#### Scenario: Shared patterns module is canonical

- **WHEN** any developer runs `uv run pytest tests/marimo/`
- **THEN** `notebooks/_shared/marimo_patterns.py` exists
- **AND** it defines the R1 `setup_biep_registry_header` function

#### Scenario: BIEP lakehouse notebooks are present

- **WHEN** any developer runs `uv run pytest tests/marimo/`
- **THEN** `notebooks/` contains ≥ 15 `10_biep_pipeline_lakehouse_*.py` files

#### Scenario: Lost LC subject panel is documented

- **WHEN** any developer runs `uv run pytest tests/marimo/`
- **THEN** the LC subject panel status test passes (file may or may not
  exist; informational)
- **AND** the skill documents the lost state

#### Scenario: Marimo CLI is available

- **WHEN** `uv run marimo --version` is executed
- **THEN** it succeeds (showing `marimo X.Y.Z`)
