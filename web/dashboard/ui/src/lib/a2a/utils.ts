/**
 * A2A Utility Functions
 *
 * Conversion utilities for A2A ↔ AG-UI message formats.
 */

import { randomUUID } from "./uuid";
import type {
  A2AMessage,
  A2APart,
  A2ATextPart,
  A2ADataPart,
  A2AFilePart,
  A2AStreamEvent,
  AGUIMessage,
  AGUIContentPart,
  ConvertAGUIMessagesOptions,
  ConvertedA2AMessages,
  ConvertA2AEventOptions,
} from "./types";

/**
 * AG-UI Event Types (subset for compatibility)
 */
export const EventType = {
  RUN_STARTED: "run-started",
  RUN_FINISHED: "run-finished",
  RUN_ERROR: "run-error",
  TEXT_MESSAGE_CHUNK: "text-message-chunk",
  TEXT_MESSAGE_START: "text-message-start",
  TEXT_MESSAGE_END: "text-message-end",
  TOOL_CALL_START: "tool-call-start",
  TOOL_CALL_ARGS: "tool-call-args",
  TOOL_CALL_END: "tool-call-end",
  TOOL_CALL_RESULT: "tool-call-result",
  RAW: "raw",
  ACTIVITY_SNAPSHOT: "activity-snapshot",
  ACTIVITY_DELTA: "activity-delta",
} as const;

export interface BaseEvent {
  type: string;
  [key: string]: unknown;
}

export interface TextMessageChunkEvent extends BaseEvent {
  type: typeof EventType.TEXT_MESSAGE_CHUNK;
  messageId: string;
  role: "assistant" | "user";
  delta: string;
}

export interface ToolCallStartEvent extends BaseEvent {
  type: typeof EventType.TOOL_CALL_START;
  toolCallId: string;
  toolCallName: string;
  parentMessageId: string;
}

export interface ToolCallArgsEvent extends BaseEvent {
  type: typeof EventType.TOOL_CALL_ARGS;
  toolCallId: string;
  delta: string;
}

export interface ToolCallEndEvent extends BaseEvent {
  type: typeof EventType.TOOL_CALL_END;
  toolCallId: string;
}

export interface ToolCallResultEvent extends BaseEvent {
  type: typeof EventType.TOOL_CALL_RESULT;
  toolCallId: string;
  content: string;
  messageId: string;
  role: "tool";
}

export interface RawEvent extends BaseEvent {
  type: typeof EventType.RAW;
  event: unknown;
  source: string;
}

// Role mapping from AG-UI to A2A
const ROLE_MAP: Record<string, "user" | "agent" | undefined> = {
  user: "user",
  assistant: "agent",
  tool: "agent",
  system: "user",
  developer: "user",
};

const TOOL_RESULT_PART_TYPE = "tool-result";
const TOOL_CALL_PART_TYPE = "tool-call";

/**
 * Safe JSON parse with fallback
 */
const safeJsonParse = (value: string): unknown => {
  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
};

/**
 * Create a text part
 */
const createTextPart = (text: string): A2ATextPart => ({
  kind: "text",
  text,
});

/**
 * Create a file part from binary content
 */
const createFilePart = (
  content: Extract<AGUIContentPart, { type: "binary" }>
): A2AFilePart | null => {
  if (content.url) {
    return {
      kind: "file",
      file: {
        uri: content.url,
        mimeType: content.mimeType,
        name: content.filename,
      },
    };
  }

  if (content.data) {
    return {
      kind: "file",
      file: {
        bytes: content.data,
        mimeType: content.mimeType,
        name: content.filename,
      },
    };
  }

  return null;
};

/**
 * Convert AG-UI message content to A2A parts
 */
