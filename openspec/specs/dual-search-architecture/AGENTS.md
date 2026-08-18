# `dual-search-architecture` — Agent Routing

> TBD - created by `2026-08-17-hygiene-drift-cleanup-v1` P4.3 (regenerate via `mise run sync:all`).

## Routing

Load this AGENTS.md when you need to work with the
`dual-search-architecture` capability (the ccc + cognee + firecrawl_mcp
triple-search workflow).

For platform-wide context, load [`../../../AGENTS.md`](../../../AGENTS.md).

## Quick start

```bash
bun run ccc:init     # first time only (creates .cocoindex_code/target_sqlite.db)
bun run ccc:index    # rebuild the index after any major file move
bun run ccc:search "Dagster asset partition definition"   # semantic search
python -c "from agents.meaisinfhoghlaim.firecrawl_mcp import FirecrawlMCPClient; c = FirecrawlMCPClient(); print(c.search('Dagster 1.13 release notes', categories=['developer'], limit=3))"
```

## Key sources

- `openspec/specs/dual-search-architecture/spec.md` — the canonical spec
- `openspec/specs/indexing-and-cognition/spec.md` — the parent spec

## Adjacent specs

- `indexing-and-cognition` — the ccc + cognee + OpenCode agent/MCP registry
- `centralized-registry` — the MODEL_REGISTRY + schema.py + deployment-choice.yaml triplet

## DO NOT

- TBD

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`indexing-and-cognition`](../../../.agents/skills/INDEXING_AND_COGNITION.md) | ccc + cognee + OpenCode registry |
| [`firecrawl`](../../../.agents/skills/firecrawl/SKILL.md) | Live web search via firecrawl_mcp |
| [`ccc`](../../../.agents/skills/ccc/SKILL.md) | Semantic code search |

<!-- generated: 2026-08-17 by 2026-08-17-hygiene-drift-cleanup-v1 P4.3 -->