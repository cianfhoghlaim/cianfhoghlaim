## Why

The 4 HuggingFace Spaces (`an_scrudu`, `meaisin_cliste`,
`cianfhoghlaim`, `anam_tuatha`) + the shared `spaces/_common/`
bundle all use a hand-rolled `baml_client.py` that calls
**raw `api-inference.huggingface.co`** with a 3-tier
Qwen 7B → Llama 8B → Gemma 9b fallback chain. This bypasses the
canonical KCG LiteLLM gateway (`http://litellm:4000/v1`), losing:

- **Single LLM endpoint** — every Space maintains its own HF
  token, model config, and fallback chain
- **LLM observability** — Langfuse auto-traces every LiteLLM call
  but does NOT see raw HF Inference calls
- **Cost tracking** — per-model cost lines in Langfuse are
  unavailable
- **The canonical fallback chain** — `sruth/oideachais/baml_src/clients.baml`
  has a 5-key rotation (minimax-m3 → kimi-k2.6 → glm-4.6 → ...
  → local qwen-math) that the Spaces cannot use

This change rewrites `spaces/_common/baml_client.py` to use the
canonical LiteLLM gateway as the primary tier, with the
hand-rolled HF Inference chain kept as the offline / dev /
HF Space free tier fallback.

After this change:
- The 4 Spaces route through `http://litellm:4000/v1` when
  the gateway is reachable
- Langfuse auto-traces every call (cost + latency + model)
- The Spaces get the canonical 5-key rotation via the
  LiteLLM gateway config
- The HF Inference fallback is preserved verbatim for offline
  mode (no functional regression)

The 4 hand-rolled Spaces do not need to change their callers
(`chat_complete_json` and `get_hackathon_client_config` have
the same signatures). Only the internal implementation changes.

## What changes

- `spaces/_common/baml_client.py` — rewrite to add the LiteLLM
  gateway tier at the top of `chat_complete()`, keep the HF
  Inference 3-tier chain as the offline fallback
- `spaces/_common/__init__.py` — no change (signatures preserved)
- 1 ADDED Requirement to the `infrastructure-stacks` spec

## Out of scope

- A1: promote hackathon BAML to canonical (already done)
- C1-C4: per-Space modernization (separate changes)
- A2 does not require regenerating baml_client/ — the existing
  `_common/baml_client.py` stays as a thin shim, the new
  `sruth/oideachais/baml_src/circular_extraction.baml` and the 3
  tuatha BAML files are used by the cross-quadrant agents
  directly, not by the Spaces
