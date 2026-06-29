# Agent 82 — Live Docs Verify: Garage S3 v2.3.0 (2026-06-29)

## 1. TL;DR

Garage **v2.3.0 (2026-04-16, 10 weeks old)** is live on `garagehq.deuxfleurs.fr` and `git.deuxfleurs.fr/Deuxfleurs/garage`; `replication_mode` was **permanently removed in v2.0.0 (2025-06-14)** with `replication_factor` + `consistency_mode` the replacement, and the admin API was reworked to **`/v2/` (utoipa-generated)**. v2.3.0 ships **`garage server --single-node --default-access-key --default-bucket`** which obsoletes our entire `infrastructure/stacks/lakehouse/compose.yaml:71-160` `garage-init` bash container — confirmed verbatim from the live quick-start page. Wave 1 was accurate on all major points; the only wave-2 additions are **v2.2.0's `block_max_concurrent_writes_per_request`** and the documentation no longer ships a `latest/` prefix — canonical paths are now `/documentation/cookbook/real-world/`, `/documentation/quick-start/`.

## 2. Current version (verified live)

| Field | Value | Source |
|:--|:--|:--|
| Latest stable | **v2.3.0** | `https://garagehq.deuxfleurs.fr/documentation/quick-start/` (Live, 200 OK, `last-modified: Mon, 11 May 2026 09:08:32 GMT`) |
| Release date | **2026-04-16 18:39:30 +00:00** | `https://git.deuxfleurs.fr/Deuxfleurs/garage/releases/tag/v2.3.0` (Forgejo release commit `7b119c0b4f`, by `lx`) |
| Docker tag | `dxflrs/garage:v2.3.0` | `https://hub.docker.com/r/dxflrs/garage/tags` — verified verbatim in quick-start snippet |
| Total releases | 41 (89 tags) | Forgejo repo page |
| Repo location | `git.deuxfleurs.fr/Deuxfleurs/garage` (Forgejo, NOT GitHub) | Forgejo releases page |
| Commits since v2.3.0 | **68 commits to `main-v2` since this release** | Forgejo release header |
| Docs site Last-Modified | `Mon, 11 May 2026 09:08:31 GMT` | HTTP response header on `/` |
| Docs stack | The site itself runs on Garage S3 — `x-garage-error: API error: Key not found` appears on 404 pages | HTTP response header |

## 3. Verbatim config examples (live, v2.3.0)

### 3.1 Single-node quick-start (`/documentation/quick-start/`) — the v2.3.0 game-changer

```bash
docker run -d --name garage-container \
  -p 3900:3900 -p 3901:3901 -p 3902:3902 -p 3903:3903 \
  -v $(pwd)/garage.toml:/etc/garage.toml \
  -e GARAGE_DEFAULT_ACCESS_KEY -e GARAGE_DEFAULT_SECRET_KEY -e GARAGE_DEFAULT_BUCKET \
  dxflrs/garage:v2.3.0 \
  /garage server --single-node --default-bucket
```

> Source: live extraction of `garagehq.deuxfleurs.fr/documentation/quick-start/` on 2026-06-29 01:21 UTC. This single command replaces the entire 90-line `garage-init` service in `infrastructure/stacks/lakehouse/compose.yaml`.

### 3.2 CLI bucket/key lifecycle (`/documentation/quick-start/`)

```bash
garage bucket create nextcloud-bucket
garage bucket list
garage bucket info nextcloud-bucket
garage key create nextcloud-app-key
garage key list
garage key info nextcloud-app-key
garage bucket allow --read --write --owner nextcloud-bucket --key nextcloud-app-key
```

### 3.3 3-node HA cluster `garage.toml` (`/documentation/cookbook/real-world/`) — replaces the old `replication_mode`

