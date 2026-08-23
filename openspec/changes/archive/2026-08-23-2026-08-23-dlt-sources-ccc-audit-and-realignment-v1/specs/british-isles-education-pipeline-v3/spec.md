# Spec Delta: british-isles-education-pipeline-v3

## ADDED Requirements

### Requirement: dlt_sources/ tree MUST have a per-subtree AGENTS.md

The system SHALL ensure that each of the 15 sub-trees of `dlt_sources/` has a 1-line `AGENTS.md` file that names the subtree + the tangent/phase/audience it serves. The canonical content is the per-subtree line documented in `openspec/changes/2026-08-23-dlt-sources-ccc-audit-and-realignment-v1/proposal.md` (Decision 1).

The audit identified 14 of 15 sub-trees without AGENTS.md (only `dlt_sources/common/` had a README.md). The gap-fill is a mechanical 1-line addition per subtree.

Per the 2026-08-23-dlt-sources-ccc-audit-and-realignment-v1 audit.

#### Scenario: New agent looks up the dlt_sources subtrees

- **WHEN** a new agent runs `ls dlt_sources/` and sees the 15 sub-trees
- **THEN** each subtree SHALL have an `AGENTS.md` file
- **AND** the 1-line content SHALL name the subtree + the tangent/phase/audience it serves

### Requirement: university_of_galway_deep source MUST be wired into the BIEP v3 5-phase pattern

The system SHALL wire the existing `dlt_sources/british_isles/ireland/education/university_of_galway_deep.py` source into the BIEP v3 5-phase pattern (Ingestion → Materials → Model Lifecycle → Asset Generation → Agent Operations). The source is currently orphaned (no Dagster asset, no CocoIndex v1 App, no MotherDuck table).

The wiring requires:
1. A Dagster asset in `orchestration/defs/1_ingestion/uog_deep/` (L1 ingestion)
2. A CocoIndex v1 App at `cocoindex_flows/biep_parity/uog_deep_embedding.py` (L2 materials)
3. A MotherDuck / LanceDB table at `cianfhoghlaim.bronze.ireland_university.uog_deep` (L3 model lifecycle)

Per the 2026-08-23-dlt-sources-ccc-audit-and-realignment-v1 audit (Decision 2).

#### Scenario: Dagster materializes the UoG deep source

- **WHEN** the operator runs `dagster asset materialize --select uog_deep_ingested`
- **THEN** the 5-phase pattern fires (Ingestion → Materials → Model Lifecycle → Asset Generation → Agent Operations)
- **AND** the asset check `uog_deep_ragas_check` passes (RAGAS score >= 0.70)
- **AND** the `uog_deep_lance_chunks_check` passes (chunk count >= 1_000)