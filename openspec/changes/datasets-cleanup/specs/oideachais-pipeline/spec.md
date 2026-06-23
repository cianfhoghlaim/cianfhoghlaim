## MODIFIED Requirements

### Requirement: Sample data is stored in `oideachais/samplaí/` only
The oideachais quadrant SHALL store all Celtic-language and education
sample data in the canonical `oideachais/samplaí/` directory only. The
`oideachais/datasets/` directory SHALL NOT exist; if any process
re-creates it, the root `.gitignore` SHALL prevent it from being
tracked.

#### Scenario: New sample data is added
- **WHEN** a contributor adds a new Celtic-language sample, exam
  paper, or curriculum snippet
- **THEN** it MUST be placed under `oideachais/samplaí/{language}/`
  (e.g. `samplaí/gaeilge/`, `samplaí/cymraeg/`)
- **AND** it MUST NOT be placed under `oideachais/datasets/` (which
  does not exist and is gitignored)

#### Scenario: Private data must never be checked in
- **WHEN** a contributor works with real student names, addresses,
  or any other personally identifying information
- **THEN** the data MUST be redacted or anonymised before commit
- **AND** any pre-existing private data found in the repo MUST be
  removed in the same commit that discovers it (a separate cleanup
  change is acceptable but not required)

### Requirement: Secrets management follows the Infisical + Locket + mise contract
The Cianfhoghlaim monorepo SHALL manage secrets exclusively via the
Infisical vault (`dev-baile` environment) hydrated through the Locket
sidecar and `mise.toml` directory hooks. Legacy 1Password + SOPS
workflows from the predecessor `bonneagar` project SHALL NOT be
re-introduced.

#### Scenario: A new secret is needed
- **WHEN** a new secret is required for any service
- **THEN** it MUST be added to the root `.infisical.env` template
  using an `infisical://dev-baile/...` URI reference
- **AND** the vault must be updated with `bun run scripts/init-vault.ts`
- **AND** no plaintext secret value SHALL be written to any file
  tracked by git
