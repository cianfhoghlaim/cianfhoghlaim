## Implementation Tasks

- [x] 1. Add `devops:stack:gold-standard-audit` and `devops:stack:drift-report` tasks to `mise.toml [tasks]`. (verification-id: stack-audit-tasks) (verification: inspection — `mise tasks --all | grep devops:stack` shows 2 tasks)

- [x] 2. Update `bonneagar/AGENTS.md` with a "Stack modernization" section. (verification-id: bonneagar-docs-updated) (verification: inspection)

- [x] 3. Run canonical CI gates: `mise run core:typecheck` (exit 0), `openspec validate --all --strict` (exit 0). (verification-id: no-regressions) (verification: integration)

## Final Validation

- [x] `openspec validate 2026-08-23-infra-stack-doctor-and-gold-standard-modernization-v1 --strict` passes
- [x] Both tasks exist
- [x] bonneagar docs updated
- [x] Gates pass