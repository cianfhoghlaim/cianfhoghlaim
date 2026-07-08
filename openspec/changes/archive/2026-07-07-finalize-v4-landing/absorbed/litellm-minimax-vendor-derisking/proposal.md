# Change: litellm-minimax-vendor-derisking

> **Companion to `docs-skills-consolidation-pipeline/` and
> `four-directory-indexing-and-standards/`.** Those changes spend the
> MiniMax-M3 budget on indexing work. This change makes sure that
> budget isn't the only fallback for the platform — the `minimax`
> alias is a 3-key round-robin with a 4-tier paid fallback chain and
> a final local GGUF floor.

## Why

Before this change, every BAML function and opencode subagent that
wanted MiniMax-M3 hit one of two paths:

1. The **direct path** — `sruth/oideachais/baml_src/clients.baml::MiniMaxClient`
   pointed straight at `https://opencode.ai/zen/go/v1/messages` with
   a single `OPENCODE_GO_API_KEY`. No fallback. If the gateway
   changes terms, the key expires, the cap model shifts, or the
   opencode-go namespace is deprecated, **every BAML call stops**.

2. The **gateway path** — `baml_src/clients.baml::OpenCodeGo` /
   `LiteLLM` reached M3 only via the single `opencode-go/minimax-m3`
   entry in `infrastructure/stacks/litellm/config/config.yaml`,
   which has no `fallback_chain` and no slot rotation.

The user has **3 OPENCODE_GO_API_KEY slots** in `.env`
(`OPENCODE_GO_API_KEY_{0,1,2}`), each independent against the
5-hour rolling cap, but only **one** of them is wired anywhere.
The 2 unused slots represent ~67% of the per-window API budget
sitting idle.

## What Changes

### 1. LiteLLM gateway: 3 new slot entries + 1 new alias route

**`infrastructure/stacks/litellm/config/config.yaml`** gets:

- `opencode-go/minimax-m3-slot0`, `slot1`, `slot2` — three new
  `model_list` entries, each pointing `anthropic/minimax-m3` at
  the opencode-go gateway with a different
  `OPENCODE_GO_API_KEY_{0,1,2}` env var. Same model, three
  independent credentials, three independent 5-hour rolling caps.
- `minimax` alias — a new `model_name` that LiteLLM's `num_retries:
  3` cycles through automatically. Its `fallback_chain` is:
  1. `opencode-go/minimax-m3-slot0`
  2. `opencode-go/minimax-m3-slot1`
  3. `opencode-go/minimax-m3-slot2`
  4. `opencode-go/qwen3.7-max` (same gateway, different model — no
     key cap on the M3 slots)
  5. `opencode-go/kimi-k2.6` (same gateway, long-context generalist)
  6. `openai/glm-4.6` (Z.ai direct — fully independent provider)
  7. `local/math/qwen25-math` (llama-swap GGUF, runs on the MacBook
     M4 even with no internet)

  Failure isolation at every tier. The local GGUF is the
  "stay-alive" floor for emergency debugging; serious workloads
  will fail under it but the system never fully breaks.

### 2. LiteLLM stack env: inject the 3 keys

**`infrastructure/stacks/litellm/compose.yaml`** gains
`OPENCODE_GO_API_KEY_{0,1,2}` env vars (with `:-` fallbacks so
missing keys don't crash dev compose).

**`infrastructure/stacks/litellm/secrets.env`** gains
`OPENCODE_GO_API_KEY_0=infisical://dev-baile/opencode-go/api_key_slot0`
and 2 more — Locket pulls the actual secrets at container runtime.

**`infrastructure/stacks/litellm/README.md`** documents the 3 new
env vars in the env-var table.

### 3. BAML: add `MiniMax` client + deprecate direct `MiniMaxClient`

**`baml_src/clients.baml`** gains a new `client<llm> MiniMax` that
points at the gateway alias `minimax` (via `LITELLM_BASE_URL` +
`LITELLM_MASTER_KEY`). This is the recommended client for any BAML
function that wants M3 with vendor-de-risking.

**`sruth/oideachais/baml_src/clients.baml::MiniMaxClient`** is rewired
from "direct to opencode-go gateway with single key" to "via
gateway alias `minimax`" (same change). The single-key version is
preserved in git history for rollback.

### 4. opencode.json: new `litellm` provider, subagents route through it