const messageContentToParts = (message: AGUIMessage): A2APart[] => {
  const parts: A2APart[] = [];
  const { content } = message;

  if (typeof content === "string") {
    const trimmed = content.trim();
    if (trimmed.length > 0) {
      parts.push(createTextPart(trimmed));
    }
  } else if (Array.isArray(content)) {
    for (const chunk of content) {
      if (chunk.type === "text" && chunk.text) {
        const value = chunk.text.trim();
        if (value.length > 0) {
          parts.push(createTextPart(value));
        }
      } else if (chunk.type === "binary") {
        const filePart = createFilePart(chunk as any);
        if (filePart) {
          parts.push(filePart);
        }
      } else {
        parts.push({ kind: "data", data: chunk } as A2ADataPart);
      }
    }
  } else if (content && typeof content === "object") {
    parts.push({
      kind: "data",
      data: content as Record<string, unknown>,
    });
  }

  // Handle tool calls
  if (message.role === "assistant" && message.toolCalls?.length) {
    for (const toolCall of message.toolCalls) {
      parts.push({
        kind: "data",
        data: {
          type: TOOL_CALL_PART_TYPE,
          id: toolCall.id,
          name: toolCall.function.name,
          arguments: safeJsonParse(toolCall.function.arguments),
          rawArguments: toolCall.function.arguments,
        },
      });
    }
  }

  // Handle tool results
  if (message.role === "tool") {
    const payload =
      typeof message.content === "string"
        ? safeJsonParse(message.content)
        : message.content;
    parts.push({
      kind: "data",
      data: {
        type: TOOL_RESULT_PART_TYPE,
        toolCallId: message.toolCallId,
        payload,
      },
    });
  }

  return parts;
};

/**
 * Convert AG-UI messages to A2A format
 */
export function convertAGUIMessagesToA2A(
  messages: AGUIMessage[],
  options: ConvertAGUIMessagesOptions = {}
): ConvertedA2AMessages {
  const history: A2AMessage[] = [];
  const includeToolMessages = options.includeToolMessages ?? true;
  const contextId = options.contextId;

  for (const message of messages) {
    // Skip activity messages
    if (message.role === "activity") {
      continue;
    }

    // Skip tool messages if not included
    if (message.role === "tool" && !includeToolMessages) {
      continue;
    }

    // Skip system/developer messages
    if (message.role === "system" || message.role === "developer") {
      continue;
    }

    const mappedRole =
      ROLE_MAP[message.role] ?? (message.role === "tool" ? "agent" : undefined);

    if (!mappedRole) {
      continue;
    }

    const parts = messageContentToParts(message);

    if (parts.length === 0 && mappedRole !== "agent") {
      continue;
    }

    const messageId = message.id ?? randomUUID();

    history.push({
      kind: "message",
      messageId,
      role: mappedRole,
      parts,
      contextId,
    });
  }

  const latestUserMessage = [...history]
    .reverse()
    .find((msg) => msg.role === "user");

  return {
    contextId,
    history,
    latestUserMessage,
  };
}

/**
 * Check if event is an A2A message
 */
const isA2AMessage = (event: A2AStreamEvent): event is A2AMessage =>
  event.kind === "message";

/**
 * Resolve or create a mapped message ID
 */
function resolveMappedMessageId(
  originalId: string,
  options: ConvertA2AEventOptions,
  aliasKey?: string
): string {
  if (aliasKey) {
    const existingAliasId = options.messageIdMap.get(aliasKey);
    if (existingAliasId) {
      options.messageIdMap.set(originalId, existingAliasId);
      return existingAliasId;
    }
  }

  const existingId = options.messageIdMap.get(originalId);
  if (existingId) {
    if (aliasKey) {
      options.messageIdMap.set(aliasKey, existingId);
    }
    return existingId;
  }

  const newId = randomUUID();
  options.messageIdMap.set(originalId, newId);
  if (aliasKey) {
    options.messageIdMap.set(aliasKey, newId);
  }
  return newId;
}

/**
 * Convert A2A message to AG-UI events
 */
