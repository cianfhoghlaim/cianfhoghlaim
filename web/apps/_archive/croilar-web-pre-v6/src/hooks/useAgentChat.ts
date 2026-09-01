/**
 * useAgentChat — the AG-UI streaming chat hook for the croilar-web admin
 * agent chat page (`/agents/chat`).
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change (Wave 6.3 + 6.4). The hook wraps the canonical `HttpAgent` from
 * `@cianfhoghlaim/api-client` (which re-exports `@ag-ui/client`) and
 * uses CopilotKit v2's runtime contract for the admin chat surface.
 *
 * Returns the contract the chat page expects:
 *   { messages, currentText, toolCalls, state, error,
 *     sendMessage, stop, clearMessages, isRunning }
 *
 * Reference:
 *   - copilotkit v2 headless: `@copilotkit/react-core/v2` (useAgent)
 *   - AG-UI canonical types:  `@cianfhoghlaim/api-client` (EventType + BaseEvent)
 *   - canonical HttpAgent:    `web/packages/api-client/src/agui.ts`
 *   - chat page consumer:     `src/routes/admin/agents/chat.tsx`
 */

import { useCallback, useMemo, useRef, useState } from "react";
import {
  EventType,
  createCianfhoghlaimAgent,
  CIANFHOGHLAIM_RUNTIME_URL,
  type BaseEvent,
  type MessagesSnapshotEvent,
  type RunAgentInput,
  type StateDeltaEvent,
  type StateSnapshotEvent,
  type StepFinishedEvent,
  type StepStartedEvent,
  type TextMessageContentEvent,
  type TextMessageEndEvent,
  type TextMessageStartEvent,
  type ToolCallArgsEvent,
  type ToolCallEndEvent,
  type ToolCallStartEvent,
} from "@cianfhoghlaim/api-client";

export interface AgentChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  toolCalls?: ReadonlyArray<AgentChatToolCall>;
  timestamp?: Date;
}

export type AgentChatToolStatus =
  | "pending"
  | "running"
  | "complete"
  | "completed"
  | "failed"
  | "error";

export interface AgentChatToolCall {
  id: string;
  name: string;
  arguments?: Record<string, unknown>;
  result?: unknown;
  status: AgentChatToolStatus;
  error?: { message: string };
}

export interface AgentChatStep {
  id: string;
  name: string;
}

export interface AgentChatState {
  isRunning: boolean;
  threadId: string | null;
  currentRunId?: string | null;
  currentStep?: AgentChatStep;
  customState: Record<string, unknown>;
}

export interface UseAgentChatOptions {
  endpoint?: string;
  threadId?: string;
}

export interface UseAgentChatResult {
  messages: ReadonlyArray<AgentChatMessage>;
  currentText: string;
  toolCalls: ReadonlyArray<AgentChatToolCall>;
  state: AgentChatState;
  error: string | null;
  isRunning: boolean;
  sendMessage: (content: string) => Promise<void>;
  stop: () => void;
  clearMessages: () => void;
}

const DEFAULT_ENDPOINT = "/api/agent";

