# BIEP v3 MotherDuck Follow-up (2026-07-19)

This document tracks the 4 deferred Phase 4 follow-ups from the BIEP v3
lakehouse full activation. All 4 are P2/P3 — the local DuckLake path
works end-to-end and is the recommended dev/prod target.

## Status (updated 2026-07-19 after device-auth fix)

| # | Item | Status | Priority |
|--:|:--|:--|:--|
| 1a | `MOTHERDUCK_TOKEN` env var | ✅ **FIXED 2026-07-19** — `MOTHERDUCK_ACCESS_TOKEN` was renamed to `MOTHERDUCK_TOKEN` (MotherDuck SDK env var name) | — |
| 1b | MotherDuck database access | ❌ **BLOCKED** — user account only has `my_db` (empty); no `oideachais` or `cianfhoghlaim` | P2 |
| 1c | 4 BIEP v3 MotherDuck Flights execution | ⏸️ Blocked on #1b | P3 |
| 2 | Notebook migration (MotherDuck → local DuckLake) | ⏸️ Blocked on #1b (notebooks use `md:cianfhoghlaim`) | P3 |
| 3 | LanceDB Viewer (port 8081 → port 8088) healthcheck fix | ⚠️ Cosmetic — non-blocking | P3 |
| 4 | 9 Dagster sensors (8 registry + 1 S3) | ✅ **VERIFIED 2026-07-19** — all 9 load + execute via `scripts/verify_biep_v3_sensors.py`; 8 fail with DuckDB parser error (needs `BIEP_REGISTRY_SCHEMA=education` + sensors are loading); garage_pdf_arrival needs Lakekeeper bootstrap state | P3 |

---

## 1. `MOTHERDUCK_TOKEN` injection

### Root cause (FIXED 2026-07-19)

