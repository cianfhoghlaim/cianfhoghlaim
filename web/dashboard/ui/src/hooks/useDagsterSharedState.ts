/**
 * CopilotKit Shared State Hook for Dagster Pipeline Progress.
 *
 * Provides bidirectional state synchronization between:
 * - Dagster pipeline execution status
 * - CopilotKit agent context
 * - UI components
 *
 * This enables the AI assistant to be aware of:
 * - Currently running pipeline jobs
 * - Asset materialization progress
 * - Errors and completion status
 */

import { useState, useEffect, useCallback, useMemo } from "react";
import {
  useCopilotReadable,
  useCopilotAction,
} from "@copilotkit/react-core";

// Types for Dagster pipeline state
export interface DagsterJob {
  runId: string;
  jobName: string;
  status: "QUEUED" | "STARTED" | "SUCCESS" | "FAILURE" | "CANCELED";
  startTime: string;
  assets: string[];
}

export interface AssetProgress {
  asset: string;
  stage: string;
  progress: number;
  message: string;
  timestamp: string;
}

export interface DagsterError {
  asset: string;
  error: string;
  timestamp: string;
  runId?: string;
}

export interface DagsterPipelineState {
  activeJobs: DagsterJob[];
  completedAssets: string[];
  assetProgress: Record<string, AssetProgress>;
  errors: DagsterError[];
  overallProgress: number;
  currentAsset: string | null;
  currentStage: string | null;
  lastUpdated: string;
}

interface UseDagsterSharedStateOptions {
  /** Enable SSE connection for real-time updates */
  enableRealtime?: boolean;
  /** SSE endpoint URL */
  progressEndpoint?: string;
  /** Filter to specific assets */
  filterAssets?: string[];
  /** Polling interval for non-SSE updates (ms) */
  pollingInterval?: number;
}

const initialState: DagsterPipelineState = {
  activeJobs: [],
  completedAssets: [],
  assetProgress: {},
  errors: [],
  overallProgress: 0,
  currentAsset: null,
  currentStage: null,
  lastUpdated: new Date().toISOString(),
};

