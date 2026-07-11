# Tasks: 2026-07-14-iac-sync-sites-pangolin-integrations-api-v1

## Phase 0 — Read baseline

- [x] Read `iac/commands/sync-resources.ts` (the template)
- [x] Read `iac/sources/discover-resources.ts`
- [x] Read `iac/auth.ts` to confirm `ensurePangolinAuth()` is ready
- [x] Read `iac/clients/pangolin-client.ts` to confirm `createSite()` + `getSite()` exist

## Phase 1 — Bonneagar code changes

- [x] Create `iac/commands/sync-sites.ts` (~120 LOC)
  - Walks `stacks/*/site.yaml`
  - For each: `GET /org/{orgId}/site/{niceId}` to check existence
  - If not exists: `POST /org/{orgId}/site` → returns `{ id, newtId, newtSecret }`
  - Writes credentials to local `.env` + Infisical
  - Idempotent: re-runs skip existing sites
- [x] Create `iac/sources/discover-sites.ts` (~60 LOC)
- [x] Create `stacks/newt/site.yaml` (the bunchloch-newt site declaration)
- [x] Wire into `iac/cli.ts` (add `sync:sites` case to dispatcher)
- [x] Wire into `iac/commands/bootstrap.ts` (replace Phase 6 TODO with `await syncSites()`)
- [x] Wire into `package.json` (add `iac:sync:sites` script)

## Phase 2 — Openspec change

- [x] Write `proposal.md`
- [x] Write `cross-repo-sync.md`
- [x] Write `tasks.md` (this file)
- [x] Write `specs/agent-platform-cluster/spec.md` with 1 ADDED Requirement:
  - `### Requirement: iac:sync:sites provisions newt sites via the Pangolin Integrations API`
  - 3 Scenarios: new site is provisioned, existing site is skipped, credentials written to .env

## Phase 3 — Validate + commit + push

- [ ] `openspec validate 2026-07-14-iac-sync-sites-pangolin-integrations-api-v1 --strict` returns 0
- [ ] `bun run iac:plan` discovers the bunchloch-newt site (smoke test)
- [ ] `bun run iac:sync:sites --dry-run` reports the correct action
- [ ] Commit on `pick-5b-bonneagar-v5-continuation`
- [ ] Push bonneagar branch
- [ ] Commit on `pick-4-biep-v1`
- [ ] Push cianfhoghlaim branch

## Phase 4 — Archive

- [ ] `openspec archive 2026-07-14-iac-sync-sites-pangolin-integrations-api-v1 --yes`
