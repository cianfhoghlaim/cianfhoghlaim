// spaces/_common/baml/clients_hackathon.baml
//
// Hackathon fork of tuatha/baml_src/tuatha_clients.baml.
// Re-points to HuggingFace Inference API (3-tier fallback) for the
// Build Small 2026 submission. All models are <=32B.
//
// Usage:
//   import { b } from "@boundaryml/baml";
//   b.config.set_primary_model("BAML_HACKATHON_PRIMARY");
//
// Env:
//   HF_TOKEN         (required, write-only in Space secrets)
//   HF_INFERENCE_URL (optional, defaults to https://api-inference.huggingface.co)
//
// Primary:   Qwen/Qwen2.5-7B-Instruct          (7.6B, fast, strong JSON)
// Fallback1: meta-llama/Llama-3.1-8B-Instruct  (8.1B, broad coverage)
// Fallback2: google/gemma-2-9b-it              (9.2B, safety-tuned)
//
// Why 3 tiers? HF Inference cold-starts can take 30-60s and rate-limits
// apply per-org. A 3-tier chain absorbs transient failures and keeps
// p95 latency under 10s in the worst case.

class HackathonClientConfig {
  base_url string
  api_key_env string
  model string
  max_tokens int
  temperature float
  timeout_seconds int
}

function GetHackathonPrimaryClient() -> HackathonClientConfig {
  return {
    base_url: env.HF_INFERENCE_URL ?? "https://api-inference.huggingface.co",
    api_key_env: "HF_TOKEN",
    model: "Qwen/Qwen2.5-7B-Instruct",
    max_tokens: 4096,
    temperature: 0.1,
    timeout_seconds: 60,
  }
}

function GetHackathonFallback1Client() -> HackathonClientConfig {
  return {
    base_url: env.HF_INFERENCE_URL ?? "https://api-inference.huggingface.co",
    api_key_env: "HF_TOKEN",
    model: "meta-llama/Llama-3.1-8B-Instruct",
    max_tokens: 4096,
    temperature: 0.1,
    timeout_seconds: 60,
  }
}

function GetHackathonFallback2Client() -> HackathonClientConfig {
  return {
    base_url: env.HF_INFERENCE_URL ?? "https://api-inference.huggingface.co",
    api_key_env: "HF_TOKEN",
    model: "google/gemma-2-9b-it",
    max_tokens: 4096,
    temperature: 0.1,
    timeout_seconds: 60,
  }
}

client<llm> BAML_HACKATHON_PRIMARY {
  provider "openai-generic"
  base_url GetHackathonPrimaryClient().base_url + "/v1"
  api_key env.HF_TOKEN
  options {
    model GetHackathonPrimaryClient().model
    max_tokens GetHackathonPrimaryClient().max_tokens
    temperature GetHackathonPrimaryClient().temperature
  }
  retry_policy {
    max_retries 2
    strategy "exponential"
  }
}

client<llm> BAML_HACKATHON_FALLBACK_1 {
  provider "openai-generic"
  base_url GetHackathonFallback1Client().base_url + "/v1"
  api_key env.HF_TOKEN
  options {
    model GetHackathonFallback1Client().model
    max_tokens GetHackathonFallback1Client().max_tokens
    temperature GetHackathonFallback1Client().temperature
  }
  retry_policy {
    max_retries 1
    strategy "exponential"
  }
}

client<llm> BAML_HACKATHON_FALLBACK_2 {
  provider "openai-generic"
  base_url GetHackathonFallback2Client().base_url + "/v1"
  api_key env.HF_TOKEN
  options {
    model GetHackathonFallback2Client().model
    max_tokens GetHackathonFallback2Client().max_tokens
    temperature GetHackathonFallback2Client().temperature
  }
}

client<llm> BAML_HACKATHON_CHAINED {
  provider "fallback"
  options {
    clients [
      BAML_HACKATHON_PRIMARY,
      BAML_HACKATHON_FALLBACK_1,
      BAML_HACKATHON_FALLBACK_2,
    ]
  }
}

client<llm> BAML_HACKATHON_DIALOGUE {
  provider "fallback"
  options {
    clients [
      BAML_HACKATHON_PRIMARY,
      BAML_HACKATHON_FALLBACK_1,
    ]
  }
  options {
    model "Qwen/Qwen2.5-7B-Instruct"
    max_tokens 1024
    temperature 0.8
  }
}
