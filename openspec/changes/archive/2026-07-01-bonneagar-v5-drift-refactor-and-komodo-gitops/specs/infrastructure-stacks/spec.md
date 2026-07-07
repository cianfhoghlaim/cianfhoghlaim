# Infrastructure Stacks — MODIFIED requirements for v5 (Bonneagar drift refactor)

## MODIFIED Requirements

### Requirement: Locket Sidecar Contract

The system SHALL enforce the canonical Locket sidecar template
across all 88 stacks. The contract is:

- `image: ghcr.io/bpbradley/locket:infisical` (the community fork
  at https://github.com/bpbradley/locket — NOT a project-owned
  image; pinning `@sha256:<actual-digest>` is reserved for a
  future change once bpbradley publishes digest-stable builds)
- `user: "65532:65532"` (nobody:nogroup)
- `security_opt: ["no-new-privileges:true"]`
- `cap_drop: ["ALL"]`
- `read_only: true`
- `tmpfs: [/run/secrets/locket:size=1m,mode=0700,uid=65532,gid=65532]`
- `volumes: [<stack>-locket-secrets:/run/secrets/locket:ro]`
  (the per-stack tmpfs; `cianchoghlaim_locket_secrets` is a
  legacy shared-volume alias that no stack uses)
- `environment.LOCKET_MODE`: one of `watch` / `exec` / `oneshot`
- `environment.LOCKET_SECRETS_FILE: /run/secrets/locket/secrets.env`

The `stack-doctor` gate `good/9-locket-image.sh` SHALL fail the
build if any sidecar uses an image other than
`ghcr.io/bpbradley/locket:infisical`. The fictional
`ghcr.io/cianfhoghlaim/locket:*` image (10+ stale references)
SHALL be rejected.

#### Scenario: A Locket sidecar uses the canonical image

- **GIVEN** `stacks/litellm/sidecar.yaml` declares
  `image: ghcr.io/bpbradley/locket:infisical`
- **WHEN** the stack-doctor runs
- **THEN** the gate SHALL pass with exit code 0
- **AND** the sidecar SHALL mount the per-stack tmpfs
  `litellm-secrets` at `/run/secrets/locket` with mode 0700

#### Scenario: A Locket sidecar uses the fictional cianfhoghlaim/locket image

- **GIVEN** `stacks/foo/sidecar.yaml` declares
  `image: ghcr.io/cianfhoghlaim/locket:latest`
