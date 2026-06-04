import { createFileRoute } from "@tanstack/react-router";
import { Activity, Cpu, HardDrive, MemoryStick, Network, RefreshCw } from "lucide-react";

export const Route = createFileRoute("/_layout/monitoring/metrics")({
  component: MetricsPage,
});

// Mock metrics data
const systemMetrics = {
  cpu: 32,
  memory: 68,
  disk: 45,
  network: { in: "125 MB/s", out: "45 MB/s" },
};

const containerMetrics = [
  { name: "langfuse-web", cpu: 12, memory: 1.2, status: "healthy" },
  { name: "langfuse-worker", cpu: 8, memory: 0.8, status: "healthy" },
  { name: "mlflow", cpu: 5, memory: 0.6, status: "healthy" },
  { name: "memgraph", cpu: 45, memory: 4.8, status: "warning" },
  { name: "falkordb", cpu: 15, memory: 2.4, status: "healthy" },
  { name: "lancedb", cpu: 5, memory: 0.5, status: "healthy" },
  { name: "tuath-api", cpu: 18, memory: 1.5, status: "healthy" },
  { name: "crypteolas-api", cpu: 15, memory: 1.2, status: "healthy" },
  { name: "dagster", cpu: 10, memory: 1.0, status: "healthy" },
  { name: "beszel", cpu: 5, memory: 0.3, status: "healthy" },
  { name: "dozzle", cpu: 2, memory: 0.1, status: "healthy" },
  { name: "redis", cpu: 3, memory: 0.4, status: "healthy" },
];

function MetricsPage() {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">System Metrics</h1>
          <p className="text-muted-foreground">Real-time infrastructure monitoring via Beszel</p>
        </div>
        <button className="flex items-center gap-2 bg-secondary px-3 py-1.5 rounded hover:bg-secondary/80">
          <RefreshCw size={14} />
          Refresh
        </button>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <MetricCard
          icon={<Cpu className="text-primary" size={24} />}
          label="CPU Usage"
          value={`${systemMetrics.cpu}%`}
          progress={systemMetrics.cpu}
        />
        <MetricCard
          icon={<MemoryStick className="text-primary" size={24} />}
          label="Memory Usage"
          value={`${systemMetrics.memory}%`}
          progress={systemMetrics.memory}
          warning={systemMetrics.memory > 80}
        />
        <MetricCard
          icon={<HardDrive className="text-primary" size={24} />}
          label="Disk Usage"
          value={`${systemMetrics.disk}%`}
          progress={systemMetrics.disk}
        />
        <MetricCard
          icon={<Network className="text-primary" size={24} />}
          label="Network I/O"
          value={`↓${systemMetrics.network.in}`}
          subValue={`↑${systemMetrics.network.out}`}
        />
      </div>

      {/* Container Metrics Table */}
      <div className="bg-card rounded-lg border">
        <div className="p-4 border-b">
          <h2 className="font-semibold flex items-center gap-2">
            <Activity size={18} />
            Container Resources
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b text-left text-sm text-muted-foreground">
                <th className="p-4">Container</th>
                <th className="p-4">Status</th>
                <th className="p-4">CPU %</th>
                <th className="p-4">Memory (GB)</th>
                <th className="p-4 w-48">CPU Graph</th>
                <th className="p-4 w-48">Memory Graph</th>
              </tr>
            </thead>
            <tbody>
              {containerMetrics.map((container) => (
                <tr key={container.name} className="border-b hover:bg-secondary/50">
                  <td className="p-4 font-medium">{container.name}</td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <div className={`status-dot ${container.status}`} />
                      <span className="capitalize text-sm">{container.status}</span>
                    </div>
                  </td>
                  <td className="p-4">{container.cpu}%</td>
                  <td className="p-4">{container.memory}</td>
                  <td className="p-4">
                    <div className="h-2 bg-secondary rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${container.cpu > 40 ? "bg-status-warning" : "bg-primary"}`}
                        style={{ width: `${container.cpu}%` }}
                      />
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="h-2 bg-secondary rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${container.memory > 4 ? "bg-status-warning" : "bg-primary"}`}
                        style={{ width: `${(container.memory / 6) * 100}%` }}
                      />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function MetricCard({
  icon,
  label,
  value,
  subValue,
  progress,
  warning,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  subValue?: string;
  progress?: number;
  warning?: boolean;
}) {
  return (
    <div className="stat-card">
      <div className="flex items-center justify-between mb-2">
        {icon}
        {progress !== undefined && (
          <span className={`text-sm ${warning ? "text-status-warning" : "text-muted-foreground"}`}>
            {progress > 80 ? "High" : progress > 50 ? "Medium" : "Normal"}
          </span>
        )}
      </div>
      <div className="text-2xl font-bold">{value}</div>
      {subValue && <div className="text-sm text-muted-foreground">{subValue}</div>}
      <div className="text-sm text-muted-foreground">{label}</div>
      {progress !== undefined && (
        <div className="mt-2 h-1.5 bg-secondary rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${warning ? "bg-status-warning" : "bg-primary"}`}
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  );
}
