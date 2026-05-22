/**
 * ProgressChart - Generative UI Component.
 *
 * Displays learning progress visualization for curriculum topics.
 * Shows completion rates, time spent, and performance metrics.
 */

import { useMemo } from "react";
import {
  TrendingUp,
  TrendingDown,
  Clock,
  Target,
  Award,
  X,
  ChevronRight,
} from "lucide-react";

// ============================================================================
// Types
// ============================================================================

export interface ProgressItem {
  id: string;
  name: string;
  nameGa?: string;
  completed: number;
  total: number;
  score?: number;
  timeSpent?: number; // minutes
  lastAccessed?: string;
}

export interface ProgressChartProps {
  /** Unique ID from AG-UI event */
  componentId?: string;
  /** Callback to dismiss the chart */
  onDismiss?: () => void;

  /** Title for the progress chart */
  title: string;
  /** Subtitle or description */
  subtitle?: string;
  /** Progress items to display */
  items: ProgressItem[];
  /** Overall completion percentage */
  overallProgress?: number;
  /** Overall score/grade */
  overallScore?: number;
  /** Total time spent (minutes) */
  totalTimeSpent?: number;
  /** Whether to show Irish names */
  showIrish?: boolean;
  /** Chart display variant */
  variant?: "compact" | "detailed" | "summary";
  /** Callback when item is clicked */
  onItemClick?: (itemId: string) => void;
  /** Callback for viewing full report */
  onViewReport?: () => void;
}

// ============================================================================
// Helper Components
// ============================================================================

