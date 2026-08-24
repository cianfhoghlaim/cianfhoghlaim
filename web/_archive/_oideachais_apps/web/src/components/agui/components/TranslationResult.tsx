/**
 * Translation Result Component
 *
 * Displays translation results between Celtic languages.
 * Rendered by agents via AG-UI GenerativeUI events.
 */

import { Languages, ArrowRight, Volume2 } from "lucide-react";
import { cn } from "../../../lib/utils";
import type { AgentComponentProps } from "../ComponentRegistry";

interface TranslationResultProps extends AgentComponentProps {
  sourceText: string;
  translatedText: string;
  sourceLanguage: string;
  targetLanguage: string;
  confidence?: number;
  alternatives?: string[];
  notes?: string;
}

const languageNames: Record<string, string> = {
  en: "English",
  ga: "Irish (Gaeilge)",
  cy: "Welsh (Cymraeg)",
  gd: "Scottish Gaelic (Gàidhlig)",
  gv: "Manx (Gaelg)",
};

export default function TranslationResult({
  sourceText,
  translatedText,
  sourceLanguage,
  targetLanguage,
  confidence,
  alternatives,
  notes,
}: TranslationResultProps) {
  const sourceName = languageNames[sourceLanguage] || sourceLanguage;
  const targetName = languageNames[targetLanguage] || targetLanguage;

  return (
    <div className="rounded-lg border bg-card shadow-sm">
      {/* Header */}
      <div className="flex items-center gap-2 p-3 border-b bg-muted/50">
        <Languages className="h-4 w-4 text-primary" />
        <span className="text-sm font-medium">{sourceName}</span>
        <ArrowRight className="h-3 w-3 text-muted-foreground" />
        <span className="text-sm font-medium">{targetName}</span>
        {confidence !== undefined && (
          <span
            className={cn(
              "ml-auto text-xs px-2 py-0.5 rounded",
              confidence >= 0.9
                ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300"
                : confidence >= 0.7
                  ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300"
                  : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300"
            )}
          >
            {Math.round(confidence * 100)}% confidence
          </span>
        )}
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* Source */}
        <div className="space-y-1">
          <p className="text-xs text-muted-foreground uppercase tracking-wider">
            Source
          </p>
          <p className="text-sm">{sourceText}</p>
        </div>

        {/* Translation */}
        <div className="space-y-1">
          <p className="text-xs text-muted-foreground uppercase tracking-wider">
            Translation
          </p>
          <p className="text-sm font-medium">{translatedText}</p>
        </div>

        {/* Alternatives */}
        {alternatives && alternatives.length > 0 && (
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wider">
              Alternatives
            </p>
            <ul className="text-sm space-y-1">
              {alternatives.map((alt, index) => (
                <li key={index} className="text-muted-foreground">
                  • {alt}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Notes */}
        {notes && (
          <div className="pt-2 border-t">
            <p className="text-xs text-muted-foreground italic">{notes}</p>
          </div>
        )}
      </div>
    </div>
  );
}
