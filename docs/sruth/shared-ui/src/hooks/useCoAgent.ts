/**
 * useCoAgent - Generic hook for AG-UI protocol agent state
 *
 * Provides SSE streaming, tool calls, and render components for any agent
 */

import { useCallback, useEffect, useReducer, useRef, useState } from 'react';

// AG-UI Event Types (aligned with AG-UI protocol)
export type AGUIEventType =
  | 'RUN_STARTED'
  | 'RUN_FINISHED'
  | 'RUN_ERROR'
  | 'TEXT_MESSAGE_START'
  | 'TEXT_MESSAGE_CONTENT'
  | 'TEXT_MESSAGE_END'
  | 'TOOL_CALL_START'
  | 'TOOL_CALL_ARGS'
  | 'TOOL_CALL_END'
  | 'TOOL_CALL_RESULT'
  | 'STATE_SNAPSHOT'
  | 'STATE_DELTA'
  | 'MESSAGES_SNAPSHOT'
  | 'STEP_STARTED'
  | 'STEP_FINISHED';

export interface RenderComponent {
  component: string;
  props: Record<string, unknown>;
  slot: 'main' | 'sidebar' | 'overlay';
}

export interface ToolCall {
  toolId: string;
  toolName: string;
  parameters: Record<string, unknown>;
  result?: unknown;
  status: 'pending' | 'running' | 'complete' | 'error';
}

export interface AgentMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface CoAgentState<TAgentState = Record<string, unknown>> {
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
  agentState: TAgentState | null;
  messages: AgentMessage[];
  streamingContent: string;
  renderComponents: RenderComponent[];
  activeToolCalls: Map<string, ToolCall>;
}

type CoAgentAction<TAgentState> =
  | { type: 'START_STREAM' }
  | { type: 'END_STREAM' }
  | { type: 'SET_ERROR'; payload: string }
  | { type: 'SET_STATE_SNAPSHOT'; payload: TAgentState }
  | { type: 'APPLY_STATE_DELTA'; payload: Partial<TAgentState> }
  | { type: 'APPEND_CONTENT'; payload: string }
  | { type: 'COMPLETE_MESSAGE' }
  | { type: 'ADD_RENDER_COMPONENT'; payload: RenderComponent }
  | { type: 'CLEAR_RENDER_COMPONENTS' }
  | { type: 'START_TOOL_CALL'; payload: ToolCall }
  | { type: 'UPDATE_TOOL_CALL_ARGS'; payload: { toolId: string; args: string } }
  | { type: 'COMPLETE_TOOL_CALL'; payload: { toolId: string; result: unknown } }
  | { type: 'ADD_USER_MESSAGE'; payload: string }
  | { type: 'RESET' };

function createReducer<TAgentState>() {
  return function coAgentReducer(
    state: CoAgentState<TAgentState>,
    action: CoAgentAction<TAgentState>
  ): CoAgentState<TAgentState> {
    switch (action.type) {
      case 'START_STREAM':
        return {
          ...state,
          isLoading: true,
          isStreaming: true,
          error: null,
          streamingContent: '',
          renderComponents: [],
        };

      case 'END_STREAM':
        return {
          ...state,
          isLoading: false,
          isStreaming: false,
        };

      case 'SET_ERROR':
        return {
          ...state,
          isLoading: false,
          isStreaming: false,
          error: action.payload,
        };

      case 'SET_STATE_SNAPSHOT':
        return {
          ...state,
          agentState: action.payload,
        };

      case 'APPLY_STATE_DELTA':
        if (!state.agentState) return state;
        return {
          ...state,
          agentState: {
            ...state.agentState,
            ...action.payload,
          },
        };

      case 'APPEND_CONTENT':
        return {
          ...state,
          streamingContent: state.streamingContent + action.payload,
        };

      case 'COMPLETE_MESSAGE':
        if (!state.streamingContent) return state;
        return {
          ...state,
          messages: [...state.messages, { role: 'assistant', content: state.streamingContent }],
          streamingContent: '',
        };

      case 'ADD_RENDER_COMPONENT':
        return {
          ...state,
          renderComponents: [...state.renderComponents, action.payload],
        };

      case 'CLEAR_RENDER_COMPONENTS':
        return {
          ...state,
          renderComponents: [],
        };

      case 'START_TOOL_CALL': {
        const newToolCalls = new Map(state.activeToolCalls);
        newToolCalls.set(action.payload.toolId, action.payload);
        return {
          ...state,
          activeToolCalls: newToolCalls,
        };
      }

      case 'UPDATE_TOOL_CALL_ARGS': {
        const updatedCalls = new Map(state.activeToolCalls);
        const existing = updatedCalls.get(action.payload.toolId);
        if (existing) {
          try {
            updatedCalls.set(action.payload.toolId, {
              ...existing,
              parameters: JSON.parse(action.payload.args),
            });
          } catch {
            // Partial JSON, skip
          }
        }
        return {
          ...state,
          activeToolCalls: updatedCalls,
        };
      }

      case 'COMPLETE_TOOL_CALL': {
        const completedCalls = new Map(state.activeToolCalls);
        const call = completedCalls.get(action.payload.toolId);
        if (call) {
          completedCalls.set(action.payload.toolId, {
            ...call,
            result: action.payload.result,
            status: 'complete',
          });
        }
        return {
          ...state,
          activeToolCalls: completedCalls,
        };
      }

      case 'ADD_USER_MESSAGE':
        return {
          ...state,
          messages: [...state.messages, { role: 'user', content: action.payload }],
        };

      case 'RESET':
        return {
          isLoading: false,
          isStreaming: false,
          error: null,
          agentState: null,
          messages: [],
          streamingContent: '',
          renderComponents: [],
          activeToolCalls: new Map(),
        };

      default:
        return state;
    }
  };
}

