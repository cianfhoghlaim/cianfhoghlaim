import { createFileRoute } from "@tanstack/react-router";

/**
 * Browser API - Browser automation task management.
 *
 * Provides access to the browser automation backends:
 * - Self-hosted: Stagehand, Crawl4AI, CDP
 * - Paid: Browserbase, Firecrawl, Skyvern
 *
 * Supports multiple agent types:
 * - Hunter: Content discovery and exploration
 * - Gatherer: Data extraction and collection
 * - Operator: Form interaction and automation
 * - Evaluator: Quality assessment
 *
 * Tasks can be executed with durable execution via Restate for
 * crash-resistant, checkpointed workflows.
 */

// Browser agent backend URL
const BROWSER_AGENT_URL = process.env.BROWSER_AGENT_URL || "http://browser-agent:8002";

type BrowserBackend = "stagehand" | "crawl4ai" | "cdp" | "browserbase" | "firecrawl" | "skyvern";
type AgentType = "hunter" | "gatherer" | "operator" | "evaluator" | "auto";

interface BrowserTaskRequest {
  url: string;
  task_type: AgentType;
  instructions?: string;
  backend?: BrowserBackend;
  options?: {
    screenshot?: boolean;
    timeout?: number;
    selector?: string;
    extract_format?: "text" | "html" | "markdown" | "json";
    durable?: boolean; // Use Restate durable execution
  };
}

interface BrowserTaskStatus {
  task_id: string;
  status: "pending" | "running" | "completed" | "failed";
  progress?: number;
  result?: unknown;
  error?: string;
}

export const Route = createFileRoute("/api/browser")({
  server: {
    handlers: {
      // POST: Create and execute browser tasks
      POST: async ({ request }) => {
        try {
          const body = (await request.json()) as BrowserTaskRequest;

          // Validate required fields
          if (!body.url) {
            return Response.json(
              { error: "URL is required" },
              { status: 400 }
            );
          }

          // Default task type
          const taskType = body.task_type || "auto";

          // Select backend based on task type if not specified
          const backend = body.backend || selectBackend(taskType, body.options);

          // Build browser agent request
          const agentRequest = {
            url: body.url,
            agent_type: taskType,
            backend,
            instructions: body.instructions,
            options: {
              screenshot: body.options?.screenshot ?? false,
              timeout: body.options?.timeout ?? 30000,
              selector: body.options?.selector,
              extract_format: body.options?.extract_format ?? "markdown",
            },
            durable: body.options?.durable ?? false,
          };

          // Execute task via browser agent
          const response = await fetch(`${BROWSER_AGENT_URL}/execute`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(agentRequest),
          });

          if (!response.ok) {
            const errorText = await response.text();
            return Response.json(
              {
                error: `Browser agent error: ${response.status}`,
                details: errorText,
              },
              { status: response.status }
            );
          }

          const result = await response.json();
          return Response.json({
            success: true,
            task_id: result.task_id,
            backend,
            agent_type: taskType,
            result: result.data,
            screenshot_url: result.screenshot_url,
          });
        } catch (error) {
          return Response.json(
            {
              error: `Internal error: ${error instanceof Error ? error.message : String(error)}`,
            },
            { status: 500 }
          );
        }
      },

      // GET: Get task status or list active sessions
      GET: async ({ request }) => {
        const url = new URL(request.url);
        const taskId = url.searchParams.get("task_id");

        // If task_id provided, get specific task status
        if (taskId) {
          try {
            const response = await fetch(`${BROWSER_AGENT_URL}/status/${taskId}`);
            if (!response.ok) {
              return Response.json(
                { error: "Task not found", task_id: taskId },
                { status: 404 }
              );
            }
            const status = await response.json();
            return Response.json(status);
          } catch (error) {
            return Response.json(
              { error: String(error) },
              { status: 500 }
            );
          }
        }

        // Otherwise, return API documentation and active sessions
        try {
          const sessionsResponse = await fetch(`${BROWSER_AGENT_URL}/sessions`);
          const sessions = sessionsResponse.ok
            ? await sessionsResponse.json()
            : { active: 0, sessions: [] };

          return Response.json({
            status: "ok",
            endpoints: {
              "POST /api/browser": "Create browser task",
              "GET /api/browser?task_id=<id>": "Get task status",
            },
            backends: {
              selfhosted: ["stagehand", "crawl4ai", "cdp"],
              paid: ["browserbase", "firecrawl", "skyvern"],
            },
            agent_types: ["hunter", "gatherer", "operator", "evaluator", "auto"],
            active_sessions: sessions.active || 0,
          });
        } catch {
          return Response.json({
            status: "ok",
            endpoints: {
              "POST /api/browser": "Create browser task",
              "GET /api/browser?task_id=<id>": "Get task status",
            },
            backends: {
              selfhosted: ["stagehand", "crawl4ai", "cdp"],
              paid: ["browserbase", "firecrawl", "skyvern"],
            },
            agent_types: ["hunter", "gatherer", "operator", "evaluator", "auto"],
            browser_agent_url: BROWSER_AGENT_URL,
            note: "Browser agent not reachable for session info",
          });
        }
      },

      // DELETE: Cancel a running task
      DELETE: async ({ request }) => {
        const url = new URL(request.url);
        const taskId = url.searchParams.get("task_id");

        if (!taskId) {
          return Response.json(
            { error: "task_id query parameter required" },
            { status: 400 }
          );
        }

        try {
          const response = await fetch(`${BROWSER_AGENT_URL}/cancel/${taskId}`, {
            method: "POST",
          });

          if (!response.ok) {
            return Response.json(
              { error: "Failed to cancel task", task_id: taskId },
              { status: response.status }
            );
          }

          return Response.json({
            success: true,
            task_id: taskId,
            message: "Task cancelled",
          });
        } catch (error) {
          return Response.json(
            { error: String(error) },
            { status: 500 }
          );
        }
      },
    },
  },
});

/**
 * Select the best backend based on task type and options.
 */
function selectBackend(taskType: AgentType, options?: BrowserTaskRequest["options"]): BrowserBackend {
  // If durable execution needed, prefer Stagehand (supports checkpoints)
  if (options?.durable) {
    return "stagehand";
  }

  // Select based on task type
  switch (taskType) {
    case "hunter":
      // Hunter needs exploration - Crawl4AI is good for discovery
      return "crawl4ai";
    case "gatherer":
      // Gatherer needs extraction - Firecrawl excels at this
      return "firecrawl";
    case "operator":
      // Operator needs interaction - Stagehand is best for forms
      return "stagehand";
    case "evaluator":
      // Evaluator needs screenshots - CDP provides raw access
      return "cdp";
    case "auto":
    default:
      // Default to Stagehand as most versatile
      return "stagehand";
  }
}
