## Implementation Tasks

- [x] 1. Add the 3 new `data:dagster:*` tasks to `mise.toml [tasks]`. (verification-id: dagster-113-tasks) (verification: inspection — `mise tasks --all | grep data:dagster` shows 6 tasks)

- [x] 2. Verify `data:dagster:list-assets` returns ≥ 199 assets (the current count per the post-2026-07-15 refactor). (verification-id: asset-count) (verification: integration — `mise run data:dagster:list-assets` exits 0 + JSON contains ≥ 199 assets)

- [x] 3. Update `.agents/skills/dagster/SKILL.md` to add a "Dagster 1.13+ new patterns" section documenting `dg` CLI + Declarative Automation + Virtual Assets. (verification-id: dagster-skill-updated) (verification: inspection)

- [x] 4. Run the canonical CI gates: `mise run core:typecheck` (exit 0), `openspec validate --all --strict` (exit 0). (verification-id: no-regressions) (verification: integration — both gates pass)

## Final Validation

Expected archive gate: `openspec validate 2026-08-23-data-dagster-1-13-features-v1 --archive-gate`

- [x] `openspec validate 2026-08-23-data-dagster-1-13-features-v1 --strict` passes
- [x] All 3 tasks exist
- [x] Skill updated
- [x] Gates pass
