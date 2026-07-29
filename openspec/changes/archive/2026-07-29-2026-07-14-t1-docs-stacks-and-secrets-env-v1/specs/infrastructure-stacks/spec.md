## ADDED Requirements

### Requirement: All 88 stacks have a `docs/stacks/<name>.md` cross-reference

The system SHALL provide a per-stack doc file at
`docs/stacks/<name>.md` for every stack in the `bonneagar/stacks/`
fleet (89 active stack dirs after the v6 cleanup; 88 in the canonical
fleet count + 1 staging area). Each per-stack doc SHALL be generated
from the 4 source files in the GOLD_STANDARD contract (`compose.yaml`
+ `README.md` + `blueprint.yaml` + `pangolin.yaml`) and SHALL contain
the 4 hand-written-baseline sections:

1. **Purpose for the Cianfhoghlaim project** — derived from
   `README.md` (preferred) or the `compose.yaml` header comment block.
2. **Why it stays in komodo/pangolin/infisical GitOps** —
   auto-generated boilerplate describing the 6-file GOLD_STANDARD +
   the LOCKET_MODE + the Pangolin route registration.
3. **Cross-references** — links to the stack's `bonneagar/stacks/`
   dir, the IaC registration in `iac/komodo/deploy-stacks.ts`, the
   Pangolin route domain (from `blueprint.yaml`), and any linked
   code/dagster assets.
4. **Tags** — `host:<...>` + `tier:<...>` + `project:cianfhoghlaim`.

The `scripts/generate-stack-docs.ts` Bun script SHALL be the canonical
generator for these docs. It SHALL accept `--apply` (write files)
and `--stack=<name>` (single-stack filter) and `--dry-run` (default).

The `scripts/stack-doctor.sh` CI gate SHALL report zero `missing-doc`
warnings for any stack in `bonneagar/stacks/<name>/` when run with
`DOCS_DIR=docs/stacks` exported (the canonical repo-relative docs
directory in this monorepo).

#### Scenario: A new stack is added to `bonneagar/stacks/<name>/`

- **GIVEN** a developer creates `bonneagar/stacks/<new>/compose.yaml`
  + the other 5 GOLD_STANDARD files
- **WHEN** `bun run scripts/generate-stack-docs.ts --apply` runs
- **THEN** `docs/stacks/<new>.md` SHALL be generated from the 4
  source files in `bonneagar/stacks/<new>/`
- **AND** the doc SHALL contain all 4 hand-written-baseline sections
- **AND** `DOCS_DIR=docs/stacks bun run validate-stacks` SHALL
  report zero `missing-doc` warnings

#### Scenario: The 9 missing per-stack docs are generated

- **GIVEN** the v6 cleanup removed 5 placeholder stack dirs and the
  T1 commit `52b90f054` shipped 89 docs/stacks/*.md files
- **WHEN** `bun run scripts/generate-stack-docs.ts --apply` runs
- **THEN** it SHALL detect 9 missing docs
  (`drop`, `hermes`, `ludusavi`, `moonlight`, `newt`,
  `olm-arm1-oci`, `storybook`, `sunshine`, `wave2`)
- **AND** it SHALL write 9 new files under `docs/stacks/`
- **AND** the total `ls docs/stacks/*.md | wc -l` SHALL reach 98
  (89 active + 9 historical covering pre-v6 stack names that were
  removed: `ci_hf-watchdog`, `lakehouse-oci`, `nimtable`, `olake`,
  `planetscale`, `pydantic-gateway`, `r2`, `tools`)
