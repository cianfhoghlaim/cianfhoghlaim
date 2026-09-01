## ADDED Requirements

### Requirement: BAML source files MUST be regeneratable via `baml-cli generate`

The Cianfhoghlaim centralized-schema-registry capability MUST be
backed by BAML source files that are regeneratable via the
canonical `uv run baml-cli generate --from baml_src` command.
The regenerated client (Python + TypeScript) MUST be reachable
from runtime code.

#### Scenario: A new BAML function is added to baml_src

- **WHEN** a developer adds a new `function GenerateXxx(...) -> Yyy`
  to a `.baml` file in `baml_src/`
- **THEN** `uv run baml-cli generate --from baml_src` regenerates
  the Python + TypeScript clients
- **AND** the new function is reachable from runtime via
  `from baml_client import b; b.GenerateXxx(...)`

### Requirement: BAML 0.226.1+ parser MUST NOT reject any BAML source file

All `.baml` files in `baml_src/` MUST pass `uv run baml-cli check`
with 0 errors under BAML 0.226.1+.

#### Scenario: A reserved keyword is used as an identifier

- **WHEN** a developer adds a function with `prompt: string` as a
  parameter name (a reserved BAML keyword)
- **THEN** `uv run baml-cli check` SHALL report an error
  pointing at the line
- **AND** the developer SHALL rename `prompt` to `input` (or
  another non-reserved name) before the check passes

#### Scenario: A template variable is used outside its scope

- **WHEN** a function prompt body uses `{{ input }}` (where
  `input` is not in scope)
- **THEN** `uv run baml-cli check` SHALL report a warning
  suggesting `_`, `collection`, or `ctx`
- **AND** the developer SHALL rewrite the template variable to
  use one of the in-scope identifiers