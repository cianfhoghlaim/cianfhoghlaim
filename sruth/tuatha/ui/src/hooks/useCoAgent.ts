/**
 * useCoAgent - Hook for CopilotKit agent state with A2UI protocol
 *
 * Implements useCoAgentStateRender pattern for reactive agent state
 */

import { useCallback, useEffect, useReducer, useRef, useState } from 'react';

// A2UI Event Types
type A2UIEventType =
  | 'lifecycle.start'
  | 'lifecycle.complete'
  | 'lifecycle.error'
  | 'state.snapshot'
  | 'state.delta'
  | 'tool.call.start'
  | 'tool.call.result'
  | 'render.component'
  | 'message.delta'
  | 'message.complete';

interface AgentState {
  agentType: string;
  conversationId: string;
  language: string;
  languageLevel: string;
  currentQuest: string | null;
  currentZone: string | null;
  vocabularyLearned: string[];
  xpEarned: number;
  toolsAvailable: string[];
}

interface RenderComponent {
  component: string;
  props: Record<string, unknown>;
  slot: 'main' | 'sidebar' | 'overlay';
}

interface ToolCall {
  toolId: string;
  toolName: string;
  parameters: Record<string, unknown>;
  result?: unknown;
  status: 'pending' | 'running' | 'complete' | 'error';
}

interface AgentMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface CoAgentState {
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
  agentState: AgentState | null;
  messages: AgentMessage[];
  streamingContent: string;
  renderComponents: RenderComponent[];
  activeToolCalls: Map<string, ToolCall>;
}

type CoAgentAction =
  | { type: 'START_STREAM' }
  | { type: 'END_STREAM' }
  | { type: 'SET_ERROR'; payload: string }
  | { type: 'SET_STATE_SNAPSHOT'; payload: AgentState }
  | { type: 'APPLY_STATE_DELTA'; payload: Partial<AgentState> }
  | { type: 'APPEND_CONTENT'; payload: string }
  | { type: 'COMPLETE_MESSAGE' }
  | { type: 'ADD_RENDER_COMPONENT'; payload: RenderComponent }
  | { type: 'CLEAR_RENDER_COMPONENTS' }
  | { type: 'START_TOOL_CALL'; payload: ToolCall }
  | { type: 'COMPLETE_TOOL_CALL'; payload: { toolId: string; result: unknown } }
  | { type: 'ADD_USER_MESSAGE'; payload: string }
  | { type: 'RESET' };

