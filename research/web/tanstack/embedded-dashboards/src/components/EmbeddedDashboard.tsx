import { useState, useEffect } from "react";

interface EmbeddedDashboardProps {
  /** URL to embed in the iframe */
  src: string;
  /** Title for accessibility */
  title: string;
  /** Optional CSS class name */
  className?: string;
  /** Height of the iframe */
  height?: string;
  /** Width of the iframe */
  width?: string;
  /** Loading state text */
  loadingText?: string;
  /** Error handler */
  onError?: (error: Error) => void;
  /** Load complete handler */
  onLoad?: () => void;
}

/**
 * Component for embedding external dashboards (marimo, dagster) in an iframe.
 *
 * Features:
 * - Loading state indication
 * - Error handling
 * - Security sandboxing
 * - Responsive sizing
 */
export function EmbeddedDashboard({
  src,
  title,
  className = "",
  height = "600px",
  width = "100%",
  loadingText = "Loading dashboard...",
  onError,
  onLoad,
}: EmbeddedDashboardProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleLoad = () => {
    setIsLoading(false);
    setError(null);
    onLoad?.();
  };

  const handleError = () => {
    const errorMsg = `Failed to load dashboard: ${title}`;
    setIsLoading(false);
    setError(errorMsg);
    onError?.(new Error(errorMsg));
  };

  // Reset loading state when src changes
  useEffect(() => {
    setIsLoading(true);
    setError(null);
  }, [src]);

  return (
    <div className={`embedded-dashboard ${className}`} style={{ position: "relative" }}>
      {/* Loading overlay */}
      {isLoading && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            backgroundColor: "rgba(255, 255, 255, 0.9)",
            zIndex: 10,
          }}
        >
          <div style={{ textAlign: "center" }}>
            <div
              style={{
                width: "40px",
                height: "40px",
                border: "3px solid #f3f3f3",
                borderTop: "3px solid #3498db",
                borderRadius: "50%",
                animation: "spin 1s linear infinite",
                margin: "0 auto 10px",
              }}
            />
            <p style={{ margin: 0, color: "#666" }}>{loadingText}</p>
          </div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div
          style={{
            padding: "20px",
            backgroundColor: "#fee",
            border: "1px solid #fcc",
            borderRadius: "4px",
            color: "#c00",
            textAlign: "center",
          }}
        >
          <p style={{ margin: 0 }}>{error}</p>
          <button
            onClick={() => {
              setIsLoading(true);
              setError(null);
            }}
            style={{
              marginTop: "10px",
              padding: "8px 16px",
              cursor: "pointer",
            }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Embedded iframe */}
      {!error && (
        <iframe
          src={src}
          title={title}
          width={width}
          height={height}
          onLoad={handleLoad}
          onError={handleError}
          style={{
            border: "1px solid #e0e0e0",
            borderRadius: "4px",
            display: isLoading ? "none" : "block",
          }}
          // Security sandboxing - allow necessary features for dashboards
          sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-downloads"
          // Loading optimization
          loading="lazy"
          // Referrer policy for privacy
          referrerPolicy="no-referrer-when-downgrade"
          // Allow fullscreen for visualizations
          allowFullScreen
        />
      )}

      {/* CSS animation for spinner */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
