## Implementation Tasks

- [x] 1. Add the 3 new `data:dlt:*` tasks to `mise.toml [tasks]`. (verification-id: dlt-130-tasks) (verification: inspection — `mise tasks --all | grep data:dlt` shows 6+ tasks)

- [x] 2. Verify each task exits 0 in dry-run mode (`--help` or empty arg). (verification-id: tasks-dry-run) (verification: integration — each task runs without erroring)

- [x] 3. Update `.agents/skills/dlt/SKILL.md` to add a "DLT 1.30+ new features" section. (verification-id: dlt-skill-updated) (verification: inspection — the section exists in the skill file)

- [x] 4. Run the canonical CI gates: `mise run core:typecheck` (exit 0), `openspec validate --all --strict` (exit 0). (verification-id: no-regressions) (verification: integration)

## Final Validation

- [x] `openspec validate 2026-08-23-data-dlt-1-30-features-v1 --strict` passes
- [x] All 3 tasks exist
- [x] Skill updated
- [x] Gates pass