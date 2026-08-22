## Implementation Tasks

- [x] 1. Add the `core-typecheck-mypy-invocation-fix` Scenario to the `core-namespace-tooling-coverage` Requirement in `openspec/specs/dev-tooling-surfaces/spec.md`. The Scenario documents the `--explicit-package-bases` flag + the 26 error codes disabled in `pyproject.toml [tool.mypy] disable_error_code`. (verification-id: typecheck-invocation-documented) (verification: inspection — the new Scenario appears in `dev-tooling-surfaces` spec under the `core-namespace-tooling-coverage` Requirement)

- [x] 2. Verify the Phase 1 commit (`2ab6aceb4`) is reachable on the current branch. (verification-id: phase-1-commit-reachable) (verification: inspection — `git log --oneline 2ab6aceb4 -1` succeeds + the commit message references the 3 fixes)

- [x] 3. Run the canonical CI gates to confirm the Phase 1 work is still working: `mise run core:typecheck` (exit 0), `mise run web:install` (exit 0), `openspec validate --all --strict` (exit 0). (verification-id: gates-still-pass) (verification: integration — all 3 gates pass)

## Final Validation

Expected archive gate: `openspec validate 2026-08-23-dev-tooling-pre-existing-failure-remediation-v1 --archive-gate`

- [x] `openspec validate 2026-08-23-dev-tooling-pre-existing-failure-remediation-v1 --strict` passes
- [x] Phase 1 commit `2ab6aceb4` reachable on `origin/token-plan-lc-pipeline-2026-08`
- [x] `mise run core:typecheck` exits 0
- [x] `mise run web:install` exits 0
- [x] `openspec validate --all --strict` exits 0

## Notes

- This change is **docs/spec only** — no code modifications. The Phase 1 fixes are already committed (`2ab6aceb4`).
- The change deliberately does NOT propose to re-enable the 26 disabled mypy error codes. That work belongs to a separate change (`data-namespace-tooling-coverage-v1`) which can systematically address each category.
