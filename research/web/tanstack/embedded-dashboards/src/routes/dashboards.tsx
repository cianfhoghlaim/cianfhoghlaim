import { createFileRoute, redirect, Link } from "@tanstack/react-router";
import { getSession } from "@/lib/auth-server";
import { useQuery } from "@tanstack/react-query";
import { orpc } from "@/orpc/client";

export const Route = createFileRoute("/dashboards")({
  beforeLoad: async () => {
    const session = await getSession();
    if (!session) {
      throw redirect({ to: "/" });
    }
    return { session };
  },
  component: DashboardsPage,
});

function DashboardsPage() {
  const { data: dashboards, isLoading } = useQuery({
    ...orpc.listDashboards.queryOptions(),
  });

  if (isLoading) {
    return (
      <div style={{ textAlign: "center", padding: "40px" }}>
        <p>Loading dashboards...</p>
      </div>
    );
  }

  return (
    <div>
      <h1>Available Dashboards</h1>
      <p style={{ color: "#666", marginBottom: "30px" }}>
        Select a dashboard to view. All dashboards are embedded via authenticated proxies.
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
          gap: "20px",
        }}
      >
        {dashboards?.map((dashboard) => (
          <Link
            key={dashboard.id}
            to={dashboard.type === "marimo" ? "/marimo" : "/dagster"}
            style={{ textDecoration: "none" }}
          >
            <div
              style={{
                padding: "20px",
                backgroundColor: "white",
                borderRadius: "8px",
                border: "1px solid #e0e0e0",
                cursor: "pointer",
                transition: "box-shadow 0.2s",
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.1)";
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.boxShadow = "none";
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "10px",
                }}
              >
                <h3 style={{ margin: 0, color: "#333" }}>{dashboard.name}</h3>
                <span
                  style={{
                    padding: "4px 8px",
                    backgroundColor:
                      dashboard.type === "marimo" ? "#e8f5e9" : "#e3f2fd",
                    color: dashboard.type === "marimo" ? "#2e7d32" : "#1565c0",
                    borderRadius: "4px",
                    fontSize: "0.8em",
                  }}
                >
                  {dashboard.type}
                </span>
              </div>
              <p style={{ margin: 0, color: "#666", fontSize: "0.9em" }}>
                {dashboard.type === "marimo"
                  ? "Interactive Python notebooks for data analysis"
                  : "Data pipeline orchestration and monitoring"}
              </p>
            </div>
          </Link>
        ))}
      </div>

      <div
        style={{
          marginTop: "40px",
          padding: "20px",
          backgroundColor: "#f8f9fa",
          borderRadius: "8px",
          border: "1px solid #e0e0e0",
        }}
      >
        <h3>How it works</h3>
        <ol style={{ lineHeight: "1.8", color: "#555" }}>
          <li>Your session is validated on each dashboard request</li>
          <li>Requests are proxied through <code>/api/proxy/[service]</code></li>
          <li>Security headers are modified to allow iframe embedding</li>
          <li>The dashboard UI is rendered inside your application</li>
        </ol>
      </div>
    </div>
  );
}
