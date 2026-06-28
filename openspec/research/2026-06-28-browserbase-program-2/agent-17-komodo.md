# Agent 17 — Komodo (Docker Compose orchestrator)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages — Infrastructure)
**BrowserBase budget:** ~200 credits (used ~120 across 8 navigations + 6 raw GitHub fetches + 3 webfetch)
**Source sites:** `https://komo.do` (homepage), `https://komo.do/docs/*` (Docusaurus site, served from `docsite/docs/` in repo), `https://raw.githubusercontent.com/moghtech/komodo/main/{docsite,compose,config}/*`, plus `infrastructure/komodo/` CCC reads

---

## TL;DR

**Komodo** (v2.2.0 latest, May 7 2026 — 11.5k stars, 333 forks, GPL-3.0) is the **GitOps-driven Docker Compose / Swarm orchestrator + server monitor** that powers the Cianfhoghlaim 90-stack fleet across `arm1-oci` + `bunchloch` (+ planned `cax41-hetzner`). Its Rust core (63.1%) and TypeScript UI (34.0%) speak a strict **TOML resource schema** (`[[server]]`, `[[stack]]`, `[[deployment]]`, `[[build]]`, `[[builder]]`, `[[repo]]`, `[[procedure]]`, `[[resource_sync]]`, `[[variable]]`, `[[user_group]]`, `[[alerter]]`) that is **GitOps-friendly**: a single `[[resource_sync]]` with `resource_path = ["path/to/*.toml", ...]` globs pulls every Cianfhoghlaim TOML into Komodo's database and diffs it on push, executing the deploy.

The canonical Cianfhoghlaim pattern is **already drifted** from the P2-12 spec: it uses **5 sub-dirs** (`servers/`, `stacks/`, `procedures/`, `resource-syncs/`, `sites/`) — the P2-12 spec mentions a non-existent `builder/` subdir that has zero hits in `infrastructure/komodo/`. The two `cax41-hetzner` hosts aren't actually wired up in `servers.toml` — only `arm1-oci` and `bunchloch` exist (line 14-43). The P2-12 spec's `variables.toml` is also fictional — variables are managed inline in each TOML file (see `infrastructure/komodo/procedures/storage-lakehouse.toml:104-121` and the `[[variable]]` block pattern in Komodo upstream docs).

## Code

### Komodo canonical resource schemas (from `moghtech/komodo` v2.2.0)

The seven resource types Komodo syncs from TOML files (`docsite/docs/automate/sync-resources.md`):

