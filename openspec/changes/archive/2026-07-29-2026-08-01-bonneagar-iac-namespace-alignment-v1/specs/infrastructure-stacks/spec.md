## ADDED Requirements

### Requirement: Bonneagar IaC uses `cianfhoghlaim` namespace

The system SHALL require the Bonneagar IaC stack catalogue to use the
`cianfhoghlaim` namespace (not the pre-BIEP-v3 `oideachais` namespace).
The canonical stack directory is `bonneagar/stacks/cianfhoghlaim/`.

#### Scenario: Stack directory renamed

- **WHEN** `ls bonneagar/stacks/` runs
- **THEN** the canonical directory SHALL be `bonneagar/stacks/cianfhoghlaim/`
  (not `bonnegar/stacks/oideachais/`)
- **AND** the 6 files inside (`blueprint.yaml`, `compose.yaml`,
  `compose.dev.yaml`, `pangolin.yaml`, `sidecar.yaml`, `secrets.env`)
  SHALL all reference `cianfhoghlaim` (not `oideachais`)

#### Scenario: Komodo resource files renamed

- **WHEN** `ls bonneagar/komodo/{stacks,procedures}/` runs
- **THEN** the 2 renamed files SHALL be present:
  - `bonnegar/komodo/stacks/cianfhoghlaim-bunchloch.toml`
  - `bonnegar/komodo/procedures/deploy-cianchfhoghlaim-bunchloch.toml`

#### Scenario: Infisical secrets mirror the rename

- **WHEN** `.infisical.env:685-686` is read
- **THEN** the 2 secret paths SHALL be `infisical://dev-baile/cianfhoghlaim-llm/api_key` and
  `infisical://dev-baile/cianfhoghlaim-llm/provider` (not `oideachais-llm/...`)
- **AND** `bun run scripts/init-vault.ts` SHALL succeed cleanly