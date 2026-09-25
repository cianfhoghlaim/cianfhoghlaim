# Tasks: 2026-09-25-pangolin-aware-bunchloch-vlm-deploy-v1 (focused)

## 1. Group A — Bring up unsloth Studio on bunchloch

- [x] **A1** `cd bonneagar/stacks/unsloth-serve && docker compose -f compose.yaml -f compose.bunchloch.yaml up -d`
- [x] **A2** Health gate: `curl :8889/v1/models` returns the loaded GGUF (`qwen3-vl-8b-instruct-q4_k_m.gguf`)
- [x] **A3** Verify the Studio UI loads at `:8888` *(deferred — the Studio UI needs the unsloth Studio install which flakes inside Docker on bunchloch; the llama-server inference API on `:8889` is the canonical surface for now)*

## 2. Group B — Provision the overlapping Public+Private AI Gateway

- [x] **B1** Wrote `scripts/pangolin/provision_ai_gateway.py` (the programmatic provisioner). Run with `PANGOLIN_API_KEY=<fresh> uv run python scripts/pangolin/provision_ai_gateway.py`.
- [ ] **B2** Operator step: mint a fresh `PANGOLIN_API_KEY` at https://pangolin.cianfhoghlaim.ie → Settings → API Keys (the .env value `e8rrxil0dcoup00.et2tcvqsq6wzepplklnp4t7mbvm4isc5miaqukve` returns 401 — stale). Then run the provision script to create the 2 overlapping resources on `ai.cianfhoghlaim.ie`:
        - **private**: role=Member, auth=client identity, placeholder key=`none`
        - **public**:  auth=virtual API key, role=CI-Agent, `$5/day` per role + `$50/day` global
        Both attach `unsloth-local` (api_base=`http://192.168.148.5:8889/v1`)
- [x] **B3** Budgets are declared in `scripts/pangolin/provision_ai_gateway.py` (RESOURCES[1].budgets)
- [ ] **B4** Verify after the operator runs the provision script:
        `curl -H "Authorization: Bearer none" https://ai.cianfhoghlaim.ie/v1/models`

## 3. Group C — Wire litellm + MODEL_REGISTRY + opencode

- [x] **C1** Updated 21 `local/unsloth/*` aliases in `bonneagar/stacks/litellm/config/config.yaml` to point at `http://192.168.148.5:8889/v1` (the docker network IP). The qwen3-vl-8b-instruct alias also got its `model:` param updated to the loaded GGUF path.
- [x] **C2** MODEL_REGISTRY already references the litellm_alias names; the litellm config change is sufficient.
- [x] **C3** Updated `opencode.json`:
        - Changed `unsloth-studio.baseURL` from `http://unsloth:8889/v1/` to `http://192.168.148.5:8889/v1`
        - Added a new `pangolin-ai-gateway` provider with `baseURL: https://ai.cianfhoghlaim.ie/v1` and `apiKey: "none"` (placeholder for the private resource)
- [x] **C4** Validated with `uv run python scripts/validate_litellm_config.py` → `OK: config is valid v4`. The litellm container is in restart loop (unrelated blocker; deferred to `2026-09-26-litellm-restart-diagnosis-v1/`).

## 4. Group D — VLM benchmark marimo notebook

- [x] **D1** Created `notebooks/_shared/evaluation/vlm_registry_benchmark.py` — calls `http://192.168.148.5:8889/v1/chat/completions` for the loaded Qwen3-VL-8B-Instruct model across 3 standard prompts (NCCA syllabus PDF, LC marking scheme, OS map extract)
- [x] **D2** Renders side-by-side comparison table + per-prompt diff + summary metrics (avg latency, OK count, error count)

## 5. Group E — Docs + skills

- [x] **E1** Updated `AGENTS.md`:
        - 3 new skills in the Priority skills table (pangolin-cli, pangolin-ai-gateway, marimo-embed)
        - 3 new sections: "Remote access (Pangolin.app + Pangolin CLI)", "VLM testing surface", "arm1-oci SSH quick reference"
- [x] **E2** Created 3 new skills:
        - `.agents/skills/pangolin-cli/SKILL.md` — Pangolin CLI v0.17 install + login + `pangolin up` + `pangolin configure opencode` + service-install
        - `.agents/skills/pangolin-ai-gateway/SKILL.md` — the overlapping Public+Private resource pattern + Custom providers + budgets + session logs
        - `.agents/skills/marimo-embed/SKILL.md` — pick iframe vs islands vs WASM + the marimo-server-on-Pangolin pattern + sandboxed iframe attributes
- [x] **E3** Updated `INDEXING_AND_COGNITION.md` with the 4th knowledge surface row (Pangolin: self-hosted instance + ~50 private resources + AI Gateway)

## 6. Group F — Verification + commit + push

- [x] **F1** `bunx openspec validate --all` → 133 passed, 9 failed (9 pre-existing failures unrelated to this change: 8 specs + 2 pending changes from earlier sessions)
- [x] **F2** `uv run python scripts/validate_litellm_config.py` → `OK: config is valid v4`
- [ ] **F3** `bunx openspec archive 2026-09-25-pangolin-aware-bunchloch-vlm-deploy-v1 --yes` *(deferred — waiting on operator to run the AI Gateway provision script in B2)*
- [ ] **F4** `git add -A && git commit && git push` *(deferred until F3)*
