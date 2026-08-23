# oideachais-baml-schemas Specification

## Purpose
The oideachais BAML schemas surface covers the 9 BAML extraction templates for the 6 Irish Leaving Certificate priority subjects (Mathematics / Chemistry / Geography / Gaeilge / English / Computer Science) + the gov.ie circulars + the university syllabus pipeline across the Cianfhoghlaim monorepo. It defines 12 invariants: the 9 canonical extraction functions (ExtractCurriculumSyllabus / ExtractExamPaperLayout / ExtractMarkingSchemeGuideline / ExtractCrossLinguisticConcept / ExtractSyllabusDiagram + 4 variants), the 3 extraction clients (ExtractEn / ExtractEnStrong / LocalVision), and the per-subject BAML test blocks.

## Requirements
### Requirement: BAML surface compiles cleanly across the 8 jurisdiction packs

The system SHALL compile the full British Isles BAML surface (Ireland LC6 +
England + Scotland/Wales/NI + Crown Dependencies + Commonwealth + EU +
American Nations) without error.

#### Scenario: All 4 canonical BIEP functions are declared with valid signatures

- **WHEN** the user runs `mise run baml:generate`
- **THEN** the BAML compiler SHALL resolve all `function` declarations,
      including:
  - 8 `ExtractCurriculumSyllabus(subject, language)` (one per jurisdiction)
  - 8 `ExtractExamPaperLayout(paper_code, year)` (one per jurisdiction)
  - 8 `ExtractMarkingSchemeGuideline(year, paper)` (one per jurisdiction)
  - 8 `ExtractCrossLinguisticConcept(...)` (one per jurisdiction)
  - 8 `ExtractSyllabusDiagram(...)` (one per jurisdiction)
- **AND THEN** `baml_src/british_isles/<jurisdiction>/education/` SHALL
      NOT depend on the deprecated `_legacy/grading/` test files for
      compilation to succeed

#### Scenario: Legacy grading files compile or are archived

- **WHEN** the BAML compiler walks `baml_src/british_isles/ireland/education/_legacy/grading/*.baml`
- **THEN** each file SHALL compile without error after the `test` → `Test`
      keyword fix
- **OR THEN** those files SHALL be archived to `_archive/` per the
      project's deprecation policy (one release cycle of deprecation
      shim is allowed)

#### Scenario: No missing-`client`-field errors in legacy web files

- **WHEN** the user runs `mise run baml:generate`
- **THEN** `_legacy/web/gaeilge_web.baml` SHALL compile without error after
      adding `client ExtractEn` to the 3 `Web*` functions
- **OR THEN** the file SHALL be archived to `_archive/`

#### Scenario: England schemas compile without default-value class fields

- **WHEN** the BAML compiler walks `baml_src/british_isles/england/education/`
- **THEN** `curriculum_syllabus.baml` (3 sites at lines 52, 71, 90) and
      `exam_paper_layout.baml` (line 47) SHALL NOT carry `language string = "en"`
- **AND THEN** the field type SHALL be `language string?` instead

#### Scenario: england_education ensembled_extraction.baml is valid

- **WHEN** the BAML compiler walks
      `baml_src/british_isles/england/education/ensembled_extraction.baml:38`
- **THEN** the `@description` string on `voted_canonical_id` SHALL be
      well-formed (closed before EOF)
- **AND THEN** the file SHALL compile

### Requirement: All 50 pre-existing BAML `field: type` errors resolved

The `cianfhoghlaim-baml-schemas` capability SHALL have all 50 pre-existing BAML `field: type` parse diagnostics (captured in the baseline at `openspec/changes/2026-07-13-baml-final-cleanup-v1/SCOPE_DECISION.md`) resolved across the full `baml/` tree. `mise run baml:generate` SHALL exit 0 against the current tree.

#### Scenario: baml:generate exits 0 against the full tree

