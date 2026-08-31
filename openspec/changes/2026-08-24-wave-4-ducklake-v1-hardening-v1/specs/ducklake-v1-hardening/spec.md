# ducklake-v1-hardening Specification

## Purpose

`ducklake-v1-hardening` is a capability of the Cianfhoghlaim platform
that codifies the Wave 4 DuckLake v1.0 hardening: the canonical
5-namespace `metadata_schema` per quadrant, the `SORTED BY` clause on
hot tables, and the nightly Dagster maintenance asset chain.

This spec captures Wave 4 of the 2026-08-24 master refactor plan.

## ADDED Requirements

### Requirement: 5-quadrant metadata_schema

Every per-pipeline Component in `orchestration/defs/` MUST declare the
canonical 5-quadrant `metadata_schema`: `oideachais` for education,
`tuatha` for game, `croilar` for cross-cutting, `agents` for agent
traces, `media` for media. The 6th namespace `tuatha_legacy` SHALL
be deprecated and aliased to `tuatha`.

#### Scenario: Every pipeline has the canonical metadata_schema

- **WHEN** `find orchestration/defs -name "*.yaml" -not -path "*__pycache__*" | xargs grep -L "metadata_schema:" 2>/dev/null` runs
- **THEN** the result SHALL be empty
- **AND** `python -c "from ducklake import get_namespace; print(get_namespace('oideachais'))"` succeeds

### Requirement: SORTED BY on hot tables
The system SHALL have `SORTED BY (jurisdiction, stage, subject)`.
in their `ALTER TABLE` statements.

#### Scenario: Hot tables are sorted

- **WHEN** `duckdb md:cianfhoghlaim.ducklake -c "DESCRIBE oideachais.lc_gaeilge_papers"` runs
- **THEN** the output SHALL include `jurisdiction, stage, subject` in the column list
- **AND** the `ORDER BY` is set to match

### Requirement: Nightly Dagster maintenance chain

The nightly Dagster asset chain SHALL be: `expire_snapshots` →
`cleanup_old_files` → `merge_adjacent_files` → `rewrite_data_files`.
This chain runs every night at 02:00 UTC.

#### Scenario: Nightly maintenance runs

- **WHEN** the cron triggers at 02:00 UTC
- **THEN** all 4 maintenance assets complete successfully
- **AND** the DuckLake catalog shows reduced file count (merged/rewritten)
