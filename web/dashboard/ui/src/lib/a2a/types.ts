/**
 * A2A (Agent-to-Agent) Type Definitions
 *
 * Type definitions for A2A protocol communication between
 * education agents (curriculum, research, translation, etc.)
 */

/**
 * A2A Message Part Types
 */
export interface A2ATextPart {
  kind: "text";
  text: string;
}

export interface A2ADataPart {
  kind: "data";
  data: Record<string, unknown>;
}

export interface A2AFilePart {
  kind: "file";
  file: {
    uri?: string;
    bytes?: string;
    mimeType?: string;
    name?: string;
  };
}

export type A2APart = A2ATextPart | A2ADataPart | A2AFilePart;

/**
 * A2A Message
 */
export interface A2AMessage {
  kind: "message";
  messageId: string;
  role: "user" | "agent";
  parts: A2APart[];
  contextId?: string;
}

/**
 * A2A Task (for long-running operations)
 */
export interface A2ATask {
  kind: "task";
  taskId: string;
  status: A2ATaskStatus;
  artifacts?: A2AArtifact[];
}

export interface A2ATaskStatus {
  state: "pending" | "running" | "completed" | "failed" | "input-required";
  message?: A2AMessage;
}

export interface A2AArtifact {
  artifactId: string;
  type: string;
  data: unknown;
}

/**
 * A2A Status Update Event
 */
export interface A2ATaskStatusUpdateEvent {
  kind: "status-update";
  taskId: string;
  status: A2ATaskStatus;
}

/**
 * A2A Artifact Update Event
 */
export interface A2ATaskArtifactUpdateEvent {
  kind: "artifact-update";
  taskId: string;
  artifactId: string;
  artifact: A2AArtifact;
}

/**
 * Union of all A2A stream event types
 */
export type A2AStreamEvent =
  | A2AMessage
  | A2ATask
  | A2ATaskStatusUpdateEvent
  | A2ATaskArtifactUpdateEvent;

/**
 * Message Send Configuration
 */
export interface MessageSendConfiguration {
  acceptedOutputModes: ("text" | "file" | "data")[];
  blocking?: boolean;
}

/**
 * Message Send Parameters
 */
export interface MessageSendParams {
  message: A2AMessage;
  configuration?: MessageSendConfiguration;
}

/**
 * AG-UI Compatible Message (for conversion)
 */
export interface AGUIMessage {
  id?: string;
  role: "user" | "assistant" | "tool" | "system" | "developer" | "activity";
  content: string | AGUIContentPart[];
  toolCalls?: AGUIToolCall[];
  toolCallId?: string;
}

export interface AGUIContentPart {
  type: "text" | "binary";
  text?: string;
  url?: string;
  data?: string;
  mimeType?: string;
  filename?: string;
}

export interface AGUIToolCall {
  id: string;
  function: {
    name: string;
    arguments: string;
  };
}

/**
 * Surface Tracker for A2UI rendering
 */
export interface SurfaceTracker {
  has(surfaceId: string): boolean;
  add(surfaceId: string): void;
}

/**
 * Options for converting AGUI messages to A2A
 */
export interface ConvertAGUIMessagesOptions {
  contextId?: string;
  includeToolMessages?: boolean;
}

/**
 * Result of converting AGUI messages to A2A
 */
export interface ConvertedA2AMessages {
  contextId?: string;
  history: A2AMessage[];
  latestUserMessage?: A2AMessage;
}

/**
 * Options for converting A2A events to AGUI
 */
export interface ConvertA2AEventOptions {
  role?: "assistant" | "user";
  messageIdMap: Map<string, string>;
  onTextDelta?: (payload: { messageId: string; delta: string }) => void;
  source?: string;
  getCurrentText?: (messageId: string) => string | undefined;
  surfaceTracker?: SurfaceTracker;
}

/**
 * A2A Agent Run Result Summary
 */
export interface A2AAgentRunResultSummary {
  messages: Array<{ messageId: string; text: string }>;
  rawEvents: A2AStreamEvent[];
}

/**
 * Education-specific agent types
 */
export type EducationAgentType =
  | "curriculum"
  | "research"
  | "translation"
  | "corpus"
  | "geospatial"
  | "statistics";

/**
 * Education agent message with domain context
 */
export interface EducationA2AMessage extends A2AMessage {
  agentType?: EducationAgentType;
  nation?: string;
  language?: string;
  educationLevel?: string;
}
