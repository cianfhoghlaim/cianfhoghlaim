# Delta: infrastructure-stacks

## REMOVED Requirements

### Requirement: Standalone graph-DB stacks are deprecated

The 5 standalone graph-DB stacks (cognee + graphiti + falkordb +
memgraph + lancedb) are consolidated into the unified
`lakehouse/` stack. Per the `2026-08-15-lakehouse-unified-data-plane-v1`
change, each standalone stack carries a 1-line deprecation banner
pointing at the unified surface; deletion is scheduled for
`2026-09-13-delete-deprecated-graph-db-stacks`.

After this delta: the 5 standalone stacks SHALL be deleted. All
references to them in the `infrastructure-stacks` spec are removed.
