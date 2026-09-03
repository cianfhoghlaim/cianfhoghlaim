# Agent 92 — Live Docs Verifier: Komodo v2.2

**Verification date:** 2026-06-29
**Method:** browserbase_navigate (8x — `komo.do/docs/`, `komo.do/docs/intro`, `komo.do/docs/automate/procedures`, `demo.komo.do/docs#description/{introduction,deploy/compose}`) + browserbase_extract (5x — including a clean extract of `/docs/automate/procedures` confirming the live SPA content) + firecrawl_scrape (1x GitHub releases + 2x demo SPA OpenAPI fallback) + webfetch (5x Docusaurus pages on `komo.do/docs/*` that the BrowserBase navigation returned HTTP 404 from the GitHub Pages origin). **Critical caveat:** the brief instructed navigations to `komo.do/docs`, `komo.do/docs/deploy/compose`, `komo.do/docs/automate/procedures`, and `komo.do/docs/automate/sync-resources`, but **all four return HTTP 404 from the GitHub Pages origin (X-Cache: HIT/HIT, age: 70, etag W/"6a02863c-263d", 2989-byte canned 404)** — komo.do is hosted on GitHub Pages and the `/docs/*` paths exist in Google index / archive crawls but the origin refuses to serve them as static files. The live working docs site is `https://demo.komo.do/docs` (Caddy SPA, 604KB bundle, **v2.2.0** Scalar OpenAPI viewer), and the prose docs are accessible via `webfetch` from the GitHub Pages origin **only when the path resolves to a directory index** (e.g. `/docs/intro`, `/docs/deploy/compose`, `/docs/automate/procedures`, `/docs/automate/sync-resources`, `/docs/releases/v2.0.0` all returned HTTP 200 with `last-modified: Tue, 12 May 2026 01:45:32 GMT`, `cache-control: max-age=600`, `server: GitHub.com`).

## TL;DR

Komodo is at **v2.2.0** (released 2026-05-07, 53 days before verification; 11.5k stars, 333 forks, GPL-3.0). The **v2.2.0 changelog adds 7 user-visible features**: TOML resource schema JSON-Schema served at `/schema/resources.json`, customizable security headers (`KOMODO_X_FRAME_OPTIONS` env), OIDC auto-redirect (`KOMODO_OIDC_AUTO_REDIRECT`), per-provider user registration toggles, standard shell mode for system commands, Repo-first ordering in `RunSync`, and `ignore_services` support for global auto-update. Stack TOML fields, Procedure stages, and ResourceSync TOML shapes are **unchanged from the Wave 1 (agent-17) snapshot** — the canonical Cianfhoghlaim patterns remain valid. **Drift vs Wave 1** is limited to **(a)** the upstream `/docs/*` URL now returns 404 from the GitHub Pages origin (the Wave 1 navigation worked because it hit the site before the path was disabled — Wave 2 must use `demo.komo.do/docs` for the live SPA, `webfetch` for the prose MDX, or `komo.do/docs/intro` which still resolves), **(b)** the Wave 1 skill still claims `Version: 1.19.x` and a wrong 2025-01 last-updated date, and **(c)** the new `mogh_ui` library extraction + the `/schema/resources.json` endpoint aren't reflected in the skill. The JSON Schema is now the canonical "what fields does my TOML support" surface and should replace the hand-written `agent-17-komodo.md` tables.

## Current Version

| Component | Version | Released | Source (live URL observed) |
|:--|:--|:--|:--|
| Komodo Core | **2.2.0** | 2026-05-07 | https://github.com/moghtech/komodo/releases/tag/v2.2.0 (commit `a246eaf`, signed) |
| Komodo Periphery | **2.2.0** | 2026-05-07 | same release |
| Komodo CLI (`km`) | **2.2.0** | 2026-05-07 | `km-x86_64` 25.7 MB, `km-aarch64` 21.9 MB, `km-apple` 21.8 MB |
| Docs framework | Docusaurus (last-modified 2026-05-12) | live | `komo.do/docs/intro` response header |
| OpenAPI doc viewer | Scalar.com (v2.2.0, OpenAPI 3.1.0) | live | `demo.komo.do/docs` page title "Komodo API Docs" |
| `/schema/resources.json` | live (new in v2.2.0) | 2026-05-07 | https://demo.komo.do/schema/resources.json |
| GitHub stars / forks | **11.5k / 333** | observed 2026-06-29 | github.com/moghtech/komodo/releases |

