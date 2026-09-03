# official-media-pipeline Specification

## Purpose

`official-media-pipeline` is a capability of the Cianfhoghlaim
platform. It is the **British-Isles government source enrichment
pipeline**: turn an Instagram-export photo + caption into a structured
record identifying the government organisation that posted it (or
should have). The pipeline uses DLT to scrape official government
sources, BAML `ClassifyOfficialMedia` to classify + entity-link, and a
4-lookup resolver (Mastodon webfinger + Bluesky xrpc + Wikipedia REST +
Companies House / CRO lookup) to find the canonical identity.

The corresponding source code lives at:

- `cianfhoghlaim/dlt/official_media/` (the 3 jurisdictions × EN/NI/IE/Scotland prerelease DLT sources)
- `cianfhoghlaim/baml/official_media/classify_official_media.baml`
- `cianfhoghlaim/agents/meaisinfhoghlaim/official_media_resolver.py`
- Dagster group `official_media` for the 2 pre-research + 3 enrichment assets

Migrated from `author-archive-pipeline` (the pre-research logic was the
prototype of this capability post-v4).
## Requirements
### Requirement: InstagramExportIngest

The system SHALL provide a DLT source at
`cianfhoghlaim/dlt_sources/official_media/instagram_export.py` that parses
the JSON bundle Instagram ships in the standard export format
(`connections/followers_and_following/*.json`,
`logged_information/recent_searches/*.json`,
`ads_information/ads_and_topics/*.json`,
`apps_and_websites_off_of_instagram/apps_and_websites/*.json`).

#### Scenario: Standard export parses end-to-end

- **GIVEN** an Instagram export directory at the path in the
  `OIDEACHAIS_IG_EXPORT_DIR` env var
- **AND** the directory contains the standard
  `connections/followers_and_following/{followers_1,following,
  close_friends,blocked_profiles,pending_follow_requests,
  removed_suggestions,restricted_profiles}.json` files
- **WHEN** `instagram_export_source().resources["profiles"]` is iterated
- **THEN** exactly one DLT row SHALL be yielded per profile
- **AND** the row SHALL contain `ig_username`, `ig_href`, `list_kind`,
  `followed_at`, `ig_export_id` columns
- **AND** the `write_disposition` SHALL be `merge` with
  `primary_key=["ig_export_id","ig_username","list_kind"]`

#### Scenario: Missing files are skipped with a warning

- **GIVEN** the export directory has `followers_1.json` and
  `following.json` but no `close_friends.json`
- **WHEN** the source is iterated
- **THEN** the missing file SHALL be skipped (not raise)
- **AND** a `structlog.warning("instagram_export_missing", file=...)` line
  SHALL be emitted

### Requirement: OfficialMediaAllowlistFilter

The system SHALL provide a two-stage filter that distinguishes
**official-media** profiles (British Isles government / political /
public-service / university / emergency-services / intelligence-agency)
from private profiles (friends, family, celebrities).

#### Scenario: Stage-1 allowlist match

- **GIVEN** the username `mi5official` is in
  `fixtures/allowlist_intelligence.yaml`
- **WHEN** `allowlist_filter.classify("mi5official")` is called
- **THEN** it SHALL return `{"is_official": true, "stage": 1,
  "category": "intelligence", "source": "allowlist_intelligence.yaml"}`

#### Scenario: Stage-1 no-match for private profile

- **GIVEN** the username `i_am_uk7` is in **no** allowlist
- **AND** it does NOT match the cheap heuristic (no `.gov`, no
  `official`, no `.ie`/`.uk`/`.ac` in the bio, no verified badge)
- **WHEN** `allowlist_filter.classify("i_am_uk7", bio="...")` is called
- **THEN** it SHALL return `{"is_official": false, "stage": 1,
  "category": null, "source": "heuristic_reject"}`
- **AND** the BAML fallback SHALL NOT be invoked

#### Scenario: Stage-2 BAML fallback for lookalike

- **GIVEN** the username `metpolice_official2024` is in **no** allowlist
- **AND** the cheap heuristic matches (`police` + `official` in bio)
- **WHEN** `allowlist_filter.classify("metpolice_official2024",
  bio="The official Metropolitan Police account")` is called
- **THEN** the BAML `ClassifyOfficialMedia` function SHALL be invoked
  with `client "extract"` (LiteLLM gateway)
- **AND** if BAML returns `is_official_media=true` with
  `confidence >= 0.7`, the result SHALL be
  `{"is_official": true, "stage": 2, "category": BAML.category,
  "source": "baml_classifier"}`

