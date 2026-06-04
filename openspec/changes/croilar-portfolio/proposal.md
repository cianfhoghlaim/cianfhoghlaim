# croilar-portfolio — Personal portfolio + CV + data engineering subproject

## Why

The cianfhoghlaim monorepo currently has 3 subprojects at the top level (`oideachais/`, `meaisínfhoghlaim/`, `tuatha/`), but **no personal-portfolio site for the project's author** (Cian). The legacy `sruth/aleyum/` (a music-producer pseudonym for a subset of the same content) is being renamed and expanded to become the canonical portfolio + CV + data-engineering showcase subproject.

The new subproject is called **croílár** (Irish: "core/heart") — reflecting the fact that this is the personal *core* of the cianfhoghlaim platform: the author's CV, achievements, teaching record, identity, music catalogue, and code projects, all unified under one bilingual (English + Irish) public site.

The change is multi-pronged:

1. **Rename** the legacy `aleyum/` to `croilar/` (preserving git history via `git mv`)
2. **Build a new TanStack Start web app** with 9 subprojects (Home, CV, Music, Code, Research, Teaching, Data, Identity, Contact) — reusing the proven patterns from `oideachais/web/` + the `cianfhoghlaim-base` Better-T-Stack template
3. **Stand up the data engineering layer** — Dagster + DLT + CocoIndex + BAML pipelines that ingest the author's CV PDFs, teaching records, identity documents, music catalogues, and code repos; cross-link with existing `oideachais` + `meaisínfhoghlaim` outputs via the DuckLake catalog
4. **Wire up full GitOps automation** — multi-arch image management (ghcr.io), Komodo stack procedures, Dagger pipeline orchestration, Forgejo + GitHub Actions workflows
5. **Establish the personal-portfolio capability tree** as 3 first-class OpenSpec capabilities (`croilar-portfolio`, `croilar-data-engineering`, `croilar-cv-extraction`)

## What Changes

### 1. Rename + restructure

- Move `stedding/dev/cianfhoghlaim copy/sruth/aleyum/*` → top-level `croilar/`
- Delete the leftover backup copies in `stedding/dev/cianfhoghlaim_backup/stedding/flows/aleyum/`, `stedding/dev/flows/aleyum/`, `stedding/flows/aleyum/`
- Repoint the `aleyum-agentos` build context in `infrastructure/stacks/storage/agent-os/compose.yaml` to the new `croilar/agent_os/`
- Update all `.infisical.env` references from `aleyum/*` to `croilar/*`

### 2. New `croilar/` subproject (top-level)

The subproject adopts the proven patterns from:
- `oideachais/web/` (TanStack Start + React 19 + Tailwind 4)
- `oideachais/data_platform/dagster_assets/` (Dagster pattern)
- `oideachais/data_platform/dlt_sources/` (DLT pattern)
- `oideachais/data_platform/cocoindex_flows/` (CocoIndex flow pattern)
- `oideachais/data_platform/baml_src/` (BAML schemas)
- `meaisínfhoghlaim/agents/` (Agent + Langfuse pattern)
- `stedding/dev/cianfhoghlaim copy/taighde/web/cianfhoghlaim-base/` (Better-T-Stack starter)

Layout: `croilar/{web, portal, cv, teaching, identity, research, music, pipelines, dagster_assets, baml, cocoindex_flows, notebooks, services, api, definitions.py, config/, sources.md, compose.yaml, Dockerfile.dagster, mise.toml}`

### 3. 9 web subprojects (all in the initial release)

| Route | Purpose | Data source |
|:--|:--|:--|
| `/` | Home — name, photo, hero tagline | Static + BAML |
| `/cv` | Full academic + professional + teaching record | BAML extraction of `author_cian_deacy_lyons.../achievement/` + `teaching/` PDFs |
| `/music` | Spotify/SoundCloud/YouTube/Lemongrass catalogue | BAML extraction from DLT pipelines |
| `/code` | GitHub repos for `@Yedya` | GitHub API |
| `/research` | Cross-linked to `oideachais/` + `meaisínfhoghlaim/` outputs | DuckLake catalog |
| `/teaching` | BCS PGC scholarship, placements, student feedback | BAML extraction from teaching PDFs |
| `/data` | Dagster pipeline status (12+ assets) | Dagster GraphQL API |
| `/identity` | Verification materials (encrypted at rest via SOPS) | PII-handled |
| `/contact` | Hono Worker on Cloudflare | End-to-end encrypted form |

### 4. Data engineering layer

