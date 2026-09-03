import { createAPIFileRoute } from "@tanstack/react-start/api";
import { proxyRequest, validateSession, MARIMO_URL } from "@/lib/proxy";

const PROXY_PREFIX = "/api/proxy/marimo";

async function handleProxy({ request }: { request: Request }) {
  // Validate authentication before proxying
  const isAuthenticated = await validateSession();
  if (!isAuthenticated) {
    return new Response(
      JSON.stringify({ error: "Unauthorized", message: "Authentication required" }),
      {
        status: 401,
        headers: { "Content-Type": "application/json" },
      }
    );
  }

  // Proxy the request to the marimo service
  return proxyRequest(request, MARIMO_URL, PROXY_PREFIX);
}

export const APIRoute = createAPIFileRoute("/api/proxy/marimo/$")({
  GET: handleProxy,
  POST: handleProxy,
  PUT: handleProxy,
  PATCH: handleProxy,
  DELETE: handleProxy,
  OPTIONS: ({ request }) => {
    // Handle CORS preflight requests
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": new URL(request.url).origin,
        "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Max-Age": "86400",
      },
    });
  },
});
