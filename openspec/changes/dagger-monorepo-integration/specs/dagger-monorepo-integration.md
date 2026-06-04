# Spec Deltas for `dagger-monorepo-integration`

This change modifies 6 existing capability specs (`dagger-ci`, `dagger-gitops`,
`dagger-forgejo`, `dagger-komodo`, `dagger-cloudflare`, `dagger-blockchain`) and
adds 1 new capability (`dagger-monorepo-integration`).

---

## `specs/dagger-ci/spec.md`

## MODIFIED Requirements

### Requirement: Polyglot CI orchestration
The Dagger module SHALL orquestrate lint, typecheck, unit, integration, and
E2E tests across the Python uv workspace (`oideachais`, `tuatha`,
`tuatha/codeolas`, `tuatha/crypteolas`, `tuatha/apps/crypteolas demo`,
`infrastructure/browser`), the bun workspaces
(`oideachais/web`, `oideachais/mcp/filesystem`, `tuatha/ui`,
`tuatha/apps/crypteolas demo`), and the Rust workspace
(`infrastructure/locket`).

#### Scenario: `dagger call test-all` returns the combined polyglot test summary
- **WHEN** the operator runs `dagger call test-all --source=infrastructure/dagger/..`
- **THEN** the module SHALL run ruff + mypy + pytest on the Python tree,
  eslint + tsc + vitest on the bun tree, and cargo test + clippy on the
  Rust tree, all in parallel via `asyncio.gather`, and SHALL return the
  combined stdout summary.

#### Scenario: failed test stops the pipeline
- **WHEN** any of the polyglot test runners returns a non-zero exit code
- **THEN** the function SHALL raise and the Forgejo Actions `ci.yaml`
  workflow SHALL fail.

### Requirement: Reference paths
The capability spec paths SHALL reference `infrastructure/dagger/src/`
(not the historical `bonneagar/dagger/src/`).

#### Scenario: spec files reference the new module location
- **WHEN** the spec is rendered
- **THEN** every `Ref:` line SHALL point at `infrastructure/dagger/src/...`
  for Python root modules and `infrastructure/dagger/ts_submodules/bonneagar/src/`
  for the TypeScript submodule.

## REMOVED Requirements

### Requirement: Functions reference stale `bonneagar/dagger/src/*.ts` paths
**Reason**: The `bonneagar/dagger/` directory never existed in this monorepo
(documented in `openspec/changes/monorepo-restructure-v2/proposal.md:27`).
The new location is `infrastructure/dagger/`.
**Migration**: Search-and-replace `bonneagar/dagger/src/*.ts` →
`infrastructure/dagger/src/*.py` (or `*.ts` for the TS submodule).

---

## `specs/dagger-gitops/spec.md`

## MODIFIED Requirements

### Requirement: 8-step GitOps pipeline
The module SHALL orquestrate the 8-step Forgejo + Komodo GitOps bring-up
(renovate user → token → secret → webhook → provider → runner → sync →
verify) by delegating to the `bonneagar` TypeScript submodule.

#### Scenario: GitOps bring-up succeeds end-to-end
- **WHEN** the operator runs `dagger call gitops.setup-complete --source=.`
- **THEN** the Python root SHALL call the TS submodule's `setupForgejo`,
  `setupKomodo`, and `verify` functions, passing the Locket-rendered
  `secrets.env` template and the `INFISICAL_TOKEN` as a Dagger `Secret`.

### Requirement: Reference paths
- Same as `dagger-ci`.

## REMOVED Requirements

### Requirement: Functions reference stale `bonneagar/dagger/src/*.ts` paths
**Reason**: Same as `dagger-ci`.
**Migration**: Same as `dagger-ci`.

---

## `specs/dagger-forgejo/spec.md`

## MODIFIED Requirements

### Requirement: Forgejo REST API wrappers
The module SHALL expose `createUser`, `createAccessToken`,
`addCollaborator`, `createWebhook`, `setActionsSecret`, `registerRunner`
functions that wrap the Forgejo REST API. The Python root SHALL delegate
to the `bonneagar` TypeScript submodule for the actual HTTP calls.

#### Scenario: secrets are never echoed
- **WHEN** any function accepts a `forgejoToken` parameter
- **THEN** the function SHALL accept it as a Dagger `Secret` (not a string)
  and SHALL pass it to the container via `withSecretVariable`.

### Requirement: Reference paths
- Same as `dagger-ci`.

## REMOVED Requirements

### Requirement: Functions reference stale `bonneagar/dagger/src/*.ts` paths
**Reason**: Same as `dagger-ci`.
**Migration**: Same as `dagger-ci`.

