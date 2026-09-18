# Cross-repo sync: pipeline-mega-3-modernization

This change touches ONLY `cianfhoghlaim`. The BAML stage templates
+ ADK agents produced here feed the sister repos via the
`sister-shared` contract (per `cianchosaint-handoff-v1`).

## Files touched (cianfhoghlaim)

| Path | Change |
|:--|:--|
| `openspec/changes/pipeline-mega-3-modernization/proposal.md` | NEW |
| `openspec/changes/pipeline-mega-3-modernization/tasks.md` | NEW |
| `openspec/changes/pipeline-mega-3-modernization/specs/pipeline-mega-3-modernization/spec.md` | NEW (the umbrella spec delta) |
| `openspec/changes/pipeline-mega-3-modernization/cross-repo-sync.md` | NEW (this file) |

## Files absorbed (archived under this umbrella)

The 3 dated changes are absorbed into this umbrella + archived:

- `2026-08-18-mega-3-roadmap-v1`
- `2026-08-18-mega-3-fast-follow-v1`
- `2026-08-26-mega-3a-baml-and-adk-v1`

After archival they live under `openspec/changes/archive/2026-09-13-pipeline-mega-3-modernization/`
for provenance.

## Files consumed cross-repo (read-only — no changes)

- `baml_src/_shared/` (cianfhoghlaim) — the 5 integration helpers
- `cocoindex_flows/_shared/` (cianfhoghlaim) — the cocoindex_query_api
- `agents/adk/_workflow_handlers.py` (cianfhoghlaim) — the BAMLFunctionTool

## Soft dependencies

- BAML 0.223.0+ — already declared in `pyproject.toml`
- CocoIndex 1.0+ — already declared
- Google ADK 2.9+ — already declared

## Licence alignment

Per `LICENSE.md`: BUSL-1.1 with the documented Educational Use Grant +
Personal/Celtic-Studies Expansion Clause. No changes.
