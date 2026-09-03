# Tasks: 2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow

## Phase 0 — Pre-flight (no edits) (10 min)

- [ ] 0.1 Verify the v6-drift-remediation-v1 change has archived (its `preflight:arm-oci` script + `iac:bootstrap` are hard deps):
      `openspec list` returns only non-v6-drift changes
- [ ] 0.2 Read `scripts/preflight-arm-oci.ts` + `bonneagar/iac/commands/deploy.ts` to confirm the 4 preflight checks + 10-step iac:bootstrap deploy
- [ ] 0.3 Confirm `bun run preflight:arm-oci --dry-run` exits 0 against the current arm1-oci state (dry-run mode, no fail)
- [ ] 0.4 Read the ccc-freshness CI workflow (`.forgejo/workflows/ccc-freshness.yml`) + the v1 ccc index location (`.cocoindex_code/target_sqlite.db`)

## Phase 1 — arm1-oci stack + 4 procedures (45 min)

- [ ] 1.1 Create `bonneagar/komodo/stacks/hermes-arm1-oci.toml` (server_id="arm1-oci", uses public `nousresearch/hermes-agent:v2026.7.1`)
- [ ] 1.2 Create `bonneagar/komodo/procedures/deploy-hermes-arm1-oci.toml` (5 stages: pre-reqs → `deploy-langfuse-arm1-oci` → DeployStack hermes → ApplyBlueprint + init-allowlist → health)
- [ ] 1.3 Create `bonneagar/komodo/procedures/deploy-langfuse-arm1-oci.toml` (4 stages)
- [ ] 1.4 Create `bonneagar/komodo/procedures/deploy-observability-arm1-oci.toml` (3 stages)
- [ ] 1.5 Create `bonneagar/komodo/procedures/deploy-agent-platform-cluster-arm1-oci.toml` (the omnibus, 6 stages, accepts `--skip=...`)
- [ ] 1.6 Verify all 4 procedure files have `server_id = "arm1-oci"` at the top
- [ ] 1.7 Run `openspec validate` on the change (catches spec errors early)

## Phase 2 — Cross-cutting prerequisite procedures (15 min)

- [ ] 2.1 Create `bonneagar/komodo/procedures/pangolin-first.toml` (3 stages: ssh + health + OIDC ready)
- [ ] 2.2 Create `bonneagar/komodo/procedures/komodo-core.toml` (3 stages: pod alive + REST + periphery)
- [ ] 2.3 Create `bonneagar/komodo/procedures/infisical-first.toml` (3 stages: vault + project + identities)
- [ ] 2.4 Create `bonneagar/komodo/procedures/locket-deploy.toml` (3 stages: binary + secret + resolved)
- [ ] 2.5 Update `komodo/resource-syncs/cross-cutting.toml` to reference all 4 by name (comment block)

## Phase 3 — `server_id` backfill on existing bunchloch procedures (20 min)

Add `server_id = "bunchloch"` at the top of each of the 14 existing bunchloch procedure files:

- [ ] 3.1 `deploy-agent-platform-cluster-bunchloch.toml`
- [ ] 3.2 `deploy-apple-photos-ingest-bunchloch.toml`
- [ ] 3.3 `deploy-cognee-bunchloch.toml`
- [ ] 3.4 `deploy-croilar-bunchloch.toml`
- [ ] 3.5 `deploy-falkordb-bunchloch.toml`
- [ ] 3.6 `deploy-graphiti-bunchloch.toml`
- [ ] 3.7 `deploy-hermes-bunchloch.toml`
- [ ] 3.8 `deploy-lakehouse-bunchloch.toml`
- [ ] 3.9 `deploy-lancedb-bunchloch.toml`
- [ ] 3.10 `deploy-langfuse-bunchloch.toml`
- [ ] 3.11 `deploy-litellm-bunchloch.toml`
- [ ] 3.12 `deploy-llama-swap-bunchloch.toml`
- [ ] 3.13 `deploy-logfire-bunchloch.toml`
- [ ] 3.14 `deploy-mailcow-dockerized-bunchloch.toml`
- [ ] 3.15 `deploy-mlflow-bunchloch.toml`
- [ ] 3.16 `deploy-cianfhoghlaim-bunchloch.toml`
- [ ] 3.17 `deploy-openchamber-bunchloch.toml`
- [ ] 3.18 `deploy-openclaw-bunchloch.toml`

## Phase 4 — Code-owned image builds (Build resources + Dockerfiles) (45 min)

