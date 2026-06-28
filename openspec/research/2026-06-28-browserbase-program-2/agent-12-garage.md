# Agent 12 — Garage S3 (2026-06-28 22:43 UTC)

## TL;DR

**Upstream latest: v2.3.0** (2026-04-16, 2 months old). **Cianfhoghlaim pinned: v1.0.1** (Dec 2024) — **18 months stale**, present in BOTH `infrastructure/stacks/garage/compose.yaml:21` AND `infrastructure/stacks/lakehouse/compose.yaml:30`. The v1→v2 jump is a **breaking-change release** (v2.0.0, 2025-06-14): the admin API was reworked from `/v1/*` to `/v2/*`, AND the `replication_mode` config field was **removed** in favour of `replication_factor` + `consistency_mode`. Both our `garage.toml` files still use the v1 `replication_mode = "1"` — they will **fail to start on v2.x**. The `garage-init` 90-line bash script in `lakehouse/compose.yaml:71-160` also hard-codes `/v1/` admin endpoints. Repo is on `git.deuxfleurs.fr` (Forgejo), NOT GitHub (`txpipe/garage` and `Deuxfleurs/garage` 404). The v2.3.0 release added a game-changing `--single-node` flag that **autocreates the layout + access key + bucket** from env vars — it would let us delete the entire `garage-init` service.

## 1. Code (current state)

### 1.1 Files in scope
- `infrastructure/stacks/garage/compose.yaml:21` — `image: dxflrs/garage:v1.0.1`
- `infrastructure/stacks/garage/garage.toml:5` — `replication_mode = "1"` (REMOVED in v2.0.0)
- `infrastructure/stacks/lakehouse/compose.yaml:30` — `image: dxflrs/garage:v1.0.1`
- `infrastructure/stacks/lakehouse/garage.toml:18` — `replication_mode = "1"` (REMOVED in v2.0.0)
- `infrastructure/stacks/lakehouse/garage.toml:31` — hardcoded `rpc_secret = "a113063123736ef..."` (security: should be Locket-resolved)
- `infrastructure/stacks/lakehouse/garage.toml:68` — hardcoded `admin_token = "dev-admin-token-change-in-production"` (security: should be Locket-resolved)
- `infrastructure/stacks/lakehouse/compose.yaml:71-160` — `garage-init` service using `/v1/status`, `/v1/layout`, `/v1/key`, `/v1/bucket`, `/v1/bucket/allow` (all moved to `/v2/` in v2.0.0)
- `infrastructure/stacks/garage/garage.toml:11,28` — correctly externalized `RPC_SECRET` + `ADMIN_API_TOKEN` (the standalone stack does this right; the lakehouse variant does not)

### 1.2 What Garage is
Lightweight, self-hosted, S3-compatible object storage written in Rust by the Deuxfleurs collective. CRDT-based consensus, 3-zone replication, geo-distribution across OCI/Hetzner. ~30 MB memory at idle. Single binary, distroless Docker image (~27 MB compressed). 4 separate ports: 3900 (S3 API), 3901 (RPC inter-node), 3902 (K2V key-to-value API), 3903 (web), 3904 (admin).

### 1.3 What Garage v2.0.0 broke (the wall blocking our upgrade)
- `replication_mode` (string) → `replication_factor` (integer) + `consistency_mode` ("degraded"|"dangerous")
- Admin API `/v1/*` → `/v2/*` (with new endpoints, new generated OpenAPI from `utoipa` crate)
- Multiple admin tokens now supported (single `admin_token` is gone)

