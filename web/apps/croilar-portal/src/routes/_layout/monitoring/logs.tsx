import { createFileRoute } from "@tanstack/react-router";
import { RefreshCw, Search } from "lucide-react";
import { useState } from "react";

export const Route = createFileRoute("/_layout/monitoring/logs")({
  component: LogsPage,
});

// Mock log data
const mockLogs = [
  { id: 1, timestamp: "2025-01-20 12:45:32", level: "info", container: "langfuse-web", message: "Request processed: POST /api/v1/traces" },
  { id: 2, timestamp: "2025-01-20 12:45:31", level: "info", container: "langfuse-web", message: "Request processed: GET /api/v1/sessions" },
  { id: 3, timestamp: "2025-01-20 12:45:30", level: "warn", container: "memgraph", message: "High memory usage detected: 4.8GB / 6GB" },
  { id: 4, timestamp: "2025-01-20 12:45:28", level: "info", container: "tuath-api", message: "Agent chat session started for user 0x1234..." },
  { id: 5, timestamp: "2025-01-20 12:45:25", level: "info", container: "crypteolas-api", message: "DeFi metrics refreshed for 450 protocols" },
  { id: 6, timestamp: "2025-01-20 12:45:20", level: "error", container: "dagster", message: "Pipeline 'defi_protocols' failed: Rate limit exceeded" },
  { id: 7, timestamp: "2025-01-20 12:45:18", level: "info", container: "falkordb", message: "Query executed in 45ms: MATCH (n:Character)..." },
  { id: 8, timestamp: "2025-01-20 12:45:15", level: "info", container: "mlflow", message: "Experiment 'embedding-finetune' created" },
  { id: 9, timestamp: "2025-01-20 12:45:10", level: "info", container: "beszel", message: "Metrics collected from 12 hosts" },
  { id: 10, timestamp: "2025-01-20 12:45:05", level: "info", container: "lancedb", message: "Index rebuild completed for table 'curriculum'" },
  { id: 11, timestamp: "2025-01-20 12:45:00", level: "warn", container: "redis", message: "Connection pool exhausted, waiting for available connection" },
  { id: 12, timestamp: "2025-01-20 12:44:55", level: "info", container: "dozzle", message: "Log stream connected for container langfuse-web" },
];

const containers = ["all", "langfuse-web", "memgraph", "tuath-api", "crypteolas-api", "dagster", "falkordb", "mlflow", "beszel", "lancedb", "redis", "dozzle"];

function LogsPage() {
  const [selectedContainer, setSelectedContainer] = useState("all");
  const [levelFilter, setLevelFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [autoRefresh, setAutoRefresh] = useState(true);

  const filteredLogs = mockLogs.filter((log) => {
    if (selectedContainer !== "all" && log.container !== selectedContainer) return false;
    if (levelFilter !== "all" && log.level !== levelFilter) return false;
    if (searchQuery && !log.message.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b p-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold">Container Logs</h1>
            <p className="text-muted-foreground">Real-time log streaming from all containers</p>
          </div>
          <div className="flex items-center gap-2">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded border-border"
              />
              Auto-refresh
            </label>
            <button className="flex items-center gap-2 bg-secondary px-3 py-1.5 rounded hover:bg-secondary/80">
              <RefreshCw size={14} />
              Refresh
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
              <input
                type="text"
                placeholder="Search logs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-secondary pl-10 pr-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>
          <select
            value={selectedContainer}
            onChange={(e) => setSelectedContainer(e.target.value)}
            className="bg-secondary px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          >
            {containers.map((c) => (
              <option key={c} value={c}>
                {c === "all" ? "All Containers" : c}
              </option>
            ))}
          </select>
          <select
            value={levelFilter}
            onChange={(e) => setLevelFilter(e.target.value)}
            className="bg-secondary px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="all">All Levels</option>
            <option value="info">Info</option>
            <option value="warn">Warning</option>
            <option value="error">Error</option>
          </select>
        </div>
      </div>

      {/* Log Viewer */}
      <div className="flex-1 overflow-auto bg-background p-2 font-mono text-sm">
        {filteredLogs.map((log) => (
          <div
            key={log.id}
            className={`log-line ${log.level === "error" ? "error" : log.level === "warn" ? "warn" : ""}`}
          >
            <span className="text-muted-foreground">{log.timestamp}</span>
            <span className={`mx-2 px-1.5 py-0.5 rounded text-xs ${
              log.level === "error"
                ? "bg-destructive/20 text-destructive"
                : log.level === "warn"
                ? "bg-status-warning/20 text-status-warning"
                : "bg-muted text-muted-foreground"
            }`}>
              {log.level.toUpperCase()}
            </span>
            <span className="text-primary">[{log.container}]</span>
            <span className="ml-2">{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