- [ ] 4.1 Create `bonneagar/komodo/builds/` directory
- [ ] 4.2 Create `bonneagar/komodo/builds/openchamber-arm1-oci.toml` (output: `ghcr.io/cianfhoghlaim/openchamber:1.14.1-arm1`)
- [ ] 4.3 Create `bonneagar/komodo/builds/openclaw-arm1-oci.toml` (output: `ghcr.io/cianfhoghlaim/openclaw:2026.6-arm1`)
- [ ] 4.4 Create `bonneagar/komodo/builds/hermes-arm1-oci.toml` (no-op; references public `nousresearch/hermes-agent:v2026.7.1`)
- [ ] 4.5 Create `bonneagar/stacks/openchamber/Dockerfile.openchamber-web` (the multi-stage build that landed `openchamber:local-1.14.1` last turn — Node 22 + multi-stage install)
- [ ] 4.6 Create `bonneagar/stacks/openclaw/Dockerfile.openclaw` (synthetic Dockerfile matching upstream shape: Node 24-bookworm + Bun 1.3.13)
- [ ] 4.7 Update `bonneagar/komodo/stacks/openchamber-arm1-oci.toml` `image:` → `ghcr.io/cianfhoghlaim/openchamber:1.14.1-arm1`
- [ ] 4.8 Update `bonneagar/komodo/stacks/openclaw-arm1-oci.toml` `image:` → `ghcr.io/cianfhoghlaim/openclaw:2026.6-arm1`
- [ ] 4.9 Test the openchamber Dockerfile locally: `docker buildx build --platform linux/arm64 -t openchamber:local-1.14.1 -f Dockerfile.openchamber-web .` from `bonneagar/stacks/openchamber/`

## Phase 5 — Remote dev workflow: newt stack (30 min)

- [ ] 5.1 Create `bonneagar/stacks/newt/docker-compose.yaml` (extracted from the user's `.local/newt/docker-compose.yaml`; 4 services: locket + newt + periphery + beszel-agent)
- [ ] 5.2 Create `bonneagar/stacks/newt/sidecar.yaml` (canonical Locket shape)
- [ ] 5.3 Create `bonneagar/stacks/newt/secrets.env` (NEWT_ID + NEWT_SECRET + PERIPHERY_ONBOARDING_KEY via Infisical)
- [ ] 5.4 Create `bonneagar/stacks/newt/pangolin.yaml` (optional, for newt as a private resource on the mesh)
- [ ] 5.5 Create `bonneagar/stacks/newt/blueprint.yaml` (Pangolin private-resource def)
- [ ] 5.6 Create `bonneagar/stacks/newt/.env.example`
- [ ] 5.7 Create `bonneagar/komodo/stacks/newt-bunchloch.toml` (server_id="bunchloch", `labels: ["komodo.skip=true"]`)
- [ ] 5.8 Create `bonneagar/komodo/procedures/deploy-newt-bunchloch.toml` (5 stages: pre-reqs → StackUp → WireGuard tunnel check → Komodo periphery registration → health)
- [ ] 5.9 Validate: `bun run validate-stacks` (0 hard failures for the newt stack)

## Phase 6 — Resource-sync TOML updates (20 min)

- [ ] 6.1 Update `komodo/resource-syncs/arm1-oci.toml`:
      - Add the 3 new build resources to `resource_path`
      - Add `hermes-arm1-oci.toml` + `deploy-newt-bunchloch.toml` to `resource_path`
      - Add comment block documenting the `server_id` convention
- [ ] 6.2 Update `komodo/resource-syncs/bunchloch.toml`:
      - Add `newt-bunchloch.toml` + `deploy-newt-bunchloch.toml` + 3 build resources to `resource_path`
      - Add the same `server_id` comment block
- [ ] 6.3 Update `komodo/resource-syncs/cross-cutting.toml`:
      - Explicit comment that the 4 prerequisite procedures (`pangolin-first`, `komodo-core`, `infisical-first`, `locket-deploy`) are now in the path
- [ ] 6.4 Create `komodo/procedures/server_id_legend.md` (the convention doc — lists each procedure + its `server_id`, back-compat, deprecation warning)

## Phase 7 — Validation + commit (20 min)

- [ ] 7.1 `openspec validate 2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow --strict` returns 0
- [ ] 7.2 `mise run lint:skills` (53/53, no regression)
- [ ] 7.3 `bun run validate-stacks` (0 hard failures)
- [ ] 7.4 `git status` shows all 24 new files + 17 modified files
- [ ] 7.5 Commit with message: `feat(komodo): deploy agent-platform-cluster to arm1-oci + newt remote-dev workflow`
- [ ] 7.6 Push to `origin pick-4-biep-v1` (or whatever the current default branch is)

## Phase 8 — Archive + final acceptance (10 min)

- [ ] 8.1 `openspec archive 2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow --yes` succeeds
- [ ] 8.2 `openspec list` returns the change as archived
- [ ] 8.3 (Post-archive on arm1-oci) `bun run preflight:arm-oci --strict --emit-md` reports ALL CHECKS PASSED
- [ ] 8.4 (Post-archive on arm1-oci) `km run procedure deploy-newt-bunchloch` completes
- [ ] 8.5 (Post-archive on arm1-oci) `km run procedure deploy-agent-platform-cluster-arm1-oci` completes within 15 min
- [ ] 8.6 (Post-archive on bunchloch) `curl https://hermes.cianfhoghlaim.ie/api/health` returns 200 (proves remote dev workflow works)
- [ ] 8.7 (Post-archive) Update root `AGENTS.md` to reflect the new arm1-oci agent surfaces + the newt remote-dev workflow
- [ ] 8.8 (Post-archive) Update `openspec/AGENTS.md` to reference the archived change as a reference for arm1-oci + newt patterns
