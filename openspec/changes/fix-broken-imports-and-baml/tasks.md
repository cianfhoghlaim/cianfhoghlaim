# Tasks: fix-broken-imports-and-baml

## Phase 1: Fix edcolearning.py import (unblocks edcolearning asset)

- [ ] Read `oideachais/dlt_sources/common/_http_factories.py` to confirm the canonical `HttpClientFactory` class exists
- [ ] In `oideachais/dlt_sources/ireland/edcolearning.py:32`:
  - Replace `from oideachais.http_utils import HttpClientFactory`
  - With `from oideachais.dlt_sources.common._http_factories import HttpClientFactory`
- [ ] Verify: `uv run --package oideachais python -c "from oideachais.dlt_sources.ireland.edcolearning import edcolearning_source; print('OK')"` succeeds

## Phase 2: Fix 4 BAML `client litellm` references

- [ ] In `baml_src/leaving_cert_marking_scheme_extraction.baml:40`:
  - Change `client "litellm"` to `client LitellmClient`
- [ ] In `baml_src/leaving_cert_past_paper_extraction.baml:31`:
  - Change `client "litellm"` to `client LitellmClient`
- [ ] In `baml_src/leaving_cert_syllabus_extraction.baml:29`:
  - Change `client "litellm"` to `client LitellmClient`
- [ ] In `baml_src/curriculum_extraction.baml:25`:
  - Change `client "litellm"` to `client LitellmClient`
- [ ] Verify: `grep -rn 'client "litellm"' oideachais/baml_src/` returns 0 hits

## Phase 3: Add ClassifyOfficialMedia to site_analysis.baml

- [ ] Read `oideachais/dlt_sources/official_media/classifier.py` to understand the call signature
- [ ] In `baml_src/site_analysis.baml`:
  - Add `function ClassifyOfficialMedia(ig_username: string, ig_bio: string, ig_external_url: string) -> OfficialMediaClassification` (matching the 3 args from `classifier.py:62`)
  - Add `class OfficialMediaClassification { is_official_media bool reason string @description("Explanation") }` (or similar)
  - Add `client LitellmClient`
  - Add a prompt that classifies based on the 3 inputs

## Phase 4: Add canonical Extractor client to clients.baml

- [ ] In `baml_src/clients.baml`:
  - Add `client<llm> Extractor { provider "openai" options { model "gpt-4o-mini" temperature 0.1 } }`
- [ ] In `baml_src/ocr_validation.baml:412`:
  - Delete the duplicate `client<llm> Extractor { ... }` declaration (now canonical in clients.baml)
- [ ] Verify: `grep -rn "^client<llm> Extractor" oideachais/baml_src/` returns 1 hit (only in clients.baml)

## Phase 5: Migrate 3 `from oideachais.core import X` to dlt_utils

- [ ] In `oideachais/dlt_utils/batching.py:34`:
  - Migrate the `HNSW_DROP_THRESHOLD = 50` constant from the shim to `dlt_utils/batching.py` directly
  - Update the import line (or remove it if the constant is now local)
- [ ] In `oideachais/dlt_utils/safety.py:20`:
  - Migrate the `get_executor(name="duckdb") -> ThreadPoolExecutor(max_workers=1)` function from the shim to `dlt_utils/safety.py` directly
  - Update the import line (or remove it if the function is now local)
- [ ] Keep `oideachais/oideachais/core/__init__.py` shim intact (backward-compat re-export for one release)
- [ ] Verify: `uv run --package oideachais python -c "from oideachais.dlt_utils.batching import HNSW_DROP_THRESHOLD; print(HNSW_DROP_THRESHOLD)"` returns 50
- [ ] Verify: `uv run --package oideachais python -c "from oideachais.dlt_utils.safety import get_executor; print(get_executor())"` works

## Phase 6: Validation

- [ ] `from oideachais.dlt_sources.ireland.edcolearning import edcolearning_source` succeeds
- [ ] `grep -rn 'client "litellm"' oideachais/baml_src/` returns 0 hits
- [ ] `uv run --package oideachais python -c "import dagster_defs.definitions"` still loads
- [ ] `openspec validate fix-broken-imports-and-baml --strict` passes

## Phase 7: Land the plane

- [ ] Stage the changes
- [ ] Commit: `git commit -m "fix-broken-imports-and-baml: unblock edcolearning + leaving_cert + official_media"`
- [ ] `git pull --rebase`
- [ ] `git push origin q3-2026-oideachais-consolidation`
