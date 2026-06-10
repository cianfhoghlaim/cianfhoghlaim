// BAML Generators Configuration for Celtic Language AI Platform
// Defines LLM clients for linguistic extraction

generator lang_py {
  output_type python/pydantic
  output_dir ../baml_client
  version "0.74.0"
  default_client_mode sync
}

// Primary client for linguistic extraction
client<llm> Claude {
  provider anthropic
  options {
    model "claude-3-5-sonnet-20241022"
    max_tokens 4096
  }
}

// Fast client for simple classifications
client<llm> ClaudeHaiku {
  provider anthropic
  options {
    model "claude-3-5-haiku-20241022"
    max_tokens 2048
  }
}

// Gemini client for long-context processing
client<llm> Gemini {
  provider google-ai
  options {
    model "gemini-2.0-flash"
    max_tokens 8192
  }
}

// OpenAI client for compatibility
client<llm> GPT4 {
  provider openai
  options {
    model "gpt-4o"
    max_tokens 4096
  }
}

// Ollama client for local development
client<llm> Ollama {
  provider ollama
  options {
    model "llama3.2"
    base_url "http://localhost:11434/v1"
  }
}
