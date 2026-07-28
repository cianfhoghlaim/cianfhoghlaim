// BAML Client Configuration for Cianfhoghlaim (post-v4 + baml 0.212+ canonical syntax)
//
// ====== 2026-07-13: scoped to minimax-m3 (coding plan API) ======
// The historical 8-client setup is preserved as a comment block below
// for when more cloud providers (Gemini, OpenAI, Anthropic, etc.) become
// available. The active single text-extraction client is `Default`,
// routing to `minimax-m3` (the M3 model available via the coding plan API).
//
// When API keys for other providers become available, uncomment the relevant
// client<llm> block below and update the default text client deliberately.
//
// Generation: `cd cianfhoghlaim && uv run baml-cli generate --from baml_src`
// Validation: `cd cianfhoghlaim && mise run baml:generate` (alias)

// ====== 8-client historical setup (commented; for when more cloud providers are available) ======
// client<llm> DefaultGPT5Mini {
//   provider "openai"
//   options {
//     base_url env.LITELLM_BASE_URL
//     api_key env.LITELLM_API_KEY
//     model "gpt-5-mini"
//   }
// }
//
// client<llm> LocalVisionQwen {
//   provider "openai"
//   options {
//     base_url env.LITELLM_BASE_URL
//     api_key env.LITELLM_API_KEY
//     model "local/vision/qwen3-vl"
//   }
// }
//
// client<llm> LocalVisionGlm {
//   provider "openai"
//   options {
//     base_url env.LITELLM_BASE_URL
//     api_key env.LITELLM_API_KEY
//     model "local/vision/glm-4.6v-flash"
//   }
// }
//
// client<llm> LocalVisionMoondream {
//   provider "openai"
//   options {
//     base_url env.LITELLM_BASE_URL
//     api_key env.LITELLM_API_KEY
//     model "local/vision/moondream2"
//   }
// }
//
// client<llm> Gemini2Flash {
//   provider "google-ai"
//   options {
//     api_key env.GOOGLE_API_KEY
//     model "gemini-2.0-flash-exp"
//   }
// }
//
// client<llm> Gemini15Pro {
//   provider "google-ai"
//   options {
//     api_key env.GOOGLE_API_KEY
//     model "gemini-1.5-pro-latest"
//   }
// }
//
// client<llm> GeminiPro {
//   provider "google-ai"
//   options {
//     api_key env.GOOGLE_API_KEY
//     model "gemini-pro"
//   }
// }
//
// client<llm> Gemini25Flash {
//   provider "google-ai"
//   options {
//     api_key env.GOOGLE_API_KEY
//     model "gemini-2.5-flash-preview-05-20"
//   }
// }

// ====== Active text client (Default) ======

client<llm> Default {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
    model "minimax-m3"
  }
}

// ====== Local vision clients (active) ======

client<llm> LocalVisionGemma4 {
  provider "openai"
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
    model "local/vision/gemma-4-26B-A4B"
  }
}

client<llm> LocalVisionQwen3vl {
  provider "openai"
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
    model "local/vision/qwen3-vl-8b"
  }
}

// ====== Canonical named clients referenced across BAML functions ======
// These are the historical aliases used by the various function definitions.
// They route to the canonical minimax-m3 text client by default, so all
// extraction functions share the same M3 provider.
//
// Note: Validator / IrishValidator / Analyzer are defined in
// processing/ocr_validation.baml (with their original OpenAI configs);
// they are intentionally NOT redeclared here to avoid duplicate definitions.

client<llm> LitellmClient {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
    model "minimax-m3"
  }
}

client<llm> ExtractEn {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
    model "minimax-m3"
  }
}

client<llm> ExtractEnStrong {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
    model "minimax-m3"
  }
}

client<llm> LocalVision {
  provider "openai"
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
    model "local/vision/qwen3-vl-8b"
  }
}

// ====== Generic aliases for the canonical mini-llm registry ======
// (Functions in the wider BAML tree reference these aliases; they all
// route to minimax-m3 for text extraction. Replace with proper provider-
// specific blocks when the relevant API keys land in dev-baile.)

client<llm> ArtworkAnalyzer     { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }
client<llm> CelticContentFallback { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }
// Claude / ClaudeMini / ClaudeOpus are defined in
// education/cross_nation/multi_nation_curriculum.baml (Anthropic Claude configs).
// They are intentionally NOT redeclared here.
// ClaudeHaiku is an alias for ClaudeMini (both target Claude 3.5 Haiku).
client<llm> ClaudeHaiku         { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }
client<llm> Extractor           { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }
client<llm> ExtractorFast       { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }
client<llm> FastAnalyzer        { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }
client<llm> FastExtraction      { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }
client<llm> Gemini2FlashAlias   { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }
client<llm> LiteLLM             { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }
client<llm> OideachaisDefault   { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }
client<llm> VisionExtractor     { provider "openai"         options { base_url env.LITELLM_BASE_URL api_key env.LITELLM_API_KEY model "local/vision/qwen3-vl-8b" } }

// ====== BIEP v3 canonical 3 clients (2026-08-13-biep-v3-systematic-download-ireland-england-v1) ======
// Per the 2026-08-07-biep-v3-hardening-v1 + 2026-08-13 changes.
// These 3 clients are the canonical home for new BIEP v3 BAML functions.
// The legacy `ExtractEn` / `ExtractEnStrong` / `LocalVision` clients
// remain active for backwards compatibility but new BIEP v3 functions
// MUST route through these 3 canonical clients.

client<llm> BIEPV3Extract {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
    model "minimax-m3"
  }
  retry_policy Exponential
}

client<llm> BIEPV3ExtractStrong {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
    model "minimax-m3"
  }
  retry_policy Exponential
}

client<llm> BIEPV3Vision {
  provider "openai"
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
    model "local/vision/qwen3-vl-8b"
  }
  retry_policy Exponential
}

// ── Retry policies ──

retry_policy Simple {
  max_retries 2
  strategy {
    type exponential_backoff
    delay_ms 500
    multiplier 2
  }
}

retry_policy Exponential {
  max_retries 3
  strategy {
    type exponential_backoff
    delay_ms 200
    multiplier 1.5
  }
}