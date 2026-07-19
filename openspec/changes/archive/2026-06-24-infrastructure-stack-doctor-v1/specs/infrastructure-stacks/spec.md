# Spec Delta: infrastructure-stacks

## MODIFIED Requirements

### Requirement: Stack Standardization

The system SHALL enforce a **6-file GOLD_STANDARD** for every
`infrastructure/stacks/<name>/` directory. The 6 files are:

1. `compose.yaml` — the Docker Compose stack definition
2. `sidecar.yaml` — the Locket secret-injection sidecar (uses
   `user: 65532:65532` + `no-new-privileges:true` + `cap_drop: [ALL]` +
   `read_only: true` + `tmpfs: [/run/secrets/locket:size=1m,mode=0700]`)
3. `secrets.env` — the list of `infisical://dev-baile/<svc>/<key>` URIs
4. `pangolin.yaml` — the 6-label private resource declaration
5. `blueprint.yaml` — the rendered Pangolin state
6. `.env.example` — the documentation of every env var (every
   stack that declares a custom env var MUST have `.env.example`)

The `bun run stack-doctor` CI gate SHALL fail the build if any
of the 6 files is missing.

The `sidecar.yaml` SHALL declare one of 3 `LOCKET_MODE` values:
`watch` (long-running services, the default), `exec` (batch jobs),
or `oneshot` (CI/CD pipelines).

The `pangolin.yaml` SHALL follow the 6-label shape (`name`,
`mode`, `full-domain`, `destination-port`, `protocol`, `roles[0]`)
documented in `.agents/skills/kcg-pangolin-stack/SKILL.md`.

#### Scenario: A new stack is added to `infrastructure/stacks/<name>/`

- **GIVEN** the stack dir has been created with 1 or 2 of the 6
  GOLD_STANDARD files
- **WHEN** `bun run stack-doctor` runs on the PR
- **THEN** the gate SHALL fail with exit code 1 (missing file)
- **AND** the developer MUST add the remaining files before the
  PR merges

#### Scenario: A Locket sidecar uses the canonical security baseline

- **GIVEN** `infrastructure/stacks/oideachais-dagster/sidecar.yaml`
- **WHEN** the stack is deployed
- **THEN** the Locket container SHALL have `user: 65532:65532` +
  `no-new-privileges: true` + `cap_drop: [ALL]` + `read_only: true`
  + `tmpfs: [/run/secrets/locket:size=1m,mode=0700]`
- **AND** the `cianfhoghlaim_locket_secrets` external tmpfs volume
  SHALL be mounted

## ADDED Requirements

### Requirement: Stack-Doctor CI Gate

The system SHALL run `bun run stack-doctor` on every PR via a
GitHub Action. The 4 gates are:

1. **File gate** (exit code 1) — every
   `infrastructure/stacks/<name>/compose.yaml` has the other 5
   GOLD_STANDARD files
2. **Container gate** (exit code 2) — every `container_name:` is
   in the live inventory OR explicitly documented as
   `stacked-only: true` in a `kcg-meta.yaml` file
3. **Secret gate** (exit code 4) — every `secrets.env` URI
   resolves in the Infisical vault (via `bun run scripts/init-vault.ts`)
4. **Pangolin gate** (exit code 8) — every `pangolin.yaml`
   parses against the official 6-label schema

The script's exit code SHALL be the bitwise-OR of the 4 gate
failures. The CI workflow SHALL report which gates failed in
the GitHub Actions summary.

The system SHALL also enforce the 3 host tags
(`host:bunchloch`, `host:arm1-oci`, `host:cax41-hetzner`) on every
Komodo stack definition; reference stacks MAY have no tag.

#### Scenario: A PR adds a new compose file but is missing the other 5 files

- **GIVEN** a developer adds `infrastructure/stacks/<new>/compose.yaml`
  with a new service
- **WHEN** the PR's GitHub Action runs `bun run stack-doctor`
- **THEN** the File gate (exit code 1) SHALL fail
- **AND** the Action SHALL post a comment on the PR listing the
  5 missing files
- **AND** the PR SHALL be blocked from merging

#### Scenario: A secret URI in `secrets.env` doesn't resolve in the vault

- **GIVEN** a developer adds
  `INFI_FOO=infisical://dev-baile/sruth/oideachais/foo` to
  `infrastructure/stacks/<stack>/secrets.env`
- **AND** the `dev-baile` Infisical environment does NOT have a
  secret at path `sruth/oideachais/foo`