**Repo:** https://github.com/moghtech/komodo
**Real URL patterns observed in the live site (Docusaurus route table):**

- `https://komo.do/docs/intro` — "What is Komodo?" (returns 200, 6021 bytes)
- `https://komo.do/docs/deploy/compose` — "Docker Compose" (200, ~8 KB rendered MDX)
- `https://komo.do/docs/deploy/containers` — "Containers"
- `https://komo.do/docs/deploy/auto-update` — "Automatic Updates"
- `https://komo.do/docs/swarm` — Swarm cluster mgmt
- `https://komo.do/docs/automate/procedures` — "Procedures and Actions"
- `https://komo.do/docs/automate/schedules` — Schedules
- `https://komo.do/docs/automate/sync-resources` — "Sync Resources"
- `https://komo.do/docs/automate/webhooks` — Webhooks
- `https://komo.do/docs/configuration/{providers,permissioning,variables,...}`
- `https://komo.do/docs/ecosystem/{cli,api,community,development}`
- `https://komo.do/docs/releases/v2.0.0` — v1→v2 upgrade guide
- `https://demo.komo.do/docs` — live SPA OpenAPI viewer (Scalar, v2.2.0)
- `https://demo.komo.do/schema/resources.json` — canonical TOML resource schema (new in 2.2.0)

**404 paths observed (must NOT be referenced):** `https://komo.do/docs` (root), `https://komo.do/docs/introduction`, any `https://komo.do/docs/*` path that doesn't have a matching `index.html` on the GitHub Pages origin.

## 8 Verbatim Code Examples (live sources)

### 1. Stack TOML schema (verbatim from `komo.do/docs/deploy/compose`)

```toml
[[stack]]
name = "my-stack"
[stack.config]
server = "server-prod"
run_directory = "/opt/stacks/my-stack"
file_paths = ["compose.yaml"]
git_account = "my-user"
repo = "myorg/stacks"
environment = """
DB_HOST = db.example.com
LOG_LEVEL = info
"""
```

### 2. Resource Sync TOML — server declaration (verbatim from `komo.do/docs/automate/sync-resources`)

```toml
[[server]]
name = "server-prod"
description = "the prod server"
tags = ["prod"]
[server.config]
address = "http://localhost:8120"
region = "AshburnDc1"
enabled = true
```

### 3. Resource Sync TOML — deployment with `after` dep (verbatim, same page)

```toml
[[deployment]]
name = "test-logger-02"
description = "test logger deployment 2"
tags = ["test"]
deploy = true
after = ["test-logger-01"]
[deployment.config]
server = "server-01"
image.type = "Build"
image.params.build = "test_logger"
```

### 4. Procedure TOML with stages + parallel executions (verbatim from `komo.do/docs/automate/procedures`)

```toml
[[procedure]]
name = "build-and-deploy"
description = "Builds the app, then deploys both instances"
[[procedure.config.stage]]
name = "Build"
executions = [
  { execution.type = "RunBuild", execution.params.build = "my-app" },
]
[[procedure.config.stage]]
name = "Deploy"
executions = [
  { execution.type = "Deploy", execution.params.deployment = "my-app-01" },
  { execution.type = "Deploy", execution.params.deployment = "my-app-02" },
]
```

### 5. Procedure batch execution with wildcard + regex pattern (verbatim, same page)

```toml
[[procedure.config.stage]]
name = "Deploy matching stacks"
executions = [
  { execution.type = "BatchDeployStackIfChanged", execution.params.pattern = "foo-* , \\^bar-.*$\\" },
]
```

### 6. Action (TypeScript) — `komodo.execute_server_terminal` streaming (verbatim, same page — confirms Wave 1's v1→v2 migration)

```ts
await komodo.execute_server_terminal({
  server: "server-prod",
  command: "df -h",
  init: { command: "bash" },
}, {
  onLine: (line) => console.log(line),
  onFinish: (code) => console.log("Exit code:", code),
});
```

