/**
 * Status Card Component
 *
 * Displays status information or feedback from agent operations.
 * Rendered by agents via AG-UI GenerativeUI events.
 */

import { CheckCircle, AlertCircle, Info, AlertTriangle } from "lucide-react";
import { cn } from "../../../lib/utils";
import type { AgentComponentProps } from "../ComponentRegistry";

type StatusType = "success" | "error" | "warning" | "info";

interface StatusCardProps extends AgentComponentProps {
  title: string;
  message?: string;
  status?: StatusType;
  details?: string[];
}

const statusConfig: Record<
  StatusType,
  { icon: typeof CheckCircle; className: string }
> = {
  success: {
    icon: CheckCircle,
    className: "border-green-500/50 bg-green-50 dark:bg-green-950/30",
  },
  error: {
    icon: AlertCircle,
    className: "border-red-500/50 bg-red-50 dark:bg-red-950/30",
  },
  warning: {
    icon: AlertTriangle,
    className: "border-yellow-500/50 bg-yellow-50 dark:bg-yellow-950/30",
  },
  info: {
    icon: Info,
    className: "border-blue-500/50 bg-blue-50 dark:bg-blue-950/30",
  },
};

export default function StatusCard({
  title,
  message,
  status = "info",
  details,
}: StatusCardProps) {
  const { icon: Icon, className } = statusConfig[status];

  return (
    <div className={cn("rounded-lg border p-4", className)}>
      <div className="flex items-start gap-3">
        <Icon
          className={cn(
            "h-5 w-5 flex-shrink-0",
            status === "success" && "text-green-600",
            status === "error" && "text-red-600",
            status === "warning" && "text-yellow-600",
            status === "info" && "text-blue-600"
          )}
        />
        <div className="space-y-1 flex-1">
          <h4 className="font-medium text-sm">{title}</h4>
          {message && (
            <p className="text-sm text-muted-foreground">{message}</p>
          )}
          {details && details.length > 0 && (
            <ul className="text-xs text-muted-foreground space-y-0.5 mt-2">
              {details.map((detail, index) => (
                <li key={index}>• {detail}</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
