// BAML client for the Irish-language LC subject pilot (per the 2026-08-10-baml-extraction-completion-v1 change).
//
// Routes through LiteLLM `uccix-mistral-24b` (the Modern Irish language path
// from MODEL_REGISTRY), not MiniMax-M3 (the default for English).
//
// Use this client for any BAML function invoked from the gaeilge subject
// pilot (or any other Irish-language extraction).

client<llm> GaeilgeLCClient {
  provider "openai-generic"
  options {
    base_url "http://litellm:4000/v1"
    api_key env.MISTRAL_API_KEY
    model "uccix-mistral-24b"
    max_tokens 8192
    temperature 0.0
  }
}

retry_policy GaeilgeLCRetry {
  max_retries 3
  strategy {
    type exponential_backoff
    delay 2000
  }
}
