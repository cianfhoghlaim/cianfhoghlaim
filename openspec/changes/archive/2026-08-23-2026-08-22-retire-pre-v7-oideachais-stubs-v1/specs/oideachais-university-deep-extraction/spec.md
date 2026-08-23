# Spec Delta: oideachais-university-deep-extraction

## REMOVED Requirements

### Requirement: Phase 1 ship — Tertiary 18+ DLT + BAML loop is functionally complete

**Reason**: Pre-v7 stub. The canonical capability spec is `cianfhoghlaim-university-deep-extraction` (8 ADDED Requirements, post-v7 flattened naming). The Tertiary 18+ DLT + BAML loop is documented in the v7-flattened spec.
**Migration**: Load `cianfhoghlaim-university-deep-extraction` for the canonical capability.

## ADDED Requirements

### Requirement: Pre-v7 stub retired — see cianfhoghlaim-university-deep-extraction

The system SHALL recognize that `oideachais-university-deep-extraction` is a pre-v7 retirement marker. The canonical capability spec is `cianfhoghlaim-university-deep-extraction` (8 ADDED Requirements, post-v7 flattened naming).

Per the 2026-08-22-openspec-audit-and-merge-v1 audit + the 2026-08-22-retire-pre-v7-oideachais-stubs-v1 retirement change.

#### Scenario: Agent looks up the canonical university deep extraction spec

- **WHEN** an agent reads `openspec/list --specs` to find the university deep extraction spec
- **THEN** the agent SHOULD load `cianfhoghlaim-university-deep-extraction` (the canonical)
- **AND** the pre-v7 name `oideachais-university-deep-extraction` is preserved as a retirement marker