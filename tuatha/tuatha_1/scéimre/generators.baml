// BAML Generator Configuration for EduVision
// Generates Python/Pydantic client for curriculum extraction and FIBO generation

generator python_client {
  output_type python/pydantic
  output_dir "../baml_client"
  version "0.214.0"
}

// LLM Client Configurations

// Primary extraction client - Gemini 2.5 Flash for document analysis
client<llm> Gemini {
  provider google-ai
  options {
    model gemini-2.5-flash
    api_key env.GEMINI_API_KEY
  }
}

// Vision-language model for local inference
client<llm> Qwen3VL {
  provider openai-generic
  options {
    model qwen3-vl
    base_url "http://localhost:8080/v1"
    api_key env.LOCAL_API_KEY
  }
}

// Claude for complex reasoning tasks
client<llm> Claude {
  provider anthropic
  options {
    model claude-sonnet-4-20250514
    api_key env.ANTHROPIC_API_KEY
  }
}

// Fallback client with retry
client<llm> FallbackClient {
  provider fallback
  options {
    strategy [Gemini, Claude]
  }
  retry_policy StandardRetry
}

// Retry policies
retry_policy StandardRetry {
  max_retries 3
  strategy {
    type exponential_backoff
    delay_ms 1000
    max_delay_ms 10000
    multiplier 2
  }
}
