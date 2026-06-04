# Tasks — croilar-portfolio

## Phase 1: Rename + restructure (this PR)
- [ ] PR1. Move `stedding/dev/cianfhoghlaim copy/sruth/aleyum/*` → top-level `croilar/` (using `git mv` to preserve history)
- [ ] PR1. Delete leftover backup copies in `stedding/dev/cianfhoghlaim_backup/stedding/flows/aleyum/`, `stedding/dev/flows/aleyum/`, `stedding/flows/aleyum/`
- [ ] PR1. Repoint `aleyum-agentos` build context in `infrastructure/stacks/storage/agent-os/compose.yaml` to the new `croilar/agent_os/`
- [ ] PR1. Update all `.infisical.env` references from `aleyum/*` to `croilar/*`
- [ ] PR1. Add `croilar = { workspace = true }` to root `pyproject.toml` `[tool.uv.sources]` + `croilar` to `[tool.uv.workspace] members`
- [ ] PR1. Add `croilar/web` and `croilar/portal` to root `package.json` `workspaces`
- [ ] PR1. Add `croilar-web` and `croilar-portal` filter targets to `turbo.json`

## Phase 2: Web app + Dagster (next PRs)
- [ ] PR2. Build `croilar/web/` TanStack Start scaffold with 9 routes
- [ ] PR2. Build `croilar/portal/` (preserve + repoint)
- [ ] PR2. Build `croilar/cv/` + `croilar/teaching/` + `croilar/identity/` BAML extraction + Dagster assets
- [ ] PR2. Build `croilar/dagster_assets/` + `croilar/cocoindex_flows/` + `croilar/notebooks/` (Marimo)
- [ ] PR2. Build 4 new croilar stacks: web + portal + dagster + marimo (compose + sidecar + secrets + pangolin + blueprint + .env.example)
- [ ] PR2. Seed 20 new Infisical items in `dev-baile/croilar/`

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
- [ ] `bash scripts/stack-doctor.sh` (passes with no NEW CRITICALs)
- [ ] `bunx --yes openspec validate <change-id> --strict` (passes)
- [ ] `docker compose -f compose.yaml -f sidecar.yaml --env-file .env.example config --quiet` for each new stack (exit 0)
- [ ] `bun install` (manifests resolve)
- [ ] `uv sync` (uv workspace resolves)
- [ ] Git commit + push (Landing the Plane)
