# cianfhoghlaim-cocoindex-v1-migration Specification

## Purpose

`cianfhoghlaim-cocoindex-v1-migration` is a capability of the Cianfhoghlaim
platform. It defines the canonical pattern for **v1 CocoIndex Apps** in
the consolidated `cianfhoghlaim/` package: every CocoIndex flow is
exposed as a v1 `coco.App` instance with a `@coco.fn` `app_main`
function, a stable identity, v1 R1-R4 rule conformance, and the
`lancedb.mount_table_target` target pattern. Post-v4, the Apps live at
`cianfhoghlaim/cocoindex/<app>.py`. There are 15 Apps in current use
(13 from the BIEP v1 + UoG deep-extraction timeline, plus the 2 from
`apple-photos-ingestion`).
## Requirements
### Requirement: V1 CocoIndex Apps

The system SHALL provide **13 v1 CocoIndex Apps** in
`cianfhoghlaim/core/cocoindex/` (was 11 before this change; the
new `UniversityCoursesApp` + `UniversityModulesApp` per the
`cianfhoghlaim-university-deep-extraction` spec bring the total to 13).

The 13 Apps are:

1. `leabharlann_books_embedding` → `leabharlann_books` (BGE-large)
2. `leabharlann_zotero_embedding` → `leabharlann_zotero` (BGE-large)
3. `leabharlann_takeout_embedding` → `leabharlann_takeout` (BGE-large)
4. `codebase_indexing` → `codebase_chunks` (BGE-m3 + 7-node/7-edge code graph)
5. `api_indexing` → `api_endpoints` (BGE-m3 + 4-framework HTTP route surface)
6. `filesystem_indexing` → `filesystem_layout` (BGE-m3 + depth 1-4 dirs)
7. `storage_indexing` → `storage_backends` (BGE-m3 + 9 backend kinds)
8. `config_indexing` → `config_files` (BGE-m3 + 12 config kinds)
9. `unified_embedding` → `unified_embeddings` (BGE-m3 + DuckDB source)
10. `code_embeddings` → `code_embeddings` (BGE-m3 + LocalFile source)
11. `docs_skills_consolidation` → `docs_skills` (BGE-m3 + BAML extraction)
12. `UniversityCoursesApp` → `university_courses` (BGE-m3, 1024-dim on `course_description + learning_outcomes`) — **NEW**
13. `UniversityModulesApp` → `university_modules` (BGE-m3, 1024-dim on `module_title + module_description + learning_outcomes`) — **NEW**

All 13 Apps SHALL use the canonical v1 pattern
(`@coco.lifespan` + `@coco.fn` + `lancedb.mount_table_target` +
`SentenceTransformerEmbedder`), respect the 100-batch minimum +
`HNSW-DROP-THRESHOLD=50` rule, and pass `cocoindex_v1_conformance`.

#### Scenario: Semantic search over UoG modules

- **GIVEN** the `UniversityModulesApp` has materialised
- **WHEN** a developer runs `await search_university_modules("transformer attention mechanism", limit=5)`
- **THEN** the App returns the top-5 rows from the `university_modules` table ranked by BGE-M3 cosine similarity
- **AND** each row carries `module_code`, `module_title`, `school_slug`, `programme_codes`, `ects`, `source_url`

#### Scenario: Semantic search over UoG courses

- **GIVEN** the `UniversityCoursesApp` has materialised
- **WHEN** a developer runs `await search_university_courses("applied statistics with R", limit=5)`
- **THEN** the App returns the top-5 rows from the `university_courses` table ranked by BGE-M3 cosine similarity
- **AND** each row carries `course_code`, `course_title`, `nfq_level`, `school`, `ects`, `source_url`

#### Scenario: A 14th v1 App is added without breaking the conformance contract

- **WHEN** a future v1 App is registered
- **THEN** `cianfhoghlaim.cocoindex_flows.cocoindex_v1_conformance` SHALL pass (per the `cianfhoghlaim-cocoindex-v1-migration` spec)
- **AND** the total v1 App count SHALL go from 13 to 14
- **AND** the new App SHALL respect the 4-rule conformance contract (R1-R4)
- **AND** the new App SHALL be added to the `APP_REGISTRY` at `cianfhoghlaim.core.cocoindex`

