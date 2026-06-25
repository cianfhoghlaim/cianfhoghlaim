# Lateralise British Isles Domains — Tasks

## Phase 1a — Toolchain bump (Python 3.13 + latest pins)

- [ ] Update `mise.toml` to `python = "3.13"`.
- [ ] Update `sruth/oideachais/pyproject.toml` `requires-python = ">=3.13"` + bump pinned runtime/dev deps to latest stable.
- [ ] Update `sruth/croilar/pyproject.toml` and `sruth/tuatha/pyproject.toml` the same way.
- [ ] `uv lock --upgrade` in each project; commit regenerated `uv.lock`.
- [ ] Update `sruth/oideachais/Dockerfile.dagster` to `python:3.13-slim`.
- [ ] Update `infrastructure/stacks/engineering/sruth/oideachais/Dockerfile.dagster` to `python:3.13-slim`.
- [ ] `bun install` and commit refreshed `bun.lock`.
- [ ] Smoke‑test: re‑run the existing `sruth/oideachais/test_crawl*.py` scripts under the new toolchain with `USE_LOCAL_SCRAPES=true`.
- [ ] Smoke‑test: re‑run `dagster dev -m oideachais.dagster_defs.definitions` and verify the UI loads.

## Phase 1b — Pytest suite (16 tests)

- [ ] Create `sruth/oideachais/tests/` package + `conftest.py` (temp DuckLake fixture, `USE_LOCAL_SCRAPES=true`, autouse).
- [ ] `sruth/oideachais/tests/dlt_sources/ie/education/test_curriculum_source_local_cache.py`
- [ ] `sruth/oideachais/tests/dlt_sources/ni/education/test_ccea_source.py`
- [ ] `sruth/oideachais/tests/dlt_sources/en/education/test_national_curriculum.py`
- [ ] `sruth/oideachais/tests/dlt_sources/common/test_firecrawl_source_router.py`
- [ ] `sruth/oideachais/tests/dlt_utils/test_destinations.py`
- [ ] `sruth/oideachais/tests/dagster_defs/test_partitions_v2.py`
- [ ] `sruth/oideachais/tests/dagster_defs/assets/ie/education/test_curriculum_dlt_assets.py`
- [ ] `sruth/oideachais/tests/dagster_defs/assets/ie/education/leaving_cert/test_lc_dlt_assets.py`
- [ ] `sruth/oideachais/tests/dagster_defs/test_definitions_loads.py`
- [ ] `sruth/oideachais/tests/dagster_defs/sensors/test_curriculum_freshness_sensors.py`
- [ ] `sruth/oideachais/tests/dagster_defs/asset_checks/test_duchas_pages.py`
- [ ] `sruth/oideachais/tests/sources/test_sources_yaml_schema.py`
- [ ] `sruth/tuatha/tests/test_definitions_loads.py`
- [ ] `sruth/croilar/tests/dlt_assets/test_spotify_soundcloud_labels.py`
- [ ] `tests/sources/test_cross_namespace.py`
- [ ] Add `[tool.pytest.ini_options]` to `sruth/oideachais/pyproject.toml` (collect from `sruth/oideachais/tests/`, `sruth/tuatha/tests/`, `sruth/croilar/tests/`, `tests/sources/`).
- [ ] Wire `bun run test` (or `mise run test`) to invoke `uv run pytest …` across all four trees.
- [ ] `openspec validate lateralise-british-isles-domains --strict` green.

## Phase 2 — `sources.yaml` + `SourceFactory` stub

- [ ] Create `sruth/oideachais/sources.yaml` from the contract in the proposal §"What"(1).
- [ ] Create `sruth/oideachais/dlt_utils/source_factory.py` with `SourceFactory.from_yaml`, pydantic `SourceSpec` model, and the 7‑method contract stub.
- [ ] Extend `sruth/oideachais/tests/sources/test_sources_yaml_schema.py` to also assert the factory validates & rejects bad entries.
- [ ] Add `sruth/oideachais/sources/sources_validation.py` (CLI: `python -m oideachais.sources.sources_validation`) that prints a coverage report (which DLT sources are referenced in YAML but missing a source file, which existing source files are not in YAML).

## Phase 3 — Re‑organisation

- [ ] Create `sruth/oideachais/dlt_sources/domains/education/{ie,ni,en,sct,wls,iom,jey,ggy}/` packages.
- [ ] Move (or import‑shim) the existing `sruth/oideachais/dlt_sources/ireland/*` → `domains/education/ie/*`.
- [ ] Move (or import‑shim) `sruth/oideachais/dlt_sources/uk/{england,scotland,wales,northern_ireland}/*` → `domains/education/{en,sct,wls,ni}/*`.
- [ ] Move (or import‑shim) `sruth/oideachais/dlt_sources/crown_dependencies/*` → `domains/education/{iom,jey,ggy}/*`.
- [ ] Keep `sruth/oideachais/dlt_sources/ireland`, `…/uk`, `…/crown_dependencies` as 1‑line re‑export shims (so legacy `from oideachais.dlt_sources.ireland.curriculum_source import …` still works).
- [ ] Move the existing asset files in `sruth/oideachais/dagster_defs/assets/ireland/*` → `…/assets/ie/education/*`; same for `leaving_cert/`.
- [ ] Move the existing asset files in `…/assets/uk_education_assets.py` (and any `uk/` subdir) → `…/assets/{ni,en,sct,wls,iom,jey,ggy}/education/*`.
- [ ] Rename every `@asset(key=[…])` from the old key to the new `["{nation}", "{domain}", …]` key.
- [ ] In `sruth/oideachais/dagster_defs/definitions.py`, add a one‑shot alias table `BACKWARDS_COMPAT_ASSET_ALIASES: dict[AssetKey, AssetKey]` that maps old keys to new keys; wire it into the combined `assets=` list.
- [ ] Update `sruth/oideachais/api/ducklake_reader.py` to `attach('oideachais')` once, then `select … from oideachais.education.ie.leaving_cert where subject = ?`.
- [ ] All 16 pytests still green.