**`opencode.json::provider`** gains a new `litellm` entry with
3 models: `minimax`, `extract`, `general` — all routing through
the LiteLLM gateway. Env-var interpolation: `LITELLM_MASTER_KEY` +
`LITELLM_BASE_URL`.

The 4 existing `minimax-coding-plan` (canonical + 3 slots)
providers are **kept** as low-level escape hatches for direct
gateway access (useful for debugging, useful if LiteLLM is down).

**`opencode.json::agent`** rewires:
- `orchestrator` → `litellm/minimax`
- `indexer-a`, `indexer-b`, `indexer-c` → `litellm/minimax`

Same model. The change is invisible to the user, but every call
now goes through the 7-tier fallback chain instead of a single
key with no fallback.

### 5. Dagster: `minimax_alias_liveliness` asset + `minimax_alias_health` check

New file `sruth/oideachais/dagster_defs/assets/llm_gateway_assets.py`
provides:

- `@asset(group_name="llm_gateway", compute_kind="litellm")` —
  `minimax_alias_liveliness` — hits `GET /health/liveliness` and
  `GET /v1/models` on the LiteLLM gateway, emits structured
  metadata (`gateway_live`, `alias_found`, `fallback_chain`,
  `fallback_chain_length`). No LLM credits burned.
- `@asset_check(asset=...)` — `minimax_alias_health` — returns
  `AssetCheckResult(passed=...)` based on: gateway is live AND the
  `minimax` alias is registered AND its `fallback_chain` has ≥ 1
  entry. Wired into `sruth/oideachais/dagster_defs/asset_checks.py` as
  part of `all_asset_checks`.

### 6. OpenSpec change artifacts

- This `proposal.md` + `tasks.md` + `specs/llm-gateway/spec.md`
- Cross-references: `infrastructure-stacks` (gateway stack),
  `agent-observability` (Langfuse traces), `oideachais-pipeline`
  (BAML routing), `data-engineering-pipeline-documentation` (this
  change is part of the 2026-06 consolidation)

## Impact

- **Affected specs:** none (new capability, not a modification of
  an existing one).
- **NEW spec:** `llm-gateway` — covers the 3-key rotation,
  fallback chain, and the asset_check contract.
- **Affected code:**
  - `infrastructure/stacks/litellm/config/config.yaml` (4 entries
    added)
  - `infrastructure/stacks/litellm/compose.yaml` (3 env vars)
  - `infrastructure/stacks/litellm/secrets.env` (3 Infisical URI
    references)
  - `infrastructure/stacks/litellm/README.md` (env-var table)
  - `baml_src/clients.baml` (1 new client)
  - `sruth/oideachais/baml_src/clients.baml` (1 client re-wired)
  - `opencode.json` (1 new provider, 4 agents re-pointed)
  - `sruth/oideachais/dagster_defs/assets/llm_gateway_assets.py` (new)
  - `sruth/oideachais/dagster_defs/assets/__init__.py` (import + register)
  - `sruth/oideachais/dagster_defs/asset_checks.py` (register the check)
  - `.infisical.env` (3 new vault entries)
- **Affected agent skills:** `.agents/skills/litellm/SKILL.md` —
  add a "MiniMax-M3 vendor-de-risking" section.
- **Affected CI:** none (config + dagster changes; no new tests
  required for the gateway change itself).
- **Affected workflows:** `mise dagster:oideachais` now shows the
  `llm_gateway` asset group with the new asset + check.

## Non-Goals

- This change does **not** rewrite any BAML extraction function.
  Existing `client<llm> LiteLLM` / `client<llm> ExtractEn` / etc.
  continue to route through the gateway as before.
- This change does **not** move the existing 3 user M3 keys
  (`OPENCODE_GO_API_KEY_{0,1,2}`) from `.env` to a different
  storage. The keys remain in `.env` (per the AGENTS.md "Strict
  Secret Hydration" rules). What changes is that the LiteLLM
  stack now *reads* them.
- This change does **not** add a new model. It only re-routes
  M3 calls and adds 6 fallback tiers. Adding new model
  registrations is a separate change.
- This change does **not** add spend-rate caps. LiteLLM's
  existing `general_settings` and per-key virtual keys cover
  that; the user already has the budget controls in place.
- This change does **not** retrain or fine-tune any model. The
  local qwen2.5-math GGUF in the fallback chain is the same
  Q4_K_M quantization already shipped via llama-swap.
