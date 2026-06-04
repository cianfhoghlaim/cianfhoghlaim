/**
 * Pipeline Streaming Route
 *
 * Proxies SSE streams from FastAPI data pipelines to the frontend.
 * Handles chat streaming, search results, and agent interactions.
 */

import { createFileRoute } from "@tanstack/react-router";
import { auth } from "@cianfhoghlaim-base/auth";

const FASTAPI_URL = process.env.FASTAPI_URL ?? "http://localhost:8000";

/**
 * Build headers with session forwarding
 */
async function buildHeaders(request: Request): Promise<Record<string, string>> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  // Get session from BetterAuth
  const session = await auth.api.getSession({
    headers: request.headers,
  });

  if (session?.user) {
    headers["X-User-ID"] = session.user.id;
    headers["X-User-Email"] = session.user.email;
    if (session.user.name) {
      headers["X-User-Name"] = session.user.name;
    }
  }

  return headers;
}

/**
 * Handle streaming POST requests
 */
async function handleStreamingPost(request: Request): Promise<Response> {
  const url = new URL(request.url);
  const path = url.pathname.replace("/api/pipeline", "");

  // Validate path
  const allowedPaths = ["/agent/chat/stream", "/agent/chat"];
  if (!allowedPaths.some((p) => path.startsWith(p))) {
    return new Response(JSON.stringify({ error: "Invalid path" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  try {
    const body = await request.json();
    const headers = await buildHeaders(request);

    // Forward to FastAPI
    const fastApiUrl = `${FASTAPI_URL}${path}`;
    const response = await fetch(fastApiUrl, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.text();
      return new Response(
        JSON.stringify({ error: `FastAPI error: ${error}` }),
        {
          status: response.status,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    // Check if streaming response
    const contentType = response.headers.get("content-type");
    if (contentType?.includes("text/event-stream")) {
      // Return SSE stream
      return new Response(response.body, {
        status: 200,
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          Connection: "keep-alive",
        },
      });
    }

    // Non-streaming response
    const data = await response.json();
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Pipeline proxy error:", error);
    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : "Unknown error",
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}

/**
 * Handle GET requests (health checks, session info)
 */
async function handleGet(request: Request): Promise<Response> {
  const url = new URL(request.url);
  const path = url.pathname.replace("/api/pipeline", "");

  // Validate path
  const allowedPaths = ["/health", "/agent/health", "/agent/sessions/"];
  if (!allowedPaths.some((p) => path.startsWith(p))) {
    return new Response(JSON.stringify({ error: "Invalid path" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  try {
    const headers = await buildHeaders(request);

    const fastApiUrl = `${FASTAPI_URL}${path}`;
    const response = await fetch(fastApiUrl, {
      method: "GET",
      headers,
    });

    if (!response.ok) {
      const error = await response.text();
      return new Response(
        JSON.stringify({ error: `FastAPI error: ${error}` }),
        {
          status: response.status,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Pipeline proxy error:", error);
    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : "Unknown error",
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}

/**
 * Handle DELETE requests (clear sessions)
 */
async function handleDelete(request: Request): Promise<Response> {
  const url = new URL(request.url);
  const path = url.pathname.replace("/api/pipeline", "");

  // Only allow session deletion
  if (!path.startsWith("/agent/sessions/")) {
    return new Response(JSON.stringify({ error: "Invalid path" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  try {
    const headers = await buildHeaders(request);

    const fastApiUrl = `${FASTAPI_URL}${path}`;
    const response = await fetch(fastApiUrl, {
      method: "DELETE",
      headers,
    });

    if (!response.ok) {
      const error = await response.text();
      return new Response(
        JSON.stringify({ error: `FastAPI error: ${error}` }),
        {
          status: response.status,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    return new Response(JSON.stringify({ success: true }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Pipeline proxy error:", error);
    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : "Unknown error",
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}

export const Route = createFileRoute("/api/pipeline/$")({
  server: {
    handlers: {
      GET: ({ request }) => handleGet(request),
      POST: ({ request }) => handleStreamingPost(request),
      DELETE: ({ request }) => handleDelete(request),
    },
  },
});
