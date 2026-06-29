// BAML client definitions for the llama-swap backend.
//
// The llama-swap service serves the 24-entry VISION_MODELS registry's
// Unsloth GGUFs at http://llama-swap:8080/v1/chat/completions. This
// client routes BAML extraction calls through llama-swap for VL tasks
// (figure captioning, formula OCR, multimodal extraction).
//
// Per the openspec change 2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority
// and oideachais-pdf-processing/spec.md (the 6-stage PDF pipeline),
// this client is the canonical VL extraction path for Stages 1-3 of
// the PDF processing pipeline.
//
// Usage in BAML schemas:
//   client LlamaSwapClient
//
// Re-gen after changes:  `cd oideachais && uv run baml-cli generate`

client<llm> LlamaSwapClient {
  provider openai
  options {
    api_key env.LLAMASWAP_API_KEY
    base_url "http://llama-swap:8080/v1"
    model "qwen3-vl-8b"
    temperature 0.1
  }
}

// Convenience aliases for specific tasks in the 6-stage PDF pipeline.
//
// Stage 1 (OCR) — qwen3-vl-8b is the workhorse for syllabus/past paper OCR
// Stage 2 (diagram detection) — molmo2-8b is the top workhorse for diagram pointing
//   (but it's transformers-only, no llama-swap; use MolmoSwapClient below)
// Stage 3 (BAML extraction) — gemma-4-12B for general text extraction from OCR
// Stage 3 (formula OCR) — deepseek-ocr-2 is transformers-only, no llama-swap

client<llm> LlamaSwapOCRClient {
  provider openai
  options {
    api_key env.LLAMASWAP_API_KEY
    base_url "http://llama-swap:8080/v1"
    model "qwen3-vl-8b"
    temperature 0.1
  }
}

client<llm> LlamaSwapExtractionClient {
  provider openai
  options {
    api_key env.LLAMASWAP_API_KEY
    base_url "http://llama-swap:8080/v1"
    model "gemma-4-12B"
    temperature 0.1
  }
}

client<llm> LlamaSwapReasoningClient {
  provider openai
  options {
    api_key env.LLAMASWAP_API_KEY
    base_url "http://llama-swap:8080/v1"
    model "qwen3.6-27b-mtp"
    temperature 0.1
  }
}
