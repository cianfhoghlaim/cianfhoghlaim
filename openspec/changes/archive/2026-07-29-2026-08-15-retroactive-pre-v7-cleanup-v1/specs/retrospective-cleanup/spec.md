# Spec delta: `retrospective-cleanup`

This delta is part of the openspec change
`2026-08-15-retroactive-pre-v7-cleanup-v1`. The 5 ADDED Requirements
(retroactive cleanup, per-directory reports, sync:dagster,
dagster_sync_health asset, dagster_assets Cognee cluster,
dagster-asset-sync skill) were already added to the canonical
spec by the parallel-session work. This delta adds ONE additional
requirement covering the safe-auto-fix semantics that the
implementation spec didn't capture.

## ADDED Requirements

### Requirement: Safe auto-fix mode requires AST validation

The system SHALL validate every file modification made by
`sync:paths --fix` via `ast.parse()` for Python files (skips
non-Python files like `.md`, `.json`, `.yaml`). The fix-mode
SHALL refuse to modify a file if `ast.parse()` raises a
`SyntaxError` post-rename, and SHALL report the file path + line
number to the fix-applied report.

#### Scenario: AST validation fails on a renamed file

- **GIVEN** `sync:paths --fix` renames a path inside a `.py` file
- **WHEN** the post-rename `ast.parse()` raises a `SyntaxError`
- **THEN** the fix-mode SHALL revert the change to the original file
- **AND** the fix-applied report SHALL include the file path + line
  number + the SyntaxError message
- **AND** the fix-mode exit code SHALL be 2 (partial failure)

#### Scenario: AST validation passes on all renamed files

- **GIVEN** `sync:paths --fix` renames a path inside 50 `.py` files
- **WHEN** all 50 files post-rename `ast.parse()` cleanly
- **THEN** the fix-mode SHALL commit all 50 renames
- **AND** the fix-applied report SHALL list the 50 file paths
- **AND** the fix-mode exit code SHALL be 0 (success)
