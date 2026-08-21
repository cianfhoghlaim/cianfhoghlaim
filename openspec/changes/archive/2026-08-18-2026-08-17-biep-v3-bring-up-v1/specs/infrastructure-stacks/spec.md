# infrastructure-stacks

## ADDED Requirements

### Requirement: litellm router_settings.fallbacks invariant

The system SHALL fail `mise run lint:litellm-router-fallbacks` if any
`bonneagar/stacks/litellm/config/config.yaml` section declares
`router_settings.fallbacks` as a bare list of model-name strings
rather than the `{primary_model: [fallback_model, ...]}` dict form.

The reason: per the `2026-07-29-lakehouse-extensive-hydration-v1`
change, litellm 1.x's `Router.validate_fallbacks()` rejects bare
lists outright ("Item 'qwen3-vl-8b' is not a dictionary") and
crash-loops the entire litellm container on every startup attempt
(verified via `docker logs litellm`). The fix is the dict form, now
applied at `bonneagar/stacks/litellm/config/config.yaml:645-647`:
```yaml
fallbacks:
  - qwen3-vl-8b: [gemma-4-26B-A4B, glm-4.6v-flash, openai/glm-4.6, gemini/gemini-2.5-pro]
```

This lint gate prevents regression to the bare-list form (which
crash-looped the container before the `2026-07-29` fix).

#### Scenario: Operator adds a new fallback as a bare list

- **WHEN** a developer adds the following to
  `bonneagar/stacks/litellm/config/config.yaml`:
  ```yaml
  router_settings:
    fallbacks: [gpt-5, claude-opus-4]
  ```
- **THEN** `mise run lint:litellm-router-fallbacks` exits 1 with
  `router_settings.fallbacks: bare list (not dict form) — crash-loops litellm. Use {[primary_model]: [fallback_model, ...]} form.`

#### Scenario: Fallback chain uses the dict form

- **WHEN** the config uses the canonical dict form:
  ```yaml
  router_settings:
    fallbacks:
      - qwen3-vl-8b: [gemma-4-26B-A4B, glm-4.6v-flash]
  ```
- **THEN** the lint exits 0

#### Scenario: Per-model fallbacks (the 8 mini-fallbacks)

- **WHEN** per-model fallbacks in `model_list:` blocks use the
  per-model `litellm_params.fallbacks:` array (the v1.x pattern for
  per-model, not per-router fallback chains)
- **THEN** the lint allows them (they're per-model, not the
  router-level crash-loop risk)