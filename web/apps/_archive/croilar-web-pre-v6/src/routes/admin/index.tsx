import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Activity,
  AlertTriangle,
  Bot,
  CheckCircle2,
  Clock,
  Database,
  FileCode,
  NotebookPen,
  Server,
  Workflow,
  XCircle,
} from "lucide-react";

export const Route = createFileRoute("/admin/")({
  component: DashboardPage,
});

function DashboardPage() {
  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Welcome to the Cianfhoghlaim Developer Portal</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <StatCard
          icon={<Server className="text-primary" size={24} />}
          label="Active Stacks"
          value="23"
          status="healthy"
        />
        <StatCard
          icon={<Bot className="text-primary" size={24} />}
          label="Agents"
          value="9"
          status="healthy"
        />
        <StatCard
          icon={<Workflow className="text-primary" size={24} />}
          label="Pipelines"
          value="12"
          status="healthy"
        />
        <StatCard
          icon={<Database className="text-primary" size={24} />}
          label="Data Sources"
          value="8"
          status="healthy"
        />
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-2 gap-6">
        {/* Stack Status */}
        <div className="bg-card rounded-lg border p-4">
          <h2 className="font-semibold mb-4 flex items-center gap-2">
            <Server size={18} />
            Stack Status
          </h2>
          <div className="space-y-3">
            <StackStatusRow name="Langfuse" status="healthy" uptime="99.9%" />
            <StackStatusRow name="MLflow" status="healthy" uptime="99.8%" />
            <StackStatusRow name="FalkorDB" status="healthy" uptime="100%" />
            <StackStatusRow name="LanceDB" status="healthy" uptime="100%" />
            <StackStatusRow name="Memgraph" status="warning" uptime="98.5%" />
            <StackStatusRow name="Dozzle" status="healthy" uptime="99.9%" />
            <StackStatusRow name="Beszel" status="healthy" uptime="99.9%" />
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-card rounded-lg border p-4">
          <h2 className="font-semibold mb-4 flex items-center gap-2">
            <Activity size={18} />
            Recent Activity
          </h2>
          <div className="space-y-3">
            <ActivityRow
              icon={<CheckCircle2 size={16} className="text-status-healthy" />}
              message="Pipeline 'celtic_curriculum' completed"
              time="2 min ago"
            />
            <ActivityRow
              icon={<Bot size={16} className="text-primary" />}
              message="Agent chat session started"
              time="5 min ago"
            />
            <ActivityRow
              icon={<AlertTriangle size={16} className="text-status-warning" />}
              message="Memgraph high memory usage"
              time="12 min ago"
            />
            <ActivityRow
              icon={<CheckCircle2 size={16} className="text-status-healthy" />}
              message="Stack 'Langfuse' deployed"
              time="1 hour ago"
            />
            <ActivityRow
              icon={<XCircle size={16} className="text-status-error" />}
              message="Pipeline 'defi_protocols' failed"
              time="2 hours ago"
            />
          </div>
        </div>
      </div>

      {/* Agent Quick Access */}
      <div className="mt-6 bg-card rounded-lg border p-4">
        <h2 className="font-semibold mb-4 flex items-center gap-2">
          <Bot size={18} />
          Quick Chat
        </h2>
        <div className="grid grid-cols-3 gap-4">
          <AgentCard
            name="Tuath Agent"
            description="Celtic language learning & mythology"
            agents={["celtic_tutor", "mythology_narrator", "quest_guide"]}
          />
          <AgentCard
            name="Crypteolas Agent"
            description="GitHub intelligence & DeFi analytics"
            agents={["protocol_research", "code_analysis", "defi_analytics"]}
          />
          <AgentCard
            name="Portal Agent"
            description="Infrastructure management & monitoring"
            agents={["stack_manager", "pipeline_runner"]}
          />
        </div>
      </div>

      {/* DevTools quick access (croilar-devtools-hub) */}
      <div className="mt-6 bg-card rounded-lg border p-4">
        <h2 className="font-semibold mb-4 flex items-center gap-2">
          <FileCode size={18} />
          DevTools Hub
        </h2>
        <div className="grid grid-cols-2 gap-4">
          <Link
            to="/web"
            className="bg-secondary/50 rounded-lg p-4 hover:bg-secondary transition-colors"
          >
            <div className="flex items-center gap-2 mb-1">
              <FileCode size={16} />
              <h3 className="font-medium">Web Stack</h3>
            </div>
            <p className="text-sm text-muted-foreground">
              TanStack routes, Convex functions, BAML schemas, Cloudflare
              resources, and marimo notebooks across all four projects.
            </p>
          </Link>
          <Link
            to="/notebooks"
            className="bg-secondary/50 rounded-lg p-4 hover:bg-secondary transition-colors"
          >
            <div className="flex items-center gap-2 mb-1">
              <NotebookPen size={16} />
              <h3 className="font-medium">Notebooks</h3>
            </div>
            <p className="text-sm text-muted-foreground">
              All marimo notebooks across the monorepo, grouped by project.
            </p>
          </Link>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  status,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  status: "healthy" | "warning" | "error";
}) {
  return (
    <div className="stat-card">
      <div className="flex items-center justify-between mb-2">
        {icon}
        <div className={`status-dot ${status}`} />
      </div>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-sm text-muted-foreground">{label}</div>
    </div>
  );
}

function StackStatusRow({
  name,
  status,
  uptime,
}: {
  name: string;
  status: "healthy" | "warning" | "error";
  uptime: string;
}) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-border last:border-0">
      <div className="flex items-center gap-2">
        <div className={`status-dot ${status}`} />
        <span>{name}</span>
      </div>
      <div className="flex items-center gap-4 text-sm text-muted-foreground">
        <span className="flex items-center gap-1">
          <Clock size={14} />
          {uptime}
        </span>
      </div>
    </div>
  );
}

function ActivityRow({
  icon,
  message,
  time,
}: {
  icon: React.ReactNode;
  message: string;
  time: string;
}) {
  return (
    <div className="flex items-center gap-3 py-2 border-b border-border last:border-0">
      {icon}
      <span className="flex-1 text-sm">{message}</span>
      <span className="text-xs text-muted-foreground">{time}</span>
    </div>
  );
}

function AgentCard({
  name,
  description,
  agents,
}: {
  name: string;
  description: string;
  agents: string[];
}) {
  return (
    <div className="bg-secondary/50 rounded-lg p-4 hover:bg-secondary cursor-pointer transition-colors">
      <h3 className="font-medium mb-1">{name}</h3>
      <p className="text-sm text-muted-foreground mb-2">{description}</p>
      <div className="flex flex-wrap gap-1">
        {agents.map((agent) => (
          <span
            key={agent}
            className="text-xs bg-background/50 px-2 py-0.5 rounded"
          >
            {agent}
          </span>
        ))}
      </div>
    </div>
  );
}
