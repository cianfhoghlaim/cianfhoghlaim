## ADDED Requirements

### Requirement: The 95-stack catalogue includes unsloth-serve

The Bonneagar `stacks/` directory SHALL contain 95 Docker Compose stacks (was 94), with the new `unsloth-serve` stack following the 6-file GOLD_STANDARD pattern plus 2 host-specific compose override files.

#### Scenario: unsloth-serve stack passes the stack-doctor CI gate

- **GIVEN** the new `bonneagar/stacks/unsloth-serve/` directory contains the 6 GOLD_STANDARD base files plus `compose.arm1-oci.yaml` and `compose.bunchloch.yaml`
- **WHEN** `mise run cic:stack-doctor --strict` is run
- **THEN** the unsloth-serve stack is reported as ✅ valid
- **AND** the secrets.env file contains only `infisical://dev-baile/unsloth/api-key` (no bare values)
- **AND** the pangolin.yaml declares the 2 private routes (`unsloth.cianfhoghlaim.ie` + `unsloth-api.cianfhoghlaim.ie`)
- **AND** the blueprint.yaml contains the Komodo stack registration

#### Scenario: unsloth-serve is on both Komodo resource-syncs

- **WHEN** `bonneagar/komodo/resource-syncs/arm1-oci.toml` and `bonneagar/komodo/resource-syncs/bunchloch.toml` are updated
- **THEN** `unsloth-serve` appears in both resource-syncs with the host-specific override (`compose.arm1-oci.yaml` on arm1-oci, `compose.bunchloch.yaml` on bunchloch)
- **AND** the deploy order is preserved (lakehouse → litellm → langfuse → unsloth-serve → mudstack consumers)
- **AND** the new Komodo procedure `unsloth-serve-deploy.toml` runs before the unsloth-serve stack is materialized
