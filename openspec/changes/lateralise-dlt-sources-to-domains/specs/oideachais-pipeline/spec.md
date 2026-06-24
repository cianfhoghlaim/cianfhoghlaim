## MODIFIED Requirements

### Requirement: DLT sources MUST live in the canonical {nation}/{domain} layout
The oideachais quadrant SHALL provide a single canonical layout
for dlt sources. Every `@dlt.source` function in
`oideachais/dlt_sources/` MUST live in a file whose path follows
the pattern `dlt_sources/domains/{domain}/{nation}/{source}.py`,
where `{domain}` is one of `education` / `medicine` / `law` /
`statistics` / `site_analysis` and `{nation}` is one of `ie` /
`en` / `ni` / `sct` / `wls` / `iom` / `jey` / `ggy`.

#### Scenario: A new dlt source is added
- **WHEN** a contributor adds a new `@dlt.source` for the
  education domain (UK, IE, or Crown Dependencies)
- **THEN** they MUST place it at
  `oideachais/dlt_sources/domains/education/{nation}/{source}.py`
  (NOT in `dlt_sources/uk/{nation}/` or `dlt_sources/ireland/`
  or `dlt_sources/crown_dependencies/`)

#### Scenario: A new dlt source is added for the medicine or law domain
- **WHEN** a contributor adds a new `@dlt.source` for the
  medicine or law domain
- **THEN** they MUST place it at
  `oideachais/dlt_sources/domains/{medicine|law}/{nation}/{source}.py`

#### Scenario: The legacy directory is encountered
- **WHEN** a contributor encounters a `dlt_sources/uk/`,
  `dlt_sources/ireland/`, or `dlt_sources/crown_dependencies/`
  file
- **THEN** that file MUST be a backward-compat re-export from
  the canonical `dlt_sources/domains/...` location
- **AND** the file MUST contain a deprecation notice pointing
  to the canonical location
- **AND** the legacy re-export shims MUST be removed in the
  next release (per REFACTORING.md)

### Requirement: AGENTS.md Quick routing table MUST point to the canonical location
The system MUST update the "Quick routing" table in
`oideachais/AGENTS.md` to point new contributors to the canonical
`dlt_sources/domains/{domain}/{nation}/` location. The routing
table MUST NOT include the legacy paths; all references MUST be
to the canonical {nation}/{domain} location.

#### Scenario: A new contributor reads the AGENTS.md routing table
- **WHEN** a contributor follows the routing table to add a
  new dlt source
- **THEN** they MUST find a row that says "add a new {nation}
  {domain} source to `dlt_sources/domains/{domain}/{nation}/`"
- **AND** the table MUST NOT include the legacy
  `dlt_sources/uk/`, `dlt_sources/ireland/`, or
  `dlt_sources/crown_dependencies/` paths
