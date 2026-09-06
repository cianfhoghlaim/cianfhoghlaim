# `ciancheiltis` — Agent Routing

> Cinder branch project: long-distance Celtic bilingual alignment.

## Routing

Load this AGENTS.md when working on the ciancheiltis umbrella project,
its 6 phase sub-directories under `dlt_sources/ciancheiltis/`, or the
openspec change `2026-09-06-ciancheiltis-v1`.

## Quick start

```bash
openspec validate 2026-09-06-ciancheiltis-v1 --strict   # required before commit
mise run sync:all                                       # keep registries in sync after landing a phase
```

## Key sources

- `openspec/specs/ciancheiltis/spec.md` — the canonical spec
- `openspec/changes/2026-09-06-ciancheiltis-v1/` — the live change proposal
- `ciancheiltis/README.md` — user-facing orientation
- `dlt_sources/ciancheiltis/` — the phase subtrees (`en_cy`, `en_ga_roi`, `en_ga_ni`, `en_gd`, `en_gv`, `en_ga_eu`)
- `dlt_sources/ciancheiltis/_shared/` — content-based language detector, opaque-URL scanner, gov.wales WAF bypass
- `dlt_sources/ciancheiltis/clarin_uk/` — cross-domain Celtic linguistic bridges

## Adjacent specs

- [`celtic-language-pipeline`](../celtic-language-pipeline/spec.md) — curated Celtic-language corpora (companion, not competitor)
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) — education-only bilingual pipeline (subset of Phase 1)
- [`repo-hygiene-agent-routing`](../repo-hygiene-agent-routing/spec.md) — the per-spec AGENTS.md convention

## DO NOT

- Hand-edit this file (the `scripts/sync/spec_agents.py` generator will overwrite it). To customise, edit `openspec/specs/ciancheiltis/spec.md` and re-run the generator.
- Trust the `metadata["language"]` tag on a scraped page — always run the content-based detector.
- Import via absolute `cianfhoghlaim.dlt_sources.ciancheiltis.…` paths inside source files — use relative imports.

## Skill pointers

- `ccc` — for semantic code search across the ciancheiltis implementation
- `openspec` — for the spec change workflow
- `firecrawl` — for the Firecrawl MCP tool surface (the canonical discovery + scraping layer)
- `dlt` — for DLT conventions
- `dagster` — for the 5-layer asset architecture
- `baml` — for the BAML extraction schema patterns
- `cocoindex` — for the R1-R4 conformance contract
- `motherduck` — for Dive + Flight + Lakehouse topology
- `secrets-management` — for `infisical://dev-baile/…` URIs (never hand-write `.env`)

<!-- generated: 2026-09-06; do not hand-edit -->
