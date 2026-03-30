import { createFileRoute, redirect } from "@tanstack/react-router";
import { getSession } from "@/lib/auth-server";
import { EmbeddedDashboard } from "@/components/EmbeddedDashboard";
import { useState } from "react";

export const Route = createFileRoute("/marimo")({
  beforeLoad: async () => {
    const session = await getSession();
    if (!session) {
      throw redirect({ to: "/" });
    }
    return { session };
  },
  component: MarimoPage,
});

function MarimoPage() {
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
          <h1 style={{ margin: 0 }}>Marimo Analytics Dashboard</h1>
          <p style={{ color: "#666", margin: "5px 0 0" }}>
            Interactive Python notebook for data analysis
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
          src="/api/proxy/marimo/"
          title="Marimo Analytics Notebook"
          height="700px"
          loadingText="Connecting to marimo notebook server..."
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
            Requests are proxied through <code>/api/proxy/marimo/</code>
          </li>
          <li>
            Session validation occurs on every request
          </li>
          <li>
            The notebook runs with <code>--no-token</code> as authentication is
            handled by the proxy
          </li>
          <li>
            WebSocket connections are supported for real-time interactivity
          </li>
        </ul>
      </div>
    </div>
  );
}
