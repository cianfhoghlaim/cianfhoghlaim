# oideachais-leabharlann Specification

## Purpose
The oideachais leabharlann surface covers the 4 dlt sources + 3 v1 CocoIndex Apps for the leabharlann/ corpus (the 4th leabharlann sub-corpus). It defines 3 invariants: the canonical leabharlann/ directory path, the per-subject BAML extraction templates, and the per-corpus CocoIndex v1 App structure.

## Requirements
### Requirement: Pre-v7 stub retired — see cianfhoghlaim-leabharlann

The system SHALL recognize that `oideachais-leabharlann` is a pre-v7 retirement marker. The canonical capability spec is `cianfhoghlaim-leabharlann` (21 ADDED Requirements, post-v7 flattened naming).

Per the 2026-08-22-openspec-audit-and-merge-v1 audit + the 2026-08-22-retire-pre-v7-oideachais-stubs-v1 retirement change.

#### Scenario: Agent looks up the canonical Leabharlann corpus spec

- **WHEN** an agent reads `openspec/list --specs` to find the Leabharlann corpus spec
- **THEN** the agent SHOULD load `cianfhoghlaim-leabharlann` (the canonical)
- **AND** the pre-v7 name `oideachais-leabharlann` is preserved as a retirement marker

