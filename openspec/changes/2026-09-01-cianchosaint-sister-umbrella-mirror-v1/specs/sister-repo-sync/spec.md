## ADDED Requirements

### Requirement: The cianchosaint sister-repo umbrella mirror SHALL be tracked

The cianfhoghlaim monorepo SHALL maintain a
`cianchosaint-sister-umbrella-mirror-v1` openspec change at
`openspec/changes/2026-09-01-cianchosaint-sister-umbrella-mirror-v1/`
that tracks the 11 cianchosaint-side backlogs
(`cianchosaint-init-v1` + `cianchosaint-bipp-v2-spec-v1` +
`cianchosaint-bipp-v2-baml-v1` +
`cianchosaint-bipp-v2-political-party-v2-v1` +
`cianchosaint-cognee-graphiti-political-v1` +
`cianchosaint-collaboration-workspace-v1` +
`cianchosaint-garda-prompt-workflow-v1` +
`cianchosaint-generative-ui-kit-v1` +
`cianchosaint-langfuse-dashboard-v1` +
`cianchosaint-langfuse-prompt-management-v1` +
`cianchosaint-ragas-eval-pipeline-v1`) + the per-PR
reciprocal mirror contract + the per-quadrant DuckLake
`metadata_schema` + the per-sister Langfuse project mapping
(`cianchosaint-dev` + `cianchosaint-prod`).

#### Scenario: The cianchosaint mirror change is in the active openspec list

- **WHEN** the operator runs `uv run openspec list | grep cianchosaint-sister-umbrella-mirror`
- **THEN** the mirror change SHALL appear in the active list
- **AND** the mirror's `proposal.md` SHALL carry the 4 metadata fields
- **AND** `uv run openspec validate 2026-09-01-cianchosaint-sister-umbrella-mirror-v1 --strict` SHALL exit 0