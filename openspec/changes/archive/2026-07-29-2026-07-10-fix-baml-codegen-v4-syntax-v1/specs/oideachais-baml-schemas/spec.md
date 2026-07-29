# Spec Delta — cianfhoghlaim-baml-schemas

This delta adds 2 new Requirements to the existing 16 (16 → 18).
The MODIFIED section is the new requirements only; the existing
16 requirements are preserved unchanged.

## ADDED Requirements

### Requirement: baml_client regenerates with 0 errors in the processing cluster

The `baml_client/` Python module SHALL regenerate cleanly (`mise run baml:generate`
exits 0 with respect to the 17 processing-cluster files) after migrating all
`.baml` files in `baml/processing/` from the deprecated
Pydantic-style `field: type` syntax to BAML v0.212+ canonical
`field type` (whitespace-separated) syntax.

#### Scenario: baml:generate succeeds for the 17 migrated processing files

- **GIVEN** the 17 `.baml` files in `baml/processing/` are
  rewritten to canonical v0.212+ syntax (per
  `scripts/migrate-baml-syntax.py --apply`)
- **WHEN** `mise run baml:generate` is run and the validator reaches the
  processing cluster
- **THEN** the validator reports 0 Pydantic-style errors in those 17 files
- **AND** `baml_client/` is regenerated at
  `baml/shared/baml_client/`

#### Scenario: Migration script is idempotent

- **GIVEN** `scripts/migrate-baml-syntax.py --apply` has been run on the
  17 target files
- **WHEN** `scripts/migrate-baml-syntax.py --dry-run` is re-run
- **THEN** the script reports 0 changes pending
- **AND** no files are modified

### Requirement: baml syntax migration helper at scripts/migrate-baml-syntax.py

A `scripts/migrate-baml-syntax.py` helper SHALL exist with `--dry-run`,
`--apply`, and `--verify` modes for rewriting `.baml` files from
Pydantic-style `field: type` to BAML v0.212+ canonical `field type`
(whitespace-separated) syntax. The script SHALL defensively skip lines
inside `#"...content...#` raw-string blocks (prompt bodies + test-arg
docs) and lines containing `{{`/`}}` Jinja tokens, so it never rewrites
content inside BAML prompts.

#### Scenario: --dry-run prints diffs without modifying files

- **WHEN** `uv run python scripts/migrate-baml-syntax.py --dry-run` is run
- **THEN** the script prints the per-file change counts and the first 10
  before/after diffs for each file
- **AND** no `.baml` file is modified

#### Scenario: --apply rewrites files in place

- **WHEN** `uv run python scripts/migrate-baml-syntax.py --apply` is run
- **THEN** each of the 17 target `.baml` files is rewritten with
  `field: type` replaced by `field type` (plus any `[]` / `?` /
  `@description(...)` attrs preserved)
- **AND** the script reports the line count rewritten per file

#### Scenario: --verify exits 1 if any Pydantic-style lines remain

- **WHEN** `uv run python scripts/migrate-baml-syntax.py --verify` is run
- **THEN** the script exits 0 with `[OK] No Pydantic-style attribute lines remain`
  if all 17 target files are canonical
- **AND** exits 1 with `[FAIL] N Pydantic-style lines remain` otherwise,
  listing each remaining line by `file:lineno`