export function useDagsterSharedState(
  options: UseDagsterSharedStateOptions = {}
) {
  const {
    enableRealtime = true,
    progressEndpoint = "/api/progress",
    filterAssets,
    pollingInterval = 5000,
  } = options;

  const [state, setState] = useState<DagsterPipelineState>(initialState);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  // Calculate derived state values
  const isProcessing = useMemo(
    () =>
      state.activeJobs.length > 0 ||
      Object.values(state.assetProgress).some(
        (p) => p.stage !== "completed" && p.stage !== "error"
      ),
    [state.activeJobs, state.assetProgress]
  );

  const hasErrors = useMemo(() => state.errors.length > 0, [state.errors]);

  // Format state for CopilotKit context
  const copilotReadableState = useMemo(
    () => ({
      pipelineStatus: isProcessing ? "running" : "idle",
      activeJobCount: state.activeJobs.length,
      completedAssetCount: state.completedAssets.length,
      errorCount: state.errors.length,
      overallProgress: Math.round(state.overallProgress * 100),
      currentAsset: state.currentAsset,
      currentStage: state.currentStage,
      recentErrors: state.errors.slice(-3).map((e) => e.error),
      activeJobNames: state.activeJobs.map((j) => j.jobName),
    }),
    [state, isProcessing]
  );

  // Register state with CopilotKit for agent access
  useCopilotReadable({
    description:
      "Current Dagster pipeline status including active jobs, asset progress, errors, and overall completion percentage. Use this to understand what data processing is happening.",
    value: copilotReadableState,
  });

  // Register detailed progress for specific queries
  useCopilotReadable({
    description:
      "Detailed asset materialization progress showing each asset's current stage and completion percentage.",
    value: state.assetProgress,
  });

  // Register action to check specific asset status
  useCopilotAction({
    name: "checkAssetStatus",
    description:
      "Check the current status of a specific asset in the Dagster pipeline",
    parameters: [
      {
        name: "assetName",
        type: "string",
        description: "The name of the asset to check",
        required: true,
      },
    ],
    handler: async ({ assetName }) => {
      const progress = state.assetProgress[assetName];
      if (!progress) {
        return {
          found: false,
          message: `Asset '${assetName}' not found in current pipeline run`,
        };
      }
      return {
        found: true,
        asset: assetName,
        stage: progress.stage,
        progress: Math.round(progress.progress * 100),
        message: progress.message,
        lastUpdated: progress.timestamp,
      };
    },
  });

  // Register action to get pipeline summary
  useCopilotAction({
    name: "getPipelineSummary",
    description: "Get a summary of the current Dagster pipeline execution",
    parameters: [],
    handler: async () => {
      return {
        status: isProcessing ? "running" : "idle",
        activeJobs: state.activeJobs.map((j) => ({
          name: j.jobName,
          status: j.status,
          assets: j.assets.length,
        })),
        completedAssets: state.completedAssets.length,
        totalProgress: Math.round(state.overallProgress * 100),
        errors: state.errors.length > 0 ? state.errors.slice(-5) : [],
      };
    },
  });

  // Update state from SSE event
  const handleProgressEvent = useCallback(
    (event: AssetProgress) => {
      // Filter by assets if specified
      if (filterAssets && !filterAssets.includes(event.asset)) {
        return;
      }

      setState((prev) => {
        const newAssetProgress = {
          ...prev.assetProgress,
          [event.asset]: event,
        };

        // Calculate overall progress
        const progressValues = Object.values(newAssetProgress);
        const overallProgress =
          progressValues.length > 0
            ? progressValues.reduce((sum, p) => sum + p.progress, 0) /
              progressValues.length
            : 0;

        // Update completed assets
        const completedAssets = [
          ...new Set([
            ...prev.completedAssets,
            ...progressValues
              .filter((p) => p.stage === "completed")
              .map((p) => p.asset),
          ]),
        ];

        return {
          ...prev,
          assetProgress: newAssetProgress,
          overallProgress,
          completedAssets,
          currentAsset: event.asset,
          currentStage: event.stage,
          lastUpdated: event.timestamp,
        };
      });
    },
    [filterAssets]
  );

  // SSE connection management
  useEffect(() => {
    if (!enableRealtime) return;

    let eventSource: EventSource | null = null;
    let reconnectTimeout: NodeJS.Timeout | null = null;

    const connect = () => {
      eventSource = new EventSource(progressEndpoint);

      eventSource.onopen = () => {
        setIsConnected(true);
        setConnectionError(null);
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as AssetProgress;
          handleProgressEvent(data);
        } catch (e) {
          console.error("Failed to parse progress event:", e);
        }
      };

      eventSource.onerror = () => {
        setIsConnected(false);
        setConnectionError("Connection lost. Reconnecting...");

        // Reconnect after 5 seconds
        reconnectTimeout = setTimeout(() => {
          eventSource?.close();
          connect();
        }, 5000);
      };
    };

    connect();

    return () => {
      eventSource?.close();
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
  }, [enableRealtime, progressEndpoint, handleProgressEvent]);

  // Polling fallback for non-SSE updates
  useEffect(() => {
    if (enableRealtime || !pollingInterval) return;

    const poll = async () => {
      try {
        const response = await fetch("/api/dagster/status");
        if (response.ok) {
          const data = await response.json();
          setState((prev) => ({
            ...prev,
            ...data,
            lastUpdated: new Date().toISOString(),
          }));
        }
      } catch (e) {
        console.error("Polling error:", e);
      }
    };

    const interval = setInterval(poll, pollingInterval);
    poll(); // Initial fetch

    return () => clearInterval(interval);
  }, [enableRealtime, pollingInterval]);

  // Actions for manual state updates
  const addJob = useCallback((job: DagsterJob) => {
    setState((prev) => ({
      ...prev,
      activeJobs: [...prev.activeJobs, job],
      lastUpdated: new Date().toISOString(),
    }));
  }, []);

  const completeJob = useCallback((runId: string) => {
    setState((prev) => ({
      ...prev,
      activeJobs: prev.activeJobs.filter((j) => j.runId !== runId),
      lastUpdated: new Date().toISOString(),
    }));
  }, []);

  const addError = useCallback((error: DagsterError) => {
    setState((prev) => ({
      ...prev,
      errors: [...prev.errors, error],
      lastUpdated: new Date().toISOString(),
    }));
  }, []);

  const clearErrors = useCallback(() => {
    setState((prev) => ({
      ...prev,
      errors: [],
      lastUpdated: new Date().toISOString(),
    }));
  }, []);

  const reset = useCallback(() => {
    setState(initialState);
  }, []);

  return {
    // State
    state,
    isConnected,
    connectionError,
    isProcessing,
    hasErrors,

    // Derived values
    activeJobCount: state.activeJobs.length,
    completedAssetCount: state.completedAssets.length,
    errorCount: state.errors.length,
    progressPercentage: Math.round(state.overallProgress * 100),

    // Actions
    addJob,
    completeJob,
    addError,
    clearErrors,
    reset,

    // For direct state updates (e.g., from WebSocket)
    updateState: setState,
  };
}

/**
 * Simplified hook for components that only need to display progress.
 */
export function useDagsterProgress(assetName?: string) {
  const { state, isConnected, isProcessing } = useDagsterSharedState();

  if (assetName) {
    const progress = state.assetProgress[assetName];
    return {
      isConnected,
      isProcessing: progress
        ? progress.stage !== "completed" && progress.stage !== "error"
        : false,
      progress: progress?.progress ?? 0,
      stage: progress?.stage ?? "unknown",
      message: progress?.message ?? "",
    };
  }

  return {
    isConnected,
    isProcessing,
    progress: state.overallProgress,
    stage: state.currentStage,
    message: state.currentAsset
      ? `Processing ${state.currentAsset}`
      : "Idle",
  };
}
