# Spec Delta: oideachais-cocoindex-v1-migration

## REMOVED Requirements

### Requirement: All 47 CocoIndex flows (22 priority + 25 non-priority) pass R1–R4 conformance

**Reason**: Pre-v7 stub. The canonical capability spec is `cianfhoghlaim-cocoindex-v1-migration` (8 ADDED Requirements, post-v7 flattened naming). The R1–R4 conformance contract is enforced in the v7-flattened spec.
**Migration**: Load `cianfhoghlaim-cocoindex-v1-migration` for the canonical capability.

## ADDED Requirements

### Requirement: Pre-v7 stub retired — see cianfhoghlaim-cocoindex-v1-migration

The system SHALL recognize that `oideachais-cocoindex-v1-migration` is a pre-v7 retirement marker. The canonical capability spec is `cianfhoghlaim-cocoindex-v1-migration` (8 ADDED Requirements, post-v7 flattened naming).

Per the 2026-08-22-openspec-audit-and-merge-v1 audit + the 2026-08-22-retire-pre-v7-oideachais-stubs-v1 retirement change.

#### Scenario: Agent looks up the canonical CocoIndex v1 migration spec

- **WHEN** an agent reads `openspec/list --specs` to find the CocoIndex v1 migration spec
- **THEN** the agent SHOULD load `cianfhoghlaim-cocoindex-v1-migration` (the canonical)
- **AND** the pre-v7 name `oideachais-cocoindex-v1-migration` is preserved as a retirement marker