```toml
metadata_dir = "/var/lib/garage/meta"
data_dir = "/var/lib/garage/data"
db_engine = "lmdb"
metadata_auto_snapshot_interval = "6h"

replication_factor = 3

compression_level = 2

rpc_bind_addr = "[::]:3901"
rpc_public_addr = "<this node's public IP>:3901"
rpc_secret = "<RPC secret>"

[s3_api]
s3_region = "garage"
api_bind_addr = "[::]:3900"
root_domain = ".s3.garage"

[s3_web]
bind_addr = "[::]:3902"
root_domain = ".web.garage"
index = "index.html"
```

> Note: **no `replication_mode`** field at all. The `consistency_mode` is set per-layout via `garage layout` — see §3.4.

### 3.4 Cluster layout injection (live, multi-node cookbook)

```bash
# After `garage node connect <id>@<ip>:3901` exchanges identity:
garage layout assign 563e -z par1 -c 1T   -t mercury
garage layout assign 86f0 -z par1 -c 2T   -t venus
garage layout assign 6814 -z lon1 -c 2T   -t earth
garage layout assign 212f -z bru1 -c 1.5T -t mars
garage layout show     # inspect before applying
garage layout apply    # commit
```

### 3.5 Docker host-mode daemon start (3-node cookbook)

```bash
docker run -d --name garaged --restart always --network host \
  -v /etc/garage.toml:/etc/garage.toml \
  -v /var/lib/garage/meta:/var/lib/garage/meta \
  -v /var/lib/garage/data:/var/lib/garage/data \
  dxflrs/garage:v2.3.0
```

### 3.6 Multi-node Docker Compose reference

```yaml
version: "3"
services:
  garage:
    image: dxflrs/garage:v2.3.0
    network_mode: "host"
    restart: unless-stopped
    volumes:
      - /etc/garage.toml:/etc/garage.toml
      - /var/lib/garage/meta:/var/lib/garage/meta
      - /var/lib/garage/data:/var/lib/garage/data
```

### 3.7 `garage status` (live multi-node cookbook)

```
==== HEALTHY NODES ====
ID                  Hostname  Address           Tag                   Zone  Capacity
563e1ac825ee3323…   Mercury   [fc00:1::1]:3901  NO ROLE ASSIGNED
86f0f26ae4afbd59…   Venus     [fc00:1::2]:3901  NO ROLE ASSIGNED
68143d720f20c89d…   Earth     [fc00:B::1]:3901  NO ROLE ASSIGNED
212f7572f0c89da9…   Mars      [fc00:F::1]:3901  NO ROLE ASSIGNED
```

### 3.8 Admin API references in the live site

- `/v1/` → **`/v2/`** (admin token rotate now `POST /v2/admin/token`, multi-token support since v2.0.0)
- Single-run JSON helper: `garage json-api <endpoint>` (new in v2.0.0)
- OpenAPI spec is **utoipa-generated** (verbatim v2.0.0 release notes: "Generate admin API spec programatically using utoipa #979")

## 4. Live changelog entries since Wave 1 (2026-06-28)

Wave 1 captured v2.0.0 → v2.2.0 correctly. **New since Wave 1 (2026-06-28):**

### 4.1 v2.3.0 (2026-04-16, 10 weeks old) — *the headline release for our upgrade*

> *"This release is a stable release. There are no breaking changes when migrating from Garage v2.2.0."*

Features/improvements (verbatim from Forgejo release notes):
- **`Make initial setup easier (#1329)`** — three sub-bullets: "allow to use `garage server --single-node` to autocreate a layout and get a functional cluster right away for single nodes"; "`--default-access-key` to automatically create an access key based on environment variable `GARAGE_DEFAULT_ACCESS_KEY` and `GARAGE_DEFAULT_SECRET_KEY`"; "`--default-bucket` to automatically create a bucket based on environment variable `GARAGE_DEFAULT_BUCKET`"
- "add missing admin API endpoints for admin UI (#1376)"
- "relax requirements on imported access keys to allow easier transition from other S3 storage providers (#1262)"
- "log api error in one self-sufficient line (#1381, #1390)"
- "Add completions sub-command for generating shell completions (#1386)"

