## Implementation Tasks

- [x] 1. Replace `.agents/skills/graphiti-core/SKILL.md` with a 5-line redirect stub (frontmatter + 4-line body pointing to `graphiti`). (verification-id: graphiti-core-stub) (verification: inspection — `wc -l .agents/skills/graphiti-core/SKILL.md` returns ≤ 10)

- [x] 2. Replace `.agents/skills/dlthub-router/SKILL.md` with a 5-line redirect stub (frontmatter + 4-line body pointing to `dlt`). (verification-id: dlthub-router-stub) (verification: inspection — `wc -l .agents/skills/dlthub-router/SKILL.md` returns ≤ 10)

- [x] 3. Replace `.agents/skills/setup-secrets/SKILL.md` with a 5-line redirect stub (frontmatter + 4-line body pointing to `secrets-management`). (verification-id: setup-secrets-stub) (verification: inspection — `wc -l .agents/skills/setup-secrets/SKILL.md` returns ≤ 10)

- [x] 4. Add the `lint-skill:deprecated-cleanup` task to `mise.toml [tasks]` (fails CI if any DEPRECATED skill has > 50 lines). (verification-id: lint-deprecated-task) (verification: integration — `mise run lint-skill:deprecated-cleanup` exits 0)

- [x] 5. Run `mise run lint:skills` to confirm the frontmatter is still valid after the replacement. (verification-id: skills-lint-passes) (verification: integration — `mise run lint:skills` exits 0)

- [x] 6. Run the canonical CI gates to confirm no regressions: `mise run core:typecheck` (exit 0), `openspec validate --all --strict` (exit 0). (verification-id: no-regressions) (verification: integration — both gates pass)

## Final Validation

Expected archive gate: `openspec validate 2026-08-22-agent-skill-refresh-and-dedup-v1 --archive-gate`

- [x] `openspec validate 2026-08-22-agent-skill-refresh-and-dedup-v1 --strict` passes
- [x] All 3 DEPRECATED skill files are ≤ 10 lines
- [x] The canonical skills are unchanged (graphiti, dlt, secrets-management)
- [x] `mise run lint:skills` exits 0
- [x] `mise run lint-skill:deprecated-cleanup` exits 0
- [x] `mise run core:typecheck` exits 0