function ProgressBar({
  value,
  max,
  className = "",
  colorClass = "bg-blue-500",
}: {
  value: number;
  max: number;
  className?: string;
  colorClass?: string;
}) {
  const percentage = max > 0 ? Math.round((value / max) * 100) : 0;

  return (
    <div className={`h-2 bg-gray-200 rounded-full overflow-hidden ${className}`}>
      <div
        className={`h-full rounded-full transition-all duration-500 ${colorClass}`}
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}

function getScoreColor(score: number): string {
  if (score >= 80) return "text-green-600";
  if (score >= 60) return "text-yellow-600";
  return "text-red-600";
}

function getProgressColor(percentage: number): string {
  if (percentage >= 80) return "bg-green-500";
  if (percentage >= 50) return "bg-yellow-500";
  return "bg-blue-500";
}

function formatTime(minutes: number): string {
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
}

// ============================================================================
// Component
// ============================================================================

export function ProgressChart({
  componentId,
  onDismiss,
  title,
  subtitle,
  items,
  overallProgress,
  overallScore,
  totalTimeSpent,
  showIrish = false,
  variant = "detailed",
  onItemClick,
  onViewReport,
}: ProgressChartProps) {
  // Calculate derived stats
  const stats = useMemo(() => {
    const totalCompleted = items.reduce((sum, item) => sum + item.completed, 0);
    const totalItems = items.reduce((sum, item) => sum + item.total, 0);
    const avgScore =
      items.filter((i) => i.score !== undefined).length > 0
        ? items
            .filter((i) => i.score !== undefined)
            .reduce((sum, item) => sum + (item.score ?? 0), 0) /
          items.filter((i) => i.score !== undefined).length
        : undefined;
    const calcProgress =
      overallProgress ?? (totalItems > 0 ? (totalCompleted / totalItems) * 100 : 0);

    return {
      totalCompleted,
      totalItems,
      avgScore,
      progress: Math.round(calcProgress),
    };
  }, [items, overallProgress]);

  const progressTrend = stats.progress >= 50 ? "up" : "down";

  return (
    <div
      className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden"
      data-component-id={componentId}
    >
      {/* Header */}
      <div className="px-4 py-3 border-b bg-gradient-to-r from-emerald-50 to-teal-50">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
              {progressTrend === "up" ? (
                <TrendingUp className="h-5 w-5 text-emerald-600" />
              ) : (
                <TrendingDown className="h-5 w-5 text-amber-600" />
              )}
            </div>
            <div>
              <h3 className="font-medium text-gray-900">{title}</h3>
              {subtitle && (
                <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>
              )}
            </div>
          </div>

          {onDismiss && (
            <button
              onClick={onDismiss}
              className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Summary Stats */}
      {(variant === "detailed" || variant === "summary") && (
        <div className="px-4 py-4 border-b bg-gray-50">
          <div className="grid grid-cols-3 gap-4">
            {/* Progress */}
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 text-2xl font-bold text-gray-900">
                {stats.progress}%
              </div>
              <p className="text-xs text-gray-500 mt-1">Completed</p>
            </div>

            {/* Score */}
            <div className="text-center">
              <div
                className={`text-2xl font-bold ${
                  stats.avgScore !== undefined
                    ? getScoreColor(overallScore ?? stats.avgScore)
                    : "text-gray-400"
                }`}
              >
                {overallScore ?? stats.avgScore !== undefined
                  ? `${Math.round(overallScore ?? stats.avgScore!)}%`
                  : "-"}
              </div>
              <p className="text-xs text-gray-500 mt-1">Avg Score</p>
            </div>

            {/* Time */}
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {totalTimeSpent !== undefined ? formatTime(totalTimeSpent) : "-"}
              </div>
              <p className="text-xs text-gray-500 mt-1">Time Spent</p>
            </div>
          </div>

          {/* Overall progress bar */}
          <div className="mt-4">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>Overall Progress</span>
              <span>
                {stats.totalCompleted} / {stats.totalItems} items
              </span>
            </div>
            <ProgressBar
              value={stats.totalCompleted}
              max={stats.totalItems}
              colorClass={getProgressColor(stats.progress)}
            />
          </div>
        </div>
      )}

      {/* Item List */}
      {variant !== "summary" && items.length > 0 && (
        <div className="divide-y max-h-80 overflow-y-auto">
          {items.map((item) => {
            const itemProgress =
              item.total > 0 ? Math.round((item.completed / item.total) * 100) : 0;
            const displayName = showIrish && item.nameGa ? item.nameGa : item.name;

            return (
              <button
                key={item.id}
                onClick={() => onItemClick?.(item.id)}
                className="w-full px-4 py-3 flex items-center gap-3 hover:bg-gray-50 transition-colors text-left"
              >
                {/* Progress indicator */}
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium ${
                    itemProgress >= 100
                      ? "bg-green-100 text-green-700"
                      : itemProgress >= 50
                      ? "bg-yellow-100 text-yellow-700"
                      : "bg-gray-100 text-gray-600"
                  }`}
                >
                  {itemProgress}%
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-800 truncate">
                      {displayName}
                    </span>
                    <div className="flex items-center gap-3 ml-3">
                      {item.score !== undefined && (
                        <div className="flex items-center gap-1">
                          <Award className="h-3 w-3 text-gray-400" />
                          <span
                            className={`text-xs font-medium ${getScoreColor(
                              item.score
                            )}`}
                          >
                            {item.score}%
                          </span>
                        </div>
                      )}
                      {item.timeSpent !== undefined && (
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3 text-gray-400" />
                          <span className="text-xs text-gray-500">
                            {formatTime(item.timeSpent)}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="mt-1.5 flex items-center gap-2">
                    <ProgressBar
                      value={item.completed}
                      max={item.total}
                      className="flex-1"
                      colorClass={getProgressColor(itemProgress)}
                    />
                    <span className="text-xs text-gray-400 whitespace-nowrap">
                      {item.completed}/{item.total}
                    </span>
                  </div>
                </div>

                <ChevronRight className="h-4 w-4 text-gray-400 flex-shrink-0" />
              </button>
            );
          })}
        </div>
      )}

      {/* Empty state */}
      {items.length === 0 && (
        <div className="px-4 py-8 text-center">
          <Target className="h-8 w-8 text-gray-300 mx-auto mb-2" />
          <p className="text-sm text-gray-500">No progress data available</p>
        </div>
      )}

      {/* Footer */}
      {onViewReport && (
        <div className="px-4 py-3 border-t bg-gray-50">
          <button
            onClick={onViewReport}
            className="text-sm text-emerald-600 hover:text-emerald-700 flex items-center gap-1"
          >
            View full report
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}

export default ProgressChart;
