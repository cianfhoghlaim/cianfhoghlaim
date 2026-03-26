/**
 * LiteLLM Gateway Client
 * Provides a unified interface to all OCR/vision models
 */

export interface OCRRequest {
  model: string;
  imageBase64: string;
  prompt?: string;
  maxTokens?: number;
}

export interface OCRResponse {
  id: string;
  model: string;
  content: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  latencyMs: number;
}

export interface ModelInfo {
  id: string;
  owned_by: string;
}

class LiteLLMClient {
  private baseUrl: string;
  private apiKey?: string;
  private timeout: number;

  constructor(config: {
    baseUrl?: string;
    apiKey?: string;
    timeout?: number;
  } = {}) {
    this.baseUrl = config.baseUrl || "http://localhost:4000";
    this.apiKey = config.apiKey;
    this.timeout = config.timeout || 120000; // 2 minutes default
  }

  async getModels(): Promise<ModelInfo[]> {
    const response = await fetch(`${this.baseUrl}/models`, {
      headers: this.getHeaders(),
    });
    const data = await response.json();
    return data.data || [];
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        headers: this.getHeaders(),
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  async runOCR(request: OCRRequest): Promise<OCRResponse> {
    const startTime = Date.now();
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(`${this.baseUrl}/v1/chat/completions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...this.getHeaders(),
        },
        body: JSON.stringify({
          model: request.model,
          messages: [
            {
              role: "user",
              content: [
                {
                  type: "text",
                  text:
                    request.prompt ||
                    "Extract all text from this document. Preserve formatting, tables, and structure as markdown.",
                },
                {
                  type: "image_url",
                  image_url: {
                    url: `data:image/png;base64,${request.imageBase64}`,
                  },
                },
              ],
            },
          ],
          max_tokens: request.maxTokens || 4096,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      const data = await response.json();
      const latencyMs = Date.now() - startTime;

      if (!response.ok) {
        throw new Error(data.error?.message || "OCR request failed");
      }

      return {
        id: data.id,
        model: data.model,
        content: data.choices[0]?.message?.content || "",
        usage: data.usage
          ? {
              promptTokens: data.usage.prompt_tokens,
              completionTokens: data.usage.completion_tokens,
              totalTokens: data.usage.total_tokens,
            }
          : undefined,
        latencyMs,
      };
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === "AbortError") {
        throw new Error(`Request timeout after ${this.timeout}ms`);
      }
      throw error;
    }
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {};
    if (this.apiKey) {
      headers["Authorization"] = `Bearer ${this.apiKey}`;
    }
    return headers;
  }
}

// Singleton instance with environment configuration
export const litellm = new LiteLLMClient({
  baseUrl: typeof window !== "undefined"
    ? import.meta.env.VITE_LITELLM_URL || "http://localhost:4000"
    : process.env.LITELLM_URL || "http://localhost:4000",
  apiKey: typeof window !== "undefined"
    ? import.meta.env.VITE_LITELLM_API_KEY
    : process.env.LITELLM_API_KEY,
  timeout: 120000,
});

export default LiteLLMClient;