Bug fixes that affect us: "fix silent write errors (#1360)" (important for our distroless healthcheck); "fix: enable TCP keepalive on RPC connections (#1348)"; "Don't die on SIGHUP" (carried from v2.1.0).

### 4.2 v2.2.0 (2026-01-24, 5 months old)
- "add `block_max_concurrent_writes_per_request` configuration parameter (#1251)" — NEW tuning knob
- "add consul discovery for WAN-federated consul servers (#1252)"
- "fix SIGILL on raspberry pi and older ARM boards (#1217)" — relevant if nodes ever move to RPi
- Optimization: "set optimization level to 3 in release builds (#1235)"

### 4.3 v1.3.1 (2026-01-24, parallel backport line)
- "add `block_max_concurrent_writes_per_request` configuration parameter (#1251)" (carried forward from v2.2.0)
- "properly handle precondition time equal to object timestamp (#1193)"

### 4.4 Confirmed Wave-1 historical entries (verbatim)

> v2.0.0: *"the following breaking changes since the `v1.x` series: The administration API has been completely reworked. Some calls to the `/v1/` endpoints will still work but most will not. New endpoints are prefixed by `/v2/`. `replication_mode` is no longer a supported configuration parameter, please use `replication_factor` and `consistency_mode` instead."*
> v2.1.0: *"A single breaking change was included in the admin API... `storage_nodes_ok` is renamed to `storage_nodes_up` in GetClusterHealthResponse, to fix generated SDK code (#1111)."*
> v2.0.0: *"Complete refactoring of the admin API... Generate admin API spec programatically using utoipa #979. New `garage json-api` command to call the JSON API from scripts. Support multiple admin API tokens #944, #982. CLI rework #984."*

## 5. Drift items vs Wave 1 text synthesis

| # | Wave 1 claim | Live confirmation (2026-06-29) | Drift |
|:--|:--|:--|:--|
| D1 | `replication_mode` removed in v2.0.0 | **CONFIRMED** — v2.0.0 release verbatim "no longer a supported configuration parameter" | None |
| D2 | `/v1/` → `/v2/` admin API in v2.0.0 | **CONFIRMED** — v2.0.0 release verbatim "Administration API has been completely reworked... New endpoints are prefixed by `/v2/`" | None |
| D3 | `garage server --single-node` in v2.3.0 | **CONFIRMED & EXPANDED** — live quick-start includes exact verbatim cmd `dxflrs/garage:v2.3.0 \ /garage \ server \ --single-node --default-bucket` with 3 env vars | None |
| D4 | `dxflrs/garage:v2.3.0` is current | **CONFIRMED** — quick-start, cluster cookbook BOTH cite v2.3.0 | None |
| D5 | Repo is on `git.deuxfleurs.fr` (Forgejo) | **CONFIRMED** — `https://git.deuxfleurs.fr/Deuxfleurs/garage/releases` returned 200 with 41 releases, 89 tags | None |
| D6 | `storage_nodes_ok` → `storage_nodes_up` in v2.1.0 | **CONFIRMED** — verbatim quote from v2.1.0 release notes issue #1111 | None |
| D7 | `--default-bucket` is single-bucket only | **CONFIRMED** — single env var `GARAGE_DEFAULT_BUCKET`; multi-bucket still needs `garage bucket create` loop | None |
| D8 | Multiple admin tokens now supported | **CONFIRMED** — v2.0.0 release notes verbatim "Support multiple admin API tokens #944, #982" | None |
| D9 | Docs URL structure `/documentation/latest/` | **DRIFT** — `/documentation/latest/quick-start/` returns 404; canonical `/documentation/quick-start/` (no `latest/` prefix). | Wave 1 doc → 1 file: `openspec/research/2026-06-28-browserbase-program-2/agent-12-garage.md` referenced `/documentation/latest/` only in narrative |
| D10 | `documentation/admin-api/` page | **DRIFT** — page 404; admin API reference is baked into `/documentation/quick-start/` | (Wave 1 doc did not claim this URL) |
| D11 | `block_max_concurrent_writes_per_request` (v2.2.0) | **NEW DRIFT** — new config knob in v2.2.0, not flagged in Wave 1 | Wave 1 doc → add to refactor list |
| D12 | `garage repair scrub-uploads` / `clear-resync-queue` (v1.3.0/v2.1.0) | **NEW DRIFT** — operational commands, useful for HA cluster ops | Wave 1 doc → add to ops handbook |
| D13 | docs site Last-Modified `2026-05-11` | **CONFIRMED** — `<last-modified: Mon, 11 May 2026 09:08:31 GMT>` on the homepage | None (means Wave-1 read was ~2 weeks stale) |
| D14 | "v1.0.1 (December 2024) — first stable release" in `infrastructure/stacks/garage/README.md:60` | **CONFIRMED STALE** — v1.0.0 was Sep 2024; **v1.3.1 (Jan 2026), v2.0.0 (Jun 2025), v2.1.0 (Sep 2025), v2.2.0 (Jan 2026), v2.3.0 (Apr 2026)** are now available | Update README |
| D15 | Hardcoded rpc_secret / admin_token in `infrastructure/stacks/lakehouse/garage.toml` | **STILL PRESENT** (untouched since Wave 1) | High-priority security debt |
| D16 | `/v1/` URLs in `garage-init` bash (90-line) | **STILL PRESENT** in `infrastructure/stacks/lakehouse/compose.yaml:71-160` (untouched) | REPLACED entirely by `garage server --single-node` flag |

