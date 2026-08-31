// BAML Client Configuration for Cianfhoghlaim v5
//
// ============================================================================
// 2026-08-31: BAML switching strategy (per the v5 model priority change)
// ============================================================================
// 3 layers stacked: a single canonical `Primary` alias per BAML function,
// a MODEL_PROFILE env-driven dispatch, and a per-function `fallback` chain.
//
// Switching the primary model = changing one of 3 knobs:
//   (a) Env-driven primary  —  MODEL_BASE_URL / MODEL_API_KEY / MODEL_PRIMARY
//                              in .env routes the `Primary` client to whatever
//                              backend the env vars point at. Default = MiniMax.
//   (b) Per-function `client "X"` override  —  swap the client block in the
//                                              function header (e.g. for Irish
//                                              LC via `GaeilgeLCClient`).
//   (c) Per-function `fallback` chain      —  chain `Primary -> UnslothGemma4
//                                              -> VertexGemini35Flash` so the
//                                              function tries the next tier
//                                              if the previous fails.
//
// All concrete clients are wired here + all 33 legacy aliases route to
// them. New BAML functions MUST declare `client "Primary"` (or a domain-
// specific override like `GaeilgeLCClient`).
// ============================================================================

// ----------------------------------------------------------------------------
// Retry policies
// ----------------------------------------------------------------------------

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

// 2026-08-31: 3 new retry policies for the 3-tier model chain.
// Tier 1 (MiniMax / Vertex) is most expensive + most reliable; high retry count.
// Tier 2 (Unsloth Gemma 4) is local; medium retry.
// Tier 3 (Gemini 3.5 Flash / AI Studio) is API; low retry (rate-limit-aware).
retry_policy Tier1 {
  max_retries 3
  strategy {
    type exponential_backoff
    delay_ms 1000
    multiplier 2
    max_delay_ms 30000
  }
}
retry_policy Tier2 {
  max_retries 2
  strategy {
    type constant_delay
    delay_ms 2000
  }
}
retry_policy Tier3 {
  max_retries 1
  strategy {
    type constant_delay
    delay_ms 500
  }
}

// ----------------------------------------------------------------------------
// Tier 1 PRIMARY — MiniMax M3 (cloud, BIEP chokepoint)
// ----------------------------------------------------------------------------

client<llm> MiniMaxPrimary {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key  env.MINIMAX_API_KEY
    model    "minimax-m3"
    temperature 0.2
    top_p 0.95
  }
  retry_policy Tier1
}

// 2026-08-31: Strong-extraction variant uses the new v2 key
// (per the 2026-08-31-cianfhoghlaim-v5-opencode-model-priority-v1 change).
client<llm> MiniMaxPrimaryStrong {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key  env.MINIMAX_API_KEY_V2
    model    "minimax-m3"
    temperature 0.1
    top_p 0.95
  }
  retry_policy Tier1
}

// ----------------------------------------------------------------------------
// Tier 1 ALT — Vertex AI Gemini 3.5 Flash (cloud, Google stack integration)
// ----------------------------------------------------------------------------

client<llm> VertexGemini35Flash {
  provider "vertex-ai"
  options {
    model       env.GEMINI_MODEL                    // gemini-3.5-flash
    credentials env.GOOGLE_APPLICATION_CREDENTIALS
    project     env.GOOGLE_CLOUD_PROJECT
    location    env.GOOGLE_CLOUD_LOCATION
    temperature 0.2
    top_p       0.95
  }
  retry_policy Tier3
}

client<llm> AIStudioGemini35Flash {
  provider "openai-generic"
  options {
    base_url "https://generativelanguage.googleapis.com/v1beta/openai"
    api_key  env.GEMINI_API_KEY
    model    "gemini-3.5-flash"
    temperature 0.2
    top_p    0.95
  }
  retry_policy Tier3
}

// ----------------------------------------------------------------------------
// Tier 2 — Unsloth Studio Gemma 4 (local fallback, Unsloth-prioritised)
// ----------------------------------------------------------------------------

client<llm> UnslothGemma4 {
  provider "openai-generic"
  options {
    base_url env.UNSLOTH_BASE_URL
    api_key  env.UNSLOTH_API_KEY
    model    env.UNSLOTH_MODEL
    temperature 0.1
    top_p    0.95
  }
  retry_policy Tier2
}

