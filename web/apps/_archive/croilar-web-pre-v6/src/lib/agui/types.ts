/**
 * croilar-web AG-UI types — thin re-export of the canonical AG-UI surface
 * (`@cianfhoghlaim/api-client`) plus the chat-UI-shaped `ToolCall` /
 * `Message` aliases that the admin agent chat page consumes.
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change (Wave 6.4). The 3 legacy stub files in this folder used loose
 * `Record<string, unknown>` shapes which produced 8 TS errors
 * (missing-property + unknown-type). Replaced with a thin re-export of
 * the canonical typed surface so existing call-sites keep importing from
 * `@/lib/agui/types`.
 *
 * Reference:
 *   - canonical:     `web/packages/api-client/src/agui.ts`
 *   - canonical events: `@ag-ui/client` (re-exported via api-client)
 */

import { EventType } from "@cianfhoghlaim/api-client";

export {
  EventType,
  type AgentSubscriber,
  type BaseEvent,
  type RunAgentInput,
  type RunStartedEvent,
  type RunFinishedEvent,
  type RunErrorEvent,
  type TextMessageStartEvent,
  type TextMessageContentEvent,
  type TextMessageEndEvent,
  type ToolCallStartEvent,
  type ToolCallArgsEvent,
  type ToolCallEndEvent,
  type StateSnapshotEvent,
  type StateDeltaEvent,
  type MessagesSnapshotEvent,
  type StepStartedEvent,
  type StepFinishedEvent,
  type CustomEvent,
  type RawEvent,
  type State,
} from "@cianfhoghlaim/api-client";

import type { Message as AGUIMessage } from "@cianfhoghlaim/api-client";

export type { AGUIMessage };

export type ToolCallStatus =
  | "pending"
  | "running"
  | "complete"
  | "completed"
  | "failed"
  | "error";

export interface ToolCall {
  id: string;
  name: string;
  arguments?: Record<string, unknown>;
  result?: unknown;
  status: ToolCallStatus;
  error?: { message: string };
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  toolCalls?: ReadonlyArray<ToolCall>;
  timestamp?: Date;
}

export interface AgentState {
  messages: ReadonlyArray<Message>;
  toolCalls: ReadonlyArray<ToolCall>;
  isRunning: boolean;
  threadId: string | null;
  currentRunId?: string | null;
  currentStep?: { id: string; name: string };
  customState: Record<string, unknown>;
}

export interface AGUIEvent {
  type: EventType;
  [key: string]: unknown;
}
