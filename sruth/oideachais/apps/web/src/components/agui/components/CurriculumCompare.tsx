/**
 * Curriculum Compare Component
 *
 * Displays a side-by-side comparison of curricula from different nations.
 * Rendered by agents via AG-UI GenerativeUI events.
 */

import { ArrowLeftRight, MapPin, GraduationCap } from "lucide-react";
import { cn } from "../../../lib/utils";
import type { AgentComponentProps } from "../ComponentRegistry";

interface CurriculumItem {
  title: string;
  nation: string;
  level?: string;
  subject?: string;
  learningOutcomes?: string[];
}

interface CurriculumCompareProps extends AgentComponentProps {
  title?: string;
  items: CurriculumItem[];
  similarities?: string[];
  differences?: string[];
}

export default function CurriculumCompare({
  title = "Curriculum Comparison",
  items,
  similarities,
  differences,
}: CurriculumCompareProps) {
  const nationColors: Record<string, string> = {
    Ireland: "bg-green-500",
    England: "bg-red-500",
    Scotland: "bg-blue-500",
    Wales: "bg-red-600",
    "Northern Ireland": "bg-orange-500",
  };

  return (
    <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
      {/* Header */}
      <div className="flex items-center gap-2 p-4 border-b bg-muted/50">
        <ArrowLeftRight className="h-5 w-5 text-primary" />
        <h3 className="font-semibold">{title}</h3>
      </div>

      {/* Comparison Grid */}
      <div className="p-4">
        <div className="grid gap-4 md:grid-cols-2">
          {items.map((item, index) => (
            <div
              key={index}
              className="rounded-lg border p-4 space-y-2"
            >
              {/* Nation indicator */}
              <div className="flex items-center gap-2">
                <span
                  className={cn(
                    "w-3 h-3 rounded-full",
                    nationColors[item.nation] || "bg-primary"
                  )}
                />
                <span className="text-sm font-medium flex items-center gap-1">
                  <MapPin className="h-3 w-3" />
                  {item.nation}
                </span>
                {item.level && (
                  <span className="text-xs text-muted-foreground flex items-center gap-1">
                    <GraduationCap className="h-3 w-3" />
                    {item.level}
                  </span>
                )}
              </div>

              <h4 className="font-medium">{item.title}</h4>

              {item.learningOutcomes && item.learningOutcomes.length > 0 && (
                <ul className="text-sm space-y-1 text-muted-foreground">
                  {item.learningOutcomes.slice(0, 3).map((outcome, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-primary">{i + 1}.</span>
                      <span>{outcome}</span>
                    </li>
                  ))}
                  {item.learningOutcomes.length > 3 && (
                    <li className="text-xs italic">
                      +{item.learningOutcomes.length - 3} more...
                    </li>
                  )}
                </ul>
              )}
            </div>
          ))}
        </div>

        {/* Similarities & Differences */}
        {(similarities?.length || differences?.length) && (
          <div className="grid gap-4 md:grid-cols-2 mt-4 pt-4 border-t">
            {similarities && similarities.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-green-600 dark:text-green-400">
                  Similarities
                </h4>
                <ul className="text-sm space-y-1">
                  {similarities.map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-muted-foreground">
                      <span className="text-green-500">+</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {differences && differences.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-orange-600 dark:text-orange-400">
                  Differences
                </h4>
                <ul className="text-sm space-y-1">
                  {differences.map((d, i) => (
                    <li key={i} className="flex items-start gap-2 text-muted-foreground">
                      <span className="text-orange-500">~</span>
                      <span>{d}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
