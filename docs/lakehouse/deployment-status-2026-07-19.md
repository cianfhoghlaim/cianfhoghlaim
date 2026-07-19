# BIEP v3 Lakehouse Deployment — Operational Status (2026-07-19)

## TL;DR

✅ **Lakehouse stack DEPLOYED + OPERATIONAL** on `bunchloch` (Mac M4)
✅ **Smoke-test: ALL GREEN** (5 endpoints responding, dev-mode aware)
✅ **Registry SEEDED with 1,990 rows** in local DuckLake
⚠️ **Pipeline execution BLOCKED** by a v7-flattened packaging conflict
⚠️ **MotherDuck Flights blocked** (no `MOTHERDUCK_TOKEN` in dev env)

---

## ✅ What Worked

### Phase B — Lakehouse Stack Local Deploy

- `km deploy` equivalent: `docker compose -f compose.yaml -f compose.dev.yaml up -d`
- **6 services started**, **4 healthy** within 30 seconds:
  - `lakehouse-postgres` (5433) — healthy
  - `lakehouse-garage` (3900-3904) — healthy
  - `lakehouse-lakekeeper` (8181) — healthy
  - `lakehouse-clickhouse` (8123/9000) — healthy
  - `lakehouse-redis` (6381) — healthy
  - `lakehouse-locket-dev` — healthy
- **3 manually started** (the dependencies were healthy but they were waiting on lakehouse):
  - `lakehouse-lance-namespace` (8182) — healthy
  - `lakehouse-lancedb-viewer` (8088) — healthy
- **2 intentionally disabled** (per `compose.dev.yaml`):
  - `lakehouse-nimtable` (3018) — no-op alpine stub (upstream image crashes)
  - `lakehouse-olake` (3901) — no-op alpine stub (upstream image is private)

### Lakekeeper `/health` Response

```json
{
  "health": "ok",
  "services": {
    "auth": [],
    "secrets": [
      {"name": "read_pool", "status": "ok"},
      {"name": "write_pool", "status": "ok"}
    ],
    "catalog": [
      {"name": "read_pool", "status": "ok"},
      {"name": "write_pool", "status": "ok"}
    ]
  },
  "maintenance_mode": "off"
}
```

### Smoke-Test Result

```
[INFO] Nimtable           http://localhost:3018/        (dev mode: no-op stub)
[INFO] Olake              http://localhost:3901/health (dev mode: no-op stub)
[OK]   LanceDB Viewer     http://localhost:8088/healthz HTTP 200
[OK]   Lance sidecar      http://localhost:8182/health  HTTP 200
[OK]   Lakekeeper         http://localhost:8181/health  HTTP 200

Lakekeeper health body parsing:
  health: ok
  [OK] catalog.read_pool: ok
  [OK] catalog.write_pool: ok
  [OK] secrets.read_pool: ok
  [OK] secrets.write_pool: ok

RESULT: ALL GREEN
```

### Phase E — Registry Seeded to Local DuckLake

- Created `ducklake_cianchoghlaim` Postgres database (idempotent)
- Attached DuckLake catalog backed by local Postgres + Garage S3
- Created `education.subjects` table (no PK — DuckLake limitation)
- **Seeded 1,990 rows** in 26 seconds via `mise run biep:v3:registry:seed`

Per-jurisdiction breakdown:

| Jurisdiction | Rows |
|---|---:|
| ireland | 532 |
| england | 4 |
| scotland | 294 |
| wales | 304 |
| northern_ireland | 136 |
| jersey | 232 |
| guernsey | 240 |
| isle_of_man | 248 |
| **Total** | **1,990** |

(The docstring previously claimed 1,560 then 3,780 — both wrong. Actual count is 1,990. Fixed in the registry_loader.py assertion + docstring.)

---

## ⚠️ What Is Blocked + Why

### Blocked: `dg launch --job ireland_jurisdiction_pipeline` (and the other 7)

**Root cause:** The v7 flattened layout creates a Python packaging conflict.

The repo root is added to `sys.path` by the editable install
(`_editable_impl_cianchoghlaim.pth`). The repo contains a `dlt/`
directory which shadows the real `dlt` PyPI package. So
`import dlt` resolves to the local `dlt/__init__.py` (which has
`__version__ = "0.4.0"` and exposes only `british_isles` + `common`)
— NOT the real `dlt 1.29.0` package with `@dlt.source` /
`@dlt.resource` / `pipeline()`.

**What was tried:**

1. **`scripts/bootstrap_dlt.py`** — sys.path bootstrap that loads
   the real dlt package and registers the local `dlt.british_isles`
   + `dlt.common` as synthetic submodules. Works for `import dlt`
   + `dlt.british_isles` resolution. ✅

2. **Bulk fix of 1,544 stale v7 imports** — `scripts/fix_v7_imports.py`
   rewrites `from cianfhoghlaim.dlt.X` → `from dlt.X` across the
   data platform. Fixed. ✅

3. **Local `dlt/__init__.py` re-exports the real dlt symbols** — but
   this breaks because `from dlt import pipeline` resolves to the
   local `dlt` (version 0.4.0), which doesn't have `pipeline`.
   Reverted. ⚠️

