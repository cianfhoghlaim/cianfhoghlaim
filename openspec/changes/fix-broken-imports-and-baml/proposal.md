# fix-broken-imports-and-baml — Unblock production pipelines

## Why

The oideachais quadrant has 6 categories of broken wiring that block
or partially break the production pipeline. Each is verified by
direct file inspection:

### 1. `edcolearning.py:32` — `HttpClientFactory` import is dead
The file imports `from oideachais.http_utils import HttpClientFactory`,
but `oideachais.http_utils` was removed in commit `8484a6353`. The
canonical client factory lives at
`oideachais/dlt_sources/common/_http_factories.py:HttpClientFactory`.
The `ireland/__init__.py` import chain is wrapped in `try/except`, so
the package-level import of `ireland.edcolearning` fails silently
(see Dagster `ireland_edcolearning_import_skipped` warning at
`definitions.py:184`). The `edcolearning_audio_extraction` asset
(group `unified_audio`) cannot materialise.

### 2. Four BAML files reference `client litellm` (lowercase, undefined)
The canonical clients in `baml_src/clients.baml` are:
- `LitellmClient` (line 17)
- `DeepSeekClient` (line 26)
- `MiniMaxClient` (line 35)
- `LitellmLongContext` (line 44)

**No `litellm` (lowercase) client exists.** Four BAML files reference
`client litellm` and will fail `baml-cli generate`:

| File | Line | Function affected |
|---|--:|---|
| `baml_src/leaving_cert_marking_scheme_extraction.baml` | 40 | `ExtractMarkingScheme` |
| `baml_src/leaving_cert_past_paper_extraction.baml` | 31 | `ExtractPastPaper` |
| `baml_src/leaving_cert_syllabus_extraction.baml` | 29 | `ExtractLeavingCertSyllabus` |
| `baml_src/curriculum_extraction.baml` | 25 | `ExtractCurriculumSyllabus` |

The `ExtractLeavingCertSyllabus` / `ExtractPastPaper` /
`ExtractMarkingScheme` (LC) functions are the **canonical** extraction
surface for the `leaving_cert_2026` openspec change (per
`oideachais/AGENTS.md:60` and the `leaving-cert-2026` change proposal).
They must work.

### 3. `baml_src/site_analysis.baml` is missing `ClassifyOfficialMedia`
The `dlt_sources/official_media/classifier.py:62` calls
`_baml_client.ClassifyOfficialMedia(...)` but the function is not
defined in any `.baml` file. `STATUS.md:29` references it but the
file has 0 functions (4 classes only). The official-media classifier
asset silently no-ops in production.

### 4. Three `from oideachais.core import X` imports remain
Per the Phase-3.6 migration shim (`oideachais/oideachais/__init__.py:1-21`),
the canonical locations for the 2 surviving constants are
`dlt_utils/batching.py` and `dlt_utils/safety.py`. The shim is still
imported by:

| File | Line | Symbol |
|---|--:|---|
| `oideachais/dlt_utils/batching.py` | 34 | `HNSW_DROP_THRESHOLD` |
| `oideachais/dlt_utils/safety.py` | 20 | `get_executor` |

These 2 are the only `from oideachais.core import X` imports
remaining in the quadrant (the third reference at
`oideachais/oideachais/core/__init__.py:6` is the shim's own
docstring). Migrating them lets us delete the shim.

### 5. Missing `Extractor` client declarations in 5 BAML files
Five BAML files reference `client Extractor` in function signatures
but only one (`baml_src/ocr_validation.baml:412`) actually has the
`client<llm> Extractor { ... }` declaration. The other 4 files
silently fall through to BAML's default client (which may or may
not work at generate time):

| File | References | Declaration |
|---|--:|---|
| `baml_src/audio_extraction.baml` | 3x | MISSING |
| `baml_src/ocr_extraction.baml` | 2x | MISSING |
| `baml_src/gaois/duchas.baml` | 5x | MISSING |
| `baml_src/gaois/folklore_extraction.baml` | 1x (also 2x `VisionExtractor`) | MISSING |
| `baml_src/gaois/logainm.baml` | 5x | MISSING |
| `baml_src/gaois/tearma.baml` | 9x | MISSING |

