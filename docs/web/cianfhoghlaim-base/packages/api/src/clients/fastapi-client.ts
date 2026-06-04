/**
 * FastAPI Client for oideachais/sruth pipelines
 *
 * Provides type-safe HTTP client for connecting TanStack Start
 * to FastAPI data pipelines with session forwarding and SSE streaming.
 */

// =============================================================================
// Session Type (matches BetterAuth session structure)
// =============================================================================

export interface SessionUser {
  id: string;
  email: string;
  name?: string | null;
  image?: string | null;
}

export interface Session {
  user: SessionUser;
  session?: {
    id: string;
    userId: string;
    expiresAt: Date;
  };
}

// =============================================================================
// Configuration
// =============================================================================

export interface FastAPIClientConfig {
  /** Base URL of the FastAPI server */
  baseUrl: string;
  /** Request timeout in milliseconds */
  timeout?: number;
  /** Additional headers to include */
  headers?: Record<string, string>;
}

// =============================================================================
// Request/Response Types
// =============================================================================

export interface ChatRequest {
  message: string;
  session_id?: string;
  language?: "en" | "ga";
  stream?: boolean;
  agents?: string[];
}

export interface ChatResponse {
  message: string;
  session_id: string;
  sources?: Source[];
  agents_used?: string[];
  metadata?: Record<string, unknown>;
}

export interface Source {
  id: string;
  title: string;
  url?: string;
  snippet?: string;
  score?: number;
}

export interface SearchRequest {
  query: string;
  language?: "en" | "ga";
  nation?: "ireland" | "uk" | "scotland" | "wales";
  limit?: number;
  offset?: number;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: string;
  facets?: Record<string, FacetValue[]>;
}

export interface SearchResult {
  id: string;
  title: string;
  content: string;
  score: number;
  metadata: Record<string, unknown>;
}

export interface FacetValue {
  value: string;
  count: number;
}

export interface HealthResponse {
  status: "healthy" | "degraded" | "unhealthy";
  services: Record<string, ServiceHealth>;
  timestamp: string;
}

export interface ServiceHealth {
  status: "up" | "down" | "unknown";
  latency_ms?: number;
  error?: string;
}

// =============================================================================
// SSE Event Types (AG-UI Protocol)
// =============================================================================

export type AGUIEventType =
  | "RUN_STARTED"
  | "RUN_FINISHED"
  | "RUN_ERROR"
  | "TEXT_MESSAGE_START"
  | "TEXT_MESSAGE_CONTENT"
  | "TEXT_MESSAGE_END"
  | "TOOL_CALL_START"
  | "TOOL_CALL_ARGS"
  | "TOOL_CALL_END"
  | "TOOL_RESULT"
  | "STATE_SNAPSHOT"
  | "STATE_DELTA"
  | "MESSAGES_SNAPSHOT"
  | "GENERATIVE_UI";

export interface AGUIEvent {
  type: AGUIEventType;
  timestamp: string;
  run_id?: string;
  message_id?: string;
  content?: string;
  delta?: string;
  tool_call?: ToolCall;
  tool_result?: ToolResult;
  state?: Record<string, unknown>;
  messages?: Message[];
  ui?: GenerativeUI;
  error?: string;
}

export interface ToolCall {
  id: string;
  name: string;
  args?: Record<string, unknown>;
}

export interface ToolResult {
  tool_call_id: string;
  output: unknown;
  is_error?: boolean;
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  tool_calls?: ToolCall[];
  tool_results?: ToolResult[];
}

export interface GenerativeUI {
  component: string;
  props: Record<string, unknown>;
  slot?: "main" | "sidebar" | "overlay";
}

// =============================================================================
// FastAPI Client Class
// =============================================================================

export class FastAPIClient {
  private baseUrl: string;
  private timeout: number;
  private defaultHeaders: Record<string, string>;

  constructor(config: FastAPIClientConfig) {
    this.baseUrl = config.baseUrl.replace(/\/$/, "");
    this.timeout = config.timeout ?? 30000;
    this.defaultHeaders = {
      "Content-Type": "application/json",
      ...config.headers,
    };
  }

  /**
   * Build headers with optional session forwarding
   */
  private buildHeaders(session?: Session | null): Record<string, string> {
    const headers = { ...this.defaultHeaders };

    if (session?.user) {
      headers["X-User-ID"] = session.user.id;
      headers["X-User-Email"] = session.user.email;
      if (session.user.name) {
        headers["X-User-Name"] = session.user.name;
      }
    }

    return headers;
  }