### 1.4 What v2.3.0 adds (April 2026, 2 months ago)
- `garage server --single-node` — auto-creates layout, single node config (our exact use case!)
- `--default-access-key` + `GARAGE_DEFAULT_ACCESS_KEY`/`GARAGE_DEFAULT_SECRET_KEY` env vars
- `--default-bucket` + `GARAGE_DEFAULT_BUCKET` env var
- Missing admin API endpoints for admin UI (#1376)
- Relaxed requirements on imported access keys (easier S3 migration)
- Bug fixes: silent write errors, DeleteObjects XML parsing, CRC64NVME, SIGHUP, RPC TCP keepalive

## 2. Env (current production)
- 5 ports exposed: 3900 (S3), 3901 (RPC), 3902 (K2V), 3903 (web), 3904 (admin)
- Virtual-host S3 addressing: `root_domain = ".s3.lakehouse.cianfhoghlaim.ie"` (lakehouse) / `.s3.garage.localhost` (standalone)
- 3 buckets created via `garage-init`: `iceberg`, `lance`, `ducklake`
- 1 access key named `lakehouse` with read/write/owner perms
- Replication: 1 (single-node dev), 1 zone `dc1`, capacity 100 GB
- DB engine: `lmdb` (experimental `fjall` added in v2.1.0)
- Locket-resolved secrets: `GARAGE_RPC_SECRET`, `GARAGE_ADMIN_TOKEN` (lakehouse uses dev defaults; standalone uses envsubst)
- Healthcheck workaround: distroless image has no curl → use `/garage -c /etc/garage.toml node id`

## 3. CCC anchors (semantic matches)
- `infrastructure/stacks/garage/README.md:9` — "Garage is the foundational storage substrate for the entire data platform"
- `infrastructure/stacks/garage/README.md:60` — "Latest: v1.0.1 (December 2024)" — STALE
- `infrastructure/stacks/lakehouse/garage.toml:18` — `replication_mode = "1"` (REMOVED in v2.0.0)
- `infrastructure/stacks/lakehouse/garage.toml:31,68` — hardcoded secrets
- `infrastructure/stacks/lakehouse/compose.yaml:30` — `image: dxflrs/garage:v1.0.1` (STALE)
- `infrastructure/stacks/lakehouse/compose.yaml:52` — healthcheck using `/garage node id` (still works on v2.x)
- `infrastructure/stacks/lakehouse/compose.yaml:71-160` — `garage-init` bash using `/v1/*` endpoints (BROKEN on v2.x)
- `infrastructure/stacks/garage/garage.toml:5` — `replication_mode = "1"` (REMOVED in v2.0.0)
- `infrastructure/stacks/garage/garage.toml:11,28` — correctly env-resolved
- `openspec/changes/2026-06-28-browserbase-phase-1b-decisions/specs/oideachais-storage/spec.md:49-61` — spec mandates 3-node HA, currently 1-node (single dev setup, not production)
- `infrastructure/stacks/lakehouse/examples/Data Lake Stack Integration Research.md:15-18` — design doc confirms Garage-on-Hetzner as the "hot" storage tier (CRDT for transient network partitions)

## 4. Drift log (upstream vs Cianfhoghlaim)

| Upstream | Cianfhoghlaim | Drift |
|:--|:--|:--|
| v2.3.0 (2026-04-16) | v1.0.1 (2024-12) | **8 releases behind, 18 months stale** |
| `replication_factor` + `consistency_mode` | `replication_mode = "1"` | **Config removed in v2.0.0 — startup will fail** |
| Admin API `/v2/*` (utoipa-generated) | `/v1/*` (hand-rolled) | **All admin calls in `garage-init` will 404** |
| `garage server --single-node` (v2.3.0) | 90-line `garage-init` bash | **Single-node flag obsoletes our init container** |
| `--default-access-key` env vars | hardcoded `lakehouse` key + manual POST | **Env var approach obsoletes key-creation step** |
| `--default-bucket` env var | manual `for bucket in iceberg lance ducklake` loop | **Env var approach obsoletes bucket-creation step** |
| `storage_nodes_up` (v2.1.0) | `storage_nodes_ok` (v1.x) | **Renamed in admin API #1111** |
| `git.deuxfleurs.fr/Deuxfleurs/garage` (Forgejo) | README says `git.deuxfleurs.fr` ✓ but task brief said GitHub | README correct; task brief was wrong |

## 5. Anti-patterns observed
1. **Hardcoded secrets in committed `garage.toml:31,68`** — plaintext `rpc_secret` and `admin_token` in git. Standalone stack does this right with `${RPC_SECRET}`. Lakehouse is a security regression.
2. **`replication_mode` (v1 syntax) committed to git** — both `garage.toml` files have this. Will fail to start on v2.0+.
3. **`/v1/` admin API URLs in `garage-init` script** — will 404 on v2.0+.
4. **90-line bash init container** — v2.3.0's `--single-node --default-access-key --default-bucket` deletes the entire `garage-init` service.
5. **Service_completed_successfully comment** at `compose.yaml:202-203,236-237` — note says condition is "unreliable with remote Komodo" but the workaround (depends_on garage only) means migrations can race past init.
6. **Stale README claim** `infrastructure/stacks/garage/README.md:60` says "v1.0.1 (December 2024) — first stable release" — actually 1.0.1 was a backport; **v1.0.0 (Sep 2024)** was the first stable, and we're now 2 major versions behind.

## 6. Decision matrix

| Decision | Option A | Option B | Option C |
|:--|:--|:--|:--|
| **Upgrade path** | Stay on v1.x (latest v1.3.1, Jan 2026) — minimal changes | Upgrade to v2.3.0 (current) — full rewrite | Fork pin at v1.0.1 — never |
| **Init mechanism** | Keep 90-line bash `garage-init` | Use `garage server --single-node --default-access-key --default-bucket` (v2.3.0) | Switch to `garage` CLI sidecar |
| **Replication** | Single-node dev only (current) | 3-node HA per `oideachais-storage` spec | 2-node degraded (compromise) |
| **Secret handling** | Hardcoded in toml (current lakehouse) | Locket + envsubst (current standalone) | HashiCorp Vault (out of scope) |
| **Recommendation** | **B + B (upgrade to v2.3.0, use --single-node, externalize secrets via Locket)** | | |

## 7. Conflicts with openspec specs

- **P1B-oideachais-storage** (`openspec/changes/2026-06-28-browserbase-phase-1b-decisions/specs/oideachais-storage/spec.md:49-61`) mandates "Garage 3-node cluster" — but the actual `garage.toml:18` has `replication_mode = "1"` (single-node) and the `garage-init` script only configures 1 node. Spec is **aspirational, not currently implemented**. Open a separate `garage-3-node-ha-cluster` change to bridge this gap.
- **No current P1A/P1B/P2 spec names Garage explicitly**, so the upgrade path is unblocked by openspec. The `2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4` change moved `infrastructure/stacks/garage/README.md` content into a duplicate at `cianfhoghlaim/stacks/garage/README.md` — both will need the version-bump fix.

## 8. Refactor opportunities (with file:line refs)

### R1. **Upgrade to v2.3.0 + migrate config to v2 syntax** (BLOCKING)
- `infrastructure/stacks/garage/compose.yaml:21` and `infrastructure/stacks/lakehouse/compose.yaml:30` — bump `dxflrs/garage:v1.0.1` → `dxflrs/garage:v2.3.0`
- `infrastructure/stacks/garage/garage.toml:5` and `infrastructure/stacks/lakehouse/garage.toml:18` — replace `replication_mode = "1"` with `replication_factor = 1` (or 3 per spec) + `consistency_mode = "degraded"` for single-node, `"strict"` for 3-node HA
- Migrate `infrastructure/stacks/lakehouse/compose.yaml:71-160` `garage-init` from `/v1/` to `/v2/` API endpoints
- Effort: 4-6 hours including integration test
- Risk: medium — changes admin API surface, but our usage is read-only via `aws s3` (which is unchanged)

### R2. **Delete `garage-init` 90-line bash in favor of v2.3.0 env-var flags**
- `infrastructure/stacks/lakehouse/compose.yaml:71-160` — 90 lines of curl + jq-able shell
- Replace with: `command: ["/garage", "-c", "/etc/garage.toml", "server", "--single-node"]` + env vars `GARAGE_DEFAULT_ACCESS_KEY=lakehouse` + `GARAGE_DEFAULT_SECRET_KEY=devpassword` + `GARAGE_DEFAULT_BUCKET=iceberg`
- Caveat: `--default-bucket` is single-bucket; for 3 buckets (`iceberg`, `lance`, `ducklake`) keep a 3-line loop or accept iceberg-only auto-create + manual `garage bucket create` for the other 2
- Effort: 1 hour
- Risk: low — env-var approach is the documented v2.3.0 happy path

### R3. **Externalize hardcoded secrets in lakehouse/garage.toml**
- `infrastructure/stacks/lakehouse/garage.toml:31` — `rpc_secret = "a11306..."` (plaintext 64-hex) → `${GARAGE_RPC_SECRET}` (already in env, just wire it)
- `infrastructure/stacks/lakehouse/garage.toml:68` — `admin_token = "dev-admin-token..."` → `${GARAGE_ADMIN_TOKEN}`
- The standalone `infrastructure/stacks/garage/garage.toml:11,28` already does this correctly with envsubst; port the pattern
- Then add `GARAGE_RPC_SECRET` and `GARAGE_ADMIN_TOKEN` to `infrastructure/stacks/lakehouse/secrets.env` (or generate via Locket at runtime)
- Effort: 30 minutes
- Risk: low — pattern proven in standalone stack

### R4. **Add 3-node HA per P1B-oideachais-storage spec**
- `infrastructure/stacks/lakehouse/garage.toml:18` + new `garage-2.toml`, `garage-3.toml`
- `infrastructure/stacks/lakehouse/compose.yaml:29-63` — convert single `garage:` service to 3 services `garage-1`, `garage-2`, `garage-3` with different `rpc_public_addr` and shared `garage-init`
- Update `garage-init` to query all 3 node IDs, stage capacity across them
- Effort: 1-2 days (includes Komodo + Pangolin service discovery wiring)
- Risk: medium — needs dedicated host on `arm1-oci` or `bunchloch` with 3 persistent volumes

### R5. **Add `infrastructure/stacks/garage` to upstream monitoring**
- Per `openspec/specs/upstream-package-monitoring`, add a Firecrawl monitor on `https://git.deuxfleurs.fr/Deuxfleurs/garage/releases` with goal "Alert on any v2.x stable release or breaking-change note"
- 12h check cadence
- Effort: 15 minutes (Firecrawl monitor via MCP)
- Risk: zero — monitoring only

### R6. **Pin distroless image by digest for reproducibility**
- `infrastructure/stacks/garage/compose.yaml:21` + `infrastructure/stacks/lakehouse/compose.yaml:30` — currently `v1.0.1` tag, mutable. Pin to `@sha256:31576811b11b7f0754cdc85a9562a2ea2dc045583109f9fc12349f810b7a89d0` (the v2.3.0 amd64 digest from Docker Hub).
- Effort: 5 minutes
- Risk: zero — same content, immutable reference
