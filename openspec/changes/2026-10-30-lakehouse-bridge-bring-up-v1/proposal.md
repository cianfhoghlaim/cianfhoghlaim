# Change: 2026-10-30-lakehouse-bridge-bring-up-v1

> **Status (added 2026-10-30, per Umbrella 4 of the platform-reset saga):**
> This change is **KEEP** in the backlog triage. Umbrella 3 of the
> 2026-10-30 platform-reset saga. Closes Stage 8 Gap 4 (the 12
> lakehouse services down on `bunchloch` because the OrbStack Docker
> daemon socket is missing) and wires the `to_dlq_table_name` schema
> helper from Umbrella 2 into the 4 lakehouse-stack compose files. The
> only blocker is operator-side OrbStack recovery; the 3
> `scripts/lakehouse/` bring-up scripts are ready to run.

## Why

The 12 lakehouse services (Garage + ClickHouse + Cognee + Graphiti +
FalkorDB + Memgraph(-lab) + Olake + Nimtable UI + OTel collector +
lakekeeper-migrate + lance-namespace sidecar) are down on `bunchloch`
because the OrbStack Docker daemon socket is missing (per Stage 8
Gap 4). The 3 bring-up scripts at `scripts/lakehouse/` are ready to
run but cannot until Docker is recovered. The `to_dlq_table_name`
helper from Umbrella 2 (the schema-naming convergence, per the
2026-10-30-biep-tertiary-baml-repair-v1 change) must be wired into
the 4 lakehouse-stack compose files during the bring-up.

This is Umbrella 3 of 4 in
`openspec/plans/2026-10-30-platform-reset-saga-v1.md`.
