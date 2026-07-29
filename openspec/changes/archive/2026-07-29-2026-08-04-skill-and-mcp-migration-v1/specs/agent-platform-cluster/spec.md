## ADDED Requirements

### Requirement: Skills + MCP server use canonical post-BIEP-v3 paths

The system SHALL require:

1. All `.agents/skills/**/*.md` files to use the canonical
   post-BIEP-v3 namespace (no `sruth/<quadrant>/` legacy paths
   appear as path references — `sruth-subagents` and
   `sruth_browser` historical mentions in skill History sections
   are explicitly exempt).
2. The `croilar-devtools` MCP server to live at the canonical path
   `agents/api/_croilar_convex/devtools.ts` (the legacy
   `agents/_croilar/_croilar_convex/devtools.ts` path MUST be
   absent).
3. A CI gate at `.github/workflows/skill-refs-check.yaml` AND
   `.forgejo/workflows/skill-refs-check.yaml` that fails on any
   remaining `sruth/(cianfhoghlaim|meaisinfhoghlaim|tuatha|croilar|oideachais)/`
   PATH reference (with explicit excludes for the 3 documents that
   intentionally quote legacy paths:
   `docs/audits/2026-07-06-drift-audit.md`,
   `docs/p3-skill-mcp-migration-status.md`, and
   `docs/biiep-v3/post-iac-namespace-rename-secrets.md`).

#### Scenario: No sruth/ PATH references in skills or in the un-excluded docs

- **WHEN** the CI gate runs against `grep -rE "sruth/(cianfhoghlaim|meaisinfhoghlaim|tuatha|croilar|oideachais)/" .agents/skills/ docs/`
- **THEN** zero matches SHALL be present in `.agents/skills/` or in any un-excluded `docs/` file
- **AND** the 3 excluded docs (`docs/audits/2026-07-06-drift-audit.md`,
  `docs/p3-skill-mcp-migration-status.md`,
  `docs/biiep-v3/post-iac-namespace-rename-secrets.md`) MAY contain
  intentional `sruth/` mentions that document the migration itself

#### Scenario: croilar-devtools lives at the canonical path

- **WHEN** `ls agents/api/_croilar_convex/devtools.ts` runs
- **THEN** the file SHALL exist
- **AND** `ls agents/_croilar/` SHALL return "No such file or directory"
  (the old path is gone)

#### Scenario: MCP test passes after migration

- **WHEN** `bun run mcp:test` runs
- **THEN** the suite SHALL pass with the migrated file at the new path

#### Scenario: CI gate present at both GitHub + Forgejo

- **WHEN** `.github/workflows/skill-refs-check.yaml` is inspected
- **THEN** it SHALL contain the strict regex check for `sruth/` PATH
  references AND the `croilar-devtools` canonical-path check
- **AND** `.forgejo/workflows/skill-refs-check.yaml` SHALL exist
  with the same checks (so both CI systems enforce the gate)