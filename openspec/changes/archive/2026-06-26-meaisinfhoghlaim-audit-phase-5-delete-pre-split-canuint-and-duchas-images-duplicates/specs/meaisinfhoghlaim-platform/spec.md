# Spec Delta: meaisinfhoghlaim-platform — Phase 5 (delete pre-split `canuint.py` + `duchas_images.py` duplicates)

## ADDED Requirements

### Requirement: No pre-split multi-source DLT file duplicates in meaisínfhoghlaim

The meaisínfhoghlaim quadrant MUST NOT contain a single `.py` file that
bundles multiple `@dlt.source` functions together when those same
source functions already exist as separate canonical files in
`sruth/oideachais/dlt_sources/ie/{culture,education,...}/`.

If a DLT source function exists at the canonical split location
(e.g. `sruth.oideachais.dlt_sources.ie.culture.canuint.canuint_source`),
meaisínfhoghlaim MUST NOT retain a duplicate copy in a pre-split
multi-source file (e.g. `sruth.meaisinfhoghlaim.language.gaeilge.canuint`).

The canonical home for each multi-source DLT pattern is one
canonical file per `@dlt.source` function. Any pre-split bundled
copy is a stale duplicate and MUST be deleted.

#### Scenario: A meaisínfhoghlaim pre-split multi-source DLT file exists

- **GIVEN** a meaisínfhoghlaim file at
  `sruth/meaisinfhoghlaim/language/gaeilge/canuint.py` (1,041 lines)
  bundles 5 `@dlt.source` functions
  (`canuint_source` + `canuint_search_source` + `canuint_audio_source`
  + `canuint_dialect_summary_source` + `canuint_word_alignment_source`)
- **AND** the canonical split already exists at
  `sruth/oideachais/dlt_sources/ie/culture/{canuint,canuint_search,canuint_audio,canuint_dialect_summary,canuint_word_alignment}.py`
  (1,095 lines across 5 files)
- **AND** the canonical split files all import cleanly via
  `PYTHONPATH=./sruth python3 -c "from sruth.oideachais.dlt_sources.ie.culture.canuint import canuint_source"`
- **WHEN** the audit confirms the pre-split file has 0 active
  importers across `sruth/`
- **THEN** the pre-split file MUST be deleted
  (via `git mv` into the openspec change archive)
- **AND** any future DLT source function additions MUST go to a
  NEW canonical file at
  `sruth/oideachais/dlt_sources/ie/{culture,education,...}/<entity>.py`,
  NOT to a pre-split multi-source file in meaisínfhoghlaim

#### Scenario: A future contributor wants to add a 6th canuint source

- **GIVEN** the canonical 5 canuint split files exist at
  `sruth/oideachais/dlt_sources/ie/culture/`
- **WHEN** a 6th canuint source function needs to be added
  (e.g. `canuint_regional_dialect_comparison_source`)
- **THEN** the contributor MUST create a new file
  `sruth/oideachais/dlt_sources/ie/culture/canuint_regional_dialect_comparison.py`
  (the canonical split location)
- **AND** the contributor MUST NOT recreate a pre-split multi-source
  file at `sruth/meaisinfhoghlaim/language/gaeilge/canuint.py`
- **AND** the contributor MUST update the existing Phase 2 / Phase 5
  audit-trail rows in `sruth/meaisinfhoghlaim/README.md` if the new
  source introduces a fresh canonical split