client<llm> UnslothGemma4Light {
  provider "openai-generic"
  options {
    base_url env.UNSLOTH_BASE_URL
    api_key  env.UNSLOTH_API_KEY
    model    "unsloth/gemma-4-E4B-it-GGUF"
    temperature 0.1
    top_p    0.95
  }
  retry_policy Tier2
}

// ----------------------------------------------------------------------------
// OCR / VLM — llama-swap via LiteLLM (Gemma 4 vision)
// ----------------------------------------------------------------------------

client<llm> LlamaSwapGemma4Vision {
  provider "openai"
  options {
    base_url env.LITELLM_BASE_URL
    api_key  env.LITELLM_API_KEY
    // 2026-08-31: Qwen3-VL-8B replaced with Gemma 4 26B-A4B-vision
    model    "local/ocr/gemma-4-26B-A4B-vision"
  }
  retry_policy Tier2
}

// ----------------------------------------------------------------------------
// TEST mock (deterministic, no network — for `baml-cli test`)
// ----------------------------------------------------------------------------

client<llm> TestMock {
  provider "openai-generic"
  options {
    base_url "http://localhost:0"
    api_key  "test"
    model    "gpt-4o-mini"
  }
  retry_policy Tier1
}

// ----------------------------------------------------------------------------
// PRIMARY — the canonical client every BAML function references.
// Routes by MODEL_BASE_URL / MODEL_API_KEY / MODEL_PRIMARY env vars.
// Default = MiniMax M3 (BIEP chokepoint). Override MODEL_PRIMARY to
// switch the entire BIEP to Gemma 4 / Gemini 3.5 / etc.
// ----------------------------------------------------------------------------

client<llm> Primary {
  provider "openai-generic"
  options {
    base_url   env.MODEL_BASE_URL       // drives the dynamic primary
    api_key    env.MODEL_API_KEY        // drives the dynamic primary
    model      env.MODEL_PRIMARY        // "minimax-m3" | "gemma-4-26b-a4b" | "gemini-3.5-flash"
    temperature 0.2
    top_p      0.95
  }
  retry_policy Tier1
}

// ----------------------------------------------------------------------------
// Historical aliases — kept on M3 chokepoint for BIEP parity.
// New BAML functions MUST use `Primary`. Override per-function via
// `client "GaeilgeLCClient"` or the per-function fallback chain.
// ----------------------------------------------------------------------------

// Default + LitellmClient — aliases for the canonical MiniMax primary.
client<llm> Default {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key  env.MINIMAX_API_KEY
    // MODEL_REGISTRY: family="text_llm", role="default" → "minimax-m3"
    model "minimax-m3"
  }
  retry_policy Simple
}

client<llm> LitellmClient {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key  env.MINIMAX_API_KEY
    model "minimax-m3"
  }
  retry_policy Simple
}

// 2026-08-31: LocalVision* updated — Gemma 4 vision replaces Qwen3-VL.
client<llm> LocalVision {
  provider "openai"
  options {
    base_url env.LITELLM_BASE_URL
    api_key  env.LITELLM_API_KEY
    // MODEL_REGISTRY: family="ocr_vision", role="gemma4_vision_default" → "gemma-4-26B-A4B-vision"
    model "local/ocr/gemma-4-26B-A4B-vision"
  }
  retry_policy Simple
}

client<llm> LocalVisionGemma4 {
  provider "openai"
  options {
    base_url env.LITELLM_BASE_URL
    api_key  env.LITELLM_API_KEY
    // MODEL_REGISTRY: family="ocr_vision", role="gemma4_strong" → "gemma-4-26B-A4B"
    model "local/vision/gemma-4-26B-A4B"
  }
  retry_policy Simple
}

// 2026-08-31: LocalVisionQwen3vl kept as a tombstone shim — emits a
// warning at first use via the BAML fallback chain, then routes to
// the Gemma 4 vision path. Removed from active use.
client<llm> LocalVisionQwen3vl {
  provider "openai"
  options {
    base_url env.LITELLM_BASE_URL
    api_key  env.LITELLM_API_KEY
    // 2026-08-31: qwen3-vl-8b replaced with gemma-4-26B-A4B-vision
    // (the v5 model priority change). Existing functions calling this
    // client are auto-routed to the Gemma 4 path via the fallback chain.
    model "local/ocr/gemma-4-26B-A4B-vision"
  }
  retry_policy Simple
}

