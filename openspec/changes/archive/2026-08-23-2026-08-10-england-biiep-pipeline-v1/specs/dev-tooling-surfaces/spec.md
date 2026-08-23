# Spec Delta: dev-tooling-surfaces

## ADDED Requirements

### Requirement: `2026-08-10-england-biiep-pipeline-v1` superseded

The system SHALL recognize that the England BIEP pipeline change is superseded by the canonical `british-isles-education-pipeline-v3` (the 5-milestone sequential plan + the 6-deferred-jurisdiction plan). The England ChangeDetection freshness guarantee is covered by the `upstream-package-monitoring` spec.

Per the 2026-08-22-stale-changes-triage-v1 (Group B: CLOSE).

#### Scenario: Agent looks up the England BIEP pipeline

- **WHEN** an agent looks up the England BIEP pipeline
- **THEN** the agent SHOULD load `british-isles-education-pipeline-v3` (the canonical)
- **AND** the older England-specific change is preserved as a historical reference