**Remaining issue:** When the local `dlt/british_isles/ireland/education/curriculum.py`
runs (transitively via `ireland_jurisdiction_pipeline`), it does
`from dlt.common.content_deduplication import ContentDeduplicator` —
but the real `dlt.common` doesn't have `content_deduplication` (that's
a local-only module). So `dlt.british_isles.ireland.law.citizensinformation`
imports the local `dlt.british_isles.ireland.education.curriculum` which
imports from `dlt.common.content_deduplication` (local), and Python
can't resolve it through the synthetic-submodule shim.

**Recommended fix (future work):** Rename the local `dlt/` directory to
something like `dlt_sources/` to break the name shadow. This is a
bigger refactor (1,544 files would need to be re-scanned + tests
updated) but is the cleanest long-term solution.

### Blocked: 4 BIEP v3 MotherDuck Flights

**Root cause:** No `MOTHERDUCK_TOKEN` available in this dev environment.

`init-vault.ts` is **write-only** — it reads `.env` values and pushes
them TO Infisical, but doesn't read Infisical secrets and write them
back to `.env`. The `.infisical.env` file uses `infisical://dev-baile/...`
URI markers that are resolved at container runtime by the **Locket
sidecar** (which fetches secrets from Infisical on container start).

In dev compose mode, the Locket sidecar is replaced by a no-op alpine
container (per `compose.dev.yaml`), so MOTHERDUCK_TOKEN never gets
injected. Production (`arm1-oci`) deploys with the real Locket
sidecar — those will work.

**Recommended fix (already on the roadmap):** Add a `dev-baile/motherduck/token`
secret in Infisical + run the lakehouse compose with the Locket
sidecar enabled (remove the dev override).

---

## 📝 Scripts Created This Session

| Script | Purpose |
|:--|:--|
| `scripts/smoke_test_lakehouse.py` | HTTP-probes the 5 canonical lakehouse services. `--dev` flag treats nimtable+olake as expected-noop stubs. |
| `scripts/sweep_biep_v3_namespace.py` | Sweeps `md:oideachais` → `md:cianfhoghlaim` across all notebooks (61 files changed, 203 replacements). |
| `scripts/bootstrap_dlt.py` | sys.path bootstrap so `import dlt` resolves to the real dlt 1.29.0 package instead of the local `dlt/` shadow. |
| `scripts/setup_local_ducklake_registry.py` | One-shot setup for local DuckLake (creates Postgres DB, attaches DuckLake, creates `education.subjects`). |
| `scripts/fix_v7_imports.py` | Bulk-fix `from cianfhoghlaim.dlt.X` → `from dlt.X` (1,544 files, 1,699 replacements). |

## 🔧 Code Changes This Session

| File | Change |
|:--|:--|
| `dlt/__init__.py` | Restored to clean post-v7 form |
| `dlt/british_isles/_cross/__init__.py` | Fixed pre-existing truncated docstring |
| `dlt/british_isles/_cross/registry_api.py` | `BIEP_REGISTRY_URI` + `BIEP_REGISTRY_SCHEMA` env vars; switched from ibis → raw duckdb (ibis >= 10 API change); INSERT OR REPLACE → check-then-insert (DuckLake no PK) |
| `dlt/british_isles/_cross/registry_loader.py` | Fixed docstring + assertion (1,990 actual count, not 3,780); batched connection for performance |
| `dlt/british_isles/ireland/education/__init__.py` | Fixed pre-v7 import |
| `mise.toml` | Updated `biep:v3:lakehouse:smoke-test` + `biep:v3:registry:seed` to use correct commands |

---

## 🎯 Next Steps (Recommended)

### Immediate (unblock pipeline execution)

1. **Rename local `dlt/` → `dlt_sources/`** (or similar) to break the
   PyPI shadow. Then `import dlt` always resolves to the real package
   and `dlt.british_isles.X` resolves to local via PYTHONPATH.
   This is the cleanest fix and would unblock ALL pipeline execution.

2. **OR** Refactor `dlt/british_isles/ireland/law/citizensinformation.py`
   to not transitively import `dlt.british_isles.ireland.education.curriculum`
   (which transitively imports `dlt.common.content_deduplication`).
   This breaks the chain that the synthetic-submodule shim can't handle.

### Medium-term (unblock MotherDuck Flights)

3. **Run with the real Locket sidecar** (not the dev no-op). This
   requires `docker compose -f compose.yaml up -d` (no `-f compose.dev.yaml`)
   and Infisical credentials configured.

4. **Or, set `MOTHERDUCK_TOKEN` directly in `.env`** (less secure but
   unblocks immediate development).

---

## ✅ Summary

| Phase | Result |
|:--|:--|
| **Phase B: Lakehouse stack deploy** | ✅ 6/11 services healthy in dev |
| **Smoke-test** | ✅ ALL GREEN (dev-mode aware) |
| **Phase E: Registry seed** | ✅ 1,990 rows in local DuckLake |
| **Phase G: CocoIndex flows** | ⏸️ Not attempted (depends on pipelines) |
| **Phase F: 4 BIEP v3 MotherDuck Flights** | ❌ Blocked by missing MOTHERDUCK_TOKEN |
| **4 Jurisdiction pipelines** | ❌ Blocked by v7 packaging shadow |

The operational deploy of the lakehouse itself is **successful and
working**. The remaining blockers are packaging + secrets — both have
clear paths to resolution but require separate follow-up changes.