---

## `specs/dagger-komodo/spec.md`

## MODIFIED Requirements

### Requirement: Komodo SDK wrapper
The module SHALL expose `createGitProvider`, `deployStack`, `startStack`,
`stopStack`, `restartStack`, `runProcedure`, `runSync`, `listServers`,
`getServerStats` functions. The Python root SHALL delegate to the
`bonneagar` TypeScript submodule for the actual HTTP calls.

#### Scenario: Komodo auth via the Locket template
- **WHEN** any Komodo call is made
- **THEN** the function SHALL pass `KOMODO_API_KEY` and `KOMODO_API_SECRET`
  as Dagger `Secret` types, not as plain strings.

### Requirement: Reference paths
- Same as `dagger-ci`.

## REMOVED Requirements

### Requirement: Functions reference stale `bonneagar/dagger/src/*.ts` paths
**Reason**: Same as `dagger-ci`.
**Migration**: Same as `dagger-ci`.

---

## `specs/dagger-cloudflare/spec.md`

## MODIFIED Requirements

### Requirement: Cloudflare Pages and Worker deploys
The module SHALL expose `deployPages`, `deployDocs`, `deployWorker`,
`listProjects`, `listWorkers`, `tailWorker` functions. The Python root
SHALL delegate to the `bonneagar` TypeScript submodule for the actual
Cloudflare API calls.

### Requirement: Reference paths
- Same as `dagger-ci`.

## REMOVED Requirements

### Requirement: Functions reference stale `bonneagar/dagger/src/*.ts` paths
**Reason**: Same as `dagger-ci`.
**Migration**: Same as `dagger-ci`.

---

## `specs/dagger-blockchain/spec.md`

## DEFERRED Requirements

The SpacetimeDB + Solana + Ethereum CI for the `tuatha/crates/` Rust
workspace is **deferred** to a followup OpenSpec change. It requires a
Rust toolchain in the Dagger Python root (currently only Python, bun, and
Komodo), GPU support for the Ethereum test runner, and a verified
`@komodo/sdk` package. Filing as a separate `dagger-blockchain` change
once the Rust toolchain wiring lands.

### Requirement: Reference paths
- The capability is recorded here so the 6-spec table stays accurate; the
  concrete functions (`spacetimedb.*`, `solana.*`, `ethereum.*`,
  `fullPipeline()`) are deferred.

---

## `specs/dagger-monorepo-integration/spec.md` (NEW)

## ADDED Requirements

### Requirement: Module location
The Dagger module SHALL live at `infrastructure/dagger/`. Its entrypoint
SHALL be declared in `pyproject.toml` as
`[project.entry-points."dagger.mod"] main_object = "cianchoghlaim:UnifiedPipeline"`.

#### Scenario: dagger develop loads the module
- **WHEN** the operator runs `cd infrastructure/dagger && dagger develop`
- **THEN** Dagger SHALL discover `UnifiedPipeline` and SHALL generate
  `client.gen.py` against the current Python source.

### Requirement: Top-level orchestrator surface
`UnifiedPipeline` SHALL expose exactly 4 functions: `test_all`,
`build_images`, `deploy`, `rollback`. Each function SHALL compose the 3
pipeline objects (`InfrastructurePipeline`, `WebPipeline`,
`DataPipeline`) via plain constructor composition.

#### Scenario: test_all runs in parallel
- **WHEN** the operator runs `dagger call test-all --source=.`
- **THEN** the function SHALL call `self.infra.test`, `self.web.test`,
  `self.data.test` concurrently via `asyncio.gather` and SHALL return
  the combined stdout.

#### Scenario: build_images targets the canonical registry
- **WHEN** the operator runs
  `dagger call build-images --source=. --registry=ghcr.io/cianfhoghlaim --tag=$GIT_SHA`
- **THEN** the function SHALL build the 3 pipeline images
  (`oideachais-api`, `tuatha-ui`, `dagster-unified`) for `linux/amd64` and
  `linux/arm64`, tag each with the supplied tag, and SHALL publish each
  image to `ghcr.io/cianfhoghlaim/<name>:<tag>`.

#### Scenario: deploy is gated by environment
- **WHEN** the operator runs `dagger call deploy --source=. --environment=production`
- **THEN** the function SHALL refuse unless the production gate is
  explicitly approved (via `--approved=true` or via the Forgejo
  `environment: production` gate).

#### Scenario: rollback reverts to a previous version
- **WHEN** the operator runs `dagger call rollback --environment=production --previous-version=v1.2.3`
- **THEN** the function SHALL call `self.infra.rollback`,
  `self.web.rollback`, `self.data.rollback` with the previous version
  and SHALL return the combined stdout.

