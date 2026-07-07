## ADDED Requirements

### Requirement: Consolidated cianfhoghlaim package manifest

The system SHALL expose a single `pyproject.toml` at `cianfhoghlaim/pyproject.toml` declaring the wheel packages, runtime dependencies, optional-dependency groups, and CLI entry-points for the consolidated `cianfhoghlaim` Python package.

The wheel package list SHALL contain exactly the 18 directories that have an `__init__.py` on disk: `agents`, `assets`, `baml`, `browser`, `cocoindex`, `cognify`, `dagster`, `dlt`, `embeddings`, `geospatial`, `leabharlann`, `meaisinfhoghlaim`, `notebooks`, `observability`, `ocr`, `pipelines`, `sources`, `storage`, plus the nested `libraries/codeolas` sub-package.

The system SHALL NOT have any `_quadrant_pyproject.toml` file at the `cianfhoghlaim/` package root. The legacy `_oideachais_pyproject.toml`, `_meaisinfhoghlaim_pyproject.toml`, `_tuatha_pyproject.toml` files SHALL be removed.

#### Scenario: All declared wheel packages resolve to directories with `__init__.py`

- **WHEN** `uv sync && uv run python -c "import cianfhoghlaim.agents, cianfhoghlaim.baml, cianfhoghlaim.cocoindex, cianfhoghlaim.dagster, cianfhoghlaim.dlt, cianfhoghlaim.meaisinfhoghlaim, cianfhoghlaim.observability, cianfhoghlaim.ocr, cianfhoghlaim.notebooks, cianfhoghlaim.geospatial, cianfhoghlaim.storage, cianfhoghlaim.leabharlann"` runs
- **THEN** no `ModuleNotFoundError` is raised
- **AND** all 12 declared wheel packages import cleanly

#### Scenario: All `[project.scripts]` entry-points resolve to real modules

- **WHEN** `uv run cianfhoghlaim --help`, `uv run cianfhoghlaim-ocr --help`, `uv run cianfhoghlaim-baml --help`, `uv run cianfhoghlaim-marimo --help`, `uv run cianfhoghlaim-stack-doctor --help`, `uv run cianfhoghlaim-dagster --help`, `uv run cianfhoghlaim-dlt --help`, `uv run cianfhoghlaim-cocoindex --help` run
- **THEN** each command's `--help` is printed without `ModuleNotFoundError`

#### Scenario: No stale `_quadrant_pyproject.toml` files exist

- **WHEN** `ls cianfhoghlaim/_*.toml` runs
- **THEN** no files are listed

## MODIFIED Requirements

### Requirement: All Python imports inside cianfhoghlaim use the canonical namespace

The system SHALL have zero `from sruth.*` or `from oideachais.*` imports inside `cianfhoghlaim/`, except inside `.archive/` directories (point-in-time snapshots that are not part of the build) or inside `compat.py` build-time helpers.

The legacy `sruth.oideachais.*`, `sruth.meaisinfhoghlaim.*`, `sruth.tuatha.*`, `sruth.shared.*`, `sruth.browser`, and bare `oideachais.*` Python namespaces SHALL NOT be importable at runtime from the consolidated `cianfhoghlaim` package.

#### Scenario: Grep finds zero stale imports in active code

- **WHEN** `grep -rE "from sruth\.|from oideachais\." cianfhoghlaim/ --include='*.py' --exclude-dir=.archive --exclude=compat.py` runs
- **THEN** zero matches are returned

#### Scenario: All Dagster assets resolve

- **WHEN** `mise run dagster:dev` launches and the asset graph is materialised
- **THEN** all 199 assets load successfully (no `ModuleNotFoundError` from `sruth.*` or `oideachais.*` imports inside asset modules)

#### Scenario: All 14 v1 CocoIndex Apps pass the conformance contract

- **WHEN** `mise run upstream:conformance` runs
- **THEN** all 14 v1 CocoIndex Apps (leabharlann_books_embedding, leabharlann_zotero_embedding, leabharlann_takeout_embedding, codebase_indexing, api_indexing, filesystem_indexing, storage_indexing, config_indexing, unified_embedding, code_embeddings, docs_skills_consolidation, culture_heritage_embedding, upstream_blog_monitor, upstream_api_surface) pass the 4-rule conformance contract R1-R4
- **AND** `cocoindex_v1_conformance` reports 14/14 PASS

## REMOVED Requirements

### Requirement: Standalone sruth-browser import alias at `cianfhoghlaim/browser/`

**Reason**: The standalone browser package was renamed from `infrastructure/stacks/browser/` to `bonneagar/stacks/browser/` during the v4 follow-on (`openspec/changes/archive/2026-06-29-2026-06-29-per-domain-web-app-consolidation/`). The local duplicate at `cianfhoghlaim/browser/` is a stale deprecation stub whose `__init__.py` imports from `cianfhoghlaim.core.browser` — a package that was never created.

**Migration**: All Dagster assets, DLT sources, scripts, and notebooks that previously imported `from cianfhoghlaim.core.browser import BrowserClient` (or similar) MUST update to `from bonneagar.stacks.browser.sruth_browser import BrowserClient` (or via the workspace source alias).