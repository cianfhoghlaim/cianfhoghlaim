import { createFileRoute } from "@tanstack/react-router";
import { auth } from "@/lib/auth";

// MCP Protocol Types
interface MCPRequest {
  jsonrpc: "2.0";
  id?: string | number;
  method: string;
  params?: Record<string, unknown>;
}

interface MCPResponse {
  jsonrpc: "2.0";
  id?: string | number;
  result?: unknown;
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
}

interface Tool {
  name: string;
  description: string;
  inputSchema: {
    type: "object";
    properties?: Record<string, unknown>;
    required?: string[];
  };
}

// Tool definitions organized by category
const tools: Tool[] = [
  // Infrastructure Tools
  {
    name: "stack_status",
    description: "Get the health and status of infrastructure stacks from Komodo",
    inputSchema: {
      type: "object",
      properties: {
        stack_id: {
          type: "string",
          description: "Optional stack ID. If not provided, returns all stacks.",
        },
        category: {
          type: "string",
          enum: ["database", "ml", "observability", "monitoring", "tools"],
          description: "Filter stacks by category",
        },
      },
      required: [],
    },
  },
  {
    name: "stack_logs",
    description: "Fetch recent logs from a stack or container",
    inputSchema: {
      type: "object",
      properties: {
        stack_id: { type: "string", description: "The stack identifier" },
        container: { type: "string", description: "Optional specific container name" },
        lines: { type: "number", description: "Number of log lines to fetch (default: 100)" },
      },
      required: ["stack_id"],
    },
  },
  {
    name: "stack_restart",
    description: "Restart a stack or specific container",
    inputSchema: {
      type: "object",
      properties: {
        stack_id: { type: "string", description: "The stack identifier" },
        container: { type: "string", description: "Optional specific container to restart" },
      },
      required: ["stack_id"],
    },
  },

  // Browser/Extraction Tools
  {
    name: "browser_extract",
    description: "Extract content from a web page using browser automation",
    inputSchema: {
      type: "object",
      properties: {
        url: { type: "string", description: "The URL to extract content from" },
        selector: { type: "string", description: "Optional CSS selector to target" },
        format: {
          type: "string",
          enum: ["text", "html", "markdown", "json"],
          description: "Output format (default: markdown)",
        },
      },
      required: ["url"],
    },
  },
  {
    name: "skyvern_task",
    description: "Create a Skyvern task for vision-based web automation",
    inputSchema: {
      type: "object",
      properties: {
        url: { type: "string", description: "Starting URL" },
        goal: { type: "string", description: "Natural language description of the task" },
      },
      required: ["url", "goal"],
    },
  },
  {
    name: "crawl4ai_extract",
    description: "Fast bulk extraction using Crawl4AI with LLM-powered cleaning",
    inputSchema: {
      type: "object",
      properties: {
        urls: {
          type: "array",
          items: { type: "string" },
          description: "List of URLs to crawl",
        },
        extraction_strategy: {
          type: "string",
          enum: ["llm", "css", "xpath"],
          description: "Extraction strategy to use",
        },
      },
      required: ["urls"],
    },
  },

  // Knowledge/Search Tools
  {
    name: "paperless_search",
    description: "Search documents in Paperless-ngx",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Search query" },
        tags: {
          type: "array",
          items: { type: "string" },
          description: "Filter by tags",
        },
        limit: { type: "number", description: "Max results (default: 10)" },
      },
      required: ["query"],
    },
  },
  {
    name: "linkwarden_bookmarks",
    description: "Get recent bookmarks from Linkwarden",
    inputSchema: {
      type: "object",
      properties: {
        collection: { type: "string", description: "Optional collection to filter by" },
        tags: {
          type: "array",
          items: { type: "string" },
          description: "Filter by tags",
        },
        limit: { type: "number", description: "Max results (default: 20)" },
      },
      required: [],
    },
  },
  {
    name: "kavita_search",
    description: "Search the Kavita library for books and comics",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Search query" },
        type: {
          type: "string",
          enum: ["book", "comic", "manga"],
          description: "Content type filter",
        },
      },
      required: ["query"],
    },
  },

  // Data Flow Tools
  {
    name: "codeolas_search",
    description: "Semantic code search using Códeolas embeddings",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Natural language search query" },
        language: {
          type: "string",
          description: "Filter by programming language",
        },
        limit: { type: "number", description: "Max results (default: 10)" },
      },
      required: ["query"],
    },
  },
  {
    name: "aleyum_artwork",
    description: "Search artwork using CLIP embeddings",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Text description or style to search for" },
        label: { type: "string", description: "Filter by record label" },
        limit: { type: "number", description: "Max results (default: 10)" },
      },
      required: ["query"],
    },
  },
  {
    name: "dagster_run",
    description: "Trigger a Dagster pipeline run",
    inputSchema: {
      type: "object",
      properties: {
        job_name: {
          type: "string",
          description: "Name of the job to run",
        },
        config: {
          type: "object",
          description: "Optional run configuration",
        },
      },
      required: ["job_name"],
    },
  },
];

// Tool execution handlers
async function executeStackStatus(params: Record<string, unknown>): Promise<unknown> {
  // Would call Komodo API
  const mockStacks = [
    { id: "langfuse", name: "Langfuse", status: "healthy", cpu: "12%", memory: "1.2GB" },
    { id: "mlflow", name: "MLflow", status: "healthy", cpu: "8%", memory: "0.8GB" },
    { id: "memgraph", name: "Memgraph", status: "warning", cpu: "45%", memory: "4.8GB" },
  ];

  if (params.stack_id) {
    const stack = mockStacks.find((s) => s.id === params.stack_id);
    return stack || { error: "Stack not found" };
  }

  if (params.category) {
    // Filter by category
    return mockStacks;
  }

  return mockStacks;
}

