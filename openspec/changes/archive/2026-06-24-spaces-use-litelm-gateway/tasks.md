# Tasks: spaces-use-litelm-gateway

## 1. Rewrite baml_client.py

- [x] Add `LITELLM_BASE_URL`, `DEFAULT_MODEL`, `LITELLM_MASTER_KEY`
      constants pointing at the canonical LiteLLM gateway
- [x] Add `_try_litellm()` helper that POSTs to the gateway with the
      same OpenAI-compatible body shape
- [x] Update `chat_complete()` to try LiteLLM first, fall back to
      the 3-tier HF Inference chain on failure
- [x] Update `get_hackathon_client_config()` to return the LiteLLM
      config + the HF fallback chain + the HF token status
- [x] Preserve the existing `chat_complete_json()` signature

## 2. Validate

- [x] `openspec validate spaces-use-litelm-gateway --strict`
- [x] Verify the 4 callers (`an_scrudu/extraction.py`,
      `meaisin_cliste/curaclam.py`, `cianfhoghlaim/app.py`,
      `anam_sruth/tuatha/mac_leinn.py`) work without changes (signatures
      preserved)

## 3. Commit + push + archive

- [x] Commit with message
      `spaces-use-litelm-gateway: 4 Spaces route through the canonical LiteLLM gateway`
- [x] Archive the openspec change
- [x] `git push`
