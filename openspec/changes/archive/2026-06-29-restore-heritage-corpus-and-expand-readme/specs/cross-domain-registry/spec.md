## MODIFIED Requirements

### Requirement: Wikipedia fixture storage convention

Every Wikipedia-derived source registered under the `culture` domain SHALL follow the dual-write pattern: a markdown clipping under `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/` AND a JSON fixture under `sruth/oideachais/dlt_sources/official_media/fixtures/identity_<slug>.json` (canonical home post-v4: `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/official_media/fixtures/identity_<slug>.json`).

#### Scenario: When a culture wikipedia source is added

- **WHEN** a new source `ie.culture.<entity>` with `kind: wikipedia_fixture` is registered
- **THEN** the build pipeline MUST create both the human-readable clipping AND the machine-readable DLT fixture
- **AND** the clipping SHALL carry Obsidian-style YAML frontmatter (title, source URL, author, published, created, description, tags: ["clippings", "culture"])
- **AND** the DLT fixture SHALL carry the canonical URL, the first-paragraph extract, and the article SHA-256 (so re-ingest can detect drift)

#### Scenario: When a Wikipedia page changes between fetches

- **WHEN** the article SHA-256 in the DLT fixture differs from a freshly-fetched version
- **THEN** the `lookup_wikipedia()` function MUST surface a `drift_detected` warning
- **AND** the warning MUST include both the old and new SHA-256

#### Scenario: When the heritage corpus is re-restored after a v4 consolidation (NEW)

- **WHEN** the `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/` directory is restored to the working tree after being dropped during a v4 consolidation
- **THEN** the restoration MUST come from the canonical pre-v4 branch (`q3-2026-oideachais-consolidation` as of 2026-06-28) via `git checkout <branch> -- "cian_mac_an_déisigh_uí_liatháin/"`
- **AND** the SHA-256 hash of each restored clipping MUST equal the SHA-256 recorded in the corresponding DLT fixture at `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/official_media/fixtures/identity_<slug>.json` (drift-detector invariant)
- **AND** an openspec change tracking the restoration MUST be filed with a `tracking_issues/unread-pdfs.md` that lists any path that the previous agent flagged as missing
