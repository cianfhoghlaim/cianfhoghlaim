# pipeline-sister-repo-handoff Specification

## ADDED Requirements

### Requirement: sister-shared cross-repo contract

The system SHALL provide a `sister-shared` capability spec that
codifies the 5 Requirements every sister repo MUST inherit:

  R1. **4-tier `ModelProviderRouter`** — Unsloth Studio (primary)
     → LiteLLM proxy → MiniMax Token Plan → Gemini API. Each sister
     repo may override the model-default but MUST keep the 4-tier
     fallback shape.
  R2. **`JurisdictionPipelineBase` wholesale-copy convention** —
     sister repos copy the base class wholesale from cianfhoghlaim
     rather than re-implementing. Drift is monitored by
     `mise run lint:drift-docs`.
  R3. **`cocoindex_flows/_shared` wholesale-copy convention** —
     sister repos copy the shared CocoIndex helpers wholesale.
  R4. **openspec workflow shared** — sister repos use the same
     openspec CLI + the same proposal/tasks/spec delta format.
  R5. **`bonneagar/stacks/` GOLD_STANDARD shared** — sister repos
     declare their Docker Compose stacks with the same 6-file
     GOLD_STANDARD layout (compose + sidecar + secrets + pangolin
     + blueprint + .env.example).

#### Scenario: ciandlithe inherits the sister-shared contract

- **WHEN** ciandlithe's `agents/adk/` is loaded
- **THEN** the `agents.ciandlithe` package MUST import from the
  wholesale-copied `agents.adk.students_union.tools` namespace (per
  R1 + R2)
- **AND** the ciandlithe `bonneagar/stacks/` directory MUST contain
  the 6-file GOLD_STANDARD per stack (per R5)

### Requirement: cianfhoghlaim canonical surface

The system SHALL provide a `cianfhoghlaim` capability spec that
codifies the 4 Requirements for what stays in the cianfhoghlaim
monorepo (vs sister-owned):

  R1. **BIEP stays** — the British Isles Education Pipeline
     (6 LC subjects + gov.ie circulars + 7 CocoIndex flows +
     42 Dagster assets + 6 marimo notebooks) stays in cianfhoghlaim.
  R2. **CIANCHEILTIS bilingual alignment stays** — the en-ga /
     en-cy / en-gd cross-linguistic layer stays in cianfhoghlaim
     (the en-IE / en-NI / en-IM standalone language sources ship
     to sister repos).
  R3. **Tuatha + 8 NCCA agents stay** — the 8 NCCA subject agents
     (gael + math + appm + chem + comp + engl + geog + hist) +
     the tuatha educational MMO stay in cianfhoghlaim.
  R4. **Bonneagar IaC stays** — all 89 Docker Compose stacks
     + Komodo + Pangolin + Locket + Infisical stay in cianfhoghlaim.

#### Scenario: Sister repos are subsets of cianfhoghlaim

- **WHEN** the sister-repo handoff completes
- **THEN** cianchosaint owns: BIPP + BIDP + BIIP + OSINT allowlist
  + 35 specs
- **AND** ciandlithe owns: civil-litigation + 8 DLT sources + 7
  specs
- **AND** ciancheiltis owns: Celtic-language bilingual sources +
  13 spec
- **AND** tuatha owns: 3D Babylon.js MMO + 8 subject specialists
- **AND** gemini-hackathon owns: Flutter web refactor + per-source
  theming

### Requirement: cianchosaint 5-layer defs mirror

The system SHALL ship the cianchosaint/orchestration/defs/
directory as a MIRROR of cianfhoghlaim/orchestration/defs/ with
5 layer namespaces (1_ingestion, 2_materials, 3_model_lifecycle,
4_asset_generation, 5_agent_ops) + the canonical `Definitions`
loader.

#### Scenario: dg list defs returns the 5 layers

- **WHEN** `dg list defs` is run in cianchosaint
- **THEN** it returns 5 layer namespaces (not an empty list like
  pre-umbrella state)
- **AND** `dg list sensors` returns the relocated
  `licence_enforcement_sensor`
- **AND** the sensor loads under `2_materials/`
