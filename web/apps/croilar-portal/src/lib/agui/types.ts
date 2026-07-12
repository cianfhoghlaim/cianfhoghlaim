// AG-UI Protocol Event Types
// Based on the CopilotKit AG-UI specification

export enum EventType {
  // Lifecycle Events
  RUN_STARTED = "RUN_STARTED",
  RUN_FINISHED = "RUN_FINISHED",
  RUN_ERROR = "RUN_ERROR",

  // Text Streaming Events
  TEXT_MESSAGE_START = "TEXT_MESSAGE_START",
  TEXT_MESSAGE_CONTENT = "TEXT_MESSAGE_CONTENT",
  TEXT_MESSAGE_END = "TEXT_MESSAGE_END",

  // Tool Execution Events
  TOOL_CALL_START = "TOOL_CALL_START",
  TOOL_CALL_ARGS = "TOOL_CALL_ARGS",
  TOOL_CALL_END = "TOOL_CALL_END",

  // State Management Events
  STATE_SNAPSHOT = "STATE_SNAPSHOT",
  STATE_DELTA = "STATE_DELTA",
  MESSAGES_SNAPSHOT = "MESSAGES_SNAPSHOT",

  // Utility Events
  RAW = "RAW",
  CUSTOM = "CUSTOM",

  // Multi-step Workflow Events
  STEP_STARTED = "STEP_STARTED",
  STEP_FINISHED = "STEP_FINISHED",
}

export interface BaseEvent {
  type: EventType;
  timestamp?: string;
}

export interface RunStartedEvent extends BaseEvent {
  type: EventType.RUN_STARTED;
  runId: string;
  threadId?: string;
}

export interface RunFinishedEvent extends BaseEvent {
  type: EventType.RUN_FINISHED;
  runId: string;
}

export interface RunErrorEvent extends BaseEvent {
  type: EventType.RUN_ERROR;
  runId: string;
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}

export interface TextMessageStartEvent extends BaseEvent {
  type: EventType.TEXT_MESSAGE_START;
  messageId: string;
}

export interface TextMessageContentEvent extends BaseEvent {
  type: EventType.TEXT_MESSAGE_CONTENT;
  messageId: string;
  content: string;
}

export interface TextMessageEndEvent extends BaseEvent {
  type: EventType.TEXT_MESSAGE_END;
  messageId: string;
}

export interface ToolCallStartEvent extends BaseEvent {
  type: EventType.TOOL_CALL_START;
  toolCallId: string;
  toolName: string;
}

export interface ToolCallArgsEvent extends BaseEvent {
  type: EventType.TOOL_CALL_ARGS;
  toolCallId: string;
  args: string; // JSON string, streamed incrementally
}

export interface ToolCallEndEvent extends BaseEvent {
  type: EventType.TOOL_CALL_END;
  toolCallId: string;
  result?: unknown;
  error?: string;
}

export interface StateSnapshotEvent extends BaseEvent {
  type: EventType.STATE_SNAPSHOT;
  state: Record<string, unknown>;
}

export interface StateDeltaEvent extends BaseEvent {
  type: EventType.STATE_DELTA;
  delta: Record<string, unknown>;
}

export interface MessagesSnapshotEvent extends BaseEvent {
  type: EventType.MESSAGES_SNAPSHOT;
  messages: Message[];
}

export interface StepStartedEvent extends BaseEvent {
  type: EventType.STEP_STARTED;
  stepId: string;
  stepName: string;
}

export interface StepFinishedEvent extends BaseEvent {
  type: EventType.STEP_FINISHED;
  stepId: string;
}

export interface RawEvent extends BaseEvent {
  type: EventType.RAW;
  data: unknown;
}

export interface CustomEvent extends BaseEvent {
  type: EventType.CUSTOM;
  name: string;
  data: unknown;
}

export type AGUIEvent =
  | RunStartedEvent
  | RunFinishedEvent
  | RunErrorEvent
  | TextMessageStartEvent
  | TextMessageContentEvent
  | TextMessageEndEvent
  | ToolCallStartEvent
  | ToolCallArgsEvent
  | ToolCallEndEvent
  | StateSnapshotEvent
  | StateDeltaEvent
  | MessagesSnapshotEvent
  | StepStartedEvent
  | StepFinishedEvent
  | RawEvent
  | CustomEvent;

// Message types
export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  toolCalls?: ToolCall[];
}

export interface ToolCall {
  id: string;
  name: string;
  status: "pending" | "running" | "completed" | "error";
  arguments?: Record<string, unknown>;
  result?: unknown;
  error?: string;
}

// Agent state
export interface AgentState {
  isRunning: boolean;
  currentRunId?: string;
  currentStep?: {
    id: string;
    name: string;
  };
  customState: Record<string, unknown>;
}
