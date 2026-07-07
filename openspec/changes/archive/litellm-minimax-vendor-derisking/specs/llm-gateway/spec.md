## ADDED Requirements

### Requirement: MiniMax-M3 Slot Rotation
The system SHALL register three independent `model_list` entries in the LiteLLM gateway config (`opencode-go/minimax-m3-slot0`, `slot1`, `slot2`) so that each entry binds the same `anthropic/minimax-m3` model to a distinct `OPENCODE_GO_API_KEY_{0,1,2}` credential. Each slot SHALL correspond to an independent 5-hour rolling cap at the upstream gateway.

#### Scenario: Three distinct slots
- **GIVEN** the LiteLLM gateway is running with the canonical config
- **WHEN** the model list is enumerated via `GET /v1/models`
- **THEN** the response SHALL include three entries whose `id` matches `opencode-go/minimax-m3-slot{0,1,2}`
- **AND** each entry's `model_info.litellm_params.api_key` SHALL resolve from a different `OPENCODE_GO_API_KEY_<n>` env var (verified by inspecting the env-var interpolation in the YAML)

#### Scenario: Key uniqueness requirement
- **GIVEN** three `OPENCODE_GO_API_KEY_{0,1,2}` env vars
- **WHEN** the gateway starts
- **THEN** the system SHALL emit a warning if any two of the three resolve to the same string (catches copy-paste typos that would silently double-charge a single key)
- **AND** the warning SHALL list which slots collide

### Requirement: MiniMax Alias Fallback Chain
The system SHALL register a `minimax` alias route in the LiteLLM gateway config whose `fallback_chain` contains at least 4 paid tiers and 1 local floor, in this order: `opencode-go/minimax-m3-slot0`, `slot1`, `slot2`, `opencode-go/qwen3.7-max`, `opencode-go/kimi-k2.6`, `openai/glm-4.6`, `local/math/qwen25-math`.

#### Scenario: First failure auto-falls-through
- **GIVEN** the `minimax` alias is called and `opencode-go/minimax-m3-slot0` returns HTTP 429
- **WHEN** LiteLLM's `num_retries: 3` cycles through the chain
- **THEN** the next attempt SHALL target `opencode-go/minimax-m3-slot1`
- **AND** the original 429 SHALL be recorded in the Langfuse trace with `metadata.fallback_triggered = true`

#### Scenario: Gateway fully down
- **GIVEN** the `minimax` alias is called
- **AND** `opencode-go/minimax-m3-slot{0,1,2}` all return network errors
- **AND** `opencode-go/qwen3.7-max` and `opencode-go/kimi-k2.6` also return network errors
- **WHEN** LiteLLM's chain continues
- **THEN** the next attempt SHALL target `openai/glm-4.6` (Z.ai direct — fully independent provider)
- **AND** the next attempt after that SHALL target `local/math/qwen25-math` (llama-swap GGUF on the MacBook M4, runs offline)

#### Scenario: Local floor returns degraded response
- **GIVEN** the `minimax` alias is called
- **AND** the only remaining model is `local/math/qwen25-math` (a 7B math-tuned GGUF)
- **WHEN** the request lands on the local floor
- **THEN** the response SHALL succeed
- **AND** the Langfuse trace metadata SHALL include `degraded_floor_used = true` and `model_used = "local/math/qwen25-math"`
- **AND** the operator SHALL be alerted (the trace lands on a `degraded_floor` dashboard panel)

### Requirement: Vendor-De-Risking Asset Check
The system SHALL provide a Dagster `@asset_check` named `minimax_alias_health` (group `llm_gateway`, bound to the `minimax_alias_liveliness` asset) that returns `AssetCheckResult(passed=True)` iff the LiteLLM gateway `/health/liveliness` endpoint returns 200 AND the `minimax` alias is registered with a `fallback_chain` of length ≥ 1.

#### Scenario: Healthy
- **GIVEN** the LiteLLM stack is up at `LITELLM_BASE_URL`
- **AND** the gateway config contains the `minimax` alias with 7 fallback entries
- **WHEN** the asset check runs
- **THEN** it returns `AssetCheckResult(passed=True)`
- **AND** the metadata includes the full `fallback_chain` as JSON

#### Scenario: Gateway down
- **GIVEN** the LiteLLM stack is NOT running
- **WHEN** the asset check runs
- **THEN** it returns `AssetCheckResult(passed=False, metadata={"error": "LiteLLM gateway at <url> is not responding"})`

#### Scenario: Alias missing
- **GIVEN** the gateway is up
- **AND** the `minimax` alias is missing from the config (e.g. someone removed the entry)
- **WHEN** the asset check runs
- **THEN** it returns `AssetCheckResult(passed=False, metadata={"error": "Alias `minimax` is not registered ..."})`
- **AND** the Dagster UI badge turns red

#### Scenario: Missing master key
- **GIVEN** `LITELLM_MASTER_KEY` is not set
- **WHEN** the asset check runs
- **THEN** it returns `AssetCheckResult(passed=False, metadata={"error": "LITELLM_MASTER_KEY is not set ..."})`

### Requirement: BAML MiniMax Client
The system SHALL expose a BAML `client<llm> MiniMax` in `baml_src/clients.baml` that points at the LiteLLM gateway alias `minimax` (via `LITELLM_BASE_URL` + `LITELLM_MASTER_KEY`).

#### Scenario: BAML function uses MiniMax client
- **GIVEN** a BAML function `Foo(x: string) -> Bar` declared as `client MiniMax`
- **WHEN** the function is called at runtime
- **THEN** the BAML runtime SHALL route the call through the LiteLLM gateway
- **AND** the actual model that answers SHALL be one of the 7 entries in the `minimax` fallback chain (whichever is currently healthy)
- **AND** the Langfuse trace SHALL attribute the call to the `minimax` alias

#### Scenario: oideachais MiniMaxClient rewired
- **GIVEN** `sruth/oideachais/baml_src/clients.baml::MiniMaxClient`
- **WHEN** the file is read
- **THEN** it SHALL point at the gateway (not directly at opencode-go)
- **AND** the file SHALL carry a comment noting the previous direct-to-gateway version is preserved in git history

### Requirement: opencode.json Subagent Routing
The system SHALL register a `litellm` provider in `opencode.json` and SHALL re-point the `orchestrator`, `indexer-a`, `indexer-b`, and `indexer-c` agents to `litellm/minimax`. The 4 pre-existing `minimax-coding-plan{,-0,-1,-2}` providers SHALL be retained as low-level escape hatches.

#### Scenario: Subagent hits minimax via LiteLLM
- **GIVEN** `indexer-a` is dispatched with a task
- **WHEN** the agent issues a chat-completion request
- **THEN** the request SHALL target the URL in `{env:LITELLM_BASE_URL}`
- **AND** the request SHALL include the header `Authorization: Bearer {env:LITELLM_MASTER_KEY}`

#### Scenario: Escape hatch survives LiteLLM outage
- **GIVEN** the LiteLLM stack is fully down
- **WHEN** the user manually switches the `orchestrator` model to `minimax-coding-plan/MiniMax-M3` (bypassing the alias)
- **THEN** the request SHALL still reach the opencode-go gateway directly via the canonical key
- **AND** no fallback is available (this is the documented escape hatch)
