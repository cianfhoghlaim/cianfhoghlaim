---
title: 'Sruth - Data Flows (Historical)'
domain: 'architecture'
status: 'superseded'
description: 'Historical overview of the pre-restructure sruth/ data flows. The post-restructure reality is documented in docs/00-core/CLAUDE.md and docs/02-data-platform/.'
read_when: []
updated: '2026-06-13'
supersedes:
  - docs/SRUTH_OVERVIEW.md
  - openspec/plans/data_engineering_deep_dive.md
superseded_by:
  - docs/00-core/CLAUDE.md
  - docs/02-data-platform/data-architecture.md
  - docs/02-data-platform/dlt-pipelines.md
  - docs/02-data-platform/dagster-orchestration.md
ccc_query_hints:
  - sruth history
  - data flows overview historical
truth: partial

---

# Sruth - Data Flows (Historical)

> **This doc is `status: superseded`.** The pre-restructure `sruth/`
> layout is gone. Read [`docs/00-core/CLAUDE.md`](../../00-core/CLAUDE.md)
> for the current 5-quadrant topology and the project identity.

The original `sruth/` subproject contained 5 sub-flows. After the
2026-06-13 restructure, those flows live in:

| Original `sruth/*` sub-flow | New location |
|---|---|
| `sruth/oideachais/` | `oideachais/` (data lakehouse quadrant) |
| `sruth/teanga/` | `oideachais/dlt_sources/celtic/` + `oideachais/teanga/` (vendor-copied corpus) |
| `sruth/oideachas_oileáin/` | `oideachais/dlt_sources/uk/` (now re-exported through `oideachais/dlt_sources/domains/education/`) |
| `sruth/crypteolas/` | `tuatha/crypteolas/` |
| `sruth/tuath/` | `tuatha/` |
| `sruth/aleyum/` | `croilar/` (Aleyum is the music persona in croilar) |
| `sruth/códeolas/` | `tuatha/codeolas/` |

For the new layout, see:
- [`docs/00-core/CLAUDE.md`](../../00-core/CLAUDE.md) §Quadrant map
- [`docs/02-data-platform/data-architecture.md`](../../02-data-platform/data-architecture.md)
- [`docs/02-data-platform/dlt-pipelines.md`](../../02-data-platform/dlt-pipelines.md)
- [`docs/02-data-platform/dagster-orchestration.md`](../../02-data-platform/dagster-orchestration.md)
- [`docs/02-data-platform/cross-domain-registry.md`](../../02-data-platform/cross-domain-registry.md)

For the project history that led to this restructure, see the
archive at `docs/archive/2026-06-06-meaisinfhoghlaim/RESEARCH_CONSOLIDATION_PLAN.md`.
