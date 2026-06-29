# `infrastructure-stacks` capability spec — bonneagar-v4-canonical-and-stack-migration delta

The `infrastructure-stacks` capability spec governs the Docker
Compose stacks + IaC TypeScript client + the 6-file
GOLD_STANDARD pattern. The previous v4 canonical location was
`infrastructure/stacks/` (a path that did not exist on disk
until today's parallel sub-agent created 5 files there).

This delta corrects the v4 reality: the canonical stack
location is `bonneagar/stacks/` (the 88-stack GitOps home that
has been the de facto canonical location since v0), and the
`infrastructure/` dir is removed.

## ADDED Requirements

### Requirement: Canonical stack location is `bonneagar/stacks/`

The system SHALL maintain every Docker Compose stack at
`bonneagar/stacks/<name>/` with the 6-file GOLD_STANDARD
pattern. The `infrastructure/stacks/` path SHALL NOT exist
(removed as part of this change).

#### Scenario: All 88 stacks live at `bonneagar/stacks/`

- **WHEN** a developer lists `bonneagar/stacks/`
- **THEN** the directory SHALL contain at least 88 stack
  subdirectories (the v0 88 stacks + 3 new ones:
  `ci/hf-watchdog/`, `browser/`, `llama-swap/`)
- **AND** every stack subdirectory SHALL contain the 6
  GOLD_STANDARD files: `compose.yaml`, `sidecar.yaml`,
  `secrets.env`, `pangolin.yaml`, `blueprint.yaml`,
  `.env.example`
- **AND** the `infrastructure/` dir at the repo root SHALL NOT
  exist

#### Scenario: 35 duplicate stacks are removed from `cianfhoghlaim/stacks/`

- **WHEN** this change is deployed
- **THEN** the 35 duplicate stack dirs that existed in BOTH
  `cianfhoghlaim/stacks/` and `bonneagar/stacks/` SHALL be
  deleted from `cianfhoghlaim/stacks/`
- **AND** the canonical twins in `bonneagar/stacks/` SHALL
  remain unchanged

#### Scenario: 2 cianfhoghlaim-only stacks are migrated

- **WHEN** this change is deployed
- **THEN** the 2 stack dirs that existed only in
  `cianfhoghlaim/stacks/` (`browser/`, `llama-swap/`) SHALL
  be moved to `bonneagar/stacks/browser/` and
  `bonneagar/stacks/llama-swap/`
- **AND** the `browser/` and `llama-swap/` dirs in
  `cianfhoghlaim/stacks/` SHALL be deleted

#### Scenario: 4 non-stack files are moved to `cianfhoghlaim/assets/`

- **WHEN** this change is deployed
- **THEN** the 4 non-stack files that existed in
  `cianfhoghlaim/stacks/` (`oideachais_dagster.yaml`,
  `oideachais_Dockerfile`, `oideachais_Dockerfile.adk`,
  `oideachais_Dockerfile.dagster`) SHALL be moved to
  `cianfhoghlaim/assets/_oideachais_dagster_defs/`
- **AND** the 4 entries SHALL be deleted from
  `cianfhoghlaim/stacks/`

### Requirement: `ci/hf-watchdog/` stack from `2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority`

The system SHALL migrate the `hf-watchdog` stack from
`infrastructure/stacks/ci/hf-watchdog/` (a v4-canonical
attempt that was never IaC-managed) to
`bonneagar/stacks/ci/hf-watchdog/`.

#### Scenario: ops files move to `bonneagar/stacks/ci/hf-watchdog/`

- **WHEN** this change is deployed
- **THEN** the 3 ops files (`blueprint.yaml`, `compose.yaml`,
  `Dockerfile`) SHALL be moved from
  `infrastructure/stacks/ci/hf-watchdog/` to
  `bonneagar/stacks/ci/hf-watchdog/`
- **AND** the 1 code file (`watchdog.py`) SHALL be moved to
  `cianfhoghlaim/ci/hf_watchdog.py`
- **AND** 4 missing GOLD_STANDARD files SHALL be added
  (`sidecar.yaml`, `secrets.env`, `pangolin.yaml`,
  `.env.example`)

#### Scenario: Dockerfile uses multi-stage build

- **WHEN** the `hf-watchdog` container is built
- **THEN** the Dockerfile SHALL use a multi-stage build that
  `COPY --from=ghcr.io/cianfhoghlaim/cianfhoghlaim:dev /app/ci/hf_watchdog.py /app/`
- **AND** the watchdog.py SHALL NOT be bundled inside the
  ops dir; it SHALL be loaded from the cianfhoghlaim image

#### Scenario: hf-watchdog registered in the IaC

- **WHEN** `bun run iac:deploy-stacks` runs
- **THEN** the `hf-watchdog-bunchloch` stack entry SHALL be
  registered in Komodo with tags `host:bunchloch` + `tier:ci` +
  `project:cianfhoghlaim` + `v4:consolidated`
- **AND** the stack SHALL be deployable via
  `komodo run procedure deploy-hf-watchdog-bunchloch`

### Requirement: IaC `package.json` at the root of `bonneagar/`

The system SHALL hoist the IaC TypeScript client's manifest
from `bonneagar/iac/komodo/package.json` to
`bonneagar/package.json` at the root.

#### Scenario: `bonneagar/package.json` exists at the root

- **WHEN** a developer lists `bonneagar/`
- **THEN** the directory SHALL contain `package.json` (the
  IaC's manifest) + `tsconfig.json` + `bun.lock` at the root
- **AND** the 4 alias scripts SHALL be present:
  - `iac:deploy-stacks` → `bun run iac/komodo/deploy-stacks.ts`
  - `iac:create-resources` → `bun run iac/komodo/create-resources.ts`
  - `iac:read-state` → `bun run iac/komodo/read-state.ts`
  - `iac:bootstrap` → combined deploy-stacks +
    create-resources + read-state

#### Scenario: `iac:bootstrap` is the 1-command entry point

- **WHEN** the user runs `bun run iac:bootstrap` (or
  `mise run bonneagar:iac:bootstrap`)
- **THEN** the script SHALL sequentially run the 3 IaC
  scripts (deploy-stacks, create-resources, read-state)
- **AND** the IaC SHALL bring the Komodo state +
  Pangolin private resources + Infisical secrets into
  consistency with the 88 stacks at `bonneagar/stacks/`

### Requirement: The 5-group model (informational only)

The system SHALL document the 88 stacks in 5 logical groups
(informational only, not a deploy-time constraint):

- **infrastructure** (Pangolin, Pocket ID, TinyAuth, Traefik,
  Infisical, Locket, Komodo Core + Periphery, Backrest) —
  9 stacks, all on `arm1-oci`
- **data-engineering** (Dagster, Lakehouse, Marimo, CocoIndex,
  Cognify, Litellm, Langfuse, Llama-swap) — 12 stacks, all
  on `bunchloch`
- **agent-platform** (Agno AgentOS, Google ADK, OpenClaw,
  OpenChamber, Cognee, Graphiti, Letta) — 7 stacks, all on
  `bunchloch`
- **language-model** (LiteLLM, llama-swap, MLX-Omni, Logfire,
  Langfuse, mlflow) — 6 stacks, all on `bunchloch`
- **user-facing-web** (oideachais-web, oideachais-api,
  oideachais-dagster, oideachais-agent-os,
  oideachais-adk-agents, openclaw) — 6 stacks, all on
  `bunchloch`
- **ci** (hf-watchdog) — 1 stack, on `bunchloch`

#### Scenario: AGENTS.md documents the 5-group model

- **WHEN** a developer reads `bonneagar/AGENTS.md`
- **THEN** the doc SHALL contain a "5-group model" table
  listing the 5 groups + the 88 stacks in each
- **AND** the doc SHALL document the cianfhoghlaim-project
  tag convention (`project:cianfhoghlaim` for the
  40+ cianfhoghlaim-relevant stacks; no tag for the
  personal/utility stacks)

## MODIFIED Requirements

*(None — the change only ADDs the new v4-canonical home
+ 5-group model + package.json hoist; the 6-file
GOLD_STANDARD pattern is unchanged.)*

## REMOVED Requirements

*(None — the change only ADDS new Requirements; the
existing 6-file GOLD_STANDARD pattern is preserved.)*
