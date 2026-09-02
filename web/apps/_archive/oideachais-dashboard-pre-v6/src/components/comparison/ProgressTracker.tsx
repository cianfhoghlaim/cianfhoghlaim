import { useQuery } from "convex/react";
import { api } from "@convex/_generated/api";
import { Id } from "@convex/_generated/dataModel";
import { CheckCircle, XCircle, Clock, Loader2 } from "lucide-react";

interface ProgressTrackerProps {
  taskId: Id<"tasks">;
}

export function ProgressTracker({ taskId }: ProgressTrackerProps) {
  const taskData = useQuery(api.tasks.getWithComparisons, { id: taskId });

  if (!taskData) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-4 w-32 rounded bg-slate-200 dark:bg-slate-700" />
        <div className="h-2 rounded-full bg-slate-200 dark:bg-slate-700" />
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-14 rounded-lg bg-slate-100 dark:bg-slate-800"
            />
          ))}
        </div>
      </div>
    );
  }

  const { task, comparisons } = taskData;

  const completed = comparisons.filter(
    (c) =>
      c.status === "success" || c.status === "failed" || c.status === "timeout"
  ).length;
  const total = comparisons.length;
  const progress = total > 0 ? Math.round((completed / total) * 100) : 0;
  const isComplete = task.status === "completed" || task.status === "failed";

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "failed":
        return <XCircle className="h-5 w-5 text-red-500" />;
      case "timeout":
        return <Clock className="h-5 w-5 text-amber-500" />;
      case "running":
        return <Loader2 className="h-5 w-5 animate-spin text-blue-500" />;
      default:
        return <Clock className="h-5 w-5 text-slate-400" />;
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      pending: "Waiting",
      running: "Processing",
      success: "Complete",
      failed: "Failed",
      timeout: "Timeout",
    };
    return labels[status] || status;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "success":
        return "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400";
      case "failed":
        return "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400";
      case "timeout":
        return "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400";
      case "running":
        return "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400";
      default:
        return "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400";
    }
  };

  return (
    <div className="space-y-6">
      {/* Overall Progress */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-600 dark:text-slate-400">
            Overall Progress
          </span>
          <span className="font-medium text-slate-900 dark:text-white">
            {completed}/{total} models • {progress}%
          </span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
          <div
            className="h-full rounded-full bg-blue-600 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Per-Model Progress */}
      <div className="space-y-2">
        {comparisons.map((comp) => (
          <div
            key={comp._id}
            className="flex items-center justify-between rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800"
          >
            <div className="flex items-center gap-3">
              {getStatusIcon(comp.status)}
              <div>
                <p className="font-medium text-slate-900 dark:text-white">
                  {comp.modelName}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {comp.modelProvider}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {comp.durationMs && (
                <span className="text-sm text-slate-500 dark:text-slate-400">
                  {(comp.durationMs / 1000).toFixed(2)}s
                </span>
              )}
              <span
                className={`rounded-full px-2.5 py-1 text-xs font-medium ${getStatusColor(comp.status)}`}
              >
                {getStatusLabel(comp.status)}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Status Message */}
      {isComplete && (
        <div
          className={`rounded-lg p-4 ${
            task.status === "completed"
              ? "bg-green-50 dark:bg-green-950/20"
              : "bg-red-50 dark:bg-red-950/20"
          }`}
        >
          <p
            className={`font-medium ${
              task.status === "completed"
                ? "text-green-700 dark:text-green-400"
                : "text-red-700 dark:text-red-400"
            }`}
          >
            {task.status === "completed"
              ? "Comparison complete! View results below."
              : "Comparison failed. Some models may have encountered errors."}
          </p>
          {task.totalDurationMs && (
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
              Total time: {(task.totalDurationMs / 1000).toFixed(2)}s
            </p>
          )}
        </div>
      )}
    </div>
  );
}
