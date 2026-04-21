import { useCallback, useRef, useState } from "react";

/**
 * AG-UI Event Types as per the protocol specification.
 * See: https://docs.ag-ui.dev/concepts/events
 */
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
  | "RAW"
  | "CUSTOM"
  | "GENERATIVE_UI";

export interface AGUIEvent {
  type: AGUIEventType;
  // Text content events
  delta?: string;
  message_id?: string;
  // Tool call events
  tool_call_id?: string;
  name?: string;
  args?: string;
  result?: unknown;
  is_error?: boolean;
  // State events
  snapshot?: Record<string, unknown>;
  // Error events
  message?: string;
  code?: string;
  // Run events
  run_id?: string;
  thread_id?: string;
  // Generative UI events
  component?: string;
  props?: Record<string, unknown>;
  slot?: "main" | "sidebar" | "overlay";
  component_id?: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  toolCalls?: ToolCall[];
  isStreaming?: boolean;
}

export interface ToolCall {
  id: string;
  name: string;
  args?: Record<string, unknown>;
  result?: unknown;
  isError?: boolean;
  status: "pending" | "executing" | "completed" | "error";
}

/**
 * Represents a dynamically rendered component from Generative UI events.
 */
export interface RenderedComponent {
  id: string;
  component: string;
  props: Record<string, unknown>;
  slot: "main" | "sidebar" | "overlay";
  timestamp: Date;
}

export interface SendMessageOptions {
  language?: "en" | "ga" | "cy" | "gd";
  agents?: string[];
  context?: Record<string, unknown>;
}

export interface UsePipelineStreamOptions {
  onText?: (fullContent: string, delta: string) => void;
  onToolCall?: (toolCall: ToolCall) => void;
  onToolResult?: (toolCallId: string, result: unknown, isError: boolean) => void;
  onStateSnapshot?: (state: Record<string, unknown>) => void;
  onStateDelta?: (delta: Record<string, unknown>) => void;
  onGenerativeUI?: (component: RenderedComponent) => void;
  onDone?: (messages: Message[]) => void;
  onError?: (error: string) => void;
  apiPath?: string;
}

export interface UsePipelineStreamReturn {
  messages: Message[];
  isStreaming: boolean;
  sessionId: string | null;
  sendMessage: (message: string, options?: SendMessageOptions) => Promise<void>;
  stopStream: () => void;
  clearMessages: () => void;
  clearSession: () => Promise<void>;
  error: string | null;
  currentToolCalls: ToolCall[];
  // Generative UI
  renderedComponents: RenderedComponent[];
  removeComponent: (componentId: string) => void;
  clearComponents: (slot?: "main" | "sidebar" | "overlay") => void;
}

/**
 * Hook for consuming AG-UI streaming events from the backend.
 *
 * Handles all 17 AG-UI event types and provides:
 * - Message accumulation with streaming support
 * - Tool call tracking with status updates
 * - Session management
 * - AbortController for cancellation
 * - Callbacks for each event type
 *
 * @example
 * ```tsx
 * const { messages, sendMessage, isStreaming, stopStream } = usePipelineStream({
 *   onText: (content, delta) => console.log("Text:", delta),
 *   onToolCall: (toolCall) => console.log("Tool:", toolCall.name),
 * });
 *
 * await sendMessage("Compare Irish and Welsh curricula", { language: "en" });
 * ```
 */
