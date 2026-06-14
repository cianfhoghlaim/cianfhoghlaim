// BAML Client Configuration for Cianfhoghlaim / Oideachais
// All clients route through the canonical LiteLLM gateway at
// infrastructure/stacks/engineering/litellm. This gives us:
//   - Unified fallback chains (see gateway config.yaml)
//   - Langfuse tracing for every BAML call
//   - Cost / rate limit enforcement in one place
//   - Cloud + local model coverage (Gemini, GLM, OpenAI, OpenCode Go,
//     llama-swap GGUF, mlx-omni MLX, InvokeAI image gen)
//
// Environment variables (injected by mise/Locket from Infisical):
//   LITELLM_BASE_URL     e.g. http://litellm:4000/v1
//   LITELLM_MASTER_KEY   e.g. sk-...
//   GEMINI_API_KEY       (used by LiteLLM cloud provider, not by BAML directly)
//   OPENCODE_GO_API_KEY  (used by LiteLLM opencode-go/* routes)

retry_policy Simple {
  max_retries 2
  strategy {
    type exponential_backoff
    delay_ms 500
    multiplier 2
  }
}

// =============================================================================
// LiteLLM gateway client (primary — use this everywhere)
// =============================================================================
client<llm> LiteLLM {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_MASTER_KEY
    model "extract"   // gateway alias → gemini-2.5-pro → glm-4.6 → gemini-flash
  }
  retry_policy Simple
}

// =============================================================================
// Gemini 2.5 Pro direct client (when bypassing the gateway for low-level
// debugging only — production should always go through LiteLLM)
// =============================================================================
client<llm> Gemini25Pro {
  provider google-ai
  options {
    model "gemini-2.5-pro"
    api_key env.GEMINI_API_KEY
  }
}

// =============================================================================
// Gemini 2.5 Flash direct (high-throughput OCR / fallback)
// =============================================================================
client<llm> Gemini25Flash {
  provider google-ai
  options {
    model "gemini-2.5-flash"
    api_key env.GEMINI_API_KEY
  }
}

// =============================================================================
// Gemini 3 Flash Preview (opt-in — set USE_GEMINI_3=true in the gateway)
// =============================================================================
client<llm> Gemini3FlashPreview {
  provider google-ai
  options {
    model "gemini-3.0-flash-preview"
    api_key env.GEMINI_API_KEY
  }
}

// =============================================================================
// OpenCode Go passthrough (subscription models per Go.md)
// =============================================================================
client<llm> OpenCodeGo {
  provider openai
  options {
    base_url "https://opencode.ai/zen/go/v1/chat/completions"
    api_key env.OPENCODE_GO_API_KEY
    model "deepseek-v4-flash"
  }
}

// =============================================================================
// Local self-hosted via the gateway (Qwen2.5-VL, UCCIX, olmOCR, Granite Docling)
// =============================================================================
client<llm> LocalVision {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_MASTER_KEY
    model "vision"   // gateway alias → local/vision/qwen25-vl → ... → gemini-flash
  }
}

client<llm> LocalOCR {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_MASTER_KEY
    model "ocr"   // gateway alias → local/ocr/olmocr-mlx → ... → gemini-flash
  }
}

client<llm> LocalIrish {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_MASTER_KEY
    model "irish"   // gateway alias → UCCIX → Qwen2.5-Math → gemini-flash
  }
}

client<llm> LocalMath {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_MASTER_KEY
    model "math"   // gateway alias → Qwen2.5-Math-7B
  }
}

// =============================================================================
// Image generation client (FIBO JSON config + Z-Image-Turbo fallback)
// =============================================================================
client<llm> ImageGen {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_MASTER_KEY
    model "image-fibo"   // gateway alias → FIBO MLX → Z-Image-Turbo
  }
}

// =============================================================================
// English-only extract clients (author-archive pipeline)
// =============================================================================
// `ExtractEn` is the default for `baml_src/author_archive.baml` functions.
// Routes through the LiteLLM gateway alias `extract-en` which the gateway
// resolves to gemini-2.5-flash → glm-4.6 → gemini-1.5-flash.
client<llm> ExtractEn {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_MASTER_KEY
    model "extract-en"
  }
  retry_policy Simple
}

// `ExtractEnStrong` is the fallback for difficult extractions (math / dense legal).
// Routes through the gateway alias `extract-en-strong` which resolves to
// anthropic/claude-sonnet-4 → gemini-2.5-pro → gemini-1.5-pro.
client<llm> ExtractEnStrong {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_MASTER_KEY
    model "extract-en-strong"
  }
  retry_policy Simple
}
