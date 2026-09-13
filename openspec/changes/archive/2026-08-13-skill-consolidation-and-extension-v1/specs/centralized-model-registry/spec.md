# centralized-model-registry — Change 1 Delta (2026-08-13)

## ADDED Requirements

### Requirement: ocr_vision family SHALL be exposed with full pipeline documentation in centralized-registry §11

The `centralized-registry` skill MUST add a `## 11. OCR/VLM
Pipeline` section (after the existing `## 10. The 6
follow-up issues`) that documents the full OCR/VLM surface
for the Cianfhoghlaim platform — at minimum:

1. The 22-entry `VISION_MODELS` subset view of the
   `ocr_vision` family in `MODEL_REGISTRY`, with per-entry
   `key` / `role` / `upstream_id` / `backend`
2. The 6 `CLASSICAL_OCR` backends in
   `meaisinfhoghlaim/models/registry.py:CLASSICAL_OCR`
   (Pylaia + TrOCR + PaddleOCR + Tesseract + dots.ocr + VLM)
3. The BIEP v2 4-path ensemble (`EnsembledExtractor` —
   `baml + unstract + qwen3_vl + gemma4`) at
   `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py`,
   including the RAGAS voting pattern and the
   `OCR_WEBHOOK_URL` emission pattern
4. The 7 PDF converters in
   `meaisinfhoghlaim/document_factory/` (`docling`,
   `marker`, `unstructured`, `deepseekocr`, `pymupdf4llm`,
   `curriculum_document`, `pdf_factory`)
5. The 4 alignment methods in
   `meaisinfhoghlaim/alignment/aligner.py` (`VecAlign`,
   `HunAlign`, `GaoisAlign`, `Hybrid`) plus the
   `ColPaliAligner` for manuscript bbox extraction
6. The Irish HTR dataset
   (`meaisinfhoghlaim/datasets/irish_htr_dataset.py`)
7. The M4-Max dispatch helper
   (`select_optimal_for_m4_max()`)
8. The llama-swap GGUF inference path
   (`meaisinfhoghlaim/models/llama_swap_config.yaml`)
9. The BAML `baml_src/clients_ocr_ensemble.baml` patterns
10. The `meaisinfhoghlaim/ocr/` back-compat shim (with
    `DeprecationWarning` documentation — canonical is
    `meaisinfhoghlaim.models`)

The §11 entry MUST be the first CCC result for any agent
query containing "OCR", "VLM", "vision model", or
"document extraction".

#### Scenario: Agent discovers OCR/VLM surface via §11

- **GIVEN** an agent is asked to add or modify an OCR model
  in the Cianfhoghlaim platform
- **WHEN** the agent runs
  `bun run ccc:search "OCR VLM pipeline"` or
  `bun run ccc:search "vision model selection"`
- **THEN** the first CCC result MUST be the
  `centralized-registry` §11 entry
- **AND** §11 MUST include the 22-entry `VISION_MODELS`
  table with `key` / `role` / `upstream_id` / `backend`
  columns
- **AND** §11 MUST include a code sample for the 4-path
  ensemble `EnsembledExtractor` invocation
- **AND** §11 MUST cross-reference
  `meaisinfhoghlaim/README.md` for the deeper sub-package
  docs
- **AND** §11 MUST document the `meaisinfhoghlaim/ocr/`
  back-compat shim `DeprecationWarning` and point at
  `meaisinfhoghlaim.models` as canonical

#### Scenario: Agent uses §11 to pick an OCR model for a new jurisdiction

- **GIVEN** an agent is adding a new BIEP v3 jurisdiction
  pipeline and needs to pick an OCR model
- **WHEN** the agent reads §11 to choose a model
- **THEN** §11 MUST group the 22 `VISION_MODELS` entries
  by role (`default` / `irish` / `bilingual` /
  `scanned_manuscript` / `diagram` / `dense_ocr`)
- **AND** §11 MUST show the M4-Max dispatch helper code
  with a sample invocation returning the recommended
  model for the M4-Max 64GB workload
- **AND** §11 MUST reference
  `meaisinfhoghlaim/models/llama_swap_config.yaml` for
  the local inference configuration
- **AND** §11 MUST reference
  `baml_src/clients_ocr_ensemble.baml` for the
  ensemble client pattern

### Requirement: dlt_sources/DATA_PLATFORM_ROUTER.md SHALL exist as the single router for the 5 per-area AGENTS.md files

