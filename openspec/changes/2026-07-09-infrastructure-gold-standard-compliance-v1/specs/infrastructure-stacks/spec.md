# Spec Delta: infrastructure-stacks

This change modifies the `infrastructure-stacks` capability
(`openspec/specs/infrastructure-stacks/spec.md`) by adding 3
new requirements and modifying 1 existing requirement. The
full modified spec lives at
`openspec/specs/infrastructure-stacks/spec.md`.

## ADDED Requirements

### Requirement: GOLD_STANDARD compliance at 90%

The `bonneagar/stacks/` fleet SHALL reach ≥90% GOLD_STANDARD
compliance for the 6-file pattern (the 6-file pattern is
defined in `Requirement: Stack Standardization` of
`openspec/specs/infrastructure-stacks/spec.md`).

Concretely, at any time the monorepo's HEAD SHALL have:

- **≥60/87 stacks** with `.env.example`
- **≥60/87 stacks** with `pangolin.yaml` (web-facing stacks MUST have one; non-web-facing stacks MAY omit)
- **87/87 stacks** with `compose.yaml`
- **87/87 stacks** with `secrets.env` (or an explicit no-secrets-required marker in `.env.example`)
- **87/87 stacks** with `blueprint.yaml`
- **87/87 stacks** with `sidecar.yaml` (if Locket is required)

The `bun run stack-doctor --strict` exit code SHALL be 0 if all
6 coverage thresholds are met.

The two generators at the repo root
(`scripts/generate-stack-env-example.ts` +
`scripts/generate-stack-pangolin-yaml.ts`) SHALL be the
canonical tools to close the gap when a new stack is added.

#### Scenario: New stack passes the 90% threshold

- **WHEN** a developer adds `bonneagar/stacks/<new>/` with
  `compose.yaml` + `blueprint.yaml` + `sidecar.yaml` + `secrets.env`
- **AND** runs `bun run scripts/generate-stack-env-example.ts --apply`
- **AND** runs `bun run scripts/generate-stack-pangolin-yaml.ts --apply`
- **THEN** the new stack has `.env.example` + `pangolin.yaml`
- **AND** the GOLD_STANDARD compliance percentage is unchanged (still ≥90%)

#### Scenario: A 5-prune drops the fleet below the 90% threshold

- **WHEN** 5 placeholder stacks are deleted (`rm -rf`)
- **AND** the new count is 87
- **THEN** `bun run stack-doctor --strict` SHALL still pass (the
  threshold is a ratio, not an absolute count)

### Requirement: iac:bootstrap is the canonical entry point

The IaC TypeScript client at `bonneagar/iac/cli.ts` SHALL be
reachable from the repo root via 3 scripts in
`package.json:scripts`:

- `iac:bootstrap` → `bun run --cwd bonneagar iac:bootstrap`
  (full Pulumi → Infisical → Pangolin → Komodo → Newt → all syncs)
- `iac:plan` → `bun run --cwd bonneagar iac:plan`
  (diff IaC-declared vs actual state)
- `iac:deploy` → `bun run --cwd bonneagar iac:deploy`
  (deploy the 30 + 57 = 87 stacks end-to-end)

The `iac/` directory SHALL have its own `package.json` (sub-package)
+ `tsconfig.json` so it can be split into a standalone repo at
`github.com/cianfhoghlaim/bonneagar` without changing the call sites.

#### Scenario: A new operator runs iac:bootstrap from an empty repo

- **GIVEN** the operator has just cloned the monorepo
- **AND** the `mise.toml` toolchain is installed (`bun`, `uv`,
  `pulumi`, `infisical`, `dagger`)
- **WHEN** the operator runs `bun run iac:bootstrap`
- **THEN** the IaC provisions a fresh `arm1-oci` + `bunchloch`
  + `cax41-hetzner` from empty in one command
- **AND** the IaC emits a final report listing which systems
  were brought up + which resources were created

#### Scenario: A developer wants to dry-run the IaC

- **WHEN** the developer runs `bun run iac:plan --dry-run`
- **THEN** the IaC SHALL print the diff between declared and
  actual state without mutating anything
- **AND** exit code SHALL be 0 (no changes) or 1 (would-have-changed)

### Requirement: stack-doctor as CI gate

The `bun run stack-doctor` script SHALL run on every PR via a
GitHub Action. The CI gate SHALL be **strict** (fail on
warnings, not just criticals) and SHALL emit a markdown summary
for the GitHub Actions comment.

