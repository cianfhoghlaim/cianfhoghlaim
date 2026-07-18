# Tasks for 2026-08-10-biep-v3-preflight-bug-fixes-v1

## 1. YAML flight config fix
- [ ] Open `motherduck/flights/config.yaml:113-129`
- [ ] Re-indent 4 BIEP v3 entries by 2 spaces so they sit under `flights:`
- [ ] Validate: `python -c "import yaml; yaml.safe_load(open('motherduck/flights/config.yaml'))"` succeeds
- [ ] Validate: `dg list jobs | grep -E "ireland_full_coverage_flight|england_full_coverage_flight|sct_wls_ni_flight|crown_dependencies_flight"` shows 4

## 2. Strong client model fix
- [ ] Open `baml_src/clients_biep_v3.py:13`
- [ ] Replace `BIEPV3ExtractStrong = "qwen3-vl-8b-it"` with `BIEPV3ExtractStrong = "gemma-3-27b-it"`
- [ ] Update the docstring at line 15 to drop the "Vision-Language" wording
- [ ] Run `baml-cli generate` (must succeed)

## 3. MotherDuck snapshots httpx implementation
- [ ] Add `httpx>=0.27,<1.0` + `tenacity>=8.2,<9.0` to `pyproject.toml` dependencies
- [ ] Run `uv sync` to install
- [ ] Open `dlt/common/motherduck_snapshots.py`
- [ ] Add `import httpx` + `from tenacity import retry, stop_after_attempt, wait_exponential`
- [ ] Define `MOTHERDUCK_API_URL = os.getenv("MOTHERDUCK_API_URL", "https://api.motherduck.com")`
- [ ] Implement `snapshot_database()` with httpx POST + tenacity retry
- [ ] Implement `create_share()` with httpx POST + tenacity retry
- [ ] Implement `attach_share()` with httpx POST + tenacity retry
- [ ] Keep `compute_size_env()` as-is (env-var reader, no HTTP)
- [ ] Add module docstring documenting `MOTHERDUCK_API_URL` env var

## 4. Registry docstring fix + 3,780-row assertion
- [ ] Open `dlt/british_isles/_cross/registry_loader.py:674-679`
- [ ] Replace docstring text "1,560 rows" → "3,780 rows" with the new per-jurisdiction breakdown
- [ ] Add `assert actual == 3_780` after the `counts` dict is populated at end of `seed_registry()`

## 5. JurisdictionPipelineBase inheritance refactor
- [ ] Open `dlt/british_isles/_cross/jurisdiction_pipeline_base.py`
- [ ] Add `subject_to_row()` method (~30 LOC of shared logic)
- [ ] Add `build_pipeline()` method (~6 LOC of shared factory)
- [ ] Refactor `dlt/british_isles/ireland/education/ireland_jurisdiction_pipeline.py` to define `class IrelandJurisdictionPipeline(JurisdictionPipelineBase)` and instantiate it
- [ ] Refactor `dlt/british_isles/england/education/england_jurisdiction_pipeline.py` similarly
- [ ] Refactor `dlt/british_isles/sct_wls_ni/education/sct_wls_ni_jurisdiction_pipeline.py` similarly
- [ ] Refactor `dlt/british_isles/crown_dependencies/education/crown_dependencies_jurisdiction_pipeline.py` similarly
- [ ] Verify `dg list assets | grep jurisdiction_pipeline` still shows the same 4 pipelines

## Final gate
- [ ] `openspec validate 2026-08-10-biep-v3-preflight-bug-fixes-v1 --strict` passes
- [ ] `mise run lint:skills` passes (53/53)
- [ ] `mise run turbo dev` boots without errors
- [ ] All 5 fixes implemented + tested
- [ ] Commit + push to `origin/openspec/2026-07-25-refactor-batch-v1`
- [ ] Archive after push: `openspec archive 2026-08-10-biep-v3-preflight-bug-fixes-v1 --yes`