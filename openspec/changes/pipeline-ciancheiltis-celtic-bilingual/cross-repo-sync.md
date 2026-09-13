# Cross-repo sync: pipeline-ciancheiltis-celtic-bilingual

This change spans cianfhoghlaim + ciancheiltis.

## Files touched

| Path | Repo | Change |
|:--|:--|:--|
| `openspec/changes/pipeline-ciancheiltis-celtic-bilingual/proposal.md` | cianfhoghlaim | NEW |
| `openspec/changes/pipeline-ciancheiltis-celtic-bilingual/tasks.md` | cianfhoghlaim | NEW |
| `openspec/changes/pipeline-ciancheiltis-celtic-bilingual/specs/pipeline-ciancheiltis-celtic-bilingual/spec.md` | cianfhoghlaim | NEW |
| `openspec/changes/pipeline-ciancheiltis-celtic-bilingual/cross-repo-sync.md` | cianfhoghlaim | NEW (this file) |
| `openspec/changes/2026-09-06-ciancheiltis-v1/` (the absorbed change) | cianfhoghlaim | ARCHIVED under this umbrella |

## Files consumed cross-repo (read-only — no changes)

- `dlt_sources/british_isles/_shared/` — the shared DLT helpers
- `cocoindex_flows/_shared/` — the shared CocoIndex helpers
- `baml_src/_shared/` — the shared BAML prompt library

## Soft dependencies

- Firecrawl MCP v1 (firecrawl_agent + firecrawl_monitor_* + firecrawl_interact
  + firecrawl_parse + firecrawl_map) — already declared in the
  cianfhoghlaim pyproject.toml
- BAML 0.223.0+ — already declared
- CocoIndex 1.0+ — already declared
