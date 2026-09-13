# llm-extraction-framework Specification

## Purpose
TBD - created by archiving change 2026-09-13-baml-health-test-and-skill-update-v1. Update Purpose after archive.

## Requirements

### Requirement: BAML Toolchain Health Detection

The system SHALL detect BAML toolchain drift (CLI vs library version
mismatch, BAML source file inventory regression) via automated tests so
that future work can identify when the BAML compilation pipeline breaks
or recovers.

#### Scenario: baml-cli binary is available

- **WHEN** any developer runs `uv run pytest tests/baml/`
- **THEN** `baml-cli --version` exits 0
- **AND** the version matches a known-good BAML release (0.223-0.226)

#### Scenario: BAML source inventory is stable

- **WHEN** any developer runs `uv run pytest tests/baml/`
- **THEN** the baml_src directory contains ≥ 300 `.baml` files
- **AND** the 4 canonical client files exist:
  - `baml_src/clients.baml`
  - `baml_src/clients_image_gen.baml`
  - `baml_src/clients_llama_swap.baml`
  - `baml_src/clients_ocr_ensemble.baml`

#### Scenario: Templates are separated from compilable BAML

- **WHEN** `baml_src/_shared/templates/` exists
- **THEN** each `.baml` template references `DomainExtractor`
  (a Python-style placeholder, processed by `baml_bulk_replace_stubs.py`)
- **AND** the templates are NOT intended for direct `baml-cli generate`

#### Scenario: baml-cli generate failure is detected

- **WHEN** `baml-cli generate --from ./baml_src` runs (currently expected to fail)
- **THEN** the test emits a `UserWarning` if the exit code is 0
  (signal that the broken stub files were fixed)
- **AND** the test fails if the exit code is non-zero AND the error
  doesn't match the known "Failed to build BAML runtime" pattern
