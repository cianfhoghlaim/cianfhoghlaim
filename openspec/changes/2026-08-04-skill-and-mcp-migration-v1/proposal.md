# 2026-08-04-skill-and-mcp-migration-v1

## Why

The BIEP v3 Phase 0 rename (`oideachais` → `cianfhoghlaim`) swept the
895 code files but the 153 SKILL.md files in `.agents/skills/` (plus
3+ docs/ files) still reference the legacy `sruth/<quadrant>/` paths
from the pre-v4 era. The `croilar-devtools` MCP server code also lives
at the wrong path (`_croilar/_croilar_convex/devtools.ts` — should be
`agents/api/_croilar_convex/devtools.ts`). The 2 open issues cover
these 2 migration tasks.

This change lives in the **cianfhoghlaim repo**.

## What changes

### 1. Migrate sruth/<quadrant>/ path references in 40+ skill files (closes #97)

- `grep -rl "sruth/" .agents/skills/ | wc -l` (the audit count)
- `find .agents/skills -name "SKILL.md" -exec sed -i ''
  's|sruth/cianchoghlaim/|.|g;
  s|sruth/meaisinfhoghlaim/|agents/meaisinfhoghlaim/|g;
  s|sruth/tuatha/|web/apps/tuatha-ui/|g;
  s|sruth/croilar/|web/apps/croilar-portal/|g;
  s|sruth/oideachais/|.|g' {} \;`
- Same for `docs/` and `*.md` files outside `.agents/skills/`
- Spot-check 5 skills manually to ensure the rename was correct
- Update the BAML examples in the skills that have them
- Run a CI gate that fails on any remaining `sruth/`

### 2. Migrate croilar-devtools MCP server code (closes #96)

- `git mv agents/_croilar/_croilar_convex/devtools.ts
  agents/api/_croilar_convex/devtools.ts`
- Move the 3 associated files (package.json + tsconfig + README)
- Update the import paths in the moved file
- Update the route registrations in `agents/api/index.ts`
- Run `bun run mcp:test` to verify the server still boots
- Add a CI gate that verifies the path

## Dependencies

```yaml
Blocked by: 2026-08-01-biep-v3-dlt-jurisdiction-pipeline-bugfix-v1
Blocked by (soft): 2026-07-26-biep-v3-root-namespace-rename-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `grep -r "sruth/" .agents/skills/ docs/` returns 0 matches
- `grep -r "croilar-devtools" agents/` shows the new canonical path
- `bun run mcp:test` passes
- `openspec validate 2026-08-04-skill-and-mcp-migration-v1 --strict` passes

## Cross-references

- `agents/api/_croilar_convex/devtools.ts` (the new canonical location)
- `.agents/skills/INDEXING_AND_COGNITION.md` (the entry point)
- `.agents/skills/browser-tools/SKILL.md` (the 2 skill files with sruth/ refs)
- `openspec/specs/agent-platform-cluster/spec.md` (the umbrella contract)
- GitHub issues #96, #97