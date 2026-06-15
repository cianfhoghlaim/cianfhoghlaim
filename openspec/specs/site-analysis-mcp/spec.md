# site-analysis-mcp Specification

## Purpose
TBD - created by archiving change lateralise-british-isles-domains. Update Purpose after archive.
## Requirements
### Requirement: BAML `SiteAnalysis` Schema

For every public source registered in `sources.yaml`, the system SHALL
produce a structured `SiteAnalysis` record (software fingerprint, layout
fingerprint, page description, screenshot path) and persist it as a DLT
source under `oideachais.site_analysis`. The record SHALL then be embedded
in LanceDB and cognified in Cognee, and exposed via a marimo dashboard.

The system SHALL provide `oideachais/baml_src/site_analysis.baml` defining:

- `class SiteAnalysis { source_id, captured_at, software, layout, pages_sampled, screenshot_path }`
- `class SoftwareFingerprint { cms, waf, captcha, analytics, framework_headers, fonts[] }`
- `class LayoutFingerprint { main_content_xpath, sticky_nav, cookie_banner, form_regions[], pagination_pattern }`
- `class PageDescription { url, h1, h2_hierarchy[], summary, links[], attachments[] }`

The generated BAML client SHALL be re‑exported via `baml_client.sync_client`.

#### Scenario: A page is analysed
- **GIVEN** a source URL from `sources.yaml`
- **WHEN** the operator runs `python -m oideachais.site_analysis.extract <id>`
- **THEN** a `SiteAnalysis` record is returned and stored as a row in `oideachais.site_analysis`

### Requirement: Firecrawl + Browserbase MCP Wiring

The system SHALL call the **firecrawl** and **browserbase** MCP servers
(declared in `opencode.json`) to produce the `SiteAnalysis` record.

- `firecrawl_firecrawl_extract` with a JSON schema derived from the BAML `SiteAnalysis` produces software + layout + description.
- `browserbase_screenshot` produces a full‑page screenshot written to `s3://lakehouse-site-analysis/{source_id}/screenshots/{date}.png`.

In test mode, the MCP clients SHALL be replaced by stub objects returning
fixed payloads from `oideachais/site_analysis/_stubs/`.

#### Scenario: MCP call succeeds
- **GIVEN** a live firecrawl + browserbase MCP server
- **WHEN** the extract command is run against a real source URL
- **THEN** a `SiteAnalysis` record and a screenshot are produced

#### Scenario: MCP call is stubbed in CI
- **GIVEN** `USE_LOCAL_SCRAPES=true` and the stub fixture
- **WHEN** the extract command is run
- **THEN** the stub is invoked and a record is produced without any live network call

### Requirement: LanceDB Embed + Cognee Cognify

The system SHALL embed the `description` and `summary` fields of every
`SiteAnalysis` record using `BAAI/bge-m3` (1024‑dim) via CocoIndex and store
the vectors in the LanceDB table `oideachais.site_analysis.descriptions`.

The system SHALL cognify every `SiteAnalysis` record into the Cognee dataset
`oideachais_site_analysis` with edge types `uses_cms`, `hosts_pdf`,
`requires_captcha`, `has_robots_txt`.

#### Scenario: Embed is produced
- **GIVEN** a row in `oideachais.site_analysis`
- **WHEN** the embed asset runs
- **THEN** the corresponding vector is searchable in LanceDB by description

#### Scenario: Cognify produces the knowledge graph
- **GIVEN** at least one `SiteAnalysis` row
- **WHEN** the cognify asset runs
- **THEN** `oideachais_site_analysis` Cognee dataset contains the expected nodes/edges

