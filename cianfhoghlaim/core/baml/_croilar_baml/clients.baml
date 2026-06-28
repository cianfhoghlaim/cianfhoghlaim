// BAML Client Configuration for Aleyum
// Defines LLM clients for artwork analysis via LiteLLM gateway

// Primary vision model - Qwen3 VL 30B
client LocalVisionQwen {
  provider openai
  options {
    base_url "http://localhost:4000/v1"
    api_key env.LITELLM_API_KEY
    model "local/vision/qwen3-vl"
  }
}

// Fast vision model - GLM 4.6V Flash
client LocalVisionGLM {
  provider openai
  options {
    base_url "http://localhost:4000/v1"
    api_key env.LITELLM_API_KEY
    model "local/vision/glm-4.6v-flash"
  }
}

// Lightweight vision - Moondream2
client LocalVisionMoondream {
  provider openai
  options {
    base_url "http://localhost:4000/v1"
    api_key env.LITELLM_API_KEY
    model "local/vision/moondream2"
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

// Fast cloud - Gemini Flash
client Gemini25Flash {
  provider google-ai
  options {
    model gemini-2.5-flash-preview-05-20
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
