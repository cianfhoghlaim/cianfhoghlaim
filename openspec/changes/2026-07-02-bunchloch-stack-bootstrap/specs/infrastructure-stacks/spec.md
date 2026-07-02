# Infrastructure Stacks — Bunchloch Cold-Boot Delta

> This file is the change-side delta for
> `2026-07-02-bunchloch-stack-bootstrap`. It applies on top of
> the canonical `infrastructure-stacks` spec at
> `../../../../specs/infrastructure-stacks/spec.md`.

## ADDED Requirements

### Requirement: Bunchloch cold-boot procedure

The system SHALL provide a documented procedure (the
`bunchloch-bootstrap.md` runbook at
`bonneagar/deploy-runbooks/bunchloch-bootstrap.md`) that an
agent can execute to bring up the 19 canonical bunchloch
workload-host stacks from cold, without relying on Komodo
TOMLs (which contain pre-v5-drift path drift that prevents
`bun run iac:bootstrap` from succeeding).

The procedure SHALL organise the 19 stacks into 3 dependency-
ordered waves:

- **Wave 1 (Foundation):** `lakehouse`, `falkordb`, `dragonfly`
- **Wave 2 (Self-contained + OCR):** `litellm`, `llama-swap`,
  `mlflow`, `cognee`, `unstract`, `langfuse`, `graphiti`,
  `dagster`, `dots-ocr`, `olmocr`, `paddleocr`, `docling-serve`
- **Wave 3 (UI + streaming):** `invokeai`, `convex`, `risingwave`

The 19 stacks SHALL be brought up via
`./scripts/stack.sh <name> up -d` (the dev-mode direct CLI that
reads `bonneagar/stacks/<name>/compose.yaml` off disk and
bypasses Komodo). The procedure SHALL NOT require Locket,
Infisical, or any live secret round-trip.

#### Scenario: Wave 1 foundation healthy
- **WHEN** an agent runs `./scripts/stack.sh lakehouse up -d`
  followed by `./scripts/stack.sh falkordb up -d` and then
  `./scripts/stack.sh dragonfly up -d`
- **THEN** Garage S3 SHALL respond at `:3900` AND Postgres SHALL
  accept connections at `:5433` AND Lakekeeper SHALL respond at
  `:8181` AND Lance Namespace SHALL respond at `:8182` AND
  ClickHouse SHALL respond at `:8123` AND Dragonfly SHALL answer
  `PING` at `:6379` AND FalkorDB SHALL answer `PING` at `:6380`
- **AND** the agent SHALL record the bring-up time in
  `bonneagar/stacks/HEALTH_REPORT.md`

#### Scenario: Wave 2 self-contained services healthy
- **WHEN** an agent runs the 12 Wave-2 stack bring-up commands
  in the order specified by the runbook
- **THEN** `litellm` SHALL respond at `:4000` (Liveness endpoint)
  AND `mlflow` SHALL respond at `:5000` (`/api/2.0/mlflow/ping`)
  AND `cognee` SHALL respond at `:8100` (`/api/health`) AND
  `unstract` SHALL respond at `:8002` (`/api/v1/health`) AND
  `langfuse` SHALL respond at `:3001` (`/api/public/health`) AND
  `graphiti` SHALL connect to the Wave-1 FalkorDB backend AND
  `dagster` SHALL load its code location once litellm and
  lakehouse are healthy (verified by the "Dagster webserver is
  ready" log message) AND the 4 OCR stacks (dots-ocr, olmocr,
  paddleocr, docling-serve) SHALL each expose a working `/health`
  endpoint on their declared ports (8001, 8003, 8000, 5001)

#### Scenario: Wave 3 UI + streaming healthy
- **WHEN** an agent runs `./scripts/stack.sh invokeai up -d`
  followed by `./scripts/stack.sh convex up -d` and then
  `./scripts/stack.sh risingwave up -d`
- **THEN** `invokeai` SHALL respond at `:9090` (its primary
  OpenAI-compatible API port) AND `convex` backend SHALL
  respond at container port `3210` (no host port mapped per
  current compose; verified via
  `./scripts/stack.sh convex exec backend curl :3210/version`)
  AND `risingwave` SHALL accept PostgreSQL wire-protocol
  connections at `:4566` (verified via `psql -h localhost -p
  4566 -U root -d dev -c '\dt'`)

#### Scenario: Browser stack deferred to follow-up
- **WHEN** an agent attempts to bring up the `browser` stack
  via `./scripts/stack.sh browser up -d`
