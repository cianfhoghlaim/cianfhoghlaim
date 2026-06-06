/**
 * API client for crypto analytics backend
 * Integrates with Agno agents, knowledge graph, and data sources
 */

const API_BASE = "/api";

export interface ApiResponse<T> {
  data: T;
  error?: string;
  meta?: {
    timestamp: string;
    source: string;
  };
}

// Protocol data types
export interface Protocol {
  id: string;
  name: string;
  tvl: number;
  apy: number;
  category: string;
  chain: string;
  status: "healthy" | "warning" | "critical";
  riskScore: number;
  lastUpdated: string;
}

// Token data types
export interface Token {
  symbol: string;
  name: string;
  price: number;
  marketCap: number;
  volume24h: number;
  priceChange24h: number;
  chain: string;
  contractAddress?: string;
}

// Graph query types
export interface GraphQuery {
  query: string;
  params?: Record<string, unknown>;
}

export interface GraphResult {
  nodes: {
    id: string;
    labels: string[];
    properties: Record<string, unknown>;
  }[];
  relationships: {
    id: string;
    type: string;
    start: string;
    end: string;
    properties: Record<string, unknown>;
  }[];
}

// Chat types
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: { title: string; type: string; url?: string }[];
}

export interface ChatRequest {
  messages: ChatMessage[];
  context?: {
    activeProtocol?: string;
    portfolio?: string[];
  };
}

// API client
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async fetch<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options?.headers,
        },
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error || `HTTP ${response.status}`);
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      return {
        data: null as T,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  }

  // Protocol endpoints
  async getProtocols(): Promise<ApiResponse<Protocol[]>> {
    return this.fetch<Protocol[]>("/protocols");
  }

  async getProtocol(id: string): Promise<ApiResponse<Protocol>> {
    return this.fetch<Protocol>(`/protocols/${id}`);
  }

  // Token endpoints
  async getTokens(chain?: string): Promise<ApiResponse<Token[]>> {
    const params = chain ? `?chain=${chain}` : "";
    return this.fetch<Token[]>(`/tokens${params}`);
  }

  async getTokenPrice(symbol: string): Promise<ApiResponse<Token>> {
    return this.fetch<Token>(`/tokens/${symbol}`);
  }

  // Knowledge graph endpoints
  async queryGraph(query: GraphQuery): Promise<ApiResponse<GraphResult>> {
    return this.fetch<GraphResult>("/graph/query", {
      method: "POST",
      body: JSON.stringify(query),
    });
  }

  async searchGraph(term: string): Promise<ApiResponse<GraphResult>> {
    return this.fetch<GraphResult>(`/graph/search?q=${encodeURIComponent(term)}`);
  }

  async getEntityRelationships(
    entityId: string
  ): Promise<ApiResponse<GraphResult>> {
    return this.fetch<GraphResult>(`/graph/entity/${entityId}/relationships`);
  }

  // Chat endpoints
  async chat(request: ChatRequest): Promise<ApiResponse<ChatMessage>> {
    return this.fetch<ChatMessage>("/chat", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async *chatStream(
    request: ChatRequest
  ): AsyncGenerator<string, void, unknown> {
    const url = `${this.baseUrl}/chat/stream`;

    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });

    if (!response.ok || !response.body) {
      throw new Error("Failed to start chat stream");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      yield chunk;
    }
  }

  // Document endpoints
  async searchDocuments(
    query: string
  ): Promise<ApiResponse<{ id: string; title: string; excerpt: string }[]>> {
    return this.fetch(`/documents/search?q=${encodeURIComponent(query)}`);
  }

  async getDocument(
    id: string
  ): Promise<ApiResponse<{ id: string; title: string; content: string }>> {
    return this.fetch(`/documents/${id}`);
  }
}

export const api = new ApiClient();

// React Query hooks factory (optional)
export function createQueryKey(
  ...parts: (string | number | undefined)[]
): string[] {
  return parts.filter((p): p is string | number => p !== undefined).map(String);
}
