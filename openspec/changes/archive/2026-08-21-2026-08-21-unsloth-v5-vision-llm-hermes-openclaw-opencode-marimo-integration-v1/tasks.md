# Tasks — Unsloth v5 Integration

Total: 67 tasks across 8 phases. Estimated effort: **6–8 days end-to-end**.

## Phase 0 — Pre-flight (0.5 day)

- [ ] **P0.1** Verify `openspec change show 2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1 --json` exists and is well-formed
- [ ] **P0.2** Run `openspec validate 2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1 --strict` — MUST exit 0 before any task starts
- [ ] **P0.3** Verify the current `MODEL_REGISTRY.filter(family="ocr_vision")` returns 22 entries (baseline; will become 26)
- [ ] **P0.4** Verify the current `MODEL_REGISTRY.filter(family="text_llm")` returns 9 entries (baseline; will become 14)
- [ ] **P0.5** Verify `unsloth==2026.8.0` is live on PyPI: `curl -s https://pypi.org/pypi/unsloth/json | jq '.info.version'` — MUST return `2026.8.0` or later
- [ ] **P0.6** Verify the Unsloth Studio headless image is live: `docker pull unsloth/unsloth:latest` — if it doesn't exist, fall back to `continuumio/miniconda3:latest` + `pip install unsloth==2026.8.0`
- [ ] **P0.7** Run `git pull --rebase && git push --dry-run` to confirm clean worktree

## Phase 1 — Bonneagar stack & secrets (1.5 days)

- [ ] **1.1** Create directory `bonneagar/stacks/unsloth-serve/`
- [ ] **1.2** Write `bonneagar/stacks/unsloth-serve/compose.yaml` — the base compose file (the host-specific overrides inherit)
- [ ] **1.3** Write `bonneagar/stacks/unsloth-serve/compose.arm1-oci.yaml` — GPU variant (`-ngl 99`, 12 GB limit, public via Pangolin)
- [ ] **1.4** Write `bonneagar/stacks/unsloth-serve/compose.bunchloch.yaml` — CPU/MPS variant (`-ngl 0`, 8 GB limit, `127.0.0.1:8889` only)
- [ ] **1.5** Write `bonneagar/stacks/unsloth-serve/sidecar.yaml` — Locket sidecar pulling `infisical://dev-baile/unsloth/api-key`
- [ ] **1.6** Write `bonneagar/stacks/unsloth-serve/secrets.env` — single shared `UNSLOTH_API_KEY=infisical://dev-baile/unsloth/api-key`
- [ ] **1.7** Write `bonneagar/stacks/unsloth-serve/pangolin.yaml` — declares `unsloth.cianfhoghlaim.ie` + `unsloth-api.cianfhoghlaim.ie`
- [ ] **1.8** Write `bonneagar/stacks/unsloth-serve/blueprint.yaml` — Komodo stack registration
- [ ] **1.9** Write `bonneagar/stacks/unsloth-serve/.env.example` — stub values for local dev
- [ ] **1.10** Append `UNSLOTH_API_KEY=infisical://dev-baile/unsloth/api-key` to root `.infisical.env`
- [ ] **1.11** Run `bun run scripts/init-vault.ts` (or `mise run secrets:init`) to materialise the new secret
- [ ] **1.12** Verify the secret materialised: `curl -s -H "Authorization: Bearer $(infisical login --silent)" https://app.infisical.cianfhoghlaim.ie/api/v3/secrets/raw?secretPath=/unsloth` returns the new key
- [ ] **1.13** Append the `unsloth-serve` block to `bonneagar/komodo/resource-syncs/arm1-oci.toml`
- [ ] **1.14** Append the `unsloth-serve` block to `bonneagar/komodo/resource-syncs/bunchloch.toml`
- [ ] **1.15** Write `bonneagar/komodo/procedures/unsloth-serve-deploy.toml` — deploy procedure (pull image → mount volumes → run sidecar → healthcheck :8888 + :8889)
- [ ] **1.16** Run `mise run cic:stack-doctor --strict` to verify both compose variants pass
- [ ] **1.17** Run `mise run cic:stack-doctor --check-grammar` to verify no mixed bare/Jinja syntax in `secrets.env`
- [ ] **1.18** Append the 2 Pangolin private resources to `bonneagar/pangolin/agent-fleet.yaml`
- [ ] **1.19** Run `mise run iac:sync:resources` to register the new Pangolin routes
- [ ] **1.20** Run `mise run iac:plan` to confirm the IaC-declared state matches the desired state
- [ ] **1.21** Run `mise run deploy:full --phase=6 --dry-run` to preview the deploy