- **GIVEN** the 2026-07-13-fix-baml-50-out-of-scope-errors-v1 change has landed
- **WHEN** `mise run baml:generate` is run from the repo root
- **THEN** it exits with code 0
- **AND** the `baml_client/` directory is regenerated successfully (14 files written to `baml/baml_client/`)
- **AND** the canonical types `MarkingScheme`, `MarkingSchemeSec`, `MarkingSchemeStrand`, `BilingualText`, `PastPaper`, `NCCAKeyCompetency`, `CrossNationLearningOutcome` are all present in the generated `baml_client/baml_client/types.py`

#### Scenario: full BAML tree compiles cleanly

- **GIVEN** the canonical 75-file `.baml` tree at `baml/`
- **WHEN** `uv run baml-cli generate --from baml_src` is invoked
- **THEN** the BAML parser reports 0 `error:` lines in its output
- **AND** the parser reports 0 `warning:` lines related to `field: type` syntax

#### Scenario: 7 lc_extraction/*.baml files are part of the fix scope

- **GIVEN** the user chose Option 2 from the SCOPE_DECISION.md (fix ALL 50 errors including the 7 `baml/education/lc_extraction/*.baml` files)
- **WHEN** the BAML tree is grep'd for `field: type` patterns (excluding inside prompt blocks)
- **THEN** the 7 `lc_extraction/*.baml` files report 0 Pydantic-style attribute lines
- **AND** the canonical 7 lc_extraction functions (`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`, `ExtractMarkingSchemeGuideline`, `ExtractStrandFromCatalog`, `ExtractMarkingSchemeStrand`, `ExtractCelticCurriculumComparison`, `ExtractSyllabusDiagram`) all remain present and produce the same Pydantic output classes as before

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

### Requirement: baml-cli test CI hard gate

The system SHALL run `baml-cli test` as a hard GitHub Actions CI gate on every pull request and push targeting `pick-4-biep-v1` or `main`.

#### Scenario: Pull request runs BAML tests

- **GIVEN** a pull request targets `pick-4-biep-v1` or `main`
- **WHEN** GitHub Actions evaluates `.github/workflows/baml-test.yaml`
- **THEN** the `baml-test` job SHALL install the Python/uv/mise runtime and dependencies
- **AND** the job SHALL run `mise run baml:test` from `cianfhoghlaim/`
- **AND** `mise run baml:test` SHALL invoke `uv run baml-cli test`
- **AND** a non-zero `baml-cli test` exit code SHALL fail the job and block merge.

#### Scenario: Push runs BAML tests

- **GIVEN** a commit is pushed to `pick-4-biep-v1` or `main`
- **WHEN** GitHub Actions evaluates `.github/workflows/baml-test.yaml`
- **THEN** the `baml-test` job SHALL run `mise run baml:test` from `cianfhoghlaim/`
- **AND** the workflow SHALL upload the captured CLI output under the `baml-test-results` artifact with 30-day retention.

#### Scenario: Manual dispatch runs BAML tests

- **GIVEN** a maintainer starts `.github/workflows/baml-test.yaml` via `workflow_dispatch`
- **WHEN** the workflow runs
- **THEN** it SHALL execute the same `mise run baml:test` hard gate used for PRs and branch pushes.

### Requirement: baml_client regenerates with 0 errors in the processing cluster

The `baml_client/` Python module SHALL regenerate cleanly (`mise run baml:generate`
exits 0 with respect to the 17 processing-cluster files) after migrating all
`.baml` files in `baml/processing/` from the deprecated
Pydantic-style `field: type` syntax to BAML v0.212+ canonical
`field type` (whitespace-separated) syntax.

#### Scenario: baml:generate succeeds for the 17 migrated processing files

- **GIVEN** the 17 `.baml` files in `baml/processing/` are
  rewritten to canonical v0.212+ syntax (per
  `scripts/migrate-baml-syntax.py --apply`)
- **WHEN** `mise run baml:generate` is run and the validator reaches the
  processing cluster
