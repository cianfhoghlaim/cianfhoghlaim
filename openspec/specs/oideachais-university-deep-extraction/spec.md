# oideachais-university-deep-extraction Specification

## Purpose
The oideachais university deep-extraction surface covers the per-university website deep extraction (BAML + DLT + Dagster + CocoIndex v1 + marimo + Cognee cross-archive) — the reusable template for any British Isles university. It defines 12 invariants: the canonical university_pipeline pattern (UniversityPipelineBase), the per-university BAML extraction templates, the Dagster assets (documents_ingested + syllabus_extracted + cognified), the per-source src/ + dst/ convention, and the Cognee cross-archive edges.

## Requirements
### Requirement: Pre-v7 stub retired — see cianfhoghlaim-university-deep-extraction

The system SHALL recognize that `oideachais-university-deep-extraction` is a pre-v7 retirement marker. The canonical capability spec is `cianfhoghlaim-university-deep-extraction` (8 ADDED Requirements, post-v7 flattened naming).

Per the 2026-08-22-openspec-audit-and-merge-v1 audit + the 2026-08-22-retire-pre-v7-oideachais-stubs-v1 retirement change.

#### Scenario: Agent looks up the canonical university deep extraction spec

- **WHEN** an agent reads `openspec/list --specs` to find the university deep extraction spec
- **THEN** the agent SHOULD load `cianfhoghlaim-university-deep-extraction` (the canonical)
- **AND** the pre-v7 name `oideachais-university-deep-extraction` is preserved as a retirement marker

