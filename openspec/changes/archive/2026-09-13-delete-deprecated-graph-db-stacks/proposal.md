# Change: Delete the 5 deprecated graph-DB stacks

## Why

Per `2026-08-15-lakehouse-unified-data-plane-v1`, all 5 graph-DB
backends (cognee + graphiti + falkordb + memgraph + lancedb) were
consolidated into the unified `lakehouse/` stack. The 5 standalone
stacks carry 1-line deprecation banners pointing at the unified
surface; deletion was deferred to the placeholder date
`2026-XX-XX-delete-deprecated-graph-db-stacks`.

This change replaces the literal `2026-XX-XX` placeholder with a
real date and files the deletion work as a tracked change.

## What changes

- Delete `bonneagar/stacks/{cognee,graphiti,falkordb,memgraph,lancedb}/`
  (each stack's `compose.yaml` + `sidecar.yaml` + `secrets.env` +
  `blueprint.yaml` + `.env.example` + `pangolin.yaml` + README).
- Remove the deprecation banner references in
  `bonneagar/stacks/lakehouse/README.md:181` + the spec for
  `infrastructure-stacks/spec.md:73`.
- Mark the `T15.3` follow-up task complete in
  `2026-08-15-lakehouse-unified-data-plane-v1/tasks.md`.

## Impact

- Affected specs: `infrastructure-stacks`, `agent-platform-cluster`,
  `baml-schemas` (each currently references the 5 standalone
  stacks for migration purposes)
- Affected code: `bonneagar/stacks/{cognee,graphiti,falkordb,
  memgraph,lancedb}/` (delete)
- Affected docs: `bonneagar/stacks/lakehouse/README.md`,
  `openspec/changes/2026-08-15-lakehouse-unified-data-plane-v1/*`

## Pre-flight checklist

- [ ] Confirm the unified `lakehouse/` stack is the production
  surface for all 5 backends (cognee, graphiti, falkordb, memgraph,
  lancedb)
- [ ] Confirm no agent or DAG references the standalone stacks
  directly
- [ ] Confirm the 5 stacks are not deployed on either bunchloch or
  arm1-oci
