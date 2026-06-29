## ADDED Requirements

### Requirement: Heritage corpus restoration provenance

The leabharlann heritage corpus is the personal-archive half of the `culture` domain. Its canonical home on disk is `cian_mac_an_déisigh_uí_liatháin/identity/lineage/` (and the read-only sub-paths `references/clippings/`, `lineage/`, `deacy/`, `teaching/`, `vetting/`, `politics/`, `disability/`, `achievement/`). When the heritage corpus is restored after a v4-consolidation drop, the restoration MUST follow the provenance contract below.

#### Scenario: When the heritage corpus is restored after a v4 consolidation

- **WHEN** the heritage corpus at `cian_mac_an_déisigh_uí_liatháin/` has been dropped from `main` (i.e. is not present in HEAD) and an agent needs to restore it
- **THEN** the agent MUST restore the corpus from the `q3-2026-oideachais-consolidation` branch (the canonical pre-v4 branch as of 2026-06-28) via `git checkout q3-2026-oideachais-consolidation -- "cian_mac_an_déisigh_uí_liatháin/"`
- **AND** the agent MUST NOT merge the `q3-2026-oideachais-consolidation` branch into `main` (the v4-consolidation history is intentionally separate; a merge would drag in ~200 unrelated commits from the browser / dagster / OCR / agent-fleet work)
- **AND** the agent MUST open an openspec change of the form `openspec/changes/YYYY-MM-DD-restore-heritage-corpus-and-expand-readme/` with a `tracking_issues/unread-pdfs.md` documenting any path that the previous agent had flagged as missing
- **AND** the openspec change MUST add a MODIFIED Requirement to `openspec/specs/cross-domain-registry/spec.md` asserting the drift-detector invariant (clipping SHA-256 === fixture SHA-256) holds for the restored corpus
