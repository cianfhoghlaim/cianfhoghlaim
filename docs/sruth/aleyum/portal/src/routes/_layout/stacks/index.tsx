import { createFileRoute } from "@tanstack/react-router";
import {
  Activity,
  Clock,
  ExternalLink,
  MoreVertical,
  Play,
  RefreshCw,
  Server,
  Square,
} from "lucide-react";

export const Route = createFileRoute("/_layout/stacks/")({
  component: StacksPage,
});

// Mock data for stacks - would come from bonneagar/storage blueprints
const stacks = [
  {
    id: "langfuse",
    name: "Langfuse",
    category: "observability",
    status: "healthy" as const,
    url: "https://langfuse.example.com",
    uptime: "99.9%",
    cpu: "12%",
    memory: "1.2GB",
    containers: 3,
  },
  {
    id: "mlflow",
    name: "MLflow",
    category: "ml",
    status: "healthy" as const,
    url: "https://mlflow.example.com",
    uptime: "99.8%",
    cpu: "8%",
    memory: "0.8GB",
    containers: 2,
  },
  {
    id: "falkordb",
    name: "FalkorDB",
    category: "database",
    status: "healthy" as const,
    url: null,
    uptime: "100%",
    cpu: "15%",
    memory: "2.4GB",
    containers: 1,
  },
  {
    id: "lancedb",
    name: "LanceDB",
    category: "database",
    status: "healthy" as const,
    url: null,
    uptime: "100%",
    cpu: "5%",
    memory: "0.5GB",
    containers: 1,
  },
  {
    id: "memgraph",
    name: "Memgraph",
    category: "database",
    status: "warning" as const,
    url: "https://memgraph.example.com",
    uptime: "98.5%",
    cpu: "45%",
    memory: "4.8GB",
    containers: 2,
  },
  {
    id: "dozzle",
    name: "Dozzle",
    category: "tools",
    status: "healthy" as const,
    url: "https://dozzle.example.com",
    uptime: "99.9%",
    cpu: "2%",
    memory: "0.1GB",
    containers: 1,
  },
  {
    id: "beszel",
    name: "Beszel",
    category: "monitoring",
    status: "healthy" as const,
    url: "https://beszel.example.com",
    uptime: "99.9%",
    cpu: "5%",
    memory: "0.3GB",
    containers: 2,
  },
  {
    id: "perplexica",
    name: "Perplexica",
    category: "tools",
    status: "healthy" as const,
    url: "https://perplexica.example.com",
    uptime: "99.5%",
    cpu: "20%",
    memory: "1.5GB",
    containers: 3,
  },
  {
    id: "cognee",
    name: "Cognee",
    category: "ml",
    status: "healthy" as const,
    url: null,
    uptime: "99.7%",
    cpu: "18%",
    memory: "2.1GB",
    containers: 2,
  },
  {
    id: "chartdb",
    name: "ChartDB",
    category: "tools",
    status: "healthy" as const,
    url: "https://chartdb.example.com",
    uptime: "99.9%",
    cpu: "3%",
    memory: "0.2GB",
    containers: 1,
  },
];

const categories = ["all", "database", "ml", "observability", "monitoring", "tools"];

function StacksPage() {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Infrastructure Stacks</h1>
          <p className="text-muted-foreground">Manage bonneagar deployment stacks</p>
        </div>
        <button className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90">
          <RefreshCw size={16} />
          Refresh All
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6">
        {categories.map((cat) => (
          <button
            key={cat}
            className="px-3 py-1.5 text-sm rounded-md bg-secondary hover:bg-secondary/80 capitalize"
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Stack Grid */}
      <div className="grid grid-cols-3 gap-4">
        {stacks.map((stack) => (
          <StackCard key={stack.id} stack={stack} />
        ))}
      </div>
    </div>
  );
}

function StackCard({
  stack,
}: {
  stack: (typeof stacks)[0];
}) {
  return (
    <div className="bg-card rounded-lg border p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-secondary rounded-lg flex items-center justify-center">
            <Server size={20} />
          </div>
          <div>
            <h3 className="font-medium">{stack.name}</h3>
            <span className="text-xs text-muted-foreground capitalize">{stack.category}</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className={`status-dot ${stack.status}`} />
          <button className="p-1 hover:bg-secondary rounded">
            <MoreVertical size={16} />
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-2 mb-4 text-sm">
        <div className="bg-secondary/50 rounded px-2 py-1">
          <div className="text-muted-foreground text-xs">CPU</div>
          <div>{stack.cpu}</div>
        </div>
        <div className="bg-secondary/50 rounded px-2 py-1">
          <div className="text-muted-foreground text-xs">Memory</div>
          <div>{stack.memory}</div>
        </div>
        <div className="bg-secondary/50 rounded px-2 py-1">
          <div className="text-muted-foreground text-xs">Containers</div>
          <div>{stack.containers}</div>
        </div>
      </div>

      {/* Uptime */}
      <div className="flex items-center gap-1 text-sm text-muted-foreground mb-4">
        <Clock size={14} />
        <span>Uptime: {stack.uptime}</span>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button className="flex-1 flex items-center justify-center gap-1 text-sm bg-secondary hover:bg-secondary/80 py-2 rounded">
          <RefreshCw size={14} />
          Restart
        </button>
        <button className="flex-1 flex items-center justify-center gap-1 text-sm bg-secondary hover:bg-secondary/80 py-2 rounded">
          <Activity size={14} />
          Logs
        </button>
        {stack.url && (
          <button className="flex items-center justify-center gap-1 text-sm bg-primary text-primary-foreground hover:bg-primary/90 px-3 py-2 rounded">
            <ExternalLink size={14} />
          </button>
        )}
      </div>
    </div>
  );
}
