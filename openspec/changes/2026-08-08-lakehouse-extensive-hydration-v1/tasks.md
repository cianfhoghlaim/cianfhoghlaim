# Tasks — Lakehouse extensive hydration

## Phase A — Code-only bug fixes — DONE

- [x] A1 `deployment-choice.yaml`: add `llama_swap: true` to
  `enabled_stacks:`.
- [x] A2 `orchestration/resources.py`: `DuckLakeResource.get_client()`
  imported a nonexistent top-level `storage.ducklake_client` module —
  rewrote to wrap the canonical `dlt_sources.common.
  destinations_cianfhoghlaim` module (`.get_dlt_destination()`) plus a
  real raw-duckdb `.get_client()` using the same env-var precedence
  fixed in A4/B.
- [x] A3 `generic_filesystem_assets.py`'s `filesystem_documents_ingested`
  asset used `destination="duckdb"` (ephemeral local file), never
  reaching DuckLake/Garage — now uses `get_dlt_destination(use_ducklake=
  None)`. Replaced the bare `except Exception: pass` with a logged
  traceback + `failed_sources` metadata.
- [x] A4 3 scripts (`verify_ducklake_population.py`,
  `8_jurisdiction_overview.py`, `export_cohorts_to_lance.py`) had an
  identical hardcoded plaintext Postgres password — confirmed it's the
  real, currently-active `.env.dev` dev password, not a dummy. Replaced
  with the established `POSTGRES_PASSWORD` (Infisical-first/`.env.dev`-
  fallback) convention, with a `DUCKLAKE_POSTGRES_PASSWORD` override.
  **Rotating the leaked value out-of-band remains a manual follow-up —
  not done here, cannot be done blindly.**
- [x] A5 `orchestration/sensors/garage_pdf_arrival_sensor.py` declared
  `job_name="garage_pdf_arrival_job"` with no matching job anywhere —
  defined it (`define_asset_job` wrapping `filesystem_documents_ingested`).
  Noted 8 sibling sensors have the identical dangling-job pattern, out
  of scope here.
- [x] A6 `pdf_factory.py`'s `CONVERTER_REGISTRY` pointed at a nonexistent
  `oideachais.document_factory.converters.*` package (every converter
  silently failed to load) — fixed to the real `meaisinfhoghlaim.
  document_factory.converters.*`.
- [x] A7 7 notebooks had hard `SyntaxError`s (stray column-0 `import
  ibis` inside function bodies) — fixed.