The 6 gates (replacing the v4 4-gate pattern):

1. **File gate** (exit code 1) — every `bonneagar/stacks/<name>/`
   has `compose.yaml` + the 5 other GOLD_STANDARD files
2. **Image-pinning gate** (exit code 2) — every `image:` is a
   `<major>.<minor>.<patch>` tag (no `:latest`)
3. **Secret-ref gate** (exit code 4) — every `secrets.env` URI
   resolves in the Infisical vault
4. **Pangolin-schema gate** (exit code 8) — every `pangolin.yaml`
   parses against the 6-label schema
5. **Env-example gate** (exit code 16) — every stack that declares
   a custom env var has `.env.example`
6. **Komodo-mirror gate** (exit code 32) — every stack has a
   matching `komodo/stacks/<name>-<host>.toml`

The script's exit code SHALL be the bitwise-OR of the 6 gate
failures. The CI workflow SHALL report which gates failed in
the GitHub Actions summary.

#### Scenario: A PR adds a new compose file but is missing the other 5 files

- **GIVEN** a developer adds `bonneagar/stacks/<new>/compose.yaml`
- **WHEN** the PR's GitHub Action runs `bun run stack-doctor --strict`
- **THEN** the File gate (exit code 1) SHALL fail
- **AND** the Action SHALL post a comment on the PR listing the
  5 missing files
- **AND** the PR SHALL be blocked from merging

#### Scenario: A stack uses `:latest` image tag

- **GIVEN** a developer adds
  `image: ghcr.io/foo/bar:latest` to `bonneagar/stacks/<s>/compose.yaml`
- **WHEN** the PR's GitHub Action runs `bun run stack-doctor --strict`
- **THEN** the Image-pinning gate (exit code 2) SHALL fail
- **AND** the developer MUST pin the image to a `<major>.<minor>.<patch>` tag

#### Scenario: A stack has no matching komodo/stacks/*.toml

- **GIVEN** a developer adds `bonneagar/stacks/<new>/` with all 6
  GOLD_STANDARD files
- **AND** `bonneagar/komodo/stacks/<new>-<host>.toml` is NOT generated
- **WHEN** the PR's GitHub Action runs `bun run stack-doctor --strict`
- **THEN** the Komodo-mirror gate (exit code 32) SHALL fail
- **AND** the developer MUST run
  `bun run scripts/generate-komodo-stacks.ts --apply`

## MODIFIED Requirements

### Requirement: Selfhosted stack inventory

The system SHALL expose the 87 selfhosted stacks at
`bonneagar/stacks/<name>/`. The 33 user-selected stacks
remain canonical at `bonneagar/stacks/` (the v4 split to
`cianfhoghlaim/stacks/` was reverted 2026-06-29). Each stack
SHALL have a `komodo/stacks/<name>-<host>.toml` mirror that
the Komodo GitOps sync can ingest.

The canonical inventory file is `bonneagar/stacks/INDEX.md`
(generated by `bun run stack-doctor --emit-md`). The
`AGENTS.md` count + the `README.md` count + the
`HEALTH_REPORT.md` count SHALL all match the `INDEX.md`
directory count (replaces the v5 88 / 86 / 94 drift).

#### Scenario: An agent wants to find a stack's komodo definition

- **GIVEN** the agent knows the stack name (`oideachais`)
- **WHEN** the agent runs `ls bonneagar/komodo/stacks/oideachais*.toml`
- **THEN** the agent SHALL find exactly one TOML file
  (`oideachais-bunchloch.toml` or `oideachais-arm1-oci.toml` per host)

#### Scenario: The fleet grows to 88 stacks

- **GIVEN** the fleet has 87 stacks and a new stack is added
- **WHEN** the developer runs `bun run stack-doctor --emit-md`
- **THEN** `bonneagar/stacks/INDEX.md` SHALL be regenerated to
  list 88 stacks
- **AND** `AGENTS.md` SHALL still reference `INDEX.md` as the
  single source of truth

#### Scenario: Validation rejects a missing komodo/stacks/*.toml

- **WHEN** `bun run validate-stacks` runs
- **THEN** every `bonneagar/stacks/<name>/` SHALL have a
  matching `bonneagar/komodo/stacks/<name>-<host>.toml`
- **AND** stacks without a matching TOML SHALL fail the
  Komodo-mirror gate (exit code 32)