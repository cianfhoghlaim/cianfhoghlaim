## ADDED Requirements

### Requirement: Dagger pipelines router skill

The Dagger CI/CD capability MUST be discoverable via a single router skill at `.agents/skills/dagger-pipelines/SKILL.md`. The router SHALL list the 8 callable functions, the 4 build pipelines, the Python root + TypeScript submodule locations, the BuildKit caching, and the LLM-secrets injection pattern.

#### Scenario: Agent finds the Dagger router

- **WHEN** an agent searches for "dagger call", "dagger module", "buildkite cache", or "gitops pipeline"
- **THEN** the loader matches `.agents/skills/dagger-pipelines/SKILL.md`
- **AND** the skill points at the underlying Dagger detail (the `dagger` skill) + the 8 functions + the 4 pipelines
