# Cross-repo-sync: 2026-08-12-biep-v3-motherduck-flights-v1

## Affected repos

- `cianfhoghlaim` (this repo) — MotherDuck Flights + notebook migration
- `bonnegar` (separate repo, not in this worktree) — no changes
  (the local dev compose Locket switch is in this repo)

## Commit plan

### Commit 1 (cianfhoghlaim)

```
1. Edit bonneagar/stacks/lakehouse/compose.dev.yaml
   (replace alpine Locket no-op with real Locket sidecar)
2. Edit notebooks/_shared/db.py (add get_db_uri() helper)
3. Update notebooks/23_8_jurisdiction_overview.py (use get_db_uri())
4. Update notebooks/12_corpus_overview_*.py (use get_db_uri())
5. Add `infisical secrets set MOTHERDUCK_TOKEN` to README onboarding
6. Add 4 acceptance tests:
   - test_motherduck_flight_ireland (triggers + asserts RunRequest)
   - test_motherduck_flight_england
   - test_motherduck_flight_sct_wls_ni
   - test_motherduck_flight_crown_dependencies
```

### No commits in bonnegar (this change doesn't touch the IaC repo)

## Order of operations

1. Operator populates `MOTHERDUCK_TOKEN` in Infisical
2. Commit 1 lands (compose + notebooks)
3. Verify 4 flights execute + emit RunRequests
4. Archive the openspec change

## Push targets

- `origin/openspec/2026-07-25-refactor-batch-v1` (the wave branch)