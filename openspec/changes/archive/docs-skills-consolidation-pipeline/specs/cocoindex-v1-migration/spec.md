## ADDED Requirements

### Requirement: Tagged-Consolidation Index
The system SHALL extract a `(category, quadrant, confidence)` tag and a list of `(subject, predicate, object)` triples for every file in `docs/` and `.agents/skills/`, persist them in the `docs_skills_graph` FalkorDB graph, and embed the file content in the `docs_skills_chunks` LanceDB table.

#### Scenario: BAML tag extraction
- **GIVEN** a Markdown file under `docs/02-data-platform/`
- **WHEN** the `docs_skills_consolidation` CocoIndex v1 App runs
- **THEN** it SHALL call the BAML `ExtractDocSkillTag` function on the file content
- **AND** declare a `DocSkill` node in FalkorDB with the returned `(category, quadrant, confidence)`
- **AND** memoisation SHALL skip re-extraction for unchanged files

#### Scenario: Triple extraction
- **GIVEN** a Markdown file with ≥ 1 factual relationship
- **WHEN** the App runs in catch-up mode
- **THEN** it SHALL call the BAML `ExtractTriples` function
- **AND** carry the resulting triples forward to the graph-build pass as a `DocTriples` record
- **AND** the per-file mount SHALL be `memo=True` so unchanged files are skipped

#### Scenario: Consolidation group proposal
- **GIVEN** two files with `cosine_similarity(embedding_a, embedding_b) ≥ 0.92`
- **WHEN** the Phase 2 graph-build pass runs
- **THEN** it SHALL call the BAML `ProposeConsolidation` function
- **AND** declare a `ConsolidationGroup` node plus a `CONSOLIDATED_INTO` edge from each member to the canonical

#### Scenario: Failure isolation
- **GIVEN** a file that fails BAML extraction
- **WHEN** the App processes the file
- **THEN** the file SHALL be logged with a `WARNING` and skipped
- **AND** downstream graph nodes SHALL still declare successfully for the remaining files
- **AND** the asset check `docs_skills_graph_publish` SHALL report the failure count

### Requirement: Live Documentation Source
The system SHALL keep `docs/` and `.agents/skills/` indexed in near real-time via CocoIndex v1 live mode.

#### Scenario: Live file-watch
- **GIVEN** a file edit in `docs/02-data-platform/`
- **WHEN** the App runs with `live=True`
- **THEN** CocoIndex SHALL re-run the `process_file` component for that file within 30 seconds (`refresh_interval=30s`)
- **AND** the FalkorDB and LanceDB target states SHALL reconcile atomically

#### Scenario: Multi-source merge
- **GIVEN** two source roots (`docs/` and `.agents/skills/`)
- **WHEN** the App mounts both via `localfs.walk_dir`
- **THEN** both filesystems SHALL contribute to the same `docs_skills_chunks` LanceDB table and the same `docs_skills_graph` FalkorDB graph
- **AND** duplicates across the two sources SHALL be deduped by file `sha256` (primary key)

## MODIFIED Requirements

### Requirement: CocoIndex v1 App per Flow
The system SHALL expose every CocoIndex flow as a v1 `coco.App` instance with a `@coco.fn` `app_main` function and stable identity.

#### Scenario: App registration
- **GIVEN** an `sruth/oideachais/cocoindex_flows/<flow>.py` module
- **WHEN** the module is loaded
- **THEN** it SHALL declare `app = coco.App(coco.AppConfig(name="<UniqueName>"), app_main, ...)` at module level
- **AND** the `app_main` function SHALL be decorated with `@coco.fn`
- **AND** the app SHALL be invokable from the CLI as `cocoindex update <flow>:<app_name>`

#### Scenario: Live mode support
- **GIVEN** an `app_main` function
- **WHEN** the user runs `cocoindex update -L <flow>:<app_name>`
- **THEN** the app SHALL support `live=True` on its source
- **AND** the file-watcher SHALL be polled for changes by the local-filesystem source

#### Scenario: New DocsSkillsConsolidation app
- **GIVEN** the `sruth/oideachais/cocoindex_flows/docs_skills_consolidation.py` module
- **WHEN** the module is loaded
- **THEN** it SHALL declare `app = coco.App(coco.AppConfig(name="DocsSkillsConsolidation"), app_main)`
- **AND** the `app_main` SHALL mount both `docs/` and `.agents/skills/` via `localfs.walk_dir` with `live=True`
- **AND** the app SHALL be re-exported from `sruth/oideachais/cocoindex_flows/__init__.py` as `docs_skills_app`

#### Scenario: New CodebaseIndex app
- **GIVEN** the `sruth/oideachais/cocoindex_flows/codebase_indexing.py` module
- **WHEN** the module is loaded
- **THEN** it SHALL declare `app = coco.App(coco.AppConfig(name="CodebaseIndex"), app_main)`
- **AND** the `app_main` SHALL mount `localfs.walk_dir(repo_root, live=True, refresh_interval=60s)` with include patterns `*.py,*.rs,*.ts,*.tsx,*.go,*.md,*.mdx,*.toml`
- **AND** the app SHALL write to a `codebase_chunks` LanceDB table
- **AND** the app SHALL be re-exported from `sruth/oideachais/cocoindex_flows/__init__.py` as `codebase_app`
