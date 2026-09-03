// BAML Client Configuration additions for the BIEP v2 OCR/VLM ensemble.
//
// Per the 2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1 change.
//
// This file extends `baml_src/clients.baml` with 2 new clients:
// - `Docling` — for the IBM Docling HTTP REST API at :5001
// - `Unstract` — for the Unstract Prompt Studio workflow REST API at :8000
//
// Both clients are first-class BAML clients and can be selected as the
// `client` for any BAML function (e.g. `client Docling` or `client Unstract`)
// to invoke the upstream OCR/IE service.
//
// Per the BIEP v2 4-path ensemble:
//   Path 1 (BAML):    client Default (or per-jurisdiction ExtractEn/ExtractEnStrong)
//   Path 2 (Unstract): client Unstract  — non-engineer-authored workflow
//   Path 3 (qwen3-vl): client ExtractEnStrong (Qwen 3-VL 8B workhorse)
//   Path 4 (gemma4):   client ExtractEnStrong (gemma-4-26B-A4B M4 default MoE)
//
// MODEL_REGISTRY canonical home:
// Per the centralized-model-registry openspec change (2026-08-15),
// the model strings (`docling`, `UNSTRACT_DEPLOYMENT_ID`) for these
// clients are resolved via the unified `MODEL_REGISTRY` at
// `meaisinfhoghlaim/models/model_registry.py` at runtime. The
// `docling` backend is a REST adapter (not a model in the registry);
// `UNSTRACT_DEPLOYMENT_ID` is a per-doc-type workflow ID, not a model.

client<llm> Docling {
  provider "openai"  // Re-use the openai-compatible HTTP client for the Docling REST API.
  options {
    base_url env.DOCLING_URL  // Default: http://localhost:5001/v1
    api_key env.DOCLING_API_KEY  // Default: "docling" (no auth on local)
    model "docling"
    // Document parsing format is DocTags XML (preserves tables / figures / equations).
  }
}

client<llm> Unstract {
  provider "openai"  // Re-use the openai-compatible HTTP client for the Unstract REST API.
  options {
    base_url env.UNSTRACT_API_URL  // Default: http://localhost:8000/api/v1/deployment
    api_key env.UNSTRACT_API_KEY    // Default: "unstract" (dev default)
    model env.UNSTRACT_DEPLOYMENT_ID  // Set per-doc-type (e.g. "aqa_gcse_spec", "ncca_jc_cba")
    // Unstract returns JSON (the workflow's structured output schema).
  }
}
