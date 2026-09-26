# Stage 8 Fresh-Slate Spec Refactor — Handoff Notes

> **The Stage 8 fresh-slate spec refactor is the NEXT work after the 2026-10
> convergence saga completes (7 of 8 plans done).** This doc is the handoff
> from Plans 1-8 to Stage 8.

## Why Stage 8 exists

The 2026-10 saga intentionally stopped at "implement all the current
planned changes in stages as advised and then we will develop fresh-slate
spec driven rules and specs for the repository from our later new baseline"
(per the original user direction).

The current spec-driven-development model has these gaps that Stage 8
will close:

### Gap 1: Phase B schema-naming convergence (deferred to Stage 8)

Three conflicting naming conventions co-exist:

| Surface | Current convention | Source |
|:--|:--|:--|
| `cognee_dataset` field | `oideachais_<agent>` | `agents/agent_registry.py:AGENT_REGISTRY` (13 entries) |
| LanceDB table names | `media.image_gen_chunks_<lang>` | `cocoindex_flows/media/{gaeilge,cymraeg,...}/asset_index.py` (6 entries) |
| DuckLake namespace | `ciianfhoghlaim` (one f, canonical) | `dlt_sources/destinations/_common.py:DUCKLAKE_NAMESPACE` |

Stage 8 picks ONE canonical pattern (recommended: `<quadrant>_<table>`) +
one converter utility `to_dlq_table_name(quadrant, table)` that all code uses +
archives the legacy `ducklake_<x>` aliases after a 6-month grace period.

### Gap 2: 79-stalled-change backlog

The 79 changes with 0 tasks done need triage: 30 are genuinely needed,
20 are research artifacts that should be archived, 29 are outdated
superfluous work that should be archived.

### Gap 3: BAML parser limitations

`baml-py 0.226.1` has a parser issue with multi-line function signatures +
`@description("...")` aligned-parens style. Affects my 3 new BAML contracts
(extract_syllabus_diagram.baml, extract_design_pattern.baml, gameplay_descriptor.baml).
Workaround: single-line `@description("...")` or wait for baml-py fix.

### Gap 4: Lakehouse bridge bring-up

The 12 lakehouse services (Garage + ClickHouse + Cognee + Graphiti + FalkordDB +
Memgraph(-lab) + Olake + Nimtable UI + OTel collector + lakekeeper-migrate +
lance-namespace sidecar) are down on bunchloch because the OrbStack Docker
daemon socket is missing.

The 3 scripts at `scripts/lakehouse/` (`init_lakehouse_postgres.sh`,
`up_lakehouse_bridge.sh`, `verify_bridge.py`) are ready to run once the
Docker daemon is recovered.

## Recommended Stage 8 work order

1. **Convergence pass** — triage the 79 stalled changes (30 keep, 20 archive
   as research, 29 archive as outdated). This unblocks all downstream schema
   naming work.

2. **Schema-naming convergence (Phase B)** — pick `<quadrant>_<table>` + add
   `to_dlq_table_name(quadrant, table)` + archive legacy aliases.

3. **BAML parser workaround** — convert the 3 new BAML contracts to single-line
   `@description` style + add a CI lint to prevent the multi-line regression.

4. **Lakehouse daemon recovery** — fix OrbStack + run the 3 bring-up scripts
   + verify the bridge end-to-end.

5. **Spec-driven-development rules** — write the fresh-slate openspec rules
   + materialise the new specs against the converged baseline.

## Branch + openspec change template

Stage 8 should ship as:
- Branch: `fresh-slate-spec-rules` (new branch off `main`)
- Openspec change: `openspec/changes/2026-10-30-fresh-slate-spec-rules-v1/`
- Pattern: 1 large PR + 9 follow-up PRs (one per archived cluster)

## Reference

- Saga plan: `openspec/plans/2026-10-01-convergence-saga-v1.md`
- Phase B TODO notes: `baml_src/AGENTS.md`, `cocoindex_flows/AGENTS.md`, `dlt_sources/AGENTS.md`
