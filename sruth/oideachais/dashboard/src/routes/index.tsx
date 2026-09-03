import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "convex/react";
import { api } from "@convex/_generated/api";
import {
  FileText,
  BarChart3,
  Clock,
  CheckCircle,
  ArrowRight,
} from "lucide-react";

export const Route = createFileRoute("/")({
  component: Dashboard,
});

function Dashboard() {
  const recentTasks = useQuery(api.tasks.recent, { limit: 5 });
  const models = useQuery(api.models.list);

  const availableModels = models?.filter((m) => m.isAvailable).length ?? 0;
  const totalModels = models?.length ?? 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
            OCR Comparison Dashboard
          </h1>
          <p className="mt-2 text-slate-600 dark:text-slate-400">
            Compare 14 OCR and vision models side-by-side
          </p>
        </div>
        <Link
          to="/compare"
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
        >
          New Comparison
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatsCard
          title="Available Models"
          value={`${availableModels}/${totalModels}`}
          icon={<BarChart3 className="h-5 w-5" />}
          description="Models ready to use"
        />
        <StatsCard
          title="Recent Comparisons"
          value={recentTasks?.length ?? 0}
          icon={<FileText className="h-5 w-5" />}
          description="In the last 24 hours"
        />
        <StatsCard
          title="Avg Processing Time"
          value="12.4s"
          icon={<Clock className="h-5 w-5" />}
          description="Per model"
        />
        <StatsCard
          title="Success Rate"
          value="98.2%"
          icon={<CheckCircle className="h-5 w-5" />}
          description="Overall accuracy"
        />
      </div>

      {/* Quick Compare Section */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
          Quick Compare
        </h2>
        <p className="text-slate-600 dark:text-slate-400 mb-4">
          Drop a PDF here or click to upload and start comparing models
          instantly.
        </p>
        <Link
          to="/compare"
          className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
        >
          Go to Compare
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      {/* Recent Tasks */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
            Recent Comparisons
          </h2>
          <Link
            to="/history"
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            View All
          </Link>
        </div>

        {recentTasks && recentTasks.length > 0 ? (
          <div className="space-y-3">
            {recentTasks.map((task) => (
              <div
                key={task._id}
                className="flex items-center justify-between rounded-lg bg-slate-50 p-3 dark:bg-slate-700"
              >
                <div className="flex items-center gap-3">
                  <FileText className="h-5 w-5 text-slate-400" />
                  <div>
                    <p className="font-medium text-slate-900 dark:text-white">
                      {task.filename}
                    </p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {task.selectedModels.length} models compared
                    </p>
                  </div>
                </div>
                <span
                  className={`rounded-full px-2 py-1 text-xs font-medium ${
                    task.status === "completed"
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : task.status === "running"
                        ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                        : "bg-slate-100 text-slate-700 dark:bg-slate-600 dark:text-slate-300"
                  }`}
                >
                  {task.status}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-500 dark:text-slate-400 text-center py-8">
            No recent comparisons. Start by uploading a PDF!
          </p>
        )}
      </div>
    </div>
  );
}

function StatsCard({
  title,
  value,
  icon,
  description,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  description: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
        {icon}
        <span className="text-sm">{title}</span>
      </div>
      <p className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
        {value}
      </p>
      <p className="mt-1 text-xs text-slate-500 dark:text-slate-500">
        {description}
      </p>
    </div>
  );
}
