/**
 * ML Gateway Module
 *
 * Provides integration with:
 * - LiteLLM Gateway (port 4000) for unified LLM access
 * - Model Registry (registry.yaml) with 70+ models
 * - Local inference backends (llama-swap, mlx-omni-server, InvokeAI)
 */

import { dag, Container, Directory, Service, object, func } from "@dagger.io/dagger";

// =============================================================================
// Types based on registry.yaml structure
// =============================================================================

export interface ModelInfo {
  name: string;
  id: string;
  hfRepo?: string;
  format: "mlx" | "gguf" | "safetensors" | "pytorch";
  category: string;
  backend: "llama-swap" | "mlx-omni-server" | "invokeai" | "lancedb" | "dedicated" | "transformers";
  port?: number;
  sizeGb: number;
  status: "ready" | "pending" | "catalog" | "training";
  description: string;
  capabilities: string[];
  quantization?: string;
  hardware?: {
    cuda: boolean;
    mps: boolean;
    cpu: boolean;
    vramGb: number;
  };
}

export interface LiteLLMConfig {
  endpoint: string;
  apiKey?: string;
  masterKey?: string;
  databaseUrl?: string;
  langfuseEnabled: boolean;
}

export interface ModelGroup {
  name: string;
  description: string;
  primary: string;
  fallbacks: string[];
}

export interface InferenceBackend {
  name: string;
  type: "llama-swap" | "mlx-omni-server" | "invokeai";
  port: number;
  dockerImage: string;
  healthEndpoint: string;
}

// =============================================================================
// Backend configurations
// =============================================================================

export const INFERENCE_BACKENDS: Record<string, InferenceBackend> = {
  "llama-swap": {
    name: "llama-swap",
    type: "llama-swap",
    port: 8080,
    dockerImage: "ghcr.io/mostlygeek/llama-swap:latest",
    healthEndpoint: "/health",
  },
  "mlx-omni-server": {
    name: "mlx-omni-server",
    type: "mlx-omni-server",
    port: 10240,
    dockerImage: "mlx-omni-server:latest",
    healthEndpoint: "/health",
  },
  "invokeai": {
    name: "invokeai",
    type: "invokeai",
    port: 9090,
    dockerImage: "ghcr.io/invoke-ai/invokeai:latest",
    healthEndpoint: "/api/v1/health",
  },
};

// =============================================================================
// Default LiteLLM endpoint
// =============================================================================

// NOTE: LiteLLM stack NOT YET DEPLOYED - create bonneagar/storage/litellm first
// Future OLM proxy: http://pangolin.cianfhoghlaim.ie:4000
const DEFAULT_LITELLM_ENDPOINT = "https://llm.cianfhoghlaim.ie";
const DEFAULT_LITELLM_LOCAL = "http://localhost:4000";

// =============================================================================
// Model Groups (from registry.yaml)
// =============================================================================

export const MODEL_GROUPS: Record<string, ModelGroup> = {
  ocr: {
    name: "ocr",
    description: "OCR and document processing models",
    primary: "local/ocr/olmocr2-7b",
    fallbacks: ["local/document/granite-docling"],
  },
  vision: {
    name: "vision",
    description: "Vision and multimodal models",
    primary: "local/vision/glm-4.6v-flash",
    fallbacks: ["local/vision/qwen3-vl", "local/vision/moondream2", "glm-4.6v"],
  },
  image: {
    name: "image",
    description: "Image generation models",
    primary: "local/image/flux2-dev",
    fallbacks: ["local/image/z-image-turbo-gguf", "local/image/qwen-image", "local/image/sdxl", "local/image/fibo"],
  },
  reasoning: {
    name: "reasoning",
    description: "Heavy reasoning models",
    primary: "local/general/nemotron-3-nano",
    fallbacks: ["local/general/gemma-3n", "glm-4.6"],
  },
  tools: {
    name: "tools",
    description: "Function calling models",
    primary: "local/general/functiongemma",
    fallbacks: ["local/vision/glm-4.6v-flash", "glm-4.6"],
  },
  retrieval: {
    name: "retrieval",
    description: "Document retrieval models (LanceDB backend)",
    primary: "retrieval/colqwen2.5-v0.2",
    fallbacks: ["retrieval/colqwen2-v1.0", "retrieval/colpali-v1.3"],
  },
  celtic_irish: {
    name: "celtic_irish",
    description: "Irish (Gaeilge) language models",
    primary: "celtic/irish/qomhra-7b",
    fallbacks: ["celtic/irish/uccix-13b", "celtic/multilingual/britllm-3b"],
  },
  celtic_translation: {
    name: "celtic_translation",
    description: "Celtic language translation models",
    primary: "celtic/translation/nllb",
    fallbacks: ["celtic/translation/seamless"],
  },
};

