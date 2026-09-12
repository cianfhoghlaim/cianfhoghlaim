# Change: BIEP v3 jurisdiction sensor jobs (fix the 8 dangling job_name pattern)

## Why

The `orchestration/sensors/` package contains **8 jurisdiction registry
sensors** (`ncca_registry_sensor`, `sqa_registry_sensor`,
`ccea_registry_sensor`, `wjec_registry_sensor`, `jcq_registry_sensor`,
`isle_of_man_registry_sensor`, `jersey_registry_sensor`,
`guernsey_registry_sensor`) that each declare
`@sensor(job_name="<jurisdiction>_registry_change_job")` — but **the
referenced jobs are not defined anywhere in the repo**.

The pattern was discovered and fixed for ONE sensor (the
`garage_pdf_arrival_sensor`) by the
`2026-08-08-lakehouse-extensive-hydration-v1` change, which explicitly
noted at `orchestration/sensors/garage_pdf_arrival_sensor.py:36-38`:

> Note: 8 other sensors in this package (`ncca_registry_sensor`,
> `sqa_registry_sensor`, etc.) have the identical dangling-`job_name`
> pattern — out of scope here, flagged as a separate follow-up.

**Impact (production silent failure)**:

- Each of the 8 sensors polls every 300s.
- On each tick, the sensor may emit one or more `RunRequest`s.
- Dagster then tries to resolve the `RunRequest`'s `run_key` + the
  sensor's `job_name` into a `JobDefinition`. Because
  `<jurisdiction>_registry_change_job` is not defined anywhere,
  Dagster logs a `JobNotFoundError` and silently drops the request.
- The BIEP critical-path auto-refresh — the auto-reingestion of the
  ~1,990 cohorts across 8 jurisdictions when the source registry
  detects a change — is broken at the wire layer for 8 of 8
  jurisdictions.

**Affected asset graph**:

| Sensor | Dangling `job_name=` | Target asset |
|:--|:--|:--|
| `ncca_registry_sensor.py:24` | `ncca_registry_change_job` | `ireland_documents_ingested` |
| `sqa_registry_sensor.py:19` | `sqa_registry_change_job` | `scotland_documents_ingested` |
| `ccea_registry_sensor.py:19` | `ccea_registry_change_job` | `northern_ireland_documents_ingested` |
| `wjec_registry_sensor.py:19` | `wjec_registry_change_job` | `wales_documents_ingested` |
| `jcq_registry_sensor.py:19` | `jcq_registry_change_job` | `england_documents_ingested` |
| `isle_of_man_registry_sensor.py:19` | `isle_of_man_registry_change_job` | `isle_of_man_documents_ingested` |
| `jersey_registry_sensor.py:19` | `jersey_registry_change_job` | `jersey_documents_ingested` |
| `guernsey_registry_sensor.py:19` | `guernsey_registry_change_job` | `guernsey_documents_ingested` |

All 8 target assets exist in the live tree (verified via `grep
"<jurisdiction>_documents_ingested = " orchestration/defs/`), so this
is a pure "wire the missing `define_asset_job`" change.

## What Changes

- Add `orchestration/sensors/jobs.py` — a single new module that
  defines all 8 `define_asset_job` instances (mirroring the proven
  pattern at `garage_pdf_arrival_sensor.py:39-42`).
- Update `orchestration/sensors/__init__.py` to re-export the 8 new
  job instances.
- Add an `agent-platform-cluster` spec delta (1 ADDED Requirement) that
  formally captures the "every registry sensor must have a defined
  `define_asset_job`" invariant — preventing future regressions.

No production code paths change behaviour beyond fixing the silent
failure; this is purely a wiring fix.

## Dependencies

`Blocked by: none`. `Affected repos: cianfhoghlaim (single repo)`.

## Impact

- Capabilities: MODIFIED `agent-platform-cluster` (1 ADDED Requirement
  formalising the "no dangling job_name" invariant).
- Code: `orchestration/sensors/jobs.py` (new, ~50 LOC);
  `orchestration/sensors/__init__.py` (8 re-export additions).
- Risk: low — purely additive wiring; existing sensors untouched.
- Restore: BIEP critical-path auto-refresh across 8 jurisdictions.