## Phase 2 — MODEL_REGISTRY extension (1 day)

- [ ] **2.1** Edit `meaisinfhoghlaim/models/registry.py` — add `UNSLOTH = "unsloth"` to `ModelBackend` enum (line ~89)
- [ ] **2.2** Edit `meaisinfhoghlaim/models/model_registry.py` — add the 10 new text_llm entries (Qwen3.8-27B + 2.4T-A95B + DeepSeek-V4-Pro-0813 + DeepSeek-V4-Flash-0731 + Kimi-K2.7-Code + Kimi-K3 + Nemotron-3.5-Lightning-30B-A3B + Muse-Glimmer-30B + MiniMax-M2.5 + Magistral-Small-2509)
- [ ] **2.3** Edit `meaisinfhoghlaim/models/model_registry.py` — add the 4 new ocr_vision entries (Qwen3-VL-8B-Instruct + Qwen3-VL-32B-Instruct + GLM-4.6V-Flash + DeepSeek-OCR-2)
- [ ] **2.4** Edit `meaisinfhoghlaim/models/model_registry.py` — add the 2 new image_gen entries (DiffusionGemma-26B-A4B + Qwen-Image-2512)
- [ ] **2.5** Edit `meaisinfhoghlaim/models/model_registry.py` — add the 2 new embedder entries (Qwen3-Embedding-4B + EmbeddingGemma-300M)
- [ ] **2.6** Edit `meaisinfhoghlaim/models/model_registry.py` — add the 2 new voice entries (Orpheus-3b-0.1-ft + Sesame-CSM-1B)
- [ ] **2.7** Verify `MODEL_REGISTRY.filter(family="ocr_vision")` returns 26 entries
- [ ] **2.8** Verify `MODEL_REGISTRY.filter(family="text_llm")` returns 14 entries
- [ ] **2.9** Verify `MODEL_REGISTRY.filter(family="image_gen")` returns 7 entries
- [ ] **2.10** Verify `MODEL_REGISTRY.filter(family="embedder")` returns 5 entries
- [ ] **2.11** Verify `MODEL_REGISTRY.filter(family="voice")` returns 7 entries
- [ ] **2.12** Verify `MODEL_REGISTRY.filter(family="translation")` returns 3 entries (unchanged)
- [ ] **2.13** Verify `MODEL_REGISTRY.filter(family="rerank")` returns 3 entries (unchanged)
- [ ] **2.14** Verify `MODEL_REGISTRY.filter(backend="unsloth")` returns exactly 20 entries
- [ ] **2.15** Run `mise run lint:registry` — MUST exit 0
- [ ] **2.16** Run `mise run cic:meaisin:litellm-regenerate` — regenerates `bonneagar/stacks/litellm/config/config.yaml` stub from the registry
- [ ] **2.17** Run `mise run cic:ocr:registry-lint` — verifies all 26 VISION_MODELS are live on HF Hub

## Phase 3 — LiteLLM config (0.5 day)

- [ ] **3.1** Edit `bonneagar/stacks/litellm/config/config.yaml` — append 20 new model entries, one per registry entry, all routing to `http://unsloth:8889/v1` with `api_key=os.environ/UNSLOTH_API_KEY`
- [ ] **3.2** Edit the `vision` alias block — flip primary to `local/unsloth/qwen3-vl-8b`, preserve `local/vision/qwen3-vl-8b` (llama-swap) + `gemini/gemini-2.5-pro` as fallback chain
- [ ] **3.3** Edit the `text` alias block — add `local/unsloth/qwen3.8-27b` as a fallback when M3 quota exhausted
- [ ] **3.4** Edit the `coding` alias block — add `local/unsloth/kimi-k2.7-code` as a fallback
- [ ] **3.5** Run `docker compose -f bonneagar/stacks/litellm/compose.yaml restart litellm`
- [ ] **3.6** Verify `curl http://localhost:4000/v1/models | jq '.data[] | select(.id | startswith("local/unsloth/")) | .id'` returns 20 entries
- [ ] **3.7** Test the 429 fallback: `curl -X POST http://localhost:4000/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"vision","messages":[{"role":"user","content":"hello"}]}' | jq .model` returns `local/unsloth/qwen3-vl-8b`

