/**
 * Curriculum Card Component
 *
 * Displays curriculum information from a specific nation.
 * Rendered by agents via AG-UI GenerativeUI events.
 */

import { BookOpen, MapPin, GraduationCap } from "lucide-react";
import { cn } from "../../../lib/utils";
import type { AgentComponentProps } from "../ComponentRegistry";

interface CurriculumCardProps extends AgentComponentProps {
  title: string;
  nation: string;
  level?: string;
  subject?: string;
  description?: string;
  learningOutcomes?: string[];
  sourceUrl?: string;
}

export default function CurriculumCard({
  title,
  nation,
  level,
  subject,
  description,
  learningOutcomes,
  sourceUrl,
}: CurriculumCardProps) {
  const nationColors: Record<string, string> = {
    Ireland: "border-l-green-500",
    England: "border-l-red-500",
    Scotland: "border-l-blue-500",
    Wales: "border-l-red-600",
    "Northern Ireland": "border-l-orange-500",
  };

  return (
    <div
      className={cn(
        "rounded-lg border bg-card text-card-foreground shadow-sm",
        "border-l-4",
        nationColors[nation] || "border-l-primary"
      )}
    >
      <div className="p-4 space-y-3">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="font-semibold text-lg leading-tight">{title}</h3>
            <div className="flex flex-wrap items-center gap-2 mt-1 text-sm text-muted-foreground">
              <span className="flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                {nation}
              </span>
              {level && (
                <span className="flex items-center gap-1">
                  <GraduationCap className="h-3 w-3" />
                  {level}
                </span>
              )}
              {subject && (
                <span className="flex items-center gap-1">
                  <BookOpen className="h-3 w-3" />
                  {subject}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Description */}
        {description && (
          <p className="text-sm text-muted-foreground">{description}</p>
        )}

        {/* Learning Outcomes */}
        {learningOutcomes && learningOutcomes.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Learning Outcomes</h4>
            <ul className="text-sm space-y-1">
              {learningOutcomes.slice(0, 5).map((outcome, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-primary font-medium">{index + 1}.</span>
                  <span className="text-muted-foreground">{outcome}</span>
                </li>
              ))}
              {learningOutcomes.length > 5 && (
                <li className="text-xs text-muted-foreground italic">
                  +{learningOutcomes.length - 5} more outcomes...
                </li>
              )}
            </ul>
          </div>
        )}

        {/* Source Link */}
        {sourceUrl && (
          <a
            href={sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center text-xs text-primary hover:underline"
          >
            View source document
          </a>
        )}
      </div>
    </div>
  );
}