```toml
# 1. Server (Periphery agent host)
[[server]]
name = "arm1-oci"
description = "Oracle Cloud ARM - Control Plane"
tags = ["location:oracle-london", "role:control-plane", "arch:arm64"]
[server.config]
address = ""                  # empty = outbound to Core (v2+ best practice)
region = "uk-london-1"
enabled = true
public_key = "MCowBQYDK2VuAyEA..."

# 2. Stack (Docker Compose project)
[[stack]]
name = "lakehouse"
description = "Unified lakehouse with Garage + Lakekeeper + Lance Namespace"
deploy = true
after = ["cognee-bunchloch"]  # cross-resource dep ordering (like docker compose depends_on)
tags = ["host:bunchloch", "tier:lakehouse", "type:data-platform"]
[stack.config]
server = "bunchloch"          # upstream uses 'server' (NOT 'server_id')
run_directory = "/opt/stacks/lakehouse"
file_paths = ["compose.yaml", "pangolin.yaml", "sidecar.yaml"]   # supports -f ... -f ...
git_provider = "github.com"
git_account = "my-user"
repo = "myorg/stacks"
branch = "main"
environment = """
DB_HOST = db.example.com
LOG_LEVEL = info
"""
auto_update = false           # auto redeploy on new image digest
poll_for_updates = false      # show update indicator only
send_alerts = true

# 3. Deployment (single container)
[[deployment]]
name = "test-logger-01"
deploy = true
after = ["some-build"]
[deployment.config]
server = "server-01"
image.type = "Build"           # tagged enum: Build | Image
image.params.build = "test_logger"
volumes = """/data/logs = /etc/logs"""
environment = """OTLP_ENDPOINT = [[OTLP_ENDPOINT]]"""

# 4. Procedure (multi-stage orchestration)
[[procedure]]
name = "nightly-backup"
[[procedure.config.stage]]
name = "Deploy all"
executions = [
  { execution.type = "DeployStack", execution.params.stack = "lakehouse" },
  { execution.type = "BatchDeployStackIfChanged", execution.params.pattern = "foo-* , \\^bar-.*$\\" },
]
# Schedule fields (Schedule fields, see automate/schedules):
[procedure.config]
schedule_format = "English"   # English | Cron
schedule = "Every day at 03:00"
schedule_enabled = true
schedule_timezone = "America/New_York"
schedule_alert = true
failure_alert = true

# 5. Resource Sync (THE GitOps primitive — declares which TOML files feed Core)
[[resource_sync]]
name = "storage-infrastructure"
[resource_sync.config]
git_provider = "git.cianfhoghlaim.ie"
repo = "cliste/bonneagar"
git_account = "cian"
branch = "main"
resource_path = [
  "bonneagar/komodo/procedures/auto-deploy-stacks.toml",
  "bonneagar/komodo/servers/servers.toml",
  "bonneagar/komodo/stacks/*.toml",
  # ... globs accepted
]
managed = true                # Core writes UI changes back to git
delete = false                # safety: don't delete resources not in Git

# 6. Variable / Secret (inline interpolation via [[KEY]])
[[variable]]
name = "OTLP_ENDPOINT"
value = "http://localhost:4317"
# Interpolation: SOME_ENV_VAR = [[OTLP_ENDPOINT]]  →  SOME_ENV_VAR = http://localhost:4317

# 7. User Group (RBAC)
[[user_group]]
name = "ops"
users = ["cian", "karamvirsingh98"]
all.Server = { level = "Write", specific = ["Attach", "Logs", "Inspect", "Terminal"] }
all.Build = "Execute"
permissions = [
  { target.type = "Server", target.id = "\\^(.+)-(.+)$\\", level = "Read" },
]
```

### Stack config field reference (from `docsite/docs/deploy/compose.md`)

| Field | Type | Default | Notes |
|:--|:--|:--|:--|
| `server` | string | — | Server name or ID; **upstream uses `server`, P2-12 spec uses `server_id`** |
| `file_paths` | array | `[]` | Compose files passed via `docker compose -f ... -f ...` |
| `run_directory` | string | — | Working directory for compose commands |
| `project_name` | string | Stack name | Override compose project name (match existing `docker compose ls`) |
| `environment` | string | `""` | Written to `.env` file; supports `[[KEY]]` interpolation |
| `extra_args` | string | `""` | Extra flags for `docker compose up` |
| `ignore_services` | array | `[]` | Services to exclude from health checks (e.g. init containers) |
| `git_provider` | string | `github.com` | Domain of git provider |
| `git_account` | string | — | Account for private repo access |
| `repo` | string | — | `owner/repo` format |
| `branch` | string | `main` | Branch to clone |
| `auto_update` | bool | `false` | Redeploy on newer image digests |
| `poll_for_updates` | bool | `false` | Show indicator + alert, no redeploy |
| `send_alerts` | bool | `true` | Alert on stack state changes |
| `links` | array | `[]` | Quick links in resource header |

### Schedule fields (from `docsite/docs/automate/schedules.md`)

| Field | Values | Default |
|:--|:--|:--|
| `schedule_format` | `English` \| `Cron` | `English` |
| `schedule` | string | `""` |
| `schedule_enabled` | bool | `true` |
| `schedule_timezone` | TZ identifier | Core's timezone |
| `schedule_alert` | bool | `true` |
| `failure_alert` | bool | `true` |

**Cron is 6-field (seconds required):** `second minute hour day month day-of-week`
- `0 0 3 * * ?` — every day at 03:00:00
- `0 */5 * * * ?` — every 5 minutes

**English examples:** `Every day at 03:00`, `Every Monday at 09:00`, `At midnight on the 1st and 15th of the month`.

### Procedure execution types (excerpt from `docsite/docs/automate/procedures.md`)