## Phase 4 — Hermes + OpenClaw + OpenCode wiring (1 day)

- [ ] **4.1** Edit `bonneagar/stacks/hermes/config/hermes.yaml` — add `unsloth` provider block pointing at `http://unsloth:8889/v1` with 3 models (Qwen3.8 + DeepSeek-V4-Pro + Magistral-Small)
- [ ] **4.2** Edit `bonneagar/stacks/hermes/Dockerfile.hermes` (or the entrypoint script) — branch on `UNSLOTH_PROVIDER` env var: `true` → `unsloth start hermes --model unsloth/Qwen3.8-27B-GGUF:UD-Q4_K_XL`, `false` → existing Hermes CLI
- [ ] **4.3** Restart the Hermes container: `docker compose -f bonneagar/stacks/hermes/compose.yaml up -d`
- [ ] **4.4** Verify: send a `telegram` message to the hermes bot, observe the langfuse trace tagged with `provider=unsloth`
- [ ] **4.5** Edit `bonneagar/stacks/openclaw/config/openclaw.json` — add `unsloth` provider block with `baseUrl: http://unsloth:8889`, `api: "anthropic-messages"`, 3 models (Qwen3.8 + DeepSeek-V4-Pro + Kimi-K2.7-Code)
- [ ] **4.6** Restart the OpenClaw container
- [ ] **4.7** Verify: in the openclaw TUI, switch the provider from `litellm` to `unsloth`, send a `webchat` message, observe the langfuse trace
- [ ] **4.8** Edit `opencode.json` — add `unsloth-studio` custom provider block (`type: "openai-compatible"`, `baseURL: http://unsloth:8889/v1/`, 4 models)
- [ ] **4.9** Edit `opencode.json` — add the 429-retry-fallback rule to the agent dispatch table (the `agent` block)
- [ ] **4.10** Restart the OpenChamber container: `docker compose -f bonneagar/stacks/openchamber/compose.yaml up -d`
- [ ] **4.11** Verify: in the OpenChamber UI at `openchamber.cianfhoghlaim.ie`, open the `/model` picker, the `unsloth-studio` group appears with 4 models
- [ ] **4.12** Verify the fallback: trigger a 429 from the M3 chokepoint and observe the retry succeeds against unsloth-studio

## Phase 5 — Marimo 10-way comparison notebook (1 day)

- [ ] **5.1** Create `notebooks/30_unsloth_vision_compare.py` (300 LOC, marimo reactive)
- [ ] **5.2** Import `MODEL_REGISTRY.filter(family="ocr_vision")` + `MODEL_REGISTRY.filter(family="text_llm")` (no hardcoded model strings)
- [ ] **5.3** Add the 10 backend picker (6 VLMs + 4 classical OCRs), grouped by `mo.ui.tabs`
- [ ] **5.4** Add the PDF picker from `stedding/ingest_queue/` (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science)
- [ ] **5.5** Add the reactive loop that sends each (backend, PDF) pair through `http://ocr-router:8090/v1/ocr` (the ocr-router stack handles the fanout)
- [ ] **5.6** Add the side-by-side `mo.hstack` of response text + latency + tokens (VLMs) / regions (classical) + KL-divergence note (VLMs) or CER/WER note (classical)
- [ ] **5.7** Add the `mo.ui.dropdown` filter by `ModelCapability`
- [ ] **5.8** Add the export-to-`stedding/eval_results/unsloth_compare_{model_role}_{pdf_hash}.json` button
- [ ] **5.9** Edit `bonneagar/stacks/ocr-router/ocr_router.py` (or the dispatch matrix config) — add the 6 unsloth-vision entries (vlms/strong/fast/reasoning/ocr) routing to `http://unsloth:8889/v1` (the existing 6 backend routes preserved)
- [ ] **5.10** Restart the ocr-router container
- [ ] **5.11** Run `mise run notebook:unsloth-compare` to verify the notebook launches
- [ ] **5.12** Test against 1 Gaeilge PDF + 4 backends (Qwen3-VL-8B, GLM-4.6V-Flash, Docling, OlmOCR) — verify all 4 produce outputs in <60s
- [ ] **5.13** Verify the export file appears at `stedding/eval_results/`
- [ ] **5.14** Add `mise run notebook:unsloth-compare` task to `mise.toml`
- [ ] **5.15** Add the notebook to the `notebooks-sync` registry at `scripts/sync/notebooks_sync.py`

