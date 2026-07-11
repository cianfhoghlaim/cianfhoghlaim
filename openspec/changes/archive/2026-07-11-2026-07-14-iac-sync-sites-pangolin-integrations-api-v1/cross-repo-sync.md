# Cross-repo Sync Plan: 2026-07-14-iac-sync-sites-pangolin-integrations-api-v1

## Commit 1 — bonneagar repo

- **Branch:** `pick-5b-bonneagar-v5-continuation`
- **Files (3 NEW + 3 EDIT):**
  - `iac/commands/sync-sites.ts` (NEW, ~120 LOC)
  - `iac/sources/discover-sites.ts` (NEW, ~60 LOC)
  - `stacks/newt/site.yaml` (NEW)
  - `iac/cli.ts` (EDIT — add `sync:sites` case)
  - `iac/commands/bootstrap.ts` (EDIT — replace Phase 6 TODO with `await syncSites()`)
  - `package.json` (EDIT — add `iac:sync:sites` script)

```
git -C kings_college_galway/bonneagar add iac/commands/sync-sites.ts iac/sources/discover-sites.ts stacks/newt/site.yaml iac/cli.ts iac/commands/bootstrap.ts package.json
git -C kings_college_galway/bonneagar commit -m "feat(iac): sync-sites command — provision newt sites via Pangolin Integrations API"
git -C kings_college_galway/bonneagar push origin pick-5b-bonneagar-v5-continuation
```

## Commit 2 — cianfhoghlaim repo

- **Branch:** `pick-4-biep-v1`
- **Files (4):**
  - `openspec/changes/2026-07-14-iac-sync-sites-pangolin-integrations-api-v1/proposal.md` (NEW)
  - `openspec/changes/2026-07-14-iac-sync-sites-pangolin-integrations-api-v1/tasks.md` (NEW)
  - `openspec/changes/2026-07-14-iac-sync-sites-pangolin-integrations-api-v1/cross-repo-sync.md` (NEW, this file)
  - `openspec/changes/2026-07-14-iac-sync-sites-pangolin-integrations-api-v1/specs/agent-platform-cluster/spec.md` (NEW, 1 ADDED Requirement)

```
git add openspec/changes/2026-07-14-iac-sync-sites-pangolin-integrations-api-v1/
git commit -m "feat(openspec): iac:sync:sites for Pangolin Integrations API v1"
git push origin pick-4-biep-v1
```

## Post-push: archive

```
openspec archive 2026-07-14-iac-sync-sites-pangolin-integrations-api-v1 --yes
```
