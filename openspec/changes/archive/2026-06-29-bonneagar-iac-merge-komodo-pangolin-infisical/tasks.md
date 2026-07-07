# Tasks — `2026-06-29-bonneagar-iac-merge-komodo-pangolin-infisical`

## Phase 0 — Pre-flight verification (done in plan mode)

- [x] **0.1** — Map the 5 v0 IaC scripts at `bonnegar/iac/komodo/` (config, komodo-rpc, deploy-stacks, create-resources, read-state). Done in plan mode.
- [x] **0.2** — Confirm the 3 bash IaC scripts at `bonnegar/scripts/` (setup-pangolin-komodo.sh, sync-blueprints.sh, create-olm-clients.sh). Done.
- [x] **0.3** — Confirm the 91 stacks at `bonnegar/stacks/` and the 5-group model (30 unique key stacks). Done.
- [x] **0.4** — Confirm the Enterprise Edition licence (`PANGOLIN_LICENCE=PER-D09BF259-...`). Done.
- [x] **0.5** — Confirm the Integrations API base path (`${PANGOLIN_URL}/v1` for per-resource CRUD; `/api/v1/integration/blueprint` for the bulk import). Done.

## Phase 1 — The 3 typed clients (the foundation)

- [ ] **1.1** — **Create `bonnegar/iac/clients/komodo-client.ts`** — re-export the v0 `KomodoRpc` class + add 9 new methods: `listProcedures`, `upsertProcedure`, `listResourceSyncs` (already in v0), `upsertResourceSync` (already in v0), `listMonitors`, `upsertMonitor`, `listAlerts`, `upsertAlert`, `listVariables`, `upsertVariable`, `listSchedules`, `upsertSchedule`, `listActionRecipients`, `upsertActionRecipient`, `listRepos`, `upsertRepo`, `listBuilders`, `upsertBuilder`. Each uses `fetch()` directly (no `komodo_client` npm package, per the v0 localStorage bug).
- [ ] **1.2** — **Create `bonnegar/iac/clients/pangolin-client.ts`** — re-export the v0 `PangolinRpc` class + add 8 new methods: `listOrganizations`, `createOrganization`, `createSite`, `createOlmClient`, `listOlmClients`, `uploadBlueprint`, `listBlueprints`, `deleteBlueprint`. Each uses `${PANGOLIN_URL}/v1/...` (or `/api/v1/integration/...` for the bulk endpoints).
- [ ] **1.3** — **Create `bonnegar/iac/clients/infisical-client.ts`** — the NEW Infisical client using `@infisical/sdk`. Methods: `login`, `listProjects`, `createEnvironment`, `createFolder`, `listSecrets`, `createSecret`, `updateSecret`, `deleteSecret`, `createMachineIdentity`, `listMachineIdentities`.
- [ ] **1.4** — **Create `bonnegar/iac/models/{komodo,pangolin,infisical}.ts`** — the typed models (one per client). Includes the 9 Komodo types (Server, Stack, Procedure, ResourceSync, Monitor, Alert, Variable, Schedule, ActionRecipient), the 5 Pangolin types (Site, Resource, Target, Blueprint, OlmClient), the 5 Infisical types (Project, Environment, Folder, Secret, MachineIdentity).

## Phase 2 — The 4 source-discoverers (auto-derive state from the 91 stacks)

- [ ] **2.1** — **`sources/discover-stacks.ts`** — walks `bonnegar/stacks/*/compose.yaml` and produces typed `Stack[]` (one per stack). Each stack has the 6-file GOLD_STANDARD check.
- [ ] **2.2** — **`sources/discover-resources.ts`** — walks `bonnegar/stacks/*/pangolin.yaml` and produces typed `PangolinResource[]`. Filters out stacks whose `pangolin.yaml` is empty/commented-out.
- [ ] **2.3** — **`sources/discover-secrets.ts`** — walks `bonnegar/stacks/*/secrets.env` and produces typed `InfisicalSecret[]`. Each `infisical://dev-baile/<stack>/<key>` ref is parsed into a `path` + `key` + `value` triplet.
- [ ] **2.4** — **`sources/key-stacks.ts`** — the curated 30-stack list (5-group model filter). Returns the names of the 30 "key" stacks that the IaC deploys.

## Phase 3 — The 11 sync commands (the heart of the IaC)

