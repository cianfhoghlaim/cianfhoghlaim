// BAML client definitions for the oideachais data platform.
//
// All LLM calls go through the LiteLLM gateway at `http://litellm:4000/v1`.
// The LiteLLM config (infrastructure/stacks/engineering/litellm/config/config.yaml)
// maps model aliases to actual providers (DeepSeek, OpenCode Go, etc.).
//
// Usage in BAML schemas:
//   client "litellm"
//
// Re-gen after changes:  `cd oideachais && uv run baml-cli generate`
//
// NOTE: LitellmClient defaults to deepseek-chat via the litellm gateway,
// NOT gemini — the local .env GEMINI_API_KEY belongs to a dead GCP project
// and /gemini/api_key is not in the Infisical vault yet (issue #12).
// When the vault has a working Gemini key, flip back to gemini-2.5-flash.

client<llm> LitellmClient {
  provider openai
  options {
    api_key env.LLM_API_KEY
    base_url "http://litellm:4000/v1"
    model "deepseek/deepseek-chat"
  }
}

client<llm> DeepSeekClient {
  provider openai
  options {
    api_key env.DEEPSEEK_API_KEY
    base_url "https://api.deepseek.com/v1"
    model "deepseek-v4-pro"
  }
}

// MiniMax-M3 via the LiteLLM gateway alias `minimax` (vendor-de-risked).
// See infrastructure/stacks/litellm/config/config.yaml for the full
// fallback chain (3-key rotation → qwen3.7-max → kimi-k2.6 → glm-4.6
// → local qwen-math). Driven by openspec/changes/
// litellm-minimax-vendor-derisking/.
//
// The previous version of this client pointed directly at the opencode-go
// gateway with a single key — that left a single point of failure
// (gateway outage, key cap, regional unavailability) with no fallback.
// Use this client instead whenever the old `MiniMaxClient` is referenced.
client<llm> MiniMaxClient {
  provider openai
  options {
    api_key env.LITELLM_MASTER_KEY
    base_url "http://litellm:4000/v1"
    model "minimax"
  }
}

client<llm> LitellmLongContext {
  provider openai
  options {
    api_key env.LLM_API_KEY
    base_url "http://litellm:4000/v1"
    model "deepseek/deepseek-chat"
  }
}

// Canonical "Extractor" client used by the BAML files in
// oideachais/baml_src/{audio_extraction,ocr_extraction,ocr_validation,
// gaois/duchas,gaois/folklore_extraction,gaois/logainm,gaois/tearma}.baml.
// Kept here (not inline) so the model/provider config is canonical.
client<llm> Extractor {
  provider openai
  options {
    api_key env.LLM_API_KEY
    base_url "http://litellm:4000/v1"
    model "gpt-4o-mini"
    temperature 0.1
  }
}