A `DATA_PLATFORM_ROUTER.md` file at `dlt_sources/` MUST
serve as the single router for the Cianfhoghlaim data
platform surface. It MUST link to each of the 5 canonical
per-area docs (`dlt_sources/AGENTS.md`, `baml_src/AGENTS.md`,
`cocoindex/AGENTS.md`, `orchestration/AGENTS.md`,
`meaisinfhoghlaim/README.md`) and document the 6 critical
conventions:

1. Always use relative imports within sub-packages
2. Respect the ingestion cache (`USE_LOCAL_SCRAPES=true`)
3. Zero absolute namespaces in data pipelines
4. R1-R4 CocoIndex conformance
5. MODEL_REGISTRY-only (no hardcoded model strings)
6. Factory pattern for N nearly-identical Apps

The router MUST be co-located with the per-area `AGENTS.md`
files (at `dlt_sources/DATA_PLATFORM_ROUTER.md`), NOT in
`.agents/skills/`, so it does not inflate the top-level
skill count.

Each of the 5 per-area docs MUST contain a cross-link back
to `DATA_PLATFORM_ROUTER.md` (verified via
`grep -l "DATA_PLATFORM_ROUTER" <5 files>` returning 5
matches).

#### Scenario: New agent discovers the data platform surface via the router

- **GIVEN** a new agent is asked to add a DLT source for a
  new British Isles education jurisdiction
- **WHEN** the agent searches for "data platform" or
  reads `dlt_sources/AGENTS.md`
- **THEN** the agent finds a link to
  `DATA_PLATFORM_ROUTER.md`
- **AND** the router points at the 5 per-area docs and the
  6 critical conventions
- **AND** the router includes a "I want to add X, where do
  I go?" routing table that the agent can use to find the
  correct sub-package for the task

#### Scenario: Per-area docs cross-link the router

- **GIVEN** the `DATA_PLATFORM_ROUTER.md` file exists at
  `dlt_sources/DATA_PLATFORM_ROUTER.md`
- **WHEN** an operator runs
  `grep -l "DATA_PLATFORM_ROUTER" dlt_sources/AGENTS.md baml_src/AGENTS.md cocoindex/AGENTS.md orchestration/AGENTS.md meaisinfhoghlaim/README.md`
- **THEN** the command returns 5 matches (one per per-area
  doc)
- **AND** each per-area doc has a
  `## Data platform router` section with a 1-line link to
  the router file

### Requirement: INDEXING_AND_COGNITION.md §10 SHALL resolve the ccc CLI vs codebase_indexing v1 App split

The `.agents/skills/INDEXING_AND_COGNITION.md` skill MUST
add a `## 10. Code-search canonical entrypoint` section
(after the existing `## 9. The cianfhoghlaim v4
consolidation`) that provides a single decision matrix
resolving the dual CLI vs v1 App vs graph companion split.

The matrix MUST list at least these 3 surfaces:

1. **CLI** — `bun run ccc:search "<query>"`
   (kept for developer shortcuts; the `ccc` skill carries
   the DEPRECATION NOTICE banner)
2. **Python v1 App** —
   `from cocoindex.codebase_indexing import code_search`
   (the canonical replacement for `ccc search`)
3. **Graph companion** —
   `search_code_graph(file_path=..., node_type=...)`
   (the 7-node / 7-edge code graph; 7 node types: File,
   Function, Class, Method, Module, Interface, Variable;
   7 edge types: CONTAINS, IMPORTS, CALLS, EXTENDS,
   IMPLEMENTS, USES, DEFINES)

Plus the 4 infrastructure companions:
`search_api_endpoints`, `search_filesystem`,
`search_storage`, `search_config`.

#### Scenario: Agent picks the right code-search surface for the task

- **GIVEN** an agent needs to find a specific function in
  the codebase
- **WHEN** the agent reads `INDEXING_AND_COGNITION.md §10`
- **THEN** the matrix MUST recommend the v1 App
  (`code_search(...)`) for pipelines and ad-hoc Python
  use, the CLI (`ccc search`) for one-off terminal
  searches, and the graph companion
  (`search_code_graph(...)`) for code-structure queries
  (e.g. "what calls function X?")
- **AND** the matrix MUST cross-reference
  `cocoindex/AGENTS.md` for the v1 App canonical pattern
- **AND** the matrix MUST cross-reference
  `.agents/skills/ccc/SKILL.md` for the CLI surface
  (with the DEPRECATION NOTICE context)