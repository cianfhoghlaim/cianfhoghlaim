# agent-memory-systems — MODIFIED Scenarios

> **MODIFIED** by `2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1/`.

The pre-v7 spec referenced `bonneagar/stacks/{mlflow,lakehouse,...}/`
which is still correct post-v7 (bonneagar/ is preserved). No
structural changes needed; only a clarifying note about the
in-tree location.

## ADDED Note

### Path Resolution

All `bonneagar/stacks/<name>/` references in this spec resolve to
files at the v7 main repo root under `bonneagar/stacks/<name>/`.
The pre-v7 separate-repo URL pattern
`https://github.com/cianfhoghlaim/bonneagar/blob/main/stacks/<name>/...`
SHALL be replaced with the in-repo relative path
`bonneagar/stacks/<name>/...`.

### Scenario reference updates

- `bonneagar/stacks/mlflow/secrets.env` → unchanged
- `bonneagar/stacks/lakehouse/secrets.env` → unchanged
- `bonneagar/stacks/graphiti/secrets.env` → unchanged
- `bonneagar/stacks/falkordb/secrets.env` → unchanged
- `bonneagar/stacks/langfuse/blueprint.yaml` → unchanged
- `bonneagar/stacks/langfuse/compose.yaml` → unchanged
- `bonneagar/stacks/graphiti/blueprint.yaml` → unchanged
- `bonneagar/stacks/graphiti/compose.yaml` → unchanged
- `bonneagar/stacks/cognee/blueprint.yaml` → unchanged
- `bonneagar/stacks/cognee/compose.yaml` → unchanged
- `bonneagar/stacks/<name>/pangolin.yaml` (for 88 stacks) → unchanged

All scenarios that reference these paths continue to resolve
correctly after v7 because the bonneagar/ subdirectory preserves
the same internal layout as the standalone bonneagar repo.

## ADDED Requirements

### Requirement: NEW — In-tree path references are repo-relative

All documentation, scripts, and tools that reference IaC stack files MUST use the repo-relative path `bonneagar/stacks/<name>/...`, NOT the pre-v7 standalone-repo URL pattern. This MUST be enforced by a CI grep that fails the build if the pre-v7 URL pattern appears in any new commit.

#### Scenario: Stack file path is repo-relative

- **WHEN** a script or doc references an IaC stack file
- **THEN** it SHALL use the path `bonneagar/stacks/<name>/<file>`
  (relative to the repo root)
- **AND** it SHALL NOT reference the standalone-repo URL
  `https://github.com/cianfhoghlaim/bonneagar/...`
