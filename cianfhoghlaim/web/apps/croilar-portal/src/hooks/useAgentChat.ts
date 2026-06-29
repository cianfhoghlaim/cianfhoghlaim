import { useState, useCallback, useRef } from "react";
import {
  EventType,
  type AGUIEvent,
  type Message,
  type ToolCall,
  type AgentState,
} from "@/lib/agui/types";

interface UseAgentChatOptions {
  endpoint?: string;
  onEvent?: (event: AGUIEvent) => void;
}

export function useAgentChat(options: UseAgentChatOptions = {}) {
  const { endpoint = "/api/agent", onEvent } = options;

  const [messages, setMessages] = useState<Message[]>([]);
  const [state, setState] = useState<AgentState>({
    isRunning: false,
    customState: {},
  });
  const [currentText, setCurrentText] = useState("");
  const [toolCalls, setToolCalls] = useState<ToolCall[]>([]);
  const [error, setError] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);
  const currentMessageIdRef = useRef<string | null>(null);
  const toolArgsBufferRef = useRef<Map<string, string>>(new Map());

  const handleEvent = useCallback(
    (event: AGUIEvent) => {
      onEvent?.(event);

      switch (event.type) {
        // Lifecycle Events
        case EventType.RUN_STARTED:
          setState((prev) => ({
            ...prev,
            isRunning: true,
            currentRunId: event.runId,
          }));
          setError(null);
          setCurrentText("");
          setToolCalls([]);
          toolArgsBufferRef.current.clear();
          break;

        case EventType.RUN_FINISHED:
          setState((prev) => ({
            ...prev,
            isRunning: false,
            currentRunId: undefined,
            currentStep: undefined,
          }));
          // Finalize any accumulated text as a message
          if (currentText) {
            setMessages((prev) => [
              ...prev,
              {
                id: currentMessageIdRef.current || Date.now().toString(),
                role: "assistant",
                content: currentText,
                timestamp: new Date(),
                toolCalls: toolCalls.length > 0 ? [...toolCalls] : undefined,
              },
            ]);
            setCurrentText("");
            setToolCalls([]);
          }
          break;

        case EventType.RUN_ERROR:
          setState((prev) => ({
            ...prev,
            isRunning: false,
            currentRunId: undefined,
          }));
          setError(event.error.message);
          break;

        // Text Streaming Events
        case EventType.TEXT_MESSAGE_START:
          currentMessageIdRef.current = event.messageId;
          setCurrentText("");
          break;

        case EventType.TEXT_MESSAGE_CONTENT:
          setCurrentText((prev) => prev + event.content);
          break;

        case EventType.TEXT_MESSAGE_END:
          // Message complete, wait for RUN_FINISHED to finalize
          break;

        // Tool Execution Events
        case EventType.TOOL_CALL_START:
          setToolCalls((prev) => [
            ...prev,
            {
              id: event.toolCallId,
              name: event.toolName,
              status: "running",
            },
          ]);
          toolArgsBufferRef.current.set(event.toolCallId, "");
          break;

        case EventType.TOOL_CALL_ARGS:
          // Accumulate streamed JSON args
          const currentArgs =
            toolArgsBufferRef.current.get(event.toolCallId) || "";
          toolArgsBufferRef.current.set(
            event.toolCallId,
            currentArgs + event.args
          );
          try {
            const parsedArgs = JSON.parse(
              toolArgsBufferRef.current.get(event.toolCallId)!
            );
            setToolCalls((prev) =>
              prev.map((tc) =>
                tc.id === event.toolCallId
                  ? { ...tc, arguments: parsedArgs }
                  : tc
              )
            );
          } catch {
            // JSON not complete yet, continue accumulating
          }
          break;

        case EventType.TOOL_CALL_END:
          setToolCalls((prev) =>
            prev.map((tc) =>
              tc.id === event.toolCallId
                ? {
                    ...tc,
                    status: event.error ? "error" : "completed",
                    result: event.result,
                    error: event.error,
                  }
                : tc
            )
          );
          break;

        // State Management Events
        case EventType.STATE_SNAPSHOT:
          setState((prev) => ({
            ...prev,
            customState: event.state,
          }));
          break;

        case EventType.STATE_DELTA:
          setState((prev) => ({
            ...prev,
            customState: { ...prev.customState, ...event.delta },
          }));
          break;

        case EventType.MESSAGES_SNAPSHOT:
          setMessages(event.messages);
          break;

        // Multi-step Workflow Events
        case EventType.STEP_STARTED:
          setState((prev) => ({
            ...prev,
            currentStep: {
              id: event.stepId,
              name: event.stepName,
            },
          }));
          break;

        case EventType.STEP_FINISHED:
          setState((prev) => ({
            ...prev,
            currentStep: undefined,
          }));
          break;

        // Custom/Raw events
        case EventType.CUSTOM:
        case EventType.RAW:
          // Pass through to onEvent handler
          break;
      }
    },
    [onEvent, currentText, toolCalls]
  );

  const sendMessage = useCallback(
    async (content: string) => {
      // Add user message
      const userMessage: Message = {
        id: Date.now().toString(),
        role: "user",
        content,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Abort any existing request
      abortControllerRef.current?.abort();
      abortControllerRef.current = new AbortController();

      try {
        const response = await fetch(endpoint, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "text/event-stream",
          },
          body: JSON.stringify({
            message: content,
            messages: messages.concat(userMessage),
          }),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP error: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error("No response body");
        }

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
              const data = line.slice(6);
              if (data === "[DONE]") continue;

              try {
                const event: AGUIEvent = JSON.parse(data);
                handleEvent(event);
              } catch (e) {
                console.warn("Failed to parse SSE event:", data);
              }
            }
          }
        }
      } catch (err) {
        if ((err as Error).name !== "AbortError") {
          setError((err as Error).message);
          setState((prev) => ({ ...prev, isRunning: false }));
        }
      }
    },
    [endpoint, messages, handleEvent]
  );

  const stop = useCallback(() => {
    abortControllerRef.current?.abort();
    setState((prev) => ({ ...prev, isRunning: false }));
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setCurrentText("");
    setToolCalls([]);
    setError(null);
  }, []);

  return {
    messages,
    currentText,
    toolCalls,
    state,
    error,
    sendMessage,
    stop,
    clearMessages,
    isRunning: state.isRunning,
  };
}
