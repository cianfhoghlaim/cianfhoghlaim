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

client<llm> MiniMaxClient {
  provider openai
  options {
    api_key env.OPENCODE_GO_API_KEY
    base_url "https://opencode.ai/zen/go/v1/messages"
    model "minimax-m3"
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
