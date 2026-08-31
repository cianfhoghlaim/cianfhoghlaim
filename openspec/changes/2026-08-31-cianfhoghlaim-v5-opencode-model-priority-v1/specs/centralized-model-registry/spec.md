# centralized-model-registry — Delta for v5 OpenCode + Model Priority

## ADDED Requirements

### Requirement: MODEL_REGISTRY SHALL include Gemma 4 family entries

The `MODEL_REGISTRY` SHALL include the following Gemma 4 entries
(text_llm family + ocr_vision family):

- `gemma-4-26b-a4b` (text_llm/fallback, unsloth_studio backend,
  hackathon profile)
- `gemma-4-e4b` (text_llm/fallback_light, unsloth_studio backend,
  hackathon profile)
- `gemma-3-27b-it` (text_llm/local_fallback, unsloth_studio backend,
  dev profile)
- `gemma-2-9b` (text_llm/local_fallback_old, unsloth_studio backend,
  dev profile)
- `gemma-4-26b-a4b-vision` (ocr_vision/default, llama_swap backend,
  hackathon profile)
- `gemma-4-12b-vision` (ocr_vision/vision_medium, llama_swap backend,
  hackathon profile)
- `gemma-4-e4b-vision` (ocr_vision/vision_light, llama_swap backend,
  hackathon profile)
- `gemma-3-12b-vision` (ocr_vision/vision_prior_gen, llama_swap backend,
  dev profile)

Each entry SHALL have `available=True` for hackathon profile entries
and the 3 dev benchmark entries.

#### Scenario: Gemma 4 entries resolve via model_for

- **WHEN** `model_for("text_llm", "fallback")` is called
- **THEN** it returns `"gemma-4-26b-a4b"`
- **AND** the entry has `profile="hackathon"`, `backend="unsloth_studio"`,
  `litellm_alias="openai/unsloth/gemma-4-26b-a4b"`

#### Scenario: Gemma 4 vision resolves via model_for

- **WHEN** `model_for("ocr_vision", "default")` is called
- **THEN** it returns `"gemma-4-26b-a4b-vision"`
- **AND** the entry has `backend="llama_swap"`,
  `litellm_alias="openai/gemma-4-26b-a4b-vision"`

### Requirement: MODEL_REGISTRY SHALL include Gemini 3.5 family entries

The `MODEL_REGISTRY` SHALL include the following Gemini 3.5 entries
(text_llm family):

- `gemini-3.5-flash` (text_llm/default, vertex backend, hackathon profile)
- `gemini-3.5-flash-aistudio` (text_llm/aistudio, aistudio backend,
  hackathon profile)
- `gemini-3.5-flash-lite` (text_llm/lite, aistudio backend, hackathon profile)
- `gemini-2.5-flash` (text_llm/alt, vertex backend, both profiles)
- `gemini-embedding-2-preview` (text_llm/embedder, aistudio backend,
  hackathon profile)

Each entry SHALL have `available=True`.

#### Scenario: Gemini 3.5 flash resolves via model_for

- **WHEN** `model_for("text_llm", "default")` is called with
  `MODEL_PROFILE=hackathon`
- **THEN** it returns `"gemini-3.5-flash"` (Vertex primary)
- **AND** `model_for("text_llm", "aistudio")` returns
  `"gemini-3.5-flash-aistudio"`

### Requirement: ModelRegistryEntry SHALL have a profile field

`ModelRegistryEntry` SHALL include a new field `profile:
ModelProfile = "hackathon" | "dev" | "both"`. Default is `"both"`.
The `ModelProfile` literal type SHALL be exported from
`meaisinfhoghlaim.models.model_registry`.

The profile field is the gating mechanism for the `public_model_roster`
+ `MODEL_PROFILE` env var (mirroring the `gemini_hackathon` registry
pattern, lifted to cianfhoghlaim).

#### Scenario: Profile filter excludes dev-only entries

- **WHEN** `MODEL_PROFILE=hackathon` is set
- **AND** the operator runs
  `MODEL_REGISTRY.filter(profile="hackathon")`
- **THEN** the result SHALL exclude `kimi-k2.6`, `glm-5.1`,
  `mimo-v2.5`, `deepseek-v4-flash` (all `"dev"`-profile entries)
- **AND** the result SHALL include `minimax-m3` (`"both"`)
- **AND** the result SHALL include `gemma-4-26b-a4b` (`"hackathon"`)

#### Scenario: Profile defaults

- **WHEN** a new `ModelRegistryEntry(...)` is constructed without
  the `profile` keyword
