# Spec Delta — cianfhoghlaim-baml-schemas

This delta adds 1 new Requirement to the existing 18 (18 → 19).
The MODIFIED section is the new requirements only; the existing
18 requirements are preserved unchanged.

## ADDED Requirements

### Requirement: NCCA strand/outcome catalog supports runtime TypeBuilder mutation

The `cianfhoghlaim-baml-schemas` capability SHALL support runtime
injection of per-strand, per-outcome, per-curriculum-spec, and
per-assessment-component properties into the 4 canonical NCCA-related
BAML classes — `LearningOutcome`, `CurriculumStrand`,
`CurriculumSpecStrand`, and `AssessmentComponentStrand` — marked
`@@dynamic` per the BAML v0.221+ `TypeBuilder` spec, with the
catalog loaded at startup from the canonical YAML config file at
`baml/education/_shared/strand_catalog.yaml`.

The runtime helper SHALL be `build_ncca_strand_type_builder()`
in `baml/education/_shared/strand_type_builder.py`.

This capability decouples the **schema-deployment cycle**
(`baml-cli generate` + release) from the **catalog-update cycle**
(NCCA yearly refresh + restart the pipeline), so the operator
can add new strands/outcomes by editing the YAML config + restarting
the pipeline without redeploying the BAML schema.

#### Scenario: 4 `@@dynamic` markers are present on the canonical NCCA classes

- **GIVEN** the file `baml/education/_shared/strand_outcome.baml`
- **WHEN** `grep -c "@@dynamic" baml/education/_shared/strand_outcome.baml`
  is run
- **THEN** the count is exactly 4
- **AND** the 4 markers are attached to the class declarations
  for `LearningOutcome`, `CurriculumStrand`, `CurriculumSpecStrand`,
  and `AssessmentComponentStrand` (NOT to siblings like
  `EnhancedLearningOutcome`, `ExamAssessmentComponent`, or
  `AssessmentComponent` in `multi_nation_curriculum.baml`)

#### Scenario: TypeBuilder helper loads the catalog YAML successfully

- **GIVEN** the catalog YAML at
  `baml/education/_shared/strand_catalog.yaml`
  contains the 6 LC priority subjects (Mathematics, Chemistry,
  Geography, Gaeilge, English, Computer Science)
- **WHEN** `python -m cianfhoghlaim.baml.education._shared.strand_type_builder`
  is run from the project root
- **THEN** the CLI prints a 4-section summary
  (`strands`, `outcomes`, `specifications`, `assessment_components`)
  with the catalog counts summing to 53 or more
- **AND** the CLI exits 0 even when the `baml_client` can't be
  imported (the helper falls back to `None` + a warning)

#### Scenario: TypeBuilder helper injects per-strand properties

- **GIVEN** a representative catalog (10 strands, 4 outcomes)
  is loaded from the YAML
- **WHEN** `build_ncca_strand_type_builder(catalog=catalog)` is
  called from Python (or the smoke test invokes it via the
  BAML test harness)
- **THEN** the helper walks the catalog and calls
  `tb.<ClassName>.add_property(prop_name, field_type)` for
  every per-strand / per-outcome / per-spec / per-component
  property declared in the YAML
- **AND** the 4 type-name mappings (`string` → `tb.string()`,
  `int` → `tb.int()`, `float` → `tb.float()`,
  `bool` → `tb.bool()`) are respected

#### Scenario: Catalog YAML is valid

- **GIVEN** `baml/education/_shared/strand_catalog.yaml`
- **WHEN** `uv run python -c "import yaml; yaml.safe_load(open('...'))"`
  is run
- **THEN** the YAML parses as a valid `dict[str, Any]`
- **AND** `len(data["strands"]) >= 23` (the 6 LC priority subjects
  are each represented)
- **AND** `len(data["outcomes"]) >= 10` (a representative subset
  across the 6 subjects)
- **AND** the 4 sections (`strands`, `outcomes`, `specifications`,
  `assessment_components`) are all present

#### Scenario: Operator can update the catalog without regen'ing the BAML schema

- **GIVEN** the operator has a new NCCA refresh (e.g. the 2027-07-01
  yearly update adds a new strand `LC Mathematics Strand 5: Discrete
  Mathematics`)
- **WHEN** the operator edits
  `baml/education/_shared/strand_catalog.yaml` to
  add the new strand + its properties
  (no `baml-cli generate`, no schema redeploy)
- **THEN** the next pipeline run that calls
  `build_ncca_strand_type_builder()` automatically picks up the
  new strand
- **AND** the LC BIEP Dagster assets that depend on this catalog
  continue to function without a release

#### Scenario: `mise run baml:test` does not add new errors

- **GIVEN** the 50+ pre-existing out-of-scope `baml-cli`
  validation errors in the `pdfs/` + `_shared/` + `lc_extraction/`
  + `qpack_*` + `celtic/` clusters
- **WHEN** `mise run baml:test` is run after this change lands
- **THEN** the error count is unchanged (1754 errors before, 1754
  errors after — the 4 `@@dynamic` markers + the new test block +
  the new `ExtractStrandFromCatalog` function add 0 new errors)
- **AND** the existing 1754 errors are out of scope per the 3
  prior follow-up commits (`1623849d9` + `476c866b8` + `49e0259a0`
  + `5e6734b57`)

#### Scenario: The 7 BIEP `lc_extraction/*.baml` files are untouched

- **GIVEN** the BIEP v1 owns the 7 `baml/education/lc_extraction/*.baml`
  files (per the
  `openspec/changes/2026-07-06-british-isles-education-pipeline-v1/`
  change)
- **WHEN** `git diff --stat origin/pick-4-biep-v1 -- baml/education/lc_extraction/`
  is run after this change lands
- **THEN** the diff is empty
- **AND** the BIEP v1 Phase 4-5 DAG materialization is not
  blocked by this change
