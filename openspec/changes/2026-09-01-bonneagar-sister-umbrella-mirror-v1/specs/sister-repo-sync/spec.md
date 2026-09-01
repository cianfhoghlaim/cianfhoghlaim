## ADDED Requirements

### Requirement: The bonneagar sister-repo umbrella mirror SHALL be tracked

The cianfhoghlaim monorepo SHALL maintain a
`bonneagar-sister-umbrella-mirror-v1` openspec change at
`openspec/changes/2026-09-01-bonneagar-sister-umbrella-mirror-v1/`
that tracks the bonneagar-side backlogs (the 6 GCP mirror
stacks promoted per
[`2026-08-31-sister-repo-gemini-lesson-transfer-v1/`](../2026-08-31-sister-repo-gemini-lesson-transfer-v1/)
§1 + the Stackdriver AI Agent ADK instrumentation) + the
per-PR reciprocal mirror contract + the per-quadrant DuckLake
`metadata_schema` + the per-sister Langfuse project mapping
(`bonneagar-dev` + `bonneagar-prod`).

The mirror MUST reference the canonical IaC surface at
`bonneagar/stacks/` (the 111 self-hosted stacks) and the 6
opt-in GCP mirror stacks at `bonneagar/stacks/gcp-*/`
(opt-in via `deployment-choice.yaml`).

#### Scenario: The bonneagar mirror change is in the active openspec list

- **WHEN** the operator runs `uv run openspec list | grep bonneagar-sister-umbrella-mirror`
- **THEN** the mirror change SHALL appear in the active list
- **AND** the mirror's `proposal.md` SHALL carry the 4 metadata fields
- **AND** `uv run openspec validate 2026-09-01-bonneagar-sister-umbrella-mirror-v1 --strict` SHALL exit 0