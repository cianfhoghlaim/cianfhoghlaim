# Tasks: Delete the 5 deprecated graph-DB stacks

## Phase A — Pre-flight verification (no infra required)

- [ ] A1 Confirm the unified `bonneagar/stacks/lakehouse/` stack
  exposes all 5 backends (cognee, graphiti, falkordb, memgraph,
  lancedb) and is the production surface.
- [ ] A2 Confirm no agent code imports from the 5 standalone
  stacks (`rg -l "stacks/(cognee|graphiti|falkordb|memgraph|lancedb)"
  --type py` returns empty).
- [ ] A3 Confirm no Dagster asset references the 5 standalone
  stacks (`rg -l "stacks/(cognee|graphiti|falkordb|memgraph|lancedb)"
  orchestration/defs/` returns empty).
- [ ] A4 Confirm the 5 stacks are not deployed on either bunchloch
  or arm1-oci (`km stack list | grep -E "^(cognee|graphiti|falkordb|memgraph|lancedb)$"`).

## Phase B — Spec update (no infra required)

- [ ] B1 Edit `openspec/specs/infrastructure-stacks/spec.md:73` to
  remove the deprecation-banner reference.
- [ ] B2 Edit `openspec/specs/agent-platform-cluster/spec.md` to
  remove the standalone stack references (per the report's
  `2026-08-13-bonneagar-infra-remediation-v3` Why section).
- [ ] B3 Edit `openspec/specs/baml-schemas/spec.md` if it
  references any of the 5 standalone stacks.

## Phase C — Documentation update (no infra required)

- [ ] C1 Edit `bonneagar/stacks/lakehouse/README.md:181` to remove
  the deletion-deferred line.
- [ ] C2 Edit
  `openspec/changes/2026-08-15-lakehouse-unified-data-plane-v1/tasks.md:95`
  to mark T15.3 complete.
- [ ] C3 Edit
  `openspec/changes/2026-08-15-lakehouse-unified-data-plane-v1/proposal.md:153,221`
  to remove the literal `2026-XX-XX-delete-deprecated-graph-db-stacks`
  references and substitute this change's date.

## Phase D — Stack deletion (operator action)

- [ ] D1 `rm -rf bonneagar/stacks/cognee/`
- [ ] D2 `rm -rf bonneagar/stacks/graphiti/`
- [ ] D3 `rm -rf bonneagar/stacks/falkordb/`
- [ ] D4 `rm -rf bonneagar/stacks/memgraph/`
- [ ] D5 `rm -rf bonneagar/stacks/lancedb/`
- [ ] D6 `git rm -r bonneagar/stacks/{cognee,graphiti,falkordb,memgraph,lancedb}/`
- [ ] D7 Run `mise run lint:stack-doctor --strict` — confirms no
  dangling references.

## Phase E — Refresh registry (operator action)

- [ ] E1 Run `mise run sync:komodo` to refresh the resource-sync
  view of the 5 stacks' removal.
- [ ] E2 Run `openspec validate 2026-09-13-delete-deprecated-graph-db-stacks --strict`.

## Phase F — Archive this change

- [ ] F1 `openspec archive 2026-09-13-delete-deprecated-graph-db-stacks -y --skip-specs`.
