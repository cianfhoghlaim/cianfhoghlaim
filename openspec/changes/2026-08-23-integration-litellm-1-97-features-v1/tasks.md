## Implementation Tasks

- [x] 1. Add the 2 new `data:litellm:*` tasks to `mise.toml [tasks]`. (verification-id: litellm-197-tasks) (verification: inspection)

- [x] 2. Update `.agents/skills/litellm/SKILL.md` with a "LiteLLM v1.97+ new features" section. (verification-id: litellm-skill-updated) (verification: inspection)

- [x] 3. Run canonical CI gates: `mise run core:typecheck` (exit 0), `openspec validate --all --strict` (exit 0). (verification-id: no-regressions) (verification: integration)

## Final Validation

- [x] `openspec validate 2026-08-23-integration-litellm-1-97-features-v1 --strict` passes
- [x] Both tasks exist
- [x] Skill updated
- [x] Gates pass