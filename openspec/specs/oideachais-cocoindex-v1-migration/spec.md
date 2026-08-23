# oideachais-cocoindex-v1-migration Specification

## Purpose
The oideachais CocoIndex v1 migration surface covers the 7 v1 CocoIndex Apps (6 LC subjects + government_circulars) across the Cianfhoghlaim monorepo. It defines 1 invariant: the canonical migration pattern from v0.x (the LocalFS-only lineage) to v1.0.14+ (the 17-connector surface with the 4-rule conformance contract).

## Requirements
### Requirement: Pre-v7 stub retired — see cianfhoghlaim-cocoindex-v1-migration

The system SHALL recognize that `oideachais-cocoindex-v1-migration` is a pre-v7 retirement marker. The canonical capability spec is `cianfhoghlaim-cocoindex-v1-migration` (8 ADDED Requirements, post-v7 flattened naming).

Per the 2026-08-22-openspec-audit-and-merge-v1 audit + the 2026-08-22-retire-pre-v7-oideachais-stubs-v1 retirement change.

#### Scenario: Agent looks up the canonical CocoIndex v1 migration spec

- **WHEN** an agent reads `openspec/list --specs` to find the CocoIndex v1 migration spec
- **THEN** the agent SHOULD load `cianfhoghlaim-cocoindex-v1-migration` (the canonical)
- **AND** the pre-v7 name `oideachais-cocoindex-v1-migration` is preserved as a retirement marker

