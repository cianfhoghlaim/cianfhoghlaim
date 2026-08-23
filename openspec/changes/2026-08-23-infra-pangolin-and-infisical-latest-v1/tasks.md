## Implementation Tasks

- [x] 1. Add `devops:pangolin:upgrade` and `devops:infisical:upgrade` tasks to `mise.toml [tasks]`. (verification-id: pangolin-infisical-upgrade-tasks) (verification: inspection)

- [x] 2. Update `.agents/skills/secrets-management/SKILL.md` with a "Pangolin + Infisical version strategy" section. (verification-id: secrets-skill-updated) (verification: inspection)

- [x] 3. Run canonical CI gates: `mise run core:typecheck` (exit 0), `openspec validate --all --strict` (exit 0). (verification-id: no-regressions) (verification: integration)

## Final Validation

- [x] `openspec validate 2026-08-23-infra-pangolin-and-infisical-latest-v1 --strict` passes
- [x] Both tasks exist
- [x] secrets-management skill updated
- [x] Gates pass