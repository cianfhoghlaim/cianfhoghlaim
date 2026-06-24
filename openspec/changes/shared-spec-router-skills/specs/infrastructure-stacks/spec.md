## ADDED Requirements

### Requirement: Infrastructure stacks router skill

The infrastructure stacks capability MUST be discoverable via a single router skill at `.agents/skills/infrastructure-stacks/SKILL.md`. The router SHALL document the 6-file GOLD_STANDARD pattern, the 3-tier host convergence (arm1-oci / bunchloch / cax41-hetzner), the 5-stage deploy procedure, the 11 inventory categories, the 5 integration points (Pangolin / Locket / Komodo / LiteLLM / Langfuse), and the port allocation map.

#### Scenario: Agent finds the infrastructure router

- **WHEN** an agent searches for "add a stack", "fix stack", "stack-doctor", "GOLD_STANDARD", "compose.yaml", or "94 stacks"
- **THEN** the loader matches `.agents/skills/infrastructure-stacks/SKILL.md`
- **AND** the skill points at the underlying operational skills (kcg-convergence, stack-ops, kcg-bunchloch, pangolin, komodo, secrets-management)
