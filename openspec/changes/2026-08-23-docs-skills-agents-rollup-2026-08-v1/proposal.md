# 2026-08-23 — Final docs roll-up (Phase 5 cleanup)

## Why

After Phase 5.1.2 + 5.1.3 + 5.1.4 (the TBD Purpose batches), all 100
specs have non-TBD Purpose fields. The final cleanup:

1. Update `AGENTS.md` count claims (was "94 stacks"; now 99)
2. Update `openspec/AGENTS.md` count claim (was "132 items"; now 145+)
3. Document the `lint:spec:purpose` workflow in the skill
4. Note the completion of the 5-phase refactor

## What changes

### 1. `AGENTS.md`

- Update "94 stacks" → "99 stacks"
- Update "166 skills pass" → "65 skills pass" (the lint-skills.sh reports 65, not 166)
- Note: the dev-tooling-refactor v3 (Phase 5) completion

### 2. `openspec/AGENTS.md`

- Update "132 items" → "145+ items" (the actual count)
- Note the 3 new TBD Purpose batches

## Dependencies

- **Blocked by:** none
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. `AGENTS.md` count claims updated
2. `openspec/AGENTS.md` count claim updated
3. `mise run lint:drift-docs` exits 0 (no drift detected)

## Rollback plan

- `git checkout` AGENTS.md + openspec/AGENTS.md
- No code changes