// 2026-08-31: ExtractQwenCrossCheck REMOVED — qwen token plan is dead.
// The 4 lc6 BAML extraction functions now use the Primary fallback chain.

// ----------------------------------------------------------------------------
// Legacy aliases (restored from baml_src.bak for backwards compatibility)
// ----------------------------------------------------------------------------

client<llm> ExtractEn {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key  env.MINIMAX_API_KEY
    // MODEL_REGISTRY: family="text_llm", role="default" → "minimax-m3"
    model "minimax-m3"
  }
  // 2026-08-31: kept on M3 chokepoint for BIEP parity. New code MUST use Primary.
  retry_policy Simple
}

client<llm> ExtractEnStrong {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key  env.MINIMAX_API_KEY_V2
    // 2026-08-31: now uses the new v2 key per the v5 model priority change.
    model "minimax-m3"
  }
  retry_policy Simple
}

// 2026-08-31: 8 generic aliases — kept on M3 chokepoint for BIEP parity.
// New BAML functions MUST use `Primary`. Override per-function via
// `client "GaeilgeLCClient"` or the per-function fallback chain.
client<llm> ArtworkAnalyzer        { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> CelticContentFallback  { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> ClaudeHaiku            { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> Extractor              { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> ExtractorFast          { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> FastAnalyzer           { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> FastExtraction         { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> Gemini2FlashAlias      { provider "openai-generic" options { base_url env.MODEL_BASE_URL    api_key env.MODEL_API_KEY      model env.MODEL_PRIMARY   } }  // MODEL_REGISTRY: env-driven (Primary)
client<llm> LiteLLM                { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> OideachaisDefault      { provider "openai-generic" options { base_url env.MINIMAX_BASE_URL api_key env.MINIMAX_API_KEY model "minimax-m3" } }  // MODEL_REGISTRY: text_llm/default
client<llm> VisionExtractor        { provider "openai"         options { base_url env.LITELLM_BASE_URL api_key env.LITELLM_API_KEY model "local/ocr/gemma-4-26B-A4B-vision" } }  // MODEL_REGISTRY: ocr_vision/gemma4_vision_default (qwen3-vl-8b removed)

// ----------------------------------------------------------------------------
// BIEP v3 canonical 3 clients (per 2026-08-13-biep-v3-systematic-download-ireland-england-v1)
// Per the 2026-08-07-biep-v3-hardening-v1 + 2026-08-13 changes.
// These 3 clients are the canonical home for new BIEP v3 BAML functions.
// The legacy `ExtractEn` / `ExtractEnStrong` / `LocalVision` clients
// remain active for backwards compatibility but new BIEP v3 functions
// MUST route through these 3 canonical clients.
// ----------------------------------------------------------------------------

client<llm> BIEPV3Extract {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key  env.MINIMAX_API_KEY
    // MODEL_REGISTRY: family="text_llm", role="default" → "minimax-m3"
    model "minimax-m3"
  }
  retry_policy Exponential
}

client<llm> BIEPV3ExtractStrong {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key  env.MINIMAX_API_KEY_V2
    // 2026-08-31: now uses the new v2 key per the v5 model priority change.
    // MODEL_REGISTRY: family="text_llm", role="default" → "minimax-m3"
    model "minimax-m3"
  }
  retry_policy Exponential
}

client<llm> BIEPV3Vision {
  provider "openai"
  options {
    base_url env.LITELLM_BASE_URL
    api_key  env.LITELLM_API_KEY
    // 2026-08-31: Gemma 4 26B-A4B-vision (was qwen3-vl-8b pre-v5).
    // MODEL_REGISTRY: family="ocr_vision", role="gemma4_vision_default" → "local/ocr/gemma-4-26B-A4B-vision"
    model "local/ocr/gemma-4-26B-A4B-vision"
  }
  retry_policy Exponential
}

// ----------------------------------------------------------------------------
// tuatha_media_intel primary client (per the gemini_hackathon Gemma refocus)
// Used by tuatha_media_intel.baml extraction functions.
// ----------------------------------------------------------------------------

client<llm> MediaIntelPrimary {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key  env.MINIMAX_API_KEY
    // MODEL_REGISTRY: family="text_llm", role="default" → "minimax-m3"
    model "minimax-m3"
  }
  retry_policy Simple
}