- **THEN** the validator reports 0 Pydantic-style errors in those 17 files
- **AND** `baml_client/` is regenerated at
  `baml/shared/baml_client/`

#### Scenario: Migration script is idempotent

- **GIVEN** `scripts/migrate-baml-syntax.py --apply` has been run on the
  17 target files
- **WHEN** `scripts/migrate-baml-syntax.py --dry-run` is re-run
- **THEN** the script reports 0 changes pending
- **AND** no files are modified

### Requirement: baml syntax migration helper at scripts/migrate-baml-syntax.py

A `scripts/migrate-baml-syntax.py` helper SHALL exist with `--dry-run`,
`--apply`, and `--verify` modes for rewriting `.baml` files from
Pydantic-style `field: type` to BAML v0.212+ canonical `field type`
(whitespace-separated) syntax. The script SHALL defensively skip lines
inside `#"...content...#` raw-string blocks (prompt bodies + test-arg
docs) and lines containing `{{`/`}}` Jinja tokens, so it never rewrites
content inside BAML prompts.

#### Scenario: --dry-run prints diffs without modifying files

- **WHEN** `uv run python scripts/migrate-baml-syntax.py --dry-run` is run
- **THEN** the script prints the per-file change counts and the first 10
  before/after diffs for each file
- **AND** no `.baml` file is modified

#### Scenario: --apply rewrites files in place

- **WHEN** `uv run python scripts/migrate-baml-syntax.py --apply` is run
- **THEN** each of the 17 target `.baml` files is rewritten with
  `field: type` replaced by `field type` (plus any `[]` / `?` /
  `@description(...)` attrs preserved)
- **AND** the script reports the line count rewritten per file

#### Scenario: --verify exits 1 if any Pydantic-style lines remain

- **WHEN** `uv run python scripts/migrate-baml-syntax.py --verify` is run
- **THEN** the script exits 0 with `[OK] No Pydantic-style attribute lines remain`
  if all 17 target files are canonical
- **AND** exits 1 with `[FAIL] N Pydantic-style lines remain` otherwise,
  listing each remaining line by `file:lineno`

### Requirement: Active single minimax-m3 text generator

The `cianfhoghlaim-baml-schemas` capability SHALL define a single active text-extraction generator in `baml/clients.baml`: `generator default`, routed to the `minimax-m3` model through the OpenAI-compatible coding-plan API using `MINIMAX_BASE_URL` and `MINIMAX_API_KEY`.

The historical 8-generator layout (`default`, `local_vision_qwen`, `local_vision_glm`, `local_vision_moondream`, `gemini_2_flash`, `gemini_1_5_pro`, `gemini_pro`, `gemini_2_5_flash`) SHALL be preserved as a comment block for future reactivation when provider credentials become available. The two local vision generators `local_vision_gemma4` and `local_vision_qwen3vl` SHALL remain active.

#### Scenario: only supported active generators remain

- **GIVEN** the 2026-07-13 minimax cleanup has landed
- **WHEN** active generator declarations are enumerated from `baml/clients.baml`
- **THEN** the active generator names are exactly `default`, `local_vision_gemma4`, and `local_vision_qwen3vl`
- **AND** `generator default` includes `provider "openai-generic"`, `model "minimax-m3"`, `base_url env.MINIMAX_BASE_URL`, and `api_key env.MINIMAX_API_KEY`
- **AND** the historical 8-generator setup remains available only as line comments

#### Scenario: Minimax-M3 environment placeholders exist

- **GIVEN** a developer is configuring the BAML runtime locally
- **WHEN** they inspect `.env.example`
- **THEN** it documents `MINIMAX_BASE_URL` and `MINIMAX_API_KEY` placeholders for the M3 coding-plan API path

### Requirement: Per-subject web schemas + stage schemas as UI schema inputs

The system SHALL cross-reference the 6 per-subject BAML web schemas
(`baml/education/web/<subject>_web.baml`) + the 5 stage BAML
extraction files
(`baml/education/stages/{aistear,primary,junior_cycle,senior_cycle,tertiary}.baml`)
as the **UI schema inputs** for the A2UI catalog at
`packages/ui/a2ui-catalog.tsx`.

