// BAML Client Configuration for Cianfhoghlaim (post-v4 + post-Phase-1 consolidation 2026-06-30)
//
// Canonical clients.baml consolidates the legacy clients.baml + clients_0.baml.
// The llama-swap specialty clients live in clients_llama_swap.baml.
//
// Generation: `cd cianfhoghlaim && uv run baml-cli generate`
// Validation: `cd cianfhoghlaim && mise run baml:generate` (alias)

// ── Section 1: Local LiteLLM-routed vision clients (post-v4) ──

// Primary vision model - Qwen3 VL 30B
client LocalVisionQwen {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
    model "local/vision/qwen3-vl"
  }
}

// Fast vision model - GLM 4.6V Flash
client LocalVisionGLM {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
    model "local/vision/glm-4.6v-flash"
  }
}

// Lightweight vision - Moondream2
client LocalVisionMoondream {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
    model "local/vision/moondream2"
  }
}

// ── Section 2: Cloud Google clients (consolidated from legacy clients_0.baml) ──

// Primary extraction model - Gemini 2.0 Flash (free tier)
client Gemini2Flash {
  provider google-ai
  options {
    model "gemini-2.0-flash-exp"
    api_key env.GOOGLE_API_KEY
  }
}

// Cloud fallback - Gemini 1.5 Pro
client Gemini15Pro {
  provider google-ai
  options {
    model gemini-1.5-pro-latest
    api_key env.GOOGLE_API_KEY
  }
}

// Standard Gemini Pro
client GeminiPro {
  provider google-ai
  options {
    model "gemini-pro"
    api_key env.GOOGLE_API_KEY
  }
}

// Fast cloud - Gemini 2.5 Flash
client Gemini25Flash {
  provider google-ai
  options {
    model gemini-2.5-flash-preview-05-20
    api_key env.GOOGLE_API_KEY
  }
}

// ── Section 3: Retry policies (consolidated from clients_0.baml) ──

retry_policy Simple {
  max_retries 2
  strategy {
    type exponential_backoff
    delay_ms 500
    multiplier 2
  }
}

// ── Section 4: Default client + fallback chains ──

// Default client for retries (consolidated from clients_0.baml)
client Default {
  provider google-ai
  retry_policy Simple
  options {
    model "gemini-2.0-flash-exp"
    api_key env.GOOGLE_API_KEY
  }
}

// Fallback chain for artwork analysis
client ArtworkAnalyzer {
  provider fallback
  options {
    strategy [LocalVisionQwen, LocalVisionGLM, Gemini15Pro]
  }
}

// Fast analysis chain
client FastAnalyzer {
  provider fallback
  options {
    strategy [LocalVisionMoondream, LocalVisionGLM, Gemini25Flash]
  }
}