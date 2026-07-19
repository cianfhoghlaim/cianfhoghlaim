# 2026-08-12-biep-v3-motherduck-flights-v1

## Why

The 4 BIEP v3 MotherDuck Flights (`ireland_full_coverage_flight`,
`england_full_coverage_flight`, `sct_wls_ni_flight`,
`crown_dependencies_flight`) were added to
`motherduck/flights/config.yaml` in the 2026-08-10 preflight change
but cannot actually execute until `MOTHERDUCK_TOKEN` is wired into
the dev environment.

This change:
1. Populates `dev-baile/motherduck/token` in Infisical (operator task)
2. Switches the local dev compose to use the REAL Locket sidecar
   (instead of the no-op alpine stub)
3. Verifies the 4 BIEP v3 Flights execute + emit Dagster `RunRequest`s
4. Migrates 8-jurisdiction overview + 12 corpus overview notebooks
   from `md:cianfhoghlaim` to a configurable URI (local DuckLake OR
   MotherDuck)

## What changes

### 1. Infisical secret population (operator task)

```bash
infisical secrets set MOTHERDUCK_TOKEN=<token> --env=dev-baile --path=/motherduck
```

Or via the Infisical UI: `Settings → Machine Identities → secret-name=MOTHERDUCK_TOKEN`.

### 2. Local dev compose switch to real Locket

`bonneagar/stacks/lakehouse/compose.dev.yaml`:
- Remove the alpine no-op Locket override
- Use the real `ghcr.io/bpbradley/locket:infisical` image with
  `infisical://dev-baile/lakehouse/*` secrets

### 3. Verify 4 BIEP v3 Flights

```bash
dg list jobs | grep full_coverage
# Should show:
#   ireland_full_coverage_flight
#   england_full_coverage_flight
#   sct_wls_ni_flight
#   crown_dependencies_flight

dg launch --job ireland_full_coverage_flight
dg launch --job england_full_coverage_flight
dg launch --job sct_wls_ni_flight
dg launch --job crown_dependencies_flight
```

### 4. Notebook migration

Update `notebooks/_shared/db.py` to support both URIs:

```python
import os
def get_db_uri():
    if os.getenv("CIANFHOGHLAIM_USE_MOTHERDUCK", "false") == "true":
        return "md:cianfhoghlaim"
    return os.getenv("BIEP_REGISTRY_URI", "ducklake:postgres:...")
```

Then update each notebook's `connect_md()` calls to `get_db_uri()`.

## Dependencies

Blocked by (soft): 2026-08-10-biep-v3-preflight-bug-fixes-v1 (already archived)
Blocks: nothing (final cleanup phase)

Affected repos: cianfhoghlaim

## Acceptance

- [ ] `infisical secrets get MOTHERDUCK_TOKEN --env=dev-baile` returns a non-empty value
- [ ] `mise run biep:v3:lakehouse:smoke-test` still passes after Locket switch
- [ ] `dg list jobs | grep full_coverage` shows 4 BIEP v3 flights
- [ ] Manual trigger of each flight emits at least 1 Dagster `RunRequest`
- [ ] `notebooks/23_8_jurisdiction_overview.py` runs against MotherDuck (when flag set)
- [ ] `notebooks/12_corpus_overview_05_baml_extraction_log_viewer.py` shows recent BAML extraction logs

## Out of scope

- Migration of the registry to MotherDuck (the registry stays in local DuckLake)
- Re-architecting the destination factory to use MotherDuck-managed storage
- 4 OpenSpec change archive cleanup

## Reference

- Full operational status: `docs/lakehouse/deployment-status-2026-07-19.md`
- MotherDuck follow-up: `docs/lakehouse/followup-2026-07-19-motherduck.md`
- Locket sidecar spec: `.agents/skills/secrets-management/SKILL.md`