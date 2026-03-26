/**
 * Model Mapping Configuration
 * Maps model names to LiteLLM identifiers and metadata
 */

export interface ModelConfig {
  litellmName: string;
  displayName: string;
  provider: "llama-swap" | "mlx-omni-server" | "vllm" | "paddle" | "docling" | "unstract" | "library";
  endpoint: string;
  vram?: string;
  capabilities: string[];
  supportsIrish?: boolean;
  contextLength?: number;
  specialization?: string;
}

export const MODEL_MAPPING: Record<string, ModelConfig> = {
  // Vision models via llama-swap (GGUF)
  "qwen3-vl-30b": {
    litellmName: "local/vision/qwen3-vl",
    displayName: "Qwen3-VL-30B",
    provider: "llama-swap",
    endpoint: "http://localhost:8080",
    vram: "18GB",
    capabilities: ["vision", "document", "table", "irish"],
    supportsIrish: true,
    contextLength: 32768,
  },
  "glm-4.6v-flash": {
    litellmName: "local/vision/glm-4.6v-flash",
    displayName: "GLM-4.6V Flash",
    provider: "llama-swap",
    endpoint: "http://localhost:8080",
    vram: "6GB",
    capabilities: ["vision", "document"],
    contextLength: 131072,
  },
  "gemma-3-27b": {
    litellmName: "local/vision/gemma-27b",
    displayName: "Gemma-3-27B",
    provider: "llama-swap",
    endpoint: "http://localhost:8080",
    vram: "16GB",
    capabilities: ["vision", "multilingual"],
  },

  // OCR models via mlx-omni-server (MLX)
  "olmocr-7b": {
    litellmName: "local/ocr/olmocr2-7b",
    displayName: "OlmOCR-7B",
    provider: "mlx-omni-server",
    endpoint: "http://localhost:10240",
    vram: "4GB",
    capabilities: ["ocr", "table", "dense-text"],
  },
  "granite-docling": {
    litellmName: "local/document/granite-docling",
    displayName: "Granite-Docling",
    provider: "mlx-omni-server",
    endpoint: "http://localhost:10240",
    vram: "0.5GB",
    capabilities: ["document", "structure"],
  },

  // VLM OCR via vLLM
  "dots-ocr": {
    litellmName: "local/ocr/dots-ocr",
    displayName: "dots.ocr",
    provider: "vllm",
    endpoint: "http://localhost:8001",
    vram: "4GB",
    capabilities: ["ocr", "layout", "table", "formula", "multilingual"],
    specialization: "SOTA layout detection, 100+ languages",
  },

  // Platform services (direct API calls, not LiteLLM)
  paddleocr: {
    litellmName: "", // Direct API
    displayName: "PaddleOCR",
    provider: "paddle",
    endpoint: "http://localhost:8000",
    capabilities: ["ocr", "fast"],
  },
  docling: {
    litellmName: "", // Direct API
    displayName: "Docling",
    provider: "docling",
    endpoint: "http://localhost:5001",
    capabilities: ["document", "layout"],
    specialization: "IBM Document Intelligence",
  },
  unstract: {
    litellmName: "", // Direct API
    displayName: "Unstract",
    provider: "unstract",
    endpoint: "http://localhost:8002",
    capabilities: ["workflow", "multi-tool"],
    specialization: "Document workflow orchestration",
  },

  // Python libraries (local execution)
  pymupdf4llm: {
    litellmName: "", // Local library
    displayName: "PyMuPDF4LLM",
    provider: "library",
    endpoint: "local",
    capabilities: ["fast", "text-extraction"],
    specialization: "Fast PDF text extraction",
  },
  markitdown: {
    litellmName: "", // Local library
    displayName: "MarkItDown",
    provider: "library",
    endpoint: "local",
    capabilities: ["markdown", "document"],
    specialization: "Microsoft markdown converter",
  },
  marker: {
    litellmName: "", // Local library
    displayName: "Marker",
    provider: "library",
    endpoint: "local",
    capabilities: ["ml", "layout", "high-quality"],
    specialization: "ML-based layout analysis, highest quality",
  },
  tesseract: {
    litellmName: "", // Local library
    displayName: "Tesseract",
    provider: "library",
    endpoint: "local",
    capabilities: ["ocr", "legacy"],
    specialization: "Classic OCR, legacy/fallback",
  },
};

/**
 * Get model configuration by name
 */
export function getModelConfig(modelName: string): ModelConfig | undefined {
  return MODEL_MAPPING[modelName];
}

/**
 * Get all models that use LiteLLM
 */
export function getLiteLLMModels(): string[] {
  return Object.entries(MODEL_MAPPING)
    .filter(([, config]) => config.litellmName)
    .map(([name]) => name);
}

/**
 * Get models by provider
 */
export function getModelsByProvider(provider: ModelConfig["provider"]): string[] {
  return Object.entries(MODEL_MAPPING)
    .filter(([, config]) => config.provider === provider)
    .map(([name]) => name);
}

/**
 * Get models with a specific capability
 */
export function getModelsByCapability(capability: string): string[] {
  return Object.entries(MODEL_MAPPING)
    .filter(([, config]) => config.capabilities.includes(capability))
    .map(([name]) => name);
}
