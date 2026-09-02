import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import {
  Server,
  Globe,
  BookOpen,
  Database,
  Activity,
  ExternalLink,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Loader2,
  FileText,
  Bookmark,
  Play,
  Settings,
} from "lucide-react";

export const Route = createFileRoute("/admin/widgets")({
  component: WidgetsPage,
});

interface Widget {
  id: string;
  title: string;
  category: "infrastructure" | "browser" | "knowledge" | "dataflows";
  size: "small" | "medium" | "large";
}

const defaultWidgets: Widget[] = [
  // Infrastructure
  { id: "komodo_status", title: "Komodo Stacks", category: "infrastructure", size: "large" },
  { id: "pangolin_health", title: "Pangolin Health", category: "infrastructure", size: "small" },

  // Browser Agent
  { id: "skyvern_queue", title: "Skyvern Tasks", category: "browser", size: "medium" },
  { id: "browser_sessions", title: "Active Sessions", category: "browser", size: "small" },

  // Knowledge
  { id: "paperless_recent", title: "Recent Documents", category: "knowledge", size: "medium" },
  { id: "linkwarden_bookmarks", title: "Bookmarks", category: "knowledge", size: "medium" },
  { id: "kavita_library", title: "Kavita Library", category: "knowledge", size: "small" },

  // Data Flows
  { id: "dagster_jobs", title: "Dagster Jobs", category: "dataflows", size: "medium" },
  { id: "codeolas_stats", title: "Code Index", category: "dataflows", size: "small" },
];

function WidgetsPage() {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  const categories = [
    { id: "all", label: "All", icon: <Activity size={16} /> },
    { id: "infrastructure", label: "Infrastructure", icon: <Server size={16} /> },
    { id: "browser", label: "Browser", icon: <Globe size={16} /> },
    { id: "knowledge", label: "Knowledge", icon: <BookOpen size={16} /> },
    { id: "dataflows", label: "Data Flows", icon: <Database size={16} /> },
  ];

  const filteredWidgets =
    selectedCategory === "all"
      ? defaultWidgets
      : defaultWidgets.filter((w) => w.category === selectedCategory);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await new Promise((r) => setTimeout(r, 1000));
    setIsRefreshing(false);
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Widget Dashboard</h1>
          <p className="text-muted-foreground">
            Glance-style overview of your homelab
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-2 bg-secondary px-4 py-2 rounded hover:bg-secondary/80"
          >
            <RefreshCw size={16} className={isRefreshing ? "animate-spin" : ""} />
            Refresh All
          </button>
          <button className="flex items-center gap-2 bg-secondary px-4 py-2 rounded hover:bg-secondary/80">
            <Settings size={16} />
            Customize
          </button>
        </div>
      </div>

      {/* Category Filter */}
      <div className="flex gap-2 mb-6">
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`flex items-center gap-2 px-3 py-1.5 text-sm rounded-md ${
              selectedCategory === cat.id
                ? "bg-primary text-primary-foreground"
                : "bg-secondary hover:bg-secondary/80"
            }`}
          >
            {cat.icon}
            {cat.label}
          </button>
        ))}
      </div>

      {/* Widget Grid */}
      <div className="grid grid-cols-12 gap-4">
        {filteredWidgets.map((widget) => (
          <WidgetCard key={widget.id} widget={widget} />
        ))}
      </div>
    </div>
  );
}

function WidgetCard({ widget }: { widget: Widget }) {
  const sizeClasses = {
    small: "col-span-3",
    medium: "col-span-4",
    large: "col-span-6",
  };

  return (
    <div
      className={`${sizeClasses[widget.size]} bg-card rounded-lg border p-4`}
    >
      <WidgetContent widget={widget} />
    </div>
  );
}

