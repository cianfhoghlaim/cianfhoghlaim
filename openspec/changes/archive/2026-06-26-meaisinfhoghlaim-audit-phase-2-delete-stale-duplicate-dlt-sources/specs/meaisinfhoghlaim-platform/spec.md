## ADDED Requirements

### Requirement: No duplicate DLT source implementations across quadrants

The meaisínfhoghlaim quadrant MUST NOT contain a `.py` file in
`sruth/meaisinfhoghlaim/language/<lang>/` that re-implements a
DLT source already living at the canonical home
`sruth/oideachais/dlt_sources/{nation}/{domain}/<entity>.py`.
Canonical homes are determined by the Round 11 audit:

- `oideachais/data_platform/` umbrella was deleted in commit
  `8484a6353` (the predecessor `bonneagar` project package
  removal)
- `oideachais/dlt_sources/celtic/` umbrella was deleted in
  Phase 3B (`oideachais-audit-phase-3b-drop-domains-wrapper`)
- `oideachais/dlt_sources/<flat>.py` flat files were migrated to
  the country-first layout in Phases 3C, 3D, 4
- The canonical layout is
  `dlt_sources/{nation}/{domain}/{entity}.py` (one file per
  `@dlt.source` function, with shared helpers in sibling
  `_<entity>_helpers.py` files)

If meaisínfhoghlaim requires a Celtic-language DLT source, it
MUST import from the canonical home via
`from oideachais.dlt_sources.<nation>.<domain> import <entity>_source`,
NOT re-implement the source at a meaisínfhoghlaim-local path.

#### Scenario: A meaisínfhoghlaim `language/gaeilge/` file re-implements a canonical DLT source

- **GIVEN** the canonical DLT source for Dúchas.ie lives at
  `sruth/oideachais/dlt_sources/ie/culture/duchas.py` with
  `@dlt.source(name="duchas_folklore") def duchas_source(...)`
- **AND** the meaisínfhoghlaim quadrant contains a
  `sruth/meaisinfhoghlaim/language/gaeilge/duchas.py` with the
  same `@dlt.source(name="duchas_folklore") def duchas_source(...)`
  decorator (verified by `grep -n "@dlt.source"`)
- **WHEN** a contributor tries to add a new Dúchas.ie feature
- **THEN** the contributor MUST edit the canonical file at
  `sruth/oideachais/dlt_sources/ie/culture/duchas.py`, NOT the
  meaisínfhoghlaim duplicate
- **AND** the meaisínfhoghlaim duplicate MUST be deleted (zero
  importers; the canonical home is the single source of truth)

#### Scenario: A meaisínfhoghlaim `language/gaeilge/` file has stale `sruth.oideachais.dlt_sources.celtic` import

- **GIVEN** a file under `sruth/meaisinfhoghlaim/language/gaeilge/`
  contains `from sruth.oideachais.dlt_sources.celtic.X import Y`
  in either an active or lazy (`try/except ImportError`) import
  block
- **AND** `sruth/oideachais/dlt_sources/celtic/` does not exist
  (it was deleted in Phase 3B)
- **WHEN** the file is loaded
- **THEN** the import fails silently (lazy) or with
  `ModuleNotFoundError` (active)
- **AND** the file MUST be either deleted (if a true duplicate of
  a canonical home) or have its stale imports rewired to the
  canonical path (if it provides genuinely new functionality)

### Requirement: `language/gaeilge/` contains only non-duplicate files

The directory `sruth/meaisinfhoghlaim/language/gaeilge/` MUST
contain only the files listed in the post-Phase-2 Scenario
below.

No additional files MAY be added without first verifying they
are NOT byte-for-byte duplicates of canonical homes at
`sruth/oideachais/dlt_sources/ie/{culture,education}/`.

- `__init__.py` (the package marker)
- Files that are NOT byte-for-byte duplicates of canonical
  homes (e.g., richer implementations where the canonical
  version is a strict subset)
- `*.yaml` data files (not Python)

#### Scenario: A future contributor adds a new DLT source to `language/gaeilge/`

- **GIVEN** the post-Phase 2 `language/gaeilge/` contains 4 files:
  `__init__.py`, `canuint.py`, `duchas_images.py`, `irish_samples.yaml`
- **WHEN** a new `@dlt.source` is needed for an Irish-language
  data source
- **THEN** the contributor MUST first verify whether a canonical
  home exists at `sruth/oideachais/dlt_sources/ie/culture/<name>.py`
  via `ls sruth/oideachais/dlt_sources/ie/culture/`
- **AND** if a canonical home exists, the contributor MUST add
  the new source to the canonical home (NOT the meaisínfhoghlaim
  copy) per the no-duplicates invariant
- **AND** if no canonical home exists, the contributor MUST
  create one at `sruth/oideachais/dlt_sources/ie/culture/<name>.py`
  with the standard country-first layout, then optionally add
  a thin re-export shim to `sruth/meaisinfhoghlaim/language/gaeilge/`
  if a meaisínfhoghlaim-specific consumer needs it
