/**
 * useCoAgent Hook - Extended AG-UI Integration.
 *
 * Extends CopilotKit's useCoAgent with support for:
 * - GENERATIVE_UI events (dynamic component rendering)
 * - SSE event streaming
 * - Component registry integration
 */

import { useState, useCallback, useEffect, useRef } from "react";
import { useCoAgent as useCopilotCoAgent, useCopilotReadable } from "@copilotkit/react-core";
import {
  useGenerativeUI,
  type GenerativeUIEvent,
  type RenderedComponent,
  type SlotType,
} from "../components/generative";

// ============================================================================
// Types
// ============================================================================

export interface AGUIEvent {
  type: string;
  timestamp: string;
  run_id?: string;
  thread_id?: string;
  [key: string]: unknown;
}

export interface UseCoAgentOptions<TState> {
  /** Agent name for CopilotKit */
  name: string;
  /** Initial state */
  initialState: TState;
  /** SSE endpoint for streaming events (optional) */
  streamEndpoint?: string;
  /** Enable generative UI handling */
  enableGenerativeUI?: boolean;
  /** Max components per slot */
  maxComponentsPerSlot?: number;
  /** Callback when generative UI component is rendered */
  onGenerativeUIRender?: (component: RenderedComponent) => void;
  /** Callback when any AG-UI event is received */
  onEvent?: (event: AGUIEvent) => void;
}

export interface UseCoAgentReturn<TState> {
  /** Current state from CopilotKit */
  state: TState;
  /** Update state */
  setState: (updater: TState | ((prev: TState) => TState)) => void;
  /** Run the agent with a message */
  run?: (message: string, args?: Record<string, unknown>) => Promise<void>;
  /** Whether currently streaming */
  isStreaming: boolean;
  /** Current run ID */
  runId: string | null;
  /** Generative UI components by slot */
  componentsBySlot: Record<SlotType, RenderedComponent[]>;
  /** Add a generative UI component */
  addComponent: (event: GenerativeUIEvent) => void;
  /** Remove a generative UI component */
  removeComponent: (componentId: string) => void;
  /** Clear all generative UI components */
  clearComponents: () => void;
  /** Connect to SSE stream */
  connectStream: (endpoint?: string) => void;
  /** Disconnect from SSE stream */
  disconnectStream: () => void;
  /** SSE connection status */
  isConnected: boolean;
}

// ============================================================================
// Hook Implementation
// ============================================================================

export function useCoAgentWithUI<TState extends Record<string, unknown>>(
  options: UseCoAgentOptions<TState>
): UseCoAgentReturn<TState> {
  const {
    name,
    initialState,
    streamEndpoint,
    enableGenerativeUI = true,
    maxComponentsPerSlot = 10,
    onGenerativeUIRender,
    onEvent,
  } = options;

  // CopilotKit's useCoAgent
  const { state, setState, run } = useCopilotCoAgent<TState>({
    name,
    initialState,
  });

  // Streaming state
  const [isStreaming, setIsStreaming] = useState(false);
  const [runId, setRunId] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Generative UI management
  const {
    componentsBySlot,
    addComponent,
    removeComponent,
    clearAll: clearComponents,
  } = useGenerativeUI({
    maxComponentsPerSlot,
    onComponentRendered: onGenerativeUIRender,
  });

  // Expose generative UI state to CopilotKit
  useCopilotReadable({
    description: "Currently rendered generative UI components from agent responses",
    value: {
      mainComponents: componentsBySlot.main.length,
      sidebarComponents: componentsBySlot.sidebar.length,
      overlayComponents: componentsBySlot.overlay.length,
      componentIds: [
        ...componentsBySlot.main,
        ...componentsBySlot.sidebar,
        ...componentsBySlot.overlay,
      ].map((c) => c.id),
    },
  });

  // Handle incoming AG-UI events
  const handleEvent = useCallback(
    (event: AGUIEvent) => {
      onEvent?.(event);

      // Track run lifecycle
      if (event.type === "RUN_STARTED") {
        setIsStreaming(true);
        setRunId(event.run_id ?? null);
      } else if (event.type === "RUN_FINISHED" || event.type === "RUN_ERROR") {
        setIsStreaming(false);
      }

      // Handle generative UI events
      if (enableGenerativeUI && event.type === "GENERATIVE_UI") {
        addComponent(event as unknown as GenerativeUIEvent);
      }

      // Handle state updates
      if (event.type === "STATE_SNAPSHOT" && event.state) {
        setState((prev) => ({
          ...prev,
          ...(event.state as Partial<TState>),
        }));
      } else if (event.type === "STATE_DELTA" && event.delta) {
        setState((prev) => ({
          ...prev,
          ...(event.delta as Partial<TState>),
        }));
      }
    },
    [enableGenerativeUI, addComponent, setState, onEvent]
  );

  // SSE connection management
  const connectStream = useCallback(
    (endpoint?: string) => {
      const url = endpoint ?? streamEndpoint;
      if (!url) {
        console.warn("[useCoAgent] No stream endpoint provided");
        return;
      }

      // Close existing connection
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        setIsConnected(true);
      };

      eventSource.onmessage = (e) => {
        try {
          const event = JSON.parse(e.data) as AGUIEvent;
          handleEvent(event);
        } catch (err) {
          console.error("[useCoAgent] Failed to parse event:", err);
        }
      };

      eventSource.onerror = () => {
        setIsConnected(false);
        // Auto-reconnect after 5 seconds
        setTimeout(() => {
          if (eventSourceRef.current === eventSource) {
            connectStream(url);
          }
        }, 5000);
      };
    },
    [streamEndpoint, handleEvent]
  );

  const disconnectStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    }
  }, []);

  // Auto-connect if endpoint provided
  useEffect(() => {
    if (streamEndpoint) {
      connectStream(streamEndpoint);
    }
    return () => {
      disconnectStream();
    };
  }, [streamEndpoint, connectStream, disconnectStream]);

  return {
    state,
    setState,
    run,
    isStreaming,
    runId,
    componentsBySlot,
    addComponent,
    removeComponent,
    clearComponents,
    connectStream,
    disconnectStream,
    isConnected,
  };
}

/**
 * Simple wrapper for components that just need generative UI rendering.
 */
export function useGenerativeUIEvents(options: {
  streamEndpoint?: string;
  maxComponentsPerSlot?: number;
  onRender?: (component: RenderedComponent) => void;
}) {
  const {
    componentsBySlot,
    addComponent,
    removeComponent,
    clearAll,
    connectStream,
    disconnectStream,
    isConnected,
  } = useCoAgentWithUI({
    name: "generative_ui_listener",
    initialState: {},
    streamEndpoint: options.streamEndpoint,
    enableGenerativeUI: true,
    maxComponentsPerSlot: options.maxComponentsPerSlot,
    onGenerativeUIRender: options.onRender,
  });

  return {
    componentsBySlot,
    addComponent,
    removeComponent,
    clearComponents: clearAll,
    connectStream,
    disconnectStream,
    isConnected,
  };
}

export default useCoAgentWithUI;
