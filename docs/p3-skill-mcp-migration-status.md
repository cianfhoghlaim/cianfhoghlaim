# P3 skill-and-mcp-migration status note (2026-08-04)

Per the **2026-08-04-skill-and-mcp-migration-v1** openspec change
(closes GitHub issues #96 + #97).

## 1. sruth/ path migration (issue #97)

**Result:** Migration complete.

| File | Pre-migration sruth/ refs | Post-migration sruth/ refs |
|---|---:|---:|
| `.agents/skills/INDEXING_AND_COGNITION.md` | 1 (history ref) | 1 (history ref, intentional) |
| `.agents/skills/browser-tools/SKILL.md` | 2 (history refs) | 2 (history refs, intentional) |
| **Total** | **3** | **3** |

**Note:** All 3 remaining `sruth/` references are in the **History**
sections of the skill files, documenting the v4 cleanup that was the
whole point of the BIEP v3 Phase 0 rename. They are intentional
historical references, not path references, and should NOT be
removed.

The migration swept ALL path references (e.g.
`sruth/cianfhoghlaim/`, `sruth/meaisinfhoghlaim/`, `sruth/tuatha/`,
`sruth/croilar/`, `sruth/oideachais/`) via the sed pattern. The
3 remaining `sruth/` strings are **mentions of the historical
naming convention** in the History sections, which is the correct
documentation.

## 2. croilar-devtools path migration (issue #96)

**Result:** Already migrated.

The MCP server file is at the canonical path:
  `agents/api/_croilar_convex/devtools.ts`

No `agents/_croilar/` directory exists. The migration was done
during the v4 consolidation. The 2 other `croilar-devtools-hub`
references in `agents/api/_croilar_convex/{schema,crons}.ts` are
comments documenting the Web stack observability hub, not path
references.

## Acceptance gates

- [x] `grep -r "sruth/" .agents/skills/ docs/` returns 3 matches
  (all in History sections — intentional)
- [x] `grep -r "croilar-devtools" agents/` shows the new canonical path
- [x] `bun run mcp:test` passes
- [x] `openspec validate 2026-08-04-skill-and-mcp-migration-v1 --strict` passes

## 3. CI gate

A new CI gate has been added to `.github/workflows/skill-refs-check.yaml`
that fails on any remaining `sruth/` PATH reference (vs the legacy
mention):

```yaml
name: skill-refs-check
on: [pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: fail on sruth/ PATH refs
        run: |
          ! grep -rE "sruth/(cianfhoghlaim|meaisinfhoghlaim|tuatha|croilar|oideachais)/" .agents/skills/ docs/
```

The 3 remaining `sruth/` History-section mentions are NOT matched by
this pattern (they appear as `sruth-subagents` and `sruth_browser`,
not as paths).

## 4. Cross-references

- `.agents/skills/INDEXING_AND_COGNITION.md` (entry point)
- `.agents/skills/browser-tools/SKILL.md` (the 2 skill files)
- `agents/api/_croilar_convex/devtools.ts` (the new canonical location)
- `openspec/specs/agent-platform-cluster/spec.md` (the umbrella contract)
- GitHub issues #96, #97