async function executeBrowserExtract(params: Record<string, unknown>): Promise<unknown> {
  // Would call browser agent
  return {
    url: params.url,
    format: params.format || "markdown",
    content: `# Extracted Content\n\nContent from ${params.url} would appear here.`,
    extracted_at: new Date().toISOString(),
  };
}

async function executePaperlessSearch(params: Record<string, unknown>): Promise<unknown> {
  // Would call Paperless API
  return {
    query: params.query,
    results: [
      { id: 1, title: "Example Document", correspondent: "Example Corp", tags: ["invoice"] },
      { id: 2, title: "Another Document", correspondent: "Test Inc", tags: ["receipt"] },
    ],
    total: 2,
  };
}

async function executeCodeolasSearch(params: Record<string, unknown>): Promise<unknown> {
  // Would call LanceDB
  return {
    query: params.query,
    results: [
      {
        file_path: "src/routes/api/mcp.ts",
        language: "typescript",
        chunk_type: "function",
        name: "executeTool",
        relevance: 0.92,
      },
    ],
    total: 1,
  };
}

// Generic tool execution dispatcher
async function executeTool(
  name: string,
  args: Record<string, unknown>
): Promise<unknown> {
  switch (name) {
    case "stack_status":
      return executeStackStatus(args);
    case "stack_logs":
      return { logs: `Logs for ${args.stack_id}...`, lines: args.lines || 100 };
    case "stack_restart":
      return { success: true, stack_id: args.stack_id, restarted_at: new Date().toISOString() };
    case "browser_extract":
      return executeBrowserExtract(args);
    case "skyvern_task":
      return { task_id: `task_${Date.now()}`, status: "created", url: args.url, goal: args.goal };
    case "crawl4ai_extract":
      return { urls: args.urls, results: [], status: "processing" };
    case "paperless_search":
      return executePaperlessSearch(args);
    case "linkwarden_bookmarks":
      return { bookmarks: [], total: 0 };
    case "kavita_search":
      return { results: [], total: 0 };
    case "codeolas_search":
      return executeCodeolasSearch(args);
    case "aleyum_artwork":
      return { results: [], total: 0 };
    case "dagster_run":
      return { run_id: `run_${Date.now()}`, job_name: args.job_name, status: "started" };
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

// MCP Request Handlers
function handleInitialize(): MCPResponse {
  return {
    jsonrpc: "2.0",
    result: {
      protocolVersion: "2024-11-05",
      capabilities: {
        tools: { listChanged: false },
      },
      serverInfo: {
        name: "aleyum-portal-mcp",
        version: "1.0.0",
      },
    },
  };
}

function handleListTools(): MCPResponse {
  return {
    jsonrpc: "2.0",
    result: { tools },
  };
}

async function handleCallTool(
  params: Record<string, unknown>,
  headers: Headers
): Promise<MCPResponse> {
  const { name, arguments: args = {} } = params as {
    name: string;
    arguments?: Record<string, unknown>;
  };

  // Check if tool requires authentication
  const authRequiredTools = ["stack_restart", "dagster_run", "skyvern_task"];
  if (authRequiredTools.includes(name)) {
    const session = await auth.api.getSession({ headers });
    if (!session) {
      return {
        jsonrpc: "2.0",
        error: {
          code: 401,
          message: "Authentication required for this tool",
        },
      };
    }
  }

  try {
    const result = await executeTool(name, args);
    return {
      jsonrpc: "2.0",
      result: {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      },
    };
  } catch (err) {
    return {
      jsonrpc: "2.0",
      error: {
        code: -32603,
        message: err instanceof Error ? err.message : "Tool execution failed",
      },
    };
  }
}

export const Route = createFileRoute("/admin/api/mcp")({
  server: {
    handlers: {
      GET: () => {
        return Response.json({
          name: "Aleyum Portal MCP Server",
          version: "1.0.0",
          description: "MCP server for infrastructure and data tools",
          capabilities: ["tools"],
          tools: tools.map((t) => ({ name: t.name, description: t.description })),
        });
      },

      POST: async ({ request }) => {
        try {
          const body: MCPRequest = await request.json();

          if (body.jsonrpc !== "2.0") {
            return Response.json({
              jsonrpc: "2.0",
              id: body.id,
              error: {
                code: -32600,
                message: "Invalid Request - jsonrpc must be '2.0'",
              },
            });
          }

          let response: MCPResponse;

          switch (body.method) {
            case "initialize":
              response = handleInitialize();
              break;
            case "tools/list":
              response = handleListTools();
              break;
            case "tools/call":
              response = await handleCallTool(
                body.params || {},
                request.headers
              );
              break;
            default:
              response = {
                jsonrpc: "2.0",
                error: {
                  code: -32601,
                  message: "Method not found",
                  data: {
                    availableMethods: ["initialize", "tools/list", "tools/call"],
                  },
                },
              };
          }

          if (body.id !== undefined) {
            response.id = body.id;
          }

          return Response.json(response);
        } catch (err) {
          return Response.json({
            jsonrpc: "2.0",
            error: {
              code: -32700,
              message: "Parse error",
              data: {
                error: err instanceof Error ? err.message : "Invalid JSON",
              },
            },
          });
        }
      },
    },
  },
});
