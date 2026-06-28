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

// =============================================================================
// Merged from /baml_src/clients.baml (root) on 2026-06-25
// =============================================================================
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
// MiniMax-M3 via the gateway alias `minimax` — vendor-de-risked
// =============================================================================
// Routes through the LiteLLM gateway alias `minimax` (see
// infrastructure/stacks/litellm/config/config.yaml). The alias chains
// 3-key round-robin (OPENCODE_GO_API_KEY_0/1/2) → qwen3.7-max →
// kimi-k2.6 → glm-4.6 (Z.ai direct) → local/math/qwen25-math
// (llama-swap GGUF, fully offline on the MacBook M4).
//
// Use this client instead of `OpenCodeGo` whenever you need a model
// that survives a single-channel outage (gateway, key cap, or
// regional unavailability of opencode-go).
// =============================================================================
client<llm> MiniMax {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_MASTER_KEY
    model "minimax"
  }
  retry_policy Simple
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
