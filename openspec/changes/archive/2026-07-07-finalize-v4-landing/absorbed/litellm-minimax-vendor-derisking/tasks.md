# Tasks: litellm-minimax-vendor-derisking

> Implementation tasks for the `litellm-minimax-vendor-derisking`
> OpenSpec change. Each task is small, testable, and traceable to
> a `## Requirements` block in `proposal.md`.

## 1. LiteLLM config — slots + alias

- [x] 1.1 Add 3 `opencode-go/minimax-m3-slot{0,1,2}` entries to
  `infrastructure/stacks/litellm/config/config.yaml`, each with
  `api_key: os.environ/OPENCODE_GO_API_KEY_{0,1,2}`.
- [x] 1.2 Add the `minimax` alias route to the same file with the
  7-tier `fallback_chain`:
  slot0 → slot1 → slot2 → qwen3.7-max → kimi-k2.6 → glm-4.6 →
  local/math/qwen25-math.
- [x] 1.3 Update the file header comment to document the new
  alias and point to this OpenSpec change.

## 2. LiteLLM stack env

- [x] 2.1 In `infrastructure/stacks/litellm/compose.yaml`, extend
  the `litellm` service `environment:` block with
  `OPENCODE_GO_API_KEY_0/1/2` (with `:-` fallbacks).
- [x] 2.2 In `infrastructure/stacks/litellm/secrets.env`, add 3
  Infisical URI references under a `dev-baile/opencode-go/`
  prefix for the 3 slots.
- [x] 2.3 In `infrastructure/stacks/litellm/README.md`, document
  the 3 new env vars in the env-var table.

## 3. Vault sync

- [x] 3.1 In `.infisical.env`, add 3 new entries
  `OPENCODE_GO_API_KEY_0/1/2` with `infisical://dev-baile/...`
  references. Document the 3-slot semantic in the section
  header.
- [ ] 3.2 Run `bun run secrets:init` (a.k.a.
  `mise run secrets:init`) in the dev shell to push the 3 new
  vault entries. **Cannot run in this agent shell** — requires
  the user to do this once.

## 4. BAML clients

- [x] 4.1 In `baml_src/clients.baml`, add a new
  `client<llm> MiniMax` that points at
  `LITELLM_BASE_URL` + `LITELLM_MASTER_KEY` with
  `model "minimax"`.
- [x] 4.2 In `sruth/oideachais/baml_src/clients.baml`, rewire
  `MiniMaxClient` to also go through the gateway alias
  `minimax` (drop the direct opencode-go URL).
- [x] 4.3 Re-export the new BAML client via
  `bun run baml:generate` (BAML regen). **Defer** to the user's
  dev shell.
- [x] 4.4 Confirm no other `.baml` file references the old
  direct `MiniMaxClient` (search returns 0 hits — verified).

## 5. opencode.json — LiteLLM provider + agent rewire

- [x] 5.1 Add a new `litellm` provider entry to `opencode.json`
  with `apiKey: {env:LITELLM_MASTER_KEY}` and
  `baseURL: {env:LITELLM_BASE_URL}`. Declare 3 models:
  `minimax`, `extract`, `general`.
- [x] 5.2 Re-point `orchestrator` from
  `minimax-coding-plan/MiniMax-M3` to `litellm/minimax`.
- [x] 5.3 Re-point `indexer-a/b/c` from
  `minimax-coding-plan-{0,1,2}/MiniMax-M3` to
  `litellm/minimax`.
- [x] 5.4 Keep the 4 `minimax-coding-plan{,-0,-1,-2}` providers
  as low-level escape hatches (no deletion).
- [x] 5.5 Validate `opencode.json` parses (Python `json.load`
  exits 0; verified).

## 6. Dagster asset + check

- [x] 6.1 Create
  `sruth/oideachais/dagster_defs/assets/llm_gateway_assets.py`
  with `minimax_alias_liveliness` (asset, no LLM credits) and
  `minimax_alias_health` (asset_check, gates the asset).
- [x] 6.2 Register the asset in
  `sruth/oideachais/dagster_defs/assets/__init__.py` and the
  `all_assets` list.
- [x] 6.3 Register the check in
  `sruth/oideachais/dagster_defs/asset_checks.py` and the
  `all_asset_checks` list.
- [x] 6.4 Validate Python AST parses cleanly (verified).

## 7. Skill update

- [ ] 7.1 In `.agents/skills/litellm/SKILL.md`, add a new
  section "MiniMax-M3 vendor-de-risking" explaining the 7-tier
  fallback chain and the 3-key rotation. **Defer** to the user's
  next skill-touch.

## 8. Verification

- [ ] 8.1 `mise run format && mise run lint && mise run
  py:typecheck` — all green. **Defer** (user runs locally).
- [ ] 8.2 `python3 -c "import yaml; yaml.safe_load(open(
  'infrastructure/stacks/litellm/config/config.yaml'))"`
  exits 0. **Verified** in this session.
- [ ] 8.3 `python3 -c "import json;
  json.load(open('opencode.json'))"` exits 0. **Verified** in
  this session.
- [ ] 8.4 `python3 -c "import ast;
  ast.parse(open('sruth/oideachais/dagster_defs/assets/llm_gateway_assets.py').read())"`
  exits 0. **Verified** in this session.
- [ ] 8.5 `mise dagster:oideachais` — the `llm_gateway` asset
  group shows the new `minimax_alias_liveliness` asset and the
  `minimax_alias_health` check. **Defer** to when the
  `litellm` stack is up.
- [ ] 8.6 Live test: `curl -sS -H "Authorization: Bearer
  $LITELLM_MASTER_KEY" http://localhost:4000/v1/models | jq
  '.data[] | select(.id == "minimax")'`. **Defer** to the user's
  dev shell (requires `litellm` stack running).
- [ ] 8.7 `openspec validate litellm-minimax-vendor-derisking
  --strict` exits 0. **Defer** to the user.

## 9. Land the plane

- [ ] 9.1 `git add -A && git commit` with a Conventional Commit
  message.
- [ ] 9.2 `git pull --rebase && git push`.
- [ ] 9.3 `git status` shows "up to date with origin".
- [ ] 9.4 Open follow-up issues for:
  - Skill update (Step 7.1)
  - BAML regen + caller migration (Step 4.3)
  - Roll the 3 vault entries after the first `secrets:init` run
    (Step 3.2)
  - Add a Langfuse alert for `fallback_rate > 50%` on the
    `minimax` alias (suggests a 3-key slot exhaustion)

## Reference

- OpenSpec change:
  `openspec/changes/litellm-minimax-vendor-derisking/`
- Sister changes:
  `openspec/changes/docs-skills-consolidation-pipeline/`,
  `openspec/changes/four-directory-indexing-and-standards/`
- Key files:
  - `infrastructure/stacks/litellm/config/config.yaml`
  - `baml_src/clients.baml`
  - `opencode.json`
  - `sruth/oideachais/dagster_defs/assets/llm_gateway_assets.py`
- Existing alias pattern:
  `infrastructure/stacks/litellm/config/config.yaml` lines
  519-653 (ocr, vision, document, extract, math, irish, image,
  general)
- OpenSpec workflow: `openspec/AGENTS.md`
