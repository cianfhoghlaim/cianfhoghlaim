// BAML Shared Client Definitions for cianfhoghlaim.
// 7 clients: 1 default (DefaultLiteLLM) + 4 per-quadrant defaults
// (OideachaisDefault, MeaisinfhoghlaimDefault, TuathaDefault,
// CroilarDefault) + 2 shared (VisionLocal, ReasoningStrong).
// All route through the LiteLLM gateway at http://litellm:4000/v1
// per infrastructure/stacks/litellm/config/config.yaml.

retry_policy Simple {
  max_retries 3
  strategy {
    type exponential_backoff
    delay_ms 1000
    multiplier 2
  }
}

retry_policy LongDelay {
  max_retries 2
  strategy {
    type exponential_backoff
    delay_ms 2000
    multiplier 2
  }
}

retry_policy Exponential3s {
  max_retries 2
  strategy {
    type exponential_backoff
    delay_ms 3000
    multiplier 2
  }
}

client<llm> DefaultLiteLLM {
  provider "openai"
  options {
    model "litellm/minimax-m3"
    temperature 0.0
  }
  retry_policy Simple
}

client<llm> OideachaisDefault {
  provider "openai"
  options {
    model "litellm/claude-3.5-sonnet"
    temperature 0.0
  }
  retry_policy Simple
}

client<llm> MeaisinfhoghlaimDefault {
  provider "openai"
  options {
    model "litellm/gpt-4o"
    temperature 0.0
  }
  retry_policy Simple
}

client<llm> TuathaDefault {
  provider "openai"
  options {
    model "litellm/gpt-4o"
    temperature 0.7
    max_tokens 4096
  }
  retry_policy Simple
}

client<llm> CroilarDefault {
  provider "openai"
  options {
    model "litellm/qwen3-vl"
    temperature 0.0
  }
  retry_policy Simple
}

client<llm> VisionLocal {
  provider "openai"
  options {
    model "local/vision/qwen3-vl"
  }
  retry_policy LongDelay
}

client<llm> ReasoningStrong {
  provider "openai"
  options {
    model "litellm/o1-preview"
    temperature 0.0
  }
  retry_policy Exponential3s
}
