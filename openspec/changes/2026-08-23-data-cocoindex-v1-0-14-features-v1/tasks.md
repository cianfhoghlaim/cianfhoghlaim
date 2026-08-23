## Implementation Tasks

- [x] 1. Add the 2 new `data:cocoindex:*` tasks to `mise.toml [tasks]`. (verification-id: cocoindex-114-tasks) (verification: inspection)

- [x] 2. Verify `data:cocoindex:apps:list` returns ≥ 7 entries (the 7 BIEP v1 Apps). (verification-id: apps-list-count) (verification: integration — `mise run data:cocoindex:apps:list` returns ≥ 7 apps)

- [x] 3. Update `.agents/skills/cocoindex/SKILL.md` to add a "CocoIndex v1.0.14+ new patterns" section. (verification-id: cocoindex-skill-updated) (verification: inspection)

- [x] 4. Run the canonical CI gates: `mise run core:typecheck` (exit 0), `openspec validate --all --strict` (exit 0). (verification-id: no-regressions) (verification: integration)

## Final Validation

- [x] `openspec validate 2026-08-23-data-cocoindex-v1-0-14-features-v1 --strict` passes
- [x] Both tasks exist
- [x] Skill updated
- [x] Gates pass