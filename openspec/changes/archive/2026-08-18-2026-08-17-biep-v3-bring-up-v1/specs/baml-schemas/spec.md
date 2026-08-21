# baml-schemas

## ADDED Requirements

### Requirement: BAML stub-prompt lint invariant

The system SHALL fail `mise run lint:baml-stub-prompts` if any
BAML function body in `baml_src/**/*.baml` is the literal string
`"Auto-generated extraction prompt."` (the 832-of-838 stub class
per the `centralized-schema-registry` spec).

The reason: per the `2026-08-10-baml-extraction-completion-v1` change
proposal, 832 of 838 BAML classes have stub prompts. Closing this
gap requires (a) replacing stubs with real prompts and (b) a lint
gate that prevents re-introduction of the stub pattern. This
requirement adds the lint gate (the `baml-extraction-completion-v1`
change is archived as part of Mega-1 Phase 2).

The lint scans `baml_src/**/*.baml` for the literal substring
`"Auto-generated extraction prompt."` in any `prompt #"..."` block.
Test-only fixtures under `baml_src/**/_test*.baml` are exempt.

#### Scenario: Developer adds a new stub prompt

- **WHEN** a developer adds:
  ```baml
  function ExtractNewFunction(text: string) -> NewType {
    prompt #"Auto-generated extraction prompt."
  }
  ```
- **THEN** `mise run lint:baml-stub-prompts` exits 1 with
  `baml_src/.../file.baml:<line>: stub prompt detected — replace with a real prompt per the centralized-schema-registry spec`

#### Scenario: Real prompt passes the lint

- **WHEN** the function body has a real prompt like:
  ```baml
  function ExtractChemSyllabus(text: string, source_pdf: string) -> ChemSyllabus {
    prompt #"
      {{ ctx.output_format }}
      Extract from: {{ text }}
    "#
  }
  ```
- **THEN** the lint exits 0

#### Scenario: Test fixture with stub prompt is exempt

- **GIVEN** `baml_src/education/lc_extraction/_test_chemistry_stub.baml`
  contains a stub prompt for testing the BAML test harness
- **WHEN** `mise run lint:baml-stub-prompts` runs
- **THEN** the lint exits 0 (the file matches `_test*.baml` and is
  exempt)