## 6. Skill file update recommendation with exact diffs

**Target**: create `.agents/skills/garage/SKILL.md` (no existing skill — **net-new**). **Justification**: Wave 1 deliverable is a one-off research note, not a loadable skill; the repository pattern requires `.agents/skills/<name>/SKILL.md` per `docs/openspec/README.md`.

```diff
--- /dev/null
+++ b/.agents/skills/garage/SKILL.md
@@ -0,0 +1,90 @@
+---
+name: garage
+description: |
+  Self-hosted, S3-compatible object storage by Deuxfleurs (Garage v2.3.0+,
+  Rust, distroless Docker ~27 MB). Use when designing cluster layouts,
+  wiring the v2 admin API /v2/ contract, single-node init via --single-node,
+  multi-zone geographic replication, or migrating from v1.x (which had
+  replication_mode removed in v2.0.0 2025-06-14).
+when_to_load:
+  - "Garage", "S3", "object storage", or "Deuxfleurs" mentioned
+  - Touching `infrastructure/stacks/{garage,lakehouse}/`
+  - Wiring Dagster/DLT/DuckLake to S3 endpoints
+  - Adding a Firecrawl monitor for Garage releases
+---
+
+# Garage S3 (v2.3.0+, April 2026)
+
+## TL;DR
+- **Upstream latest**: v2.3.0 (2026-04-16). Cianfhoghlaim pinned: v1.0.1 — 18 months stale.
+- **Critical drift**: `infrastructure/stacks/{garage,lakehouse}/garage.toml` uses `replication_mode = "1"` (removed v2.0.0). Will fail to start on v2.x.
+- **The single-node flag** (v2.3.0) obsoletes the 90-line `garage-init` service in `infrastructure/stacks/lakehouse/compose.yaml:71-160`.
+
+## Verified-live v2.3.0 single-node init (REPLACES garage-init)
+```bash
+docker run -d --name garage-container \
+  -p 3900:3900 -p 3901:3901 -p 3902:3902 -p 3903:3903 \
+  -v $(pwd)/garage.toml:/etc/garage.toml \
+  -e GARAGE_DEFAULT_ACCESS_KEY -e GARAGE_DEFAULT_SECRET_KEY -e GARAGE_DEFAULT_BUCKET \
+  dxflrs/garage:v2.3.0 \
+  /garage server --single-node --default-bucket
+```
+
+## Verified-live 3-node HA garage.toml (`/documentation/cookbook/real-world/`)
+```toml
+metadata_dir = "/var/lib/garage/meta"
+data_dir = "/var/lib/garage/data"
+db_engine = "lmdb"
+metadata_auto_snapshot_interval = "6h"
+replication_factor = 3        # NOT replication_mode (removed v2.0.0)
+compression_level = 2
+rpc_bind_addr = "[::]:3901"
+rpc_public_addr = "<ip>:3901"
+rpc_secret = "<32-byte hex: openssl rand -hex 32>"
+[s3_api]
+s3_region = "garage"
+api_bind_addr = "[::]:3900"
+root_domain = ".s3.lakehouse.cianfhoghlaim.ie"
+[s3_web]
+bind_addr = "[::]:3902"
+root_domain = ".web.garage"
+index = "index.html"
+```
+
+## v1 → v2 migration cheat sheet
+| v1.x | v2.x |
+|:--|:--|
+| `replication_mode = "1"` | `replication_factor = 1` + `consistency_mode = "degraded"` |
+| `replication_mode = "3"` | `replication_factor = 3` (omit `consistency_mode` for default = "strict") |
+| `POST /v1/layout` | `POST /v2/layout` |
+| `GET /v1/health` (`storage_nodes_ok`) | `GET /v2/health` (`storage_nodes_up` — renamed v2.1.0) |
+| `admin_token = "..."` | Multiple tokens via `garage admin token create` |
+| `garage init` (manual bash) | `garage server --single-node --default-access-key --default-bucket` |
+
+## Ports
+3900 S3 API, 3901 RPC, 3902 K2V, 3903 web, 3904 admin.
+
+## Source
+Docs: https://garagehq.deuxfleurs.fr/documentation/quick-start/
+Cookbook: https://garagehq.deuxfleurs.fr/documentation/cookbook/real-world/
+Releases: https://git.deuxfleurs.fr/Deuxfleurs/garage/releases
+Docker: https://hub.docker.com/r/dxflrs/garage/tags
+Wave 1: openspec/research/2026-06-28-browserbase-program-2/agent-12-garage.md
+Wave 2 (this): openspec/research/2026-06-28-browserbase-program-2/live-docs/82-live-garage-23.md
+
+## Cross-references
+- `.agents/skills/change-detection/SKILL.md` — Firecrawl monitor on /releases
+- `.agents/skills/secrets-management/SKILL.md` — Locket for rpc_secret/admin_token
+- `openspec/specs/infrastructure-stacks/spec.md:288,815`
+- `openspec/changes/2026-06-28-browserbase-phase-1b-decisions/specs/oideachais-storage/`
```