## Phase 6 — Modal fine-tune update (0.5 day)

- [ ] **6.1** Verify live: `uv run pip index versions unsloth` — pin `unsloth==2026.8.0` (or the verified version)
- [ ] **6.2** Edit `meaisinfhoghlaim/training/modal_finetune/finetune_irish.py` — replace the git ref with the pinned PyPI version
- [ ] **6.3** Edit the default `base_model` from `unsloth/gemma-4-31B-it-GGUF` to `unsloth/Qwen3.8-27B-GGUF`
- [ ] **6.4** Create `meaisinfhoghlaim/training/modal_finetune/finetune_unsloth_local.py` (M4 Max 48 GB QLoRA r=8)
- [ ] **6.5** Run `modal run meaisinfhoghlaim/training/modal_finetune/finetune_irish.py --dry-run` — verify the new pin works
- [ ] **6.6** Run `python meaisinfhoghlaim/training/modal_finetune/finetune_unsloth_local.py --smoke-test` — verify the M4 Max variant works

## Phase 7 — CCC + Firecrawl (0.5 day)

- [ ] **7.1** Edit `.cocoindex_code/guides.yml` — add the `unsloth-integration` guide pointing at the 8 canonical Unsloth pages
- [ ] **7.2** Run `bun run ccc:index` — refresh the semantic index with the new guide
- [ ] **7.3** Verify: `bun run ccc:search "Unsloth Studio Hermes integration"` returns the guide
- [ ] **7.4** Add 5 `firecrawl_monitor_create` calls for the Unsloth integration doc URLs (7-day interval, `changeTracking: markdown`)
- [ ] **7.5** Run `mise run sync:firecrawl` to push the new monitors to the corpus
- [ ] **7.6** Verify the monitors appear in the firecrawl dashboard

## Phase 8 — Validation (0.5 day)

- [ ] **8.1** Run `openspec validate 2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1 --strict` — MUST exit 0
- [ ] **8.2** Run `openspec validate --all --strict` — MUST exit 0 (verify no other changes break)
- [ ] **8.3** Run `mise run lint:drift-docs` — verify the per-area AGENTS.md impact tables are updated
- [ ] **8.4** Run `mise run devops:validate-stacks` — verify both compose variants pass
- [ ] **8.5** Run `mise run sync:all` — trigger the 15-layer sync loop
- [ ] **8.6** End-to-end test from bunchloch: `docker exec unsloth-serve unsloth run --model unsloth/Qwen3.8-27B-GGUF:UD-Q4_K_XL --port 8889 --disable-tools`, then `curl http://localhost:8889/v1/models -H "Authorization: Bearer $UNSLOTH_API_KEY"` — verify the model ID matches
- [ ] **8.7** End-to-end test from a hermes telegram chat: send a message, observe langfuse trace tagged `provider=unsloth`
- [ ] **8.8** End-to-end test from openclaw webchat: switch to unsloth provider, send a message, observe response
- [ ] **8.9** End-to-end test from OpenChamber: open `/model`, select `unsloth-studio/Qwen3.8`, send a prompt, observe response
- [ ] **8.10** End-to-end test from marimo: `mise run notebook:unsloth-compare`, run a 4-way comparison on a Gaeilge PDF, verify export file
- [ ] **8.11** Run `mise run lint:registry` — final audit, MUST exit 0
- [ ] **8.12** Run `mise run sync:notebooks` — verify the new notebook is in the registry

## Post-flight

- [ ] **PF.1** Commit: `git commit -m "feat(unsloth-v5): Qwen3.8 + Hermes + OpenClaw + OpenCode + marimo 10-way comparison"`
- [ ] **PF.2** Push: `git pull --rebase && git push` — MUST succeed
- [ ] **PF.3** Archive the change: `openspec archive 2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1 --yes`
- [ ] **PF.4** Land the plane: file any remaining follow-ups as GitHub issues; close the related milestone
