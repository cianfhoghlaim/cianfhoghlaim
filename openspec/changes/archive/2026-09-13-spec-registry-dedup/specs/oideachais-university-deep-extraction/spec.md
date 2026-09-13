## REMOVED Requirements

### Requirement: Phase 1 ship — Tertiary 18+ DLT + BAML loop is functionally complete

**Reason**: This spec was a single-requirement retirement marker
pointing at `cianfhoghlaim-university-deep-extraction` (the
8-requirement canonical spec). All Tertiary 18+ DLT + BAML loop
invariants are already owned by `cianfhoghlaim-university-deep-extraction`.
Retiring this spec removes the duplication without losing any
contract.

**Migration**: All references in skills/AGENTS.md/READMEs SHOULD point
at `cianfhoghlaim-university-deep-extraction` instead. After this
change archives, `openspec list --specs` SHALL NOT include
`oideachais-university-deep-extraction`.