12+ Dagster assets:
- 4 music pipeline assets (spotify_ingestion, soundcloud_ingestion, youtube_ingestion, music_embedded)
- 3 CV pipeline assets (cv_pdf_ingestion, cv_extraction, cv_search_index)
- 3 teaching pipeline assets (placement_ingestion, teaching_extraction, teaching_search)
- 1 identity asset (id_document_verification)
- 2 cross-link assets (oideachais_assets_embedded, meaisinfhoghlaim_assets_embedded)
- BAML schemas: `cv_extraction.baml`, `teaching_extraction.baml`, `identity_verification.baml` (new) + 4 preserved from aleyum

### 5. GitOps automation (the main ask)

**Image management** (codify in `.agents/skills/image-management/SKILL.md`):
- Pinning policy: `<major>.<minor>.<patch>` for production, never `:latest`
- Multi-arch: `linux/amd64,linux/arm64` for every in-repo image
- Renovate opens weekly PRs
- 5 existing images (`browser-grid`, `cal-diy`, `stagehand-local`, `n8n-init`, `vikunja-seed`) need multi-arch rebuilds
- 5 new images: `croilar-web`, `croilar-portal`, `croilar-dagster`, `croilar-marimo`, `croilar-image-pipeline`

**Komodo procedures** (8 new):
- `croilar-stack-up` / `croilar-stack-down` / `croilar-stack-health` (4 new croilar stacks)
- `croilar-image-rebuild` / `croilar-image-publish`
- `croilar-renovate-pr`
- `croilar-backup` (pg_dump to Garage S3)
- `croilar-gitops-fullstack` (full chain: Forgejo build → ghcr.io push → Komodo deploy → Pangolin refresh)

**Dagger module** (`infrastructure/dagger/`):
- `dagger call ci`
- `dagger call build-images --platforms=linux/amd64,linux/arm64`
- `dagger call deploy-cloudflare`
- `dagger call deploy-komodo --stack=croilar-web`
- `dagger call deploy-pangolin --resource=croilar-web`
- `dagger call gitops-fullstack`

**Both Forgejo + GitHub Actions** (per user request):
- `.forgejo/workflows/`: 7 workflows (primary)
- `.github/workflows/`: 7 mirror workflows (for community / external PRs)

**Infisical** (~20 new items in `dev-baile/croilar/`)
**Locket** sidecar in all 4 new croilar stacks
**SOPS** for long-lived credentials (GitHub App keys, signing keys, disaster-recovery passphrases)

### 6. OpenSpec ecosystem

- 3 new capability specs (`croilar-portfolio`, `croilar-data-engineering`, `croilar-cv-extraction`)
- 3 new openspec specs (the same 3) committed at `openspec/specs/<capability>/spec.md`
- `openspec/project.md` and `openspec/AGENTS.md` updated to include the new capabilities
- The 3 historical research files moved to `docs/openspec/`

## Impact

| Surface | Before | After |
|:--|:--|:--|
| Top-level subprojects | 3 (oideachais, meaisínfhoghlaim, tuatha) | 4 (+ croilar) |
| Web subprojects | 1 (oideachais-web in bun workspaces) | 3 (+ croilar-web, croilar-portal) |
| Python workspace members | 4 (oideachais, tuath, códeolas, sruth-browser) | 5 (+ croilar) |
| OpenSpec capabilities | 24 | 27 (+ 3 croilar) |
| Komodo procedures | 56 (incl. team-*) | 64 (+ 8 croilar-*) |
| Image registry tags | 5 in-repo images, mixed `:latest` and pinned | 10 in-repo images, all pinned to `<major>.<minor>.<patch>` + multi-arch |
| Forgejo Actions workflows | 0 | 7 |
| GitHub Actions workflows | 0 | 7 (mirror) |
| Dagger modules | 0 in-repo | 6 in-repo (ci, build-images, deploy-cloudflare, deploy-komodo, deploy-pangolin, gitops-fullstack) |
| Infisical items | ~50 | ~70 (+ 20 croilar) |

## Out of scope (follow-up issues to file)

- Mobile app (the `cianfhoghlaim-base` template has React Native + Expo — deferred to v2 of croilar)
- Custom domain `iomha.cianfhoghlaim.ie` vs `croilar.cianfhoghlaim.ie` (deferred to user decision)
- BAML extraction of identity documents (PII-heavy, will require SOPS encryption at rest + Pocket ID SSO-gated access — deferred to a separate change)
- GitHub mirror repo setup (deferred — user needs to create the GitHub repo first)
- Replacing BAML with OpenCode Go API structured outputs (deferred — BAML is fine for this use case)