- [x] A8 Re-indenting A7 surfaced 3 further real cross-cell `NameError`
  bugs (`ibis` imported in one cell, used in another, never round-
  tripped through the cell's `return`/parameter list) in
  `02_syllabus_visualizer`, `06_exam_papers_explorer`,
  `09_pipeline_e2e_test` — fixed all three. Also fixed a real
  `ibis.ibis.duckdb.connect()` double-prefix typo in
  `08_leabharlann_full_stack_demo`.
- [x] A9 `02_lakehouse_inspector` needed `import ibis` added (missing
  entirely) plus 4 occurrences of a wrong `infrastructure/stacks/
  lakehouse/` path fixed to the real `bonneagar/stacks/lakehouse/`.
  Verified `03_dlt_pipeline_overview` / `04_cocoindex_embedding_coverage`
  do NOT actually need an `ibis` import — their only "ibis." grep hits
  were docstring prose, not real code (both are static/mocked demo
  notebooks with no live connection calls).
- [x] A10 Installed `dlt`, `structlog`, `dagster`, `pillow`, `httpx`,
  `pymupdf`, `pypdf`, `pandas`, `baml-py==0.223.0` (pinned to match the
  repo's BAML generator config version) into this worktree's `.venv` —
  all real declared dependencies (except `pypdf`/`pandas`, used
  pervasively but not declared in `pyproject.toml` — noted, not chased
  further, out of scope).

**Verify:** all 17 notebooks `ast.parse` clean; `ruff check` introduces
no new issues on any touched file; `grep -rn "805c7a45"` → 0 hits.

## Phase B — Consolidate the DuckLake client — DONE

- [x] B1 Confirmed `dlt_sources/common/destinations_cianfhoghlaim.py`
  canonical (dlt's native `DuckLakeCredentials`, not hand-rolled
  `ATTACH` SQL). `orchestration/storage/ducklake_client.py`'s docstring
  rewritten from "the canonical client" to a clear deprecation note;
  confirmed (grep, root package only) nothing imports its
  `DuckLakeClient` class anymore. `sruth/oideachais/storage/*` and
  `sruth/crypteolas/storage/*` variants left untouched — separate
  `pyproject.toml` workspaces, not reachable from `orchestration/`
  regardless; flagged as separate follow-up, not silently left
  inconsistent.
- [x] B2 Documented the `ducklake` (DuckLake Parquet tables) vs.
  `garage/oideachais` (raw PDF blobs) bucket split as intentional, not
  leftover inconsistency.
- [x] B3 **Live-verified** (see Phase D): `get_dlt_destination(
  use_ducklake=True)` real ATTACH + dlt pipeline write round-trip
  against the actual `lakehouse-garage`/`lakehouse-postgres` containers
  succeeded — corrected the bucket-name default from the
  never-actually-verified `ducklake-cianfhoghlaim` to the live-verified
  real value `ducklake` (a real `ATTACH` with the wrong DATA_PATH fails
  outright with "does not match existing data path in the catalog").

**Verify:** `get_dlt_destination(use_ducklake=False)` and
`use_ducklake=True` both import/construct cleanly with zero live
services (construction, not connection). Full round-trip verified live
in Phase D.

## Phase C — Real image-based OCR/VLM wiring — DONE

- [x] C1 `sruth/shared/extraction/docling_resource.py`'s `ocr_page_vlm`/
  `pdf_to_images` pattern reused conceptually, not imported directly
  (separate workspace with an unrelated FastAPI/PyJWT eager-import
  chain in its `__init__.py`).
- [x] C2 `ExtractSyllabusDiagram` gained `image: image[]?`
  (backwards-compatible), prompt updated to reference it via Jinja.
- [x] C3 New `meaisinfhoghlaim/document_factory/pdf_to_image_bridge.py`
  — pymupdf-based page render → `baml_py.Image` / data URI. Fixed a
  real, previously-undiscovered `PydanticUserError` in
  `curriculum_document.py` (missing `ClassVar` annotation) that was
  blocking `import meaisinfhoghlaim.document_factory` entirely, found
  while wiring this module through that package's `__init__.py`.
- [x] C4 `fibo_configs_from_syllabus_diagrams` updated to render up to 8
  real page images and pass them alongside `pdf_text`. **Live-verified**
  against the real chemistry syllabus PDF: 8/46 pages rendered, real
  image content embedded in the BAML request, request reached the real
  (then-unreachable) litellm endpoint before failing gracefully —
  confirms correct wiring up to the network boundary.
- [x] C5 Fixed `ensembled_extractor.py`'s `_call_qwen3_vl`/`_call_gemma4`
  — both used to send a text string containing a local filesystem path
  as "content"; both now render page 1 and send a real payload
  (OpenAI-compatible `image_url` block for qwen3-vl's `/v1/chat/
  completions`; llama.cpp's own `image_data` array for gemma4's raw
  `/completion` route — **flagged as unverified against a live
  instance**, no live gemma4/llama-swap endpoint reachable here). Also
  fixed a separate, previously-undiscovered bug in the same file: `json`
  was used (`json.dumps(data)`) but never imported anywhere — every
  path's success case would have raised `NameError`.
- [x] C6 `_run_path_baml`'s `NotImplementedError` left in place —
  explicitly out of scope this pass.
- [x] C7 Un-stubbed exactly 1 of the 24 factory-generated stub assets in
  `lc5_assets.py` (`lc5_chemistry_diagrams_extracted`), wired with a
  real `deps=["lc5_chemistry_ingested"]`, reusing `quest_pack_assets.py`'s
  `_classify_pdfs`/`_extract_pdf_text` (same directory/layer, via
  `importlib.import_module` since `"2_materials"` isn't a valid static
  import path). **Live-verified**: 8 real page images embedded, request
  reached the real `BIEPV3Vision` endpoint. Also fixed this file's
  `BAML_AVAILABLE` import to fall back to `baml_client.baml_client.
  sync_client` (matching sibling files in the same directory) — without
  it, `BAML_AVAILABLE` was always `False` here and all 24 assets were
  permanently stubbed regardless of whether `baml_client` actually
  works. The other 23 stub assets are left as explicitly-scoped future
  work, not silently claimed done.

**Verify:** `.venv/bin/baml-cli generate` succeeds after the schema
change; both `fibo_configs_from_syllabus_diagrams` and
`lc5_chemistry_diagrams_extracted` live-verified to render real images
and construct correct multimodal requests.

## Phase D — Bring up live infra and run the real hydration pass

- [x] D1 `docker ps` showed `lakehouse-garage` and `lakehouse-postgres`
  already up and healthy in this environment (contrary to the plan's
  initial assumption of "down") — no compose-up needed for those two.
- [x] D2a `llama-swap` has no container at all (never brought up) and
  the required GGUF model weights (`stedding/huggingface/gguf/`) do not
  exist locally — bringing it up would start an empty container with no
  models to serve. **Confirmed blocked on missing multi-GB model
  weights, a genuine environment limitation, not a code bug.**
- [x] D2b `litellm` was running but crash-looping — `docker logs litellm`
  showed a real config bug: `router_settings.fallbacks` was a bare list
  of model-name strings, which litellm's `Router.validate_fallbacks()`
  rejects ("Item 'qwen3-vl-8b' is not a dictionary"). Fixed at the
  source (`scripts/generate_litellm_config.py`) and in the checked-in
  `bonneagar/stacks/litellm/config/config.yaml`. **The actually-running
  container is deployed from a separate Komodo-managed copy at
  `~/.komodo-stacks/litellm/config/config.yaml`, outside this
  worktree** — the harness correctly blocked editing it directly from
  this isolated-worktree session. Flagged, not silently worked around:
  the user needs to redeploy/resync that Komodo stack to pick up the
  fix. Confirmed the deployed copy has the identical bug.
- [x] D3 Live-verified `get_dlt_destination(use_ducklake=True)` end to
  end: a real `dlt.pipeline(...).run(...)` against the actual
  `lakehouse-garage`/`lakehouse-postgres` containers completed with
  "Load package ... is LOADED and contains no failed jobs". Also
  live-verified a direct raw-`duckdb` `ATTACH` (matching
  `DuckLakeResource.get_client()`'s new implementation) against the
  real catalog, confirming an existing real table
  (`education.subjects`) with real BIEP registry data.
- [ ] D4 OCR/VLM end-to-end round-trip (real network call succeeding, not
  just reaching the endpoint) — **blocked**: litellm's live Komodo
  deployment needs a manual redeploy (D2b) and llama-swap needs real
  GGUF weights (D2a), neither achievable from this session. The code
  path itself is verified correct up to the network boundary (Phase C).
- [x] D5 **The hydration pass**: new `scripts/hydrate_lc_full_corpus.py`
  (modeled on `scripts/load_lc_chemistry_pilot.py`, extended from 1
  subject to all 13 via the already-present but previously-unused
  `LC_ALL_SUBJECTS` constant). Metadata-only dry run (`--skip-extraction`)
  live-verified: 139 real document rows across 13 subjects loaded into
  `cianfhoghlaim.leaving_cert.corpus_documents` in the real DuckLake
  catalog. Full run (real MiniMax-primary/Qwen-secondary cross-check
  extraction per subject's syllabus) — see the live run's final summary
  captured directly in this session for actual row counts/status per
  subject.
- [x] D6 England: no local PDF corpus confirmed to exist — explicitly out
  of scope this pass, not attempted, not fabricated.

**Verify:** direct DuckDB/DuckLake queries against the hydrated
`corpus_documents` (139 rows / 13 subjects) and `syllabus_cross_check`
tables, matching this session's own live run output.

## Phase E — Restore the notebook investigation surface

- [ ] E1 Locate each notebook's fabricated-fallback pattern (hash-based
  fake row counts) and replace with a visible warning callout.
- [ ] E2 Point notebooks at `connect_local_lakehouse()` first (now real),
  falling back to `connect_md()` only if local genuinely fails.
- [ ] E3 Run all 17 notebooks headless against the hydrated lakehouse.

## Verification (whole change)

- [x] `openspec validate 2026-08-08-lakehouse-extensive-hydration-v1
  --strict`
- [x] All 17 notebooks parse (`ast.parse`); 0 SyntaxErrors (was 7)
- [x] `grep -rn "805c7a45"` (leaked password fragment) → 0 hits repo-wide
- [x] `lakehouse-garage` + `lakehouse-postgres` confirmed healthy; real
  dlt pipeline write round-trip succeeded
- [ ] `litellm` healthy — blocked on a manual Komodo redeploy outside
  this worktree (fix applied at the repo source; not yet live)
- [ ] `llama-swap` healthy — blocked on missing local GGUF model weights
- [x] A direct DuckDB/DuckLake query against the hydrated lakehouse
  returns a real row count matching the local corpus (139 documents /
  13 subjects, metadata-only pass; full extraction pass results per
  this session's live run)
- [x] At least one `ExtractSyllabusDiagram`/ensemble-extractor call
  verified to construct a real image-bearing request (both live-verified
  up to the network boundary; full round-trip blocked per D4)
- [x] `.venv/bin/baml-cli generate` succeeds after the schema change
- [x] England hydration explicitly documented as skipped (no local
  corpus), not silently omitted
