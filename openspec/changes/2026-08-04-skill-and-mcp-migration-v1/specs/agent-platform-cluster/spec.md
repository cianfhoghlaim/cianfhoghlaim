## MODIFIED Requirements

### Requirement: Skills + MCP server use canonical post-BIEP-v3 paths

The system SHALL require:
1. All `.agents/skills/**/*.md` files to use the canonical
   post-BIEP-v3 namespace (no `sruth/<quadrant>/` legacy paths)
2. The `croilar-devtools` MCP server to live at the canonical path
   `agents/api/_croilar_convex/devtools.ts`

#### Scenario: No sruth/ references in skills

- **WHEN** `grep -r "sruth/" .agents/skills/ docs/` runs
- **THEN** zero matches SHALL be present

#### Scenario: croilar-devtools lives at the canonical path

- **WHEN** `ls agents/api/_croilar_convex/devtools.ts` runs
- **THEN** the file SHALL exist
- **AND** `ls agents/_croilar/` SHALL return "No such file or directory"
  (the old path is gone)

#### Scenario: MCP test passes after migration

- **WHEN** `bun run mcp:test` runs
- **THEN** the suite SHALL pass with the migrated file at the new path