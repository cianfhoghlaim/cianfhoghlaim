// BAML Client Configuration for the Cianfhoghlaim Educational MMO
// (formerly "Tuath" Celtic Educational MMO - LLM Clients)
// The clients are reused by the new 8 NCCA subject agents (math_agent,
// appm_agent, chem_agent, geog_agent, hist_agent, engl_agent, gael_agent,
// comp_agent). The legacy "Tuath" naming is preserved only in client
// variable names that may be referenced by historical BAML code; new
// code SHOULD use the names "CianfhoghlaimContentFallback" etc.

// Primary client for orchestration and complex tasks
client<llm> GPT4o {
  provider openai
  options {
    model "gpt-4o"
    temperature 0.7
    max_tokens 4096
  }
}

// Fast client for simple extractions
client<llm> GPT4oMini {
  provider openai
  options {
    model "gpt-4o-mini"
    temperature 0.5
    max_tokens 2048
  }
}

// Claude for nuanced content generation
client<llm> Claude {
  provider anthropic
  options {
    model "claude-sonnet-4-20250514"
    temperature 0.7
    max_tokens 4096
  }
}

// Qwen for multilingual Celtic language support
client<llm> Qwen {
  provider openai-generic
  options {
    model "qwen3-8b"
    base_url "http://localhost:8080/v1"
    temperature 0.6
    max_tokens 2048
  }
}

// Ollama local model for Irish content
client<llm> OllamaIrish {
  provider ollama
  options {
    model "uccix-llama"
    temperature 0.6
  }
}

// Retry configuration
retry_policy Default {
  max_retries 3
  strategy {
    type exponential_backoff
    delay_ms 500
    max_delay_ms 10000
    multiplier 2
  }
}

// Fallback chain for Celtic content
client<llm> CelticContentFallback {
  provider fallback
  options {
    strategy [Qwen, Claude, GPT4o]
  }
}

// Fast extraction fallback
client<llm> FastExtraction {
  provider fallback
  options {
    strategy [GPT4oMini, GPT4o]
  }
}