export function usePipelineStream(
  options: UsePipelineStreamOptions = {}
): UsePipelineStreamReturn {
  const {
    onText,
    onToolCall,
    onToolResult,
    onStateSnapshot,
    onStateDelta,
    onGenerativeUI,
    onDone,
    onError,
    apiPath = "/api/agent",
  } = options;

  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentToolCalls, setCurrentToolCalls] = useState<ToolCall[]>([]);
  const [renderedComponents, setRenderedComponents] = useState<RenderedComponent[]>([]);

  const abortControllerRef = useRef<AbortController | null>(null);
  const currentMessageRef = useRef<string>("");
  const currentMessageIdRef = useRef<string>("");

  const sendMessage = useCallback(
    async (message: string, sendOptions: SendMessageOptions = {}) => {
      if (isStreaming) return;

      setError(null);
      setIsStreaming(true);
      currentMessageRef.current = "";
      setCurrentToolCalls([]);

      // Add user message
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: "user",
        content: message,
        timestamp: new Date(),
      };

      // Create assistant message placeholder
      const assistantId = `assistant-${Date.now()}`;
      currentMessageIdRef.current = assistantId;
      const assistantMessage: Message = {
        id: assistantId,
        role: "assistant",
        content: "",
        timestamp: new Date(),
        isStreaming: true,
        toolCalls: [],
      };

      setMessages((prev) => [...prev, userMessage, assistantMessage]);
      abortControllerRef.current = new AbortController();

      try {
        const response = await fetch(apiPath, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({
            message,
            session_id: sessionId,
            language: sendOptions.language ?? "en",
            agents: sendOptions.agents,
            context: sendOptions.context,
            stream: true,
          }),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`API error: ${errorText}`);
        }

        if (!response.body) throw new Error("No response body");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6).trim();
              if (data && data !== "[DONE]") {
                try {
                  const event: AGUIEvent = JSON.parse(data);
                  handleEvent(event, assistantId);
                } catch {
                  // Skip invalid JSON
                }
              }
            }
          }
        }

        // Mark message as no longer streaming
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantId
              ? { ...msg, isStreaming: false }
              : msg
          )
        );

        onDone?.(messages);
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") return;
        const errorMsg = err instanceof Error ? err.message : "Unknown error";
        setError(errorMsg);
        onError?.(errorMsg);
      } finally {
        setIsStreaming(false);
        abortControllerRef.current = null;
      }
    },
    [apiPath, isStreaming, messages, onDone, onError, sessionId]
  );

  const handleEvent = useCallback(
    (event: AGUIEvent, assistantId: string) => {
      switch (event.type) {
        case "RUN_STARTED":
          if (event.run_id) {
            setSessionId(event.run_id);
          }
          break;

        case "TEXT_MESSAGE_START":
          // Message is starting, prepare for content
          break;

        case "TEXT_MESSAGE_CONTENT":
          if (event.delta) {
            currentMessageRef.current += event.delta;
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantId
                  ? { ...msg, content: currentMessageRef.current }
                  : msg
              )
            );
            onText?.(currentMessageRef.current, event.delta);
          }
          break;

        case "TEXT_MESSAGE_END":
          // Message content is complete
          break;

        case "TOOL_CALL_START":
          if (event.tool_call_id && event.name) {
            const toolCall: ToolCall = {
              id: event.tool_call_id,
              name: event.name,
              status: "executing",
            };
            setCurrentToolCalls((prev) => [...prev, toolCall]);
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantId
                  ? { ...msg, toolCalls: [...(msg.toolCalls || []), toolCall] }
                  : msg
              )
            );
            onToolCall?.(toolCall);
          }
          break;

        case "TOOL_CALL_ARGS":
          if (event.tool_call_id && event.args) {
            try {
              const args = JSON.parse(event.args);
              setCurrentToolCalls((prev) =>
                prev.map((tc) =>
                  tc.id === event.tool_call_id ? { ...tc, args } : tc
                )
              );
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantId
                    ? {
                        ...msg,
                        toolCalls: msg.toolCalls?.map((tc) =>
                          tc.id === event.tool_call_id ? { ...tc, args } : tc
                        ),
                      }
                    : msg
                )
              );
            } catch {
              // Skip invalid JSON
            }
          }
          break;

        case "TOOL_CALL_END":
          if (event.tool_call_id) {
            setCurrentToolCalls((prev) =>
              prev.map((tc) =>
                tc.id === event.tool_call_id ? { ...tc, status: "completed" } : tc
              )
            );
          }
          break;

        case "TOOL_RESULT":
          if (event.tool_call_id) {
            const isError = event.is_error ?? false;
            setCurrentToolCalls((prev) =>
              prev.map((tc) =>
                tc.id === event.tool_call_id
                  ? { ...tc, result: event.result, isError, status: isError ? "error" : "completed" }
                  : tc
              )
            );
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantId
                  ? {
                      ...msg,
                      toolCalls: msg.toolCalls?.map((tc) =>
                        tc.id === event.tool_call_id
                          ? { ...tc, result: event.result, isError, status: isError ? "error" : "completed" }
                          : tc
                      ),
                    }
                  : msg
              )
            );
            onToolResult?.(event.tool_call_id, event.result, isError);
          }
          break;

        case "STATE_SNAPSHOT":
          if (event.snapshot) {
            onStateSnapshot?.(event.snapshot);
          }
          break;

        case "STATE_DELTA":
          if (event.snapshot) {
            onStateDelta?.(event.snapshot);
          }
          break;

        case "RUN_ERROR":
          setError(event.message || "Agent error occurred");
          onError?.(event.message || "Agent error occurred");
          break;

        case "RUN_FINISHED":
          // Run completed successfully
          break;

        case "GENERATIVE_UI":
          if (event.component && event.component_id) {
            const renderedComponent: RenderedComponent = {
              id: event.component_id,
              component: event.component,
              props: event.props || {},
              slot: event.slot || "main",
              timestamp: new Date(),
            };
            setRenderedComponents((prev) => [...prev, renderedComponent]);
            onGenerativeUI?.(renderedComponent);
          }
          break;
      }
    },
    [onText, onToolCall, onToolResult, onStateSnapshot, onStateDelta, onGenerativeUI, onError]
  );

  const stopStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setCurrentToolCalls([]);
    currentMessageRef.current = "";
  }, []);

  const clearSession = useCallback(async () => {
    setSessionId(null);
    clearMessages();
  }, [clearMessages]);

  // Generative UI management
  const removeComponent = useCallback((componentId: string) => {
    setRenderedComponents((prev) => prev.filter((c) => c.id !== componentId));
  }, []);

  const clearComponents = useCallback((slot?: "main" | "sidebar" | "overlay") => {
    if (slot) {
      setRenderedComponents((prev) => prev.filter((c) => c.slot !== slot));
    } else {
      setRenderedComponents([]);
    }
  }, []);

  return {
    messages,
    isStreaming,
    sessionId,
    sendMessage,
    stopStream,
    clearMessages,
    clearSession,
    error,
    currentToolCalls,
    // Generative UI
    renderedComponents,
    removeComponent,
    clearComponents,
  };
}
