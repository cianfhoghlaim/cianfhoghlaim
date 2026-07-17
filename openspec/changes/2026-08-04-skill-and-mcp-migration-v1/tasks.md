# 2026-08-04-skill-and-mcp-migration-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify A1 (dlt bugfix) merged
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Audit sruth/ references (closes #97)

- [ ] `grep -rl "sruth/" .agents/skills/ | wc -l` (baseline count)
- [ ] `grep -rl "sruth/" docs/ | head -10` (find docs/ files)

## Stage 2 — Migrate sruth/ paths

- [ ] `find .agents/skills -name "SKILL.md" -exec sed -i ''
  's|sruth/cianchoghlaim/|.|g;
  s|sruth/meaisinfhoghlaim/|agents/meaisinfhoghlaim/|g;
  s|sruth/tuatha/|web/apps/tuatha-ui/|g;
  s|sruth/croilar/|web/apps/croilar-portal/|g;
  s|sruth/oideachais/|.|g' {} \;`
- [ ] Apply the same sed to `docs/`
- [ ] Spot-check 5 skills manually: `.agents/skills/INDEXING_AND_COGNITION.md`,
  `.agents/skills/browser-tools/SKILL.md`, 3 others chosen at random
- [ ] Update the BAML examples in the skills that have them
- [ ] Add a CI gate that fails on any remaining `sruth/`

## Stage 3 — Migrate croilar-devtools (closes #96)

- [ ] `git mv agents/_croilar/_croilar_convex/devtools.ts
  agents/api/_croilar_convex/devtools.ts`
- [ ] Move the 3 associated files (package.json + tsconfig + README)
- [ ] Update the import paths in the moved file
- [ ] Update the route registrations in `agents/api/index.ts`

## Stage 4 — Validation

- [ ] `grep -r "sruth/" .agents/skills/ docs/` returns 0 matches
- [ ] `grep -r "croilar-devtools" agents/` shows the new canonical path
- [ ] `bun run mcp:test` passes
- [ ] `openspec validate 2026-08-04-skill-and-mcp-migration-v1 --strict` passes

## Stage 5 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-08-04-skill-and-mcp-migration-v1/specs/agent-platform-cluster/spec.md`
- [ ] Commit the change on a dedicated branch
- [ ] Open a PR on `origin/main` referencing this change
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-08-04-skill-and-mcp-migration-v1 --yes`

## Stage 6 — Close the GitHub issues

- [ ] `gh issue close 96 --comment "Closes via 2026-08-04-skill-and-mcp-migration-v1"`
- [ ] `gh issue close 97 --comment "Closes via 2026-08-04-skill-and-mcp-migration-v1"`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol