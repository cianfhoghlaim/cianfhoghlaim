## MODIFIED Requirements

### Requirement: All BAML functions are client-qualified
Every BAML function in `oideachais/baml_src/*.baml` MUST be
associated with exactly one client from the canonical registry
`oideachais/baml_src/clients.baml`. The client is specified via
the `client <Name>` directive in the function signature.

#### Scenario: A BAML function is invoked from Python
- **WHEN** a Python file calls `b.SomeFunction(...)` and the
  function has `client <Name>` in its signature
- **THEN** `<Name>` MUST be declared in `clients.baml` as
  `client<llm> <Name> { ... }`
- **AND** the function MUST NOT be invoked with a client name that
  does not exist in the registry

#### Scenario: A BAML function signature is missing the client directive
- **WHEN** `baml-cli generate` runs and encounters a function
  without a `client <Name>` directive
- **THEN** the build SHALL fail with a clear error message
  pointing to the missing client

### Requirement: Inline `client<llm>` declarations are forbidden in non-registry files
Inline `client<llm> <Name> { ... }` blocks MUST NOT exist in
`oideachais/baml_src/*.baml` files other than `clients.baml`,
`clients_0.baml` (legacy Gemini clients), and `generators.baml`
(legacy). New canonical clients MUST be added to `clients.baml`.

#### Scenario: A duplicate client declaration is found
- **WHEN** two files declare the same client name (e.g. two
  `client<llm> Extractor { ... }` blocks)
- **THEN** the second declaration MUST be removed
- **AND** the canonical declaration MUST be in `clients.baml`