This requirement is the source-of-truth for the UI schema pipeline
described in `openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-leaving-cert-portal/spec.md`
R18 + R21 + R22.

#### Scenario: A developer updates a per-subject web schema

- **GIVEN** a developer adds a new field to `mathematics_web.baml::MathematicsWebStudyPlanResponse`
- **WHEN** they re-generate the BAML client
- **THEN** the A2UI catalog TypeScript types update automatically
- **AND** the corresponding `<StudyPlanCard>` renderer signature updates
- **AND** `mise run baml:cli:test` fails until the catalog is updated

### Requirement: BAML v0.212+ migration — canonical `field Type` syntax + migrate-baml-syntax.py helper

The `baml_client/` Python module SHALL regenerate cleanly
(`mise run baml:generate` exits 0 with respect to the 17
processing-cluster files) after migrating all `.baml` files in
`baml/processing/` from the deprecated Pydantic-style
`field: type` syntax to BAML v0.212+ canonical `field type`
(whitespace-separated) syntax.

A `scripts/migrate-baml-syntax.py` helper SHALL exist with
`--dry-run`, `--apply`, and `--verify` modes for rewriting `.baml`
files from Pydantic-style `field: type` to BAML v0.212+ canonical
`field type` (whitespace-separated) syntax. The script SHALL
defensively skip lines inside `#"...content...#` raw-string blocks
(prompt bodies + test-arg docs) and lines containing `{{`/`}}` Jinja
tokens, so it never rewrites content inside BAML prompts.

*(Consolidates the 2 ADDED Requirements from
`2026-07-10-fix-baml-codegen-v4-syntax-v1`.)*

#### Scenario: baml:generate succeeds for the 17 migrated processing files

- **GIVEN** the 17 `.baml` files in `baml/processing/`
      are rewritten to canonical v0.212+ syntax (per
      `scripts/migrate-baml-syntax.py --apply`)
- **WHEN** `mise run baml:generate` is run and the validator reaches
      the processing cluster
- **THEN** the validator reports 0 Pydantic-style errors in those 17
      files
- **AND** `baml_client/` is regenerated at
      `baml/shared/baml_client/`

#### Scenario: Migration script is idempotent

- **GIVEN** `scripts/migrate-baml-syntax.py --apply` has been run on
      the 17 target files
- **WHEN** `scripts/migrate-baml-syntax.py --dry-run` is re-run
- **THEN** the script reports 0 changes pending
- **AND** no files are modified

#### Scenario: --dry-run prints diffs without modifying files

- **WHEN** `uv run python scripts/migrate-baml-syntax.py --dry-run`
      is run
- **THEN** the script prints the per-file change counts and the first
      10 before/after diffs for each file
- **AND** no `.baml` file is modified

#### Scenario: --apply rewrites files in place

- **WHEN** `uv run python scripts/migrate-baml-syntax.py --apply` is run
- **THEN** each of the 17 target `.baml` files is rewritten with
      `field: type` replaced by `field type` (plus any `[]` / `?` /
      `@description(...)` attrs preserved)
- **AND** the script reports the line count rewritten per file

#### Scenario: --verify exits 1 if any Pydantic-style lines remain

- **WHEN** `uv run python scripts/migrate-baml-syntax.py --verify` is run
- **THEN** the script exits 0 with
      `[OK] No Pydantic-style attribute lines remain` if all 17
      target files are canonical
- **AND** exits 1 with `[FAIL] N Pydantic-style lines remain`
      otherwise, listing each remaining line by `file:lineno`

### Requirement: BAML v0.223 test CI gate — `baml-cli test` as a hard GitHub Actions CI gate