function coAgentReducer(state: CoAgentState, action: CoAgentAction): CoAgentState {
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
      return {
        ...state,
        messages: [
          ...state.messages,
          { role: 'assistant', content: state.streamingContent },
        ],
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

    case 'COMPLETE_TOOL_CALL': {
      const updatedToolCalls = new Map(state.activeToolCalls);
      const existingCall = updatedToolCalls.get(action.payload.toolId);
      if (existingCall) {
        updatedToolCalls.set(action.payload.toolId, {
          ...existingCall,
          result: action.payload.result,
          status: 'complete',
        });
      }
      return {
        ...state,
        activeToolCalls: updatedToolCalls,
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
}

const initialState: CoAgentState = {
  isLoading: false,
  isStreaming: false,
  error: null,
  agentState: null,
  messages: [],
  streamingContent: '',
  renderComponents: [],
  activeToolCalls: new Map(),
};

interface UseCoAgentOptions {
  agentEndpoint?: string;
  language?: string;
  languageLevel?: string;
  sessionId?: string;
  paymentId?: string;
  context?: Record<string, unknown>;
}

export function useCoAgent(options: UseCoAgentOptions = {}) {
  const {
    agentEndpoint = '/api/copilot/agent',
    language = 'ga',
    languageLevel = 'beginner',
    sessionId,
    paymentId,
    context = {},
  } = options;

  const [state, dispatch] = useReducer(coAgentReducer, initialState);
  const [conversationId, setConversationId] = useState<string>(() =>
    crypto.randomUUID()
  );
  const abortControllerRef = useRef<AbortController | null>(null);

  // Parse incoming SSE events
  const parseSSEEvent = useCallback(
    (line: string): { event: A2UIEventType; data: unknown } | null => {
      const eventMatch = line.match(/^event: (.+)$/);
      const dataMatch = line.match(/^data: (.+)$/);

      if (eventMatch && dataMatch) {
        return null; // Wait for complete event
      }

      return null;
    },
    []
  );

  // Process A2UI events
  const processA2UIEvent = useCallback(
    (eventType: A2UIEventType, data: Record<string, unknown>) => {
      switch (eventType) {
        case 'lifecycle.start':
          dispatch({ type: 'START_STREAM' });
          break;

        case 'lifecycle.complete':
          dispatch({ type: 'END_STREAM' });
          break;

        case 'lifecycle.error':
          dispatch({ type: 'SET_ERROR', payload: data.error as string });
          break;

        case 'state.snapshot':
          dispatch({
            type: 'SET_STATE_SNAPSHOT',
            payload: transformStateFromAPI(data.state as Record<string, unknown>),
          });
          break;

        case 'state.delta':
          dispatch({
            type: 'APPLY_STATE_DELTA',
            payload: transformStateDeltaFromAPI(data),
          });
          break;

        case 'tool.call.start':
          dispatch({
            type: 'START_TOOL_CALL',
            payload: {
              toolId: data.tool_id as string,
              toolName: data.tool_name as string,
              parameters: data.parameters as Record<string, unknown>,
              status: 'running',
            },
          });
          break;

        case 'tool.call.result':
          dispatch({
            type: 'COMPLETE_TOOL_CALL',
            payload: {
              toolId: data.tool_id as string,
              result: data.result,
            },
          });
          break;

        case 'render.component':
          dispatch({
            type: 'ADD_RENDER_COMPONENT',
            payload: {
              component: data.component as string,
              props: data.props as Record<string, unknown>,
              slot: data.slot as 'main' | 'sidebar' | 'overlay',
            },
          });
          break;

        case 'message.delta':
          dispatch({ type: 'APPEND_CONTENT', payload: data.content as string });
          break;

        case 'message.complete':
          dispatch({ type: 'COMPLETE_MESSAGE' });
          break;
      }
    },
    []
  );

  // Send message to agent
  const sendMessage = useCallback(
    async (content: string) => {
      if (state.isLoading) return;

      // Add user message
      dispatch({ type: 'ADD_USER_MESSAGE', payload: content });

      // Cancel any existing request
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
      if (paymentId) {
        headers['X-Payment-ID'] = paymentId;
      }

      try {
        const response = await fetch(agentEndpoint, {
          method: 'POST',
          headers,
          body: JSON.stringify({
            messages: [
              ...state.messages,
              { role: 'user', content },
            ],
            context: {
              ...context,
              preferred_language: language,
              language_level: languageLevel,
            },
            conversation_id: conversationId,
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
        let currentEvent: string | null = null;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Process complete SSE events
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('event: ')) {
              currentEvent = line.slice(7);
            } else if (line.startsWith('data: ') && currentEvent) {
              try {
                const data = JSON.parse(line.slice(6));
                processA2UIEvent(currentEvent as A2UIEventType, data);
              } catch {
                // Skip invalid JSON
              }
              currentEvent = null;
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
    [
      state.isLoading,
      state.messages,
      agentEndpoint,
      sessionId,
      paymentId,
      context,
      language,
      languageLevel,
      conversationId,
      processA2UIEvent,
    ]
  );

  // Reset conversation
  const reset = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    dispatch({ type: 'RESET' });
    setConversationId(crypto.randomUUID());
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
    conversationId,

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

// Transform API state to frontend format
function transformStateFromAPI(
  apiState: Record<string, unknown>
): AgentState {
  return {
    agentType: apiState.agent_type as string,
    conversationId: apiState.conversation_id as string,
    language: apiState.language as string,
    languageLevel: apiState.language_level as string,
    currentQuest: apiState.current_quest as string | null,
    currentZone: apiState.current_zone as string | null,
    vocabularyLearned: apiState.vocabulary_learned as string[],
    xpEarned: apiState.xp_earned as number,
    toolsAvailable: apiState.tools_available as string[],
  };
}

// Transform state delta from API
function transformStateDeltaFromAPI(
  data: Record<string, unknown>
): Partial<AgentState> {
  const delta: Partial<AgentState> = {};

  if ('xp_earned' in data) {
    delta.xpEarned = data.xp_earned as number;
  }
  if ('vocabulary_learned' in data) {
    delta.vocabularyLearned = data.vocabulary_learned as string[];
  }
  if ('current_quest' in data) {
    delta.currentQuest = data.current_quest as string | null;
  }
  if ('current_zone' in data) {
    delta.currentZone = data.current_zone as string | null;
  }

  return delta;
}

/**
 * useCoAgentStateRender - Hook for rendering agent state changes
 *
 * Follows CopilotKit's useCoAgentStateRender pattern
 */
export function useCoAgentStateRender<T>(
  agentState: T | null,
  render: (state: T) => React.ReactNode
): React.ReactNode {
  if (!agentState) return null;
  return render(agentState);
}

export type {
  AgentState,
  RenderComponent,
  ToolCall,
  AgentMessage,
  CoAgentState,
  A2UIEventType,
};