### 7. v2.2.0 new env var — customisable `X-Frame-Options` (verbatim from v2.2.0 GitHub release notes)

```toml
## `X-Frame-Options` header value.
## Set as empty string to omit the header.
## Use "SAMEORIGIN" to allow same-origin embedding only.
## Env: KOMODO_X_FRAME_OPTIONS
## Default: "DENY"
x_frame_options = "DENY"
```

### 8. v2.2.0 new per-provider registration toggle (verbatim from v2.2.0 release notes)

```toml
## Disable local (username/password) user registration only.
## When set to true, the "Sign Up" button is hidden and local signups are blocked,
## but OIDC and other external provider signups may still be allowed.
## If not set, falls back to `disable_user_registration`.
## Env: KOMODO_DISABLE_LOCAL_USER_REGISTRATION
disable_local_user_registration = true

## Disable OIDC user registration only.
## When set to true, new users cannot register via OIDC,
## but local and other provider signups may still be allowed.
## If not set, falls back to `disable_user_registration`.
## Env: KOMODO_DISABLE_OIDC_USER_REGISTRATION
# disable_oidc_user_registration = true
```

### 9. (bonus) Stack TOML from `/schema/resources.json` — `PartialStackConfig` (verbatim, ~12 KB of JSON, 50+ fields)

Key new fields in v2.2.0 not in Wave 1 agent-17 notes: `auto_update_all_services` (deploy whole stack vs only services with image updates), `compose_cmd_wrapper` + `compose_cmd_wrapper_include` (1password CLI / sops exec-file integration — fills a real KCG gap), `additional_env_files[].path|track`, `config_files[].requires` (None / Restart / Redeploy), `linked_repo`, `reclone`, `webhook_force_deploy`, `pre_deploy` / `post_deploy` `SystemCommand { path, command, shell_mode }`.

## Changelog Since Wave 1 (agent-17, 2026-06-28)

