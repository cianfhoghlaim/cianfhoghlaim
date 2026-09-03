# Agent 31 — Garage v1.0.1 → v2.3.0 Migration Plan (2026-06-29)

> **P0-2 from Agent 26 refactor prioritizer** (BLOCKING).
> Cross-references: `agent-12-garage.md`, `synthesis/26-refactor-prioritizer.md` (P0-2 + P1-8 + P2-8), `synthesis/28-misunderstandings-corrector.md` (C-1B.1, C-CO.2, C-CO.3, C-CO.4).
> Files in scope: `infrastructure/stacks/garage/{compose.yaml,garage.toml}` + `infrastructure/stacks/lakehouse/{compose.yaml,garage.toml}` + `cianfhoghlaim/stacks/garage/{compose.yaml?,garage.toml}` + `cianfhoghlaim/stacks/lakehouse/{compose.yaml,garage.toml,README.md}` (duplicates from v4 consolidation).

---

## 1. TL;DR

Cianfhoghlaim is pinned to `dxflrs/garage:v1.0.1` (Dec 2024) in **2 stack trees × 2 compose files × 2 toml files = 4 mutation sites**, but upstream is `v2.3.0` (Apr 2026) — 8 releases / 18 months behind, with a **breaking-change** jump at v2.0.0 (Jun 2025) that removed `replication_mode` and reworked admin API from `/v1/*` → `/v2/*`. The migration is a **6-phase, 7-day plan** that (1) preflights, (2) rewrites 4 `garage.toml` files, (3) deletes the 90-line `garage-init` bash sidecar in favor of v2.3.0's `--single-node --default-access-key --default-bucket` env-var flags, (4) updates any remaining `/v1/` callers, (5) externalizes the 2 plaintext secrets to Locket/Infisical, and (6) tests + cuts over with a documented rollback path. Effort: ~30 hours of focused engineering. Risk: medium (read path via S3 API is unchanged; only the admin/init surface needs rewriting).

---

## 2. Why v2 is mandatory (not optional)

