import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery, useMutation } from "convex/react";
import { api } from "@convex/_generated/api";
import { Id } from "@convex/_generated/dataModel";
import {
  FileText,
  Trash2,
  Eye,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
} from "lucide-react";
import { useState } from "react";

export const Route = createFileRoute("/history/")({
  component: HistoryPage,
});

function HistoryPage() {
  const tasks = useQuery(api.tasks.recent, { limit: 50 });
  const deleteTask = useMutation(api.tasks.deleteTask);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (taskId: Id<"tasks">) => {
    if (!confirm("Are you sure you want to delete this comparison?")) return;
    setDeletingId(taskId);
    try {
      await deleteTask({ taskId });
    } finally {
      setDeletingId(null);
    }
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "running":
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      default:
        return <Clock className="h-4 w-4 text-slate-400" />;
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Comparison History
          </h1>
          <p className="mt-1 text-slate-600 dark:text-slate-400">
            View and manage your past OCR comparisons
          </p>
        </div>
        <Link
          to="/compare"
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          New Comparison
        </Link>
      </div>

      {/* Tasks List */}
      <div className="rounded-xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
        {tasks && tasks.length > 0 ? (
          <div className="divide-y divide-slate-200 dark:divide-slate-700">
            {tasks.map((task) => (
              <div
                key={task._id}
                className="flex items-center justify-between p-4 hover:bg-slate-50 dark:hover:bg-slate-800/50"
              >
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 dark:bg-slate-700">
                    <FileText className="h-5 w-5 text-slate-400" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-medium text-slate-900 dark:text-white">
                        {task.filename}
                      </p>
                      {getStatusIcon(task.status)}
                    </div>
                    <div className="flex items-center gap-3 text-sm text-slate-500 dark:text-slate-400">
                      <span>{formatDate(task.createdAt)}</span>
                      <span>•</span>
                      <span>
                        {task.selectedModels.length} model
                        {task.selectedModels.length !== 1 ? "s" : ""}
                      </span>
                      {task.totalDurationMs && (
                        <>
                          <span>•</span>
                          <span>
                            {(task.totalDurationMs / 1000).toFixed(1)}s
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Link
                    to="/compare/$taskId"
                    params={{ taskId: task._id }}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-400 dark:hover:bg-slate-700"
                  >
                    <Eye className="h-4 w-4" />
                    View
                  </Link>
                  <button
                    onClick={() => handleDelete(task._id)}
                    disabled={deletingId === task._id}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50 dark:border-slate-700 dark:text-red-400 dark:hover:bg-red-950/20"
                  >
                    {deletingId === task._id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="h-4 w-4" />
                    )}
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : tasks ? (
          <div className="py-12 text-center">
            <FileText className="mx-auto h-12 w-12 text-slate-300 dark:text-slate-600" />
            <p className="mt-4 text-slate-600 dark:text-slate-400">
              No comparisons yet
            </p>
            <Link
              to="/compare"
              className="mt-4 inline-flex items-center gap-2 text-blue-600 hover:text-blue-700"
            >
              Start your first comparison
            </Link>
          </div>
        ) : (
          <div className="animate-pulse space-y-4 p-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 rounded-lg bg-slate-100 dark:bg-slate-700" />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
