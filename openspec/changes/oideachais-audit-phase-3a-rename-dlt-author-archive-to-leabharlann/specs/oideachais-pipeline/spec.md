# Spec Delta: oideachais-pipeline

## ADDED Requirements

### Requirement: Leabharlann DLT Source Package Naming
The personal-archive DLT source package SHALL be located at `sruth/oideachais/dlt_sources/leabharlann/`.

The package directory SHALL be named `leabharlann` (Irish for "library") to match:
- the source callable names inside the package (`leabharlann_books`, `leabharlann_zotero`, `leabharlann_takeout`),
- the `oideachais-leabharlann` skill documentation, and
- the Irish-first naming convention used across the data platform.

The previous `dlt_sources/author_archive/` directory SHALL NOT exist after this change is applied.

#### Scenario: dlt_sources/leabharlann package exists
- **WHEN** a developer lists the contents of `sruth/oideachais/dlt_sources/`
- **THEN** a `leabharlann/` directory SHALL be present
- **AND** the directory SHALL contain `__init__.py`, `leabharlann_books.py`, `zotero.py`, `takeout_v1.py`, `google_takeout.py`, `gemini_deep_research.py`, `university_of_galway.py`, `previews.py`, `_citation_extractor.py`, `_epub_extractor.py`, `_scanner.py`, `_takeout_paths.py`, and `config.example.yaml`
- **AND** no `author_archive/` directory SHALL be present

#### Scenario: leabharlann sources importable from canonical path
- **WHEN** Python code executes `from dlt_sources.leabharlann import leabharlann_books_source, zotero_source, takeout_v1_source`
- **THEN** the import SHALL succeed without raising `ModuleNotFoundError`
- **AND** the callable names SHALL match the `name=` argument on each `@dlt.source` decorator

#### Scenario: no stale references to author_archive import path
- **WHEN** a developer runs `grep -rn "dlt_sources\.author_archive" --include="*.py" sruth/`
- **THEN** zero matches SHALL be returned
- **AND** the legacy `dlt_sources.author_archive` import path SHALL be fully retired
