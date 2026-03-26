import { createFileRoute } from "@tanstack/react-router";
import {
  Server,
  Layers,
  Container,
  Activity,
  Cpu,
  HardDrive,
  MemoryStick,
  ArrowUpRight,
} from "lucide-react";

export const Route = createFileRoute("/")({
  component: DashboardPage,
});

// Placeholder data - will be loaded from API
const serverStats = {
  total: 3,
  online: 3,
  stacks: 12,
  containers: 28,
};

const servers = [
  {
    id: "srv-1",
    name: "bunchloch-main",
    status: "online",
    cpu: 45,
    memory: 62,
    disk: 34,
    stacks: 5,
  },
  {
    id: "srv-2",
    name: "bunchloch-worker",
    status: "online",
    cpu: 23,
    memory: 48,
    disk: 28,
    stacks: 4,
  },
  {
    id: "srv-3",
    name: "bunchloch-gpu",
    status: "online",
    cpu: 78,
    memory: 85,
    disk: 45,
    stacks: 3,
  },
];

const recentActivity = [
  { action: "Stack deployed", target: "langfuse", time: "2 min ago" },
  { action: "Container restarted", target: "marimo-1", time: "15 min ago" },
  { action: "Stack updated", target: "litellm", time: "1 hour ago" },
  { action: "Server synced", target: "bunchloch-main", time: "2 hours ago" },
];

function DashboardPage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
          <p className="text-muted-foreground">
            Overview of your self-hosted infrastructure
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard
            icon={<Server className="h-5 w-5" />}
            label="Servers"
            value={serverStats.total}
            subtext={`${serverStats.online} online`}
          />
          <StatCard
            icon={<Layers className="h-5 w-5" />}
            label="Stacks"
            value={serverStats.stacks}
            subtext="deployed"
          />
          <StatCard
            icon={<Container className="h-5 w-5" />}
            label="Containers"
            value={serverStats.containers}
            subtext="running"
          />
          <StatCard
            icon={<Activity className="h-5 w-5" />}
            label="Uptime"
            value="99.9%"
            subtext="last 30 days"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Server List */}
          <div className="lg:col-span-2 rounded-xl bg-card border border-border p-6">
            <h2 className="text-xl font-semibold mb-4">Servers</h2>
            <div className="space-y-4">
              {servers.map((server) => (
                <ServerCard key={server.id} server={server} />
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="rounded-xl bg-card border border-border p-6">
            <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
            <div className="space-y-4">
              {recentActivity.map((activity, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-3 text-sm"
                >
                  <div className="w-2 h-2 rounded-full bg-primary mt-1.5" />
                  <div>
                    <p className="font-medium">{activity.action}</p>
                    <p className="text-muted-foreground">
                      {activity.target} - {activity.time}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 rounded-xl bg-card border border-border p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <QuickAction
              label="Browse Stacks"
              description="Discover new software"
              href="/stacks"
            />
            <QuickAction
              label="Deploy Stack"
              description="Add to your cluster"
              href="/deploy"
            />
            <QuickAction
              label="View Containers"
              description="Manage running services"
              href="/deploy"
            />
            <QuickAction
              label="Ask Assistant"
              description="Get AI help"
              href="/chat"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  subtext: string;
}

function StatCard({ icon, label, value, subtext }: StatCardProps) {
  return (
    <div className="rounded-xl bg-card border border-border p-4">
      <div className="flex items-center gap-2 text-muted-foreground mb-2">
        {icon}
        <span className="text-sm">{label}</span>
      </div>
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-sm text-muted-foreground">{subtext}</p>
    </div>
  );
}

interface Server {
  id: string;
  name: string;
  status: string;
  cpu: number;
  memory: number;
  disk: number;
  stacks: number;
}

function ServerCard({ server }: { server: Server }) {
  return (
    <div className="rounded-lg bg-muted/50 p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              server.status === "online" ? "bg-green-500" : "bg-red-500"
            }`}
          />
          <span className="font-medium">{server.name}</span>
        </div>
        <span className="text-sm text-muted-foreground">
          {server.stacks} stacks
        </span>
      </div>

      <div className="grid grid-cols-3 gap-4 text-sm">
        <ResourceBar
          icon={<Cpu className="h-3 w-3" />}
          label="CPU"
          value={server.cpu}
        />
        <ResourceBar
          icon={<MemoryStick className="h-3 w-3" />}
          label="RAM"
          value={server.memory}
        />
        <ResourceBar
          icon={<HardDrive className="h-3 w-3" />}
          label="Disk"
          value={server.disk}
        />
      </div>
    </div>
  );
}

interface ResourceBarProps {
  icon: React.ReactNode;
  label: string;
  value: number;
}

function ResourceBar({ icon, label, value }: ResourceBarProps) {
  const getColor = (val: number) => {
    if (val > 80) return "bg-red-500";
    if (val > 60) return "bg-yellow-500";
    return "bg-green-500";
  };

  return (
    <div>
      <div className="flex items-center gap-1 text-muted-foreground mb-1">
        {icon}
        <span>{label}</span>
        <span className="ml-auto">{value}%</span>
      </div>
      <div className="h-1.5 rounded-full bg-muted overflow-hidden">
        <div
          className={`h-full rounded-full ${getColor(value)}`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}

interface QuickActionProps {
  label: string;
  description: string;
  href: string;
}

function QuickAction({ label, description, href }: QuickActionProps) {
  return (
    <a
      href={href}
      className="flex items-start justify-between rounded-lg bg-muted/50 p-4 hover:bg-muted transition-colors group"
    >
      <div>
        <p className="font-medium">{label}</p>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      <ArrowUpRight className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
    </a>
  );
}
