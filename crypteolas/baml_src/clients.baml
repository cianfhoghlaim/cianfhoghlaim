// BAML Client Configuration for Crypteolas
// Crypto Intelligence Platform - LLM Clients
//
// Client names are prefixed with "Crypteolas" to avoid name collisions
// with the Celtic MMO `tuatha_clients.baml` (GPT4o, Claude, etc.) and to
// allow the baml-cli to merge the two schemas into a single `baml_client/`
// output. The `tuatha_clients.baml` file lives at the parent
// `tuatha/baml_src/` directory; this file lives at
// `tuatha/crypteolas/baml_src/`. Each baml_src generates to its own
// `baml_client/` output directory.
//
// Update all .baml files in this directory to use the prefixed client
// names (e.g., `client CrypteolasClaude` instead of `client Claude`).

// Primary client for orchestration and complex analysis
client<llm> CrypteolasGPT4o {
  provider openai
  options {
    model "gpt-4o"
    temperature 0.4
    max_tokens 4096
  }
}

// Fast client for structured extractions
client<llm> CrypteolasGPT4oMini {
  provider openai
  options {
    model "gpt-4o-mini"
    temperature 0.3
    max_tokens 2048
  }
}

// Claude for nuanced document analysis and reasoning
client<llm> CrypteolasClaude {
  provider anthropic
  options {
    model "claude-sonnet-4-20250514"
    temperature 0.5
    max_tokens 4096
  }
}

// Claude Haiku for fast classification tasks
client<llm> CrypteolasClaudeHaiku {
  provider anthropic
  options {
    model "claude-3-5-haiku-20241022"
    temperature 0.3
    max_tokens 1024
  }
}

// DeepSeek for code analysis (cost-effective)
client<llm> CrypteolasDeepSeek {
  provider openai-generic
  options {
    model "deepseek-coder"
    base_url "https://api.deepseek.com/v1"
    temperature 0.2
    max_tokens 4096
  }
}

// Qwen for multilingual and technical content
client<llm> CrypteolasQwen {
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
client<llm> CrypteolasDocumentAnalysis {
  provider fallback
  options {
    strategy [CrypteolasClaude, CrypteolasGPT4o, CrypteolasQwen]
  }
}

// Fast extraction fallback
client<llm> CrypteolasFastExtraction {
  provider fallback
  options {
    strategy [CrypteolasGPT4oMini, CrypteolasClaudeHaiku]
  }
}

// Code analysis fallback (prefer specialized models)
client<llm> CrypteolasCodeAnalysis {
  provider fallback
  options {
    strategy [CrypteolasDeepSeek, CrypteolasGPT4o, CrypteolasClaude]
  }
}

// Risk assessment (needs strong reasoning)
client<llm> CrypteolasRiskAssessment {
  provider fallback
  options {
    strategy [CrypteolasClaude, CrypteolasGPT4o]
  }
}