- **WHEN** the Secret gate runs
- **THEN** the gate SHALL fail with exit code 4
- **AND** the developer MUST either create the secret in
  Infisical OR remove the URI from `secrets.env`

### Requirement: Image Pinning Policy

The system SHALL pin every `image:` line in every
`infrastructure/stacks/<name>/compose.yaml` to a specific
`<major>.<minor>.<patch>` semver tag. The tag `:latest` is
**forbidden** for upstream images. Local-build images with
`pull_policy: never` are exempt and MUST include an inline YAML
comment explaining the deviation.

The `stack-doctor` SHALL report any unpinned image as
**WARNING** (exit code 1, soft failure) so that pre-existing
stacks can be migrated incrementally.

#### Scenario: A PR introduces an unpinned image

- **GIVEN** a developer adds
  `image: ghcr.io/cianfhoghlaim/oideachais-dagster:latest` to
  a compose file
- **WHEN** the Image Pinning Policy gate runs
- **THEN** the gate SHALL report a WARNING
- **AND** the developer SHOULD pin to a semver tag like
  `ghcr.io/cianfhoghlaim/oideachais-dagster:1.2.3`

### Requirement: Locket Sidecar Contract

The system SHALL enforce the canonical Locket sidecar template
across all 86+ stacks. The contract is:

- `image: ghcr.io/cianfhoghlaim/locket:<sha-pinned-tag>`
- `user: "65532:65532"` (nobody:nogroup)
- `security_opt: ["no-new-privileges:true"]`
- `cap_drop: ["ALL"]`
- `read_only: true`
- `tmpfs: [/run/secrets/locket:size=1m,mode=0700,uid=65532,gid=65532]`
- `volumes: [cianfhoghlaim_locket_secrets:/run/secrets/locket:ro]`
- `environment.LOCKET_MODE`: one of `watch` / `exec` / `oneshot`
- `environment.LOCKET_SECRETS_FILE: /run/secrets/locket/secrets.env`

The `cianfhoghlaim_locket_secrets` external tmpfs volume is
defined in `infrastructure/locket/compose.yaml` and is
**shared** across all 86+ stacks.

#### Scenario: A Locket sidecar uses the wrong user

- **GIVEN** a developer's `sidecar.yaml` declares `user: root`
- **WHEN** the Locket Sidecar Contract gate runs
- **THEN** the gate SHALL fail with exit code 8
- **AND** the developer MUST change to `user: "65532:65532"`

### Requirement: Host Tag Mandatory

The system SHALL require every
`infrastructure/komodo/stacks/<name>.toml` to declare exactly
one `host:*` tag from the 3-tag taxonomy
(`host:bunchloch`, `host:arm1-oci`, `host:cax41-hetzner`).
Reference stacks (which document a pattern but are not deployed)
MAY have no tag.

The `stack-doctor` SHALL report a stack without a `host:*` tag
as **CRITICAL** (exit code 16).

#### Scenario: A new Komodo stack has no host tag

- **GIVEN** a developer adds
  `infrastructure/komodo/stacks/<new>.toml` with no `tags = [...]`
  field
- **WHEN** the Host Tag gate runs
- **THEN** the gate SHALL fail with exit code 16
- **AND** the developer MUST add `tags = ["host:<one-of-3>"]`

### Requirement: Pangolin 6-Label Pattern

The system SHALL enforce the 6-label pattern in every
`pangolin.yaml` (per `.agents/skills/kcg-pangolin-stack/SKILL.md`):

1. `pangolin.private-resources.<name>.name` — unique slug
2. `pangolin.private-resources.<name>.mode` — `http` / `tcp` / `udp`
3. `pangolin.private-resources.<name>.full-domain` — the FQDN
4. `pangolin.private-resources.<name>.destination-port` — the container port
5. `pangolin.private-resources.<name>.protocol` — `http` / `https`
6. `pangolin.private-resources.<name>.roles[0]` — the Traefik role

The 4 common Traefik middlewares are `tinyauth@file`,
`secure-headers@file`, `rate-limit-api@file`, `rate-limit-auth@file`.

#### Scenario: A pangolin.yaml is malformed

- **GIVEN** a developer adds a `pangolin.yaml` with the wrong
  field name (`destination_port` with an underscore)
- **WHEN** the Pangolin gate runs
- **THEN** the gate SHALL fail with exit code 8
- **AND** the developer MUST rename to `destination-port`
  (with a hyphen)

## REMOVED Requirements

(None.)
