# 2026-08-04-lakehouse-storage-cleanup-v1

## Why

The 3 standalone IaC stacks (`olake`, `nimtable`, `lancedb-viewer`)
live at `bonnegar/stacks/{olake,nimtable,lancedb-viewer}/` and
duplicate functionality the canonical `lakehouse` stack now provides.
The `lakehouse` stack at `bonnegar/stacks/lakehouse/compose.yaml` ships
Nimtable + Olake + LanceDB Viewer as sidecar services (per the
2026-07 BIEP v2-era change that added them). Issue #90 says
"delete after the release cycle" — that release cycle is now complete.
Issue #89 says "smoke-test the 3 new lakehouse services" — they're
already shipped but never tested end-to-end.

This change closes both issues. It lives in the **bonneagar repo**
(not the cianfhoghlaim repo) per the post-v7 flatten split.

## What changes

### 1. Smoke-test the 3 lakehouse services (closes #89)

- `docker compose -f bonnegar/stacks/lakehouse/compose.yaml up -d`
- curl `http://localhost:3018/api/v1/health` (Nimtable)
- curl `http://localhost:3901/v1/databases` (Olake)
- curl `http://localhost:8081/health` (LanceDB Viewer)
- Run a 1-row round-trip: write to Nimtable → query via Olake → embed in LanceDB
- Document the smoke-test results in `docs/lakehouse/smoke-test-2026-08-04.md`

### 2. Delete the 3 standalone IaC stacks (closes #90)

- `git rm -r bonnegar/stacks/olake/`
- `git rm -r bonnegar/stacks/nimtable/`
- `git rm -r bonnegar/stacks/lancedb-viewer/`
- Delete the 3 corresponding Komodo stack files
  (`bonnegar/komodo/stacks/{olake,nimtable,lancedb-viewer}.toml`)
- Delete the 3 Komodo procedure files
- Update `bonnegar/iac/sources/key-stacks.ts:55-85` to remove the 3 entries
- Update `openspec/specs/infrastructure-stacks/spec.md` to drop the 3 names
- Verify with `bun run iac:health` that the lakehouse stack still resolves

### 3. Migrate any consumer that still points at the deleted stacks

- `grep -r "olake\|nimtable\|lancedb-viewer" bonnegar/ --include="*.yaml" --include="*.toml"`
- Update any references to point at the canonical `lakehouse` stack
- Update CI workflows that boot these stacks

## Dependencies

```yaml
Blocked by: none (independent of BIEP v3)
Affected repos: bonneagar (single-repo change)
```

## Acceptance gates

- `docker compose -f bonnegar/stacks/lakehouse/compose.yaml up -d` succeeds
- All 3 services (`Nimtable :3018`, `Olake :3901`, `LanceDB Viewer :8081`)
  respond 200 OK
- `grep -r "olake\|nimtable\|lancedb-viewer" bonnegar/ --include="*.toml"
  --include="*.yaml"` returns 0 matches
- `openspec validate 2026-08-04-lakehouse-storage-cleanup-v1 --strict` passes
- `bun run iac:health` reports all 88+ stacks healthy (the 3 deleted
  stacks are gone)

## Cross-references

- `bonnegar/stacks/lakehouse/compose.yaml` (the canonical stack with
  all 3 services)
- `openspec/specs/infrastructure-stacks/spec.md` (the umbrella contract)
- `.agents/skills/infrastructure-stacks/SKILL.md` (the GOLD_STANDARD
  6-file stack contract)
- GitHub issues #89, #90