The fix is to add a single canonical `Extractor` client declaration
to `baml_src/clients.baml` (the canonical client registry).

### 6. `agentic_discovery.py` — `AgenticCrawler` class is missing
`oideachais/dagster_defs/resources.py:264` imports
`from ..dlt_sources.ireland.agentic_discovery import AgenticCrawler`,
but the class is not defined in `agentic_discovery.py` (only
`agentic_discovery_source` and `deep_research_source` are). The
import will fail at materialisation time when the
`AgenticCrawlerResource.__init__` runs. (Deferred to a follow-up
openspec change — the resource is not currently used by any asset.)

### 7. `leabharlann_full_stack_demo` — 4 missing asset_check functions
`oideachais/dagster_defs/definitions.py:198-202` imports 5 names
from `assets.leabharlann_full_stack_demo` but the file only defines
1 (`leabharlann_full_stack_demo`). The 4 missing are:
- `leabharlann_full_stack_demo_uog_extracted`
- `leabharlann_full_stack_demo_zotero_extracted`
- `leabharlann_full_stack_demo_baml_ok`
- `leabharlann_full_stack_demo_cocoindex_ok`

The file docstring (line 21) says: *"The asset's 4 checks assert the
5 steps above all ran successfully."* — the 4 checks are the
`@asset_check` decorators for the 5 pipeline steps (UoG extract,
Zotero extract, BAML extraction, CocoIndex update, Cognee cognify).
The current code logs a warning and falls through to an empty
asset list, which silently disables the demo asset. (Deferred to a
follow-up openspec change — the demo asset is non-critical.)

## What

This change fixes items **1, 2, 3, 4, 5** (the high-impact fixes
that unblock production). Items **6, 7** are documented and
deferred to a follow-up change.

### 1. Fix `edcolearning.py` import
- Replace `from oideachais.http_utils import HttpClientFactory`
  with `from oideachais.dlt_sources.common._http_factories import HttpClientFactory`
- Verify the `edcolearning.py` module imports cleanly

### 2. Fix 4 BAML `client litellm` references
- In each of the 4 BAML files, change `client litellm` → `client LitellmClient`
- Verify `baml-cli generate` succeeds for the 4 files

### 3. Add `ClassifyOfficialMedia` to `baml_src/site_analysis.baml`
- Add the missing function signature matching the call in
  `official_media/classifier.py:62`
- Use `client LitellmClient` (the canonical client)
- Define a simple prompt that classifies the Instagram profile as
  "official_media" or "not_official_media"

### 4. Migrate 3 `from oideachais.core import X` imports
- `dlt_utils/batching.py:34`: `from oideachais.core import HNSW_DROP_THRESHOLD`
  → `from oideachais.oideachais.core import HNSW_DROP_THRESHOLD`
  (or migrate the constant to `dlt_utils/batching.py` directly)
- `dlt_utils/safety.py:20`: `from oideachais.core import get_executor`
  → `from oideachais.oideachais.core import get_executor`
  (or migrate the function to `dlt_utils/safety.py` directly)

  The shim at `oideachais/oideachais/core/__init__.py` defines the
  constants inline; the canonical values are `HNSW_DROP_THRESHOLD = 50`
  and `get_executor(name="duckdb")` returning `ThreadPoolExecutor(max_workers=1)`.
  We migrate the **canonical definitions** into `dlt_utils/batching.py`
  and `dlt_utils/safety.py` directly, then keep the shim as a
  backward-compat re-export for one release.

### 5. Add canonical `Extractor` client to `baml_src/clients.baml`
- Add `client<llm> Extractor { provider "openai" options { model "gpt-4o-mini" temperature 0.1 } }`
- This becomes the canonical `Extractor` client; all 6 BAML files
  (audio_extraction, ocr_validation, ocr_extraction, gaois/duchas,
  gaois/folklore_extraction, gaois/logainm, gaois/tearma) reference
  it by name
- The duplicate `client<llm> Extractor` declaration in
  `baml_src/ocr_validation.baml:412` is deleted (replaced by the
  canonical declaration in clients.baml)

