# Tasks: wire-baml-with-known-consumers

## Phase 1: Create early_childhood.baml

- [ ] Create `oideachais/baml_src/early_childhood.baml` with:
  - `class AistearFramework` (themes, principles, learning_goals)
  - `class AistearPrinciple` (name, description, age_band)
  - `class AistearLearningGoal` (goal_id, description, theme, age_band)
  - `class AistearDocument` (document_id, title, framework, extracted_at)
  - `function ExtractAistearFramework(pdf_text: string) -> AistearFramework` (with `client LitellmClient`)
  - Prompt that asks for the 4 Aistear themes (Well-being, Identity & Belonging, Communicating, Exploring & Thinking), 12 principles, and 50+ learning goals
- [ ] Verify: `grep -n "ExtractAistearFramework" oideachais/baml_src/early_childhood.baml` shows 1 hit

## Phase 2: Wire aistear.py

- [ ] In `oideachais/dlt_sources/ireland/aistear.py`:
  - Add the BAML client import with try/except graceful degradation
  - In the `aistear_documents` resource, after the placeholder yield, extract text and call `b.ExtractAistearFramework`
  - Add `@dlt.resource(name="aistear_principles", write_disposition="merge", primary_key=["framework_document_id", "principle_name"])` yielding one row per principle
  - Add `@dlt.resource(name="aistear_learning_goals", write_disposition="merge", primary_key=["goal_id"])` yielding one row per learning goal
  - Update `aistear_curriculum()` to yield all 3 resources
- [ ] Verify: `python -c "from oideachais.dlt_sources.ireland.aistear import aistear_principles, aistear_learning_goals, aistear_curriculum; print('OK')"`

## Phase 3: Add Dagster asset wrapper

- [ ] Create `oideachais/dagster_defs/assets/ie/education/aistear_dlt_assets.py`:
  - 3 `@asset` functions: `aistear_documents_ducklake`, `aistear_principles_ducklake`, `aistear_learning_goals_ducklake`
  - 1 `@asset_check` function asserting the row counts match
  - 1 `define_asset_job` for `aistear_full`
  - Use the same pattern as `leaving_cert/dlt_assets.py`
- [ ] Verify: `python -c "from oideachais.dagster_defs.assets.ie.education.aistear_dlt_assets import aistear_documents_ducklake; print('OK')"`

## Phase 4: Register the new assets

- [ ] Read `oideachais/dagster_defs/assets/ie/education/__init__.py` to find the registration point
- [ ] Add the 3 new assets + the job to the registration
- [ ] Verify: `python -c "import dagster_defs.definitions; print('OK')"` still loads

## Phase 5: Update re-exports

- [ ] In `oideachais/dlt_sources/ireland/__init__.py`:
  - Add `aistear_principles, aistear_learning_goals` to the re-exports
- [ ] Verify: `python -c "from oideachais.dlt_sources.ireland import aistear_principles, aistear_learning_goals; print('OK')"`

## Phase 6: Validation

- [ ] `openspec validate wire-baml-with-known-consumers --strict` passes
- [ ] `grep -rn "ExtractAistearFramework" oideachais/` shows 2 hits (the BAML declaration + the aistear.py call)
- [ ] `grep -rn "PENDING_BAML" oideachais/dlt_sources/ireland/aistear.py` returns 0 hits (placeholder replaced)
- [ ] `uv run --package oideachais python -c "import dagster_defs.definitions"` still loads

## Phase 7: Land the plane

- [ ] Stage the changes
- [ ] Commit: `git commit -m "wire-baml-with-known-consumers: wire aistear ExtractAistearFramework"`
- [ ] `git pull --rebase`
- [ ] `git push origin q3-2026-oideachais-consolidation`
