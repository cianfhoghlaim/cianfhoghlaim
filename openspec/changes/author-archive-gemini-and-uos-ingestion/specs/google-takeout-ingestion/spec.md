# Spec Delta — `google-takeout-ingestion` (new capability)

## Purpose

`google-takeout-ingestion` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives at `oideachais/dlt_sources/author_archive/google_takeout.py`. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.

Filesystem ingestion of Google Takeout archives (Phase 1) and, when the user provides OAuth credentials, OAuth-driven downloading + extraction (Phase 2) for one or more Google/Gemini accounts. Phase 2 is documented but not implemented in this change.

## ADDED Requirements

### Requirement: Takeout Directory Indexing (Phase 1)
The system SHALL index a Google Takeout directory (already extracted from a `.zip`) on the workstation, applying the standard `oideachais/dlt_sources/author_archive/_scanner.py` extraction pipeline.

#### Scenario: Takeout directory provided
- **GIVEN** the user has placed an extracted `Takeout/<account_label>/` directory on the workstation
- **AND** added an entry to `author_archive_accounts.yaml` with `account_label`, `takeout_path`, and `default_domain`
- **WHEN** the `author_archive_takeout_raw` Dagster asset is materialised for that partition
- **THEN** the `google_takeout_source()` DLT source SHALL walk every file under `takeout_path` recursively
- **AND** yield one row per file with `account=<account_label>`, `domain=<default_domain>`, `mime_type`, `modified_at`, `file_hash`, and `relative_path` (relative to `takeout_path`)

#### Scenario: Mime-type routing
- **GIVEN** a Takeout file is scanned
- **WHEN** the resource is selected
- **THEN** `application/pdf` files SHALL be yielded by the `takeout_pdf_documents` resource (with pymupdf extraction)
- **AND** `application/vnd.openxmlformats-officedocument.wordprocessingml.document` files SHALL be yielded by the `takeout_word_documents` resource (with python-docx extraction)
- **AND** `application/vnd.google-apps.document` (Google Docs) files SHALL be yielded by the `takeout_google_docs` resource as the exported `.docx` or `.pdf` mirror present in the Takeout

#### Scenario: Partition by account
- **GIVEN** the `author_archive_accounts` DynamicPartitionsDefinition is configured
- **WHEN** new accounts are added to `author_archive_accounts.yaml`
- **THEN** the Dagster sensor `author_archive_directory_sensor` SHALL pick up the new partition key on the next scan cycle (60 s)
- **AND** the corresponding `author_archive_takeout_raw` asset SHALL be materialisable for that partition

### Requirement: Configuration via YAML
The system SHALL load per-account Takeout configuration from a YAML file rather than hard-coded paths.

#### Scenario: Default config path
- **GIVEN** no `AUTHOR_ARCHIVE_ACCOUNTS_PATH` environment variable is set
- **WHEN** the `google_takeout_source()` is instantiated
- **THEN** the configuration SHALL be loaded from `./author_archive_accounts.yaml` (repo root)

#### Scenario: Custom config path
- **GIVEN** `AUTHOR_ARCHIVE_ACCOUNTS_PATH=/path/to/accounts.yaml`
- **WHEN** the source is instantiated
- **THEN** the configuration SHALL be loaded from that path

#### Scenario: Empty configuration
- **GIVEN** the YAML file is absent or empty
- **WHEN** the asset is materialised
- **THEN** the source SHALL yield zero rows and log a warning via `structlog` (`takeout_config_empty`)

### Requirement: GPG-At-Rest Opt-In
The system SHALL support an opt-in `gpg_encrypt_paths` knob on the Takeout source, default empty.

#### Scenario: Paths match
- **GIVEN** `gpg_encrypt_paths: ["identity/", "vetting/", "disability/", "catharnacht/"]` is set in the YAML
- **WHEN** a scanned file's relative path matches one of those prefixes
- **THEN** the `takeout_documents` resource SHALL encrypt the file's content with the workstation GPG key (looked up by `gpg --list-keys`) before yielding the row
- **AND** the `gpg_fingerprint` column SHALL record the recipient fingerprint

#### Scenario: Default behaviour
- **GIVEN** `gpg_encrypt_paths` is absent or empty
- **WHEN** the source runs
- **THEN** no file SHALL be encrypted
- **AND** the `gpg_fingerprint` column SHALL be `NULL`

## MODIFIED Requirements

*(None — this is a new capability.)*

## REMOVED Requirements

*(None.)*

## Out of Scope (Phase 2 — follow-up change)

- OAuth 2.0 flow with `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` (from the Infisical `google/oauth` vault path).
- Google Drive API v3 `files.list` for the `application/vnd.google-apps.document` and `application/pdf` MIME types in a configured folder.
- Gmail API export of `from:gemini.google.com` threads.
- Per-account refresh-token rotation; the OAuth helper at `oideachais/dlt_sources/author_archive/_oauth.py` (stub) will be the entry point.

These are explicitly deferred to a follow-up change once the user has provided the Takeout zips and confirmed the OAuth flow.
