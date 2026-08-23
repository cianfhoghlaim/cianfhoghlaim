## Implementation Tasks

- [x] 1. Add `devops:locket:rotate` and `devops:locket:audit` tasks to `mise.toml [tasks]`. (verification-id: locket-rotate-audit-tasks) (verification: inspection)

- [x] 2. Update `docs/research/infrastructure/locket/locket.md` with a "Locket v0.3+ new features" section. (verification-id: locket-doc-updated) (verification: inspection)

- [x] 3. Run canonical CI gates: `mise run core:typecheck` (exit 0), `openspec validate --all --strict` (exit 0). (verification-id: no-regressions) (verification: integration)

## Final Validation

- [x] `openspec validate 2026-08-23-infra-locket-shim-v0-3-and-sidecar-pattern-v1 --strict` passes
- [x] Both tasks exist
- [x] Locket doc updated
- [x] Gates pass