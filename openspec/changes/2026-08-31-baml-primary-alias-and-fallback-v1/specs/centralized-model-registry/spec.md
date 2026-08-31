# centralized-model-registry — Delta for BAML Primary Alias + Fallback Chains

## ADDED Requirements

### Requirement: BAML clients.baml SHALL declare the Primary alias

The `baml_src/clients.baml` SHALL declare a `client<llm> Primary`
that reads `MODEL_BASE_URL` / `MODEL_API_KEY` / `MODEL_PRIMARY` from
env vars. Default behaviour: routes to MiniMax M3.

#### Scenario: Primary routes to MiniMax by default

- **WHEN** `MODEL_BASE_URL=https://api.minimax.io/v1` + `MODEL_API_KEY=...` + `MODEL_PRIMARY=minimax-m3`
- **THEN** the `Primary` client routes to MiniMax M3

#### Scenario: Primary routes to Gemma 4 when env is overridden

- **WHEN** `MODEL_BASE_URL=http://host.docker.internal:8888/v1/` + `MODEL_API_KEY=...` + `MODEL_PRIMARY=unsloth/gemma-4-26B-A4B-it-GGUF`
- **THEN** the `Primary` client routes to Unsloth Studio Gemma 4 26B-A4B

### Requirement: BAML functions SHALL declare a fallback chain

The system MUST require every BAML function in `baml_src/**`
(excluding the 6 exception list functions: `TestMock`,
`GaeilgeLCClient`, the 5 `tuatha_media_intel` helpers) to declare a
`fallback` chain of length ≥ 2 that includes at least one of:

- `UnslothGemma4` (Tier 2 local)
- `VertexGemini35Flash` (Tier 1 Google Vertex)
- `AIStudioGemini35Flash` (Tier 1 Google AI Studio)

#### Scenario: BIEP v3 function has explicit fallback chain

- **WHEN** `ExtractCurriculumSyllabus` is invoked
- **THEN** the function tries `Primary` first
- **AND** falls back to `UnslothGemma4` on failure
- **AND** falls back to `VertexGemini35Flash` on second failure

#### Scenario: GaeilgeLC functions are exempt

- **WHEN** `GaeilgeLCClient` is used (the Modern Irish-language path)
- **THEN** the function does NOT need a `fallback` block
- **BECAUSE** the per-function `client "GaeilgeLCClient"` override
  is the canonical pattern (knob b)

### Requirement: mise run baml:switch-primary SHALL exist

The mise.toml MUST declare `[tasks."baml:switch-primary"]` that
updates `MODEL_BASE_URL` + `MODEL_API_KEY` + `MODEL_PRIMARY` in
`.infisical.env` via `mise env set`. Accepts a `model` arg from
the choices `minimax-m3` | `gemma-4-26b-a4b` | `gemini-3.5-flash`.

#### Scenario: Switch primary to Gemma 4

- **WHEN** the operator runs `mise run baml:switch-primary --model gemma-4-26b-a4b`
- **THEN** `MODEL_PRIMARY` is updated to `unsloth/gemma-4-26B-A4B-it-GGUF`
- **AND** `MODEL_BASE_URL` is updated to `http://host.docker.internal:8888/v1/`
- **AND** the operator is prompted to restart running BAML daemons

### Requirement: scripts/baml_audit_fallbacks.py SHALL exist

The system MUST provide `scripts/baml_audit_fallbacks.py` script that
fails (exit 1) if any non-exception BAML function is missing a
`fallback` block. Wired via `[tasks."lint:baml-fallbacks"]`.

#### Scenario: Audit fails on missing fallback

- **WHEN** `baml_src/foo.baml` declares `function Foo(...) -> X { client "Primary" prompt #"..." }`
- **AND** the function has no `fallback` block
- **THEN** `uv run python scripts/baml_audit_fallbacks.py --strict` exits 1
- **AND** the audit output reports `baml_src/foo.baml:42: 'Foo' missing fallback chain`