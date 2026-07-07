# Tasks — croilar-portfolio

## Phase 1: Rename + restructure (DONE — PR 8aac964b5)
- [x] PR1. Move `stedding/dev/cianfhoghlaim copy/sruth/aleyum/*` → top-level `sruth/croilar/`
      (rsync — `stedding/` is gitignored, no git history to preserve)
- [x] PR1. Delete leftover backup copies in `stedding/dev/cianfhoghlaim_backup/stedding/flows/aleyum/`, `stedding/dev/flows/aleyum/`, `stedding/flows/aleyum/` (8.8M freed)
- [x] PR1. Update `infrastructure/stacks/agent-os/` 6-file pattern (compose + sidecar + secrets + pangolin + blueprint + .env.example) — aleyum-agentos → croilar-agentos (with legacy alias for safe transition)
- [x] PR1. Update `sruth/oideachais/data_platform/agent_os/config.yaml` to add `croilar` to A2A `allowed_services`
- [x] PR1. Update `infrastructure/stacks/motherduck/` (blueprint + README) — add `croilar_market` alongside legacy `aleyum_market`
- [x] PR1. Update `infrastructure/stacks/lakehouse/init-db.sql` — add `ducklake_croilar` alongside legacy `ducklake_aleyum`
- [x] PR1. Update `infrastructure/templates/github-pr-forward.yaml` — add `croilar` to FLOW_NAME list
- [x] PR1. Update `infrastructure/pangolin/a2a-resources.blueprint.yaml` (TODO: follow-up — keep aleyum-agentos as legacy, add croilar-agentos)
- [x] PR1. Update `.infisical.env` — R2/Cloudflare refs use `dev-baile/cloudflare/*` (was `aleyum/cloudflare/account_id`); add a 13-line CROILAR block with Spotify/GitHub/SoundCloud/YouTube/HMAC/encryption_key/db_url/portfolio_bucket
- [x] PR1. Add `croilar` to root `pyproject.toml` `[tool.uv.workspace] members` + `[tool.uv.sources]`
- [x] PR1. Add `croilar` + `sruth/croilar/portal` to root `package.json` `workspaces`
- [x] PR1. Update `openspec/specs/infrastructure-stacks/spec.md` line 104 (aleyum → croilar)
- [x] PR1. Validate: `uv workspace list` shows croilar; `bun install` resolves; `docker compose -f compose.yaml -f sidecar.yaml --env-file .env.example config --quiet` exits 0

## Phase 2: Web app + Dagster (next PRs)
- [ ] PR2. Build `sruth/croilar/web/` TanStack Start scaffold with 9 routes
- [ ] PR2. Build `sruth/croilar/portal/` (preserve + repoint)
- [ ] PR2. Build `sruth/croilar/cv/` + `sruth/croilar/teaching/` + `sruth/croilar/identity/` BAML extraction + Dagster assets
- [ ] PR2. Build `sruth/croilar/dagster_assets/` + `sruth/croilar/cocoindex_flows/` + `sruth/croilar/notebooks/` (Marimo)
- [ ] PR2. Build 4 new croilar stacks: web + portal + dagster + marimo (compose + sidecar + secrets + pangolin + blueprint + .env.example)
- [ ] PR2. Seed 20 new Infisical items in `dev-baile/sruth/croilar/`

## Phase 3: Image management + GitOps (later PRs)
- [ ] PR3. Image management: `.agents/skills/image-management/SKILL.md` + pinning policy
- [ ] PR3. R2 bucket `croilar-assets` + sharp image pipeline (3 sizes + WebP)
- [ ] PR3. Multi-arch rebuilds of 5 existing in-repo images
- [ ] PR3. Build 5 new croilar images (web, portal, dagster, marimo, image-pipeline)
- [ ] PR3. Dagger module: `infrastructure/dagger/` with 6 functions

## Phase 4: CI/CD (last PRs)
- [ ] PR4. `.forgejo/workflows/`: 7 workflows (ci, build-images, deploy-prod, renovate, release-please, secret-scan, openspec-validate)
- [ ] PR4. `.github/workflows/`: 7 mirror workflows
- [ ] PR4. 8 new Komodo procedures
- [ ] PR4. SOPS setup for long-lived credentials

## Validation (per PR)
- [x] `bash scripts/stack-doctor.sh` (passes with no NEW CRITICALs) — run as part of `validate-stacks`
- [x] `bunx --yes openspec validate croilar-portfolio --strict` (passes)
- [x] `docker compose -f compose.yaml -f sidecar.yaml --env-file .env.example config --quiet` for the agent-os stack (exit 0)
- [x] `bun install` (manifests resolve)
- [x] `uv sync` (uv workspace resolves — `uv workspace list` shows croilar)
- [ ] Git commit + push (Landing the Plane) — pending
