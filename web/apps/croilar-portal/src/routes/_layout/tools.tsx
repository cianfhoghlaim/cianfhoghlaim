import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import {
  Play,
  Server,
  Globe,
  Search,
  Database,
  Loader2,
  CheckCircle2,
  XCircle,
  ChevronRight,
} from "lucide-react";

export const Route = createFileRoute("/_layout/tools")({
  component: ToolsPage,
});

interface Tool {
  name: string;
  description: string;
  category: string;
  inputSchema: {
    type: "object";
    properties?: Record<string, unknown>;
    required?: string[];
  };
}

// Tool definitions matching the MCP server
const tools: Tool[] = [
  // Infrastructure
  {
    name: "stack_status",
    description: "Get the health and status of infrastructure stacks from Komodo",
    category: "infrastructure",
    inputSchema: {
      type: "object",
      properties: {
        stack_id: { type: "string", description: "Optional stack ID" },
        category: { type: "string", description: "Filter by category" },
      },
    },
  },
  {
    name: "stack_logs",
    description: "Fetch recent logs from a stack or container",
    category: "infrastructure",
    inputSchema: {
      type: "object",
      properties: {
        stack_id: { type: "string", description: "The stack identifier" },
        lines: { type: "number", description: "Number of log lines" },
      },
      required: ["stack_id"],
    },
  },
  {
    name: "stack_restart",
    description: "Restart a stack or specific container",
    category: "infrastructure",
    inputSchema: {
      type: "object",
      properties: {
        stack_id: { type: "string", description: "The stack identifier" },
      },
      required: ["stack_id"],
    },
  },

  // Browser
  {
    name: "browser_extract",
    description: "Extract content from a web page using browser automation",
    category: "browser",
    inputSchema: {
      type: "object",
      properties: {
        url: { type: "string", description: "The URL to extract from" },
        format: { type: "string", description: "Output format" },
      },
      required: ["url"],
    },
  },
  {
    name: "skyvern_task",
    description: "Create a Skyvern task for vision-based web automation",
    category: "browser",
    inputSchema: {
      type: "object",
      properties: {
        url: { type: "string", description: "Starting URL" },
        goal: { type: "string", description: "Natural language goal" },
      },
      required: ["url", "goal"],
    },
  },
  {
    name: "crawl4ai_extract",
    description: "Fast bulk extraction using Crawl4AI",
    category: "browser",
    inputSchema: {
      type: "object",
      properties: {
        urls: { type: "array", description: "List of URLs to crawl" },
      },
      required: ["urls"],
    },
  },

  // Knowledge
  {
    name: "paperless_search",
    description: "Search documents in Paperless-ngx",
    category: "knowledge",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Search query" },
        limit: { type: "number", description: "Max results" },
      },
      required: ["query"],
    },
  },
  {
    name: "linkwarden_bookmarks",
    description: "Get recent bookmarks from Linkwarden",
    category: "knowledge",
    inputSchema: {
      type: "object",
      properties: {
        collection: { type: "string", description: "Collection filter" },
        limit: { type: "number", description: "Max results" },
      },
    },
  },
  {
    name: "kavita_search",
    description: "Search the Kavita library",
    category: "knowledge",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Search query" },
        type: { type: "string", description: "Content type" },
      },
      required: ["query"],
    },
  },

  // Data Flows
  {
    name: "codeolas_search",
    description: "Semantic code search using Códeolas embeddings",
    category: "dataflows",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Search query" },
        language: { type: "string", description: "Language filter" },
      },
      required: ["query"],
    },
  },
  {
    name: "aleyum_artwork",
    description: "Search artwork using CLIP embeddings",
    category: "dataflows",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Text description" },
        label: { type: "string", description: "Record label filter" },
      },
      required: ["query"],
    },
  },
  {
    name: "dagster_run",
    description: "Trigger a Dagster pipeline run",
    category: "dataflows",
    inputSchema: {
      type: "object",
      properties: {
        job_name: { type: "string", description: "Job name" },
      },
      required: ["job_name"],
    },
  },
];

const categories = {
  all: { label: "All Tools", icon: <Database size={16} /> },
  infrastructure: { label: "Infrastructure", icon: <Server size={16} /> },
  browser: { label: "Browser", icon: <Globe size={16} /> },
  knowledge: { label: "Knowledge", icon: <Search size={16} /> },
  dataflows: { label: "Data Flows", icon: <Database size={16} /> },
};

function ToolsPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null);
  const [args, setArgs] = useState<Record<string, string>>({});
  const [isExecuting, setIsExecuting] = useState(false);
  const [result, setResult] = useState<unknown | null>(null);
  const [error, setError] = useState<string | null>(null);

  const filteredTools =
    selectedCategory === "all"
      ? tools
      : tools.filter((t) => t.category === selectedCategory);

  const executeTool = async () => {
    if (!selectedTool) return;

    setIsExecuting(true);
    setResult(null);
    setError(null);

    try {
      const response = await fetch("/api/mcp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          jsonrpc: "2.0",
          id: Date.now(),
          method: "tools/call",
          params: {
            name: selectedTool.name,
            arguments: args,
          },
        }),
      });

      const data = await response.json();

      if (data.error) {
        setError(data.error.message);
      } else {
        setResult(data.result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Execution failed");
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="flex h-full">
      {/* Tool List */}
      <div className="w-80 border-r flex flex-col">
        <div className="p-4 border-b">
          <h1 className="text-xl font-bold">MCP Tools</h1>
          <p className="text-sm text-muted-foreground">
            Execute tools via MCP protocol
          </p>
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap gap-1 p-2 border-b">
          {Object.entries(categories).map(([key, { label, icon }]) => (
            <button
              key={key}
              onClick={() => setSelectedCategory(key)}
              className={`flex items-center gap-1 px-2 py-1 text-xs rounded ${
                selectedCategory === key
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary hover:bg-secondary/80"
              }`}
            >
              {icon}
              {label}
            </button>
          ))}
        </div>

        {/* Tool List */}
        <div className="flex-1 overflow-auto">
          {filteredTools.map((tool) => (
            <button
              key={tool.name}
              onClick={() => {
                setSelectedTool(tool);
                setArgs({});
                setResult(null);
                setError(null);
              }}
              className={`w-full text-left p-3 border-b hover:bg-secondary/50 ${
                selectedTool?.name === tool.name ? "bg-secondary" : ""
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-sm">{tool.name}</span>
                <ChevronRight size={16} className="text-muted-foreground" />
              </div>
              <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                {tool.description}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Tool Detail & Execution */}
      <div className="flex-1 flex flex-col">
        {selectedTool ? (
          <>
            {/* Header */}
            <div className="p-4 border-b">
              <h2 className="text-lg font-semibold font-mono">
                {selectedTool.name}
              </h2>
              <p className="text-muted-foreground">{selectedTool.description}</p>
            </div>

            {/* Arguments */}
            <div className="p-4 border-b space-y-4">
              <h3 className="font-medium">Arguments</h3>
              {selectedTool.inputSchema.properties &&
                Object.entries(selectedTool.inputSchema.properties).map(
                  ([key, schema]) => {
                    const prop = schema as { type: string; description?: string };
                    const isRequired =
                      selectedTool.inputSchema.required?.includes(key);
                    return (
                      <div key={key}>
                        <label className="text-sm font-medium">
                          {key}
                          {isRequired && (
                            <span className="text-red-500 ml-1">*</span>
                          )}
                        </label>
                        <input
                          type={prop.type === "number" ? "number" : "text"}
                          value={args[key] || ""}
                          onChange={(e) =>
                            setArgs({ ...args, [key]: e.target.value })
                          }
                          placeholder={prop.description}
                          className="w-full mt-1 px-3 py-2 bg-secondary rounded focus:outline-none focus:ring-2 focus:ring-primary"
                        />
                        {prop.description && (
                          <p className="text-xs text-muted-foreground mt-1">
                            {prop.description}
                          </p>
                        )}
                      </div>
                    );
                  }
                )}

              <button
                onClick={executeTool}
                disabled={isExecuting}
                className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded hover:bg-primary/90 disabled:opacity-50"
              >
                {isExecuting ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  <Play size={16} />
                )}
                Execute
              </button>
            </div>

            {/* Result */}
            <div className="flex-1 overflow-auto p-4">
              <h3 className="font-medium mb-2">Result</h3>
              {error && (
                <div className="flex items-center gap-2 text-red-500 bg-red-500/10 p-3 rounded">
                  <XCircle size={16} />
                  {error}
                </div>
              )}
              {result ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-green-500">
                    <CheckCircle2 size={16} />
                    Success
                  </div>
                  <pre className="bg-secondary p-3 rounded text-sm overflow-auto max-h-96">
                    {JSON.stringify(result, null, 2)}
                  </pre>
                </div>
              ) : null}
              {!error && !result && (
                <p className="text-muted-foreground">
                  Execute the tool to see results
                </p>
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <Database size={48} className="mx-auto mb-4 opacity-50" />
              <p>Select a tool from the list</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
