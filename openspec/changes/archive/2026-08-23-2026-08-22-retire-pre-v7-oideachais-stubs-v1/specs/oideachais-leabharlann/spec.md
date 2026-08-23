# Spec Delta: oideachais-leabharlann

## REMOVED Requirements

### Requirement: Phase 1 complete — 21 requirements all functional end-to-end

**Reason**: Pre-v7 stub. The canonical capability spec is `cianfhoghlaim-leabharlann` (21 ADDED Requirements, post-v7 flattened naming). The Phase 1 work has been re-scoped under the v7-flattened spec.
**Migration**: Load `cianfhoghlaim-leabharlann` for the canonical capability.

## ADDED Requirements

### Requirement: Pre-v7 stub retired — see cianfhoghlaim-leabharlann

The system SHALL recognize that `oideachais-leabharlann` is a pre-v7 retirement marker. The canonical capability spec is `cianfhoghlaim-leabharlann` (21 ADDED Requirements, post-v7 flattened naming).

Per the 2026-08-22-openspec-audit-and-merge-v1 audit + the 2026-08-22-retire-pre-v7-oideachais-stubs-v1 retirement change.

#### Scenario: Agent looks up the canonical Leabharlann corpus spec

- **WHEN** an agent reads `openspec/list --specs` to find the Leabharlann corpus spec
- **THEN** the agent SHOULD load `cianfhoghlaim-leabharlann` (the canonical)
- **AND** the pre-v7 name `oideachais-leabharlann` is preserved as a retirement marker