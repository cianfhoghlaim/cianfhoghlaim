# Spec delta — `british-isles-education-pipeline` — ADDED Requirement: BIEP BAML surface drift fix

> This file is the spec delta for the change
> `2026-07-14-fix-foundation-v7-flattening-and-baml-drift-v1`. Apply by
> merging the ADDED Requirements block below into
> `openspec/specs/british-isles-education-pipeline/spec.md`.

## ADDED Requirements

### Requirement: BIEP BAML surface drift fix (5 categories)

The system SHALL compile the full BIEP BAML surface without errors. The
following 5 drift categories SHALL be eliminated:

1. **Default-value class fields** SHALL NOT exist in `baml_src/`. Class
   field declarations SHALL NOT carry `= "<value>"` syntax. Optional
   fields SHALL use the `field type?` syntax instead.
2. **Unterminated strings** SHALL NOT exist in any `@description`,
   `prompt`, or `args { ... }` block.
3. **Test block keyword** SHALL be PascalCase `Test` (not `test`). BAML
   0.222+ requires PascalCase.
4. **Function block `client` field** SHALL be present on every `function`
   block. The `client <Name>` line SHALL appear before `prompt #"..."`.
5. **String-literal type references** SHALL NOT exist in class field
   type annotations. Use bare class references (resolved by the BAML
   type system) instead.

#### Scenario: baml-cli generate succeeds

- **WHEN** the user runs `mise run baml:generate` (or `cic:baml:generate`)
- **THEN** BAML SHALL generate the Python client into `baml_client/` without error
- **AND THEN** exit 0

#### Scenario: baml-cli test passes

- **WHEN** the user runs `mise run baml:test` (or `cic:baml:test`)
- **THEN** all `Test PascalCaseDescription { ... }` blocks SHALL execute
- **AND THEN** all assertions SHALL pass
- **AND THEN** exit 0

#### Scenario: BIEP client declarations

- **WHEN** the BIEP v3 hardening change (`2026-08-07-biep-v3-hardening-v1`) ships
- **THEN** the BIEP canonical 3 clients (`BIEPV3Extract`,
      `BIEPV3ExtractStrong`, `BIEPV3Vision`) SHALL each declare a distinct
      model: `gemma-3-4b-it`, `qwen3-vl-8b-it`,
      `qwen3-vl-8b-it-via-llama-swap` respectively
- **AND THEN** the legacy `ExtractEn` / `ExtractEnStrong` aliases MAY collapse to
      a single model (per the BIEP v3 consolidation rationale)

#### Scenario: No `baml_src` field references latent missing types

- **WHEN** any `.baml` file references a class (e.g., `GradeDescriptor`)
- **THEN** that class SHALL be either declared in the same file or
      imported from `_shared/` (no string-literal type references)
