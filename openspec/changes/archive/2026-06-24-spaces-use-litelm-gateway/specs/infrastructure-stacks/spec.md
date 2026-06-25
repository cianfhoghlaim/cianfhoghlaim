## ADDED Requirements

### Requirement: Spaces route through the canonical LiteLLM gateway

The Cianfhoghlaim HuggingFace Spaces (`an_scrudu`, `meaisin_cliste`, `cianfhoghlaim`, `anam_tuatha`, `data-engineering`) MUST route every LLM call through the canonical LiteLLM gateway (`http://litellm:4000/v1`) as the primary tier, with the hand-rolled HF Inference 3-tier chain kept as the offline fallback. The gateway is configured in `sruth/oideachais/baml_src/clients.baml` (the `LitellmClient`) and `sruth/oideachais/foinse/litellm_config.yaml` (the 5-key rotation).

#### Scenario: Space calls LLM via the gateway

- **WHEN** a Space (e.g. `an_scrudu/extraction.py`) calls `chat_complete_json(messages=...)`
- **THEN** the underlying `chat_complete()` first tries the LiteLLM gateway with the canonical model (`minimax` by default)
- **AND** if the gateway is unreachable (offline / dev / HF free tier), it falls back to the HF Inference 3-tier chain (Qwen 7B → Llama 8B → Gemma 9b)

#### Scenario: Langfuse auto-traces every Space LLM call

- **WHEN** the LiteLLM gateway is the tier that responds
- **THEN** Langfuse records the call with cost + latency + model (because the gateway is the same proxy that every KCG agent uses)
- **AND** the HF Inference fallback is invisible to Langfuse (acceptable: it only fires when the gateway is down)
