# Spec Delta: british-isles-education-pipeline

## ADDED Requirements

### Requirement: BIEP v3 supersedes BIEP v1 — the unified umbrella

The system SHALL recognize `british-isles-education-pipeline-v3` (25 requirements) as the canonical umbrella for all British Isles education work. The pre-v3 spec `british-isles-education-pipeline` (41 requirements) was the v1 cohort of LC subjects + gov.ie circulars; that work has been re-scoped under the v3 5-milestone plan + the per-cohort 5-phase pattern.

When the `openspec archive --yes` of the 2026-08-22-openspec-audit-and-merge-v1 change runs:
- `british-isles-education-pipeline-v1` (the canonical spec at `openspec/specs/british-isles-education-pipeline/spec.md`) becomes a thin "v1 retirement marker" spec containing only the cross-reference Requirement below
- `british-isles-education-pipeline-v3` (the canonical spec at `openspec/specs/british-isles-education-pipeline-v3/spec.md`) is renamed to `british-isles-education-pipeline` (drop the `-v3` suffix) so it becomes the canonical name
- The cross-reference Requirements in the v1 + v2 specs ensure agents can find the canonical

The merge is non-destructive — no requirement text is lost, the 25 v3 requirements become the canonical, and the v1 retirement marker preserves the historical pointer.

#### Scenario: Agent looks up BIEP canonical spec

- **GIVEN** an agent reads `openspec/specs/british-isles-education-pipeline-v3/spec.md` for the canonical BIEP
- **WHEN** the agent runs `openspec list --specs`
- **THEN** the canonical name is `british-isles-education-pipeline` (was `british-isles-education-pipeline-v3`)
- **AND** the v3 requirements are unchanged
- **AND** the historical reference to v1 is at `openspec/changes/archive/` (where the v1 spec was archived)

### Requirement: BIEP v2 retirement — v2 is superseded by v3

The system SHALL recognize `british-isles-education-pipeline-v2` as a transitional spec (4 requirements: 4-jurisdiction coverage + 4-path OCR/VLM ensemble + Cross-jurisdiction marimo portal + England ChangeDetection freshness). All v2 work has been re-scoped under v3's milestone plan + per-cohort 5-phase pattern.

When the audit archive runs, `british-isles-education-pipeline-v2` becomes a retirement marker containing only this cross-reference Requirement.

#### Scenario: Agent looks up BIEP v2 work

- **WHEN** an agent reads `openspec/list --specs` to find the spec for "4-jurisdiction coverage"
- **THEN** the agent SHOULD load `british-isles-education-pipeline-v3` (not `-v2`)
- **AND** find the jurisdiction requirements under the v3 5-milestone plan + the deferred-jurisdiction plan (M5-M10)

## REMOVED Requirements

(None at this time — the v1 + v2 retirement happens in a follow-up Phase E change. This delta only ADDS the cross-reference Requirements that prepare the audit.)