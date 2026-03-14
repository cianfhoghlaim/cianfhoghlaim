// =============================================================================
// BAML GENERATORS CONFIGURATION
// =============================================================================
// Configure BAML to use LiteLLM gateway at llm.cianfhoghlaim.ie
// LiteLLM handles model routing, fallbacks, and API key management
// =============================================================================

// Python client generator
generator python {
  output_dir "../src/gaois/baml_client"
  output_type "python/pydantic"
  version "0.214.0"
}

// =============================================================================
// CLIENT CONFIGURATIONS
// =============================================================================
// All clients route through LiteLLM which provides:
// - Unified API for local (MLX, llama-swap) and cloud (Gemini, Z.ai) models
// - Automatic fallbacks configured in litellm_config.yaml
// - Observability via Langfuse
//
// Fallback Chains:
//   Extraction: gemini-2.5-pro -> glm-4.6v -> gemini-2.5-flash
//   OCR: olmocr2-7b -> granite-docling
//   Vision: qwen3-vl-30b -> glm-4.6v -> gemma-27b-vision
// =============================================================================

// Primary extraction client - Gemini 2.5 Pro with fallbacks
// Fallback chain: gemini-2.5-pro -> glm-4.6v -> gemini-2.5-flash
client<llm> Extractor {
  provider openai
  options {
    base_url env.LITELLM_API_BASE
    api_key env.LITELLM_API_KEY
    model "extract"
  }
}

// High-quality extraction - Gemini 2.5 Pro (same as Extractor but explicit)
client<llm> ExtractorHQ {
  provider openai
  options {
    base_url env.LITELLM_API_BASE
    api_key env.LITELLM_API_KEY
    model "gemini-2.5-pro"
  }
}

// Fast extraction - Local Gemma 3n (lightweight GGUF)
client<llm> ExtractorFast {
  provider openai
  options {
    base_url env.LITELLM_API_BASE
    api_key env.LITELLM_API_KEY
    model "fast"
  }
}

// OCR extraction - Local OLMoCR MLX with fallback to Granite Docling
// Fallback chain: olmocr2-7b -> granite-docling
client<llm> OCRExtractor {
  provider openai
  options {
    base_url env.LITELLM_API_BASE
    api_key env.LITELLM_API_KEY
    model "ocr"
  }
}

// Vision/multimodal - Local Qwen3 VL with fallbacks
// Fallback chain: qwen3-vl-30b -> glm-4.6v -> gemma-27b-vision
client<llm> VisionExtractor {
  provider openai
  options {
    base_url env.LITELLM_API_BASE
    api_key env.LITELLM_API_KEY
    model "vision"
  }
}

// Document understanding - Granite Docling (IBM MLX)
// Used as OCR fallback and for document layout analysis
client<llm> DocumentExtractor {
  provider openai
  options {
    base_url env.LITELLM_API_BASE
    api_key env.LITELLM_API_KEY
    model "document"
  }
}

// =============================================================================
// FALLBACK CHAIN CLIENT
// =============================================================================
// Uses LiteLLM's built-in fallback mechanism:
// gemini-2.5-pro -> glm-4.6v -> gemini-2.5-flash
// =============================================================================

client<llm> ExtractorWithFallback {
  provider openai
  retry_policy Resilient
  options {
    base_url env.LITELLM_API_BASE
    api_key env.LITELLM_API_KEY
    model "extract"
  }
}

// =============================================================================
// RETRY POLICIES
// =============================================================================

retry_policy Resilient {
  max_retries 3
  strategy {
    type exponential_backoff
    delay_ms 500
    multiplier 2
    max_delay_ms 10000
  }
}

retry_policy Quick {
  max_retries 2
  strategy {
    type constant_delay
    delay_ms 200
  }
}