- **THEN** the procedure SHALL refuse (the `browser` stack is
  missing 5 of 6 GOLD_STANDARD files: `secrets.env`, `sidecar.yaml`,
  `blueprint.yaml`, `README.md`, plus the canonical
  `compose.yaml` exists but is 387 lines covering 21 services
  with mixed Python project structure)
- **AND** the agent SHALL file a separate openspec change
  (`2026-07-XX-bring-browser-stack-to-gold-standard`) to
  remediate the stack before it can be brought up

#### Scenario: Health report regenerated
- **WHEN** Wave 1 + Wave 2 + Wave 3 complete successfully
- **THEN** `bonneagar/stacks/HEALTH_REPORT.md` SHALL be
  refreshed with the 2026-07-02 live container inventory
  (replacing or augmenting the 2026-06-15 static snapshot)
- **AND** `bun run validate-stacks` SHALL continue to pass
  with no new hard failures introduced (existing WARNINGs for
  the 5 unpinned `:latest` images are accepted in this change
  and addressed by the sibling change
  `2026-07-02-add-lancedb-and-logfire-stacks`)
- **AND** `mise run lint:skills` SHALL continue to pass (123/123)

### Requirement: Stack GitOps registration deferred until v5-drift lands

The system SHALL NOT register the 19 stacks in Komodo (via
`bun run iac:bootstrap` or any equivalent IaC sync) until the
in-flight `2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops`
change merges. That change is healing the TOML `file_paths`
entries that currently reference `infrastructure/stacks/<x>/`
(a path that no longer exists after the 2026-06-29
`bonneagar-v4-canonical-and-stack-migration` change), plus 17
other drift items.

#### Scenario: Komodo attempt blocked pre-v5-drift
- **WHEN** an agent runs `bun run iac:bootstrap` before the
  v5-drift change is merged
- **THEN** `iac:plan` SHALL fail with a clear "path drift"
  diagnostic pointing at the TOML `file_paths` entries that do
  not resolve
- **AND** the agent SHALL fall back to `./scripts/stack.sh
  <name> up -d` for the duration of the cold-boot

#### Scenario: Komodo post-v5-drift
- **WHEN** the v5-drift change has merged AND an agent runs
  `bun run iac:bootstrap`
- **THEN** all 19 stacks SHALL register under the `host:bunchloch`
  tag with their `bonneagar/stacks/<x>/` compose paths
- **AND** the `bunchloch-bootstrap.md` runbook SHALL be marked
  DEPRECATED in favour of the IaC GitOps path
- **AND** the runbook SHALL be moved to
  `archive/deploy-runbooks/` with a pointer to the canonical
  GitOps procedure

### Requirement: Three remaining follow-up changes sequenced

The system SHALL deploy the 4 deferred sets of stacks via 3
sequenced sibling changes:

| Change | Stacks | Wave |
|:--|:--|:--|
| `2026-07-02-add-lancedb-and-logfire-stacks` | `lancedb` (Wave 1), `logfire` (Wave 2b), plus 5 image pins (`cognee`, `dots-ocr`, `olmocr`, `paddleocr`, `docling-serve`) | 1, 2b |
| `2026-07-02-add-marimo-stack` | `marimo` | 3 |
| `2026-07-02-add-agent-surface-stacks` | `hermes`, `openclaw`, `openchamber` | 4 |

The 4 deferred features (`mailcow-dockerized`, `mlx-omni`,
`letta`, `browser`) SHALL each be addressed by a separate
future openspec change (not in this sequence).

#### Scenario: Change 2 brings up lancedb + logfire
- **WHEN** Change 2 is archived
- **THEN** `lancedb` SHALL be in Wave 1 (brought up alongside
  `lakehouse`) AND `logfire` SHALL be in Wave 2b (brought up
  after `langfuse` and `mlflow` are healthy) AND all 5
  previously-unpinned `:latest` images SHALL be pinned to their
  resolved semver tags in their compose.yaml files
- **AND** `bun run validate-stacks` SHALL report zero
  `:latest` WARNINGs for the 5 affected stacks

#### Scenario: Change 3 brings up marimo
- **WHEN** Change 3 is archived
- **THEN** `marimo` SHALL be in Wave 3 (brought up after
  `invokeai` and `convex` are healthy) AND the 11 marimo
  notebooks in `cianfhoghlaim/notebooks/` SHALL be navigable
  from the marimo server UI

#### Scenario: Change 4 brings up the 3 agent surfaces
- **WHEN** Change 4 is archived
- **THEN** `hermes`, `openclaw`, and `openchamber` SHALL be in
  Wave 4 (brought up after all data + observability stacks are
  healthy) AND each of the 3 stacks SHALL route its LLM
  traffic through the canonical `litellm` gateway (no direct
  provider keys in any of the 3 stacks' `secrets.env` files)