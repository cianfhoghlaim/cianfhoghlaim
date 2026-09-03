# infrastructure-stacks

> STUB — to be filled by Phase 2 research agent. Covers the
> infrastructure-tier packages: olake, planetscale, postgresql,
> openchamber, openclaw, litellm, pangolin, komodo, infisical,
> mlx-omni, invokeai, nimtable, dragonfly, risingwave.

## ADDED Requirements

### Requirement: 6-file GOLD_STANDARD alignment

The infrastructure stacks SHALL remain compatible with the
6-file GOLD_STANDARD pattern (compose.yaml + sidecar.yaml +
pangolin.yaml + secrets.env + blueprint.yaml + .env.example)
documented in `openspec/research/2026-06-28-browserbase-credit-program/phase-2/`.

#### Scenario: New stack onboarding

WHEN a new infrastructure stack is added,
THEN it SHALL pass `bun run validate-stacks` AND align with
the patterns documented in the Phase 2 research output.