| Type | Purpose | Batch variant |
|:--|:--|:--|
| `RunBuild` / `DeployStack` / `Deploy` / `Deploy` | Single-resource actions | `BatchRunBuild`, `BatchDeployStackIfChanged` (wildcard `foo-*` and regex `\^bar-.*$\\` matching) |
| `RunProcedure` / `RunAction` | Sub-orchestration | — |
| `PullRepo` / `CloneRepo` | Git ops | — |
| `GlobalAutoUpdate` | Loop all `auto_update`/`poll_for_updates` resources | — |

### Webhook URL pattern (from `docsite/docs/automate/webhooks.md`)

```
https://<HOST>/listener/<AUTH_TYPE>/<RESOURCE_TYPE>/<ID_OR_NAME>/<EXECUTION>
```

| Component | Values |
|:--|:--|
| `AUTH_TYPE` | `github` (X-Hub-Signature-256 — also Gitea/Forgejo) \| `gitlab` (X-Gitlab-Token) |
| `RESOURCE_TYPE` | `build` \| `repo` \| `stack` \| `sync` \| `procedure` \| `action` |
| `EXECUTION` | Resource-specific (Stack: `/deploy` `/refresh`; Sync: `/sync` `/refresh`; Procedure: branch name or `/__ANY__`) |

### Variable interpolation (from `docsite/docs/configuration/variables.md`)

```toml
# Before interpolation
SOME_ENV_VAR = [[KEY_1]]
# After interpolation:
SOME_ENV_VAR = value_1
```

**Secret storage tiers (in order of security):**
1. UI Variable with `secret=true` — hidden in logs, admin-only
2. Core `secrets` block (`[secrets] KEY = "value"` in `core.config.toml`) — values never exposed by API
3. Periphery `secrets` block — distributed per-host, **never** travels over network
4. External (Hashicorp Vault) — for enterprise-grade secret management

### Cianfhoghlaim-side file inventory (`infrastructure/komodo/`)

| Sub-dir | Files | Purpose |
|:--|--:|:--|
| `servers/` | 1 (`servers.toml`) | 2 hosts only: `arm1-oci` + `bunchloch` (P2-12 spec mentions 3, including `cax41-hetzner`, but `cax41-hetzner` is not present) |
| `stacks/` | 30+ | One TOML per stack; `lakehouse` + `lakehouse-oci` is the canonical example (`stacks/storage-lakehouse.toml:17-64`) |
| `procedures/` | 73+ | Mix of `[[procedure]]` (true Komodo procedures) AND `[[action]]` blocks (Komodo Actions — TypeScript-free shell commands) AND drift: `procedures/storage-lakehouse.toml` is actually a stack definition with embedded `[[stack.procedures]]` health-check blocks, not a Komodo `[[procedure]]` |
| `resource-syncs/` | 1 (`storage-infrastructure.toml`) | The single GitOps pull-sync from Forgejo `cliste/bonneagar` |
| `sites/` | 0 (empty) | P2-12 spec did not mention this dir; it exists in filesystem but is unused |

**Top-level file:** `infrastructure/komodo/README.md` (orientation), no `variables.toml`.

### `servers.toml` actual content (`infrastructure/komodo/servers/servers.toml:1-44`)

- `arm1-oci` (Oracle Cloud ARM, London, 4 OCPU/24GB/200GB) — control plane: Pangolin, Komodo, Infisical, Garage, Beszel, Dozzle, Qdrant, Pocket-ID
- `bunchloch` (MacBook M4 Max, ~14 cores/48GB/local NVMe) — primary workloads: Memgraph, FalkorDB, Graphiti, LanceDB, Cognee, Langfuse, MLflow, LakeFS, Lakekeeper, OLake-UI, Convex, Crawl4AI

Both use `address = ""` (outbound to Core) — matches v2+ best practice. Both have explicit SPKI `public_key` fields (NOT the legacy v1 `passkey`).

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `KOMODO_BASE_URL` | `https://komodo.cianfhoghlaim.ie` | Locket |
| `KOMODO_API_KEY` | `infisical://dev-baile/komodo/api_key` | Locket |
| `KOMODO_API_SECRET` | `infisical://dev-baile/komodo/api_secret` | Locket |
| `KOMODO_WEBHOOK_SECRET` | `infisical://dev-baile/komodo/webhook_secret` | Locket (used for `/listener/github/*` HMAC validation) |
| `PERIPHERY_ROOT_DIRECTORY` | `/etc/komodo` | Systemd or container env |
| `PERIPHERY_CORE_ADDRESS` | `komodo.cianfhoghlaim.ie` | Per-host systemd unit |
| `PERIPHERY_CONNECT_AS` | `arm1-oci` \| `bunchloch` | Per-host systemd unit |
| `PERIPHERY_ONBOARDING_KEY` | `O-...` (one-shot, reusable) | Used only on first boot per host |
| `PERIPHERY_PORT` | `8120` | Default inbound port (only used in inbound mode) |
| `PERIPHERY_PRIVATE_KEY` | `file:${root_directory}/keys/periphery.key` | Default; auto-generated on first start |

