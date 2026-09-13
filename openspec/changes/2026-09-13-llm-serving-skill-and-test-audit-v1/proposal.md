# Change: LLM Serving Skill + Test Audit v1

## Why

Plan 3 (LLM serving layer audit) revealed significant version drift and
documentation gaps across the three LLM serving stacks (LiteLLM, Unsloth,
Llama-swap):

1. **Version drift**:
   - `.agents/skills/litellm/SKILL.md` claims v1.90 (verified 2026-06-29)
   - Actual installed: `litellm==1.97.0` (Python lib)
   - Docker image in compose.yaml: `litellm-database:v1.91.0`
   - Mismatch between skill, Python lib, and Docker image

2. **Missing skill**: No `.agents/skills/llama-swap/SKILL.md`
   despite llama-swap being the primary inference backend for ~52 models

3. **Test coverage gap**: No tests verify the LLM serving stack
   is configured consistently (which models route through which backend,
   what versions are installed, what compose files exist)

This change adds the missing skill, updates the existing skills, and
adds smoke tests that catch version drift + missing files.

## What Changes

### 1. Skill updates
- `.agents/skills/litellm/SKILL.md`: v1.90 → v1.97.0 (matches installed);
  adds "⚠️ CURRENT STATUS" section documenting 52-model catalog
- `.agents/skills/unsloth/SKILL.md`: v2026.6.9 → v2026.9.x; adds status section
- `.agents/skills/llama-swap/SKILL.md`: **NEW** skill with full
  GPU-vs-CPU reality check (per the 2026-08-08-lakehouse-extensive-
  hydration-v1 commit message)

### 2. Health tests
- `tests/llm_serving/__init__.py`: new test package
- `tests/llm_serving/test_llm_serving.py`: 7 tests verifying:
  - `test_litellm_python_lib_installed` — litellm ≥ 1.x
  - `test_litellm_config_model_count` — ≥ 30 models in config
  - `test_litellm_config_local_models_route_to_llama_swap` — local/* uses llama-swap
  - `test_llama_swap_compose_exists` — compose.yaml present + working image
  - `test_unsloth_serve_compose_exists` — unsloth compose present
  - `test_litellm_docker_image_matches_compose` — docker image in major-version family
  - `test_baml_clients_minimax3_is_default` — minimax-m3 dominates BAML clients

## What Does NOT Change

- ❌ No litellm config.yaml edits (52 models is the right count)
- ❌ No compose.yaml edits (images already correct)
- ❌ No new model routes added
- ❌ No new MCP gateway / vector store / workflows adoption (deferred —
  1.97 features not yet used in our config)

## Dependencies

- `Blocked by: none`
- `Affected repos: cianfhoghlaim`
- Soft dependency: `2026-09-12-dlt-1.29-feature-adoption-v1` (Plan 1)
  (DLT pipeline feeds litellm-routed BAML extraction)

## Cross-links

- Sister change: `2026-09-12-baml-health-test-and-skill-update-v1` (Plan 2)
- Sister change: `2026-09-12-dlt-1.29-feature-adoption-v1` (Plan 1)
- Stack compose: `bonneagar/stacks/{litellm,llama-swap,unsloth-serve}/compose.yaml`
- Feature-flag monitor: `docs/firecrawl/monitors/upstream_packages/dlthub_blog.yml`
  (auto-scrapes dlt + litellm + unsloth upstream API changes)