@object()
export class MLGateway {
  /**
   * Get LiteLLM configuration for connecting to the gateway
   */
  @func()
  getLiteLLMConfig(
    endpoint?: string,
    useLangfuse: boolean = true
  ): LiteLLMConfig {
    return {
      endpoint: endpoint || DEFAULT_LITELLM_ENDPOINT,
      langfuseEnabled: useLangfuse,
    };
  }

  /**
   * Get local development LiteLLM configuration
   */
  @func()
  getLocalLiteLLMConfig(): LiteLLMConfig {
    return {
      endpoint: DEFAULT_LITELLM_LOCAL,
      langfuseEnabled: true,
    };
  }

  /**
   * Test connection to LiteLLM gateway
   */
  @func()
  async testConnection(endpoint?: string): Promise<boolean> {
    const url = endpoint || DEFAULT_LITELLM_ENDPOINT;

    try {
      const result = await dag
        .container()
        .from("curlimages/curl:latest")
        .withExec(["curl", "-sf", `${url}/health`])
        .stdout();

      return result.includes("healthy") || result.length > 0;
    } catch {
      return false;
    }
  }

  /**
   * List available models from LiteLLM gateway
   */
  @func()
  async listModels(endpoint?: string, apiKey?: string): Promise<string[]> {
    const url = endpoint || DEFAULT_LITELLM_ENDPOINT;

    const container = dag
      .container()
      .from("curlimages/curl:latest");

    const headers = apiKey
      ? ["-H", `Authorization: Bearer ${apiKey}`]
      : [];

    const result = await container
      .withExec(["curl", "-sf", ...headers, `${url}/v1/models`])
      .stdout();

    try {
      const parsed = JSON.parse(result);
      if (parsed.data && Array.isArray(parsed.data)) {
        return parsed.data.map((m: { id: string }) => m.id);
      }
      return [];
    } catch {
      return [];
    }
  }

  /**
   * Get model groups (fallback chains)
   */
  @func()
  getModelGroups(): ModelGroup[] {
    return Object.values(MODEL_GROUPS);
  }

  /**
   * Get a specific model group by name
   */
  @func()
  getModelGroup(name: string): ModelGroup | undefined {
    return MODEL_GROUPS[name];
  }

  /**
   * Get inference backend configuration
   */
  @func()
  getInferenceBackend(backend: string): InferenceBackend | undefined {
    return INFERENCE_BACKENDS[backend];
  }

  /**
   * Get all inference backends
   */
  @func()
  getInferenceBackends(): InferenceBackend[] {
    return Object.values(INFERENCE_BACKENDS);
  }

  /**
   * Get the endpoint URL for a specific backend
   */
  @func()
  getInferenceEndpoint(backend: string, host: string = "localhost"): string {
    const config = INFERENCE_BACKENDS[backend];
    if (!config) {
      throw new Error(`Unknown backend: ${backend}`);
    }
    return `http://${host}:${config.port}`;
  }

  /**
   * Parse model registry YAML and extract model info
   */
  @func()
  async parseModelRegistry(source: Directory): Promise<string> {
    const registryPath = "meaisínfhoghlaim/models/registry.yaml";

    const container = dag
      .container()
      .from("python:3.12-slim")
      .withMountedDirectory("/workspace", source)
      .withWorkdir("/workspace")
      .withExec(["pip", "install", "--quiet", "pyyaml"]);

    const script = `
import yaml
import json

with open("${registryPath}") as f:
    data = yaml.safe_load(f)

models = data.get("models", {})
summary = {
    "total_models": len(models),
    "categories": {},
    "backends": {},
    "statuses": {}
}

for model_id, info in models.items():
    cat = info.get("category", "unknown")
    backend = info.get("backend", "unknown")
    status = info.get("status", "unknown")

    summary["categories"][cat] = summary["categories"].get(cat, 0) + 1
    summary["backends"][backend] = summary["backends"].get(backend, 0) + 1
    summary["statuses"][status] = summary["statuses"].get(status, 0) + 1

print(json.dumps(summary, indent=2))
`;

    const result = await container
      .withExec(["python", "-c", script])
      .stdout();

    return result;
  }

  /**
   * Sync model registry to LiteLLM config
   * Reads registry.yaml and generates litellm_config.yaml updates
   */
  @func()
  async syncModelRegistry(source: Directory): Promise<string> {
    // Parse and validate the registry
    const summary = await this.parseModelRegistry(source);
    return `Model registry synced:\n${summary}`;
  }

