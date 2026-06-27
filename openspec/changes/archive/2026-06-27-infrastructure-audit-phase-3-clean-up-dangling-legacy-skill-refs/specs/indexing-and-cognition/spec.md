# Spec Delta: extend `no-dead-superseded-legacy-docs` with the dangling-cross-references scenario

## MODIFIED Requirements

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

After the files are removed, there SHALL be NO dangling
cross-references to the deleted files in any active surface
of the repo (skill docs, infrastructure scripts, agent fleet
prompts, etc.).

#### Scenario: Files removed

- **WHEN** `ls infrastructure/legacy/` is run
- **THEN** the directory SHALL contain only `README.md`
- **AND** `ANALYSIS.md` + `LOCKET-MODES.md` SHALL NOT exist

#### Scenario: No dangling cross-references

- **WHEN** `grep -rn "legacy/ANALYSIS\|legacy/LOCKET-MODES" .` is run (excluding `.git`/`.venv`/`__pycache__`)
- **THEN** the only matches SHALL be inside `openspec/changes/archive/2026-06-27-infrastructure-audit-phase-2-delete-superseded-legacy-docs/` (historical record) and inside `openspec/specs/indexing-and-cognition/spec.md` (canonical spec)
- **AND** there SHALL be NO active references in `.agents/skills/*.md`, `infrastructure/*`, `spaces/*`, `sruth/*`, or any other active surface
- **AND** the 2 dangling cross-references in `.agents/skills/kcg-pangolin-stack/SKILL.md:155` + `.agents/skills/kcg-locket-sidecar/SKILL.md:201` SHALL be removed

#### Scenario: README.md remains canonical archive index

- **WHEN** `cat infrastructure/legacy/README.md` is run
- **THEN** the file SHALL document the 4 archived TypeScript scripts and the Komodo migration paths
- **AND** it SHALL remain the canonical archive index (referenced by `infrastructure/komodo/README.md:35`)

#### Scenario: Spec delta format compliant

- **WHEN** `openspec validate infrastructure-audit-phase-{2,3}-delete-superseded-legacy-docs --strict` is run
- **THEN** both changes MUST pass strict validation
- **AND** the spec delta MUST land in `openspec/specs/indexing-and-cognition/spec.md` (the canonical home for the indexing + cognition capability)