## Phase 4a — Ireland medicine

- [ ] `sruth/oideachais/dlt_sources/domains/medicine/ie/hse.py` (firecrawl_pages)
- [ ] `sruth/oideachais/dlt_sources/domains/medicine/ie/medical_council.py` (api_table, public search)
- [ ] `sruth/oideachais/dlt_sources/domains/medicine/ie/doh.py` (firecrawl_pages)
- [ ] `sruth/oideachais/dlt_sources/domains/medicine/ie/hpsc.py` (api_table)
- [ ] Add new entries to `sruth/oideachais/sources.yaml`.
- [ ] Add new asset files in `sruth/oideachais/dagster_defs/assets/ie/medicine/*`.
- [ ] Add pytests for each.

## Phase 4b — Ireland law (statutory only)

- [ ] `sruth/oideachais/dlt_sources/domains/law/ie/irish_statute_book.py` (api_xml, incremental on `act_id`, `data_writer.file_max_items=1000`).
- [ ] `sruth/oideachais/dlt_sources/domains/law/ie/doj.py` (firecrawl_pages).
- [ ] `sruth/oideachais/dlt_sources/domains/law/ie/lawreform.py` (firecrawl_pages).
- [ ] Add new entries to `sruth/oideachais/sources.yaml`.
- [ ] Add new asset files in `sruth/oideachais/dagster_defs/assets/ie/law/*`.
- [ ] Add pytests for each.

## Phase 5 — Lateralise NI/EN/SCT/WLS + crown deps

- [ ] `domains/medicine/{ni,en,sct,wls}/*` (one source file per public‑endpoint entity in the proposal).
- [ ] `domains/law/{ni,en,sct,wls}/*` (statutory only).
- [ ] `domains/education/{ni,en,sct,wls,iom,jey,ggy}/*` — promote the existing `uk/*` + `crown_dependencies/*` into domain‑first packages.
- [ ] Asset files: `sruth/oideachais/dagster_defs/assets/{ni,en,sct,wls,iom,jey,ggy}/{education,medicine,law}/*`.
- [ ] Per‑nation pytests.
- [ ] `sruth/oideachais/sources.yaml` coverage check passes for all 8 nations × 4 domains.

## Phase 6 — `site_analysis/` + dashboards

- [ ] `sruth/oideachais/baml_src/site_analysis.baml` (SiteAnalysis, SoftwareFingerprint, LayoutFingerprint, PageDescription).
- [ ] Regenerate `baml_client/`.
- [ ] `sruth/oideachais/site_analysis/__init__.py`, `extractor.py` (calls firecrawl_mcp + browserbase_mcp via `mcp` library or subprocess JSON‑RPC), `schema.py` (Pydantic mirror), `screenshot.py` (uploads to Garage S3).
- [ ] `sruth/oideachais/dlt_sources/domains/site_analysis/__init__.py` (DLT source over the extractor output).
- [ ] `sruth/oideachais/dagster_defs/assets/site_analysis/extract.py` (Dagster asset).
- [ ] `sruth/oideachais/dagster_defs/assets/site_analysis/embed.py` (LanceDB embed via CocoIndex).
- [ ] `sruth/oideachais/dagster_defs/assets/site_analysis/cognify.py` (Cognee cognify into `oideachais_site_analysis` dataset).
- [ ] `sruth/oideachais/cocoindex_flows/site_analysis_embedding.py`.
- [ ] `sruth/oideachais/cognee_integration/site_analysis_cognify.py`.
- [ ] `sruth/oideachais/notebooks/dashboards/education/all_nations.py` (marimo).
- [ ] `sruth/oideachais/notebooks/dashboards/medicine/registers.py` (marimo).
- [ ] `sruth/oideachais/notebooks/dashboards/law/statute_book.py` (marimo).
- [ ] Dagster `marimo_render` asset (uses `marimo export html-wasm`).
- [ ] Add `firecrawl` and `browserbase` MCP servers to `sruth/oideachais/dlt_utils/source_factory.py` to call them at materialisation time (test mode: stubbed).

## Phase 7 — Archive

- [ ] `openspec validate lateralise-british-isles-domains --strict` green.
- [ ] Add `domain-source-registry` and `site-analysis-mcp` capabilities to `openspec/project.md`.
- [ ] `openspec archive lateralise-british-isles-domains --yes`.