function convertMessageToEvents(
  message: A2AMessage,
  options: ConvertA2AEventOptions,
  aliasKey?: string
): BaseEvent[] {
  const role = options.role ?? "assistant";
  const events: BaseEvent[] = [];

  const originalId = message.messageId ?? randomUUID();
  const mappedId = resolveMappedMessageId(originalId, options, aliasKey);

  const openToolCalls = new Set<string>();

  for (const part of message.parts ?? []) {
    if (part.kind === "text") {
      const textPart = part as A2ATextPart;
      const partText = textPart.text ?? "";
      if (partText) {
        const previousText = options.getCurrentText?.(mappedId) ?? "";

        if (partText !== previousText) {
          const deltaText = partText.startsWith(previousText)
            ? partText.slice(previousText.length)
            : partText;

          if (deltaText.length > 0) {
            const chunkEvent: TextMessageChunkEvent = {
              type: EventType.TEXT_MESSAGE_CHUNK,
              messageId: mappedId,
              role,
              delta: deltaText,
            };
            options.onTextDelta?.({ messageId: mappedId, delta: deltaText });
            events.push(chunkEvent);
          }
        }
      }
      continue;
    }

    if (part.kind === "data") {
      const dataPart = part as A2ADataPart;
      const payload = dataPart.data;

      // Handle tool calls
      if (
        payload &&
        typeof payload === "object" &&
        (payload as any).type === TOOL_CALL_PART_TYPE
      ) {
        const toolCallId = (payload as any).id ?? randomUUID();
        const toolCallName = (payload as any).name ?? "unknown_tool";
        const args = (payload as any).arguments;

        const startEvent: ToolCallStartEvent = {
          type: EventType.TOOL_CALL_START,
          toolCallId,
          toolCallName,
          parentMessageId: mappedId,
        };
        events.push(startEvent);

        if (args !== undefined) {
          const argsEvent: ToolCallArgsEvent = {
            type: EventType.TOOL_CALL_ARGS,
            toolCallId,
            delta: JSON.stringify(args),
          };
          events.push(argsEvent);
        }

        openToolCalls.add(toolCallId);
        continue;
      }

      // Handle tool results
      if (
        payload &&
        typeof payload === "object" &&
        (payload as any).type === TOOL_RESULT_PART_TYPE &&
        (payload as any).toolCallId
      ) {
        const toolCallId = (payload as any).toolCallId;
        const toolResultEvent: ToolCallResultEvent = {
          type: EventType.TOOL_CALL_RESULT,
          toolCallId,
          content: JSON.stringify((payload as any).payload ?? payload),
          messageId: randomUUID(),
          role: "tool",
        };
        events.push(toolResultEvent);

        if (openToolCalls.has(toolCallId)) {
          const endEvent: ToolCallEndEvent = {
            type: EventType.TOOL_CALL_END,
            toolCallId,
          };
          events.push(endEvent);
          openToolCalls.delete(toolCallId);
        }

        continue;
      }

      continue;
    }
  }

  // Close any open tool calls
  for (const toolCallId of openToolCalls) {
    const endEvent: ToolCallEndEvent = {
      type: EventType.TOOL_CALL_END,
      toolCallId,
    };
    events.push(endEvent);
  }

  return events;
}

/**
 * Convert A2A stream event to AG-UI events
 */
export function convertA2AEventToAGUIEvents(
  event: A2AStreamEvent,
  options: ConvertA2AEventOptions
): BaseEvent[] {
  const events: BaseEvent[] = [];
  const source = options.source ?? "a2a";

  if (isA2AMessage(event)) {
    return convertMessageToEvents(event, options);
  }

  // Handle status updates
  if (event.kind === "status-update") {
    const statusMessage = event.status?.message;
    const statusState = event.status?.state;
    const aliasKey =
      statusState && statusState !== "input-required"
        ? `${event.taskId}:status`
        : undefined;

    if (statusMessage && statusMessage.kind === "message") {
      return convertMessageToEvents(
        statusMessage as A2AMessage,
        options,
        aliasKey
      );
    }
    return events;
  }

  // Handle task events
  if (event.kind === "task") {
    const rawEvent: RawEvent = {
      type: EventType.RAW,
      event,
      source,
    };
    events.push(rawEvent);
    return events;
  }

  // Fallback for unknown events
  const fallbackEvent: RawEvent = {
    type: EventType.RAW,
    event,
    source,
  };
  events.push(fallbackEvent);
  return events;
}

/**
 * Tool definition for sending messages to A2A agents
 */
export const sendMessageToA2AAgentTool = {
  name: "send_message_to_a2a_agent",
  description:
    "Sends a task to the agent named `agentName`, including the full conversation context and goal",
  parameters: {
    type: "object",
    properties: {
      agentName: {
        type: "string",
        description: "The name of the A2A agent to send the message to.",
      },
      task: {
        type: "string",
        description:
          "The comprehensive conversation-context summary and goal to be achieved regarding the user inquiry.",
      },
    },
    required: ["task"],
  },
} as const;
