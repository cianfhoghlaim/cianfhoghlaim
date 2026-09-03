# Tasks: 2026-08-15-bonneagar-infra-remediation-v2

> **Phase 0 (BLOCKER CHECKS)** — these gates MUST pass before any implementation work begins:
> 1. The repo-root `.env` has `PANGOLIN_API_KEY` set (operator-provided in the 2026-08-15 session)
> 2. The repo-root `.env` has `POCKETID_PANGOLIN_CLIENT_ID` set (`2dd6dfe6-47e0-456f-9736-9afed63134fc`)
> 3. The repo-root `.env` has `INFISICAL_PROJECT_ID` set
> 4. `mise run lint:drift-docs` passes before commit

## Phase A: OpenSpec change artifacts (the source of truth)

- [x] Create `openspec/changes/2026-08-15-bonneagar-infra-remediation-v2/`
- [x] Create `proposal.md` (this change)
- [x] Create `tasks.md` (this file)
- [x] Create `cross-repo-sync.md`
- [x] Create `specs/infrastructure-stacks/spec.md` delta (2 ADDED Requirements)
- [x] Create `specs/bonneagar-iac-merge/spec.md` delta (3 ADDED Requirements)

## Phase B: IaC TypeScript implementation

- [x] NEW `bonneagar/iac/load-env.ts` — the env loader (the missing piece)
- [x] Extend `iac/cli.ts` to side-effect import `load-env.ts` + register 2 NEW commands + update help text
- [x] Extend `iac/models/pangolin.ts` with the `PangolinClientCert` interface
- [x] Extend `iac/clients/pangolin-client.ts` with 4 NEW methods (`listClients`/`getClient`/`createClient`/`deleteClient`)
- [x] NEW `iac/commands/bootstrap-pangolin-client.ts`
- [x] NEW `iac/commands/sync-clients.ts`
- [x] Extend `iac/commands/rotate-auth.ts` — fix the `newApiKey` vs `newApiKey.apiKey` bug + record metadata in audit JSON
- [x] Extend `iac/commands/bootstrap.ts` — add `await syncClients()` to Phase 9 (the all-syncs phase)

## Phase C: Stack + Komodo

- [x] NEW `bonneagar/stacks/newt-arm1-oci/compose.yaml` (newt:1.14.0 + bons-locket-shim:infisical-0.2.0)
- [x] NEW `bonneagar/stacks/newt-arm1-oci/sidecar.yaml` (sentinel)
- [x] NEW `bonneagar/stacks/newt-arm1-oci/secrets.env` (2 infisical:// URIs)
- [x] NEW `bonneagar/stacks/newt-arm1-oci/pangolin.yaml` (no-op sentinel)
- [x] NEW `bonneagar/stacks/newt-arm1-oci/blueprint.yaml` (no-op sentinel)
- [x] NEW `bonneagar/stacks/newt-arm1-oci/.env.example`
- [x] NEW `bonneagar/komodo/procedures/deploy-pangolin-client-arm1-oci.toml`
- [x] NEW `bonneagar/komodo/procedures/deploy-pangolin-client-bunchloch.toml`
- [x] Extend `bonneagar/komodo/resource-syncs/cross-cutting.toml` (reference the 2 NEW procedures)

## Phase D: Orchestrator + scripts

- [x] Extend `scripts/deploy-full.ts` to 10 phases
- [x] Extend `scripts/deploy-full.sh` to 10 phases (PHASE_NAMES + phase validation regex)

## Phase E: Drift + IaC package.json scripts

- [x] Add `iac:bootstrap-pangolin-client` script to `bonneagar/package.json`
- [x] Add `iac:sync:clients` script to `bonneagar/package.json`
- [x] Add `bootstrap-pangolin-client` script to `bonneagar/iac/package.json`
- [x] Add `sync:clients` script to `bonneagar/iac/package.json`
- [x] Update root AGENTS.md spec count (89 specs, 4 shared)
- [ ] Update bonneagar/AGENTS.md stack count (90) + IaC commands count (26) — DEFERRED (not critical)

## Phase F: Validation + runbook

- [x] Phase 0 verification: iac:health reaches the Pangolin API
- [ ] Run `bun run openspec validate 2026-08-15-bonneagar-infra-remediation-v2 --strict`
- [ ] Run `mise run iac:health` to verify all 3 systems (or document what's broken)
- [ ] Run `mise run iac:bootstrap-pangolin-client --host=arm1-oci --type=machine` to mint the arm1-oci client
- [ ] Run `mise run iac:bootstrap-pangolin-client --host=bunchloch --type=user` to mint the bunchloch user
- [ ] Run `mise run deploy:full` to verify the 10-phase orchestrator
- [ ] Verify all 92 stacks pass `mise run stack-doctor`
- [ ] Verify the 6 Dagster sensors are ACTIVE

## Acceptance criteria (ALL must pass)

1. `bun run openspec validate 2026-08-15-bonneagar-infra-remediation-v2 --strict` exits 0
2. `iac:health` exits 0 for Pangolin (the root cause is now fixed via load-env.ts)
3. `iac:bootstrap-pangolin-client --host=arm1-oci --type=machine` mints a Pangolin client + writes credentials to `.env` + Infisical + renders the newt compose
4. `iac:bootstrap-pangolin-client --host=bunchloch --type=user` mints a Pangolin user client + prints the login command
5. `mise run deploy:full` completes all 10 phases (warm start, ~25 min)
6. `mise run stack-doctor` passes on all 92 stacks
7. `mise run lint:drift-docs` passes on all AGENTS.md files
