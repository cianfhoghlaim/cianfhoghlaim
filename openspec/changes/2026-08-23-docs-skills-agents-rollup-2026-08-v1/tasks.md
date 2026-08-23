## Implementation Tasks

- [x] 1. Update `AGENTS.md` count claims (94 → 99 stacks; 166 → 65 skills pass). (verification-id: counts-updated) (verification: inspection)

- [x] 2. Update `openspec/AGENTS.md` count claim (132 → 145+ items). (verification-id: openspec-count-updated) (verification: inspection)

- [x] 3. Run `mise run lint:drift-docs` to confirm no drift. (verification-id: no-drift) (verification: integration)

## Final Validation

- [x] `openspec validate 2026-08-23-docs-skills-agents-rollup-2026-08-v1 --strict` passes
- [x] Count claims match ground truth
- [x] No drift detected