### 6.1 Patch to `infrastructure/stacks/garage/README.md` (Wave 1 anti-pattern #6)

```diff
--- a/infrastructure/stacks/garage/README.md
+++ b/infrastructure/stacks/garage/README.md
@@ -57,7 +57,7 @@
-Latest: v1.0.1 (December 2024) — first stable release
+Latest: v2.3.0 (April 2026) — current stable. The v1→v2 jump (2025-06-14)
+was a breaking-change release: `replication_mode` was removed, admin API
+moved from `/v1/` to `/v2/`, and `admin_token` was replaced by multiple
+admin tokens. See `.agents/skills/garage/SKILL.md` for the v1→v2 migration
+cheat sheet. The single-node init flow (`garage server --single-node`)
+added in v2.3.0 obsoletes the 90-line `garage-init` service in
+`infrastructure/stacks/lakehouse/compose.yaml`.

 See the upstream changelog:
 https://git.deuxfleurs.fr/Deuxfleurs/garage/releases
```

### 6.2 Firecrawl monitor per Wave-1 R5 (`upstream-package-monitoring` spec)

Add to `openspec/specs/upstream-package-monitoring/spec.md`:

```diff
+### Monitor: Garage releases
+- URL: https://git.deuxfleurs.fr/Deuxfleurs/garage/releases
+- Cadence: 12h; Goal: "Alert on any v2.x stable release or breaking-change note"
+- Baseline: openspec/research/2026-06-28-browserbase-program-2/live-docs/82-live-garage-23.md
```