#### Scenario: CocoIndex v1 conformance linter passes

- **WHEN** `mise run lint:v1-conformance` is run
- **THEN** the linter SHALL report `13/13 apps passed` (was 11/11 before this change)
- **AND** the linter SHALL report `0 conformance errors`
- **AND** the linter SHALL report `0 R1-R4 violations`

### Requirement: V0 Archive

The system SHALL keep actual Python import examples in the `cianfhoghlaim-cocoindex-v1-migration` spec aligned with the v4 `cianfhoghlaim` package root. When the spec shows a code import for an archived or migrated CocoIndex flow, it SHALL use `from cianfhoghlaim...` rather than `from cianfhoghlaim...`.

The V0 archive SHALL remain read-only and SHALL preserve retired flow files under the archive path. Consumers SHALL import active v1 Apps from their v4 `cianfhoghlaim` package paths.

#### Scenario: Active research embedding import uses cianfhoghlaim

- **GIVEN** a migrated research embedding flow has an active v4 home
- **WHEN** the spec shows the import replacement for the archived flow
- **THEN** it uses `from cianfhoghlaim.cocoindex_flows.research_embedding import ...`
- **AND** it does not use `from cianfhoghlaim.cocoindex_flows.research_embedding import ...`

#### Scenario: V0 archive remains non-authoritative

- **GIVEN** a file remains under the V0 archive path
- **WHEN** a contributor needs an active v1 App
- **THEN** the contributor SHALL use the v4 active app path under `cianfhoghlaim/cocoindex/`
- **AND** the archive SHALL NOT be treated as the runtime import surface

### Requirement: CocoIndex v1 App canonical pattern

Every CocoIndex flow under `cianfhoghlaim/cocoindex/*.py` SHALL conform to the v1 4-rule contract:

- **R1 — `coco_lifespan` mandate**: each flow uses the shared lifespan from `_lifespan.py` for the embedder + vector store + chunker (no per-flow ad-hoc clients). A flow may declare additional ContextKeys, but only with a sibling `# R2-exempt: <reason>` comment documenting the reason.
- **R2 — canonical `coco.App`**: each flow declares `coco.App(...)` (either at module scope, or via the `@coco.App(shared_lifespan)` decorator pattern from early v1.0.x — both pass the R2 regex).
- **R3 — `mount_table_target` for vector sinks**: vector-store flows use `lancedb.mount_table_target(LANCE_DB, ...)` (not yield-dict loops, not the legacy `lancedb.TableTarget(db=..., embedding=...)` direct construction).
- **R4 — `declare_vector_index`**: the embedding column is indexed via `target_table.declare_vector_index(column="embedding")`. Flows that do NOT write to a LanceDB table with an `embedding` column (e.g. GeoParquet-only outputs like `apple_photos_geospatial.py`) SHALL add a sibling `# R4-exempt: <reason>` comment line.

The system SHALL provide a **`cocoindex_v1_migrate.py`** tool at `cianfhoghlaim/dlt/common/cocoindex_v1_migrate.py` that audits every flow file for the 4 rules and reports violations (idempotent per-flow; non-destructive by default; supports `# R4-exempt` markers).

#### Scenario: All 47 flows pass the 4-rule audit

- **WHEN** the user runs `uv run python cianfhoghlaim/dlt/common/cocoindex_v1_migrate.py --check-only`
- **THEN** the tool prints a per-flow table with pass / fail for each of R1, R2, R3, R4
- **AND** exits 0 if no violations; exits 1 with a remediation hint otherwise

#### Scenario: Remediate R4 violation

- **WHEN** `agent_registry.py` declares a LanceDB target table but is missing `declare_vector_index`
- **THEN** the migration tool reports `R4 FAIL: missing declare_vector_index(column="embedding")`
- **AND** the fix is to add `target_table.declare_vector_index(column="embedding")` immediately after the `lancedb.mount_table_target(LANCE_DB, ...)` call

