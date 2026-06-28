/**
 * Progress Indicator Component
 *
 * Shows progress of agent operations or pipeline stages.
 * Rendered by agents via AG-UI GenerativeUI events.
 */

import { Loader2, CheckCircle, XCircle, Clock } from "lucide-react";
import { cn } from "../../../lib/utils";
import type { AgentComponentProps } from "../ComponentRegistry";

interface ProgressStep {
  id: string;
  label: string;
  status: "pending" | "running" | "completed" | "error";
  message?: string;
}

interface ProgressIndicatorProps extends AgentComponentProps {
  title?: string;
  steps: ProgressStep[];
  currentStepId?: string;
  overallProgress?: number;
}

export default function ProgressIndicator({
  title,
  steps,
  currentStepId,
  overallProgress,
}: ProgressIndicatorProps) {
  const StatusIcon = ({ status }: { status: ProgressStep["status"] }) => {
    switch (status) {
      case "running":
        return <Loader2 className="h-4 w-4 animate-spin text-primary" />;
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "error":
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  return (
    <div className="rounded-lg border bg-card p-4 space-y-4">
      {/* Header */}
      {title && (
        <div className="flex items-center justify-between">
          <h3 className="font-medium text-sm">{title}</h3>
          {overallProgress !== undefined && (
            <span className="text-xs text-muted-foreground">
              {Math.round(overallProgress)}% complete
            </span>
          )}
        </div>
      )}

      {/* Overall progress bar */}
      {overallProgress !== undefined && (
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-primary rounded-full transition-all"
            style={{ width: `${overallProgress}%` }}
          />
        </div>
      )}

      {/* Steps */}
      <div className="space-y-2">
        {steps.map((step, index) => (
          <div
            key={step.id}
            className={cn(
              "flex items-center gap-3 p-2 rounded-md",
              step.id === currentStepId && "bg-muted/50",
              step.status === "error" && "bg-red-50 dark:bg-red-950/20"
            )}
          >
            <StatusIcon status={step.status} />
            <div className="flex-1">
              <span
                className={cn(
                  "text-sm",
                  step.status === "pending" && "text-muted-foreground",
                  step.status === "running" && "font-medium",
                  step.status === "completed" && "text-muted-foreground",
                  step.status === "error" && "text-red-600"
                )}
              >
                {step.label}
              </span>
              {step.message && (
                <p className="text-xs text-muted-foreground">{step.message}</p>
              )}
            </div>
            <span className="text-xs text-muted-foreground">
              {index + 1}/{steps.length}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
