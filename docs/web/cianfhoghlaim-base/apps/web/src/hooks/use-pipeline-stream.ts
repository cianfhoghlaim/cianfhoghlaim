/**
 * Pipeline Stream Hook
 *
 * React hook for consuming SSE streams from FastAPI pipelines.
 * Provides real-time chat, search, and agent interaction capabilities.
 */

import { useCallback, useRef, useState } from "react";

// =============================================================================
// Types
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
  | "start"
  | "text"
  | "done"
  | "error";

export interface AGUIEvent {
  type: AGUIEventType;
  timestamp?: string;
  run_id?: string;
  message_id?: string;
  content?: string;
  delta?: string;
  session_id?: string;
  agents_used?: string[];
  error?: string;
  tool_call?: {
    id: string;
    name: string;
    args?: Record<string, unknown>;
  };
  tool_result?: {
    tool_call_id: string;
    output: unknown;
    is_error?: boolean;
  };
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  sources?: Source[];
  toolCalls?: ToolCall[];
  isStreaming?: boolean;
}

export interface Source {
  id: string;
  title: string;
  url?: string;
  snippet?: string;
}

export interface ToolCall {
  id: string;
  name: string;
  args?: Record<string, unknown>;
  result?: unknown;
  isError?: boolean;
}

export interface UsePipelineStreamOptions {
  /** Callback when text content is received */
  onText?: (text: string, delta: string) => void;
  /** Callback when a tool call starts */
  onToolCall?: (toolCall: ToolCall) => void;
  /** Callback when a tool result is received */
  onToolResult?: (toolCallId: string, result: unknown, isError: boolean) => void;
  /** Callback when stream completes */
  onDone?: (agentsUsed: string[]) => void;
  /** Callback when an error occurs */
  onError?: (error: string) => void;
  /** API base path */
  apiPath?: string;
}

export interface UsePipelineStreamReturn {
  /** Current messages in the conversation */
  messages: Message[];
  /** Whether the stream is currently active */
  isStreaming: boolean;
  /** Current session ID */
  sessionId: string | null;
  /** Send a message and start streaming */
  sendMessage: (message: string, options?: SendMessageOptions) => Promise<void>;
  /** Stop the current stream */
  stopStream: () => void;
  /** Clear all messages and reset session */
  clearMessages: () => void;
  /** Clear the session on the server */
  clearSession: () => Promise<void>;
  /** Current error if any */
  error: string | null;
}

export interface SendMessageOptions {
  language?: "en" | "ga";
  agents?: string[];
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function usePipelineStream(
  options: UsePipelineStreamOptions = {}
): UsePipelineStreamReturn {
  const {
    onText,
    onToolCall,
    onToolResult,
    onDone,
    onError,
    apiPath = "/api/pipeline/agent/chat/stream",
  } = options;

  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);
  const currentMessageRef = useRef<string>("");

  /**
   * Send a message and start streaming the response
   */
  const sendMessage = useCallback(
    async (message: string, sendOptions: SendMessageOptions = {}) => {
      if (isStreaming) {
        console.warn("Already streaming, ignoring new message");
        return;
      }

      setError(null);
      setIsStreaming(true);
      currentMessageRef.current = "";

      // Add user message
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: "user",
        content: message,
        timestamp: new Date(),
      };

      // Add placeholder for assistant message
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: "",
        timestamp: new Date(),
        isStreaming: true,
      };

      setMessages((prev) => [...prev, userMessage, assistantMessage]);

      // Create abort controller
      abortControllerRef.current = new AbortController();

      try {
        const response = await fetch(apiPath, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            message,
            session_id: sessionId,
            language: sendOptions.language ?? "en",
            agents: sendOptions.agents,
            stream: true,
          }),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`API error: ${errorText}`);
        }

        if (!response.body) {
          throw new Error("No response body");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        const toolCalls: ToolCall[] = [];
        const sources: Source[] = [];
        let agentsUsed: string[] = [];

        while (true) {
          const { done, value } = await reader.read();

          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Parse SSE events
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6).trim();
              if (data && data !== "[DONE]") {
                try {
                  const event = JSON.parse(data) as AGUIEvent;
                  handleEvent(event);
                } catch {
                  // Skip invalid JSON
                }
              }
            }
          }
        }

        // Finalize message
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessage.id
              ? {
                  ...msg,
                  content: currentMessageRef.current,
                  isStreaming: false,
                  sources,
                  toolCalls,
                }
              : msg
          )
        );

        onDone?.(agentsUsed);

        function handleEvent(event: AGUIEvent) {
          switch (event.type) {
            case "start":
            case "RUN_STARTED":
              if (event.session_id) {
                setSessionId(event.session_id);
              }
              break;

            case "text":
            case "TEXT_MESSAGE_CONTENT":
              const delta = event.delta || event.content || "";
              currentMessageRef.current += delta;

              // Update message content
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMessage.id
                    ? { ...msg, content: currentMessageRef.current }
                    : msg
                )
              );

              onText?.(currentMessageRef.current, delta);
              break;

            case "TOOL_CALL_START":
              if (event.tool_call) {
                const toolCall: ToolCall = {
                  id: event.tool_call.id,
                  name: event.tool_call.name,
                  args: event.tool_call.args,
                };
                toolCalls.push(toolCall);
                onToolCall?.(toolCall);
              }
              break;

            case "TOOL_RESULT":
              if (event.tool_result) {
                const tc = toolCalls.find(
                  (t) => t.id === event.tool_result?.tool_call_id
                );
                if (tc) {
                  tc.result = event.tool_result.output;
                  tc.isError = event.tool_result.is_error;
                }
                onToolResult?.(
                  event.tool_result.tool_call_id,
                  event.tool_result.output,
                  event.tool_result.is_error ?? false
                );
              }
              break;

            case "done":
            case "RUN_FINISHED":
              if (event.agents_used) {
                agentsUsed = event.agents_used;
              }
              break;

            case "error":
            case "RUN_ERROR":
              const errorMsg = event.error || "Unknown error";
              setError(errorMsg);
              onError?.(errorMsg);
              break;
          }
        }
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") {
          // Stream was intentionally stopped
          return;
        }

        const errorMsg = err instanceof Error ? err.message : "Unknown error";
        setError(errorMsg);
        onError?.(errorMsg);

        // Update message to show error
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessage.id
              ? {
                  ...msg,
                  content: `Error: ${errorMsg}`,
                  isStreaming: false,
                }
              : msg
          )
        );
      } finally {
        setIsStreaming(false);
        abortControllerRef.current = null;
      }
    },
    [apiPath, isStreaming, onDone, onError, onText, onToolCall, onToolResult, sessionId]
  );

  /**
   * Stop the current stream
   */
  const stopStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  /**
   * Clear all messages (local only)
   */
  const clearMessages = useCallback(() => {
    setMessages([]);
    currentMessageRef.current = "";
    setError(null);
  }, []);

  /**
   * Clear the session on the server
   */
  const clearSession = useCallback(async () => {
    if (!sessionId) return;

    try {
      await fetch(`/api/pipeline/agent/sessions/${sessionId}`, {
        method: "DELETE",
        credentials: "include",
      });

      setSessionId(null);
      clearMessages();
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to clear session";
      setError(errorMsg);
    }
  }, [sessionId, clearMessages]);

  return {
    messages,
    isStreaming,
    sessionId,
    sendMessage,
    stopStream,
    clearMessages,
    clearSession,
    error,
  };
}
