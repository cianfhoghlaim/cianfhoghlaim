# Cross-Domain Registry Specification

## Purpose

`cross-domain-registry` is the canonical capability spec for the 8-nation × 7-domain asset-key contract that every DLT source and Dagster asset in the Cianfhoghlaim platform MUST honour. The contract enforces a single source-of-truth for asset keys (so the cross-domain collision detector in CI can catch conflicts) and a uniform shape for `sruth/oideachais/sources.yaml` entries.

This spec was created by archiving change `ingest-culture-heritage` (which also introduced the 6th domain `culture`). See `openspec/changes/ingest-culture-heritage/proposal.md` for the originating change.

## Background

The platform organises every data source by:

- **Nation** (one of `ie`, `ni`, `en`, `sct`, `wls`, `iom`, `jey`, `ggy`)
- **Domain** (one of `education`, `medicine`, `law`, `statistics`, `site_analysis`, `culture`)
- **Kind** (`filesystem_pdf`, `rest_api`, `wikipedia_fixture`, `rss`, `csv`, `gdelt`, etc.)

The asset key convention is `{nation}.{domain}.{entity}`. Examples:

- `ie.education.primary.maths` — Irish primary maths curriculum
- `ie.culture.claiming_r_na_gaillimhe` — Irish cultural-heritage synthesis (new in this change)

The 7 domains were originally: `education`, `medicine`, `law`, `statistics`, `site_analysis`. The 6th domain `culture` is added by `ingest-culture-heritage`.

## Requirements

### Requirement: Culture domain registry

The cross-domain-registry SHALL recognise `culture` as a valid domain under all 8 supported nations (`ie`, `ni`, `en`, `sct`, `wls`, `iom`, `jey`, `ggy`).

#### Scenario: When a culture source is registered under nation ie

- **WHEN** an operator adds a `kind: filesystem_pdf` or `kind: wikipedia_fixture` source with `domain: culture` and `nation: ie`
- **THEN** the asset key resolves to `ie.culture.<entity>`
- **AND** the source is discoverable by the `ingest-culture-heritage` Dagster asset group

#### Scenario: When a culture source conflicts with a non-culture domain

- **WHEN** two sources claim the same `ie.culture.<entity>` key
- **THEN** `openspec validate` SHALL fail with a domain-collision error
- **AND** the conflict is reported with both source IDs and their respective file paths

#### Scenario: When a culture source is added under a different nation

- **WHEN** a culture source is registered under any of the 8 nations
- **THEN** the asset key resolves to `<nation>.culture.<entity>`
- **AND** the source is discoverable by the same asset group regardless of nation

### Requirement: Wikipedia fixture storage convention

Every Wikipedia-derived source registered under the `culture` domain SHALL follow the dual-write pattern: a markdown clipping under `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/` AND a JSON fixture under `sruth/oideachais/dlt_sources/official_media/fixtures/identity_<slug>.json`.

#### Scenario: When a culture wikipedia source is added

- **WHEN** a new source `ie.culture.<entity>` with `kind: wikipedia_fixture` is registered
- **THEN** the build pipeline MUST create both the human-readable clipping AND the machine-readable DLT fixture
- **AND** the clipping SHALL carry Obsidian-style YAML frontmatter (title, source URL, author, published, created, description, tags: ["clippings", "culture"])
- **AND** the DLT fixture SHALL carry the canonical URL, the first-paragraph extract, and the article SHA-256 (so re-ingest can detect drift)

#### Scenario: When a Wikipedia page changes between fetches

- **WHEN** the article SHA-256 in the DLT fixture differs from a freshly-fetched version
- **THEN** the `lookup_wikipedia()` function MUST surface a `drift_detected` warning
- **AND** the warning MUST include both the old and new SHA-256