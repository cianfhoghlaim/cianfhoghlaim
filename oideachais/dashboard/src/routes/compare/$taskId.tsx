import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "convex/react";
import { api } from "@convex/_generated/api";
import { Id } from "@convex/_generated/dataModel";
import { ProgressTracker } from "~/components/comparison/ProgressTracker";
import { ArrowLeft, Download, FileText, Copy, Check } from "lucide-react";
import { useState } from "react";

export const Route = createFileRoute("/compare/$taskId")({
  component: TaskResultsPage,
});

function TaskResultsPage() {
  const { taskId } = Route.useParams();
  const taskData = useQuery(api.tasks.getWithComparisons, {
    id: taskId as Id<"tasks">,
  });
  const [copiedId, setCopiedId] = useState<string | null>(null);

  if (!taskData) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          <p className="mt-4 text-slate-600 dark:text-slate-400">
            Loading comparison...
          </p>
        </div>
      </div>
    );
  }

  const { task, comparisons } = taskData;
  const successfulComparisons = comparisons.filter((c) => c.status === "success");
  const isComplete = task.status === "completed" || task.status === "failed";

  const handleCopy = async (content: string, id: string) => {
    await navigator.clipboard.writeText(content);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            to="/compare"
            className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
              {task.filename}
            </h1>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {task.selectedModels.length} models • {task.outputFormat} format
            </p>
          </div>
        </div>

        {isComplete && successfulComparisons.length > 0 && (
          <button className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700">
            <Download className="h-4 w-4" />
            Download All
          </button>
        )}
      </div>

      {/* Progress Section */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-white">
          Progress
        </h2>
        <ProgressTracker taskId={taskId as Id<"tasks">} />
      </div>

      {/* Results Grid */}
      {isComplete && successfulComparisons.length > 0 && (
        <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-white">
            Results
          </h2>
          <div
            className={`grid gap-4 ${
              successfulComparisons.length === 1
                ? "grid-cols-1"
                : successfulComparisons.length === 2
                  ? "grid-cols-2"
                  : "grid-cols-1 lg:grid-cols-3"
            }`}
          >
            {successfulComparisons.map((comparison) => (
              <ResultCard
                key={comparison._id}
                comparison={comparison}
                onCopy={handleCopy}
                isCopied={copiedId === comparison._id}
              />
            ))}
          </div>
        </div>
      )}

      {/* Metrics Table */}
      {isComplete && successfulComparisons.length > 1 && (
        <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-white">
            Comparison Metrics
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-700">
                  <th className="py-3 pr-4 text-left text-sm font-medium text-slate-500 dark:text-slate-400">
                    Model
                  </th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-slate-500 dark:text-slate-400">
                    Duration
                  </th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-slate-500 dark:text-slate-400">
                    Output Size
                  </th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-slate-500 dark:text-slate-400">
                    Characters
                  </th>
                  <th className="pl-4 py-3 text-right text-sm font-medium text-slate-500 dark:text-slate-400">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {comparisons.map((c) => (
                  <tr
                    key={c._id}
                    className="border-b border-slate-100 dark:border-slate-800"
                  >
                    <td className="py-3 pr-4 font-medium text-slate-900 dark:text-white">
                      {c.modelName}
                    </td>
                    <td className="px-4 py-3 text-right text-slate-600 dark:text-slate-400">
                      {c.durationMs ? `${(c.durationMs / 1000).toFixed(2)}s` : "-"}
                    </td>
                    <td className="px-4 py-3 text-right text-slate-600 dark:text-slate-400">
                      {c.outputSizeBytes
                        ? `${(c.outputSizeBytes / 1024).toFixed(1)} KB`
                        : "-"}
                    </td>
                    <td className="px-4 py-3 text-right text-slate-600 dark:text-slate-400">
                      {c.metrics?.characterCount?.toLocaleString() ?? "-"}
                    </td>
                    <td className="pl-4 py-3 text-right">
                      <span
                        className={`rounded-full px-2 py-1 text-xs font-medium ${
                          c.status === "success"
                            ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                            : c.status === "failed"
                              ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                              : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400"
                        }`}
                      >
                        {c.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

interface ResultCardProps {
  comparison: {
    _id: Id<"comparisons">;
    modelName: string;
    modelProvider: string;
    durationMs?: number;
    outputSizeBytes?: number;
  };
  onCopy: (content: string, id: string) => void;
  isCopied: boolean;
}

function ResultCard({ comparison, onCopy, isCopied }: ResultCardProps) {
  const result = useQuery(api.comparisons.getResult, {
    comparisonId: comparison._id,
  });

  return (
    <div className="flex flex-col rounded-lg border border-slate-200 dark:border-slate-700">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 p-4 dark:border-slate-700">
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-slate-400" />
          <span className="font-medium text-slate-900 dark:text-white">
            {comparison.modelName}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onCopy(result?.content ?? "", comparison._id)}
            className="rounded p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-700"
          >
            {isCopied ? (
              <Check className="h-4 w-4 text-green-500" />
            ) : (
              <Copy className="h-4 w-4" />
            )}
          </button>
          <button className="rounded p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-700">
            <Download className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Content Preview */}
      <div className="flex-1 overflow-auto p-4">
        {result ? (
          <pre className="max-h-[300px] overflow-auto whitespace-pre-wrap text-sm text-slate-700 dark:text-slate-300">
            {result.isTruncated
              ? `${result.content}...\n\n[Truncated - ${result.previewLength} chars shown]`
              : result.content}
          </pre>
        ) : (
          <div className="flex h-32 items-center justify-center">
            <p className="text-sm text-slate-400">Loading result...</p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between border-t border-slate-200 px-4 py-2 text-xs text-slate-500 dark:border-slate-700 dark:text-slate-400">
        <span>{comparison.modelProvider}</span>
        <span>
          {comparison.durationMs
            ? `${(comparison.durationMs / 1000).toFixed(2)}s`
            : "-"}
        </span>
      </div>
    </div>
  );
}