export interface UseCoAgentOptions<TAgentState = Record<string, unknown>> {
  /** Agent API endpoint */
  agentEndpoint?: string;
  /** Session ID for authentication */
  sessionId?: string;
  /** Additional context to send with requests */
  context?: Record<string, unknown>;
  /** Transform API state to frontend format */
  transformState?: (apiState: Record<string, unknown>) => TAgentState;
  /** Transform state delta from API */
  transformStateDelta?: (data: Record<string, unknown>) => Partial<TAgentState>;
}

export function useCoAgent<TAgentState = Record<string, unknown>>(
  options: UseCoAgentOptions<TAgentState> = {}
) {
  const {
    agentEndpoint = '/api/agent',
    sessionId,
    context = {},
    transformState = (s) => s as TAgentState,
    transformStateDelta = (d) => d as Partial<TAgentState>,
  } = options;

  const reducer = createReducer<TAgentState>();
  const initialState: CoAgentState<TAgentState> = {
    isLoading: false,
    isStreaming: false,
    error: null,
    agentState: null,
    messages: [],
    streamingContent: '',
    renderComponents: [],
    activeToolCalls: new Map(),
  };

  const [state, dispatch] = useReducer(reducer, initialState);
  const [threadId, setThreadId] = useState<string>(() => crypto.randomUUID());
  const abortControllerRef = useRef<AbortController | null>(null);

  // Process AG-UI events from SSE stream
  const processAGUIEvent = useCallback(
    (eventType: AGUIEventType, data: Record<string, unknown>) => {
      switch (eventType) {
        case 'RUN_STARTED':
          dispatch({ type: 'START_STREAM' });
          break;

        case 'RUN_FINISHED':
          dispatch({ type: 'COMPLETE_MESSAGE' });
          dispatch({ type: 'END_STREAM' });
          break;

        case 'RUN_ERROR':
          dispatch({ type: 'SET_ERROR', payload: data.message as string });
          break;

        case 'TEXT_MESSAGE_CONTENT':
          dispatch({ type: 'APPEND_CONTENT', payload: data.delta as string });
          break;

        case 'TEXT_MESSAGE_END':
          dispatch({ type: 'COMPLETE_MESSAGE' });
          break;

        case 'STATE_SNAPSHOT':
          dispatch({
            type: 'SET_STATE_SNAPSHOT',
            payload: transformState(data.state as Record<string, unknown>),
          });
          break;

        case 'STATE_DELTA':
          dispatch({
            type: 'APPLY_STATE_DELTA',
            payload: transformStateDelta(data),
          });
          break;

        case 'TOOL_CALL_START':
          dispatch({
            type: 'START_TOOL_CALL',
            payload: {
              toolId: data.tool_call_id as string,
              toolName: data.tool_call_name as string,
              parameters: {},
              status: 'running',
            },
          });
          break;

        case 'TOOL_CALL_ARGS':
          dispatch({
            type: 'UPDATE_TOOL_CALL_ARGS',
            payload: {
              toolId: data.tool_call_id as string,
              args: data.delta as string,
            },
          });
          break;

        case 'TOOL_CALL_END':
        case 'TOOL_CALL_RESULT':
          dispatch({
            type: 'COMPLETE_TOOL_CALL',
            payload: {
              toolId: data.tool_call_id as string,
              result: data.result,
            },
          });
          break;
      }
    },
    [transformState, transformStateDelta]
  );

  // Send message to agent
  const sendMessage = useCallback(
    async (content: string) => {
      if (state.isLoading) return;

      dispatch({ type: 'ADD_USER_MESSAGE', payload: content });

      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      abortControllerRef.current = new AbortController();

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }

      try {
        const response = await fetch(agentEndpoint, {
          method: 'POST',
          headers,
          body: JSON.stringify({
            messages: [...state.messages, { role: 'user', content }],
            context,
            thread_id: threadId,
          }),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          if (response.status === 402) {
            dispatch({ type: 'SET_ERROR', payload: 'Payment required' });
            return;
          }
          throw new Error(`HTTP ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.type) {
                  processAGUIEvent(data.type as AGUIEventType, data);
                }
              } catch {
                // Skip invalid JSON
              }
            }
          }
        }
      } catch (error) {
        if ((error as Error).name !== 'AbortError') {
          dispatch({
            type: 'SET_ERROR',
            payload: (error as Error).message,
          });
        }
      }
    },
    [state.isLoading, state.messages, agentEndpoint, sessionId, context, threadId, processAGUIEvent]
  );

  // Reset conversation
  const reset = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    dispatch({ type: 'RESET' });
    setThreadId(crypto.randomUUID());
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    // State
    ...state,
    threadId,

    // Actions
    sendMessage,
    reset,

    // Computed
    hasMessages: state.messages.length > 0,
    lastMessage: state.messages[state.messages.length - 1],
    sidebarComponents: state.renderComponents.filter((c) => c.slot === 'sidebar'),
    mainComponents: state.renderComponents.filter((c) => c.slot === 'main'),
    overlayComponents: state.renderComponents.filter((c) => c.slot === 'overlay'),
  };
}

export function useCoAgentStateRender<T>(
  agentState: T | null,
  render: (state: T) => React.ReactNode
): React.ReactNode {
  if (!agentState) return null;
  return render(agentState);
}
