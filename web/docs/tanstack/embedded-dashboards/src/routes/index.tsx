import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useSession } from "@/lib/auth-client";
import { AuthForm } from "@/components/AuthForm";
import { useEffect } from "react";

export const Route = createFileRoute("/")({
  component: IndexPage,
});

function IndexPage() {
  const { data: session, isPending } = useSession();
  const navigate = useNavigate();

  useEffect(() => {
    if (session) {
      navigate({ to: "/dashboards" });
    }
  }, [session, navigate]);

  if (isPending) {
    return (
      <div style={{ textAlign: "center", padding: "40px" }}>
        <p>Loading...</p>
      </div>
    );
  }

  if (session) {
    return (
      <div style={{ textAlign: "center", padding: "40px" }}>
        <p>Redirecting to dashboards...</p>
      </div>
    );
  }

  return (
    <div>
      <div style={{ textAlign: "center", marginBottom: "40px" }}>
        <h1>Embedded Dashboards Demo</h1>
        <p style={{ color: "#666", maxWidth: "600px", margin: "0 auto" }}>
          This example demonstrates embedding marimo notebooks and Dagster pipelines
          in a TanStack Start application with BetterAuth authentication and oRPC APIs.
        </p>
      </div>

      <AuthForm onSuccess={() => navigate({ to: "/dashboards" })} />

      <div
        style={{
          marginTop: "40px",
          padding: "20px",
          backgroundColor: "white",
          borderRadius: "8px",
          border: "1px solid #e0e0e0",
        }}
      >
        <h3>Architecture Overview</h3>
        <ul style={{ lineHeight: "1.8", color: "#555" }}>
          <li>
            <strong>TanStack Start</strong> - Full-stack React framework with SSR
          </li>
          <li>
            <strong>BetterAuth</strong> - Authentication layer protecting dashboard access
          </li>
          <li>
            <strong>oRPC</strong> - Type-safe RPC for dashboard management
          </li>
          <li>
            <strong>Hono-style Proxy</strong> - Routes requests to marimo/dagster services
          </li>
          <li>
            <strong>Iframe Embedding</strong> - Secure embedding with proper CSP headers
          </li>
        </ul>
      </div>
    </div>
  );
}