## CCC anchors

**Found via CCC** (`bun run ccc:search "[[stack]]"` + `bun run ccc:search "resource_sync git_account branch"`):

| File | Line | Significance |
|:--|--:|:--|
| `infrastructure/QUADRANT-TO-STACK-MAP.md` | 62-65 | Confirms `komodo` stack runs on `arm1-oci + bunchloch` |
| `infrastructure/komodo/procedures/auto-deploy-stacks.toml` | 1538-1574 | **Second canonical `[[resource_sync]]`** (the "auto-deploy-stacks" variant) — not in `resource-syncs/`, embedded inside a procedure file. `resource_path` uses explicit per-file paths, not globs |
| `infrastructure/komodo/resource-syncs/storage-infrastructure.toml` | 1-37 | First canonical resource-sync with `managed = true` and glob patterns |
| `infrastructure/komodo/stacks/storage-lakehouse.toml` | 17-64 | Canonical stack TOML with `server_id` (P2-12 local convention — upstream Komodo uses `server`) |
| `infrastructure/komodo/procedures/croilar-stack-up.toml` | 1-47 | Canonical multi-stage `[[procedure]]` with `DeployStack` executions across 3 stages |
| `infrastructure/komodo/procedures/croilar-gitops-fullstack.toml` | 1-56 | Canonical chained `[[procedure.config.stages]]` calling other `[[procedure]]`s (`RunProcedure`) |
| `infrastructure/komodo/procedures/team-backup.toml` | 1-50 | Canonical `[[action]]` block — TypeScript-free shell command, scheduled pg_dump to Garage S3 |

Search terms used: `"[[stack]]"`, `"resource_sync git_account branch"`, `"server_id"`, `"file_paths"`, `"run_directory"`.

## Drift log

| Date | Event | Source |
|:--|:--|:--|
| 2025-09 | Initial Komodo deploy (single host) | P2-12 spec |
| 2025-12 | Added bunchloch as second host (workloads) | P2-12 spec |
| 2026-02 | Migrated from Komodo v1 to v2 (TOML-based config; PKI replaces passkeys; outbound Periphery replaces inbound) | `docsite/docs/releases/v2.0.0.md` |
| 2026-03 | Added procedures/ subdir (reusable deploy patterns) | P2-12 spec |
| 2026-04 | Onboarded cax41-hetzner as 3rd host (storage backups) | **P2-12 spec claim — NOT IN FILESYSTEM** (only `arm1-oci` + `bunchloch` exist) |
| 2026-06 | Added `infrastructure-audit` cron (weekly health check) | P2-12 spec |
| 2026-06-28 | v2.2.0 latest release (May 7 2026); Docusaurus-based docsite at `https://komo.do/docs/*` | `https://api.github.com/repos/moghtech/komodo` + `komo.do` fetch |

### Drift between P2-12 spec and actual filesystem

