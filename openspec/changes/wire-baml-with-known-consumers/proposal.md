# wire-baml-with-known-consumers — Wire the aistear BAML extraction

## Why

Of the 30+ BAML functions defined in `oideachais/baml_src/`, several
have known downstream consumers but are not currently invoked. The
6 orphans that have known consumers per the explore agent's audit
(`STATUS.md:35` and the codebase) are:

1. `ExtractAistearFramework` (planned) — feeds the 5-stage cross-stage
   cognify pipeline (`cognee_integration/cross_stage_cognify.py`).
2. `ExtractLeavingCertSyllabus` (leaving-cert-2026) — feeds the LC
   2026 per-subject asset graph (70 stub `@asset`s in
   `dagster_defs/assets/leaving_cert/__init__.py`).
3. `ExtractPastPaper` (leaving-cert-2026) — same.
4. `ExtractMarkingScheme` (leaving-cert-2026) — same.
5. `ParseLogainmPlace` (planned) — feeds the logainm asset.
6. `ValidateOCRResult` (planned) — feeds the OCR comparison assets.

Of these 6, the **aistear wiring is the smallest and highest-impact**:
- The dlt source `aistear.py` already exists (per
  `dlt_sources/ireland/__init__.py`) with placeholder `"extracted_at":
  "PENDING_BAML"` fields
- A `@dlt_assets` wrapper does not exist
- The 5-stage cross-stage cognify pipeline depends on it but currently
  logs and returns 0

The other 5 (LC + logainm + OCR) are scoped to the existing
`leaving-cert-2026`, `ireland-primary-jc-dlt-baml-and-full-stack-demo`,
and `croilar-cv-extraction` openspec changes which already track the
work. **This change scopes the AISTEAR wiring only**; the other 5
remain on the respective openspec changes.

## What

### 1. Add a new BAML module: `baml_src/early_childhood.baml`
A new dedicated BAML module for early-childhood curriculum
extraction. Contains:
- `class AistearFramework { themes string[]; principles AistearPrinciple[]; learning_goals AistearLearningGoal[]; }`
- `class AistearPrinciple { name string; description string; age_band string; }`
- `class AistearLearningGoal { goal_id string; description string; theme string; age_band string; }`
- `class AistearDocument { document_id string; title string; framework AistearFramework; extracted_at string; }`
- `function ExtractAistearFramework(pdf_text: string) -> AistearFramework` (uses `client LitellmClient`)

### 2. Wire the BAML call in `dlt_sources/ireland/aistear.py`
- Import `baml_client.b` (with `try/except ImportError` graceful degradation)
- In the `aistear_documents` resource, after the placeholder yield,
  call `b.ExtractAistearFramework(pdf_text=extracted_text, file_name=pdf.name)`
  to extract principles + learning goals
- Add 2 new `@dlt.resource` functions:
  - `aistear_principles(primary_key=["framework_document_id", "principle_name"])`
  - `aistear_learning_goals(primary_key=["goal_id"])`
- Update `aistear_curriculum()` source to yield all 3 resources

### 3. Add a Dagster asset wrapper: `dagster_defs/assets/ie/education/aistear_dlt_assets.py`
A simple `@asset` wrapper (similar to the `leaving_cert/dlt_assets.py`
pattern) that runs the dlt pipeline and materialises the 3 tables
into a per-stage `ie.education.aistear` DuckLake dataset. Computes:
- `aistear_documents_ducklake` (1 asset)
- `aistear_principles_ducklake` (1 asset, depends on documents)
- `aistear_learning_goals_ducklake` (1 asset, depends on documents)
- A `aistear_baml_extraction` asset that reads the documents table
  and writes the BAML-extracted fields back (graceful no-op if
  `baml_client` is not generated)

### 4. Register the new assets
- Add the 3 new assets to `dagster_defs/assets/__init__.py` (or
  `dagster_defs/assets/ie/education/__init__.py` if it exists)
- Add a job `aistear_full` that materialises all 3

## Impact

### Affected files
- **NEW:** `oideachais/baml_src/early_childhood.baml` (~80 lines)
- **MODIFIED:** `oideachais/dlt_sources/ireland/aistear.py` (~50 lines added: BAML call + 2 new resources)
- **NEW:** `oideachais/dagster_defs/assets/ie/education/aistear_dlt_assets.py` (~80 lines)
- **MODIFIED:** `oideachais/dagster_defs/assets/__init__.py` (register the 3 new assets)

### Affected specs
- MODIFIED `oideachais-baml-schemas` — the rule that BAML functions
  for the 5 educational stages (Aistear, Primary, JC, SC, Tertiary)
  MUST be defined and wired to their consuming dlt sources.
- MODIFIED `oideachais-pipeline` — the rule that every dlt source
  in `dlt_sources/ireland/` MUST have a corresponding Dagster asset
  wrapper that materialises its tables.

### Backward compatibility
- The new BAML function `ExtractAistearFramework` is added, not
  replaced. The dlt source's existing `aistear_curriculum` source
  signature is unchanged; the 2 new resources are additive.
- The new Dagster assets use `try/except ImportError` graceful
  degradation (the same pattern used by `edcolearning.py` and
  `agentic_discovery.py`); the dlt source still works even
  without BAML client generation.
- The `ireland/__init__.py` re-export list gains
  `ExtractAistearFramework` (additive).

## Non-Goals

- No wiring of the 5 LC BAML functions (`ExtractLeavingCertSyllabus`,
  `ExtractPastPaper`, `ExtractMarkingScheme`) — those are scoped to
  the existing `leaving-cert-2026` openspec change.
- No wiring of `ParseLogainmPlace` — scoped to the existing
  `ireland-primary-jc-dlt-baml-and-full-stack-demo` change.
- No wiring of `ValidateOCRResult` — scoped to the existing
  `celtic-data-engineering-patterns` change.
- No new BAML extraction for Primary / JC / Tertiary stages —
  scoped to the `ireland-primary-jc-dlt-baml-and-full-stack-demo`
  change.
- No Cognee cognify change — the 5-stage cross-stage cognify
  already exists; this change only provides the aistear input
  data.

## Risk Assessment

- **Risk: BAML client is not generated in the dev venv.** Mitigation:
  the dlt source and Dagster asset both use `try/except ImportError`
  graceful degradation. Without BAML, the placeholder fields stay
  as `"extracted_at": "PENDING_BAML"`.
- **Risk: aistear.py doesn't have a Dagster asset wrapper today.**
  Mitigation: this change adds the wrapper.
- **Risk: cross-stage cognify depends on aistear data that doesn't
  exist yet.** Mitigation: the cognify is already a stub that
  returns 0 edges; adding the aistear data is the prerequisite
  for the cognify to be turned on (separate change).

## Validation

1. `from oideachais.dlt_sources.ireland.aistear import aistear_curriculum` succeeds
2. `from oideachais.dlt_sources.ireland.aistear import aistear_principles, aistear_learning_goals` succeeds
3. `baml-cli generate` succeeds (no schema errors in the new early_childhood.baml)
4. `uv run --package oideachais python -c "import dagster_defs.definitions"` still loads
5. `uv run --package oideachais python -c "from oideachais.dagster_defs.assets.ie.education.aistear_dlt_assets import aistear_documents_ducklake"` succeeds
6. `openspec validate wire-baml-with-known-consumers --strict` passes
