## MODIFIED Requirements

### Requirement: Wikipedia fixture storage convention

Every Wikipedia-derived source registered under the `culture` domain SHALL follow the dual-write pattern: a markdown clipping under `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/` AND a JSON fixture under `sruth/oideachais/dlt_sources/official_media/fixtures/identity_<slug>.json`.

The fixture corpus SHALL grow to **8 identity fixtures** (3 first-batch + 5 second-batch) by the close of `extend-culture-heritage-to-8-articles`. New fixtures beyond the 8 SHALL continue to follow the same dual-write convention.

#### Scenario: When a culture wikipedia source is added

- **WHEN** a new source `ie.culture.<entity>` with `kind: wikipedia_fixture` is registered
- **THEN** the build pipeline MUST create both the human-readable clipping AND the machine-readable DLT fixture
- **AND** the clipping SHALL carry Obsidian-style YAML frontmatter (title, source URL, author, published, created, description, tags: ["clippings", "culture"])
- **AND** the DLT fixture SHALL carry the canonical URL, the first-paragraph extract, and the article SHA-256 (so re-ingest can detect drift)

#### Scenario: When a Wikipedia page changes between fetches

- **WHEN** the article SHA-256 in the DLT fixture differs from a freshly-fetched version
- **THEN** the `lookup_wikipedia()` function MUST surface a `drift_detected` warning
- **AND** the warning MUST include both the old and new SHA-256

#### Scenario: When the second batch of 5 Wikipedia fixtures is added

- **WHEN** the `extend-culture-heritage-to-8-articles` change adds 5 new fixtures for Leath Cuinn, Cian, Aos Sí, Tuatha Dé Danann, and Déisi
- **THEN** all 8 fixtures SHALL resolve via the DLT `wikipedia_fixtures` path-glob (`identity_*.json` in `sruth/oideachais/dlt_sources/official_media/fixtures/`)
- **AND** all 8 fixtures SHALL carry the canonical `lineage/` path in their `clipping_path` field (the legacy `deacy/` path is removed)
- **AND** the `culture_heritage` Cognee dataset SHALL ingest the 8 articles on the next `cognee.cognify()` run

#### Scenario: When a user opens the README personal section

- **WHEN** a reader opens `README.md` lines 312–596
- **THEN** the "About the author, the name, and the lineage" section SHALL contain exactly 6 subsections (A=username, B=family, C=claim, D=joint-claim, E=qualifications, F=repository-name)
- **AND** no occurrence of "lighthearted", "tongue-in-cheek", "playful homage", or "Coláiste na Ríoga" SHALL remain
- **AND** the byline (line 596) SHALL contain the verbatim phrase "born a British citizen and obliged by oath of allegiance to King Charles the Third"
- **AND** 8 Wikipedia citations + 6 PDF citations SHALL be listed under section C