/**
 * AG-UI consumer hook — the canonical React hook for subscribing to the
 * Agent-User Interaction protocol stream from the Cianfhoghlaim platform.
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change (Wave 6.4). The 5 consolidated web apps call `useAgUiStream` to
 * subscribe to a thread and receive a reactive stream of AG-UI events
 * (RUN_STARTED, TEXT_MESSAGE_CONTENT, TOOL_CALL_*, STATE_DELTA, …).
 *
 * The hook wraps `@ag-ui/react`'s `useAgent` hook and exposes the
 * simplified `PipelineEvent` envelope from `@cianfhoghlaim/contracts`.
 *
 * Reference:
 *   - AG-UI spec:        https://docs.ag-ui.com/
 *   - HttpAgent client:   web/packages/api-client/src/agui.ts
 *   - Stream endpoint:    web/hono-api/src/routes/agui/index.ts
 *   - @ag-ui/react:       https://www.npmjs.com/package/@ag-ui/react
 */

import { useAgent } from "@ag-ui/react";
import type { PipelineEvent } from "@cianfhoghlaim/contracts";
import {
  type AgentSubscriber,
  type RunAgentInput,
  CIANFHOGHLAIM_RUNTIME_URL,
  createCianfhoghlaimAgent,
} from "@cianfhoghlaim/api-client";

export interface UseAgUiStreamOptions {
  readonly threadId: string;
  readonly initialMessages?: ReadonlyArray<PipelineEvent>;
  readonly onStateDelta?: AgentSubscriber<"StateDelta">;
  readonly onToolCallStart?: AgentSubscriber<"ToolCallStart">;
  readonly onToolCallArgs?: AgentSubscriber<"ToolCallArgs">;
  readonly onToolCallEnd?: AgentSubscriber<"ToolCallEnd">;
  readonly onToolCallResult?: AgentSubscriber<"ToolCallResult">;
  readonly onRunFinished?: AgentSubscriber<"RunFinished">;
}

export interface UseAgUiStreamResult {
  readonly runId: string | null;
  readonly events: ReadonlyArray<PipelineEvent>;
  readonly isRunning: boolean;
  readonly sendMessage: (input: Partial<RunAgentInput>) => Promise<void>;
}

/**
 * Subscribe to one AG-UI thread. The agent is created lazily on the
 * client (browser-only) because the `HttpAgent` opens a streaming SSE
 * connection to `${runtimeBase}/agui/sse?thread_id=<id>`.
 *
 * Returns a reactive view of the thread's `PipelineEvent` log plus a
 * `sendMessage` callback that triggers `POST /agui/run`.
 */
export function useAgUiStream(
  options: UseAgUiStreamOptions,
): UseAgUiStreamResult {
  const agent = typeof window !== "undefined"
    ? createCianfhoghlaimAgent({
        threadId: options.threadId,
        runtimeUrl: CIANFHOGHLAIM_RUNTIME_URL,
      })
    : null;

  const {
    runId,
    messages,
    isRunning,
    send,
  } = useAgent({
    agent: agent ?? undefined,
    initialMessages: options.initialMessages as never,
    onStateDelta: options.onStateDelta,
    onToolCallStart: options.onToolCallStart,
    onToolCallArgs: options.onToolCallArgs,
    onToolCallEnd: options.onToolCallEnd,
    onToolCallResult: options.onToolCallResult,
    onRunFinished: options.onRunFinished,
  });

  return {
    runId,
    events: messages as unknown as ReadonlyArray<PipelineEvent>,
    isRunning,
    sendMessage: send as never,
  };
}

export { createCianfhoghlaimAgent, CIANFHOGHLAIM_RUNTIME_URL };
