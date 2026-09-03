# 2026-08-11-biep-v3-lakehouse-population-v1

## Why

The BIEP v3 stack is fully implemented and tested at the code level
(see the 2026-08-06 → 09 hardening batch + the 2026-08-10 preflight
bug fixes), but the lakehouse has never been populated end-to-end.

This change executes the operational deployment + initial population:

1. Deploy the 11-service Lakehouse stack to `bunchloch` (Mac M4) via
   Komodo (`km deploy stack lakehouse-bunchloch --action=up`).
2. Seed the 3,780-row BIEP v3 subject registry.
3. Run all 4 BIEP v3 jurisdiction pipelines (Ireland / England /
   SCT+WLS+NI / Crown Dependencies) → writes to local DuckLake.
4. Wire the 8 CocoIndex v1 BIIP parity flows + the new
   `consume_voted_ducklake_to_lance()` consumer.
5. Trigger the 4 BIEP v3 MotherDuck Flights (post-YAML-fix from the
   2026-08-10 preflight change) and validate they emit Dagster
   `RunRequest`s.
6. Sweep the ~25 notebooks still referencing `md:oideachais` to
   `md:cianfhoghlaim` (completing the P0 namespace rename from the
   2026-08-06 critical-path batch).

This is the operational counterpart to the preflight bug fixes —
once the bugs are fixed (P0), we deploy + populate the lakehouse (P1).

## What changes

This is primarily an **operational** change, not a code change. No
new features or refactors. The work is to:

1. Run the lakehouse deploy commands.
2. Run `seed_registry()`.
3. Run the 4 jurisdiction pipelines.
4. Run the CocoIndex flows.
5. Run the 4 BIEP v3 MotherDuck Flights.
6. Run the notebook namespace sweep (`scripts/refactor-biep-notebooks.py`).

## Dependencies

```yaml
Blocked by: 2026-08-10-biep-v3-preflight-bug-fixes-v1
Blocked by (soft): 2026-08-09-biep-v3-cross-cutting-docs-v1
Affected repos: cianfhoghlaim
```

## Destination strategy

`DLT_ENVIRONMENT=local` + `MOTHERDUCK_MODE=byob` for the first run.
Local Postgres (`localhost:5433`) + Garage S3 (`http://localhost:3900`).

PlanetScale is **NOT** in this scope — Phase B.0 hard-switch is
deferred per the user's audit decision.

## Acceptance gates

- `openspec validate 2026-08-11-biep-v3-lakehouse-population-v1 --strict` passes
- All 3 lakehouse services return 200 from `mise run biep:v3:lakehouse:smoke-test`
- Lakekeeper `/health/deep` returns `{"postgres": "healthy", "s3": "healthy"}`
- `seed_registry()` returns counts matching 3,780-row assertion
- All 4 jurisdiction pipelines complete successfully (8 jurisdictions total)
- 8 jurisdiction namespaces exist in Lakekeeper (`GET /v1/namespaces`)
- All 4 BIEP v3 MotherDuck Flights visible in `dg list jobs`
- `consume_voted_ducklake_to_lance()` populates at least 6 LC6 subjects × 8 jurisdictions in LanceDB
- `grep -rn "md:oideachais" notebooks/ | wc -l` returns 0
- `notebooks/23_8_jurisdiction_overview.py` runs successfully against the populated registry
- All 4 BIEP v3 MotherDuck Flights emit at least 1 Dagster `RunRequest` each

## Cross-references

- `dlt/common/destinations_cianfhoghlaim.py` (the canonical destination factory)
- `dlt/common/ducklake_pool.py` (DuckLakeConnectionPool + time_travel_query)
- `dlt/british_isles/_cross/registry_loader.py` (the canonical seed_registry)
- `motherduck/flights/config.yaml` (the flight registry, fixed in 2026-08-10)
- `scripts/refactor-biep-notebooks.py` (the canonical namespace sweep script)
- `bonneagar/stacks/lakehouse/compose.yaml` (the 11-service lakehouse stack)
- `.agents/skills/motherduck/SKILL.md` (MotherDuck destination modes)
- `.agents/skills/dlt/SKILL.md` (DLT patterns)