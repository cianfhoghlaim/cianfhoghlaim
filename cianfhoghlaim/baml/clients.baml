// BAML Client Configuration for Cianfhoghlaim (post-v4 + baml 0.212+ canonical syntax)
//
// ====== 2026-07-13: scoped to minimax-m3 (coding plan API) ======
// The historical 8-generator setup is preserved as a comment block below
// for when more cloud providers (Gemini, OpenAI, Anthropic, etc.) become
// available. The active single text-extraction generator is `default`,
// routing to `minimax-m3` (the M3 model available via the coding plan API).
//
// When API keys for other providers become available, uncomment the relevant
// generator block below and update the default text generator deliberately.
//
// Generation: `cd cianfhoghlaim && uv run baml-cli generate --from baml_src`
// Validation: `cd cianfhoghlaim && mise run baml:generate` (alias)

// ====== 8-generator historical setup (commented; for when more cloud providers are available) ======
// generator default {
//   provider "openai"
//   model "gpt-5-mini"
//   retry_policy Exponential
//   timeout { total_ms 60000 }
//   options {
//     base_url env.LITELLM_BASE_URL
//     api_key env.LITELLM_API_KEY
//   }
// }
//
// generator local_vision_qwen {
//   provider "openai"
//   model "local/vision/qwen3-vl"
//   retry_policy Exponential
//   timeout { total_ms 60000 }
//   options {
//     base_url env.LITELLM_BASE_URL
//     api_key env.LITELLM_API_KEY
//   }
// }
//
// generator local_vision_glm {
//   provider "openai"
//   model "local/vision/glm-4.6v-flash"
//   retry_policy Exponential
//   timeout { total_ms 60000 }
//   options {
//     base_url env.LITELLM_BASE_URL
//     api_key env.LITELLM_API_KEY
//   }
// }
//
// generator local_vision_moondream {
//   provider "openai"
//   model "local/vision/moondream2"
//   retry_policy Exponential
//   timeout { total_ms 60000 }
//   options {
//     base_url env.LITELLM_BASE_URL
//     api_key env.LITELLM_API_KEY
//   }
// }
//
// generator gemini_2_flash {
//   provider "google-ai"
//   model "gemini-2.0-flash-exp"
//   retry_policy Exponential
//   timeout { total_ms 60000 }
//   options {
//     api_key env.GOOGLE_API_KEY
//   }
// }
//
// generator gemini_1_5_pro {
//   provider "google-ai"
//   model "gemini-1.5-pro-latest"
//   retry_policy Exponential
//   timeout { total_ms 60000 }
//   options {
//     api_key env.GOOGLE_API_KEY
//   }
// }
//
// generator gemini_pro {
//   provider "google-ai"
//   model "gemini-pro"
//   retry_policy Exponential
//   timeout { total_ms 60000 }
//   options {
//     api_key env.GOOGLE_API_KEY
//   }
// }
//
// generator gemini_2_5_flash {
//   provider "google-ai"
//   model "gemini-2.5-flash-preview-05-20"
//   retry_policy Exponential
//   timeout { total_ms 60000 }
//   options {
//     api_key env.GOOGLE_API_KEY
//   }
// }

// ====== Active text generator ======

generator default {
  provider "openai-generic"
  model "minimax-m3"
  retry_policy Exponential
  timeout { total_ms 60000 }
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
  }
}

// ====== Local vision generators (active) ======

generator local_vision_gemma4 {
  provider "openai"
  model "local/vision/gemma-4-26B-A4B"
  retry_policy Exponential
  timeout { total_ms 60000 }
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
  }
}

generator local_vision_qwen3vl {
  provider "openai"
  model "local/vision/qwen3-vl-8b"
  retry_policy Exponential
  timeout { total_ms 60000 }
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
  }
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