  /**
   * Make a fetch request with timeout and error handling
   */
  private async fetch<T>(
    path: string,
    options: RequestInit = {},
    session?: Session | null
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.buildHeaders(session),
          ...(options.headers as Record<string, string>),
        },
        signal: controller.signal,
      });

      if (!response.ok) {
        const error = await response.text();
        throw new FastAPIError(response.status, error, path);
      }

      return response.json() as Promise<T>;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  // ===========================================================================
  // Agent Endpoints
  // ===========================================================================

  /**
   * Send a chat message (non-streaming)
   */
  async chat(
    request: ChatRequest,
    session?: Session | null
  ): Promise<ChatResponse> {
    return this.fetch<ChatResponse>(
      "/agent/chat",
      {
        method: "POST",
        body: JSON.stringify({ ...request, stream: false }),
      },
      session
    );
  }

  /**
   * Send a chat message with SSE streaming
   * Returns an AsyncIterable of AG-UI events
   */
  async *chatStream(
    request: ChatRequest,
    session?: Session | null
  ): AsyncGenerator<AGUIEvent, void, unknown> {
    const url = `${this.baseUrl}/agent/chat/stream`;

    const response = await fetch(url, {
      method: "POST",
      headers: this.buildHeaders(session),
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new FastAPIError(response.status, error, "/agent/chat/stream");
    }

    if (!response.body) {
      throw new FastAPIError(500, "No response body", "/agent/chat/stream");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Parse SSE events from buffer
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6).trim();
            if (data && data !== "[DONE]") {
              try {
                const event = JSON.parse(data) as AGUIEvent;
                yield event;
              } catch {
                // Skip invalid JSON
                console.warn("Invalid SSE event:", data);
              }
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * Get chat session info
   */
  async getSession(
    sessionId: string,
    session?: Session | null
  ): Promise<{ session_id: string; messages: Message[]; created_at: string }> {
    return this.fetch(`/agent/sessions/${sessionId}`, { method: "GET" }, session);
  }

  /**
   * Clear a chat session
   */
  async clearSession(sessionId: string, session?: Session | null): Promise<void> {
    await this.fetch(`/agent/sessions/${sessionId}`, { method: "DELETE" }, session);
  }

  // ===========================================================================
  // Search Endpoints
  // ===========================================================================

  /**
   * Search curriculum content
   */
  async searchCurriculum(
    request: SearchRequest,
    session?: Session | null
  ): Promise<SearchResponse> {
    return this.fetch<SearchResponse>(
      "/search/curriculum",
      {
        method: "POST",
        body: JSON.stringify(request),
      },
      session
    );
  }

  /**
   * Search folklore collection
   */
  async searchFolklore(
    request: SearchRequest,
    session?: Session | null
  ): Promise<SearchResponse> {
    return this.fetch<SearchResponse>(
      "/search/folklore",
      {
        method: "POST",
        body: JSON.stringify(request),
      },
      session
    );
  }

  /**
   * Search terminology database
   */
  async searchTerminology(
    request: SearchRequest,
    session?: Session | null
  ): Promise<SearchResponse> {
    return this.fetch<SearchResponse>(
      "/search/terminology",
      {
        method: "POST",
        body: JSON.stringify(request),
      },
      session
    );
  }

  /**
   * Unified search across all domains
   */
  async searchUnified(
    request: SearchRequest & { domains?: string[] },
    session?: Session | null
  ): Promise<SearchResponse> {
    return this.fetch<SearchResponse>(
      "/search/unified",
      {
        method: "POST",
        body: JSON.stringify(request),
      },
      session
    );
  }

  // ===========================================================================
  // Health & Status
  // ===========================================================================

  /**
   * Check API health
   */
  async health(): Promise<HealthResponse> {
    return this.fetch<HealthResponse>("/health", { method: "GET" });
  }

  /**
   * Check agent system health
   */
  async agentHealth(): Promise<HealthResponse> {
    return this.fetch<HealthResponse>("/agent/health", { method: "GET" });
  }
}

// =============================================================================
// Error Class
// =============================================================================

export class FastAPIError extends Error {
  constructor(
    public status: number,
    public body: string,
    public path: string
  ) {
    super(`FastAPI error ${status} at ${path}: ${body}`);
    this.name = "FastAPIError";
  }

  get isNotFound(): boolean {
    return this.status === 404;
  }

  get isUnauthorized(): boolean {
    return this.status === 401;
  }

  get isServerError(): boolean {
    return this.status >= 500;
  }
}

// =============================================================================
// Factory Function
// =============================================================================

let _client: FastAPIClient | null = null;

export function getFastAPIClient(config?: FastAPIClientConfig): FastAPIClient {
  if (!_client) {
    const baseUrl =
      config?.baseUrl ??
      process.env.FASTAPI_URL ??
      "http://localhost:8000";

    _client = new FastAPIClient({
      baseUrl,
      timeout: config?.timeout ?? 30000,
      headers: config?.headers,
    });
  }
  return _client;
}