- **THEN** the default is `"both"`

### Requirement: qwen3 token-plan entries SHALL be tombstoned

The following qwen3 token-plan entries SHALL have `available=False`
plus a redirect note in the `notes` field pointing at the Gemma 4
family as the replacement:

- `qwen3.7-plus` (text_llm/token_plan_primary) — redirect to
  `gemma-4-26b-a4b`
- `qwen3-coder-next` (text_llm/token_plan_coding) — redirect to
  `gemma-4-e4b`
- `qwen3-coder-plus` (text_llm/token_plan_coding_strong) — redirect
  to `gemma-4-26b-a4b`
- `qwen3.6-27b-mtp` (text_llm/token_plan_mtp) — redirect to
  `gemma-4-26b-a4b`

The entries SHALL remain in the registry for backward compatibility
but SHALL NOT be reachable from `model_for(...)` returns for active
use.

#### Scenario: Tombstoned qwen entry does not resolve

- **WHEN** `model_for("text_llm", "token_plan_primary")` is called
- **THEN** it raises `ValueError("Entry is tombstoned: qwen3.7-plus")`
  OR returns the entry with `available=False` (caller checks)

#### Scenario: Existing qwen references raise registry audit

- **WHEN** any `agents/`, `baml_src/`, `notebooks/`, `web/`,
  `orchestration/`, `spaces/`, or `meaisinfhoghlaim/` file contains
  `qwen3.7-plus`, `qwen3-coder-next`, `qwen3-coder-plus`, or
  `qwen3.6-27b-mtp` as a hardcoded string (not via `model_for(...)`)
- **THEN** `mise run lint:registry` exits 1 with the file:line

### Requirement: opencode.json SHALL declare both MiniMax v1 and v2 providers

The project-level `opencode.json` SHALL declare both
 provider
entries:

- `minimax-coding-plan` — uses `{env:MINIMAX_API_KEY}` (key #1,
  shared with research / orchestrator / agent-platform /
  data-platform / infrastructure / mise / proposal-author /
  dev-env-demo)
- `minimax-coding-plan-v2` — uses `{env:MINIMAX_API_KEY_V2}`
  (key #2, used by `build` + `plan` agents)

The `agent.build.model` SHALL be `"minimax-coding-plan-v2/MiniMax-M3"`
and the `agent.plan.model` SHALL also be
`"minimax-coding-plan-v2/MiniMax-M3"`.

#### Scenario: Build agent routes to v2 provider

- **WHEN** the operator invokes `opencode` with the default
  `build` agent
- **THEN** the request is sent to the `minimax-coding-plan-v2`
  provider
- **AND** the provider uses `MINIMAX_API_KEY_V2` from the env

#### Scenario: Plan agent routes to v2 provider

- **WHEN** the operator invokes `opencode` with the `plan` agent
- **THEN** the request is sent to the `minimax-coding-plan-v2`
  provider
- **AND** the request is denied (`edit: deny` permission holds)

### Requirement: opencode.json SHALL NOT declare qwen or litellm_local providers

The project-level `opencode.json` SHALL NOT declare:

- `provider.qwen` — removed entirely (DASHSCOPE token plan deprioritised)
- `provider["litellm_local"]` — removed entirely (Unsloth Studio
  Gemma 4 + Vertex/AI-Studio Gemini 3.5 covers all fallbacks)

#### Scenario: Project config has no qwen provider

- **WHEN** the operator runs
  `jq '.provider | keys' opencode.json`
- **THEN** the output SHALL NOT include `"qwen"` or `"litellm_local"`

### Requirement: opencode.json SHALL declare the unsloth-studio Gemma 4 family

The project-level `opencode.json` SHALL declare the
`unsloth-studio` provider with the following Gemma 4 model entries:

- `gemma-4-26b-a4b` — `unsloth/gemma-4-26B-A4B-it-GGUF`
- `gemma-4-e4b` — `unsloth/gemma-4-E4B-it-GGUF`
- `gemma-3-27b-it` — `unsloth/gemma-3-27B-it-GGUF` (dev benchmark)

The `agent.notebooks.model` SHALL be
`"unsloth-studio/gemma-4-26b-a4b"` and the `agent.deep-cuts.model`
SHALL also be `"unsloth-studio/gemma-4-26b-a4b"`.

#### Scenario: Notebooks agent uses Gemma 4

- **WHEN** the `notebooks` subagent is invoked
- **THEN** the request is sent to the `unsloth-studio` provider
- **AND** the model string is `gemma-4-26b-a4b`