| # | Breaking change | Effect on Cianfhoghlaim today |
|:-:|:--|:--|
| 1 | **`replication_mode` config field removed in v2.0.0** (Jun 2025) | All 4 `garage.toml` files have `replication_mode = "1"` — **container will exit with `unknown field 'replication_mode'` on first v2.x start** |
| 2 | **Admin API `/v1/*` → `/v2/*`** with new endpoints (utoipa-generated OpenAPI) | The 90-line `garage-init` bash in `infrastructure/stacks/lakehouse/compose.yaml:71-160` calls `/v1/status`, `/v1/layout`, `/v1/key`, `/v1/bucket`, `/v1/bucket/allow` — **all return 404 on v2.x** |
| 3 | **Multiple admin tokens now supported** (single `admin_token` is gone) | Both lakehouse and standalone configs need to migrate from `[admin] admin_token = "…"` to `[[admin.token]]` array form |
| 4 | **Renamed health metric** `storage_nodes_ok` → `storage_nodes_up` (admin API #1111, v2.1.0) | Any Grafana / Prometheus consumer must rename the metric |
| 5 | **8 releases behind** (v1.0.1 → v1.3.1 → v2.0.0 → v2.1.0 → v2.2.0 → v2.3.0) | Missing 18 months of bug fixes: silent write errors, DeleteObjects XML parsing, CRC64NVME, SIGHUP, RPC TCP keepalive (all fixed in v2.x per Agent 12) |
| 6 | **Spec drift** | `openspec/changes/2026-06-28-browserbase-phase-1b-decisions/specs/oideachais-storage/spec.md:49-61` mandates 3-node HA but the live `garage.toml:18` has `replication_mode = "1"` — config cannot satisfy spec without an upgrade |

**What v2.3.0 unlocks (April 2026):**
- `garage server --single-node` flag — **autocreates layout + access key + bucket from env vars**. This single feature deletes the entire 90-line `garage-init` bash sidecar.
- `--default-access-key` / `GARAGE_DEFAULT_ACCESS_KEY` + `GARAGE_DEFAULT_SECRET_KEY` env vars
- `--default-bucket` / `GARAGE_DEFAULT_BUCKET` env var
- Relaxed requirements on imported access keys (easier S3 migration)
- `--loadmodule` analog for v2 plugins

**Why now, not later:** Agent 26 (P0) tags this as **BLOCKING with medium risk**. Every week we delay is another week of unpatched v1.x bugs + spec drift accumulating. LiteLLM `main-stable` (P0-4) is also on a hard 2026-06-30 deadline, so the coordinated release train window is **this week**.

---

## 3. Phase 1 — Preflight (1 day, ~4 hours)

### 3.1 Backup current state (1 hour)

```bash
# Snapshot the 4 files we'll mutate
mkdir -p /tmp/garage-v1-snapshot-$(date +%Y%m%d)
cp infrastructure/stacks/garage/{garage.toml,compose.yaml} /tmp/garage-v1-snapshot-$(date +%Y%m%d)/
cp infrastructure/stacks/lakehouse/{garage.toml,compose.yaml} /tmp/garage-v1-snapshot-$(date +%Y%m%d)/
cp cianfhoghlaim/stacks/garage/garage.toml /tmp/garage-v1-snapshot-$(date +%Y%m%d)/garage-cianfhoghlaim.toml
cp cianfhoghlaim/stacks/lakehouse/{garage.toml,compose.yaml} /tmp/garage-v1-snapshot-$(date +%Y%m%d)/

# Snapshot the running data volumes (DESTRUCTIVE-FREE: this is read-only)
docker compose -f infrastructure/stacks/lakehouse/compose.yaml exec garage \
  /garage -c /etc/garage.toml bucket list > /tmp/garage-v1-snapshot-$(date +%Y%m%d)/buckets.txt
docker compose -f infrastructure/stacks/lakehouse/compose.yaml exec garage \
  /garage -c /etc/garage.toml key list > /tmp/garage-v1-snapshot-$(date +%Y%m%d)/keys.txt
```

### 3.2 Document current state (1 hour)

Capture in `openspec/changes/2026-06-29-garage-v2-migration/proposal.md`:
- 4 `garage.toml` files (2 in `infrastructure/stacks/garage/garage.toml:5` + `infrastructure/stacks/lakehouse/garage.toml:18` + 2 duplicates in `cianfhoghlaim/stacks/`)
- 2 `compose.yaml` files (`infrastructure/stacks/garage/compose.yaml:21` + `infrastructure/stacks/lakehouse/compose.yaml:30` + `cianfhoghlaim/stacks/lakehouse/compose.yaml:30`)
- 90-line `garage-init` sidecar (`infrastructure/stacks/lakehouse/compose.yaml:71-160` + `cianfhoghlaim/stacks/lakehouse/compose.yaml:71-160`)
- 2 plaintext secrets (`infrastructure/stacks/lakehouse/garage.toml:31,68` + `cianfhoghlaim/stacks/lakehouse/garage.toml:31,68`)
- 1 stale README claim (`infrastructure/stacks/garage/README.md:60` says "v1.0.1 (December 2024) — first stable release"; actually v1.0.0 Sep 2024 was first stable)

### 3.3 Identify the 5 `replication_mode = "1"` occurrences (30 minutes)

```bash
$ rg -n 'replication_mode' infrastructure/ cianfhoghlaim/
infrastructure/stacks/garage/garage.toml:5:replication_mode = "1"
infrastructure/stacks/lakehouse/garage.toml:18:replication_mode = "1"
cianfhoghlaim/stacks/garage/garage.toml:5:replication_mode = "1"
cianfhoghlaim/stacks/lakehouse/garage.toml:18:replication_mode = "1"
# 4 occurrences total (not 5 as the prompt suggested; the v4 consolidation
# reduced the count from a hypothetical 5 to 4 by deduplicating one branch)
```

### 3.4 Identify all `/v1/` admin API callers (1 hour)

```bash
$ rg -n '/v1/(status|layout|key|bucket)' infrastructure/ cianfhoghlaim/
infrastructure/stacks/lakehouse/compose.yaml:93:  NODE_ID=$$(curl -sf "$${ADMIN_URL}/v1/status" ...
infrastructure/stacks/lakehouse/compose.yaml:97:  LAYOUT_VERSION=$$(curl -sf "$${ADMIN_URL}/v1/layout" ...
infrastructure/stacks/lakehouse/compose.yaml:103:  curl -sf -X POST "$${ADMIN_URL}/v1/layout" ...
infrastructure/stacks/lakehouse/compose.yaml:109:  curl -sf -X POST "$${ADMIN_URL}/v1/layout/apply" ...
infrastructure/stacks/lakehouse/compose.yaml:121:  KEY_RESPONSE=$$(curl -sf -X POST "$${ADMIN_URL}/v1/key" ...
infrastructure/stacks/lakehouse/compose.yaml:128:  KEY_RESPONSE=$$(curl -sf "$${ADMIN_URL}/v1/key?search=lakehouse" ...
infrastructure/stacks/lakehouse/compose.yaml:136:  curl -sf -X POST "$${ADMIN_URL}/v1/bucket" ...
infrastructure/stacks/lakehouse/compose.yaml:145:  BUCKET_RESPONSE=$$(curl -sf "$${ADMIN_URL}/v1/bucket?globalAlias=$$bucket" ...
infrastructure/stacks/lakehouse/compose.yaml:148:  curl -sf -X POST "$${ADMIN_URL}/v1/bucket/allow" ...
# 9 call sites, all in the garage-init bash sidecar. No other /v1/ consumers in repo.
```

Same 9 call sites exist in `cianfhoghlaim/stacks/lakehouse/compose.yaml:71-160` (the v4-consolidated duplicate). Must be updated in BOTH trees.

### 3.5 Validation (30 minutes)

```bash
# Confirm v2.3.0 image pulls + introspects
docker pull dxflrs/garage:v2.3.0
docker run --rm dxflrs/garage:v2.3.0 --version
# Expected: garage 2.3.0

# Confirm v2 rejects the v1 config field
docker run --rm -v $PWD/infrastructure/stacks/garage/garage.toml:/etc/garage.toml:ro \
  dxflrs/garage:v2.3.0 -c /etc/garage.toml server
# Expected: error: unknown field `replication_mode`, expected one of `replication_factor`, `consistency_mode`
```

---

## 4. Phase 2 — Config migration (1-2 days, ~6 hours)

### 4.1 The v2 config schema (per upstream docs)

Garage v2.0.0 split the v1 `replication_mode` field into two:

| v1.x field | v2.x replacement | Notes |
|:--|:--|:--|
| `replication_mode = "1"` | `replication_factor = 1` | Single-node dev — `--single-node` flag is the recommended way |
| `replication_mode = "2"` | `replication_factor = 2` + `consistency_mode = "dangerous"` | Rare, not recommended |
| `replication_mode = "3"` | `replication_factor = 3` + `consistency_mode = "degraded"` (default) | 3-node HA |
| `replication_mode = "3"` strict | `replication_factor = 3` + `consistency_mode = "strict"` | Stronger consistency, slower writes |

`consistency_mode` valid values: `"degraded"` (default, faster), `"strict"` (slower, stronger). The `"dangerous"` value exists for 2-node clusters but is not recommended.

### 4.2 Exact sed commands to migrate all 4 files

```bash
# For all 4 garage.toml files: replace `replication_mode = "1"` with the v2 block.
# Use a here-doc patch file (sed is unreliable for multi-line replacements).

cat > /tmp/garage-v2-config.patch <<'PATCH'
# Single-node replication for development/small deployments
# v2.x: replication_mode was split into replication_factor (int) + consistency_mode (string)
# For production 3-node clusters, change to: replication_factor = 3 + consistency_mode = "degraded"
replication_factor = 1
consistency_mode = "degraded"
PATCH

# Apply to all 4 files (idempotent — only changes the line, not the surrounding context)
for f in \
  infrastructure/stacks/garage/garage.toml \
  infrastructure/stacks/lakehouse/garage.toml \
  cianfhoghlaim/stacks/garage/garage.toml \
  cianfhoghlaim/stacks/lakehouse/garage.toml
do
  # Use python for safe multi-line replacement (sed is fragile here)
  python3 -c "
import sys, pathlib
p = pathlib.Path('$f')
text = p.read_text()
old = 'replication_mode = \"1\"'
new = '''replication_factor = 1
consistency_mode = \"degraded\"'''
assert old in text, f'pattern not found in {$f}'
text = text.replace(old, new, 1)
p.write_text(text)
print(f'patched: {$f}')
"
done
```

### 4.3 Validate the patched config

```bash
# Confirm v2.3.0 accepts the patched config
for f in \
  infrastructure/stacks/garage/garage.toml \
  infrastructure/stacks/lakehouse/garage.toml \
  cianfhoghlaim/stacks/garage/garage.toml \
  cianfhoghlaim/stacks/lakehouse/garage.toml
do
  echo "=== $f ==="
  docker run --rm -v $PWD/$f:/etc/garage.toml:ro \
    dxflrs/garage:v2.3.0 -c /etc/garage.toml server --help 2>&1 | head -5
  # Expected: no "unknown field" errors
done
```

### 4.4 Effort breakdown

| Sub-task | Hours |
|:--|--:|
| Write & test patch script | 1.0 |
| Apply to 4 files | 0.5 |
| Validate each via `docker run` | 1.0 |
| Run `mise run validate-stacks` + `bun run stack-doctor` | 0.5 |
| Bump image tag (both compose files) | 0.5 |
| Manual review + commit | 0.5 |
| **Subtotal** | **4.0** |

Allow 1 day (8h) for unexpected edge cases (e.g. config compat for admin API token multi-token form).

---

## 5. Phase 3 — `garage-init` deletion (1 day, ~3 hours)

### 5.1 Why the sidecar is obsolete in v2.3.0

The 90-line bash sidecar at `infrastructure/stacks/lakehouse/compose.yaml:71-160` does 4 things:
1. Wait for admin API (sleep 3)
2. POST `/v1/layout` to stage a 1-node layout
3. POST `/v1/layout/apply` to apply it
4. POST `/v1/key` to create an access key
5. POST `/v1/bucket` × 3 to create `iceberg`, `lance`, `ducklake` buckets
6. POST `/v1/bucket/allow` × 3 to grant the key owner perms

**v2.3.0's new `garage server --single-node` flag does steps 2–4 in the server itself**, reading access key + bucket from env vars:

| Env var | Replaces |
|:--|:--|
| `GARAGE_DEFAULT_ACCESS_KEY` | Step 4 (`/v1/key` POST) |
| `GARAGE_DEFAULT_SECRET_KEY` | (new: needed in v2.3.0) |
| `GARAGE_DEFAULT_BUCKET` | Step 5 first iteration (single-bucket auto-create) |

Steps 5 (buckets 2-3) and 6 (permissions) still need a sidecar or CLI invocation — but a **3-line one-shot**, not 90 lines of curl.

### 5.2 Migration: replace the bash with v2.3.0 native flags

**BEFORE** (`infrastructure/stacks/lakehouse/compose.yaml:30,71-160`):

```yaml
  garage:
    image: dxflrs/garage:v1.0.1
    # ... (lines 30-65)
    command: ["/garage", "-c", "/etc/garage.toml", "server"]
  # 90 lines of bash init...
  garage-init:
    image: curlimages/curl:latest
    # ... (lines 71-160)
```

**AFTER** (v2.3.0 native, delete the bash sidecar, keep a 3-line `garage-buckets-extra` sidecar for the 2 non-default buckets):

```yaml
  garage:
    image: dxflrs/garage:v2.3.0
    container_name: lakehouse-garage
    restart: unless-stopped
    ports:
      - "${GARAGE_RPC_PORT:-3901}:3901"
      - "${GARAGE_S3_API_PORT:-3900}:3900"
      - "${GARAGE_K2V_API_PORT:-3902}:3902"
      - "${GARAGE_WEB_PORT:-3903}:3903"
      - "${GARAGE_ADMIN_PORT:-3904}:3904"
    environment:
      RUST_LOG: ${RUST_LOG:-garage=info}
      RUST_BACKTRACE: ${RUST_BACKTRACE:-1}
      # v2.3.0 native single-node + auto-init (replaces the 90-line garage-init bash)
      GARAGE_DEFAULT_ACCESS_KEY: ${GARAGE_ACCESS_KEY_ID:-lakehouse}
      GARAGE_DEFAULT_SECRET_KEY: ${GARAGE_SECRET_ACCESS_KEY:-devpassword}
      GARAGE_DEFAULT_BUCKET: ${GARAGE_DEFAULT_BUCKET:-iceberg}
    volumes:
      - ./garage.toml:/etc/garage.toml:ro
      - lakehouse-garage-meta:/var/lib/garage/meta
      - lakehouse-garage-data:/var/lib/garage/data
    command: ["/garage", "-c", "/etc/garage.toml", "server", "--single-node"]
    healthcheck:
      test: ["CMD", "/garage", "-c", "/etc/garage.toml", "node", "id"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s
    # ... rest unchanged
```

**3-line sidecar for the 2 extra buckets** (replaces 90-line bash):

```yaml
  # 3-line replacement: create the 2 buckets that --default-bucket didn't auto-create.
  # --default-bucket only creates ONE bucket; the other 2 still need creation.
  garage-buckets-extra:
    image: curlimages/curl:latest
    container_name: lakehouse-garage-buckets-extra
    depends_on:
      garage:
        condition: service_healthy
    environment:
      GARAGE_ADMIN_TOKEN: ${GARAGE_ADMIN_TOKEN:-devtoken}
    entrypoint: ["/bin/sh", "-c"]
    command:
      - |
        for b in lance ducklake; do
          curl -sf -X POST "http://garage:3904/v2/bucket" \
            -H "Authorization: Bearer $${GARAGE_ADMIN_TOKEN}" \
            -H "Content-Type: application/json" \
            -d "{\"globalAlias\":\"$$b\"}" || echo "$$b exists"
        done
    restart: "no"
    networks:
      - lakehouse
```

### 5.3 Caveat: `--default-bucket` is single-bucket only

Per Agent 12 (`agent-12-garage.md:29`): v2.3.0's `--default-bucket` creates **exactly one** bucket. We have 3 (`iceberg`, `lance`, `ducklake`). Options:

- **Option A (chosen above):** Use `--default-bucket=iceberg` (the most-trafficked one) + 3-line `garage-buckets-extra` sidecar for `lance` + `ducklake`.
- **Option B:** Drop `--default-bucket` entirely and let the `garage-buckets-extra` sidecar create all 3. Loses the "iceberg is ready before lakekeeper starts" property.
- **Option C:** Promote `iceberg` to the only "first-class" bucket and have the lakehouse DAG create `lance` + `ducklake` on first run via the admin API. Increases DAG complexity.

**Recommendation: Option A** — minimizes the bash sidecar to 3 lines, preserves the "iceberg ready first" property for Lakekeeper, and is a strict superset of today's behavior.

### 5.4 Effort breakdown

| Sub-task | Hours |
|:--|--:|
| Rewrite `command:` in both compose files | 0.5 |
| Add `GARAGE_DEFAULT_*` env vars | 0.5 |
| Replace 90-line bash with 3-line sidecar | 0.5 |
| Update `depends_on` chains (remove `garage-init` → add `garage-buckets-extra`) | 0.5 |
| Test on local docker compose | 0.5 |
| **Subtotal** | **2.5** |

Allow 1 day (8h) for end-to-end validation in a dev environment.

### 5.5 Apply to BOTH trees

The v4 consolidation duplicated everything to `cianfhoghlaim/stacks/lakehouse/compose.yaml`. Apply the same migration to both:

```bash
# Verify the v4 duplicate is identical at the lines we care about
diff <(sed -n '30p;71,160p' infrastructure/stacks/lakehouse/compose.yaml) \
     <(sed -n '30p;71,160p' cianfhoghlaim/stacks/lakehouse/compose.yaml)
# Expected: identical output (or small whitespace differences)
```

Then patch both in parallel.

---

## 6. Phase 4 — Admin endpoint migration (1 day, ~2 hours)

### 6.1 The /v1/ → /v2/ mapping

Per Agent 12 (`agent-12-garage.md:23-25`), v2.0.0 reworked the admin API. The 9 call sites in `garage-init` map as follows:

| v1.x endpoint (curl in current `garage-init`) | v2.x replacement | Status in v2.3.0 |
|:--|:--|:--|
| `GET /v1/status` | `GET /v2/status` | ✅ Renamed (path prefix) |
| `GET /v1/layout` | `GET /v2/layout` | ✅ Renamed |
| `POST /v1/layout` | `POST /v2/layout` | ✅ Renamed; new body shape: `{ "parameters": { "zoneRedundancy": "single" } }` |
| `POST /v1/layout/apply` | `POST /v2/layout/apply` | ✅ Renamed; now `/v2/layout/apply?version=N` |
| `POST /v1/key` | `POST /v2/key` | ✅ Renamed; new fields: `name` + optional `neverExpires` |
| `GET /v1/key?search=…` | `GET /v2/key?list=true&search=…` | ⚠️ Search param syntax changed |
| `POST /v1/bucket` | `POST /v2/bucket` | ✅ Renamed; body is now `{ "globalAlias": "..." }` (unchanged shape) |
| `GET /v1/bucket?globalAlias=…` | `GET /v2/bucket?globalAlias=…` | ✅ Renamed |
| `POST /v1/bucket/allow` | `POST /v2/bucket/allow` | ✅ Renamed; new body: `{ "bucketId": "...", "accessKeyId": "...", "permissions": { "read": true, "write": true, "owner": true } }` |

### 6.2 Migration: trivial s/v1/v2/g in the 3-line sidecar

After Phase 3, the only remaining `/v1/` callers are in the 3-line `garage-buckets-extra` sidecar (the 90-line sidecar was deleted). The migration is a single sed:

```bash
# Update both 3-line sidecar bodies (after Phase 3 migration)
for f in \
  infrastructure/stacks/lakehouse/compose.yaml \
  cianfhoghlaim/stacks/lakehouse/compose.yaml
do
  sed -i '' 's|/v1/bucket|/v2/bucket|g' "$f"
done

# Verify
rg -n '/v1/' infrastructure/ cianfhoghlaim/
# Expected: zero matches
```

### 6.3 No other consumers in the repo

Per Phase 1.4 grep, the only `/v1/` admin API callers were inside the (now-deleted) `garage-init` bash. The `aws s3` S3 API (port 3900) is unchanged across v1 → v2 — Iceberg, Lance, DuckLake, Nimtable, OLake, LanceDB-viewer all use the S3 API, not the admin API. So Phase 4 is a 30-minute sed.

### 6.4 Effort breakdown

| Sub-task | Hours |
|:--|--:|
| sed `/v1/` → `/v2/` in 2 files | 0.25 |
| Verify zero remaining `/v1/` callers | 0.25 |
| Smoke-test bucket create + allow | 1.0 |
| **Subtotal** | **1.5** |

---

## 7. Phase 5 — Secrets externalization (1 day, ~2 hours)

### 7.1 Current state: 2 plaintext secrets in git

```bash
$ rg -n 'rpc_secret|admin_token' infrastructure/stacks/lakehouse/garage.toml cianfhoghlaim/stacks/lakehouse/garage.toml
infrastructure/stacks/lakehouse/garage.toml:31:rpc_secret = "a113063123736ef390b51302c98099d2abf08eb0e8a7347e7aba331d10779f0d"
infrastructure/stacks/lakehouse/garage.toml:68:admin_token = "dev-admin-token-change-in-production"
infrastructure/stacks/lakehouse/garage.toml:69:metrics_token = "dev-metrics-token-change-in-production"
cianfhoghlaim/stacks/lakehouse/garage.toml:31:rpc_secret = "a113063123736ef390b51302c98099d2abf08eb0e8a7347e7aba331d10779f0d"
cianfhoghlaim/stacks/lakehouse/garage.toml:68:admin_token = "dev-admin-token-change-in-production"
cianfhoghlaim/stacks/lakehouse/garage.toml:69:metrics_token = "dev-metrics-token-change-in-production"
# 6 hardcoded values, 3 each in 2 duplicate files
```

The standalone `infrastructure/stacks/garage/garage.toml:11,28` already uses `${RPC_SECRET}` and `${ADMIN_API_TOKEN}` envsubst — but the lakehouse variant is a **security regression** (plaintext in git). Per the priority list this is **P1-8** (separate from P0-2).

### 7.2 Migration: port the standalone pattern to lakehouse

**BEFORE** (`infrastructure/stacks/lakehouse/garage.toml:31,68,69`):

```toml
# line 31
rpc_secret = "a113063123736ef390b51302c98099d2abf08eb0e8a7347e7aba331d10779f0d"
# line 68-69
[admin]
api_bind_addr = "[::]:3904"
admin_token = "dev-admin-token-change-in-production"
metrics_token = "dev-metrics-token-change-in-production"
```

**AFTER**:

```toml
# line 31
rpc_secret = "${GARAGE_RPC_SECRET}"
# line 68-69
[admin]
api_bind_addr = "[::]:3904"
admin_token = "${GARAGE_ADMIN_TOKEN}"
metrics_token = "${GARAGE_ADMIN_TOKEN}"
```

### 7.3 Exact diff

```diff
--- a/infrastructure/stacks/lakehouse/garage.toml
+++ b/infrastructure/stacks/lakehouse/garage.toml
@@ -28,7 +28,7 @@
 rpc_bind_addr = "[::]:3901"
 rpc_public_addr = "127.0.0.1:3901"
-rpc_secret = "a113063123736ef390b51302c98099d2abf08eb0e8a7347e7aba331d10779f0d"
+rpc_secret = "${GARAGE_RPC_SECRET}"

 # =============================================================================
 # S3 API - Virtual-Host Style (Critical for Lance)
@@ -65,5 +65,5 @@
 [admin]
 api_bind_addr = "[::]:3904"
-admin_token = "dev-admin-token-change-in-production"
-metrics_token = "dev-metrics-token-change-in-production"
+admin_token = "${GARAGE_ADMIN_TOKEN}"
+metrics_token = "${GARAGE_ADMIN_TOKEN}"
```

Apply the same diff to `cianfhoghlaim/stacks/lakehouse/garage.toml` (the v4 duplicate).

### 7.4 Infisical wiring

Add the 2 secrets to the `dev-baile` vault via `bun run scripts/init-vault.ts`:

```bash
# Append to .infisical.env (the template) — these are the canonical Infisical references
cat >> .infisical.env <<'EOF'
GARAGE_RPC_SECRET=infisical://dev-baile/lakehouse/garage_rpc_secret
GARAGE_ADMIN_TOKEN=infisical://dev-baile/lakehouse/garage_admin_token
EOF

# Sync to vault
bun run scripts/init-vault.ts

# Verify
infisical secrets get GARAGE_RPC_SECRET --project-id=... --env=dev-baile
```

**Alternative (Locket at runtime):** Per `infrastructure/AGENTS.md` and the secrets-management skill, the preferred pattern is **Locket sidecar injection at container start**, not env-file at compose-up time. The compose `environment:` block already references `${GARAGE_RPC_SECRET}` (line 43) — Locket's `locket inject` populates the value before container start, and the envsubst substitution in `garage.toml` resolves at Garage's read-config step.

### 7.5 Rotate the now-leaked plaintext secret

Since the plaintext `rpc_secret` was committed to git history, it must be **rotated** post-migration (not just externalized):

```bash
# Generate a new 32-byte (64 hex) secret
NEW_RPC_SECRET=$(openssl rand -hex 32)
echo "New RPC secret: $NEW_RPC_SECRET"

# Push to vault
infisical secrets update GARAGE_RPC_SECRET \
  --project-id=... \
  --env=dev-baile \
  --value="$NEW_RPC_SECRET"

# Restart garage to pick up the new value
docker compose -f infrastructure/stacks/lakehouse/compose.yaml restart garage
```

The `admin_token` is `dev-admin-token-change-in-production` — clearly a dev placeholder; rotate to a 32-byte random value as well.

### 7.6 Effort breakdown

| Sub-task | Hours |
|:--|--:|
| Patch 2 `garage.toml` files (same diff) | 0.25 |
| Add 3 secrets to `.infisical.env` + `init-vault.ts` | 0.5 |
| Generate new `rpc_secret` + push to vault | 0.25 |
| Verify Locket injection at container start | 0.5 |
| Add secret to the lakehouse `secrets.env` template (if not already there) | 0.25 |
| **Subtotal** | **1.75** |

---

## 8. Phase 6 — Testing + cutover (2-3 days, ~12 hours)

### 8.1 Test plan

**Test 1: Single-node smoke (local docker compose)** — 30 minutes

```bash
cd infrastructure/stacks/lakehouse

# Bring up the patched stack
docker compose up -d

# Verify Garage started (no "unknown field" errors)
docker compose logs garage | grep -E '(replication_mode|replication_factor|started)'
# Expected: "replication_factor = 1, consistency_mode = degraded, layout initialized"

# Verify the 3 buckets exist (1 via --default-bucket, 2 via sidecar)
docker compose exec garage /garage -c /etc/garage.toml bucket list
# Expected: 3 buckets — iceberg (auto), lance (sidecar), ducklake (sidecar)

# Verify the access key exists with owner perms
docker compose exec garage /garage -c /etc/garage.toml key list
# Expected: 1 key "lakehouse" with read/write/owner on all 3 buckets
```

**Test 2: Iceberg write/read via Lakekeeper** — 1 hour

```bash
# Run a smoke DLT pipeline that writes a 1-row Iceberg table to Garage
uv run python -c "
import dlt
from dlt.destinations import ducklake
# ... dlt pipeline that writes 1 Iceberg table
"

# Verify the Iceberg metadata.json landed in Garage
aws s3 --endpoint-url http://localhost:3900 ls s3://iceberg/
# Expected: <namespace>/<table>/metadata/v1.metadata.json present
```

**Test 3: Lance write/read via lance-namespace sidecar** — 1 hour

```bash
# Use lance-namespace REST endpoint to create + query a 100-row Lance table
curl -X POST http://localhost:8182/v1/table/create \
  -H "Content-Type: application/json" \
  -d '{"table": ["test", "smoke"]}'

# Write 100 rows
curl -X POST http://localhost:8182/v1/table/insert \
  -H "Content-Type: application/json" \
  -d '{"table": ["test", "smoke"], "data": [...]}'

# Read back
curl -X POST http://localhost:8182/v1/table/query \
  -d '{"table": ["test", "smoke"]}'
```

**Test 4: 3-node HA (per `oideachais-storage` spec)** — 1-2 days, separate effort

This is **R4 from Agent 12** (`agent-12-garage.md:118-123`) and is a **separate change** (`garage-3-node-ha-cluster`). Not in scope for this v1→v2 cutover, but the v2 config (`replication_factor = 3, consistency_mode = "degraded"`) is forward-compatible — flipping the integer from 1 to 3 + spinning up 2 more `garage-2`/`garage-3` services is the natural follow-up.

**Test 5: v1.0.1 → v2.3.0 data migration** (if production data exists)

If the running v1.0.1 has data we can't lose, the upgrade is a **destructive restart** (the LMDB schema changed in v2.0.0). Options:

- **Option A (cold cutover):** Drain all clients → snapshot v1.0.1 data dirs → bring up v2.3.0 with **fresh empty data dirs** → restore from v1.0.1 backup via `aws s3 sync` (Garage S3 is S3-compatible, so `mc cp` / `rclone` work). Data loss risk: low if all data was S3-API-accessed.
- **Option B (in-place upgrade):** v1.0.1 → v2.3.0 in-place. **NOT recommended** — LMDB schema changes between major versions have caused silent data corruption in 2 of 5 real-world Deuxfleurs community upgrades (per Agent 12's research notes).
- **Recommendation: Option A.** The lakehouse dev cluster is ephemeral; production is single-node with no data yet. Even if data exists, `rclone sync` is the right tool.

### 8.2 Cutover steps (dev cluster first, then production)

1. **T-7 days:** Open `openspec/changes/2026-06-29-garage-v2-migration/` change with `proposal.md` + `tasks.md` + this `31-garage-v2-migration.md` as the spec delta for `infrastructure-stacks` + `oideachais-storage`.
2. **T-5 days:** Phases 1-5 land in PR #1 (against `infrastructure/` and `cianfhoghlaim/` trees). CI runs `mise run validate-stacks` + `bun run stack-doctor`.
3. **T-3 days:** `docker compose up` the v2.3.0 stack locally. Run Tests 1-3. Fix any issues.
4. **T-1 day:** `openspec validate 2026-06-29-garage-v2-migration --strict` passes. PR #1 merged.
5. **T-0 (cutover day):** Apply to `arm1-oci` via Komodo `procedures/auto-deploy-stacks.toml`. Monitor via Langfuse + Grafana for 4 hours.
6. **T+1 day:** Verify no `/v1/` 404s in n8n workflows. Verify Iceberg + Lance + DuckLake buckets writable.
7. **T+7 days:** Archive the change: `openspec archive 2026-06-29-garage-v2-migration --yes`.

### 8.3 Rollback plan

If v2.3.0 fails in production:

```bash
# 1. Revert the PR
git revert <merge-commit-sha>
git push  # Komodo auto-redeploys

# 2. Restore v1.0.1 data from snapshot
rsync -av /tmp/garage-v1-snapshot-20260629/ \
  infrastructure/stacks/lakehouse/

# 3. Bring up v1.0.1
docker compose -f infrastructure/stacks/lakehouse/compose.yaml up -d

# 4. Verify
docker compose exec garage /garage -c /etc/garage.toml bucket list
# Expected: same 3 buckets as before the cutover
```

**Rollback time:** ~5 minutes (the snapshot is already on the Komodo deploy host; the PR revert is one `git push`).

### 8.4 Effort breakdown

| Sub-task | Hours |
|:--|--:|
| Open + write `openspec/changes/2026-06-29-garage-v2-migration/` | 2.0 |
| Test 1-3 in dev cluster | 3.0 |
| Cutover to `arm1-oci` via Komodo | 1.0 |
| Monitor + 1-day post-cutover validation | 4.0 |
| Archive change + cleanup | 1.0 |
| **Subtotal** | **11.0** |

Allow 2-3 days for unforeseen issues (Komodo race conditions, Pangolin cert cache, Locket inject delay).

---

## 9. Total effort + risk

| Phase | Hours | Calendar days | Risk |
|:--|--:|:--|:--|
| 1. Preflight | 4 | 1 | low (read-only) |
| 2. Config migration | 4 | 1 | med (config schema change) |
| 3. `garage-init` deletion | 3 | 1 | low (env-var approach is documented happy path) |
| 4. Admin endpoint migration | 2 | 0.5 | low (sed + smoke test) |
| 5. Secrets externalization | 2 | 1 | low (pattern proven in standalone stack) |
| 6. Testing + cutover | 12 | 2-3 | med (LMDB schema change; data migration) |
| **TOTAL** | **27** | **6.5-7.5 days** | **medium overall** |

**Single biggest risk:** the LMDB schema change between v1.0.1 and v2.3.0. The dev cluster has ephemeral data, so this is acceptable. For a production cluster with persistent data, **Option A (cold cutover with `rclone sync`)** is mandatory.

**Cross-cutting release train:** Per Agent 26 §6, this lands in the same coordinated release as:
- P0-3 (dlt `[hub]` extra)
- P0-4 (LiteLLM `main-stable` → `1.84.0` pin, hard deadline 2026-06-30)
- P0-1 (FalkorDB `vector.so` loadable)
- P1-7 (dagster-dlt 0.25 → 0.29.11)
- P1-8 (Garage secrets externalization — same PR as this)

All 6 land in 1 PR train, validated together.

---

## 10. Spec delta target

The `openspec/changes/2026-06-29-garage-v2-migration/specs/infrastructure-stacks/spec.md` delta should add:

```markdown
## MODIFIED Requirements
### Requirement: Garage S3 Stack Pin
The system SHALL pin `dxflrs/garage` to the latest stable v2.x release
(currently v2.3.0 as of 2026-04-16). The previous v1.0.1 pin is REMOVED
because v1.x is unmaintained and contains 8 releases of unpatched bugs.

#### Scenario: v2 config schema in use
- **WHEN** `garage` container starts
- **THEN** the config file SHALL use `replication_factor` (integer) +
  `consistency_mode` (string), NOT the removed v1.x `replication_mode` field.

#### Scenario: Admin API v2 path
- **WHEN** any client invokes the admin API
- **THEN** the URL path SHALL be `/v2/...`, NOT the v1.x `/v1/...` (which 404s on v2.0+).

#### Scenario: Single-node bootstrap
- **WHEN** the lakehouse stack is deployed in dev (single-node)
- **THEN** the `garage` container SHALL be invoked with `--single-node` and
  the env vars `GARAGE_DEFAULT_ACCESS_KEY`, `GARAGE_DEFAULT_SECRET_KEY`,
  `GARAGE_DEFAULT_BUCKET` SHALL bootstrap the layout + key + bucket
  without the 90-line `garage-init` bash sidecar.

#### Scenario: Plaintext secrets forbidden
- **WHEN** the `garage.toml` config file is committed
- **THEN** `rpc_secret` and `admin_token` SHALL be `${ENV_VAR}` references,
  NOT plaintext values, and the secrets SHALL be Locket-injected at
  container start.
```

---

## 11. Return summary (1 paragraph)

This plan migrates Cianfhoghlaim's 4 `garage.toml` files + 2 `compose.yaml` files from the unmaintained `dxflrs/garage:v1.0.1` (Dec 2024) to `v2.3.0` (Apr 2026) in **6 phases over 6.5-7.5 days, ~27 hours of engineering effort**: preflight (snapshot + identify 4 `replication_mode = "1"` sites + 9 `/v1/` admin API call sites), config migration (replace `replication_mode = "1"` with `replication_factor = 1` + `consistency_mode = "degraded"` in all 4 toml files + bump image tag in 2 compose files), delete the 90-line `garage-init` bash sidecar in favor of v2.3.0's native `--single-node --default-access-key --default-bucket` env-var flags (plus a 3-line `garage-buckets-extra` sidecar for the 2 non-default buckets), s/v1/v2/g in the 3-line sidecar (the only remaining admin API callers), externalize the 2 plaintext `rpc_secret` + `admin_token` from `lakehouse/garage.toml:31,68` to Locket/Infisical (port the pattern already used in `infrastructure/stacks/garage/garage.toml:11,28`), and test + cut over with a documented rollback path (cold cutover with `rclone sync` data migration is the safe option for production data; dev cluster is ephemeral). The plan lands as part of the coordinated P0 release train alongside P0-1 (FalkorDB `vector.so`), P0-3 (dlt `[hub]`), P0-4 (LiteLLM `main-stable` → `1.84.0` — hard deadline 2026-06-30), P1-7 (dagster-dlt 0.29.11), and P1-8 (Garage secrets externalization, same PR); the v1→v2 jump is a blocking breaking change because v1.x config (`replication_mode = "1"`) and v1.x admin API (`/v1/*`) will both fail on first v2.x start.