The system SHALL run `baml-cli test` as a hard GitHub Actions CI gate
on every pull request and push targeting `pick-4-biep-v1` or `main`,
via `.github/workflows/baml-test.yaml`. A non-zero `baml-cli test`
exit code SHALL fail the job and block merge. The captured CLI
output SHALL be uploaded under the `baml-test-results` artifact with
30-day retention. The same hard gate SHALL apply to manual
`workflow_dispatch` runs.

*(Consolidates the 1 ADDED Requirement from
`2026-07-12-baml-cli-test-ci-gate-v1`.)*

#### Scenario: Pull request runs BAML tests

- **GIVEN** a pull request targets `pick-4-biep-v1` or `main`
- **WHEN** GitHub Actions evaluates `.github/workflows/baml-test.yaml`
- **THEN** the `baml-test` job SHALL install the Python/uv/mise
      runtime and dependencies
- **AND** the job SHALL run `mise run baml:test` from
      `cianfhoghlaim/`
- **AND** `mise run baml:test` SHALL invoke `uv run baml-cli test`
- **AND** a non-zero `baml-cli test` exit code SHALL fail the job
      and block merge

#### Scenario: Push runs BAML tests

- **GIVEN** a commit is pushed to `pick-4-biep-v1` or `main`
- **WHEN** GitHub Actions evaluates `.github/workflows/baml-test.yaml`
- **THEN** the `baml-test` job SHALL run `mise run baml:test` from
      `cianfhoghlaim/`
- **AND** the workflow SHALL upload the captured CLI output under
      the `baml-test-results` artifact with 30-day retention

#### Scenario: Manual dispatch runs BAML tests

- **GIVEN** a maintainer starts `.github/workflows/baml-test.yaml`
      via `workflow_dispatch`
- **WHEN** the workflow runs
- **THEN** it SHALL execute the same `mise run baml:test` hard gate
      used for PRs and branch pushes

### Requirement: BAML v0.223 NCCA strand/outcome TypeBuilder — runtime mutation

The `cianfhoghlaim-baml-schemas` capability SHALL support runtime
injection of per-strand, per-outcome, per-curriculum-spec, and
per-assessment-component properties into the 4 canonical
NCCA-related BAML classes — `LearningOutcome`, `CurriculumStrand`,
`CurriculumSpecStrand`, and `AssessmentComponentStrand` — marked
`@@dynamic` per the BAML v0.221+ `TypeBuilder` spec, with the catalog
loaded at startup from the canonical YAML config file at
`baml/education/_shared/strand_catalog.yaml`. The
runtime helper SHALL be `build_ncca_strand_type_builder()` in
`baml/education/_shared/strand_type_builder.py`.

*(Consolidates the 1 ADDED Requirement from
`2026-07-12-baml-type-builder-ncca-v1`.)*

#### Scenario: 4 `@@dynamic` markers are present on the canonical NCCA classes

- **GIVEN** the file `baml/education/_shared/strand_outcome.baml`
- **WHEN** `grep -c "@@dynamic" baml/education/_shared/strand_outcome.baml`
      is run
- **THEN** the count is exactly 4
- **AND** the 4 markers are attached to the class declarations for
      `LearningOutcome`, `CurriculumStrand`, `CurriculumSpecStrand`,
      and `AssessmentComponentStrand`

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

- **GIVEN** a representative catalog (10 strands, 4 outcomes) is
      loaded from the YAML
- **WHEN** `build_ncca_strand_type_builder(catalog=catalog)` is called
      from Python
- **THEN** the helper walks the catalog and calls
      `tb.<ClassName>.add_property(prop_name, field_type)` for every
      per-strand / per-outcome / per-spec / per-component property
      declared in the YAML

#### Scenario: Operator can update the catalog without regen'ing the BAML schema

- **GIVEN** the operator has a new NCCA refresh (e.g. the 2027-07-01
      yearly update adds a new strand
      `LC Mathematics Strand 5: Discrete Mathematics`)
- **WHEN** the operator edits
      `baml/education/_shared/strand_catalog.yaml` to
      add the new strand + its properties (no `baml-cli generate`,
      no schema redeploy)
