// BAML Client Configuration for Cianfhoghlaim
// Using Gemini 2.0 Flash for extraction (free tier available)

client<llm> Gemini2Flash {
  provider google-ai
  options {
    model "gemini-2.0-flash-exp"
    api_key env.GOOGLE_API_KEY
  }
}

// Fallback client with standard Gemini
client<llm> GeminiPro {
  provider google-ai
  options {
    model "gemini-pro"
    api_key env.GOOGLE_API_KEY
  }
}

// Default client for retries
client<llm> Default {
  provider google-ai
  retry_policy Simple
  options {
    model "gemini-2.0-flash-exp"
    api_key env.GOOGLE_API_KEY
  }
}

// Retry policy for resilient extraction
retry_policy Simple {
  max_retries 2
  strategy {
    type exponential_backoff
    delay_ms 500
    multiplier 2
  }
}
