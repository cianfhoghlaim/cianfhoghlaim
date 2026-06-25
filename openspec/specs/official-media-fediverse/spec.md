# official-media-fediverse Specification

## Purpose
TBD - created by archiving change official-media-pipeline. Update Purpose after archive.
## Requirements
### Requirement: FediverseHandleResolution

The system SHALL provide a module at
`sruth/oideachais/dlt_sources/official_media/fediverse.py` that resolves
Mastodon and Bluesky handles to their canonical URL via the standard
public protocols.

#### Scenario: Mastodon webfinger success

- **GIVEN** the handle `@metpolice@masodon.club` is a valid Mastodon
  account (mocked webfinger response returns an `acct` link to
  `https://masodon.club/@metpolice`)
- **WHEN** `fediverse.resolve_mastodon("metpolice", host="masodon.club")`
  is called
- **THEN** the result SHALL be
  `{"platform": "mastodon", "handle": "@metpolice@masodon.club", "url":
  "https://masodon.club/@metpolice", "resolved_at": <iso8601>}`

#### Scenario: Bluesky xrpc success

- **GIVEN** the search term `metpoliceuk` returns one match in the
  public Bluesky index (mocked xrpc response)
- **WHEN** `fediverse.resolve_bluesky("metpoliceuk")` is called
- **THEN** the result SHALL be
  `{"platform": "bluesky", "handle": "metpoliceuk.bsky.social", "url":
  "https://bsky.app/profile/metpoliceuk.bsky.social", "did":
  "did:plc:...", "resolved_at": <iso8601>}`

#### Scenario: Rate limit respected

- **GIVEN** 5 webfinger calls in 1 second are attempted
- **WHEN** they are executed via `fediverse.resolve_mastodon(...)`
- **THEN** the rate limiter SHALL enforce at most 1 req/sec per host
- **AND** subsequent calls SHALL be queued and retried with backoff
- **AND** the total wall time SHALL be ≥ 4 seconds

#### Scenario: Network failure returns None gracefully

- **GIVEN** the webfinger request raises `httpx.ConnectError`
- **WHEN** `fediverse.resolve_mastodon("metpolice", host="deadhost.club")`
  is called
- **THEN** the function SHALL return `None` (not raise)
- **AND** a `structlog.warning("webfinger_failed", host=...,
  error=str(exc))` line SHALL be emitted

### Requirement: WikipediaAndCompaniesHouseLookup

The system SHALL provide a module at
`sruth/oideachais/dlt_sources/official_media/source_resolver.py` that resolves
the canonical Wikipedia article and Companies House / CRO entity for
each candidate.

#### Scenario: Wikipedia summary retrieved

- **GIVEN** the title `Metropolitan Police` resolves to a Wikipedia
  article (mocked `en.wikipedia.org/api/rest_v1/page/summary/Metropolitan_Police`
  response with extract)
- **WHEN** `source_resolver.lookup_wikipedia("Metropolitan Police")` is
  called
- **THEN** the result SHALL be
  `{"wikipedia_url":
  "https://en.wikipedia.org/wiki/Metropolitan_Police", "extract": "...",
  "resolved_at": <iso8601>}`

#### Scenario: Companies House match for UK public body

- **GIVEN** the search term `Metropolitan Police` returns one match on
  the Companies House API (mocked)
- **WHEN** `source_resolver.lookup_companies_house("Metropolitan
  Police")` is called
- **THEN** the result SHALL be
  `{"companies_house_id": "12086314", "company_name": "Metropolitan
  Police Service", "company_status": "active", "resolved_at": <iso8601>}`

#### Scenario: CRO lookup for Irish body

- **GIVEN** the search term `University of Galway` returns one match on
  the CRO API (mocked)
- **WHEN** `source_resolver.lookup_cro("University of Galway")` is
  called
- **THEN** the result SHALL be
  `{"cro_number": "123456", "company_name": "University of Galway",
  "resolved_at": <iso8601>}`

