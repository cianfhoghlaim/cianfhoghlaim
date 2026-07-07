# `data-engineering-pipeline-documentation` capability spec — bonneagar-v4-canonical-and-stack-migration delta

The `data-engineering-pipeline-documentation` capability spec
governs the canonical STATUS.md + REFACTORING.md + per-area
READMEs. After the migration, the 4 canonical ops dirs are
updated to reflect the v4 reality.

## ADDED Requirements

### Requirement: 4 canonical ops dirs

The system SHALL document the 4 canonical ops dirs that
house the deployment + ops surface of the cianfhoghlaim
platform:

1. **`bonneagar/`** — the 88-stack GitOps home (Docker
   compose, Pangolin routing, Infisical secrets, Komodo
   orchestration, Backrest backups, IaC TypeScript client)
2. **`cianfhoghlaim/assets/`** — the dagster code-location
   + 3 oideachais Dockerfiles (per the
   `oideachais-stack-polish` change)
3. **`cianfhoghlaim/docs/stacks/`** — the per-stack docs
   (purpose + why-GitOps + cross-references)
4. **`bonneagar/komodo/`** — the Komodo procedure + stack
   + resource-sync TOML files (the orchestration
   definitions)

#### Scenario: STATUS.md references the 4 canonical ops dirs

- **WHEN** a developer reads `cianfhoghlaim/STATUS.md` (or
  the equivalent)
- **THEN** the doc SHALL list the 4 canonical ops dirs with
  a 1-line description of each
- **AND** the doc SHALL NOT reference `infrastructure/stacks/`
  (removed as part of this change)

## MODIFIED Requirements

*(None — the change only ADDs the 4-dir documentation; the
existing STATUS.md + REFACTORING.md patterns are unchanged.)*

## REMOVED Requirements

*(None.)*