export function useAgentChat(
  options: UseAgentChatOptions = {},
): UseAgentChatResult {
  const { threadId } = options;

  const [messages, setMessages] = useState<ReadonlyArray<AgentChatMessage>>(
    [],
  );
  const [currentText, setCurrentText] = useState<string>("");
  const [toolCalls, setToolCalls] = useState<ReadonlyArray<AgentChatToolCall>>(
    [],
  );
  const [state, setState] = useState<AgentChatState>({
    isRunning: false,
    threadId: threadId ?? null,
    customState: {},
  });
  const [error, setError] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);
  const currentMessageIdRef = useRef<string | null>(null);
  const toolArgsBufferRef = useRef<Map<string, string>>(new Map());
  const threadIdRef = useRef<string | null>(threadId ?? null);
  const messagesRef = useRef<ReadonlyArray<AgentChatMessage>>([]);
  const currentTextRef = useRef<string>("");
  const toolCallsRef = useRef<ReadonlyArray<AgentChatToolCall>>([]);

  messagesRef.current = messages;
  currentTextRef.current = currentText;
  toolCallsRef.current = toolCalls;

  const agent = useMemo(() => createCianfhoghlaimAgent(), []);

  const handleEvent = useCallback((event: BaseEvent): void => {
    switch (event.type) {
      case EventType.RUN_STARTED: {
        const e = event as BaseEvent & { runId?: string };
        setState((prev) => ({
          ...prev,
          isRunning: true,
          currentRunId: e.runId ?? prev.currentRunId,
        }));
        setCurrentText("");
        setToolCalls([]);
        toolArgsBufferRef.current.clear();
        break;
      }

      case EventType.RUN_FINISHED:
        setState((prev) => ({
          ...prev,
          isRunning: false,
          currentRunId: undefined,
          currentStep: undefined,
        }));
        break;

      case EventType.RUN_ERROR: {
        const e = event as BaseEvent & {
          message?: string;
          code?: string;
        };
        setState((prev) => ({
          ...prev,
          isRunning: false,
          currentRunId: undefined,
        }));
        setError(e.message ?? e.code ?? "Agent run error");
        break;
      }

      case EventType.TEXT_MESSAGE_START: {
        const e = event as TextMessageStartEvent;
        currentMessageIdRef.current = e.messageId;
        setCurrentText("");
        break;
      }

      case EventType.TEXT_MESSAGE_CONTENT: {
        const e = event as TextMessageContentEvent;
        setCurrentText((prev) => prev + e.delta);
        break;
      }

      case EventType.TEXT_MESSAGE_END: {
        const e = event as TextMessageEndEvent;
        const finalText = currentTextRef.current;
        if (finalText) {
          const newMsg: AgentChatMessage = {
            id: e.messageId,
            role: "assistant",
            content: finalText,
            timestamp: new Date(),
            toolCalls:
              toolCallsRef.current.length > 0
                ? toolCallsRef.current
                : undefined,
          };
          setMessages((prev) => [...prev, newMsg]);
          setCurrentText("");
        }
        break;
      }

      case EventType.TOOL_CALL_START: {
        const e = event as ToolCallStartEvent;
        setToolCalls((prev) => [
          ...prev,
          { id: e.toolCallId, name: e.toolCallName, status: "running" },
        ]);
        toolArgsBufferRef.current.set(e.toolCallId, "");
        break;
      }

      case EventType.TOOL_CALL_ARGS: {
        const e = event as ToolCallArgsEvent;
        const next =
          (toolArgsBufferRef.current.get(e.toolCallId) ?? "") + e.delta;
        toolArgsBufferRef.current.set(e.toolCallId, next);
        try {
          const parsed = JSON.parse(next) as Record<string, unknown>;
          setToolCalls((prev) =>
            prev.map((tc) =>
              tc.id === e.toolCallId ? { ...tc, arguments: parsed } : tc,
            ),
          );
        } catch {
          // incomplete JSON; keep accumulating
        }
        break;
      }

      case EventType.TOOL_CALL_END: {
        const e = event as ToolCallEndEvent;
        setToolCalls((prev): ReadonlyArray<AgentChatToolCall> =>
          prev.map((tc) =>
            tc.id === e.toolCallId
              ? ({
                  ...tc,
                  status: e.error ? "error" : "completed",
                  result: e.result,
                  error: e.error,
                } as AgentChatToolCall)
              : tc,
          ),
        );
        break;
      }

      case EventType.STATE_SNAPSHOT: {
        const e = event as StateSnapshotEvent;
        setState((prev) => ({ ...prev, customState: { ...e.snapshot } }));
        break;
      }

      case EventType.STATE_DELTA: {
        const e = event as StateDeltaEvent;
        setState((prev) => ({
          ...prev,
          customState: { ...prev.customState, ...e.delta },
        }));
        break;
      }

      case EventType.MESSAGES_SNAPSHOT: {
        const e = event as MessagesSnapshotEvent;
        setMessages(
          e.messages.map((m) => ({
            id: m.id,
            role: (m.role === "user" || m.role === "assistant" || m.role === "system"
              ? m.role
              : "assistant") as AgentChatMessage["role"],
            content:
              typeof m.content === "string"
                ? m.content
                : JSON.stringify(m.content ?? ""),
          })),
        );
        break;
      }

      case EventType.STEP_STARTED: {
        const e = event as StepStartedEvent;
        setState((prev) => ({
          ...prev,
          currentStep: { id: e.stepName, name: e.stepName },
        }));
        break;
      }

      case EventType.STEP_FINISHED: {
        const e = event as StepFinishedEvent;
        setState((prev) => ({
          ...prev,
          currentStep:
            prev.currentStep?.id === e.stepName
              ? undefined
              : prev.currentStep,
        }));
        break;
      }

      default:
        break;
    }
  }, []);

  const sendMessage = useCallback(
    async (content: string): Promise<void> => {
      const userMessage: AgentChatMessage = {
        id: `msg_${Date.now()}`,
        role: "user",
        content,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setError(null);

      abortControllerRef.current?.abort();
      const controller = new AbortController();
      abortControllerRef.current = controller;

      const runInput: RunAgentInput = {
        threadId: threadIdRef.current ?? `thread_${Date.now()}`,
        runId: `run_${Date.now()}`,
        messages: [
          ...messagesRef.current.map((m) => ({
            id: m.id,
            role: m.role,
            content: m.content,
          })),
          { id: userMessage.id, role: "user", content: userMessage.content },
        ],
        state: {},
        tools: [],
        context: [],
        forwardedProps: {},
      };

      try {
        setState((prev) => ({
          ...prev,
          isRunning: true,
          currentRunId: runInput.runId,
          threadId: runInput.threadId,
        }));

        await agent.runAgent(runInput, {
          onEvent: ({ event }) => handleEvent(event),
        });

        setState((prev) => ({
          ...prev,
          isRunning: false,
          currentRunId: undefined,
          currentStep: undefined,
        }));
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") {
          return;
        }
        const message =
          err instanceof Error ? err.message : "Unknown agent error";
        setError(message);
        setState((prev) => ({
          ...prev,
          isRunning: false,
          currentRunId: undefined,
        }));
      }
    },
    [agent, handleEvent],
  );

  const stop = useCallback((): void => {
    abortControllerRef.current?.abort();
    try {
      agent.abortRun();
    } catch {
      // ignore
    }
    setState((prev) => ({ ...prev, isRunning: false }));
  }, [agent]);

  const clearMessages = useCallback((): void => {
    setMessages([]);
    setCurrentText("");
    setToolCalls([]);
    setError(null);
    toolArgsBufferRef.current.clear();
  }, []);

  return {
    messages,
    currentText,
    toolCalls,
    state,
    error,
    isRunning: state.isRunning,
    sendMessage,
    stop,
    clearMessages,
  };
}

export { CIANFHOGHLAIM_RUNTIME_URL, DEFAULT_ENDPOINT as DEFAULT_RUNTIME_PATH };
