## ADDED Requirements

### Requirement: Pre-commit hook blocks drift regressions

The system MUST publish a pre-commit hook that blocks commits that
introduce hardcoded model strings (the missing enforcement layer
that would have caught v1 + v2 regressions at commit time).

The hook MUST:

1. Live in `.pre-commit-config.yaml` as a single `local` repo with a
   `lint-registry` hook (`language: system`, `pass_filenames: false`,
   `always_run: true`, `stages: [pre-commit]`).
2. Invoke `mise run lint:registry` (which calls
   `scripts/registry_audit.py`).
3. Exit non-zero if any hardcoded model name or model ID is found
   in `agents/`, `baml_src/`, `notebooks/`, `web/`,
   `orchestration/`, `spaces/`, or `meaisinfhoghlaim/` that isn't
   routed through `MODEL_REGISTRY`.
4. Be installable via `mise run pre-commit-install` (new task) or
   `pre-commit install` (manual).
5. Be runnable manually via `mise run pre-commit-run` (new task)
   or `pre-commit run --all-files` (manual).
6. Be skippable via `git commit --no-verify` (rare — for emergencies).
7. Be documented in `.agents/skills/centralized-registry/SKILL.md`
   under a `## Pre-commit hook` subsection.

#### Scenario: A developer commits a file with a hardcoded model string

- **GIVEN** the developer has run `mise run pre-commit-install`
- **AND** they edit `agents/foo/bar.py` to add `default_model="gemini-2.0-flash"`
- **WHEN** they run `git commit -m "add agent"`
- **THEN** the pre-commit hook runs `mise run lint:registry`
- **AND** the audit detects the hardcoded string
- **AND** the commit is blocked with a non-zero exit code

#### Scenario: A developer commits a file that uses MODEL_REGISTRY.resolve()

- **GIVEN** the developer has run `mise run pre-commit-install`
- **AND** they edit `agents/foo/bar.py` to add
  `from meaisinfhoghlaim.models import model_for; default = model_for("text_llm", "default")`
- **WHEN** they run `git commit -m "add agent"`
- **THEN** the pre-commit hook runs `mise run lint:registry`
- **AND** the audit reports 0 drift
- **AND** the commit succeeds