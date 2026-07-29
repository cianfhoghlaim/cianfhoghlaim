# 2026-07-29-complete-remaining-model-registry-migrations-v1

## Why

Tracked by **issue #141**: "Complete remaining MODEL_REGISTRY migrations (Phase 1.3-1.10 + 1.12-1.19)". The centralized-model-schema-registry change (`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`, archived 2026-07-29) shipped Phase 1.1-1.2 + 1.11 + 1.15-1.19 but deferred the remaining 8 tasks (1.3-1.10 + 1.12-1.14) due to runtime/agent-bound dependencies. This change closes those remaining migrations to bring MODEL_REGISTRY coverage from ~58 entries to a single canonical source of truth across the entire platform.

## What changes

### 1. Update the 6 remaining hardcoded model sites (Phase 1.3-1.10)

| # | File | Hardcoded model(s) | Replace with |
|:--|:--|:--|:--|
| 1.3 | `agents/image_generation.py:IMAGE_MODELS` | `flux2-dev`, `z-image-turbo`, `qwen-image`, `sdxl`, `fibo` | `MODEL_REGISTRY.filter(family="image_gen")` |
| 1.4 | `agents/translation.py:primary_model/fallback_model` | `opus-mt`, `m2m100`, `nllb` | `MODEL_REGISTRY.filter(family="translation")` + per-language fallback chain |
| 1.5 | `agents/letta_client.py:139` (DONE in Wave 5) | — | — |
| 1.6 | `agents/hitl_agent.py:107,449` (DONE in Wave 5) | — | — |
| 1.7 | `agents/agno/education_team.py:170-185` (DONE in Wave 5) | — | — |
| 1.8 | `agents/adk/voice_agent.py:25-29` (DONE in Wave 5) | — | — |
| 1.9 | `agents/adk/email_triage_agent.py:504` (DONE in Wave 5) | — | — |
| 1.10 | `agents/api/_oideachais_api/services/chatterbox.py:35` (DONE in Wave 5) | — | — |

### 2. Update the 3 remaining notebook sites (Phase 1.12-1.13)

| # | File | Hardcoded model(s) | Replace with |
|:--|:--|:--|:--|
| 1.12 | `notebooks/10_biep_pipeline_lakehouse_semantic_01_search.py` (DONE in Wave 5) | — | — |
| 1.13 | `spaces/_common/baml_client.py:69-71` (DONE in Wave 5) | — | — |

### 3. Update the BAML clients (Phase 1.15) - VERIFY DONE

`baml_src/clients.baml` was updated in Wave 5 (68-line historical block deleted + `MODEL_REGISTRY:` annotations added to all 21 active clients). Verify all 21 clients now have explicit `family` + `role` references matching the registry keys.

### 4. Activate BAML TypeScript codegen (Phase 2.2-2.5)

- 2.1 Run `mise run baml:generate` to populate `baml_client_ts/` (DONE in Wave 5)
- 2.2 Add `baml_client/zod_exports.ts` mirror file for web app
- 2.3 Update `web/apps/cianfhoghlaim-leaving-cert/packages/api/src/routers/*.ts` to use the zod_exports
- 2.4 Update `web/...` (wherever the canonical rewrite is)
- 2.5 Update `scripts/schema-generate.ts` to consume BAML TS exports

## Dependencies

`Blocked by: none` (the Wave 5 work unblocked this)

`Affected repos: cianfhoghlaim` (single-repo)

## Estimated effort

~3 hours of mechanical work + 1 hour of verification. The Wave 5 sub-agent completed ~50% of these in pass 2; this change finishes the rest.

## Acceptance gates

- [ ] `openspec validate 2026-07-29-complete-remaining-model-registry-migrations-v1 --strict` exits 0
- [ ] `mise run lint:registry` reports 0 hardcoded model strings in audited files
- [ ] `MODEL_REGISTRY.filter(family="image_gen").keys() == IMAGE_MODELS.keys()`
- [ ] `MODEL_REGISTRY.filter(family="translation").keys() == primary_model_keys + fallback_keys`
- [ ] All 21 BAML clients in `baml_src/clients.baml` have explicit `MODEL_REGISTRY: family="..." role="..." → "..."` annotations
- [ ] `web/apps/cianfhoghlaim-leaving-cert/` builds with the zod_exports
