# Tasks for 2026-08-12-biep-v3-motherduck-flights-v1

## 1. Populate MOTHERDUCK_TOKEN in Infisical
- [ ] Operator task: `infisical secrets set MOTHERDUCK_TOKEN=<token> --env=dev-baile --path=/motherduck`
- [ ] Verify: `infisical secrets get MOTHERDUCK_TOKEN --env=dev-baile` returns the token

## 2. Switch dev compose to real Locket sidecar
- [ ] Edit `bonneagar/stacks/lakehouse/compose.dev.yaml`
- [ ] Remove the alpine no-op Locket override
- [ ] Use the real `ghcr.io/bpbradley/locket:infisical` image
- [ ] Restart the lakehouse stack + verify secrets resolve

## 3. Verify 4 BIEP v3 MotherDuck Flights
- [ ] `dg list jobs | grep full_coverage` shows 4 flights
- [ ] `dg launch --job ireland_full_coverage_flight` succeeds
- [ ] `dg launch --job england_full_coverage_flight` succeeds
- [ ] `dg launch --job sct_wls_ni_flight` succeeds
- [ ] `dg launch --job crown_dependencies_flight` succeeds
- [ ] Each emits at least 1 Dagster `RunRequest` event in the event log

## 4. Notebook migration (optional)
- [ ] Update `notebooks/_shared/db.py` with `get_db_uri()` helper
- [ ] Update `notebooks/23_8_jurisdiction_overview.py`
- [ ] Update `notebooks/12_corpus_overview_*.py` (10 notebooks)
- [ ] Verify notebooks run against MotherDuck + local DuckLake

## 5. Final cleanup
- [ ] Archive this openspec change after verification: `openspec archive 2026-08-12-biep-v3-motherduck-flights-v1 --yes`
- [ ] Update `docs/lakehouse/deployment-status-2026-07-19.md` to mark all 4 follow-ups resolved