### Requirement: OfficialMediaDiscovery

The system SHALL resolve, for each surviving official-media profile,
the canonical official source through 4 parallel lookups:

1. Wikipedia REST summary endpoint
   (`en.wikipedia.org/api/rest_v1/page/summary/{title}`)
2. Companies House (UK) / CRO (ROI) entity search
3. Mastodon handle resolution via webfinger
   (`https://host/.well-known/webfinger?resource=acct:user@host`)
4. Bluesky DID via the public
   `public.api.bsky.app/xrpc/app.bsky.actor.searchActors?q=...` endpoint

The 4 lookups SHALL be invoked **in parallel** via `asyncio.gather`
(off the main thread) and SHALL short-circuit on
`official_media_overrides.yaml` for the 4 seed intelligence agencies
(mi5, mi6, gchq, hmgcc).

#### Scenario: Override short-circuit

- **GIVEN** the candidate `ig_username="gchq"` has an override in
  `fixtures/official_media_overrides.yaml`
- **WHEN** `source_resolver.resolve("gchq", stage=1)` is called
- **THEN** the override SHALL be returned immediately
- **AND** NO network calls SHALL be made (Wikipedia, Companies House,
  Mastodon, Bluesky all skipped)
- **AND** the result SHALL contain
  `{"official_website": "https://www.gchq.gov.uk", "wikipedia_url":
  "https://en.wikipedia.org/wiki/GCHQ", "resolver_notes":
  "override"}`

#### Scenario: Live lookup fan-out (USE_LIVE_LOOKUPS=true)

- **GIVEN** the candidate `ig_username="metpoliceuk"` has NO override
- **AND** `USE_LIVE_LOOKUPS=true` is set
- **WHEN** `source_resolver.resolve("metpoliceuk", stage=1)` is called
- **THEN** exactly 4 network calls SHALL be made in parallel
  (Wikipedia, Companies House, Mastodon webfinger, Bluesky xrpc)
- **AND** the rate limiter SHALL enforce a maximum of 1 req/sec per
  authority
- **AND** the result SHALL be a dict with at most 4 non-null resolved
  fields

#### Scenario: Offline stub mode (USE_LIVE_LOOKUPS=false)

- **GIVEN** `USE_LIVE_LOOKUPS=false` (the CI default)
- **WHEN** any non-override candidate is resolved
- **THEN** Wikipedia / Companies House / Mastodon / Bluesky SHALL all
  return `None` for their respective fields
- **AND** a `structlog.debug("lookup_skipped_offline", authority=...)`
  line SHALL be emitted per authority
- **AND** the function SHALL NOT raise

### Requirement: OfficialMediaLakehouseTables

The system SHALL write the enriched records to the lakehouse under the
`cianfhoghlaim.official_media.*` namespace (DuckLake), with at minimum:

- `cianfhoghlaim.official_media.candidates` — one row per surviving
  Instagram profile (after Stage-1 + Stage-2 filter)
- `cianfhoghlaim.official_media.resolved_sources` — one row per resolved
  source (after the 4-lookup fan-out)
- `cianfhoghlaim.official_media.descriptions` — LanceDB table of BGE-M3
  embeddings of the resolved source summaries

#### Scenario: DLT write disposition

- **GIVEN** the `candidates` resource yields N rows
- **WHEN** the Dagster asset `official_media_extract` materialises
- **THEN** `cianfhoghlaim.official_media.candidates` SHALL contain exactly
  N rows (write_disposition=`merge`)
- **AND** the primary key SHALL be `(ig_export_id, ig_username)`
- **AND** the asset SHALL be tagged `group_name="official_media"`

#### Scenario: Embedding table seeded

- **GIVEN** `cianfhoghlaim.official_media.resolved_sources` has 10 rows
- **WHEN** the `official_media_embed` asset materialises
- **THEN** `cianfhoghlaim.official_media.descriptions` SHALL contain 10
  rows of 1024-dim float vectors (BGE-M3)
- **AND** the metadata SHALL record `{"model": "BAAI/bge-m3",
  "vector_dim": 1024, "rows_embedded": 10}`


## Migrated from (2026-07-06)

- `author-archive-credit-budget` — the Credit Budget pattern moved here
- `author-archive-pipeline` — the pre-research pipeline is now the L1 ingestion step here
- `author-archive-web-scraping` — the BackendRouter is now the `official-media-pipeline` browser layer
