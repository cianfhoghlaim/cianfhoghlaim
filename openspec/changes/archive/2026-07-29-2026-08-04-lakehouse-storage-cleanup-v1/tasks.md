# 2026-08-04-lakehouse-storage-cleanup-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Smoke-test the 3 lakehouse services (closes #89)

- [ ] `cd /Users/cianmacandeisigh/dev/kings_college_galway/bonnegar`
- [ ] `docker compose -f stacks/lakehouse/compose.yaml up -d`
- [ ] `curl -s http://localhost:3018/api/v1/health | jq .` (Nimtable)
- [ ] `curl -s http://localhost:3901/v1/databases | jq .` (Olake)
- [ ] `curl -s http://localhost:8081/health | jq .` (LanceDB Viewer)
- [ ] Run a 1-row round-trip: write to Nimtable → query via Olake →
  embed in LanceDB
- [ ] Document the smoke-test results in
  `docs/lakehouse/smoke-test-2026-08-04.md`

## Stage 2 — Delete the 3 standalone IaC stacks (closes #90)

- [ ] `git rm -r stacks/olake/`
- [ ] `git rm -r stacks/nimtable/`
- [ ] `git rm -r stacks/lancedb-viewer/`
- [ ] `git rm komodo/stacks/olake.toml`
- [ ] `git rm komodo/stacks/nimtable.toml`
- [ ] `git rm komodo/stacks/lancedb-viewer.toml`
- [ ] `git rm komodo/procedures/deploy-olake.toml` (if exists)
- [ ] `git rm komodo/procedures/deploy-nimtable.toml` (if exists)
- [ ] `git rm komodo/procedures/deploy-lancedb-viewer.toml` (if exists)
- [ ] Edit `iac/sources/key-stacks.ts:55-85` to remove the 3 entries
- [ ] Edit `openspec/specs/infrastructure-stacks/spec.md` to drop the 3 names
- [ ] `bun run iac:health` — verify all 88+ stacks still resolve

## Stage 3 — Migrate any consumer

- [ ] `grep -r "olake\|nimtable\|lancedb-viewer" bonnegar/ --include="*.yaml"
  --include="*.toml"` — fix any remaining references
- [ ] Update any CI workflows that boot these stacks

## Stage 4 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-08-04-lakehouse-storage-cleanup-v1/specs/infrastructure-stacks/spec.md`
- [ ] Run `openspec validate 2026-08-04-lakehouse-storage-cleanup-v1 --strict`
- [ ] Commit the change on a dedicated branch
- [ ] Open a PR on `origin/main` referencing this change
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-08-04-lakehouse-storage-cleanup-v1 --yes`

## Stage 5 — Close the GitHub issues

- [ ] `gh issue close 89 --comment "Closes via 2026-08-04-lakehouse-storage-cleanup-v1"`
- [ ] `gh issue close 90 --comment "Closes via 2026-08-04-lakehouse-storage-cleanup-v1"`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol