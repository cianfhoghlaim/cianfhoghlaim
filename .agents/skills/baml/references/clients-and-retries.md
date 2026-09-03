# Named Clients + Retry Policies

BAML supports **named clients** with explicit `retry_policy` blocks,
`fallback` chains, and `round-robin` strategies. This is the
canonical way to manage LLM clients in BAML.

## The 3 KCG production clients

The `baml/clients.baml` defines:

```baml
client<llm> ExtractEn {
  provider "openai"
  options {
    model "gpt-4o-mini"
    temperature 0.0
  }
  retry_policy Constant {
    max_retries 3
    delay_ms 1000
  }
}

client<llm> ExtractEnStrong {
  provider "openai"
  options {
    model "gpt-4o"
    temperature 0.0
  }
  retry_policy Exponential {
    max_retries 5
    strategy { type exponential_backoff, multiplier 2.0 }
  }
}

client<llm> LocalVision {
  provider "openai-generic"
  options {
    base_url "http://localhost:8000/v1"
    model "dots-ocr"
  }
  retry_policy Constant {
    max_retries 2
    delay_ms 500
  }
}
```

## Provider list

| Provider | `provider` value | Notes |
|:--|:--|:--|
| OpenAI (chat completions) | `"openai"` | Standard chat completions API |
| OpenAI (responses API) | `"openai-responses"` | Newer, supports built-in tools |
| Anthropic | `"anthropic"` | Claude 3.5 Sonnet, Claude 3 Opus |
| Google AI | `"google-ai"` | Gemini 2.5 Flash, Gemini 2.5 Pro |
| Vertex AI | `"vertex-ai"` | GCP-hosted Gemini / Claude |
| AWS Bedrock | `"aws-bedrock"` | Claude / Titan / Llama 2 |
| Azure OpenAI | `"azure-openai"` | Azure-hosted OpenAI |
| OpenAI generic | `"openai-generic"` | Any OpenAI-compatible API (vLLM, llama.cpp, etc.) |
| Ollama | `"ollama"` | Local model server |
| Anthropic Vertex | `"anthropic-vertex"` | Claude on Vertex AI |

## Retry policies

```baml
// Constant: retry every N ms, up to M times
retry_policy Constant {
  max_retries 3
  delay_ms 1000
}

// Exponential: backoff doubles each retry
retry_policy Exponential {
  max_retries 5
  strategy { type exponential_backoff, multiplier 2.0 }
  max_delay_ms 30000  // cap the delay at 30s
}

// Exponential with jitter (recommended for high-concurrency)
retry_policy ExponentialWithJitter {
  max_retries 5
  strategy { type exponential_backoff, multiplier 2.0, jitter true }
}
```

## Fallback chains

```baml
client<llm> PrimaryWithFallback {
  provider "openai"
  options { model "gpt-4o" temperature 0.0 }
  fallback [
    (provider "anthropic", options { model "claude-3-5-sonnet-20241022" temperature 0.0 }),
    (provider "google-ai", options { model "gemini-2.5-pro" temperature 0.0 }),
  ]
  retry_policy Constant { max_retries 2 delay_ms 500 }
}
```

When the primary fails, BAML falls through to the fallback clients
in order. Each fallback can have its own `retry_policy`.

## Round-robin (load balancing)

```baml
client<llm> RoundRobin {
  provider "openai"
  options { model "gpt-4o-mini" }
  round_robin [
    (provider "openai", options { model "gpt-4o-mini" api_key env.OPENAI_API_KEY_1 }),
    (provider "openai", options { model "gpt-4o-mini" api_key env.OPENAI_API_KEY_2 }),
    (provider "openai", options { model "gpt-4o-mini" api_key env.OPENAI_API_KEY_3 }),
  ]
}
```

Useful for distributing load across multiple API keys (rate-limit
avoidance).

## Multimodal client config (vision-specific)

```baml
client<llm> Gemini25Flash {
  provider "google-ai"
  options {
    model "gemini-2.5-flash"
    generationConfig {
      temperature 0.0
      maxOutputTokens 8192
    }
    safetySettings [
      { category "HARM_CATEGORY_HARASSMENT" threshold "BLOCK_NONE" }
      { category "HARM_CATEGORY_HATE_SPEECH" threshold "BLOCK_NONE" }
      { category "HARM_CATEGORY_SEXUALLY_EXPLICIT" threshold "BLOCK_NONE" }
      { category "HARM_CATEGORY_DANGEROUS_CONTENT" threshold "BLOCK_NONE" }
    ]
  }
}
```

## Using a named client in a function

```baml
function ExtractPrimaryLearningOutcomes(text: string) -> PrimaryLearningOutcome[] {
  client ExtractEn  // ← use the named client
  prompt #"..."#
}

function ExtractPrimaryLearningOutcomesStrong(text: string) -> PrimaryLearningOutcome[] {
  client ExtractEnStrong  // ← use the stronger client
  prompt #"..."#
}
```

## Async client mode

```baml
client<llm> ExtractEn {
  provider "openai"
  options { model "gpt-4o-mini" }
  default_client_mode async  // or "sync"
}
```

For high-concurrency KCG pipelines (the dlt → BAML → Dagster
pattern), `default_client_mode async` is required.

## KCG conventions

- `ExtractEn` (GPT-4o-mini) for production extraction
- `ExtractEnStrong` (GPT-4o) for higher-accuracy or fallback
- `LocalVision` (dots-ocr) for offline OCR
- `Gemini25Flash` (vision) for multimodal extraction
- Always `temperature 0.0` for deterministic extraction
- Always wrap the LLM in a `retry_policy` (default `Constant` with
  3 retries, 1s delay)
- For multimodal: `safetySettings` with `BLOCK_NONE` (KCG content
  includes historical political / cultural material)

## Reference

- The full `baml/clients.baml` (and `clients_0.baml`
  in the repo) define the KCG production clients
- BAML clients docs: <https://docs.boundaryml.com/docs/snippets/clients>
- BAML retry docs: <https://docs.boundaryml.com/docs/configuration/retries>