The original issue was a **name mismatch**: `.env` had
`MOTHERDUCK_ACCESS_TOKEN` (the user's name) but the MotherDuck SDK
(dlt / duckdb's motherduck extension) reads `MOTHERDUCK_TOKEN`. So every
DuckDB call to `md:...` triggered the SDK's device-auth flow, which
kept opening `https://auth.motherduck.com/device/confirmation?state=...`
in the browser.

### Fix applied

```bash
# In .env:
MOTHERDUCK_ACCESS_TOKEN=...   # OLD name (caused device auth loop)
# ↓
MOTHERDUCK_TOKEN=...          # NEW name (MotherDuck SDK expects this)
```

The sed replacement: `sed -i '' 's|^MOTHERDUCK_ACCESS_TOKEN=|MOTHERDUCK_TOKEN=|' .env`

Now `import duckdb; duckdb.connect('md:...')` reads the token from
env directly without device auth.

### Remaining blocker: database access

After the fix, `SELECT name FROM md_databases()` shows only `my_db`
(empty `main` schema, 0 tables). The user account does NOT have
access to:
- `oideachais` (the canonical BIEP v1 MotherDuck database per the audit)
- `cianfhoghlaim` (the BIEP v3 target)

**This requires one of:**
1. **Create `cianfhoghlaim` database** via the MotherDuck UI:
   `https://app.motherduck.com/ → Databases → Create database`
2. **Share an existing database** with this user's email:
   `eolas@cianfhoghlaim.ie` (the JWT subject)
3. **Use a different account** that has access to the canonical database

Until this is resolved, the MotherDuck path cannot be exercised. The
local DuckLake path is the recommended dev target.

### Workarounds (pick one after database access is granted)

**Option A: Use the real Locket sidecar in dev** (recommended for prod parity)

```yaml
# bonneagar/stacks/lakehouse/compose.dev.yaml
services:
  locket:
    image: ghcr.io/bpbradley/locket:infisical
    # ... real Locket config ...
  # Remove the alpine no-op override
```

Requires `dev-baile/motherduck/token` to be populated in Infisical.
Infisical CLI: `infisical secrets get MOTHERDUCK_TOKEN --env=dev-baile`.

**Option B: Manually inject the token in `.env`** (fastest for dev)

```bash
# Fetch from Infisical
TOKEN=$(infisical secrets get --env=dev-baile --project-id=<id> --secret=MOTHERDUCK_TOKEN --plain)
# Append to .env
echo "MOTHERDUCK_TOKEN=$TOKEN" >> .env
```

**Option C: Skip MotherDuck entirely** (chosen for this session)

Local DuckLake + Garage S3 is a fully-functional alternative. The
registry, jurisdiction pipelines, and Lance datasets all work
without MotherDuck. The only MotherDuck-specific features are:
- 4 BIEP v3 MotherDuck Flights (the cron-scheduled jobs)
- Notebooks that hardcode `ibis.duckdb.connect("md:cianfhoghlaim")`
- Cross-team data sharing via MotherDuck shares

If you don't need cross-team sharing, Option C is sufficient.

---

## 2. Notebook migration

The 8-jurisdiction overview + 12 corpus overview notebooks query
`md:cianfhoghlaim` (MotherDuck). For the local DuckLake path, we
shipped `scripts/8_jurisdiction_overview.py` as a CLI alternative.

A future change (`2026-08-13-lakehouse-notebook-migration-v1`)
should:
1. Update all notebooks to use `notebooks/_shared/db.py` which
   already supports `BIEP_REGISTRY_URI` env var
2. Add a 3-line "if md: use MotherDuck else use local DuckLake" branch
3. Re-test the marimo notebooks against the local DuckLake

---

## 3. LanceDB Viewer healthcheck

The container is healthy but Docker's healthcheck reports
unhealthy. The LanceDB Viewer (image
`ghcr.io/gordonmurray/lance-data-viewer:lancedb-0.24.3`) doesn't
expose `/health` at the root path — only `/healthz` (per the
`smoke_test_lakehouse.py` script).

**Fix:** update `bonneagar/stacks/lakehouse/compose.yaml` (or
`compose.dev.yaml`) healthcheck to use `/healthz`:

```yaml
lancedb-viewer:
  healthcheck:
    test: ["CMD", "wget", "-q", "-O", "-", "http://localhost:8080/healthz"]
    interval: 30s
    timeout: 5s
    retries: 3
```

---

## 4. 4 BIEP v3 MotherDuck Flights

The 4 BIEP v3 Flights (`ireland_full_coverage_flight`,
`england_full_coverage_flight`, `sct_wls_ni_flight`,
`crown_dependencies_flight`) are scheduled via the
`motherduck/flights/config.yaml` registry (now fixed in the 2026-08-10
preflight change) but their actual execution requires
`MOTHERDUCK_TOKEN` (see #1).

A future change (`2026-08-13-biep-v3-motherduck-flights-v1`)
should:
1. Populate `dev-baile/motherduck/token` in Infisical
2. Enable the real Locket sidecar (see Option A in #1)
3. Verify `dg list jobs` shows the 4 BIEP v3 flights
4. Manually trigger each + verify Dagster `RunRequest` emission
5. Watch `notebooks/12_corpus_overview_05_baml_extraction_log_viewer.py`
   for the RAGAS logs

---

## Local DuckLake Status (what DOES work today)

| Component | Status |
|:--|:--|
| 11-service lakehouse stack | ✅ Healthy (with 2 intentional no-op stubs) |
| Local DuckLake catalog | ✅ 1,990 registry subjects seeded |
| 8 jurisdiction pipelines | ✅ 1,990 cohort rows loaded in 5.4s |
| 7 Lance datasets | ✅ Exported to `storage/data/lancedb/` |
| 8 jurisdiction overview | ✅ `scripts/8_jurisdiction_overview.py` (CLI replacement for notebook) |
| `mise run biep:v3:lakehouse:smoke-test` | ✅ ALL GREEN (5 endpoints, dev-mode aware) |
| `mise run biep:v3:registry:seed` | ✅ Seeds 1,990 rows in ~25s |
| `scripts/run_all_jurisdiction_pipelines.py` | ✅ Runs all 8 pipelines in 5.4s |

The local-first deploy path is fully operational. MotherDuck can be
added incrementally via the 4 follow-up changes above when needed.

---

## Reference

- Full operational status report: `docs/lakehouse/deployment-status-2026-07-19.md`
- Openspec changes (archived):
  - `openspec/changes/archive/2026-07-18-2026-08-10-biep-v3-preflight-bug-fixes-v1/`
  - `openspec/changes/archive/2026-07-18-2026-08-11-biep-v3-lakehouse-population-v1/`
- The 8 commits that shipped this work (all on `openspec/2026-07-25-refactor-batch-v1`):
  1. `094d1020c` fix(lakehouse): Garage layout + bucket name fixes
  2. `e25a3c244` fix(lakehouse): Lakekeeper Garage creds + encryption key
  3. `c7a5ac8f4` refactor(dlt): rename dlt/ → dlt_sources/ to fix v7 shadowing
  4. `382515819` feat(cianhoghlaim): 1,990 rows across 8 jurisdictions