function WidgetContent({ widget }: { widget: Widget }) {
  switch (widget.id) {
    case "komodo_status":
      return <KomodoStatusWidget />;
    case "pangolin_health":
      return <PangolinHealthWidget />;
    case "skyvern_queue":
      return <SkyvernQueueWidget />;
    case "browser_sessions":
      return <BrowserSessionsWidget />;
    case "paperless_recent":
      return <PaperlessRecentWidget />;
    case "linkwarden_bookmarks":
      return <LinkwardenBookmarksWidget />;
    case "kavita_library":
      return <KavitaLibraryWidget />;
    case "dagster_jobs":
      return <DagsterJobsWidget />;
    case "codeolas_stats":
      return <CodeolasStatsWidget />;
    default:
      return <div>Unknown widget: {widget.id}</div>;
  }
}

// Infrastructure Widgets
function KomodoStatusWidget() {
  const stacks = [
    { name: "Langfuse", status: "healthy", cpu: "12%", memory: "1.2GB" },
    { name: "MLflow", status: "healthy", cpu: "8%", memory: "0.8GB" },
    { name: "Memgraph", status: "warning", cpu: "45%", memory: "4.8GB" },
    { name: "FalkorDB", status: "healthy", cpu: "15%", memory: "2.4GB" },
    { name: "LanceDB", status: "healthy", cpu: "5%", memory: "0.5GB" },
  ];

  const statusIcon = {
    healthy: <CheckCircle2 size={14} className="text-green-500" />,
    warning: <AlertTriangle size={14} className="text-yellow-500" />,
    error: <XCircle size={14} className="text-red-500" />,
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <Server size={18} />
          Komodo Stacks
        </h3>
        <span className="text-xs text-muted-foreground">
          {stacks.filter((s) => s.status === "healthy").length}/{stacks.length} healthy
        </span>
      </div>
      <div className="space-y-2">
        {stacks.map((stack) => (
          <div
            key={stack.name}
            className="flex items-center justify-between p-2 bg-secondary/50 rounded"
          >
            <div className="flex items-center gap-2">
              {statusIcon[stack.status as keyof typeof statusIcon]}
              <span className="text-sm">{stack.name}</span>
            </div>
            <div className="flex gap-3 text-xs text-muted-foreground">
              <span>{stack.cpu}</span>
              <span>{stack.memory}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function PangolinHealthWidget() {
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <Globe size={18} />
          Pangolin
        </h3>
        <CheckCircle2 size={16} className="text-green-500" />
      </div>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Traefik</span>
          <span className="text-green-500">Online</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">TinyAuth</span>
          <span className="text-green-500">Online</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">PocketID</span>
          <span className="text-green-500">Online</span>
        </div>
      </div>
    </div>
  );
}

// Browser Widgets
function SkyvernQueueWidget() {
  const tasks = [
    { id: 1, url: "example.com", status: "running", progress: 65 },
    { id: 2, url: "another.com", status: "queued", progress: 0 },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <Globe size={18} />
          Skyvern Tasks
        </h3>
        <span className="text-xs text-muted-foreground">{tasks.length} active</span>
      </div>
      <div className="space-y-3">
        {tasks.map((task) => (
          <div key={task.id} className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="truncate max-w-[180px]">{task.url}</span>
              <span
                className={`text-xs ${task.status === "running" ? "text-yellow-500" : "text-muted-foreground"}`}
              >
                {task.status}
              </span>
            </div>
            {task.status === "running" && (
              <div className="h-1.5 bg-secondary rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all"
                  style={{ width: `${task.progress}%` }}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function BrowserSessionsWidget() {
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <Activity size={18} />
          Sessions
        </h3>
      </div>
      <div className="text-3xl font-bold">3</div>
      <div className="text-sm text-muted-foreground">Active browser sessions</div>
    </div>
  );
}

// Knowledge Widgets
function PaperlessRecentWidget() {
  const docs = [
    { id: 1, title: "Invoice #1234", date: "2h ago", correspondent: "Acme Corp" },
    { id: 2, title: "Contract Draft", date: "1d ago", correspondent: "Legal Dept" },
    { id: 3, title: "Receipt - Office", date: "2d ago", correspondent: "Staples" },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <FileText size={18} />
          Recent Documents
        </h3>
        <a href="#" className="text-xs text-primary hover:underline">
          View all
        </a>
      </div>
      <div className="space-y-2">
        {docs.map((doc) => (
          <div
            key={doc.id}
            className="flex items-center justify-between p-2 bg-secondary/50 rounded hover:bg-secondary cursor-pointer"
          >
            <div>
              <div className="text-sm font-medium">{doc.title}</div>
              <div className="text-xs text-muted-foreground">{doc.correspondent}</div>
            </div>
            <span className="text-xs text-muted-foreground">{doc.date}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function LinkwardenBookmarksWidget() {
  const bookmarks = [
    { id: 1, title: "TanStack Start Docs", url: "tanstack.com", tags: ["docs"] },
    { id: 2, title: "AG-UI Protocol", url: "github.com", tags: ["ai", "protocol"] },
    { id: 3, title: "Better Auth Guide", url: "better-auth.com", tags: ["auth"] },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <Bookmark size={18} />
          Bookmarks
        </h3>
        <a href="#" className="text-xs text-primary hover:underline">
          View all
        </a>
      </div>
      <div className="space-y-2">
        {bookmarks.map((bm) => (
          <a
            key={bm.id}
            href={`https://${bm.url}`}
            target="_blank"
            rel="noreferrer"
            className="flex items-center justify-between p-2 bg-secondary/50 rounded hover:bg-secondary"
          >
            <div>
              <div className="text-sm font-medium">{bm.title}</div>
              <div className="text-xs text-muted-foreground">{bm.url}</div>
            </div>
            <ExternalLink size={14} className="text-muted-foreground" />
          </a>
        ))}
      </div>
    </div>
  );
}

function KavitaLibraryWidget() {
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <BookOpen size={18} />
          Kavita
        </h3>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div>
          <div className="text-xl font-bold">142</div>
          <div className="text-xs text-muted-foreground">Books</div>
        </div>
        <div>
          <div className="text-xl font-bold">38</div>
          <div className="text-xs text-muted-foreground">Comics</div>
        </div>
        <div>
          <div className="text-xl font-bold">5</div>
          <div className="text-xs text-muted-foreground">Reading</div>
        </div>
      </div>
    </div>
  );
}

// Data Flow Widgets
function DagsterJobsWidget() {
  const jobs = [
    { name: "codeolas_indexing", status: "success", lastRun: "1h ago" },
    { name: "aleyum_ingestion", status: "running", lastRun: "now" },
    { name: "browser_extract", status: "success", lastRun: "3h ago" },
  ];

  const statusIcon = {
    success: <CheckCircle2 size={14} className="text-green-500" />,
    running: <Loader2 size={14} className="text-yellow-500 animate-spin" />,
    failed: <XCircle size={14} className="text-red-500" />,
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <Play size={18} />
          Dagster Jobs
        </h3>
        <a href="#" className="text-xs text-primary hover:underline">
          Open Dagster
        </a>
      </div>
      <div className="space-y-2">
        {jobs.map((job) => (
          <div
            key={job.name}
            className="flex items-center justify-between p-2 bg-secondary/50 rounded"
          >
            <div className="flex items-center gap-2">
              {statusIcon[job.status as keyof typeof statusIcon]}
              <span className="text-sm font-mono">{job.name}</span>
            </div>
            <span className="text-xs text-muted-foreground">{job.lastRun}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function CodeolasStatsWidget() {
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <Database size={18} />
          Code Index
        </h3>
      </div>
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Indexed Files</span>
          <span>12,453</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Code Chunks</span>
          <span>89,721</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Last Update</span>
          <span>1h ago</span>
        </div>
      </div>
    </div>
  );
}