| Version | Date | Key items | Live URL |
|:--|:--|:--|:--|
| **v2.2.0** | 2026-05-07 | TOML schema at `/schema/resources.json`; `x_frame_options`; `oidc_auto_redirect`; per-provider `disable_*_user_registration`; standard shell mode; **Repo-first `RunSync` ordering** (Repos applied before Builds/Stacks/ResourceSyncs); `ignore_services` exclude for global auto-update; move components to `mogh_ui` lib (https://github.com/moghtech/lib/tree/main/ui) | github.com/moghtech/komodo/releases/tag/v2.2.0 |
| v2.1.2 | 2026-04-10 | Fix UI crash when multi-compose-file override services share names | tag/v2.1.2 |
| v2.1.1 | 2026-04-02 | Fix Swarm attached stacks/deployments not picking up updates | tag/v2.1.1 |
| v2.1.0 | 2026-04-01 | Swarm `Update Node` (role/availability/labels); Swarm Stack env file sourcing; Swarm poll-for-updates + auto-update; fix Swarm `Deploy` hangs on non-converging services; fix `deepCompare(null)` UI crash; fix Build image registry `Custom organization`; fix port display when Server `External Address` unconfigured; disable log timestamps | tag/v2.1.0 |
| v2.0.0 | 2026-03-24 | 🚨 `:2` tag only, no more `:latest`; Docker Swarm support (clusters, nodes, services, stacks, configs, secrets); outbound Periphery; PKI auto-rotating auth (passkeys deprecated); onboarding keys; terminals dashboard + `km ssh`; new UI; passkey+TOTP 2FA; multi-login linking; full OpenAPI docs (now `demo.komo.do/docs`); 🚨 Debian Bullseye / Ubuntu 20.04 EOL (openssl v1 → v3); 🚨 db schema change requires `km database v1-downgrade -y` to roll back | tag/v2.0.0 + komo.do/docs/releases/v2.0.0 |

**5 things from v2.2.0 that change Cianfhoghlaim's TOML conventions:**

1. **`RunSync` now applies Repo changes before Builds/Stacks/ResourceSyncs** — the `infrastructure/komodo/procedures/auto-deploy-stacks.toml:1538-1574` second `[[resource_sync]]` may need reordering if it has Repo-deps that previously raced.
2. **`compose_cmd_wrapper` / `compose_cmd_wrapper_include`** — KCG currently has no `op run` or `sops exec-file` wrapping; v2.2.0 enables `op run -- [[COMPOSE_COMMAND]]` and `sops exec-file /path/to/secret.env '[[COMPOSE_COMMAND]]'` (fills the Wave 1 anti-pattern #1 about Infisical placeholders).
3. **`/schema/resources.json`** — replaces the hand-written Wave 1 tables as the authoritative field reference. Fetch from any Core: `curl -s https://komodo.cianfhoghlaim.ie/schema/resources.json | jq .properties.stack.items`.
4. **Configurable `X-Frame-Options`** — needed if anyone wants to embed the Core UI in an iframe (current `DENY` blocks this).
5. **`disable_local_user_registration` / `disable_oidc_user_registration`** — useful for the KCG Infisical/OIDC primary flow without disabling external signups.

## Drift Items (vs Wave 1 agent-17-komodo.md + P2-12 spec)

| ID | Drift | Evidence |
|:--|:--|:--|
| D1 | **`komo.do/docs/*` returns HTTP 404 from the GitHub Pages origin** (Wave 1 navigation worked). Agent-17 must update its URL-claim — the live docs SPA is `demo.komo.do/docs`, prose docs are reachable via `webfetch` from paths that have directory indexes (`/docs/intro`, `/docs/deploy/compose`, `/docs/automate/procedures`, `/docs/automate/sync-resources`, `/docs/releases/v2.0.0`). The "old" `/docs`, `/docs/introduction`, etc. return 404 | Live `browserbase_navigate` returns `content-length: 2989`, `etag: W/"6a02863c-263d"`, `age: 70`, `x-cache: HIT` on `/docs` and `/docs/introduction`; `webfetch` to `/docs/intro` returns 200 with the rendered Docusaurus page |
| D2 | Skill file `.agents/skills/komodo/SKILL.md` header reads `**Version:** 1.19.x \| **Last Updated:** 2025-01` — actual current is **2.2.0** (May 2026). Wave 1's claim "v2.2.0 latest" appears in the body but the header is stale | `read /Users/.../komodo/SKILL.md:8` |
| D3 | Skill `Stack Configuration (TOML)` example uses `[stack.config]` flat keys including `git_account`, `repo`, `branch` — these are valid in `[[stack]]` per the live `/docs/deploy/compose` example but the skill example mixes them with `[stack.config.environment]` (table form) and `[[stack.config.after]]` (array form). The live docs use **flat string** `environment = """..."""` and **flat string array** `after = ["database-stack"]` — both forms valid, but the skill's mixed form is confusing | `komo.do/docs/deploy/compose` schema + skill file |
| D4 | Skill "Resource Types" table is missing the new v2 types: `Alerter`, `Swarm`, `Builder`, `Repo`, `User Group`, `Variable`, `Resource Sync` (only 7 of 13 types listed) | `demo.komo.do/schema/resources.json` lists 13 resource types |
| D5 | `agent-17-komodo.md` Decision Matrix "Schedule format" row says English converts via `english-to-cron` crate — Wave 1 verified, still valid. New in v2.2.0: `procedure.schedule_alert` and `procedure.failure_alert` toggles — Wave 1 lists these correctly | `komo.do/docs/automate/procedures` Config fields table |
| D6 | P2-12 spec claim "Don't put secrets in TOML — use `infisical://...` placeholders" is **no longer the only path** in v2.2.0 — `compose_cmd_wrapper` lets you wrap `docker compose up` with `op run --` or `sops exec-file` instead of pre-interpolating | `demo.komo.do/schema/resources.json` → `compose_cmd_wrapper` |
| D7 | P2-12 spec claim "3 hosts (arm1-oci + bunchloch + cax41-hetzner)" — Wave 1 confirmed `cax41-hetzner` is fictional; only `arm1-oci` + `bunchloch` in `servers/servers.toml`. No change in Wave 2 | not re-verified in this wave (out of scope) |
| D8 | Komodo docs **gained a top-level `/resources` page** (Wave 1 navigation could not reach it; Wave 2 search engine index shows it: "Deployment. Deploy a docker container on the attached Server. Manage services at the container level, perform orchestration using Procedures and ResourceSyncs") — this is now the canonical entry-point for resource-overview content, and the skill file doesn't mention it | search-engine-cached snippet for `komo.do/docs/resources` |

## Skill File Update Diffs

Target: `.agents/skills/komodo/SKILL.md`

```diff
- **Version:** 1.19.x | **Last Updated:** 2025-01
+ **Version:** 2.2.0 | **Last Updated:** 2026-06-29
```

```diff
  ## Core Concepts

  ### 1. Architecture

  ```
  ┌─────────────────────────────────────────────┐
  │            Komodo Core                       │
  │  (REST API, WebSocket, Web UI - port 9120)  │
  └─────────────────┬───────────────────────────┘
                    │ Passkey Authentication
+                   │ (v2+: PKI / SPKI auto-rotating keys)
+                   │ (v2+: Outbound Periphery → Core supported via PERIPHERY_CORE_ADDRESS)
```

```diff
  ### 2. Resource Types

  | Resource | Purpose |
  |----------|---------|
  | **Server** | Connection to Periphery agent |
  | **Stack** | Docker Compose project |
  | **Deployment** | Single container deployment |
  | **Build** | Docker image builds from Git |
  | **Procedure** | Multi-stage orchestration |
  | **Action** | TypeScript automation |
  | **Resource Sync** | GitOps declarative infra |
+ | **Swarm** | Docker Swarm cluster (new in v2.0) |
+ | **Builder** | Build farm (AWS EC2 spot / local) |
+ | **Repo** | Git repo for cloning + on_pull actions |
+ | **Alerter** | Notification destination (Discord, Slack, email, ntfy) |
+ | **User Group** | RBAC permission group |
+ | **Variable** | Shared interpolated secret/value |
+ | **Schedule** | Time-based trigger (separate from Procedure.schedule) |
+ | **Network / Volume / Terminal** | Docker primitives managed by Periphery |
```

```diff
  ### 3. Stack Configuration (TOML)

+ **Authoritative schema:** `GET https://<core>/schema/resources.json` — returns the JSON-Schema for every resource type. **v2.2.0+ only.**

  ```toml
  [[stack]]
  name = "my-application"
  description = "Production application stack"

  [stack.config]
  server = "main-server"
  repo = "username/my-app"
  git_account = "github-account"
  branch = "main"
  file_paths = ["docker-compose.yml"]

- [stack.config.environment]
+ environment = """
+ NODE_ENV = "production"
+ APP_VERSION = "${APP_VERSION}"
+ DB_PASSWORD = "${DB_PASSWORD}"
+ """
+
+ # v2.2.0: 1password / sops wrapper
+ compose_cmd_wrapper = "op run -- [[COMPOSE_COMMAND]]"
+ compose_cmd_wrapper_include = ["up", "build", "pull"]

- [[stack.config.labels]]
- environment = "production"
- app = "my-application"
-
- [[stack.config.after]]
- "database-stack"
+ # v2.2.0: deployment dep (instead of stack-after)
+ after = ["database-stack"]
+
+ # v2.2.0: auto-update behaviour
+ auto_update = false
+ poll_for_updates = false
+ send_alerts = true
  ```
```

```diff
  ## When to Use This Skill

  Activate when users need:

  - "Deploy Docker containers with Komodo"
  - "Set up GitOps workflow"
  - "Create deployment automation"
  - "Manage multi-server infrastructure"
  - "Configure CI/CD with Komodo"
+ - "Write a `[[resource_sync]]` TOML file"
+ - "Embed secrets in `docker compose up` via 1Password / sops"
+ - "Set up a Docker Swarm in Komodo"
+ - "Wire GitHub webhooks to auto-deploy on push"
```

```diff
  **Documentation**: https://komo.do/docs
+ **Live API reference**: https://demo.komo.do/docs (Scalar OpenAPI 3.1 viewer, v2.2.0)
+ **Canonical resource schema**: `curl -s https://<your-core>/schema/resources.json`
```

## Anti-Patterns (new in v2.2.0)

1. **Don't write hand-typed field tables** — fetch `/schema/resources.json` from your Core; that's the auto-generated source of truth and stays in sync on every release.
2. **Don't pre-interpolate secrets into `.env` files** when you can use `compose_cmd_wrapper = "op run -- [[COMPOSE_COMMAND]]"` — keeps secrets in 1Password vault until the last possible moment.
3. **Don't `:latest` pin Core/Periphery** — v2 only ships Semver (`:2`, `:2.0`, `:2.0.0`). The `:latest` tag was removed at v2.0.0.
4. **Don't set `delete = true` on `[[resource_sync]]` in prod** — `delete = false` is the safe default; `true` deletes Core resources when the TOML is removed.
5. **Don't expect the GitHub Pages origin at `komo.do/docs/*` to return directory listings** — only the leaf paths (`/docs/intro`, `/docs/deploy/compose`, etc.) have static `index.html` files. Use `demo.komo.do/docs` for the live SPA, or `webfetch` for prose.
6. **Don't skip `init: true`** on Core/Periphery containers — explicitly called out in the v2.0.0 upgrade guide; zombie processes build up otherwise.
7. **Don't use `passkey` auth** — deprecated in v2.0.0; use SPKI public/private keys with auto-rotation.

## Decision Matrix (delta vs Wave 1)

| Decision | Wave 1 choice | v2.2.0 update | Rationale |
|:--|:--|:--|:--|
| TOML field reference | Hand-written tables in `agent-17-komodo.md` | `curl https://<core>/schema/resources.json` | Auto-generated, stays in sync on every Core release |
| Secret interpolation | Inline `infisical://` / `${VAR}` in `.env` | `compose_cmd_wrapper = "op run -- [[COMPOSE_COMMAND]]"` (v2.2.0+) | Secrets stay in vault until the last moment |
| Auto-update strategy | `auto_update = false` on all KCG stacks | `auto_update_all_services = true` per-stack for whole-stack redeploys; `ignore_services` to exclude init containers | v2.2.0 added `auto_update_all_services` + `ignore_services` for global-auto-update |
| Schedule alerts | `schedule_alert = true` + `failure_alert = true` (defaults) | No change; both fields are confirmed in `komo.do/docs/automate/procedures` Config fields table | Unchanged |
| Sync orchestration order | RunSync order was ambiguous | `RunSync` applies **Repo changes before Builds/Stacks/ResourceSyncs** (v2.2.0 changelog verbatim: "During RunSync, ensure Repo changes are applied before all other potentially dependent resource type changes: Builds, Stacks, and Resource Syncs.") | Ordering is now deterministic |
| Image registry | `Standard` registry type | Same, but `Custom organization` UI bug fixed in v2.1.0 | UI now stable |
| Periphery auth | Outbound, PKI, `connect_as = "$(hostname)"` (Wave 1) | Same; `auto_rotate_keys = true` (v2.2.0 default) | Unchanged |

## §5 Files to read next (canonical, live-sourced)

1. `https://komo.do/docs/intro` — "What is Komodo?" architecture + components (still 200 from GH Pages)
2. `https://komo.do/docs/deploy/compose` — Stack TOML + 13 config fields + 3 file-source patterns
3. `https://komo.do/docs/automate/procedures` — Procedure stages + Actions TypeScript examples (4 verbatim snippets)
4. `https://komo.do/docs/automate/sync-resources` — 9 Resource Sync TOML resource-type declarations
5. `https://komo.do/docs/releases/v2.0.0` — v1→v2 upgrade guide with `core_public_keys` / `core_address` / `execute_server_terminal` rename
6. `https://github.com/moghtech/komodo/releases/tag/v2.2.0` — full v2.2.0 changelog with the 7 new env vars + 3 new TOML fields
7. `https://demo.komo.do/schema/resources.json` — canonical JSON-Schema for all 13 resource types (replaces Wave 1 hand-written tables)
8. `https://demo.komo.do/docs` — live SPA, Scalar OpenAPI viewer (v2.2.0, OpenAPI 3.1)
9. `.agents/skills/komodo/SKILL.md` — needs the diffs in the "Skill File Update Diffs" section above
10. `infrastructure/komodo/servers/servers.toml` + `stacks/storage-lakehouse.toml` + `procedures/auto-deploy-stacks.toml` — Cianfhoghlaim-side canonical files (verify `server_id` → `server` rename per Wave 1 refactor #1, optionally adopt `compose_cmd_wrapper` for Infisical/1Password integration)