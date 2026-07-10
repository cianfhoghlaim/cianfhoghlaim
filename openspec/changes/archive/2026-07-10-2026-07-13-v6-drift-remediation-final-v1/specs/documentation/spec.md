# Spec Delta: documentation

## ADDED Requirements

### Requirement: Per-stack docs cross-reference every active stack

The system SHALL maintain one Markdown cross-reference document for every active stack in the stack inventory. Each active stack listed in `docs/stacks/README.md` SHALL have a corresponding `docs/stacks/<name>.md` document, using the documented stack-doc template.

The docs contract SHALL remain separate from the `bonneagar/` source-of-truth stack files: this repo documents and validates cross-references, while the separate `bonneagar` repo owns the live `bonneagar/stacks/<name>/` stack definitions.

#### Scenario: Stack docs inventory is complete

- **GIVEN** the stack inventory lists an active stack name `<name>`
- **WHEN** a contributor runs the stack-doc completeness check
- **THEN** `docs/stacks/<name>.md` SHALL exist
- **AND** the document SHALL include purpose, GitOps rationale, cross-references, and tags sections

#### Scenario: Missing generator is treated as deferred implementation work

- **GIVEN** this final drift cleanup change is implemented
- **AND** the optional T1 generator `scripts/generate-stack-docs.ts` is not present in the Cianfhoghlaim worktree
- **WHEN** the optional T1 follow-up is evaluated
- **THEN** stack-doc generation MAY be deferred
- **AND** the OpenSpec proposal MUST record the deferred status rather than modifying the separate `bonneagar/` repo

#### Scenario: Stack docs do not hand-edit secrets

- **GIVEN** a stack doc references a stack's secret contract
- **WHEN** the doc describes how runtime secrets are hydrated
- **THEN** it SHALL point to Infisical + Locket + mise
- **AND** it SHALL NOT instruct contributors to manually create `.env` files
