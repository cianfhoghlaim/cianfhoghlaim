# Tasks: 2026-07-29-complete-remaining-model-registry-migrations-v1

## Phase 1 — Complete remaining MODEL_REGISTRY migrations (autonomous)

- [ ] **1.1** Update `agents/image_generation.py:IMAGE_MODELS` to use `MODEL_REGISTRY.filter(family="image_gen")` (5 entries: flux2-dev, z-image-turbo, qwen-image, sdxl, fibo)
- [ ] **1.2** Update `agents/translation.py:primary_model/fallback_model` to use `MODEL_REGISTRY.filter(family="translation")` (3 entries: opus-mt, m2m100, nllb)
- [ ] **1.3** Verify `agents/letta_client.py:139` uses MODEL_REGISTRY (DONE in Wave 5)
- [ ] **1.4** Verify `agents/hitl_agent.py:107,449` uses MODEL_REGISTRY (DONE in Wave 5)
- [ ] **1.5** Verify `agents/agno/education_team.py:170-185` uses MODEL_REGISTRY (DONE in Wave 5)
- [ ] **1.6** Verify `agents/adk/voice_agent.py:25-29` uses MODEL_REGISTRY (DONE in Wave 5)
- [ ] **1.7** Verify `agents/adk/email_triage_agent.py:504` uses MODEL_REGISTRY (DONE in Wave 5)
- [ ] **1.8** Verify `agents/api/_oideachais_api/services/chatterbox.py:35` uses MODEL_REGISTRY (DONE in Wave 5)

## Phase 2 — Notebook + spaces sites

- [ ] **2.1** Verify `notebooks/10_biep_pipeline_lakehouse_semantic_01_search.py` uses MODEL_REGISTRY (DONE in Wave 5)
- [ ] **2.2** Verify `spaces/_common/baml_client.py:69-71` uses MODEL_REGISTRY (DONE in Wave 5)
- [ ] **2.3** Verify `spaces/oideachais-pdf-review/app.py:39-40` uses MODEL_REGISTRY (DONE in Wave 5)

## Phase 3 — BAML clients verify

- [ ] **3.1** Verify all 21 BAML clients in `baml_src/clients.baml` have `MODEL_REGISTRY: family="..." role="..." → "..."` annotations (DONE in Wave 5)
- [ ] **3.2** Delete the 8 commented-out historical clients in `baml_src/clients.baml` (DONE in Wave 5)
- [ ] **3.3** Update `scripts/generate_litellm_config.py` to read from MODEL_REGISTRY (DONE in Wave 5)
- [ ] **3.4** Run `mise run cic:meaisin:litellm-regenerate` (DONE in Wave 5 — output: 58 entries)

## Phase 4 — BAML TypeScript codegen activation

- [ ] **4.1** Verify `mise run baml:generate` populated `baml_client_ts/` (DONE in Wave 5)
- [ ] **4.2** Add `baml_client/zod_exports.ts` mirror file for web app
- [ ] **4.3** Update `web/apps/cianfhoghlaim-leaving-cert/packages/api/src/routers/*.ts` to use the zod_exports
- [ ] **4.4** Update `web/...` (wherever the canonical rewrite is — verify with the web app's TanStack Start router)
- [ ] **4.5** Update `scripts/schema-generate.ts` to consume BAML TS exports

## Phase 5 — Verification

- [ ] **5.1** `openspec validate 2026-07-29-complete-remaining-model-registry-migrations-v1 --strict` exits 0
- [ ] **5.2** `mise run lint:registry` reports 0 hardcoded model strings
- [ ] **5.3** `MODEL_REGISTRY.filter(family="image_gen").keys()` includes all 5 IMAGE_MODELS
- [ ] **5.4** `MODEL_REGISTRY.filter(family="translation").keys()` includes all 3 translation models
- [ ] **5.5** `web/apps/cianfhoghlaim-leaving-cert/` builds with the zod_exports (run `bun run build` if available)