| P2-12 claim | Reality | Evidence |
|:--|:--|:--|
| `builder/builder.toml` exists | No `builder/` subdir | `ls infrastructure/komodo/` |
| `variables.toml` is a shared file | No `variables.toml`; vars live inline in each TOML | `ls infrastructure/komodo/`, `procedures/team-backup.toml:13-49` (inline shell vars) |
| 3 servers (arm1-oci + bunchloch + cax41-hetzner) | Only 2 servers (`arm1-oci` + `bunchloch`) | `servers/servers.toml:14-43` |
| Stack TOML uses `server_id = "..."` | Cianfhoghlaim uses `server_id`; **upstream Komodo uses `server`** (see `docsite/docs/deploy/compose.md` example) | `stacks/storage-lakehouse.toml:23,52` vs upstream docs |
| Stack TOML has `[stack.schedule]` block | No `schedule` field; schedules live on `[[procedure]]` only | `docsite/docs/deploy/compose.md` schema + upstream |
| Stack TOML has `tags = ["host:bunchloch", "tier:lakehouse", "type:data-platform"]` | Correct (matches upstream) | `stacks/storage-lakehouse.toml:20` |
| `infrastructure/komodo/procedures/storage-lakehouse.toml` is a Komodo `[[procedure]]` | It's a **`[[stack]]` definition** with `[[stack.depends_on]]` + `[[stack.procedures]]` (health-check shell snippets embedded in the stack) — NOT a Komodo Procedure | `procedures/storage-lakehouse.toml:26-47` (note `[[stack]]` not `[[procedure]]`) |
| `docs.komo.do/{install-script,stacks,procedures,variables,servers}` are real docs URLs | `docs.komo.do/*` is a placeholder returning a generic Rust sample. Real docs are at `https://komo.do/docs/{intro,setup,resources,deploy/compose,automate/procedures,automate/sync-resources,configuration/variables,automate/schedules,automate/webhooks,releases/v2.0.0}` | webfetch results |
| 4 sub-dirs (`servers, stacks, procedures, builder`) | 5 sub-dirs (`servers, stacks, procedures, resource-syncs, sites`) — `sites/` exists but is empty | `ls infrastructure/komodo/` |

## Anti-patterns (from upstream `docsite/docs/`)

1. **Don't put secrets in TOML files** — use `[[variable]]` with `secret=true`, or Core/Periphery `secrets` block, or external Vault.
2. **Don't run Komodo Core in a container on the same host as your workloads** — Core needs MongoDB/FerretDB and the Core API; Periphery runs on each host.
3. **Don't use `:latest` for Core/Periphery images** — v2 ships only Semver tags (`:2`, `:2.0`, `:2.0.0`). Use `:2` to stay current.
4. **Don't skip the `init: true` directive** — without it, zombie processes build up (called out explicitly in `releases/v2.0.0.md` upgrade guide).
5. **Don't use `delete = true` on a `[[resource_sync]]` in production** — drift deletes Core resources when a TOML file is removed; `delete = false` is the safe default.
6. **Don't run Periphery as a container when you can run it as systemd** — container mode has known issues with `/proc` mounting, Docker socket, and signal handling (`connect-servers.mdx` recommends systemd).
7. **Don't use legacy `passkey` auth** — replaced by SPKI public/private key pairs in v2; passkey was deprecated.
8. **Don't write long-running stateful logic in `[[action]]` TypeScript** — Actions are stateless; long workflows belong in `[[procedure]]` stages.

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Komodo version | v2.2.0+ (Semver `:2` tag) | PKI auth, outbound Periphery, Docusaurus docs |
| Install method | Systemd for Periphery; Docker Compose for Core | Avoids `/proc` + Docker socket issues with container Periphery |
| Auth (Core ↔ Periphery) | SPKI public/private key + Noise protocol handshake | Replaces legacy passkey; auto-rotation supported (`auto_rotate_keys = true`) |
| Connection mode | Outbound (Periphery → Core) | v2 best practice; survives inbound firewall rules; onboarding key one-shot, then auto-rotating pubkey |
| Stack config | TOML in git (`stacks/*.toml`) | Diffable, reviewable, resource-sync drives Core |
| Procedure reuse | Multi-file with `RunProcedure` chaining | Avoid mega-procedures; each `RunProcedure` is a stage boundary |
| Image pinning | Semver `:2` for Core/Periphery; pinned tags for stack images | Reproducibility, no surprise upgrades |
| Secrets | UI `secret=true` for shared; Core `secrets` block for global; Periphery `secrets` for host-local | Three-tier matching the blast radius |
| Resource Sync | `managed = true`, `delete = false`, single sync with globbed `resource_path` | Core writes UI changes back to git; safe from drift-deletes |
| Schedule format | `English` for humans; `Cron` (6-field with seconds) for precise | English converts via `english-to-cron` crate; Cron is the canonical format |
| Webhook auth | `github` (X-Hub-Signature-256) — works for Forgejo/Gitea too | Single auth type covers 90% of CI providers |