#### Scenario: R4-exempt marker for non-LanceDB flows

- **WHEN** `apple_photos_geospatial.py` (a GeoParquet-only output) is audited
- **THEN** the migration tool detects the `# R4-exempt: <reason>` marker on a standalone line
- **AND** reports R4 as PASS, citing the exemption reason in the audit log

#### Scenario: CI check

- **WHEN** CI runs the conformance audit (`mise run cocoindex:conformance`) on every push
- **THEN** the build fails if any new flow violates R1, R2, R3, or R4
- **AND** a PR-comment is posted listing the violation table + the failing flow names

### Requirement: 22 priority flows migrated to v1

The system SHALL prioritise 22 flows for v1 conformance. The list includes the 6 LC subjects (mathematics, chemistry, geography, gaeilge, english, computer_science), government_circulars_embedding, 6 leabharlann flows, 3 official-media flows, apple_photos metadata chunks geospatial, agent_registry, codebase_indexing, upstream_api_surface, upstream_blog_monitor, cross_subject_competency_embedding, and ocr_aware_flow.

#### Scenario: Priority migration list is exhaustive

- **WHEN** the user runs `uv run python cianfhoghlaim/dlt/common/cocoindex_v1_migrate.py --priority-list`
- **THEN** the tool prints the 22 flow names sorted alphabetically
- **AND** flows that don't exist as standalone files are flagged with the comment `# may not exist as standalone`

### Requirement: Conformance helper lifecycle

The `cocoindex_v1_migrate.py` tool MUST be CI-friendly (exits 0/1 with no exception leakage), and MUST support `--check-only`, `--apply`, `--priority-list`, and `--help` modes.

#### Scenario: CI exit code contract

- **WHEN** the conformance audit runs in CI with zero violations
- **THEN** it exits 0
- **AND** prints a one-line summary: `cocoindex_v1_conformance: N/N flows pass`

### Requirement: 22-priority flow migration batch completed

Every flow in the 22-flow priority list SHALL satisfy the 4-rule R1+R2+R3+R4 conformance contract, or carry a documented `# R4-exempt: <reason>` marker if it does not write to a LanceDB table with an `embedding` column.

The 14 flows that exist as standalone files (the other 4 of the 22 listed flows live as inner apps inside `leabharlann_embedding.py` and `unified_embedding.py` and are migrated as part of those files) SHALL be the first batch migrated to v1 conformance via the `2026-07-09-cocoindex-v1-remaining-apps-v1` change.

#### Scenario: All 14 existing priority flows pass

- **WHEN** `uv run python cianfhoghlaim/dlt/common/cocoindex_v1_migrate.py --check-only` is run after the migration batch
- **THEN** every flow in the 22-priority list (excluding the 4 non-existent ones) reports `PASS`
- **AND** the audit summary reports `>= 14/14 priority flows pass` (out of the 47 total flows)

#### Scenario: Non-LanceDB flow carries the R4-exempt marker

- **WHEN** `apple_photos_geospatial.py` is audited (a GeoParquet-only flow with no `embedding` column)
- **THEN** it reports R4 PASS via the `# R4-exempt: GeoParquet output, no embedding column` marker
- **AND** the exemption reason is documented in the file's module docstring

### Requirement: v1 conformance check as CI gate

The system SHALL wire the conformance audit as a hard-failure CI gate via the `mise run cocoindex:conformance` task + a new `.github/workflows/cocoindex-conformance.yaml` workflow.

The CI gate SHALL:
- Run on every PR + every push to `main` and `pick-4-biep-v1`
- Invoke `mise run cocoindex:conformance` (which runs `cocoindex_v1_migrate.py --check-only`)
- Exit non-zero on any R1/R2/R3/R4 violation
- Post a PR-comment via `peter-evans/create-or-update-comment` on failure (with the violation table + the failing flow list)
- Upload the per-flow audit report as a build artifact
- The existing `cic:cocoindex:conformance` task (which calls the CocoIndex v1 App) is NOT a replacement for this CI gate; it is the deep materialisation path.