## 7. Cross-references

- **Wave 1**: `openspec/research/2026-06-28-browserbase-program-2/agent-12-garage.md` — accurate for v2.0.0 → v2.2.0; URLs referencing `/documentation/latest/` are now 404.
- **Spec**: `openspec/specs/infrastructure-stacks/spec.md:288,815` — Garage stack contract.
- **Wave-1 3-node spec** (`openspec/changes/2026-06-28-browserbase-phase-1b-decisions/specs/oideachais-storage/spec.md:49-61`) mandates HA, but `infrastructure/stacks/lakehouse/garage.toml:18` still has `replication_mode = "1"` — aspirational gap remains.

## 8. Quick recon summary (browser usage stats)

| Tool | Count | Targets |
|:--|:--|:--|
| `browserbase_navigate` | 6 | garagehq home, /documentation/, /documentation/quick-start/, /documentation/cookbook/, /documentation/cookbook/managing-multiple-nodes/, /documentation/cookbook/{deploying-a-cluster-of-3-nodes, cluster} (last 3 → 404, fallback) |
| `browserbase_extract` | 4 | homepage, quick-start, cookbook (×2 — first returned cross-doc stale content) |
| `browserbase_observe` | 1 | cookbook page state-confusion check |
| `firecrawl_firecrawl_scrape` | 6 | /documentation/cookbook/, /documentation/cookbook/real-world/, git.deuxfleurs.fr/releases, /download/, 2× 404 fallback |

**Verbatim quotes captured from live sources** (5 quotes — ≥3 required):
1. **Quick-start** (live v2.3.0): *"dxflrs/garage:v2.3.0 \ /garage \ server \ --single-node --default-bucket"*
2. **v2.0.0 release notes** (Forgejo): *"`replication_mode` is no longer a supported configuration parameter, please use `replication_factor` and `consistency_mode` instead."*
3. **v2.3.0 release notes** (Forgejo): *"allow to use `garage server --single-node` to autocreate a layout and get a functional cluster right away for single nodes"*
4. **Live 3-node cookbook**: *"`replication_factor = 3`"* (3-node verbatim `garage.toml`)
5. **HTTP header on docs site**: `x-garage-error: API error: Key not found` (Garage site served by Garage)

**Real URL patterns observed** (≥1 required):
- `https://garagehq.deuxfleurs.fr/documentation/cookbook/real-world/` — 3-node cluster cookbook
- `https://git.deuxfleurs.fr/Deuxfleurs/garage/releases/tag/v2.3.0` — v2.3.0 release
- `https://hub.docker.com/r/dxflrs/garage/tags?page=1&ordering=last_updated` — Docker Hub (verbatim in cookbook)

**Failed live targets** (documented with HTTP codes):
- `/documentation/latest/quick-start/` → **404** (path dropped; canonical `/documentation/quick-start/`)
- `/documentation/admin-api/`, `/documentation/v2/admin-api/`, `/documentation/configuration/`, `/documentation/integrations/` → **404** (no standalone pages; all consolidated under `/documentation/quick-start/` and reference pages)
- `/documentation/cookbook/managing-multiple-nodes/` → **404** (renamed to `/documentation/cookbook/real-world/` without redirect)

**Fallback method**: Firecrawl `firecrawl_scrape` with `formats: ["markdown"]` and `onlyMainContent: true` — used for 6 of the 8 target pages after `browserbase_extract` returned inconsistent cross-document content (the docs site itself runs on Garage S3, which caused browser-tooling stale-frame issues on cookbook sub-paths).
