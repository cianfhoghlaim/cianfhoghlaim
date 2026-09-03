## MODIFIED Requirements

### Requirement: 8-step tutorial presence

The system SHALL provide exactly 8 marimo notebooks at `notebooks/{01..08}_*.py`, one per numbered tutorial step.

#### Scenario: All 8 notebooks present

- **WHEN** the user runs `ls notebooks/{01..08}_*.py`
- **THEN** exactly 8 files exist
- **AND** `marimo edit 01_overview_setup.py` renders without error

### Requirement: Legacy preservation

The system SHALL preserve the existing 50+ stage-specific notebooks under `notebooks/legacy/` (unmodified) so the existing per-subject / per-corpus analyses remain reachable.

#### Scenario: Legacy discovery

- **WHEN** the user runs `uv run cianfhoghlaim-marimo list legacy`
- **THEN** the CLI returns ≥50 notebook names (the pre-restructure count)

### Requirement: Reactive cell chaining

The system SHALL use marimo's reactive cell execution so that editing a cell in step N re-runs all dependent cells in steps N+1...8.

#### Scenario: Edit step 3 propagates forward

- **WHEN** the user edits step 3 (`03_extract_baml.py`) to change the input PDF
- **THEN** step 4 (`04_embed_cocoindex.py`) and step 5 (`05_query_ibis_duckdb.py`) re-run automatically when re-opened

### Requirement: CLI dual-mode

The system SHALL support the dual-mode (`edit` / `run` / `dashboard`) CLI for both the 8 tutorial notebooks and the legacy/ subtree via `uv run cianfhoghlaim-marimo <verb> <name>`.

#### Scenario: CLI discovers both layers

- **WHEN** the user runs `uv run cianfhoghlaim-marimo list`
- **THEN** the output lists the 8 tutorial steps first (sorted by step), then the legacy/ subtree (sorted by name)

### Requirement: Reference fastmcp_servers notebook

The system SHALL provide a `notebooks/reference/fastmcp_servers.py` marimo notebook that exercises BOTH the `dlt-workspace` MCP server (from the `dlthub-platform-integration` spec) and the `mcp-server-motherduck` MCP server, side-by-side, so the agent stack is visible at a glance.

#### Scenario: Both MCP servers discoverable

- **WHEN** the user runs `marimo run notebooks/reference/fastmcp_servers.py`
- **THEN** the notebook reports 8 dlt-workspace tools + ≥3 MotherDuck tools available

### Requirement: Companion documentation

The system SHALL provide a `docs/agents/five-tangent-modernization.md` companion doc with the 5 tangents at a glance (1-paragraph summary per tangent + a "what to read next" cross-link to the relevant spec).

#### Scenario: Doc discoverable

- **WHEN** the user runs `ccc search "five-tangent-modernization"` or `openspec list --specs | grep llm-zoomcamp`
- **THEN** the companion doc + the canonical spec both appear

### Requirement: Workshop vendoring

The system SHALL vendor the `DataTalksClub/llm-zoomcamp/cohorts/2026/workshops/dlt` workshop at `dlthub-ai-workbench/external/llm-zoomcamp-dlt-workshop/` as a read-only reference (MIT-licensed, sparse-checkout, regenerable). The vendored workshop is NOT imported — it's documentation only.

#### Scenario: Reference workshop present

- **WHEN** the user runs `ls dlthub-ai-workbench/external/llm-zoomcamp-dlt-workshop/`
- **THEN** the dlt workshop files exist (e.g. `01-overview.ipynb`, `02-dlt-resources.ipynb`)

### Requirement: 5-notebook BAML+CocoIndex tutorial track

The system SHALL provide 5 marimo tutorial notebooks at `notebooks/13_baml_cocoindex_tutorial/` (a new directory following the existing 01-12 numbering scheme) covering the full BAML 0.223.0 + CocoIndex v1 + vision-model stack. The 5 notebooks SHALL be:

1. `01_baml_post_v4_syntax.py` — canonical post-v4 BAML 0.223.0 syntax (`generator` block + `field Type` whitespace + `enum` / `class` / `function` + `@description` + `image` + `@stream.*` + `?` optionality)
2. `02_qpack_8_subject_walkthrough.py` — the 8 `qpack_<subject>.baml` files, demonstrating the `paragraph → LO[] → FormativeItem → Score → Validate` pattern across all 8 LC subjects (40+ BAML calls)
3. `03_education_pdf_vision_pipeline.py` — the vision+PDF extraction pipeline (`ExtractCurriculumSyllabus` → `ExtractExamPaperLayout` → `ExtractSyllabusDiagram` → `ExtractMarkingSchemeGuideline`) with a **side-by-side** `gemma-4-26B-A4B` vs `qwen3-vl-8b` comparison cell on the same PDFs
4. `04_cocoindex_baml_integration.py` — the 3 real CocoIndex+BAML integration patterns (`upstream_api_surface`, `upstream_blog_monitor`, `docs_skills_consolidation`) including the lazy-import pattern, the `coco.use_context(BAML_CLIENT_*)` provider, and the fallback-stub for when BAML isn't generated
5. `05_post_v4_duplicate_audit_and_migration.py` — the interactive (marimo-reactive) audit of the duplicates from the 42-renames commit (`49e0259a0`), with each duplicate row becoming a cell block + the user picking which one to keep + a `baml-rename-XX.patch` diff emission + the residual `baml-cli generate --mode check` 50-error report

#### Scenario: 5 tutorial files present and CLI-discoverable

- **GIVEN** the 5 follow-up tutorials exist at `notebooks/13_baml_cocoindex_tutorial/{01..05}_*.py`
- **WHEN** the user runs `uv run cianfhoghlaim-marimo list 13_baml_cocoindex_tutorial`
- **THEN** the CLI returns exactly 5 entries
- **AND** `uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/01_baml_post_v4_syntax` opens marimo edit without error
- **AND** all 5 files AST-parse under `python -c "import ast; ast.parse(open(f).read())"`

#### Scenario: side-by-side vision model comparison in tutorial 3

- **GIVEN** the `03_education_pdf_vision_pipeline.py` tutorial renders
- **WHEN** the user clicks the side-by-side cell
- **THEN** the cell calls `baml_sync.ExtractSyllabusDiagram(pdf=..., pointing_model="gemma-4-26B-A4B")` AND `baml_sync.ExtractSyllabusDiagram(pdf=..., pointing_model="qwen3-vl-8b")` on the same PDF
- **AND** the cell emits a marimo `mo.ui.table` showing both outputs side-by-side
- **AND** the cell notes the practical difference between the two local vision models (gemma-4-26B-A4B favours structure, qwen3-vl-8b favours OCR fidelity)

### Requirement: `01_overview_setup.py` Step 0.5 pointer

The system SHALL append a "Step 0.5: the BAML+CocoIndex tutorial track" Markdown cell to `notebooks/01_overview_setup.py`'s table of contents between Step 0 (env setup) and Step 1 (vision models). The pointer SHALL link to the 5 tutorial notebooks in `notebooks/13_baml_cocoindex_tutorial/` and SHALL list their purpose in 1-line summaries.

#### Scenario: Step 0.5 pointer cell renders in marimo

- **WHEN** the user runs `marimo edit notebooks/01_overview_setup.py`
- **THEN** the notebook renders with a "Step 0.5: the BAML+CocoIndex tutorial track" Markdown cell
- **AND** the cell lists all 5 tutorial notebooks with their 1-line summaries
- **AND** the cell does not depend on any of the 5 tutorial notebooks existing (it links to the dir by reference)