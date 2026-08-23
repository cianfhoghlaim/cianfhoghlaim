# Spec Delta: dev-tooling-surfaces

## ADDED Requirements

### Requirement: `2026-08-21-unsloth-v5-architecture-refinement-v1` superseded

The system SHALL recognize that the unsloth-v5 architecture refinement change is superseded by the archived `2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1` change. The refined topology (direct host + Pangolin private resource) is documented in the latter.

Per the 2026-08-22-stale-changes-triage-v1 (Group B: CLOSE).

#### Scenario: Agent looks up Unsloth v5 architecture

- **WHEN** an agent looks up the Unsloth v5 architecture
- **THEN** the agent SHOULD load `2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1` (archived)
- **AND** the refinement change is preserved as a historical reference