## §8 Refactor opportunities

1. **Rename `server_id` → `server` to match upstream.** Cianfhoghlaim uses `server_id` in 30+ stack TOMLs (`stacks/storage-lakehouse.toml:23,52`) but upstream Komodo v2 uses `server` (`docsite/docs/deploy/compose.md`). The `server_id` form is silently accepted by Core (Komodo is lenient with extra fields) but breaks copy-paste from upstream docs. A single sed across `infrastructure/komodo/**/*.toml` would fix it. Drift risk: LOW (Core accepts both), value: HIGH (fewer surprises when reading upstream docs).

2. **Split `procedures/storage-lakehouse.toml` into its two halves.** Currently it has BOTH `[[stack]] lakehouse` + `[[stack.depends_on]]` + `[[stack.procedures]]` health-check snippets AND a duplicate `[[stack]] lakehouse-oci`. This is a stack definition masquerading as a procedure file. Move the `[[stack]]` blocks to `stacks/storage-lakehouse.toml` (where a slightly different copy already lives) and turn the shell health-check snippets into real `[[procedure]] lakehouse-health` files in `procedures/lakehouse-health.toml`. Drift: MEDIUM, value: HIGH (single source of truth per file).

3. **Hoist the 73 `[[action]]` blocks into one `actions.toml`.** `procedures/team-backup.toml`, `procedures/croilar-image-rebuild.toml`, `procedures/dagster-unified.toml` etc. each contain inline `[[action]]` blocks (TypeScript-free shell commands). These would be cleaner if grouped under `actions/<domain>.toml`, mirroring the upstream pattern of separating actions from procedures. Drift: LOW (works either way), value: MEDIUM.

4. **Add a `variables.toml` (or `[[variable]]` ResourceSync) for shared registry URLs / image tags.** Currently the only variable pattern in Cianfhoghlaim is the inline `[[variable]]` block pattern (seen in upstream Komodo docs). A single file like `infrastructure/komodo/variables.toml` referenced from `resource-syncs/storage-infrastructure.toml` would give one place to bump `LAKEKEEPER_VERSION=0.9.x` → `0.10.x`. Drift: NONE (matches P2-12 spec), value: HIGH.

5. **Replace the duplicate `[[resource_sync]]` definitions.** `resource-syncs/storage-infrastructure.toml` AND `procedures/auto-deploy-stacks.toml:1538-1574` BOTH define `[[resource_sync]] name = "storage-infrastructure"` with overlapping `resource_path` arrays (one uses globs, one uses explicit per-file lists, both are correct). Pick one source of truth, delete the other. Drift: MEDIUM (Core warns about duplicate definitions), value: HIGH (eliminates sync-conflict ambiguity).

6. **Drop or document the empty `sites/` subdir.** `infrastructure/komodo/sites/` is empty but listed in `ls`. Either populate it (the upstream Komodo `Site` resource is for swarm monitoring) or add a `.gitkeep` + comment explaining its intended use. Drift: LOW, value: LOW.

7. **Refresh the P2-12 spec to reflect reality.** The spec's anti-patterns, decision matrix, and CCC anchors are largely accurate but contain 4 specific factual errors (builder/ subdir, variables.toml, 3 hosts including cax41-hetzner, docs.komo.do URLs). A short follow-up change would close the loop.

## Files to read next

`infrastructure/komodo/README.md` · `infrastructure/komodo/servers/servers.toml` · `infrastructure/komodo/stacks/storage-lakehouse.toml` · `infrastructure/komodo/procedures/croilar-gitops-fullstack.toml` · `infrastructure/komodo/procedures/croilar-stack-up.toml` · `infrastructure/komodo/procedures/auto-deploy-stacks.toml` (lines 1538-1574 for the embedded resource_sync) · `infrastructure/komodo/resource-syncs/storage-infrastructure.toml` · `.agents/skills/komodo/SKILL.md` · `.agents/skills/infrastructure-stacks/SKILL.md` · `moghtech/komodo` (Rust source — `client/`, `lib/`, `compose/`, `scripts/setup-periphery.py`) · `https://komo.do/docs/automate/sync-resources` (canonical GitOps reference) · `https://komo.do/docs/releases/v2.0.0` (v1→v2 upgrade guide)
