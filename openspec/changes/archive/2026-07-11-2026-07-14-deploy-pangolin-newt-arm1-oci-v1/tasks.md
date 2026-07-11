# Tasks: 2026-07-14-deploy-pangolin-newt-arm1-oci-v1

## Phase 0 — Read baseline

- [x] Read `stacks/pangolin/newt.yaml` (the arm1-oci newt template, now pinned at v1.14.0)
- [x] Read `stacks/pangolin/compose.yaml` (the parent compose to extend)
- [x] Read `komodo/stacks/pangolin-core-arm1.toml` (the Komodo stack registration)

## Phase 1 — Bonneagar code changes

- [x] Create `komodo/procedures/deploy-pangolin-newt-arm1-oci.toml` with 5 stages:
  - preflight (Pangolin + Infisical health)
  - iac-provision (bun run iac:sync:sites)
  - stackup (docker compose -f compose.yaml -f newt.yaml -f newt.sidecar.yaml up -d newt)
  - wireguard-tunnel (wait + wg show)
  - health-checks (5 verifications)
- [x] Update `komodo/procedures/server_id_legend.md` — add the new procedure to the arm1-oci section

## Phase 2 — Openspec change

- [x] Write `proposal.md`
- [x] Write `cross-repo-sync.md`
- [x] Write `tasks.md` (this file)
- [x] Write `specs/agent-platform-cluster/spec.md` with 1 ADDED Requirement:
  - `### Requirement: deploy-pangolin-newt-arm1-oci brings the arm1-oci-side newt client online`
  - 3 Scenarios: iac-provision runs, version mismatch detected, all 5 health-checks pass

## Phase 3 — Validate + commit + push

- [ ] `openspec validate 2026-07-14-deploy-pangolin-newt-arm1-oci-v1 --strict` returns 0
- [ ] Commit on `pick-5b-bonneagar-v5-continuation`
- [ ] Push bonneagar branch
- [ ] Commit on `pick-4-biep-v1`
- [ ] Push cianfhoghlaim branch

## Phase 4 — Archive

- [ ] `openspec archive 2026-07-14-deploy-pangolin-newt-arm1-oci-v1 --yes`