- **WHEN** the stack-doctor runs
- **THEN** the gate SHALL fail with exit code 8 + a clear error
  message ("cianchoghlaim/locket does not exist; use
  bpbradley/locket:infisical — see
  https://github.com/bpbradley/locket")

#### Scenario: A Locket sidecar uses a different tag than `:infisical`

- **GIVEN** `stacks/foo/sidecar.yaml` declares
  `image: ghcr.io/bpbradley/locket:latest` (or `:connect`,
  or any other tag)
- **WHEN** the stack-doctor runs
- **THEN** the gate SHALL fail with exit code 8 + message
  ("only `:infisical` tag is currently allowed; pinning by
  digest is a future change")

### Requirement: Host Tag Mandatory

The system SHALL require every
`bonneagar/komodo/stacks/<name>.toml` to declare exactly
one `host:*` tag from the **2-tag taxonomy**
(`host:bunchloch`, `host:arm1-oci`). The third host
`cax41-hetzner` referenced in earlier drafts is removed
per the v5 cleanup; Hetzner provisioning is exclusively in
`bonneagar/pulumi/`.

Reference stacks (which document a pattern but are not deployed)
MAY have no tag.

The `stack-doctor` SHALL report a stack without a `host:*` tag
as **CRITICAL** (exit code 16).

#### Scenario: A new Komodo stack has no host tag

- **GIVEN** a developer adds
  `bonneagar/komodo/stacks/<new>.toml` with no `tags = [...]`
  field
- **WHEN** the Host Tag gate runs
- **THEN** the gate SHALL fail with exit code 16
- **AND** the developer MUST add
  `tags = ["host:bunchloch"]` (or `host:arm1-oci`)

#### Scenario: A stack references a retired `cax41-hetzner` host

- **GIVEN** a stack or procedure declares
  `host:cax41-hetzner`
- **WHEN** the gate runs
- **THEN** the gate SHALL fail with exit code 16 + message
  ("cax41-hetzner host removed in v5; Hetzner is Pulumi-only")

## ADDED Requirements

### Requirement: IaC Completion

The IaC at `bonneagar/iac/` SHALL be functional end-to-end,
with all 15 commands (`iac:plan`, `iac:deploy`,
`iac:bootstrap`, `iac:teardown`, `iac:health`, and the 10
`iac:sync:*` commands) implementing real logic (not stub
`logWarn` calls). The `iac:sync:secrets` regex SHALL match
the canonical 2-segment Infisical URI format
`infisical://dev-baile/<svc>/<key>` used by all 88 stack
`secrets.env` files. The `iac:bootstrap` command SHALL
implement an 8-phase state machine (Pulumi → Infisical →
Pangolin → Komodo Core → Komodo Periphery → Newt → all
syncs → blueprint import). The `iac/diff.ts` helper SHALL
be wired into `iac:plan` (not orphaned).

#### Scenario: IaC discovers all 88 stacks

- **WHEN** `bun run iac:plan --dry-run` is run
- **THEN** the output SHALL show exactly 88 stacks (matching
  `find stacks/ -maxdepth 1 -name compose.yaml -printf '%h\n' | wc -l`)
- **AND** zero "phantom" key-stacks (the 11 phantom names in
  the pre-v5 `key-stacks.ts` SHALL be replaced with real
  directory names or removed)

#### Scenario: IaC:bootstrap completes all 8 phases

- **WHEN** `bun run iac:bootstrap` is run on a fresh
  `arm1-oci`
- **THEN** all 8 phases SHALL complete without `logWarn`
  stubs
- **AND** `iac:health` SHALL return 0 (all 3 systems
  healthy)

### Requirement: Komodo GitOps Resource-Syncs

The Komodo fleet SHALL be managed via **resource-syncs**
(the canonical Komodo GitOps pattern), not via per-file
`iac:sync:procedures` pushes. The fleet SHALL be split into
3 resource-syncs — `arm1-oci.toml` (control plane),
`bunchloch.toml` (data plane + dev), `cross-cutting.toml`
(the 4 prerequisites) — each registered with Komodo via
`POST /sync` and auto-pulled from the repo on every commit.

The IA C at `iac/` SHALL NOT push procedures + stacks +
monitors + alerts (these are owned by the resource-syncs).
The IaC SHALL keep only the orchestration responsibilities
(see the `bonneagar-komodo-gitops` spec for the 7 retained
sync commands).

#### Scenario: A new procedure is added to a resource-sync

- **GIVEN** a developer adds a new `[[procedure]]` block to
  `komodo/resource-syncs/bunchloch.toml`
- **WHEN** the commit is pushed to `main`
- **THEN** Komodo SHALL auto-pull the updated file within
  60s (via the resource-sync `on_pull: true`)
- **AND** the new procedure SHALL appear in the Komodo UI
- **AND** no manual `iac:deploy` invocation SHALL be required

### Requirement: Ansible Layer Removed

The `bonneagar/ansible/` directory SHALL NOT exist
(removed in v5 per the user's decision). All host-bootstrap
logic SHALL live in `iac/commands/bootstrap.ts` Phase 0
(Docker pre-install + SSH key authorization helper) and
Phase 6 (Newt client deployment). The prior 3 Ansible roles
(`komodo_core`, `newt`, `pangolin_core`) are permanently
removed in favour of `stacks/komodo/`, `stacks/newt/`,
`stacks/pangolin/` (each 6/6 GOLD_STANDARD).

The `deploy-runbooks/ansible.md` SHALL be moved to
`archive/deploy-runbooks/ansible.md` (no longer the
canonical bring-up playbook).

#### Scenario: Bring-up uses IaC, not Ansible

- **WHEN** a fresh `arm1-oci` host is provisioned
- **THEN** `bun run iac:bootstrap` SHALL deploy Pangolin +
  Komodo + Infisical + Locket + Komodo Periphery + Newt
  end-to-end
- **AND** no `ansible-playbook` invocation SHALL be required
- **AND** `bonneagar/ansible/` SHALL not exist on disk

### Requirement: Pangolin Blueprint Per-Stack Migration

The Pangolin private-resource blueprints SHALL live at
`stacks/<name>/pangolin.yaml` (per-stack, the canonical
surface). The `pangolin/` root SHALL contain NO blueprint
files (or only platform-level blueprints that span multiple
stacks). The 4 pre-v5 root blueprint files
(`blueprint.yaml`, `a2a-resources.blueprint.yaml`,
`olm-resources.blueprint.yaml`,
`private-resources.blueprint.yaml`) SHALL be moved to
per-stack locations:
- `stacks/pangolin/blueprint.yaml` (just the 3 self-routes)
- `stacks/agent-os/{pangolin.yaml,blueprint.yaml}` (the 4
  AgentOS A2A routes)
- `stacks/olm-arm1-oci/{pangolin.yaml,blueprint.yaml}` (the
  14 OLM TCP tunnels, with the 2 `ssh-oci`/`ssh-oracle`
  duplicates collapsed to one)
- per-stack `pangolin.yaml` for the 11 services in
  `private-resources.blueprint.yaml` (mailcow gets the 3
  missing routes: webmail, imap, smtp)

#### Scenario: A new stack is added with a private resource

- **GIVEN** the stack has a `pangolin.yaml` with a
  `private-resources:` block
- **WHEN** `bun run iac:sync:resources` is run
- **THEN** the IaC SHALL create the Pangolin private
  resource at `<name>.cianfhoghlaim.ie` via the Integrations
  API
- **AND** no manual Pangolin UI click SHALL be required

### Requirement: Secrets Contract Enforcement

The system MUST rotate + gitignore the 9 plaintext /
regenerated-artifact files at `pangolin/`: `api_key`,
`secrets.env`, `secrets.env.resolved`,
`config/infisical_secret`, `config/db/db.sqlite`,
`config/openapi.yaml`, `config/tinyauth/users`,
`config/secrets/templates/*`, and `config/traefik/rules/*`.
The `stacks/<name>/secrets.env` files SHALL use only the
canonical `infisical://dev-baile/<svc>/<key>` URI format
(not `op://taisce-secrets/...`). The 3 remaining
`op item create` 1Password CLI calls in `PANGOLIN-SETUP.md`
and `pangolin/olm-oracle/secrets.env` SHALL be replaced with
`infisical secrets create`. The vault name `taisce-secrets`
SHALL be replaced with `dev-baile` everywhere.

#### Scenario: A secrets.env file uses the canonical URI

- **WHEN** `git ls-files | xargs grep -l 'op://'` returns 0
  results
- **THEN** the 0-remaining-1Password check SHALL pass
- **AND** `bun run validate-stacks` (the op:// lint) SHALL
  exit 0

### Requirement: Stack Consolidation

The 9 obsolete stack directories SHALL be deleted:
`stacks/lakehouse-oci/` (stale duplicate of `stacks/lakehouse/`),
`stacks/r2/` (4 privileged FUSE containers + competing S3 to
`stacks/garage/`), `stacks/olake/` + `stacks/nimtable/`
(self-deprecated per their `DEPRECATED.md`), and the 5
reference-only dirs without `compose.yaml`
(`stacks/{ci,motherduck,planetscale,pydantic-gateway,tools}/`).

`stacks/browser/` (multi-service compose) and
`stacks/croilar/` (with nested sub-stacks) SHALL be kept
as-is per the v5 user decision — no structural split,
no flattening.

#### Scenario: stack-doctor passes on the v5 inventory

- **WHEN** `bun run validate-stacks` is run
- **THEN** the gate SHALL report exactly 88 stacks, each
  with the canonical 6/6 GOLD_STANDARD files (or the
  documented reduction for stacks that don't need a
  sidecar/blueprint)
- **AND** the gate SHALL fail with a clear error if any of
  the 88 has missing files
- **AND** `stacks/{browser,croilar}/` SHALL remain
  structurally unchanged

### Requirement: Locket Image Canonical

The canonical Locket sidecar image SHALL be
`ghcr.io/bpbradley/locket:infisical` (the community fork at
https://github.com/bpbradley/locket, which implements the
Infisical secrets templating pattern). The fictional
`ghcr.io/cianfhoghlaim/locket` image SHALL NOT be referenced
anywhere in `bonneagar/`. Stacks SHALL pin the `:infisical`
tag; a future change may add `@sha256:<actual-digest>`
pinning once bpbradley/locket publishes digest-stable
builds.

#### Scenario: A new stack adds a locket sidecar

- **WHEN** `stacks/<name>/sidecar.yaml` is created
- **THEN** the `image:` line SHALL be exactly
  `ghcr.io/bpbradley/locket:infisical`
- **AND** the stack-doctor SHALL fail the build if any other
  image is referenced

### Requirement: Komodo Procedures Structural Integrity

The `komodo/procedures/*.toml` files SHALL NOT contain
`[[stack]]` blocks (those belong in `stacks/`). The
`komodo/procedures/*.toml` `RunAction` invocations SHALL
resolve to real Dagger functions (no phantom action names).
The 5 dated backup directories in `komodo/backups/` +
`Stats.gz` SHALL be deleted (Backrest is the canonical
data backup destination). The 9 procedure files that
contain phantom Dagger actions SHALL be deleted. The 29
`[[stack]]`-only procedure files SHALL be deleted. The 3
stale procedure files (referencing non-existent stacks)
SHALL be deleted.

#### Scenario: A procedure file contains a `[[stack]]` block

- **GIVEN** `komodo/procedures/foo.toml` contains
  `[[stack]]` (not `[[procedure]]`)
- **WHEN** the stack-doctor lint runs
- **THEN** the gate SHALL fail with exit code 16 + message
  ("`[[stack]]` blocks belong in `stacks/`")

#### Scenario: A procedure references a ghost host

- **GIVEN** `komodo/procedures/foo.toml` references
  `host:oci-databases` (or `oci-devtools`, `macbook-media`,
  `macbook-analytics`, `cax41`)
- **WHEN** the lint runs
- **THEN** the gate SHALL fail with exit code 16 + message
  ("ghost host reference; only `arm1-oci` + `bunchloch` are
  valid")