  /**
   * Generate client SDK code for accessing LiteLLM
   */
  @func()
  generateClientCode(
    runtime: "typescript" | "python",
    appName: string
  ): string {
    if (runtime === "typescript") {
      return `// ${appName} LiteLLM Client
// Auto-generated by Dagger ML Gateway module

export const llmConfig = {
  endpoint: process.env.LITELLM_URL || "${DEFAULT_LITELLM_ENDPOINT}",
  apiKey: process.env.LITELLM_API_KEY,
};

export async function chat(messages: Array<{ role: string; content: string }>, model = "fast") {
  const response = await fetch(\`\${llmConfig.endpoint}/v1/chat/completions\`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(llmConfig.apiKey ? { Authorization: \`Bearer \${llmConfig.apiKey}\` } : {}),
    },
    body: JSON.stringify({ model, messages }),
  });

  if (!response.ok) {
    throw new Error(\`LiteLLM error: \${response.status}\`);
  }

  return response.json();
}

// Model aliases
export const models = {
  fast: "fast",           // Gemma-3n (lightweight)
  reasoning: "reasoning", // Nemotron-3-Nano (complex tasks)
  vision: "vision",       // Qwen3-VL (multimodal)
  ocr: "ocr",            // olmOCR2 (document processing)
  image: "image",        // Z-Image-Turbo (generation)
  irish: "irish",        // Qomhrá (Irish language)
};
`;
    } else {
      return `# ${appName} LiteLLM Client
# Auto-generated by Dagger ML Gateway module

import os
import httpx

LITELLM_URL = os.environ.get("LITELLM_URL", "${DEFAULT_LITELLM_ENDPOINT}")
LITELLM_API_KEY = os.environ.get("LITELLM_API_KEY")

async def chat(messages: list[dict], model: str = "fast") -> dict:
    headers = {"Content-Type": "application/json"}
    if LITELLM_API_KEY:
        headers["Authorization"] = f"Bearer {LITELLM_API_KEY}"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{LITELLM_URL}/v1/chat/completions",
            json={"model": model, "messages": messages},
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

# Model aliases
MODELS = {
    "fast": "fast",           # Gemma-3n (lightweight)
    "reasoning": "reasoning", # Nemotron-3-Nano (complex tasks)
    "vision": "vision",       # Qwen3-VL (multimodal)
    "ocr": "ocr",            # olmOCR2 (document processing)
    "image": "image",        # Z-Image-Turbo (generation)
    "irish": "irish",        # Qomhrá (Irish language)
}
`;
    }
  }

  /**
   * Generate environment variables for LiteLLM integration
   */
  @func()
  generateEnvVars(endpoint?: string): string {
    const url = endpoint || DEFAULT_LITELLM_ENDPOINT;
    return `# LiteLLM Gateway Configuration
# Auto-generated by Dagger ML Gateway module

LITELLM_URL=${url}
LITELLM_API_KEY=  # Optional: Set if authentication required

# Model Aliases (resolved by LiteLLM)
# fast      -> Gemma-3n (lightweight, fast inference)
# reasoning -> Nemotron-3-Nano (complex reasoning tasks)
# vision    -> Qwen3-VL (multimodal vision-language)
# ocr       -> olmOCR2 (document text extraction)
# image     -> Z-Image-Turbo (image generation)
# irish     -> Qomhrá (Irish language model)
`;
  }

  /**
   * Validate LiteLLM configuration file
   */
  @func()
  async validateConfig(source: Directory): Promise<string> {
    const configPath = "meaisínfhoghlaim/models/litellm_config.yaml";

    const container = dag
      .container()
      .from("python:3.12-slim")
      .withMountedDirectory("/workspace", source)
      .withWorkdir("/workspace")
      .withExec(["pip", "install", "--quiet", "pyyaml"]);

    const script = `
import yaml
import json

with open("${configPath}") as f:
    config = yaml.safe_load(f)

validation = {
    "valid": True,
    "model_count": len(config.get("model_list", [])),
    "has_router_settings": "router_settings" in config,
    "has_general_settings": "general_settings" in config,
    "has_fallbacks": "litellm_settings" in config and "fallbacks" in config.get("litellm_settings", {}),
    "errors": []
}

# Check model list
for model in config.get("model_list", []):
    if "model_name" not in model:
        validation["errors"].append(f"Model missing name: {model}")
        validation["valid"] = False
    if "litellm_params" not in model:
        validation["errors"].append(f"Model {model.get('model_name', 'unknown')} missing litellm_params")
        validation["valid"] = False

print(json.dumps(validation, indent=2))
`;

    const result = await container
      .withExec(["python", "-c", script])
      .stdout();

    return result;
  }

  /**
   * Get container for local LiteLLM development
   */
  @func()
  async litellmContainer(source: Directory): Promise<Container> {
    return dag
      .container()
      .from("ghcr.io/berriai/litellm:main-stable")
      .withMountedDirectory("/workspace", source)
      .withWorkdir("/workspace")
      .withFile("/app/config.yaml", source.file("meaisínfhoghlaim/models/litellm_config.yaml"))
      .withExposedPort(4000)
      .withExec(["litellm", "--config", "/app/config.yaml", "--port", "4000"]);
  }

  /**
   * Start LiteLLM as a service for development
   */
  @func()
  async startLiteLLMService(source: Directory): Promise<Service> {
    const container = await this.litellmContainer(source);
    return container.asService();
  }
}
