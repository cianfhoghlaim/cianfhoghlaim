# Tasks: Cianfhoghlaim v5 — OpenCode + Model Priority + Qwen Removal v1

> 9 phases, ~40 tasks. All tasks MUST pass before `openspec archive`.
> The phase ordering is hard — later phases depend on earlier ones.

## Phase A — OpenSpec scaffolding (30 min)

- [ ] **A.1** `mkdir -p openspec/changes/2026-08-31-cianfhoghlaim-v5-opencode-model-priority-v1/{proposal.md,tasks.md,specs/centralized-model-registry/}`
- [ ] **A.2** Author `proposal.md` + `tasks.md` + `specs/centralized-model-registry/spec.md`
- [ ] **A.3** `openspec validate 2026-08-31-cianfhoghlaim-v5-opencode-model-priority-v1 --strict` — passes 0 errors

## Phase B — Global opencode config (`~/.config/opencode/opencode.jsonc`) (15 min)

- [ ] **B.1** Backup the current config to `~/.config/opencode/opencode.jsonc.bak-pre-v5-{timestamp}`
- [ ] **B.2** Update top-level `model` + `small_model`
- [ ] **B.3** Extend `provider.google-vertex` to expose Gemini 3.5/2.5 Flash
- [ ] **B.4** Add `provider.google-aistudio`
- [ ] **B.5** Add `provider.minimax-coding-plan` (key #1 = existing `MINIMAX_API_KEY`)
- [ ] **B.6** Add `provider.minimax-coding-plan-v2` (key #2 = new `MINIMAX_API_KEY_V2`)
- [ ] **B.7** Add `provider.unsloth-studio` (host.docker.internal:8888/v1, Gemma 4 family)
- [ ] **B.8** Update `agent.build.model` to v2
- [ ] **B.9** Update `agent.plan.model` to v2
- [ ] **B.10** Keep `agent.research.model` on key #1

## Phase C — Project opencode config (`cianfhoghlaim/opencode.json`) (30 min)

- [ ] **C.1** Backup the current config to `opencode.json.bak-pre-v5-{timestamp}`
- [ ] **C.2** DELETE `provider.qwen` block entirely
- [ ] **C.3** DELETE `provider["litellm_local"]` block entirely
- [ ] **C.4** DELETE `unsloth/Qwen3.8-27B-GGUF` model entry
- [ ] **C.5** Add `provider.minimax-coding-plan` (key #1)
- [ ] **C.6** Add `provider.minimax-coding-plan-v2` (key #2)
- [ ] **C.7** Add `provider.google-aistudio`
- [ ] **C.8** Extend `provider.google-vertex` to expose Gemini 3.5/2.5 Flash
- [ ] **C.9** Extend `provider.unsloth-studio` with gemma-4 + gemma-3-27b-it
- [ ] **C.10** Update `agent.build.model` to v2
- [ ] **C.11** Update `agent.plan.model` to v2
- [ ] **C.12** Update `agent.frontend-apps.model` from qwen to M3
- [ ] **C.13** Update `agent.notebooks.model` from qwen to gemma-4
- [ ] **C.14** Update `agent.baml.model` from qwen to M3
- [ ] **C.15** Update `agent.dagster.model` from qwen to M3
- [ ] **C.16** Update `agent.deep-cuts.model` from qwen to gemma-4

## Phase D — `.env.example` + `.infisical.env` (20 min)

- [ ] **D.1** Add `MINIMAX_API_KEY_V2=` next to existing `MINIMAX_API_KEY=`
- [ ] **D.2** Add `MODEL_PROFILE=dev`
- [ ] **D.3** Add `GEMINI_API_KEY=` (AI-Studio fallback)
- [ ] **D.4** Add `UNSLOTH_BASE_URL=` + `UNSLOTH_API_KEY=`
- [ ] **D.5** Add `GOOGLE_CLOUD_PROJECT=` + `GOOGLE_CLOUD_LOCATION=`
- [ ] **D.6** REMOVE `DASHSCOPE_API_KEY=` (3 occurrences)
- [ ] **D.7** REMOVE `DASHSCOPE_BASE_URL=` (2 occurrences)
- [ ] **D.8** Update `.infisical.env` (root) + `.infisical.env.cognee` + `.infisical.env.lakehouse` + `.infisical.env.observability` accordingly

## Phase E — `.opencode/agents/*.md` frontmatter (15 min)

- [ ] **E.1** `.opencode/agents/build.md` — `model: minimax-coding-plan-v2/MiniMax-M3`
- [ ] **E.2** `.opencode/agents/plan.md` — `model: minimax-coding-plan-v2/MiniMax-M3`
- [ ] **E.3** `.opencode/agents/frontend-apps.md` — `model: minimax-coding-plan/MiniMax-M3`
- [ ] **E.4** `.opencode/agents/notebooks.md` — `model: unsloth-studio/gemma-4-26b-a4b`
- [ ] **E.5** `.opencode/agents/baml.md` — `model: minimax-coding-plan/MiniMax-M3`
- [ ] **E.6** `.opencode/agents/dagster.md` — `model: minimax-coding-plan/MiniMax-M3`
- [ ] **E.7** `.opencode/agents/deep-cuts.md` — `model: unsloth-studio/gemma-4-26b-a4b`

## Phase F — `meaisinfhoghlaim/models/model_registry.py` (45 min)

- [ ] **F.1** Add `profile: ModelProfile = "hackathon" | "dev" | "both"` field to `ModelRegistryEntry`
- [ ] **F.2** Add `gemini-3.5-flash` (text_llm/default, vertex backend, hackathon profile)
- [ ] **F.3** Add `gemini-3.5-flash-aistudio` (text_llm/aistudio, hackathon)
- [ ] **F.4** Add `gemini-3.5-flash-lite` (text_llm/lite, hackathon)
- [ ] **F.5** Add `gemini-2.5-flash` (text_llm/alt, both)
- [ ] **F.6** Add `gemini-embedding-2-preview` (text_llm/embedder, hackathon)
- [ ] **F.7** Add `gemma-4-26b-a4b` (text_llm/fallback, unsloth_studio, hackathon)
- [ ] **F.8** Add `gemma-4-e4b` (text_llm/fallback_light, unsloth_studio, hackathon)
- [ ] **F.9** Add `gemma-3-27b-it` (text_llm/local_fallback, unsloth_studio, dev)
- [ ] **F.10** Add `gemma-2-9b` (text_llm/local_fallback_old, unsloth_studio, dev)
- [ ] **F.11** Add `gemma-4-26b-a4b-vision` (ocr_vision/default, llama_swap, hackathon)
- [ ] **F.12** Add `gemma-4-12b-vision` (ocr_vision/vision_medium, llama_swap, hackathon)
- [ ] **F.13** Add `gemma-4-e4b-vision` (ocr_vision/vision_light, llama_swap, hackathon)
- [ ] **F.14** Add `gemma-3-12b-vision` (ocr_vision/vision_prior_gen, llama_swap, dev)
- [ ] **F.15** TOMBSTONE `qwen3.7-plus` (text_llm/token_plan_primary, available=False)
- [ ] **F.16** TOMBSTONE `qwen3-coder-next` (text_llm/token_plan_coding, available=False)
- [ ] **F.17** TOMBSTONE `qwen3-coder-plus` (text_llm/token_plan_coding_strong, available=False)
- [ ] **F.18** TOMBSTONE `qwen3.6-27b-mtp` (text_llm/token_plan_mtp, available=False)
- [ ] **F.19** Update profile gates: `minimax-m3` → `"both"`; `kimi-k2.6`, `glm-5.1`, `mimo-v2.5`, `deepseek-v4-flash` → `"dev"`

## Phase G — Cascade: qwen hardcoded removals (~30 files) (60 min)

- [ ] **G.1** `cocoindex_flows/knowledge_graph/youtube_kg_embedding.py` — `qwen3-vl-8b` → `gemma-4-26b-a4b-vision`; `qwen3.6-27b-mtp` → `gemma-4-26b-a4b`
- [ ] **G.2** `cocoindex_flows/knowledge_graph/multihop_search.py` — `qwen3.6-27b-mtp` → `gemma-4-26b-a4b`
- [ ] **G.3** `cocoindex_flows/corpus/local_documents_embedding.py` — `qwen3-vl-8b` → `gemma-4-26b-a4b-vision`
- [ ] **G.4** `cocoindex_flows/british_isles/ireland/canuint_embedding.py` — `qwen3-vl-8b` → `gemma-4-26b-a4b-vision`
- [ ] **G.5** `cocoindex_flows/_shared/reranker.py` — drop `DASHSCOPE_API_KEY` branch
- [ ] **G.6** `cocoindex_flows/media/artwork_embedding.py` — `qwen3-vl` → `gemma-4-26b-a4b-vision`
- [ ] **G.7** `cocoindex_flows/media/tg4_foghlaim_embedding.py` — `qwen3-vl-8b` → `gemma-4-26b-a4b-vision`
- [ ] **G.8** `meaisinfhoghlaim/backends/scanned_detector.py` — `qwen3-vl-8b` → `gemma-4-26b-a4b-vision`
- [ ] **G.9** `meaisinfhoghlaim/datasets/irish_processing.py` — `qwen3-vl` → `gemma-4-e4b-vision`
- [ ] **G.10** `meaisinfhoghlaim/ocr/ensemble/__init__.py` — add `"gemma4"` to `PathName`
- [ ] **G.11** `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py` — same
- [ ] **G.12** `meaisinfhoghlaim/training/modal_finetune/finetune_unsloth_local.py` — `irish-qwen3.8` → `irish-gemma-4`
- [ ] **G.13** `meaisinfhoghlaim/training/training/langfuse_callbacks.py` — `qwen3-vl` price metadata key swap
- [ ] **G.14** `cocoindex_flows/infrastructure/test_phase0_primitives.py` — drop `DASHSCOPE_API_KEY` monkeypatch
- [ ] **G.15** Run `mise run lint:registry` — must report `0 drift`

## Phase H — `baml_src/clients.baml` rewrite (45 min)

- [ ] **H.1** Add 3 new retry policies: `Tier1`, `Tier2`, `Tier3`
- [ ] **H.2** Add concrete clients: `MiniMaxPrimary`, `VertexGemini35Flash`, `AIStudioGemini35Flash`, `UnslothGemma4`, `UnslothGemma4Light`, `LlamaSwapGemma4Vision`, `TestMock`
- [ ] **H.3** Add `Primary` alias that reads `MODEL_BASE_URL`/`MODEL_API_KEY`/`MODEL_PRIMARY` from env
- [ ] **H.4** REMOVE `ExtractQwenCrossCheck` block
- [ ] **H.5** UPDATE `BIEPV3Vision` model from `local/vision/qwen3-vl-8b` → `local/ocr/gemma-4-26B-A4B-vision`
- [ ] **H.6** UPDATE `BIEPV3ExtractStrong` to use `MINIMAX_API_KEY_V2`
- [ ] **H.7** UPDATE the 8 generic aliases — keep on M3 for BIEP parity, add comments pointing at Primary
- [ ] **H.8** `mise run baml:generate` — regenerates `baml_client/` from the new clients.baml
- [ ] **H.9** `mise run baml:test` — 558 BAML functions pass

## Phase I — Skills + AGENTS.md + ccc guides cascade (30 min)

- [ ] **I.1** `.agents/skills/opencode/SKILL.md` — drop qwen example, add `minimax-coding-plan-v2` + `google-aistudio`
- [ ] **I.2** `.agents/skills/centralized-registry/SKILL.md` — add Gemma 4 + Gemini 3.5 entries
- [ ] **I.3** `.agents/skills/litellm/SKILL.md` — add Gemini 3.5 + Gemma 4 routes
- [ ] **I.4** `.cocoindex_code/guides.yml` — add `# google-aistudio-models`, `# unsloth-gemma-4-tier-2`, `# minimax-coding-plan-v2`
- [ ] **I.5** `openspec/AGENTS.md` — replace qwen3.7-plus mention with gemma-4
- [ ] **I.6** `openspec/specs/centralized-model-registry/spec.md` — 4 new ADDED Requirements
- [ ] **I.7** `AGENTS.md` (root) — replace OpenCode Go mention with the new v2 chain

## Phase J — Validation (15 min)

- [ ] **J.1** `mise run openspec:validate 2026-08-31-cianfhoghlaim-v5-opencode-model-priority-v1 --strict`
- [ ] **J.2** `mise run lint:registry` — 0 drift
- [ ] **J.3** `mise run lint:skills` — 167+ skills pass
- [ ] **J.4** `mise run lint:drift-docs` — number claims match
- [ ] **J.5** `mise run sync:all` — 14 sync layers green
- [ ] **J.6** `mise run baml:generate && mise run baml:test`
- [ ] **J.7** `openspec archive 2026-08-31-cianfhoghlaim-v5-opencode-model-priority-v1 --yes` (after deploy)

## Phase K — Hand-off (5 min)

- [ ] **K.1** Update `openspec/AGENTS.md` Phase 5 cross-reference
- [ ] **K.2** Notify Phase 2 (BAML fallback chains) + Phase 5 (meaisinfhoghlaim refactor)

---

*Last updated by build subagent at 2026-08-31.*