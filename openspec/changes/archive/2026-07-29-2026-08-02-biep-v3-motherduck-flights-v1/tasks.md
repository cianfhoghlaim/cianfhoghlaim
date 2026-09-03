# 2026-08-02-biep-v3-motherduck-flights-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify A1 (dlt bugfix) merged
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Create the 4 missing jurisdiction MotherDuck Flights

- [ ] Create `motherduck/flights/ireland_full_coverage_flight.sql` — daily
  02:00 UTC, scans `s3://garage/cianfhoghlaim/ireland/`
- [ ] Create `motherduck/flights/england_full_coverage_flight.sql` — daily
  03:00 UTC, scans `s3://garage/cianfhoghlaim/england/`
- [ ] Create `motherduck/flights/sct_wls_ni_flight.sql` — daily
  04:00 UTC, scans `s3://garage/cianfhoghlaim/{scotland,wales,northern_ireland}/`
- [ ] Create `motherduck/flights/crown_dependencies_flight.sql` — daily
  04:30 UTC, scans `s3://garage/cianfhoghlaim/{jersey,guernsey,isle_of_man}/`

## Stage 2 — Fix the 2 existing flights' `md_oideachais` typo

- [ ] Edit `motherduck/flights/eng_daily_sync_flight.sql:11` —
  `DATABASE md_oideachais` → `ATTACH 'md:cianfhoghlaim' AS md_cianfhoghlaim`
- [ ] Edit `motherduck/flights/jc_pdf_sync_flight.sql:18` — same fix

## Stage 3 — Update `motherduck/flights/config.yaml`

- [ ] Register the 4 new flights with cron + tags

## Stage 4 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-08-02-biep-v3-motherduck-flights-v1/specs/motherduck-dive/spec.md`
  (or whichever canonical spec the MotherDuck flights belong to)
- [ ] Run `openspec validate 2026-08-02-biep-v3-motherduck-flights-v1 --strict`
- [ ] Commit the change on a dedicated branch
- [ ] Open a PR on `origin/main` referencing this change
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-08-02-biep-v3-motherduck-flights-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol