// BAML Client Configuration for Crypteolas
// Crypto Intelligence Platform - LLM Clients

// Primary client for orchestration and complex analysis
client<llm> GPT4o {
  provider openai
  options {
    model "gpt-4o"
    temperature 0.4
    max_tokens 4096
  }
}

// Fast client for structured extractions
client<llm> GPT4oMini {
  provider openai
  options {
    model "gpt-4o-mini"
    temperature 0.3
    max_tokens 2048
  }
}

// Claude for nuanced document analysis and reasoning
client<llm> Claude {
  provider anthropic
  options {
    model "claude-sonnet-4-20250514"
    temperature 0.5
    max_tokens 4096
  }
}

// Claude Haiku for fast classification tasks
client<llm> ClaudeHaiku {
  provider anthropic
  options {
    model "claude-3-5-haiku-20241022"
    temperature 0.3
    max_tokens 1024
  }
}

// DeepSeek for code analysis (cost-effective)
client<llm> DeepSeek {
  provider openai-generic
  options {
    model "deepseek-coder"
    base_url "https://api.deepseek.com/v1"
    temperature 0.2
    max_tokens 4096
  }
}

// Qwen for multilingual and technical content
client<llm> Qwen {
  provider openai-generic
  options {
    model "qwen3-32b"
    base_url "http://localhost:8080/v1"
    temperature 0.4
    max_tokens 4096
  }
}

// Retry configuration for API stability
retry_policy Default {
  max_retries 3
  strategy {
    type exponential_backoff
    delay_ms 500
    max_delay_ms 10000
    multiplier 2
  }
}

// Fallback chain for document analysis
client<llm> DocumentAnalysis {
  provider fallback
  options {
    strategy [Claude, GPT4o, Qwen]
  }
}

// Fast extraction fallback
client<llm> FastExtraction {
  provider fallback
  options {
    strategy [GPT4oMini, ClaudeHaiku]
  }
}

// Code analysis fallback (prefer specialized models)
client<llm> CodeAnalysis {
  provider fallback
  options {
    strategy [DeepSeek, GPT4o, Claude]
  }
}

// Risk assessment (needs strong reasoning)
client<llm> RiskAssessment {
  provider fallback
  options {
    strategy [Claude, GPT4o]
  }
}
