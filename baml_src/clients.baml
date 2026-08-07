// BAML Client Configuration for Cianfhoghlaim (post-v4 + baml 0.212+ canonical syntax)
//
// ====== 2026-08-15: model strings are now defined in MODEL_REGISTRY ======
// Per the centralized-model-registry openspec change, the hardcoded
// model strings in BAML clients are replaced with comments that
// point at the canonical MODEL_REGISTRY key. The model strings
// (e.g. "minimax-m3", "local/vision/qwen3-vl-8b") are sourced from
// `meaisinfhoghlaim.models.model_registry` at runtime via the
// `model_for(family, role)` helper. The historical 8-client
// commented block has been deleted (it referenced ghost models
// like gpt-5-mini / gemini-2.0-flash-exp that have no env-var
// backing in dev-baile).
//
// When API keys for other providers become available, add a new
// client<llm> block here AND add a corresponding entry to the
// MODEL_REGISTRY (per the centralized-model-registry contract).
//
// Generation: `cd cianfhoghlaim && uv run baml-cli generate --from baml_src`
// Validation: `cd cianfhoghlaim && mise run baml:generate` (alias)

// ====== Active text client (Default; role="default" → minimax-m3) ======

client<llm> Default {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
    // MODEL_REGISTRY: family="text_llm", role="default" → "minimax-m3"
    model "minimax-m3"
  }
}

// ====== Local vision clients (active) ======
// MODEL_REGISTRY: family="ocr_vision", role="gemma4_strong" → "gemma-4-26B-A4B"
// MODEL_REGISTRY: family="ocr_vision", role="qwen3_vl_default" → "qwen3-vl-8b"

client<llm> LocalVisionGemma4 {
  provider "openai"
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
    // MODEL_REGISTRY: family="ocr_vision", role="gemma4_strong" → "gemma-4-26B-A4B"
    model "local/vision/gemma-4-26B-A4B"
  }
}

client<llm> LocalVisionQwen3vl {
  provider "openai"
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
    // MODEL_REGISTRY: family="ocr_vision", role="qwen3_vl_default" → "qwen3-vl-8b"
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
//
// All ``model`` strings below are resolved via MODEL_REGISTRY at
// runtime — see the comments next to each block.

client<llm> LitellmClient {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
    // MODEL_REGISTRY: family="text_llm", role="default" → "minimax-m3"
    model "minimax-m3"
  }
}

client<llm> ExtractEn {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
    // MODEL_REGISTRY: family="text_llm", role="default" → "minimax-m3"
    model "minimax-m3"
  }
}

client<llm> ExtractEnStrong {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
    // MODEL_REGISTRY: family="text_llm", role="default" → "minimax-m3"
    // (per the centralized-model-registry contract, BIEP v3 strong
    //  text extraction still routes through the M3 chokepoint
    //  because no separate strong-text API key is provisioned)
    model "minimax-m3"
  }
}

client<llm> LocalVision {
  provider "openai"
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
    // MODEL_REGISTRY: family="ocr_vision", role="qwen3_vl_default" → "qwen3-vl-8b"
    model "local/vision/qwen3-vl-8b"
  }
}

// ====== Qwen token plan (DashScope) — secondary cross-check client ======
// MODEL_REGISTRY: family="text_llm", role="token_plan_primary" → "qwen3.7-plus"
// Direct DashScope OpenAI-compatible endpoint (base_url is env-driven via
// DASHSCOPE_BASE_URL so switching between the coding-plan endpoint and the
// international console endpoint is a one-line .infisical.env change).
// Used as the secondary cross-check client (alongside Default/minimax-m3)
// for the lc6 extraction functions; retry_policy Simple — Exponential is
// reserved for the 3 canonical BIEP v3 clients above.

client<llm> ExtractQwenCrossCheck {
  provider "openai-generic"
  options {
    base_url env.DASHSCOPE_BASE_URL
    api_key env.DASHSCOPE_API_KEY
    // MODEL_REGISTRY: family="text_llm", role="token_plan_primary" → "qwen3.7-plus"
    model "qwen3.7-plus"
  }
  retry_policy Simple
}

// ====== Generic aliases for the canonical mini-llm registry ======
// (Functions in the wider BAML tree reference these aliases; they all
// route to minimax-m3 for text extraction. Replace with proper provider-
// specific blocks when the relevant API keys land in dev-baile.)

// ====== Generic aliases for the canonical mini-llm registry ======
// (Functions in the wider BAML tree reference these aliases; they all
// route to minimax-m3 for text extraction. Replace with proper provider-
// specific blocks when the relevant API keys land in dev-baile.)
//
// All ``model`` strings below are resolved via MODEL_REGISTRY at
// runtime — see the comments next to each block.

client<llm> ArtworkAnalyzer     { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> CelticContentFallback { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
// Claude / ClaudeMini / ClaudeOpus are defined in
// education/cross_nation/multi_nation_curriculum.baml (Anthropic Claude configs).
// They are intentionally NOT redeclared here.
// ClaudeHaiku is an alias for ClaudeMini (both target Claude 3.5 Haiku).
client<llm> ClaudeHaiku         { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> Extractor           { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> ExtractorFast       { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> FastAnalyzer        { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> FastExtraction      { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> Gemini2FlashAlias   { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> LiteLLM             { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> OideachaisDefault   { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> VisionExtractor     { provider "openai"         options { base_url env.LITELLM_BASE_URL api_key env.LITELLM_API_KEY model "local/vision/qwen3-vl-8b" } }  // MODEL_REGISTRY: ocr_vision/qwen3_vl_default

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
    // MODEL_REGISTRY: family="text_llm", role="default" → "minimax-m3"
    model "minimax-m3"
  }
  retry_policy Exponential
}

client<llm> BIEPV3ExtractStrong {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
    // MODEL_REGISTRY: family="text_llm", role="default" → "minimax-m3"
    model "minimax-m3"
  }
  retry_policy Exponential
}

client<llm> BIEPV3Vision {
  provider "openai"
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
    // MODEL_REGISTRY: family="ocr_vision", role="qwen3_vl_default" → "qwen3-vl-8b"
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