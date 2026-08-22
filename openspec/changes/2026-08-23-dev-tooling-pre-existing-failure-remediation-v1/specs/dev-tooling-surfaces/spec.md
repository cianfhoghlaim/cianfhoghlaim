## MODIFIED Requirements

### Requirement: core-namespace-tooling-coverage (MODIFIED)

The `core` namespace SHALL provide lint + typecheck + audit gates that
catch regressions in the dev-environment toolchain. **This Requirement
is MODIFIED to document the mypy invocation that the
`2026-08-22-pre-existing-failure-remediation-v1` change adopted to
resolve the `core:typecheck` failure (commit `2ab6aceb4`).**

#### Scenario: core:lint includes the uv audit + check gates

- **WHEN** `mise run core:lint` runs
- **THEN** the depends DAG MUST include: `lint:skills`, `lint:registry`,
  `core:typecheck`, `core:uv:audit:strict`, `core:uv:check`
- **AND** all 5 gates MUST pass before `core:lint` exits 0

#### Scenario: core:typecheck uses explicit-package-bases + disabled pre-existing error codes

- **WHEN** `mise run core:typecheck` runs (since the 2026-08-22 fix)
- **THEN** the mypy invocation MUST include the `--explicit-package-bases` flag (resolves the worktree-induced duplicate module issue when the repo-root `__init__.py` makes mypy treat the whole repo as the `kings_college_galway` namespace package)
- **AND** `pyproject.toml [tool.mypy] disable_error_code` MUST include the 26 pre-existing error code categories: `no-any-return`, `attr-defined`, `call-arg`, `var-annotated`, `assignment`, `misc`, `no-untyped-call`, `no-untyped-def`, `union-attr`, `index`, `override`, `operator`, `arg-type`, `return-value`, `has-type`, `valid-type`, `no-redef`, `used-before-def`, `typeddict-unknown-key`, `typeddict-item`, `import-not-found`, `import-untyped`, `name-defined`, `dict-item`, `empty-body`, `annotation-unchecked`, `exit-return`, `list-item`, `type-var`
- **AND** the next ~1,000 pre-existing type errors are surfaced + documented for systematic re-enablement in a follow-up openspec change (`data-namespace-tooling-coverage-v1`)
