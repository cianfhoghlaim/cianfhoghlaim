# cocoindex-v0-stragglers Specification

## Purpose

`cocoindex-v0-stragglers` is a capability of the Cianfhoghlaim platform
that tracks the 18 v0 CocoIndex files (excluding `__init__.py` markers)
that have NOT yet been migrated to v1 API. Wave 3 will execute the
rewrite.

This spec captures Wave 3 of the 2026-08-24 master refactor plan.

## ADDED Requirements

### Requirement: v0 stragglers inventory
The system SHALL be inventoried here so Wave 3 can.
execute the rewrite. The full list is in
`openspec/changes/2026-08-24-wave-3-cocoindex-v0-stragglers-v1/spec.md`.

#### Scenario: The v0 inventory is captured

- **WHEN** `find cocoindex_flows -name "*.py" -not -path "*__pycache__*" | xargs grep -L "import cocoindex as coco\|@coco\.fn\|coco\.App\|coco\.ContextKey" 2>/dev/null` runs
- **THEN** the resulting file count SHALL equal 18 (or its post-Wave-3 update)

### Requirement: Wave 3 migration plan

The 18 v0 files SHALL be migrated to v1 API in Wave 3 of the master
refactor plan. The migration MUST preserve the runtime behavior of every
App.

#### Scenario: Wave 3 migration executes end-to-end

- **WHEN** Wave 3 lands
- **THEN** `find cocoindex_flows -name "*.py" -not -path "*__pycache__*" | xargs grep -l "from cocoindex.connectors import lancedb\|from cocoindex.connectors import qdrant" 2>/dev/null` returns empty
- **AND** `dg list defs` lists all 18 formerly v0 CocoIndex App assets
- **AND** `mise run sync:dagster` passes without errors
