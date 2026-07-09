## ADDED Requirements

### Requirement: CocoIndex v1 App canonical pattern

Every CocoIndex flow under `cianfhoghlaim/cocoindex/*.py` SHALL conform to the v1 4-rule contract:

- **R1 — `coco_lifespan` mandate**: each flow uses the shared lifespan from `_lifespan.py` for the embedder + vector store + chunker (no per-flow ad-hoc clients). A flow may declare additional ContextKeys, but only with a sibling `# R2-exempt: <reason>` comment documenting the reason.
- **R2 — canonical `coco.App`**: each flow declares `coco.App(...)` (either at module scope, or via the `@coco.App(shared_lifespan)` decorator pattern from early v1.0.x — both pass the R2 regex).
- **R3 — `mount_table_target` for vector sinks**: vector-store flows use `lancedb.mount_table_target(LANCE_DB, ...)` (not yield-dict loops, not the legacy `lancedb.TableTarget(db=..., embedding=...)` direct construction).
- **R4 — `declare_vector_index`**: the embedding column is indexed via `target_table.declare_vector_index(column="embedding")`. Flows that do NOT write to a LanceDB table with an `embedding` column (e.g. GeoParquet-only outputs like `apple_photos_geospatial.py`) SHALL add a sibling `# R4-exempt: <reason>` comment line.

The system SHALL provide a **`cocoindex_v1_migrate.py`** tool at `cianfhoghlaim/dlt/common/cocoindex_v1_migrate.py` that audits every flow file for the 4 rules and reports violations (idempotent per-flow; non-destructive by default; supports `# R4-exempt` markers).

#### Scenario: All 47 flows pass the 4-rule audit

- **WHEN** the user runs `uv run python cianfhoghlaim/dlt/common/cocoindex_v1_migrate.py --check-only`
- **THEN** the tool prints a per-flow table with pass / fail for each of R1, R2, R3, R4
- **AND** exits 0 if no violations; exits 1 with a remediation hint otherwise

#### Scenario: Remediate R4 violation

- **WHEN** `agent_registry.py` declares a LanceDB target table but is missing `declare_vector_index`
- **THEN** the migration tool reports `R4 FAIL: missing declare_vector_index(column="embedding")`
- **AND** the fix is to add `target_table.declare_vector_index(column="embedding")` immediately after the `lancedb.mount_table_target(LANCE_DB, ...)` call

#### Scenario: R4-exempt marker for non-LanceDB flows

- **WHEN** `apple_photos_geospatial.py` (a GeoParquet-only output) is audited
- **THEN** the migration tool detects the `# R4-exempt: <reason>` marker on a standalone line
- **AND** reports R4 as PASS, citing the exemption reason in the audit log

#### Scenario: CI check

- **WHEN** CI runs the conformance audit (`mise run cocoindex:conformance`) on every push
- **THEN** the build fails if any new flow violates R1, R2, R3, or R4
- **AND** a PR-comment is posted listing the violation table + the failing flow names

### Requirement: 22 priority flows migrated to v1

The system SHALL prioritise 22 flows for v1 conformance. The list includes the 6 LC subjects (mathematics, chemistry, geography, gaeilge, english, computer_science), government_circulars_embedding, 6 leabharlann flows, 3 official-media flows, apple_photos metadata chunks geospatial, agent_registry, codebase_indexing, upstream_api_surface, upstream_blog_monitor, cross_subject_competency_embedding, and ocr_aware_flow.

#### Scenario: Priority migration list is exhaustive

- **WHEN** the user runs `uv run python cianfhoghlaim/dlt/common/cocoindex_v1_migrate.py --priority-list`
- **THEN** the tool prints the 22 flow names sorted alphabetically
- **AND** flows that don't exist as standalone files are flagged with the comment `# may not exist as standalone`

### Requirement: Conformance helper lifecycle

The `cocoindex_v1_migrate.py` tool MUST be CI-friendly (exits 0/1 with no exception leakage), and MUST support `--check-only`, `--apply`, `--priority-list`, and `--help` modes.

#### Scenario: CI exit code contract

- **WHEN** the conformance audit runs in CI with zero violations
- **THEN** it exits 0
- **AND** prints a one-line summary: `cocoindex_v1_conformance: N/N flows pass`

### Requirement: 22-priority flow migration batch completed

Every flow in the 22-flow priority list SHALL satisfy the 4-rule R1+R2+R3+R4 conformance contract, or carry a documented `# R4-exempt: <reason>` marker if it does not write to a LanceDB table with an `embedding` column.

The 14 flows that exist as standalone files (the other 4 of the 22 listed flows live as inner apps inside `leabharlann_embedding.py` and `unified_embedding.py` and are migrated as part of those files) SHALL be the first batch migrated to v1 conformance via the `2026-07-09-cocoindex-v1-remaining-apps-v1` change.

#### Scenario: All 14 existing priority flows pass

- **WHEN** `uv run python cianfhoghlaim/dlt/common/cocoindex_v1_migrate.py --check-only` is run after the migration batch
- **THEN** every flow in the 22-priority list (excluding the 4 non-existent ones) reports `PASS`
- **AND** the audit summary reports `>= 14/14 priority flows pass` (out of the 47 total flows)

#### Scenario: Non-LanceDB flow carries the R4-exempt marker

- **WHEN** `apple_photos_geospatial.py` is audited (a GeoParquet-only flow with no `embedding` column)
- **THEN** it reports R4 PASS via the `# R4-exempt: GeoParquet output, no embedding column` marker
- **AND** the exemption reason is documented in the file's module docstring

### Requirement: v1 conformance check as CI gate

The system SHALL wire the conformance audit as a hard-failure CI gate via the `mise run cocoindex:conformance` task + a new `.github/workflows/cocoindex-conformance.yaml` workflow.

The CI gate SHALL:
- Run on every PR + every push to `main` and `pick-4-biep-v1`
- Invoke `mise run cocoindex:conformance` (which runs `cocoindex_v1_migrate.py --check-only`)
- Exit non-zero on any R1/R2/R3/R4 violation
- Post a PR-comment via `peter-evans/create-or-update-comment` on failure (with the violation table + the failing flow list)
- Upload the per-flow audit report as a build artifact
- The existing `cic:cocoindex:conformance` task (which calls the CocoIndex v1 App) is NOT a replacement for this CI gate; it is the deep materialisation path.

#### Scenario: New R4 violation fails the build

- **WHEN** a contributor adds a new flow under `cianfhoghlaim/cocoindex/` that is missing `declare_vector_index(column="embedding")`
- **THEN** `mise run cocoindex:conformance` exits 1
- **AND** the PR-comment lists the failing flow name + the specific R4 violation
- **AND** the build artifact `cocoindex-v1-conformance-report.txt` is uploaded

#### Scenario: Marker exemption is respected by the CI gate

- **WHEN** a contributor adds a new GeoParquet-only flow with a `# R4-exempt: GeoParquet output` marker
- **THEN** `mise run cocoindex:conformance` exits 0 (the marker is respected)
- **AND** the PR-comment shows the new flow as R4 PASS via the exemption