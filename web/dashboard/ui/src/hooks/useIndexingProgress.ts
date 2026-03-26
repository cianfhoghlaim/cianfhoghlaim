import { useState, useEffect, useCallback } from "react";

/**
 * Hook for real-time indexing progress updates via SSE.
 *
 * Connects to the progress tracking endpoint for:
 * - PDF processing status
 * - Embedding generation progress
 * - Pipeline completion notifications
 */

interface ProgressEvent {
  asset: string;
  partition: string | null;
  stage: string;
  current: number;
  total: number;
  message: string;
  pct: number;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

interface UseIndexingProgressOptions {
  enabled?: boolean;
  assets?: string[];
}

export function useIndexingProgress(options: UseIndexingProgressOptions = {}) {
  const { enabled = true, assets } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [progress, setProgress] = useState<Record<string, ProgressEvent>>({});
  const [error, setError] = useState<string | null>(null);

  const connect = useCallback(() => {
    if (!enabled) return;

    const eventSource = new EventSource("/api/progress");

    eventSource.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as ProgressEvent;

        // Filter by assets if specified
        if (assets && !assets.includes(data.asset)) {
          return;
        }

        setProgress((prev) => ({
          ...prev,
          [data.asset]: data,
        }));
      } catch (e) {
        console.error("Failed to parse progress event:", e);
      }
    };

    eventSource.onerror = () => {
      setIsConnected(false);
      setError("Connection lost. Reconnecting...");

      // Reconnect after 5 seconds
      setTimeout(() => {
        eventSource.close();
        connect();
      }, 5000);
    };

    return () => {
      eventSource.close();
    };
  }, [enabled, assets]);

  useEffect(() => {
    const cleanup = connect();
    return cleanup;
  }, [connect]);

  // Get progress for a specific asset
  const getAssetProgress = useCallback(
    (assetName: string): ProgressEvent | null => {
      return progress[assetName] || null;
    },
    [progress]
  );

  // Get overall progress across all tracked assets
  const getOverallProgress = useCallback((): {
    current: number;
    total: number;
    pct: number;
  } => {
    const events = Object.values(progress);
    if (events.length === 0) {
      return { current: 0, total: 0, pct: 0 };
    }

    const current = events.reduce((sum, e) => sum + e.current, 0);
    const total = events.reduce((sum, e) => sum + e.total, 0);
    const pct = total > 0 ? (current / total) * 100 : 0;

    return { current, total, pct };
  }, [progress]);

  // Check if any asset is currently processing
  const isProcessing = useCallback((): boolean => {
    return Object.values(progress).some(
      (e) => e.stage !== "completed" && e.stage !== "error"
    );
  }, [progress]);

  return {
    isConnected,
    progress,
    error,
    getAssetProgress,
    getOverallProgress,
    isProcessing,
  };
}

/**
 * Hook for subscribing to progress updates for a specific asset.
 */
export function useAssetProgress(assetName: string) {
  const { progress, isConnected, error } = useIndexingProgress({
    assets: [assetName],
  });

  const assetProgress = progress[assetName];

  return {
    isConnected,
    error,
    progress: assetProgress,
    isProcessing: assetProgress
      ? assetProgress.stage !== "completed" && assetProgress.stage !== "error"
      : false,
    isCompleted: assetProgress?.stage === "completed",
    hasError: assetProgress?.stage === "error",
    percentage: assetProgress?.pct || 0,
    message: assetProgress?.message || "",
  };
}
