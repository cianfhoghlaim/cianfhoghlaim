# Image Management — Cianfhoghlaim Monorepo

## Pinning Policy

Every image pushed to `ghcr.io/cianfhoghlaim/` MUST be pinned to a
semver tag. **Never use `:latest` in production stacks.**

All in-repo images SHALL be tagged as `<major>.<minor>.<patch>` and
built for multi-arch (`linux/amd64,linux/arm64`).

## Image Registry

- **Registry:** `ghcr.io/cianfhoghlaim/`
- **Auth:** GitHub Actions OIDC → `GITHUB_TOKEN` with `write:packages`
- **Visibility:** Public

## In-Repo Images

| Image | Source | Dockerfile | Multi-Arch |
|:--|:--|:--|:--|
| `croilar-web` | `croilar/` | `croilar/Dockerfile.web` | `linux/amd64,linux/arm64` |
| `croilar-portal` | `croilar/portal/` | `croilar/portal/Dockerfile` | `linux/amd64,linux/arm64` |
| `croilar-dagster` | `croilar/` | `croilar/Dockerfile.dagster` | `linux/amd64,linux/arm64` |
| `croilar-marimo` | `croilar/notebooks/` | `croilar/Dockerfile.marimo` | `linux/amd64,linux/arm64` |
| `browser-grid` | `infrastructure/stacks/browser/` | - | PENDING multi-arch rebuild |
| `cal-diy` | `stedding/repos/cal.diy/` | - | PENDING multi-arch rebuild |
| `stagehand-local` | `infrastructure/stacks/browser/` | - | PENDING multi-arch rebuild |
| `n8n-init` | `infrastructure/stacks/engineering/n8n/` | - | PENDING multi-arch rebuild |
| `vikunja-seed` | `infrastructure/stacks/tools/vikunja/` | - | PENDING multi-arch rebuild |

## Build Commands

### Multi-arch build (single image)

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag ghcr.io/cianfhoghlaim/croilar-web:0.1.0 \
  --push \
  -f croilar/Dockerfile.web \
  croilar/
```

### Via Dagger (once the Dagger module is added)

```bash
dagger call build-images --platforms=linux/amd64,linux/arm64
```

## Renovate Automation

Renovate opens weekly PRs bumping image tags. Pin to minor
(`ghcr.io/cianfhoghlaim/croilar-web:0.1`) and Renovate will
propose patch bumps automatically.

Renovate config (future — `.github/renovate.json`):

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"],
  "docker": {
    "pinDigests": true,
    "enabled": true
  },
  "packageRules": [
    {
      "matchDatasources": ["docker"],
      "matchPackageNames": ["ghcr.io/cianfhoghlaim/**"],
      "schedule": ["on monday"],
      "automerge": false
    }
  ]
}
```

## Multi-Arch Rebuild Checklist

For each of the 5 existing in-repo images needing rebuilds:

- [ ] `browser-grid:local` → `ghcr.io/cianfhoghlaim/browser-grid:0.1.0` (linux/amd64,linux/arm64)
- [ ] `cal-diy:local` → `ghcr.io/cianfhoghlaim/cal-diy:0.1.0` (linux/amd64,linux/arm64)
- [ ] `stagehand-local:local` → `ghcr.io/cianfhoghlaim/stagehand:0.1.0` (linux/amd64,linux/arm64)
- [ ] `n8n-init:latest` → `ghcr.io/cianfhoghlaim/n8n-init:0.1.0` (linux/amd64,linux/arm64)
- [ ] `vikunja-seed:latest` → `ghcr.io/cianfhoghlaim/vikunja-seed:0.1.0` (linux/amd64,linux/arm64)

## Edge Cases & Gotchas

1. **DuckDB is single-threaded** — do NOT run concurrent writes from
   multiple containers against the same `croilar.duckdb` file. Use
   DuckLake (S3 + PostgreSQL) for production concurrency.

2. **CLIP models are large** (600MB+) — the Docker build context
   should exclude model weights. Mount them as Docker volumes at
   runtime instead.

3. **Git LFS** — the 37 author PDFs in
   `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/` are tracked
   directly (not LFS). They add ~15MB to the repo. Consider LFS if
   the corpus grows beyond 50MB.

4. **Secrets never in images** — all credentials flow through Infisical
   → Locket sidecar → environment variables. Images contain zero secrets.
