import { createRootRoute, Outlet, Link } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { useSession, signOut } from "@/lib/auth-client";

const queryClient = new QueryClient();

function RootComponent() {
  const { data: session } = useSession();

  return (
    <QueryClientProvider client={queryClient}>
      <div style={{ minHeight: "100vh", backgroundColor: "#f5f5f5" }}>
        {/* Navigation Header */}
        <header
          style={{
            backgroundColor: "white",
            borderBottom: "1px solid #e0e0e0",
            padding: "15px 20px",
          }}
        >
          <nav
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              maxWidth: "1200px",
              margin: "0 auto",
            }}
          >
            <div style={{ display: "flex", gap: "20px", alignItems: "center" }}>
              <Link
                to="/"
                style={{
                  fontSize: "1.2em",
                  fontWeight: "bold",
                  textDecoration: "none",
                  color: "#333",
                }}
              >
                Embedded Dashboards
              </Link>
              {session && (
                <>
                  <Link
                    to="/dashboards"
                    style={{ textDecoration: "none", color: "#666" }}
                    activeProps={{ style: { color: "#0070f3" } }}
                  >
                    Dashboards
                  </Link>
                  <Link
                    to="/marimo"
                    style={{ textDecoration: "none", color: "#666" }}
                    activeProps={{ style: { color: "#0070f3" } }}
                  >
                    Marimo
                  </Link>
                  <Link
                    to="/dagster"
                    style={{ textDecoration: "none", color: "#666" }}
                    activeProps={{ style: { color: "#0070f3" } }}
                  >
                    Dagster
                  </Link>
                </>
              )}
            </div>
            <div>
              {session ? (
                <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                  <span style={{ color: "#666" }}>{session.user.email}</span>
                  <button
                    onClick={() => signOut()}
                    style={{
                      padding: "8px 16px",
                      backgroundColor: "#f0f0f0",
                      border: "1px solid #ddd",
                      borderRadius: "4px",
                      cursor: "pointer",
                    }}
                  >
                    Sign Out
                  </button>
                </div>
              ) : (
                <Link
                  to="/"
                  style={{
                    padding: "8px 16px",
                    backgroundColor: "#0070f3",
                    color: "white",
                    textDecoration: "none",
                    borderRadius: "4px",
                  }}
                >
                  Sign In
                </Link>
              )}
            </div>
          </nav>
        </header>

        {/* Main Content */}
        <main
          style={{
            maxWidth: "1200px",
            margin: "0 auto",
            padding: "20px",
          }}
        >
          <Outlet />
        </main>
      </div>
      <TanStackRouterDevtools />
      <ReactQueryDevtools />
    </QueryClientProvider>
  );
}

export const Route = createRootRoute({
  component: RootComponent,
});
