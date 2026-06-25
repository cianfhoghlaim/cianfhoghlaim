/**
 * Learning Outcome Component
 *
 * Displays a single learning outcome with metadata.
 * Rendered by agents via AG-UI GenerativeUI events.
 */

import { Target, BookOpen, Layers } from "lucide-react";
import { cn } from "../../../lib/utils";
import type { AgentComponentProps } from "../ComponentRegistry";

interface LearningOutcomeProps extends AgentComponentProps {
  code?: string;
  text: string;
  strand?: string;
  level?: string;
  subject?: string;
  nation?: string;
  keywords?: string[];
}

export default function LearningOutcome({
  code,
  text,
  strand,
  level,
  subject,
  nation,
  keywords,
}: LearningOutcomeProps) {
  return (
    <div className="rounded-lg border bg-card p-4 space-y-3">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
          <Target className="h-4 w-4 text-primary" />
        </div>
        <div className="flex-1 space-y-2">
          {/* Code and metadata */}
          <div className="flex flex-wrap items-center gap-2">
            {code && (
              <span className="text-xs font-mono bg-muted px-2 py-0.5 rounded">
                {code}
              </span>
            )}
            {nation && (
              <span className="text-xs text-muted-foreground">{nation}</span>
            )}
            {level && (
              <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">
                {level}
              </span>
            )}
          </div>

          {/* Main text */}
          <p className="text-sm">{text}</p>

          {/* Additional info */}
          <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
            {strand && (
              <span className="flex items-center gap-1">
                <Layers className="h-3 w-3" />
                {strand}
              </span>
            )}
            {subject && (
              <span className="flex items-center gap-1">
                <BookOpen className="h-3 w-3" />
                {subject}
              </span>
            )}
          </div>

          {/* Keywords */}
          {keywords && keywords.length > 0 && (
            <div className="flex flex-wrap gap-1 pt-2">
              {keywords.map((keyword, index) => (
                <span
                  key={index}
                  className="text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded"
                >
                  {keyword}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
