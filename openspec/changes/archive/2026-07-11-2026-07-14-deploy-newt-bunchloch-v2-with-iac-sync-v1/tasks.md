# Tasks: 2026-07-14-deploy-newt-bunchloch-v2-with-iac-sync-v1

## Phase 0 — Read baseline

- [x] Read `komodo/procedures/deploy-newt-bunchloch.toml` (v1)
- [x] Read `iac/commands/sync-sites.ts` (the new IaC command)
- [x] Read `stacks/newt/IMAGE` (the v1.14.0 pin)

## Phase 1 — Bonneagar code changes

- [x] Create `komodo/procedures/deploy-newt-bunchloch-v2.toml` with 5 stages:
  - preflight (docker + env vars + locket)
  - iac-provision (bun run iac:sync:sites)
  - stackup (mkdir + docker compose up -d)
  - wireguard-tunnel (wait + wg show)
  - health-checks (5 verifications)
- [x] Update `komodo/procedures/server_id_legend.md`:
  - Add `deploy-newt-bunchloch-v2.toml` entry (RECOMMENDED)
  - Mark `deploy-newt-bunchloch.toml` as LEGACY (v1)

## Phase 2 — Openspec change

- [x] Write `proposal.md`
- [x] Write `cross-repo-sync.md`
- [x] Write `tasks.md` (this file)
- [x] Write `specs/agent-platform-cluster/spec.md` with 1 ADDED Requirement:
  - `### Requirement: deploy-newt-bunchloch-v2 integrates with iac:sync:sites + asserts newt v1.14.0`
  - 3 Scenarios: iac-provision runs, version mismatch detected, all 5 health-checks pass

## Phase 3 — Validate + commit + push

- [ ] `openspec validate 2026-07-14-deploy-newt-bunchloch-v2-with-iac-sync-v1 --strict` returns 0
- [ ] Commit on `pick-5b-bonneagar-v5-continuation`
- [ ] Push bonneagar branch
- [ ] Commit on `pick-4-biep-v1`
- [ ] Push cianfhoghlaim branch

## Phase 4 — Archive

- [ ] `openspec archive 2026-07-14-deploy-newt-bunchloch-v2-with-iac-sync-v1 --yes`
