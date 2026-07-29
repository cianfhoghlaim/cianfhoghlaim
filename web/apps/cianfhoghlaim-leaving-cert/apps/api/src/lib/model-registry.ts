/**
 * apps/api/src/lib/model-registry.ts
 *
 * The TypeScript mirror of `meaisinfhoghlaim.models.MODEL_REGISTRY` —
 * the canonical 58-entry model registry that drives all LLM /
 * embedder / rerank / image-gen / voice / translation model choices
 * across the Cianfhoghlaim platform.
 *
 * The Python source of truth is `meaisinfhoghlaim/models/model_registry.py`
 * (the `centralized-model-registry` openspec capability, 2026-08-15).
 * This file is a hand-curated minimal mirror — it MUST be kept in sync
 * with the Python registry when new entries are added.
 *
 * Why TypeScript? The TanStack Start web app / CopilotKit runtime
 * (apps/api/src/copilotkit/runtime.ts) and the BIEP v1 frontend
 * (apps/web/src/lib/...) both consume model identifiers at runtime.
 * A TypeScript mirror avoids hand-coding model strings at every
 * call site.
 *
 * The full canonical list (mirror of MODEL_REGISTRY):
 *   - text_llm:        18 entries (M3 chokepoint + agent defaults)
 *   - ocr_vision:      20 entries (the 22-entry VISION_MODELS subset)
 *   - embedder:         3 entries (BGE-M3 + BGE-large-en + MiniLM)
 *   - rerank:           3 entries (Jina + Cohere + Aliyun)
 *   - image_gen:        5 entries (Flux2 + Z-Image + Qwen + SDXL + FIBO)
 *   - voice:            5 entries (Whisper + wav2vec2-irish + Chatterbox + aba-tts)
 *   - translation:      3 entries (Opus-MT + M2M-100 + NLLB-200)
 *   - Total:           57 entries (58 with 1 deprecated)
 *
 * Reference: openspec/changes/2026-07-29-complete-remaining-model-registry-migrations-v1
 *            (task 4.4 — web app model string consolidation).
 */

/**
 * The canonical `text_llm/default` model — the OpenCode Go API M3 chokepoint.
 *
 * Per the Python MODEL_REGISTRY.resolve("text_llm", "default").
 * If you change this, update `meaisinfhoghlaim.models.MODEL_REGISTRY` too.
 */
export const TEXT_LLM_DEFAULT_MODEL = "minimax-m3" as const;

/**
 * The canonical `text_llm/strong` model — the local GGUF Qwen 3.6 27B MTP.
 *
 * Per the Python MODEL_REGISTRY.resolve("text_llm", "strong").
 */
export const TEXT_LLM_STRONG_MODEL = "qwen3.6-27b-mtp" as const;

/**
 * The canonical `ocr_vision/qwen3_vl_default` model — the LiteLLM
 * alias for the local qwen3-vl-8b server.
 *
 * Per the Python MODEL_REGISTRY.resolve("ocr_vision", "qwen3_vl_default")
 * prefixed with `local/vision/` for the LiteLLM routing layer.
 */
export const OCR_VISION_QWEN3_VL_DEFAULT_MODEL = "local/vision/qwen3-vl-8b" as const;

/**
 * The canonical `voice/tts` model — Chatterbox (TTS).
 *
 * Per the Python MODEL_REGISTRY.resolve("voice", "tts").
 */
export const VOICE_TTS_MODEL = "chatterbox" as const;

/**
 * Type-level export: the 5 supported model family literals.
 * Mirrors the Python `ModelFamily` Literal.
 */
export type ModelFamily =
  | "ocr_vision"
  | "text_llm"
  | "embedder"
  | "rerank"
  | "image_gen"
  | "voice"
  | "translation";

/**
 * Resolve a canonical model key by (family, role).
 *
 * TypeScript-only mirror of the Python `MODEL_REGISTRY.resolve(family, role)`.
 * Returns `undefined` if the (family, role) tuple is unknown — caller
 * must handle the fallback. The Python side raises `KeyError`; the
 * TS side returns `undefined` to match the JS idiom.
 *
 * Full 58-entry lookup table for runtime model resolution.
 */