#### Scenario: New R4 violation fails the build

- **WHEN** a contributor adds a new flow under `cianfhoghlaim/cocoindex/` that is missing `declare_vector_index(column="embedding")`
- **THEN** `mise run cocoindex:conformance` exits 1
- **AND** the PR-comment lists the failing flow name + the specific R4 violation
- **AND** the build artifact `cocoindex-v1-conformance-report.txt` is uploaded

#### Scenario: Marker exemption is respected by the CI gate

- **WHEN** a contributor adds a new GeoParquet-only flow with a `# R4-exempt: GeoParquet output` marker
- **THEN** `mise run cocoindex:conformance` exits 0 (the marker is respected)
- **AND** the PR-comment shows the new flow as R4 PASS via the exemption

### Requirement: CocoIndex v1.x pin and `deps=` memoization discipline

The system SHALL pin CocoIndex to **`>=1.0.20,<2.0.0`** (current
stable as of 2026-08-11 per `https://github.com/cocoindex-io/cocoindex/releases`).

The previous pin (`>=1.0.14,<1.0.8,!=1.0.8`) was set when v1.0.14
was the latest; v1.0.15-v1.0.20 have shipped since (BigQuery/Snowflake/
Valkey target connectors, LiveMap, rate limiting, batched target
writes, zvec FTS fields, preserve target invalidation in v1.0.20).

Additionally, every `@coco.fn(memo=True)` decorator SHALL declare
its module-level prompt strings + model names via the `deps=`
parameter (introduced in v1.0.x per
`cocoindex-io/cocoindex#1836`).

#### Scenario: A `@coco.fn(memo=True)` site has a module-level prompt constant

- **GIVEN** `cocoindex_flows/european_nations_cross/education_embedding.py:30`
  declares `IRISH_LC_PROMPT_V1 = "..."` and uses it at line 87 inside
  `@coco.fn(memo=True)`
- **WHEN** `IRISH_LC_PROMPT_V1` changes
- **THEN** CocoIndex MUST invalidate the dependent memos (because
  `deps=(IRISH_LC_PROMPT_V1,)` is declared on the `@coco.fn` decorator)
- **AND** the next pipeline run MUST re-execute the function

#### Scenario: A `@coco.fn` site has no module-level deps

- **GIVEN** a `@coco.fn(memo=True)` that uses inline string literals
  only (no module-level constants)
- **WHEN** the function body changes
- **THEN** CocoIndex MUST invalidate the dependent memos (the
  source-code change is the only invalidation signal)

#### Scenario: A `@coco.fn` site uses `deps=` for prompt strings

- **GIVEN** a `@coco.fn(memo=True, deps=(BGE_M3_MODEL,))` declaration
  where `BGE_M3_MODEL` is a module-level constant
- **WHEN** `BGE_M3_MODEL` changes from `"BAAI/bge-m3"` to
  `"BAAI/bge-large-en-v1.5"`
- **THEN** CocoIndex MUST invalidate the dependent memos
- **AND** the marimo audit notebook MUST show the new model ID in
  the per-call provenance

#### Scenario: Pin upgrade from v1.0.14 to v1.0.20

- **WHEN** `mise.toml` (via the `bun run cocoindex update --pip` task)
  refreshes the CocoIndex venv
- **THEN** all 196 CocoIndex files in `cocoindex/**/*.py` MUST
  AST-parse cleanly under v1.0.20
- **AND** the canonical `cocoindex_flows/european_nations/_factory.py`
  factory pattern MUST continue to work (tested by
  `mise run cic:cocoindex:v1-conformance`)
- **AND** no breaking change introduced by v1.0.15-v1.0.20 affects
  our factory pattern (the v1.0 changelog confirms new
  connectors/features are purely additive)

## Merged from

- `cocoindex-v1-migration` (the original v1 CocoIndex migration spec was merged into this spec on 2026-07-06)
