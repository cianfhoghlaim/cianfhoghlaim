import React from "react";
import { cn } from "@/lib/utils";
import { Maximize2, MoreHorizontal, Minimize2 } from "lucide-react";

interface AnalyticsPanelProps {
  title: string;
  children: React.ReactNode;
  className?: string;
  headerActions?: React.ReactNode;
  isResizable?: boolean;
}

export function AnalyticsPanel({
  title,
  children,
  className,
  headerActions,
  isResizable = true,
}: AnalyticsPanelProps) {
  const [isExpanded, setIsExpanded] = React.useState(false);

  return (
    <div
      className={cn(
        "group relative flex flex-col rounded-xl border border-slate-700 bg-slate-900 overflow-hidden transition-all duration-300",
        isExpanded ? "fixed inset-4 z-50 shadow-2xl" : "h-full",
        className,
      )}
    >
      <div className="flex items-center justify-between border-b border-slate-700 bg-slate-800/50 px-4 py-3 backdrop-blur-sm">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="h-3 w-3 rounded-full bg-rose-500/20 border border-rose-500/50" />
            <div className="h-3 w-3 rounded-full bg-amber-500/20 border border-amber-500/50" />
            <div className="h-3 w-3 rounded-full bg-emerald-500/20 border border-emerald-500/50" />
          </div>
          <h3 className="ml-2 font-semibold text-slate-200">{title}</h3>
        </div>

        <div className="flex items-center gap-2 opacity-0 transition-opacity group-hover:opacity-100">
          {headerActions}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="rounded p-1 text-slate-400 hover:bg-slate-700 hover:text-white"
          >
            {isExpanded ? (
              <Minimize2 className="h-4 w-4" />
            ) : (
              <Maximize2 className="h-4 w-4" />
            )}
          </button>
          <button className="rounded p-1 text-slate-400 hover:bg-slate-700 hover:text-white">
            <MoreHorizontal className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-4 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
        {children}
      </div>

      {isResizable && !isExpanded && (
        <div className="absolute bottom-0 right-0 h-4 w-4 cursor-se-resize">
          <svg
            viewBox="0 0 6 6"
            className="h-full w-full fill-slate-500 opacity-50"
          >
            <path d="M 6 6 L 6 4 L 4 6 Z" />
            <path d="M 6 2 L 6 0 L 0 6 L 2 6 Z" />
          </svg>
        </div>
      )}
    </div>
  );
}