### Requirement: Secret model
All secrets SHALL be passed as Dagger `Secret` types, never as plain
strings. The module SHALL NOT inject `INFISICAL_TOKEN`,
`LOCKET_*`, `KOMODO_*`, `PANGOLIN_*`, `GITHUB_TOKEN`, or
`PULUMI_ACCESS_TOKEN` via `withEnvVariable`.

#### Scenario: secrets are masked in stdout
- **WHEN** a function accepts a `Secret` parameter
- **THEN** Dagger SHALL mask the value in any stdout output (Dagger's
  built-in `Secret` type behavior).

### Requirement: Container image policy
Every base image SHALL be pinned to a `sha256:` digest, never `:latest`.
The `Ignore` exclude list SHALL cover `.venv`, `node_modules`,
`__pycache__`, `.git`, `.turbo`, `dist`, `*.lock`, `data/`, `stedding/`,
`.cocoindex_code/`, `dlthub/`, `instagram_output/`, `docs/`.

#### Scenario: pinned base image
- **WHEN** the operator runs `dagger develop`
- **THEN** the module SHALL load without errors even if the host has no
  internet (Dagger caches the pinned images in the `cianchoghlaim-*-cache`
  volume).

### Requirement: Locket secret model
The module SHALL produce `secrets.env` templates that contain
`{{ infisical://dev-baile/<folder>/<key> }}` references. The Locket
sidecar (deployed per `GOLD_STANDARD.md`) SHALL resolve these at
container runtime. Dagger SHALL NEVER directly resolve the secrets.

#### Scenario: Locket resolves the template
- **WHEN** a container starts with the rendered `secrets.env` mounted at
  `/run/secrets/locket/secrets.env`
- **THEN** the Locket sidecar SHALL have replaced the
  `{{ infisical://... }}` references with real values from the
  `dev-baile` Infisical vault.

### Requirement: Forgejo Actions integration
`infrastructure/dagger/.forgejo/workflows/ci.yaml` SHALL install Dagger
via `https://dl.dagger.io/dagger/install.sh`, install mise via the
official Forgejo Action, and run `dagger call test-all --source=../..`.
`infrastructure/dagger/.forgejo/workflows/deploy.yaml` SHALL run
`dagger call deploy --source=../..` gated by `environment: staging`
and `environment: production`.

#### Scenario: PR triggers dagger test-all
- **WHEN** a pull request is opened against `main`
- **THEN** the Forgejo Actions runner SHALL run `dagger call test-all`
  and SHALL fail the PR if the test summary indicates any failures.

#### Scenario: main triggers dagger deploy
- **WHEN** a push to `main` succeeds
- **THEN** the Forgejo Actions runner SHALL run `dagger call deploy
  --environment=staging` first, and only after the staging smoke tests
  pass SHALL it run `--environment=production` (gated by
  `environment: production`).

### Requirement: TypeScript submodule integration
The prior `bonneagar/dagger/` TypeScript implementation SHALL be
consumed as a submodule via `dagger.json` `dependencies` so the prior
work is preserved and the Python root can call into it via
`await Module("bonneagar", source=...)`.

#### Scenario: Python root calls TS submodule
- **WHEN** the Python root calls a TS function (e.g. `komodo-redeploy`)
- **THEN** the cross-module call SHALL succeed and the Python root SHALL
  receive the TS function's return value as a string.

### Requirement: mise.toml integration
The 5 `dagger:*` task aliases in `mise.toml` SHALL point at the new
`infrastructure/dagger/` location. The 4 pre-existing broken aliases
(`dagger:ci`, `dagger:test-python`, `dagger:test-typescript`,
`dagger:deploy-cloudflare`) SHALL be uncommented and rewritten. A new
`dagger:build-images` alias SHALL be added.

#### Scenario: mise task resolves
- **WHEN** the operator runs `mise run dagger:ci`
- **THEN** the alias SHALL `cd infrastructure/dagger` and SHALL run
  `dagger call test-all --source ../..`.

### Requirement: Out of scope
The `dagger-blockchain` capability is OUT OF SCOPE for this change and
is deferred to a separate followup. The prior `Bonneagar.ts` SIWE/x402
blockchain extensions, the SpacetimeDB / Solana / Ethereum CI, and the
GPU support for Dagster AI / LiteLLM are all deferred.

#### Scenario: deferral is documented
- **WHEN** the spec is read
- **THEN** it SHALL clearly state that `dagger-blockchain` is deferred
  to a followup OpenSpec change.
