// BAML client definitions for the oideachais data platform.
//
// All LLM calls go through the LiteLLM gateway at `http://litellm:4000/v1`.
// The LiteLLM config (infrastructure/stacks/engineering/litellm/config/config.yaml)
// maps model aliases to actual providers (Gemini, DeepSeek, MiniMax, etc.).
//
// Usage in BAML schemas:
//   client "litellm"
//
// Re-gen after changes:  `cd oideachais && uv run baml-cli generate`

client<llm> LitellmClient {
  provider openai
  options {
    api_key env.LLM_API_KEY
    base_url "http://litellm:4000/v1"
    model "gemini/gemini-2.5-flash"
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
    model "gemini/gemini-2.5-pro"
  }
}
