## REMOVED Requirements

### Requirement: Phase 1 complete — 21 requirements all functional end-to-end

**Reason**: This spec was a single-requirement retirement marker
pointing at `cianfhoghlaim-leabharlann` (the 21-requirement canonical
spec). All invariants recorded here are already owned by
`cianfhoghlaim-leabharlann`. Retiring this spec removes the
duplication without losing any contract — see the
`2026-09-02-spec-registry-dedup-v1` change's `proposal.md` §Why for the
classification logic (single-requirement retirement markers vs
genuine content overlaps).

**Migration**: All references in skills/AGENTS.md/READMEs SHOULD point
at `cianfhoghlaim-leabharlann` instead. After this change archives,
`openspec list --specs` SHALL NOT include `oideachais-leabharlann`.