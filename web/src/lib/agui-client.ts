/**
 * AG-UI Protocol Client for SSE streaming.
 * Handles communication with the AG-UI backend agent.
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
  | "TOOL_CALL_RESULT"
  | "STATE_SNAPSHOT"
  | "STATE_DELTA"
  | "MESSAGES_SNAPSHOT"
  | "STEP_STARTED"
  | "STEP_FINISHED";

export interface AGUIEvent {
  type: AGUIEventType;
  data: Record<string, unknown>;
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "tool";
  content: string;
  tool_call_id?: string;
  tool_calls?: ToolCall[];
}

export interface ToolCall {
  id: string;
  function: {
    name: string;
    arguments: string;
  };
}

export interface CurriculumUIState {
  search_query: string;
  selected_nations: string[];
  selected_levels: string[];
  selected_subjects: string[];
  results: CurriculumSearchResult[];
  comparison_table: ComparisonTableRow[];
  pending_translations: TranslationRequest[];
  is_loading: boolean;
  error: string | null;
}

export interface CurriculumSearchResult {
  outcome_id: string;
  nation: string;
  level: string;
  subject: string;
  title: string;
  description: string;
  language: string;
  similarity_score: number | null;
}

export interface ComparisonTableRow {
  topic: string;
  ireland: string | null;
  england: string | null;
  scotland: string | null;
  wales: string | null;
  northern_ireland: string | null;
  alignment_score: number | null;
}

export interface TranslationRequest {
  translation_id: string;
  source_language: string;
  target_language: string;
  source_text: string;
  translated_text: string;
  domain: string;
  confidence: number;
  needs_review: boolean;
}

// Simplified interface for Chat component
export interface AgentEvent {
  type: AGUIEventType;
  delta?: string;
  snapshot?: CurriculumUIState;
  name?: string;
  message?: string;
}

export interface RunAgentInput {
  thread_id: string;
  run_id: string;
  messages: Message[];
  tools?: Array<{
    name: string;
    description: string;
    parameters: Record<string, unknown>;
  }>;
  state?: CurriculumUIState;
}

// Note: streamAgent function is defined below with simpler interface

/**
 * Generate a unique ID for messages and runs.
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

/**
 * Apply JSON Patch delta to state.
 */
export function applyStateDelta<T extends Record<string, unknown>>(
  state: T,
  delta: Array<{ op: string; path: string; value?: unknown }>
): T {
  const newState = { ...state };

  for (const patch of delta) {
    const pathParts = patch.path.split("/").filter(Boolean);

    if (patch.op === "replace" || patch.op === "add") {
      let current: Record<string, unknown> = newState;
      for (let i = 0; i < pathParts.length - 1; i++) {
        current = current[pathParts[i]] as Record<string, unknown>;
      }
      current[pathParts[pathParts.length - 1]] = patch.value;
    }
  }

  return newState;
}

/**
 * Simplified stream function for Chat component.
 * Takes a message string and optional abort signal.
 */
export async function* streamAgent(
  message: string,
  signal?: AbortSignal,
  endpoint = "/api/agent"
): AsyncGenerator<AgentEvent> {
  const input: RunAgentInput = {
    thread_id: generateId(),
    run_id: generateId(),
    messages: [
      {
        id: generateId(),
        role: "user",
        content: message,
      },
    ],
  };

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify(input),
    signal,
  });

  if (!response.ok) {
    throw new Error(`Agent request failed: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("No response body");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      let currentEventType: AGUIEventType | null = null;

      for (const line of lines) {
        if (line.startsWith("event: ")) {
          currentEventType = line.slice(7).trim() as AGUIEventType;
        } else if (line.startsWith("data: ") && currentEventType) {
          try {
            const data = JSON.parse(line.slice(6));
            yield transformEvent(currentEventType, data);
          } catch (e) {
            console.error("Failed to parse SSE data:", e);
          }
          currentEventType = null;
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

/**
 * Transform raw AG-UI event to simplified AgentEvent.
 */
function transformEvent(type: AGUIEventType, data: Record<string, unknown>): AgentEvent {
  switch (type) {
    case "TEXT_MESSAGE_CONTENT":
      return { type, delta: data.delta as string };
    case "STATE_SNAPSHOT":
      return { type, snapshot: data.snapshot as CurriculumUIState };
    case "STATE_DELTA":
      return { type, delta: data as unknown as string };
    case "TOOL_CALL_START":
      return { type, name: data.name as string };
    case "RUN_ERROR":
      return { type, message: data.message as string };
    default:
      return { type };
  }
}

/**
 * Full stream function with RunAgentInput (for advanced use).
 */
export async function* streamAgentFull(
  input: RunAgentInput,
  endpoint = "/api/agent"
): AsyncGenerator<AGUIEvent> {
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    throw new Error(`Agent request failed: ${response.statusText}`);
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

    let currentEventType: AGUIEventType | null = null;

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        currentEventType = line.slice(7).trim() as AGUIEventType;
      } else if (line.startsWith("data: ") && currentEventType) {
        try {
          const data = JSON.parse(line.slice(6));
          yield { type: currentEventType, data };
        } catch (e) {
          console.error("Failed to parse SSE data:", e);
        }
        currentEventType = null;
      }
    }
  }
}
