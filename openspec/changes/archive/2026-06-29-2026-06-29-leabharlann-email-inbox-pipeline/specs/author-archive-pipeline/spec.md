# `author-archive-pipeline` capability spec — leabharlann-email-inbox-pipeline delta

The `author-archive-pipeline` capability spec governs the
author-archive DLT sources (UoG artefacts, Gemini Deep
Research, Google Takeout Phase 1) and the 7 + 7 + 1 Dagster
assets in the `author_archive_ingestion` group.

This delta extends the `author-archive-pipeline` capability
with a cross-reference to the new email-inbox pipeline (the
`leabharlann_email_inbox` source + the 5 new inbox Dagster
assets) so the two namespaces share configuration + Dagster
group naming conventions.

## ADDED Requirements

### Requirement: Cross-reference to `leabharlann-email-inbox-pipeline`

The system SHALL cross-reference the new
`leabharlann-email-inbox-pipeline` change from the
`author-archive-pipeline` capability so the two namespaces
share the same `author_archive_accounts.yaml` schema and the
same `TakeoutAccountConfig` dataclass.

#### Scenario: Shared account schema

- **GIVEN** 4 email accounts (`dkit_ie`, `gmail_personal`,
  `gmail_academic`, `hotmail_legacy`) in
  `author_archive_accounts.yaml`
- **WHEN** the `leabharlann_email_inbox_source()` source
  loads the YAML
- **THEN** it uses the same `TakeoutAccountConfig` dataclass
  as `leabharlann.google_takeout_source`
- **AND** the same `gpg_encrypt_paths` knob is honoured

#### Scenario: Dagster group naming convention

- **GIVEN** the 5 new email-inbox assets
- **WHEN** they register in Dagster
- **THEN** they use the `group_name="leabharlann_ingestion"`
  convention (NOT `author_archive_ingestion`)
- **AND** the original 7 `author_archive_ingestion` assets
  are unchanged

## MODIFIED Requirements

*(None — the change only ADDS the cross-reference; the 7
original `author_archive_ingestion` assets are unchanged.)*

## REMOVED Requirements

*(None.)*