- **THEN** the next pipeline run that calls
      `build_ncca_strand_type_builder()` automatically picks up the
      new strand
- **AND** the LC BIEP Dagster assets that depend on this catalog
      continue to function without a release

#### Scenario: The 7 BIEP `lc_extraction/*.baml` files are untouched

- **GIVEN** the BIEP v1 owns the 7
      `baml/education/lc_extraction/*.baml` files
- **WHEN** `git diff --stat origin/pick-4-biep-v1 -- baml/education/lc_extraction/`
      is run after this change lands
- **THEN** the diff is empty
- **AND** the BIEP v1 Phase 4-5 DAG materialization is not blocked
      by this change

### Requirement: BAML Option-2 fix — 50 pre-existing `field: type` errors resolved

The `cianfhoghlaim-baml-schemas` capability SHALL have all 50
pre-existing BAML `field: type` parse diagnostics (captured in the
baseline at `openspec/changes/2026-07-13-baml-final-cleanup-v1/SCOPE_DECISION.md`)
resolved across the full `baml/` tree. `mise run
baml:generate` SHALL exit 0 against the current tree. The canonical
types `MarkingScheme`, `MarkingSchemeSec`, `MarkingSchemeStrand`,
`BilingualText`, `PastPaper`, `NCCAKeyCompetency`,
`CrossNationLearningOutcome` SHALL all be present in the generated
`baml_client/baml_client/types.py`. The 7 `lc_extraction/*.baml`
files SHALL report 0 Pydantic-style attribute lines AND the canonical
7 lc_extraction functions
(`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`,
`ExtractMarkingSchemeGuideline`, `ExtractStrandFromCatalog`,
`ExtractMarkingSchemeStrand`, `ExtractCelticCurriculumComparison`,
`ExtractSyllabusDiagram`) SHALL all remain present and produce the
same Pydantic output classes as before.

*(Consolidates the 1 ADDED Requirement from
`2026-07-13-fix-baml-50-out-of-scope-errors-v1`.)*

#### Scenario: baml:generate exits 0 against the full tree

- **GIVEN** the 2026-07-13-fix-baml-50-out-of-scope-errors-v1 change
      has landed
- **WHEN** `mise run baml:generate` is run from the repo root
- **THEN** it exits with code 0
- **AND** the `baml_client/` directory is regenerated successfully
      (14 files written to `baml/baml_client/`)
- **AND** the canonical types `MarkingScheme`, `MarkingSchemeSec`,
      `MarkingSchemeStrand`, `BilingualText`, `PastPaper`,
      `NCCAKeyCompetency`, `CrossNationLearningOutcome` are all
      present in the generated `baml_client/baml_client/types.py`

#### Scenario: full BAML tree compiles cleanly

- **GIVEN** the canonical 75-file `.baml` tree at
      `baml/`
- **WHEN** `uv run baml-cli generate --from baml_src`
      is invoked
- **THEN** the BAML parser reports 0 `error:` lines in its output
- **AND** the parser reports 0 `warning:` lines related to
      `field: type` syntax

#### Scenario: 7 lc_extraction/*.baml files are part of the fix scope

- **GIVEN** the user chose Option 2 from the SCOPE_DECISION.md (fix
      ALL 50 errors including the 7
      `baml/education/lc_extraction/*.baml` files)
- **WHEN** the BAML tree is grep'd for `field: type` patterns
      (excluding inside prompt blocks)
- **THEN** the 7 `lc_extraction/*.baml` files report 0
      Pydantic-style attribute lines
- **AND** the canonical 7 lc_extraction functions
      (`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`,
      `ExtractMarkingSchemeGuideline`, `ExtractStrandFromCatalog`,
      `ExtractMarkingSchemeStrand`, `ExtractCelticCurriculumComparison`,
      `ExtractSyllabusDiagram`) all remain present and produce the
      same Pydantic output classes as before

