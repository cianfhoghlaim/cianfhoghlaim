# `british-isles-education-pipeline` spec delta — v4-finalize landing

## ADDED Requirements

### Requirement: 29 absorbed in-progress changes must land via v4-landing-finalize

The system SHALL land all 29 absorbed in-progress openspec changes via the
single `2026-07-07-finalize-v4-landing` mega-change. The 29 absorbed
changes are:

- 9 T1 changes (force-finish): `cianfhoghlaim-educational-mmo-v1`,
  `cianfhoghlaim-website-rewrite`, `monorepo-restructure-v2`,
  `docs-restructuring`,
  `2026-07-06-wire-dlthub-platform-toolkits-and-deployment`,
  `2026-07-04-dev-env-setup-latest-packages-and-wire-25-notebooks`,
  `litellm-minimax-vendor-derisking`, `croilar-portfolio`,
  `2026-07-03-specs-and-session-9-health-report`
- 6 T2 changes (mid-progress continuation):
  `2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs`,
  `2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams`,
  `2026-07-03-infrastructure-foundation`,
  `2026-07-03-gemini-6-corpus-pipeline`,
  `ncca-leaving-cert-syllabi-corpus`,
  `rewrite-cianfhoghlaim-leaving-cert-v2`
- 5 T3 changes (zero-progress flagship work-streams):
  `2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority`,
  `2026-06-30-agent-platform-cluster-hermes-cocoindex`,
  `2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops`,
  `2026-07-02-replace-private-images-and-bring-wave2`,
  `retro-educational-game-asset-pipeline-v1`
- 9 T4 changes (zero-progress infra sub-tasks):
  `2026-07-06-deploy-infisical-bunchloch-local`,
  `2026-07-06-ireland-legal-pipeline`,
  `2026-07-06-notebooks-flatten-refactor-and-wire-bi-ep`,
  `2026-07-02-align-cianfhoghlaim-env-with-stacks`,
  `2026-07-02-bunchloch-stack-bootstrap`,
  `2026-07-02-add-agent-surface-stacks`,
  `2026-07-02-add-marimo-stack`,
  `2026-07-02-add-lancedb-and-logfire-stacks`,
  `2026-07-02-public-about-route`

The surviving in-progress flagship
(`2026-07-06-british-isles-education-pipeline-v1`) is NOT absorbed;
it remains a standalone change.

#### Scenario: openspec list shows ≤2 in-progress after absorption

- **WHEN** the 29 originals have been moved to `openspec/changes/archive/`
- **THEN** `openspec list` shows exactly 2 in-progress changes: the
  mega-change + the surviving BIEP v1
- **AND** every absorbed change has an `ABSORBED.md` note in
  `openspec/changes/archive/<name>/`
- **AND** the mega-change has a verbatim copy of each original's
  `proposal.md` + `tasks.md` under
  `openspec/changes/2026-07-07-finalize-v4-landing/absorbed/<name>/`

### Requirement: Force-finish T1 changes via mega-change Phase 1

The system SHALL force-finish all 9 T1 changes (≥50% done) by absorbing
their remaining tasks into the mega-change's Phase 1 sub-batches and
driving each to 100% completion. The 9 T1 changes cover ~57 remaining
tasks across 9 sub-batches (1.1-1.9).

#### Scenario: All 9 T1 changes reach 100%

- **GIVEN** the 9 T1 absorbed changes (Phase 1 sub-batches 1.1-1.9)
- **WHEN** the mega-change is fully implemented
- **THEN** every T1 absorbed change's `tasks.md` shows 100% `[x]`
- **AND** the mega-change's `tasks.md` Phase 1 has all boxes checked