### Defer to follow-up
- **6. `agentic_discovery.py:AgenticCrawler`** — requires designing
  the resource properly. Tracked in a separate openspec change.
- **7. `leabharlann_full_stack_demo:4 asset_check functions`** —
  the demo asset is non-critical. Tracked in a separate openspec change.

## Impact

### Affected files
- **Modified:** `oideachais/dlt_sources/ireland/edcolearning.py` (1 import line)
- **Modified:** `oideachais/baml_src/leaving_cert_marking_scheme_extraction.baml` (1 line)
- **Modified:** `oideachais/baml_src/leaving_cert_past_paper_extraction.baml` (1 line)
- **Modified:** `oideachais/baml_src/leaving_cert_syllabus_extraction.baml` (1 line)
- **Modified:** `oideachais/baml_src/curriculum_extraction.baml` (1 line)
- **Modified:** `oideachais/baml_src/site_analysis.baml` (+ 1 function definition)
- **Modified:** `oideachais/baml_src/clients.baml` (+ 1 `Extractor` client declaration)
- **Modified:** `oideachais/baml_src/ocr_validation.baml` (- 1 redundant declaration)
- **Modified:** `oideachais/dlt_utils/batching.py` (migrate 1 import, add 1 constant)
- **Modified:** `oideachais/dlt_utils/safety.py` (migrate 1 import, add 1 function)

### Affected specs
- MODIFIED `oideachais-pipeline` — the rule that the canonical
  `HttpClientFactory` lives in `oideachais.dlt_sources.common._http_factories`
  and BAML functions use the canonical clients from `clients.baml`.
- MODIFIED `oideachais-baml-schemas` — the rule that the canonical
  `Extractor` client is in `clients.baml` and all BAML function
  signatures use `client <Name>` references to the canonical
  registry.

### Backward compatibility
- The `oideachais/oideachais/core/` shim is preserved as a
  backward-compat re-export for one release.
- All 4 leaving_cert_*_extraction.baml function signatures are
  unchanged; only the `client` name is corrected.
- The canonical `Extractor` client uses the same provider/model
  as the duplicate in `ocr_validation.baml` (gpt-4o-mini,
  temperature 0.1), so no behavior change for the 6 files that
  reference it.

## Non-Goals

- No new BAML functions added (other than the 1 missing
  `ClassifyOfficialMedia`).
- No agent resource changes (deferred).
- No demo asset check additions (deferred).
- No BAML client rewrite (the 4 canonical clients in
  `clients.baml` are the source of truth; we only add the
  `Extractor` declaration).

## Risk Assessment

- **Risk: edcolearning.py has a different API surface.** Mitigation:
  the `HttpClientFactory` class is byte-equivalent (defined in
  `dlt_sources/common/_http_factories.py:5-180`). Only the import
  path changes.
- **Risk: `client LitellmClient` doesn't match the BAML function
  expectations.** Mitigation: the 4 leaving_cert files use
  LitellmClient as the default for all BAML functions; the model
  is `deepseek-chat` via `http://litellm:4000/v1` (per
  `clients.baml:18`), which is the canonical oideachais LLM gateway.
- **Risk: the `Extractor` client declaration conflicts with the
  one in `ocr_validation.baml`.** Mitigation: we delete the
  duplicate in `ocr_validation.baml` in the same commit.

## Validation

1. `from oideachais.dlt_sources.ireland.edcolearning import edcolearning_source` succeeds (no `ImportError`)
2. `baml-cli generate` succeeds for `oideachais/baml_src/` (no `client litellm` errors)
3. `from oideachais.baml_src.site_analysis import SiteAnalysis` (no missing `ClassifyOfficialMedia` error at import time)
4. `uv run --package oideachais python -c "from oideachais.dlt_utils import EmbeddingBatcher"` still works
5. `uv run --package oideachais python -c "import dagster_defs.definitions"` still loads (pre-existing `leabharlann_full_stack_demo` warning unchanged)
6. `openspec validate fix-broken-imports-and-baml --strict` passes
