# Spec Delta: no-dead-superseded-legacy-docs

## ADDED Requirements

### Requirement: No superseded `infrastructure/legacy/{ANALYSIS,LOCKET-MODES}.md`

The system SHALL NOT include
`infrastructure/legacy/ANALYSIS.md` or
`infrastructure/legacy/LOCKET-MODES.md`. These 2 documents were
superseded by current skill docs:

  1. `ANALYSIS.md` (15,539 bytes) — superseded by
     `.agents/skills/kcg-pangolin-stack/SKILL.md`
     (2025-12 predecessor-project analysis)
  2. `LOCKET-MODES.md` (8,630 bytes) — superseded by
     `.agents/skills/kcg-locket-sidecar/SKILL.md`
     (v0 predecessor analysis)

The `infrastructure/legacy/README.md` archive index SHALL remain
as the canonical entry point for the 4 archived TypeScript
scripts (`cloudflare-dns.ts`, `pangolin-setup.ts`, `servers.ts`,
`taisce-deploy.ts`) that are still documented in README.md.

#### Scenario: Files removed

- **WHEN** `ls infrastructure/legacy/` is run
- **THEN** the directory SHALL contain only `README.md`
- **AND** `ANALYSIS.md` + `LOCKET-MODES.md` SHALL NOT exist

#### Scenario: README.md remains canonical archive index

- **WHEN** `cat infrastructure/legacy/README.md` is run
- **THEN** the file SHALL document the 4 archived TypeScript scripts and the Komodo migration paths
- **AND** it SHALL remain the canonical archive index (referenced by `infrastructure/komodo/README.md:35`)

#### Scenario: Zero dangling cross-references in skill docs (follow-up)

- **WHEN** the round 11 phase 16 commit lands
- **THEN** the 2 cross-references in skill docs (`.agents/skills/kcg-pangolin-stack/SKILL.md:155` + `.agents/skills/kcg-locket-sidecar/SKILL.md:201`) MAY remain as dangling references until the user cleans them up out-of-band (the `.agents/skills/*.md` files are pre-existing in-flight work, out of scope for this change)

#### Scenario: Spec delta format compliant

- **WHEN** `openspec validate infrastructure-audit-phase-2-delete-superseded-legacy-docs --strict` is run
- **THEN** the change MUST pass strict validation
- **AND** the spec delta MUST land in `openspec/specs/indexing-and-cognition/spec.md` (the canonical home for the indexing + cognition capability)