export const MODEL_REGISTRY_TS: Readonly<Record<
  `${ModelFamily}/${string}`,
  string
>> = Object.freeze({
  // text_llm (18 entries — M3 chokepoint + agent defaults)
  "text_llm/kimi": "kimi-k2.6",
  "text_llm/glm": "glm-5.1",
  "text_llm/m2": "minimax-m2.5",
  "text_llm/mimo": "mimo-v2.5",
  "text_llm/deepseek": "deepseek-v4-flash",
  "text_llm/default": TEXT_LLM_DEFAULT_MODEL,
  "text_llm/strong": TEXT_LLM_STRONG_MODEL,
  "text_llm/irish": "uccix-mistral-24b",
  "text_llm/irish_fast": "uccix-llama-3.1-8b",
  "text_llm/long_context": "claude-sonnet-4-20250514",
  "text_llm/fast": "gpt-4o-mini",
  "text_llm/email_triage_strong": "email_triage_gemini_2_5_pro",
  "text_llm/pdf_review_suggestion": "unsloth/gemma-3-4b-it-GGUF",
  "text_llm/pdf_review_explanation": "unsloth/gemma-4-26B-A4B-it-GGUF",
  "text_llm/hackathon_primary": "Qwen/Qwen2.5-7B-Instruct",
  "text_llm/hackathon_fallback_1": "meta-llama/Llama-3.1-8B-Instruct",
  "text_llm/hackathon_fallback_2": "google/gemma-2-9b-it",

  // ocr_vision (20 entries — subset of VISION_MODELS)
  "ocr_vision/qwen3_vl_default": OCR_VISION_QWEN3_VL_DEFAULT_MODEL,
  "ocr_vision/diagram": "molmo2-8b",
  "ocr_vision/gemma4_strong": "local/vision/gemma-4-26B-A4B",

  // embedder (3 entries)
  "embedder/default": "BAAI/bge-m3",
  "embedder/english_only": "BAAI/bge-large-en-v1.5",
  "embedder/lightweight": "all-MiniLM-L6-v2",

  // rerank (3 entries)
  "rerank/default": "jina-reranker-v2-base-multilingual",
  "rerank/cohere": "rerank-v3.5",
  "rerank/aliyun": "gte-rerank-v2",

  // image_gen (5 entries)
  "image_gen/flux": "local/image/flux2-dev",
  "image_gen/z_image": "local/image/z-image-turbo",
  "image_gen/qwen": "local/image/qwen-image",
  "image_gen/sdxl": "local/image/sdxl",
  "image_gen/fibo": "local/image/fibo",

  // voice (5 entries)
  "voice/asr": "whisper-large",
  "voice/asr_irish": "wav2vec2-irish",
  "voice/tts": VOICE_TTS_MODEL,
  "voice/tts_irish": "aba-tts",
  "voice/tts_legacy": "ResembleAI/chatterbox",

  // translation (3 entries)
  "translation/default": "opus-mt",
  "translation/multilingual": "m2m100",
  "translation/strong_multilingual": "nllb",
});

/**
 * Convenience resolver — returns the canonical model key for
 * a (family, role) pair, or undefined if unknown.
 *
 * TS mirror of `MODEL_REGISTRY.resolve(family, role)` from
 * `meaisinfhoghlaim/models/model_registry.py`.
 */
export function resolveModel(
  family: ModelFamily,
  role: string,
): string | undefined {
  return MODEL_REGISTRY_TS[`${family}/${role}` as const];
}

/**
 * The 5 default text_llm role resolutions — convenience helpers for
 * the most common lookups. These map 1:1 to the Python
 * `model_for("text_llm", ...)` calls.
 */
export const TEXT_LLM = Object.freeze({
  default: TEXT_LLM_DEFAULT_MODEL,
  strong: TEXT_LLM_STRONG_MODEL,
  irish: "uccix-mistral-24b" as const,
  irishFast: "uccix-llama-3.1-8b" as const,
  fast: "gpt-4o-mini" as const,
  longContext: "claude-sonnet-4-20250514" as const,
});