## MODIFIED Requirements
### Requirement: Streaming extraction

The system SHALL support `b.stream.<Function>(...)` for partial
streaming + `stream.get_final_response()` for the typed final result.

#### Scenario: Streamed function call

- **GIVEN** a BAML function with `@stream.not_null` (or `@stream.done`
  / `@stream.with_state`)
- **WHEN** the user iterates over the `BamlStream` returned by
  `b.stream.<Function>(...)`
- **THEN** partial chunks are yielded in real time
- **AND** `stream.get_final_response()` returns the typed final object
  once the LLM finishes

### Requirement: BAML 0.221+ streaming semantic-attributes on Extract* functions

The system SHALL annotate all 121 `Extract*` functions in
`cianfhoghlaim/baml/` (excluding the 5 in `education/lc_extraction/`
owned by the BIEP v1 change + the 5 in `celtic/_archive/`) with the
3 BAML 0.221+ streaming semantic-attributes, applied at the canonical
class level (per the BAML docs: "The return type of a function is not
affected by streaming attributes!").

The 3 attributes are:
1. `@@stream.done` (class-level, 2 `@`s) on every class returned by an
   `Extract*` function — makes the class stream atomically.
2. `@stream.not_null` (field-level, 1 `@`) on the discriminator field
   of classes that have one (e.g. `MarkingSchemeSec.subject`,
   `CurriculumSpecStrand.title`, all 8 `<Subject>QuestPack.title` +
   `subject`).
3. `@stream.with_state` (field-level, 1 `@`) on the large list field
   of classes that return one (e.g. `MarkingSchemeSec.markingPoints`,
   `CurriculumSpecStrand.strands`, all 8 `<Subject>QuestPack.items`).

#### Scenario: All Extract* return classes are atomic

- **GIVEN** a class `X` is the return type of one or more `Extract*`
  functions in `cianfhoghlaim/baml/`
- **WHEN** the BAML source is parsed
- **THEN** the class `X` body SHALL contain `@@stream.done`
- **AND** the partial_types Pydantic class for `X` SHALL have no
  optional fields (per the BAML 0.221+ type transformation table)

#### Scenario: Discriminator fields stream after the discriminator lands

- **GIVEN** a class `X` with a discriminator field `d` (e.g.
  `MarkingSchemeSec.subject`, `CurriculumSpecStrand.title`,
  `<Subject>QuestPack.title`)
- **WHEN** the BAML source is parsed
- **THEN** the field `d` SHALL be annotated with `@stream.not_null`
- **AND** the partial_types Pydantic class for `X.d` SHALL be marked
  as non-nullable

#### Scenario: Large list fields emit completion state

- **GIVEN** a class `X` with a large list field `l` (e.g.
  `MarkingSchemeSec.markingPoints`, `CurriculumSpecStrand.strands`,
  `<Subject>QuestPack.items`)
- **WHEN** the BAML source is parsed
- **THEN** the field `l` SHALL be annotated with `@stream.with_state`
- **AND** the partial_types Pydantic class for `X.l` SHALL be wrapped
  in `StreamState[Partial[T]]` with `state: "Pending" | "Incomplete" | "Complete"`

#### Scenario: Streaming attribute coverage

- **GIVEN** all 121 in-scope `Extract*` functions
- **WHEN** the streaming attributes are counted
- **THEN** there SHALL be >= 70 `@stream.*` attribute matches
  (achieved: 135 = 97 `@@stream.done` + 24 `@stream.not_null` +
  14 `@stream.with_state`)
