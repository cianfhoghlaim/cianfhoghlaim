# Tasks: Bridge the shared provider_router into cianfhoghlaim

## Phase 0 — Wholesale copy

- [x] 0.1. Copy `/Users/cianmacandeisigh/dev/cianchosaint/baml_src/_shared/provider_router.py` to `/Users/cianmacandeisigh/dev/cianfhoghlaim/baml_src/_shared/provider_router.py`
- [x] 0.2. Copy `/Users/cianmacandeisigh/dev/cianchosaint/baml_src/_shared/provider_router_config.yaml` to `/Users/cianmacandeisigh/dev/cianfhoghlaim/baml_src/_shared/provider_router_config.yaml`

## Phase 1 — cianfhoghlaim-local extensions

- [x] 1.1. Add the 6 hackathon HF Inference backends to the `Provider` enum
- [x] 1.2. Add the 9 M3 chokepoint aliases (minimax-m3, kimi-k2.6, glm-5.1, minimax-m2.5, mimo-v2.5, deepseek-v4-flash, deepseek-v4-pro, kimi-k2.7-code, kimi-k3) as fallback routes

## Phase 2 — Validation

- [x] 2.1. `openspec validate 2026-09-13-shared-provider-router-bridge-v1 --strict` exits 0
- [x] 2.2. `uv run python -c "from baml_src._shared.provider_router import ProviderRouter; print(ProviderRouter())"` succeeds
- [x] 2.3. `mise run lint:registry` reports `Found 0 hardcoded model strings`

## Phase 3 — Commit + push

- [x] 3.1. `git add baml_src/_shared/provider_router{,_config}.py baml_src/_shared/provider_router_config.yaml`
- [x] 3.2. `git commit -m "feat(baml): bridge shared provider_router from cianchosaint + add 9 M3 chokepoint aliases"`
- [x] 3.3. `git push origin openspec/cianchosaint-handoff-v1`