- [ ] **3.1** — **`commands/sync-secrets.ts`** — reads every `discover-secrets.ts` ref + calls `infisical.createSecret` (or `updateSecret` if exists). Idempotent.
- [ ] **3.2** — **`commands/sync-resources.ts`** — for every `discover-resources.ts` resource: check if exists, if not `createSiteResource`. If the 3 manually-created override resources (komodo, calcom, infisical) are detected, DELETE then CREATE (fixes blocker #2).
- [ ] **3.3** — **`commands/sync-procedures.ts`** — reads every `bonnegar/komodo/procedures/*.toml` + calls `komodo.upsertProcedure`.
- [ ] **3.4** — **`commands/sync-resource-syncs.ts`** — reads every `bonnegar/komodo/resource-syncs/*.toml` + calls `komodo.upsertResourceSync`.
- [ ] **3.5** — **`commands/sync-monitors.ts`** — for every Pangolin-routed stack: create a Komodo `Monitor` that does an HTTP health check at `https://<name>.cianfhoghlaim.ie/health` every 60s. (opt-in)
- [ ] **3.6** — **`commands/sync-alerts.ts`** — create 4 Komodo `Alerts` (failed deploy, failed backup, host down, monitor failing) that post to a Discord webhook. (opt-in)
- [ ] **3.7** — **`commands/sync-variables.ts`** — create Komodo `Variables` for the 12 cross-stack env vars (KOMODO_PASSWORD, PANGOLIN_API_KEY, etc.).
- [ ] **3.8** — **`commands/sync-schedules.ts`** — create Komodo `Schedules` for the 5 cron jobs (daily backup, hourly CDC, nightly secret rotation, weekly stack-promote audit, monthly disaster-recovery drill). (opt-in)
- [ ] **3.9** — **`commands/sync-action-recipients.ts`** — create 3 Komodo `ActionRecipients` (Discord, email, Slack). (opt-in)
- [ ] **3.10** — **`commands/sync-olm.ts`** — sync the Pangolin OLM clients (the 2 manually-created OLM resources get the same DELETE-then-CREATE treatment).
- [ ] **3.11** — **`commands/teardown.ts`** — the reverse of deploy. With `--force`. Idempotent.

## Phase 4 — The 4 top-level commands (plan / deploy / bootstrap / health)

- [ ] **4.1** — **`commands/plan.ts`** — calls all 11 sync commands in `--dry-run` mode and prints a diff. Includes the `diff.ts` engine. Reads actual state from all 3 systems.
- [ ] **4.2** — **`commands/deploy.ts`** — the end-to-end deploy: `sync-secrets` → `sync-procedures` → `sync-resource-syncs` → `sync-variables` → `sync-resources` → `sync-monitors` → `sync-alerts` → `sync-schedules` → `sync-action-recipients` → `sync-olm`. Each step is idempotent + prints a summary.
- [ ] **4.3** — **`commands/bootstrap.ts`** — the 1-command full bootstrap: Pulumi → Infisical → Pangolin → Komodo → Newt → all syncs. Supports `--with-blueprint-import` flag (uses the bulk endpoint for the initial Pangolin resource creation).
- [ ] **4.4** — **`commands/health.ts`** — health check all 3 systems: Komodo `GET /health`, Pangolin `GET /api/health`, Infisical `GET /api/status`. Returns 0/1 exit code.

## Phase 5 — CLI + auth + diff engine (the supporting infra)

- [ ] **5.1** — **`config.ts`** — the single env loader. Reads `KOMODO_URL`, `KOMODO_JWT`, `PANGOLIN_URL`, `PANGOLIN_API_KEY`, `PANGOLIN_ORG_ID`, `INFISICAL_URL`, `INFISICAL_TOKEN`, `LOCKET_TOKEN`. Supports `mise` directory hooks.
- [ ] **5.2** — **`auth.ts`** — the 3 auth flows. (a) `komodoLogin()` uses `KOMODO_PASSWORD` if set, else auto-mints via `komodo-recover.sh`. (b) `pangolinLogin()` mints a new OIDC token via Pocket ID if the existing one is 401. (c) `infisicalLogin()` mints a new machine identity if needed.
- [ ] **5.3** — **`diff.ts`** — generic deep-equal diff engine (for `plan.ts`).
- [ ] **5.4** — **`cli.ts`** — the `bun run iac <cmd>` entry point. Uses Bun's built-in `Bun.argv` parser. Supports `--dry-run`, `--force`, `--stack=<name>`, `--with-blueprint-import`, `--verbose`.
- [ ] **5.5** — **`README.md`** — the new IaC README.

## Phase 6 — Update the root `bonneagar/package.json` + migrate the v0 scripts

- [ ] **6.1** — **Update `bonnegar/package.json`** to add the 15 new alias scripts: `iac:plan`, `iac:deploy`, `iac:bootstrap`, `iac:teardown`, `iac:health`, `iac:sync:secrets`, `iac:sync:resources`, `iac:sync:procedures`, `iac:sync:resource-syncs`, `iac:sync:monitors`, `iac:sync:alerts`, `iac:sync:variables`, `iac:sync:schedules`, `iac:sync:action-recipients`, `iac:sync:olm`. Keep the v0 4 as backward-compat aliases.
- [ ] **6.2** — **Add `@infisical/sdk` to `bonnegar/package.json`** dependencies.
- [ ] **6.3** — **Migrate the 5 v0 `iac/komodo/*.ts` scripts to the new `iac/` structure.** The new files supersede the old ones.
- [ ] **6.4** — **Delete the old `bonnegar/iac/komodo/` dir** (the 5 v0 TS files + the nested `package.json` + `tsconfig.json` + `bun.lock`).
- [ ] **6.5** — **Run `bun install`** in the `bonnegar/` root to fetch `@infisical/sdk`.

## Phase 7 — Update openspec + validate

- [ ] **7.1** — **Update the `infrastructure-stacks` spec** at `openspec/specs/infrastructure-stacks/spec.md` — +1 Requirement: the IaC at `bonnegar/iac/` is the single source of truth.
- [ ] **7.2** — **Update the `indexing-and-cognition` spec** at `openspec/specs/indexing-and-cognition/spec.md` — cross-reference the new IaC.
- [ ] **7.3** — **Create the new `bonneagar-iac-merge` spec** at `openspec/specs/bonneagar-iac-merge/spec.md`.
- [ ] **7.4** — **Update `openspec/project.md`** with the new capability row.
- [ ] **7.5** — **Run `openspec validate 2026-06-29-bonneagar-iac-merge-komodo-pangolin-infisical --strict`** — all deltas pass.
- [ ] **7.6** — **Run `bun run iac:health`** — all 3 systems respond.
- [ ] **7.7** — **Run `bun run iac:plan --dry-run`** — no unexpected diffs.
- [ ] **7.8** — **Run `bun run iac:bootstrap`** (the 1-command full bootstrap) — Infisical → Pangolin → Komodo all synced.
