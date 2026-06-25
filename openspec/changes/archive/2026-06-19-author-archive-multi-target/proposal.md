# Author-Archive v1: Multi-Target Deployment

## Why

Stages 0.5-3 of `author-archive-v1` shipped code that runs against a
single target (the local DuckDB in `~/.cache/sruth/oideachais/`). The
codebase has a `oideachais.dlt_utils.destinations` module with
DuckLake wiring, but the Dagster assets and the DLT sources are hard-
coded to local DuckDB.

The user has a 3-tier deployment topology:

  1. **dev** — local DuckDB on the workstation (CI + quick local runs)
  2. **staging** — MotherDuck (managed DuckDB in the cloud, pre-prod)
  3. **prod** — Garage S3 + Lakekeeper (full lakehouse)

Stage 4 introduces a `Target` dataclass + a factory that resolves a
target name to a DLT pipeline configured for the right destination.
A `make_target.sh` CLI helper wraps the env-var setup so the user can
do `./make_target.sh prod python -c "..."` without manually exporting
the 6 DUCKLAKE_* vars + BUCKET.

## What Changes

### Code

- `sruth/oideachais/dlt_utils/target_factory.py` (NEW): the `Target`
  dataclass + 3 canonical instances (`DEV`, `STAGING`, `PROD`) +
  `get_target(name)` + `validate_target_secrets(target)` +
  `create_pipeline_for_target(target_name, pipeline_name, dataset_name)`
  + 3 shortcut functions (`create_dev_pipeline`, `create_staging_pipeline`,
  `create_prod_pipeline`).

- `sruth/oideachais/scripts/make_target.sh` (NEW, 100 LOC): the CLI helper.
  Validates the target name, sources the env file, exports
  `OIDEACHAIS_TARGET`, runs the pre-flight secret check, and execs
  the user-supplied command.

### Spec deltas

- `author-archive-multi-target/spec.md` — the 3 targets + the
  factory contract

## Impact

- Dagster assets can be deployed to staging or prod by setting
  `OIDEACHAIS_TARGET=staging` (or `prod`) without code changes.
- The CLI helper gives a single entry point for any author-archive
  pipeline command.
- The pre-flight secret check prevents accidental staging/prod
  deployments when required env vars are missing.

## Out of scope (deferred)

- Dagster code-locations for staging and prod (the user runs
  `dagster dev` locally and `dagster-webserver` on the workstation;
  the staging/prod deployments are scheduled via Komodo in a
  follow-up change)
- Pulumi / Komodo updates to deploy the 3 targets as separate
  Docker stacks
- Per-target IAM roles (the staging/prod targets reuse the same
  Komodo service account for now)
