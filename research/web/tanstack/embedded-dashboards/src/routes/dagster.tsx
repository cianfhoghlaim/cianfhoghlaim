import { createFileRoute, redirect } from "@tanstack/react-router";
import { getSession } from "@/lib/auth-server";
import { EmbeddedDashboard } from "@/components/EmbeddedDashboard";
import { useState } from "react";

export const Route = createFileRoute("/dagster")({
  beforeLoad: async () => {
    const session = await getSession();
    if (!session) {
      throw redirect({ to: "/" });
    }
    return { session };
  },
  component: DagsterPage,
});

function DagsterPage() {
  const [loadStatus, setLoadStatus] = useState<"loading" | "loaded" | "error">(
    "loading"
  );

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px",
        }}
      >
        <div>
          <h1 style={{ margin: 0 }}>Dagster Pipeline Dashboard</h1>
          <p style={{ color: "#666", margin: "5px 0 0" }}>
            Data pipeline orchestration and monitoring
          </p>
        </div>
        <div
          style={{
            padding: "8px 16px",
            borderRadius: "4px",
            backgroundColor:
              loadStatus === "loaded"
                ? "#e8f5e9"
                : loadStatus === "error"
                  ? "#ffebee"
                  : "#fff3e0",
            color:
              loadStatus === "loaded"
                ? "#2e7d32"
                : loadStatus === "error"
                  ? "#c62828"
                  : "#ef6c00",
          }}
        >
          {loadStatus === "loading" && "Loading..."}
          {loadStatus === "loaded" && "Connected"}
          {loadStatus === "error" && "Connection Error"}
        </div>
      </div>

      <div
        style={{
          backgroundColor: "white",
          borderRadius: "8px",
          overflow: "hidden",
          border: "1px solid #e0e0e0",
        }}
      >
        <EmbeddedDashboard
          src="/api/proxy/dagster/"
          title="Dagster Pipeline Dashboard"
          height="700px"
          loadingText="Connecting to Dagster webserver..."
          onLoad={() => setLoadStatus("loaded")}
          onError={() => setLoadStatus("error")}
        />
      </div>

      <div
        style={{
          marginTop: "20px",
          padding: "15px",
          backgroundColor: "#f5f5f5",
          borderRadius: "4px",
          fontSize: "0.9em",
          color: "#666",
        }}
      >
        <strong>Technical Details:</strong>
        <ul style={{ margin: "10px 0 0", paddingLeft: "20px" }}>
          <li>
            Requests are proxied through <code>/api/proxy/dagster/</code>
          </li>
          <li>
            Dagster webserver runs on port 3000 inside the container
          </li>
          <li>
            PostgreSQL stores run history and event logs
          </li>
          <li>
            The daemon handles job scheduling and execution
          </li>
        </ul>
      </div>

      <div
        style={{
          marginTop: "15px",
          padding: "15px",
          backgroundColor: "#e3f2fd",
          borderRadius: "4px",
          fontSize: "0.9em",
        }}
      >
        <strong>Available Assets:</strong>
        <ul style={{ margin: "10px 0 0", paddingLeft: "20px", color: "#1565c0" }}>
          <li>
            <code>sample_data</code> - Generate sample data for demonstration
          </li>
          <li>
            <code>aggregated_stats</code> - Calculate statistics from sample data
          </li>
          <li>
            <code>time_series_analysis</code> - Perform time series analysis
          </li>
        </ul>
      </div>
    </div>
  );
}
