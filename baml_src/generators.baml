// BAML Generators Configuration for Oideachais / Cianfhoghlaim
// All clients route through the canonical LiteLLM gateway. See
// baml_src/clients.baml for the primary client definitions.

generator lang_py {
  output_type python/pydantic
  output_dir ../baml_client
  version "0.74.0"
  default_client_mode sync
}

// =============================================================================
// Note: the `client<llm>` blocks previously declared here (Claude, Gemini, GPT4,
// Ollama) have been removed in favour of the unified LiteLLM client in
// baml_src/clients.baml. Every BAML function should declare `client LiteLLM`
// (or one of the gateway-aware aliases: LocalVision, LocalOCR, LocalIrish,
// LocalMath, ImageGen). The gateway handles fallback, tracing, rate limits.
// =============================================================================
