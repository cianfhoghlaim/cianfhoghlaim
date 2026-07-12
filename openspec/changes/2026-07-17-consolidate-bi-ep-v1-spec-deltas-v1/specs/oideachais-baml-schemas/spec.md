# `oideachais-baml-schemas` MODIFIED — Consolidate 6 ADDED Requirements from 5 changes into 4 logical change groups

> Consolidates the 6 ADDED Requirements shipped across the 5 source
> changes (2 + 1 + 1 + 1 + 1) into 4 logical change groups (v0.212+
> migration / v0.223 test CI gate / v0.223 type-builder NCCA /
> Option-2 50-error fix). The logical-change labels correspond to the
> BAML v0.212 → v0.223 migration timeline + the post-migration
> Option-2 fix for the 50 remaining `field: type` errors.

## ADDED Requirements

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

The `oideachais-baml-schemas` capability SHALL support runtime
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

The `oideachais-baml-schemas` capability SHALL have all 50
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

## Cross-references *(unchanged — pre-existing)*

- [`baml_src/`](../../baml_src/) (the 8 BAML files)
- [`baml_client/`](../../baml_client/) (the auto-generated client)
- [`.agents/skills/baml/SKILL.md`](../../.agents/skills/baml/SKILL.md)
- [`baml_src/README.md`](../../baml_src/README.md) (the BAML file map)

## Logical-change history *(added by this consolidation change)*

| Logical change | Source change(s) | Description |
|:--|:--|:--|
| **v0.212+ migration** | `2026-07-10-fix-baml-codegen-v4-syntax-v1` | Canonical `field Type` syntax migration + `migrate-baml-syntax.py` helper (2 ADDEDs combined) |
| **v0.223 test CI gate** | `2026-07-12-baml-cli-test-ci-gate-v1` | `baml-cli test` as a hard GitHub Actions CI gate |
| **v0.223 type-builder NCCA** | `2026-07-12-baml-type-builder-ncca-v1` | Runtime `@@dynamic` + `TypeBuilder` for the 4 NCCA canonical classes |
| **Option-2 50-error fix** | `2026-07-13-fix-baml-50-out-of-scope-errors-v1` | Resolve all 50 pre-existing `field: type` errors (incl. 7 lc_extraction files) |

**Note**: `2026-07-13-baml-final-cleanup-v1` is the `baml_client`
generator cleanup (single `minimax-m3` text generator + 2 local vision
generators active; the historical 8-generator layout preserved as a
comment block) — it lives in the `clients.baml` file and is
**not** part of this consolidation (it doesn't touch the BAML schema
grammar or the `baml_cli test` flow; it's a generator wiring
change). See `openspec/changes/2026-07-13-baml-final-cleanup-v1/specs/oideachais-baml-schemas/spec.md`
for the standalone delta.

**Summary**: 6 ADDED Requirements from 5 source changes consolidated
into 4 logical change groups.