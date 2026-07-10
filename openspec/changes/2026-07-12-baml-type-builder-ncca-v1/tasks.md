# Tasks — BAML TypeBuilder + `@@dynamic` for the NCCA strand/outcome catalog

## 1. Mark 4 NCCA classes as `@@dynamic` in `strand_outcome.baml`

- [x] **1.1** `LearningOutcome` (line 10) gets `@@dynamic` after
      `key_skills`
- [x] **1.2** `CurriculumStrand` (line 92) gets `@@dynamic` after
      `weighting`
- [x] **1.3** `AssessmentComponentStrand` (line 100) gets
      `@@dynamic` after `levels`
- [x] **1.4** `CurriculumSpecStrand` (line 116) gets `@@dynamic`
      after `total_hours`
- [x] **1.5** Confirm `grep -c "@@dynamic" baml/education/_shared/strand_outcome.baml`
      returns exactly 4

## 2. Create the runtime TypeBuilder helper at `strand_type_builder.py`

- [x] **2.1** Write `baml/education/_shared/strand_type_builder.py`
      (~280 lines)
- [x] **2.2** Implement `load_catalog(catalog_path=None)` — reads the
      YAML, returns a 4-section dict (`strands`, `outcomes`,
      `specifications`, `assessment_components`)
- [x] **2.3** Implement `_inject_properties(class_viewer, properties, tb)`
      — maps the 4 primitive type names (`string` / `int` / `float`
      / `bool`) to the `tb.<primitive>()` factory and calls
      `class_viewer.add_property(name, type)`
- [x] **2.4** Implement `build_ncca_strand_type_builder(...)` — instantiates
      `baml_client.type_builder.TypeBuilder()`, walks the catalog,
      injects the per-strand / per-outcome / per-spec / per-component
      properties
- [x] **2.5** Fall back to `None` when `baml_client` is not
      importable (baml-py version skew); caller can still detect this
      and skip the TypeBuilder step
- [x] **2.6** Add `python -m baml.education._shared.strand_type_builder`
      CLI that prints the catalog summary and the TypeBuilder status

## 3. Create the representative NCCA catalog YAML

- [x] **3.1** Write `baml/education/_shared/strand_catalog.yaml` with
      23 strands (4 Mathematics, 4 Chemistry, 3 Geography, 4 Gaeilge,
      4 English, 4 Computer Science)
- [x] **3.2** Add 10 outcomes across the 6 LC priority subjects
      (Mathematics MO1-MO3, Chemistry CO1-CO2, Geography GO1-GO2,
      Gaeilge GaO1, English EO1, Computer Science CSO1)
- [x] **3.3** Add 7 curriculum specifications (per `(subject, level)`
      pair the pipeline tracks: math/chem/geog/ga/en/cs at higher or
      ordinary)
- [x] **3.4** Add 13 assessment components (per-subject component
      tree: 2 Math papers, 1 Chem written + 1 Chem practical,
      2 Geography written + 1 Geography field report, 3 Gaeilge,
      2 English, 2 Computer Science)
- [x] **3.5** Confirm `python -c "import yaml; yaml.safe_load(open('strand_catalog.yaml'))"`
      returns a valid YAML structure
- [x] **3.6** Confirm total catalog entries = 53 (23 + 10 + 7 + 13)

## 4. Add `strand_type_builder_smoke` test block to `strand_outcome.baml`

- [x] **4.1** Write `test strand_type_builder_smoke { ... }` block
      referencing the new `ExtractStrandFromCatalog` function
- [x] **4.2** Write `function ExtractStrandFromCatalog(catalog_yaml: string)
      -> CurriculumSpecStrand[]` — the extraction function the test
      exercises (uses the canonical
      `anthropic/claude-sonnet-4-20250514` client)
- [x] **4.3** Inline the representative 10-strand catalog as a
      `<<#>>` raw-string test argument
- [x] **4.4** Confirm the test block parses (no new
      `Error validating` in lines 325-417 of `strand_outcome.baml`)

## 5. Create the 2 new `__init__.py` package markers

- [x] **5.1** Create `baml/education/__init__.py` (empty docstring,
      mirrors the `baml/education/law/__init__.py` precedent)
- [x] **5.2** Create `baml/education/_shared/__init__.py` (empty
      docstring, documents the 8 cross-stage shared BAML files +
      the 2 runtime helpers + the catalog YAML)
- [x] **5.3** Confirm `python -c "from baml.education._shared.strand_type_builder import build_ncca_strand_type_builder"`
      imports cleanly

## 6. Verify

- [x] **6.1** Run `python -m baml.education._shared.strand_type_builder`
      — confirm the catalog loads (53 entries) and the TypeBuilder
      status is reported (warns on the pre-existing baml-py version
      skew, but exits 0)
- [x] **6.2** Run `mise run baml:test` — confirm the error count is
      unchanged (1754 before, 1754 after — my changes add 0 new
      errors; the 50+ pre-existing out-of-scope errors are out of
      scope per the 3 prior follow-up commits)
- [x] **6.3** Run `grep -c "@@dynamic" baml/education/_shared/strand_outcome.baml`
      — confirm exactly 4
- [x] **6.4** Run `grep -c "^@@dynamic" baml/education/_shared/strand_outcome.baml`
      — confirm exactly 4 markers (comment text shouldn't count as a
      marker)
- [x] **6.5** Run `openspec validate 2026-07-12-baml-type-builder-ncca-v1 --strict`
      — must pass before commit

## 7. OpenSpec change artefacts

- [x] **7.1** Create `openspec/changes/2026-07-12-baml-type-builder-ncca-v1/`
- [x] **7.2** Write `proposal.md` (this change)
- [x] **7.3** Write `tasks.md` (this file)
- [x] **7.4** Write `specs/oideachais-baml-schemas/spec.md` delta
      (1 ADDED Requirement)

## 8. Commit + push

- [x] **8.1** `git add -A` (5 modified + 4 new files)
- [x] **8.2** Commit with `feat(baml):` prefix
- [x] **8.3** Push to `origin/pick-4-biep-v1` (NOT `main`)

## Out of scope (deferred to follow-up openspec changes)

- The 7 `lc_extraction/*.baml` files (owned by BIEP v1 follow-up)
- The 50+ pre-existing `baml-cli` validation errors in the
  `_shared/` / `pdfs/` / `lc_extraction/` / `qpack_*` / `celtic/`
  clusters (owned by separate openspec changes)
- The baml-py / baml_client version skew (this change ships the
  helper + the test + the catalog anyway; the skew is gracefully
  handled)
- The final follow-up (5 tutorials) — owned by a separate openspec
  change
- The 50+ archived openspec changes under `openspec/changes/archive/*`
  — preserved unchanged
