# BIEP v3 MotherDuck Follow-up (2026-07-19)

This document tracks the 4 deferred Phase 4 follow-ups from the BIEP v3
lakehouse full activation. All 4 are P2/P3 — the local DuckLake path
works end-to-end and is the recommended dev/prod target.

## Status

| # | Item | Status | Priority |
|--:|:--|:--|:--|
| 1 | `MOTHERDUCK_TOKEN` injected into dev env | **BLOCKED** — requires Locket sidecar or manual secret | P2 |
| 2 | Notebook migration (MotherDuck → local DuckLake) | **BLOCKED** — depends on #1 | P3 |
| 3 | LanceDB Viewer (port 8081 → port 8088) healthcheck fix | **BLOCKED** — non-blocking | P3 |
| 4 | 4 BIEP v3 MotherDuck Flights registration | **BLOCKED** — depends on #1 | P3 |

---

## 1. `MOTHERDUCK_TOKEN` injection

### Root cause

`init-vault.ts` (in `scripts/`) is **write-only** — it pushes local
`.env` values TO Infisical but does NOT read Infisical secrets back
to `.env`. The `.infisical.env` file uses `infisical://dev-baile/...`
URIs that the **Locket sidecar** resolves at container runtime.

In dev compose (`compose.dev.yaml`), the Locket sidecar is replaced
by a no-op alpine container (per the audit). So `MOTHERDUCK_TOKEN`
never gets injected into `.env` at runtime.

Production (`arm1-oci`) deploys with the REAL Locket sidecar, so
those will work.

### Workarounds (pick one)

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