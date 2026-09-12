## REMOVED Requirements

### Requirement: All 47 CocoIndex flows (22 priority + 25 non-priority) pass R1–R4 conformance

**Reason**: This spec was a single-requirement retirement marker
pointing at `cianfhoghlaim-cocoindex-v1-migration` (the 8-requirement
canonical spec). The conformance contract R1–R4 for all 47 flows is
already owned by `cianfhoghlaim-cocoindex-v1-migration`. Retiring this
spec removes the duplication without losing any contract.

**Migration**: All references in skills/AGENTS.md/READMEs SHOULD point
at `cianfhoghlaim-cocoindex-v1-migration` instead. After this change
archives, `openspec list --specs` SHALL NOT include
`oideachais-cocoindex-v1-migration`.