# 2026-08-02-biep-v3-motherduck-flights-v1

## Why

The BIEP v3 batch shipped 5 generic jurisdiction pipelines covering
~1,560 cohorts across 8 British Isles jurisdictions. But only 2
MotherDuck Flights exist:
- `jc_pdf_sync_flight.sql` (BIEP v2 — JC only)
- `eng_daily_sync_flight.sql` (BIEP v2 — England only)

Neither covers Ireland (LC + JC + CBAs), Scotland, Wales, NI, or
the 3 Crown Dependencies. The 4 missing jurisdiction flights
(per the BIEP v3 proposal) need to be created.

This is the B1 change. It lives in the **cianfhoghlaim repo** (the
MotherDuck stack is at `motherduck/flights/`).

## What changes

### 1. Create the 4 missing jurisdiction MotherDuck Flights

- `motherduck/flights/ireland_full_coverage_flight.sql` (new) — daily
  02:00 UTC, scans `s3://garage/cianfhoghlaim/ireland/`
- `motherduck/flights/england_full_coverage_flight.sql` (new) — daily
  03:00 UTC, scans `s3://garage/cianfhoghlaim/england/`
- `motherduck/flights/sct_wls_ni_flight.sql` (new) — daily 04:00 UTC,
  scans `s3://garage/cianfhoghlaim/{scotland,wales,northern_ireland}/`
- `motherduck/flights/crown_dependencies_flight.sql` (new) — daily
  04:30 UTC, scans `s3://garage/cianfhoghlaim/{jersey,guernsey,isle_of_man}/`

### 2. Fix the 2 existing flights' `md_oideachais` typo

- `motherduck/flights/eng_daily_sync_flight.sql:11` —
  `DATABASE md_oideachais` → `ATTACH 'md:cianfhoghlaim' AS md_cianfhoghlaim`
- `motherduck/flights/jc_pdf_sync_flight.sql:18` — same fix

### 3. Update `motherduck/flights/config.yaml`

- Register the 4 new flights with cron + tags

## Dependencies

```yaml
Blocked by: 2026-08-01-biep-v3-dlt-jurisdiction-pipeline-bugfix-v1
Blocked by (soft): 2026-07-31-biep-v3-crown-dependencies-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `duckdb -c "SELECT name FROM motherduck_dwh.flights WHERE name LIKE '%cianfhoghlaim%'"`
  returns 6 entries (2 fixed + 4 new)
- All 4 new flights are scheduled at the correct UTC time
- `openspec validate 2026-08-02-biep-v3-motherduck-flights-v1 --strict` passes

## Cross-references

- `motherduck/flights/{eng_daily_sync,jc_pdf_sync}_flight.sql` (existing)
- `motherduck/flights/config.yaml` (existing)
- `dlt/british_isles/ireland/education/ireland_jurisdiction_pipeline.py` (B1 consumer)
- `dlt/british_isles/england/education/england_jurisdiction_pipeline.py` (B1 consumer)
- `dlt/british_isles/sct_wls_ni/education/sct_wls_ni_jurisdiction_pipeline.py` (B1 consumer)
- `dlt/british_isles/crown_dependencies/education/crown_dependencies_jurisdiction_pipeline.py` (B1 consumer)