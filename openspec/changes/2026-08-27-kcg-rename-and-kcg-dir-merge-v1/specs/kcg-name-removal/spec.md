## MODIFIED Requirements

> **Context.** The Cianfhoghlaim monorepo
> (`/Users/cianmacandeisigh/dev/cianfhoghlaim/`) was historically
> named `kings_college_galway` with `kcg` as the shorthand. The
> legacy name STILL leaks across 6 repos (cianfhoghlaim +
> cianchosaint + ciandlithe + ciancheiltis + tuatha +
> gemini_hackathon) + 1 staging directory
> (`/Users/cianmacandeisigh/dev/kings_college_galway/`). The
> phased execution lives in the
> `2026-08-27-kcg-rename-and-kcg-dir-merge-v1` change (Phase 1
> through Phase 4 cover the migration).

### Requirement: Naming conventions (binding substitution table)

The system SHALL enforce the following **binding substitution
table** for all new files, identifiers, paths, slugs, repo
names, Forgejo org slugs, and Komodo resource names across all
6 repos:

| Legacy token | New token | Where |
|:--|:--|:--|
| `kings_college_galway` | `cianfhoghlaim` (long form) | Identifiers, paths, slugs, repo names, Forgejo org slugs, Komodo resource names |
| `kings-college-galway` | `cianfhoghlaim` (long form, hyphenated) | URL slugs, hyphenated identifiers |
| `kcg` (lowercase) | **drop or rewrite in prose**; never as an identifier | Prose, commit messages, informal references |
| `kcg` (uppercase `KCG`) | **rewrite as full word** — `CIANFHOGHLAIM` | Identifiers — e.g. `KCG_COMPONENT` → `CIANFHOGHLAIM_COMPONENT` |
| `KCGu` (legacy host alias) | `arm1-oci` or `bunchloch` (the canonical 2-host topology) | IaC, host references |
| `CIANFHLOGHLAIM` (typo) | `cianfhoghlaim` | All identifiers (the misspelling silently fails Cognee searches) |

The substitution table applies retroactively to all existing files.

#### Scenario: A new file is added to the monorepo

- **GIVEN** the binding substitution table is in force
- **WHEN** an agent or human adds a new file to any of the
  6 repos (cianfhoghlaim + cianchosaint + ciandlithe +
  ciancheiltis + tuatha + gemini_hackathon)
- **THEN** the new file SHALL NOT contain any of the legacy
  tokens (`kings_college_galway`, `kings-college-galway`,
  `kcg` as an identifier, `KCGu`, `CIANFHLOGHLAIM`)
- **AND** `bun run scripts/cianfhoghlaim-brand-lint.ts`
  SHALL pass (0 violations across the default `bonneagar +
  mise.toml + .infisical.env + scripts + openspec + agents +
  notebooks + web/apps + meaisinfhoghlaim + orchestration +
  dlt_sources + .agents/skills + docs + cocoindex_flows +
  tests` scope)
- **AND** the existing 8 exclusions (`.agents/skills_backup/`,
  `stedding/`, `bonneagar/_archive/`, `bonneagar/iac/pulumi/hetzner`,
  `bonneagar/stacks/openclaw/skills-curated`,
  `bonneagar/stacks/GOLD_STANDARD.md`,
  `scripts/cianfhoghlaim-brand-lint.ts`,
  `scripts/cianfhoghlaim-preflight.ts`,
  `scripts/cianfhoghlaim-stack-lint.ts`,
  `scripts/cianfhoghlaim-cli.ts`, `.research/`, `.git/`,
  `node_modules/`, `spaces/data-engineering/`) SHALL be
  preserved

#### Scenario: A sister-repo commit uses the legacy name

- **GIVEN** the binding substitution table is in force and
  the `2026-08-27-kcg-rename-and-kcg-dir-merge-v1` change
  has archived
- **WHEN** a sister-repo PR (cianchosaint / ciandlithe /
  tuatha / gemini_hackathon) is opened that contains any
  of the legacy tokens in tracked files
- **THEN** the PR CI gate SHALL fail with a brand-lint
  error citing the offending file + line + token
- **AND** the PR author SHALL apply the substitution table
  before re-running CI

#### Scenario: The Forgejo org slug is renamed

- **GIVEN** `openspec/project.md` §136 currently references
  `forgejo.cianfhoghlaim.ie/cliste/kings_college_galway` in
  the `bonneagar-komodo-gitops` row
- **WHEN** the Forgejo org is renamed from `cliste/kings_college_galway`
  to `cliste/cianfhoghlaim`
- **THEN** `openspec/project.md` §136 SHALL be updated to
  reference `forgejo.cianfhoghlaim.ie/cliste/cianfhoghlaim`
- **AND** the 3 Komodo resource-syncs at
  `bonneagar/komodo/resource-syncs/{arm1-oci,bunchloch,cross-cutting}.toml`
  SHALL be updated to the new org slug
- **AND** the v5 IaC state machine (`iac:bootstrap` Phase 7)
  SHALL re-register the 3 resource-syncs against the new slug

#### Scenario: A Letta agent ID uses the legacy prefix

- **GIVEN** the 12 Letta agents in `tuatha/` are registered
  with `kcg-*` prefix
- **WHEN** the `tuatha/` Phase 3.4 mirror-rebase ships
- **THEN** all 12 Letta agent IDs SHALL be rotated from
  `kcg-*` to `cianfhoghlaim-*` (the breaking change for
  external Letta consumers)
- **AND** a Forgejo release note SHALL be published at least
  24h before the merge (per the `tuatha` Phase 3.4 protocol)
