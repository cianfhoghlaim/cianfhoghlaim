/**
 * CurriculumCard - Generative UI Component.
 *
 * Displays curriculum content (learning outcomes, subjects, strands)
 * with bilingual support (English/Irish).
 */

import { useState } from "react";
import {
  BookOpen,
  Target,
  ChevronRight,
  Volume2,
  ExternalLink,
  X,
  Layers,
} from "lucide-react";

// ============================================================================
// Types
// ============================================================================

export interface CurriculumCardProps {
  /** Unique ID from AG-UI event */
  componentId?: string;
  /** Callback to dismiss the card */
  onDismiss?: () => void;

  /** Title in English */
  titleEn: string;
  /** Title in Irish (optional) */
  titleGa?: string;
  /** Description/content in English */
  descriptionEn: string;
  /** Description/content in Irish (optional) */
  descriptionGa?: string;
  /** Type of content */
  type: "learning_outcome" | "strand" | "unit" | "subject" | "topic";
  /** Education level */
  level?: "primary" | "junior_cycle" | "senior_cycle";
  /** Subject name */
  subject?: string;
  /** Learning outcome code (e.g., "LO1.2.3") */
  code?: string;
  /** Key skills associated */
  keySkills?: string[];
  /** Document link */
  documentUrl?: string;
  /** Callback for pronunciation */
  onPronounce?: (text: string) => void;
  /** Callback for viewing full document */
  onViewDocument?: () => void;
}

// ============================================================================
// Component
// ============================================================================

export function CurriculumCard({
  componentId,
  onDismiss,
  titleEn,
  titleGa,
  descriptionEn,
  descriptionGa,
  type,
  level,
  subject,
  code,
  keySkills = [],
  documentUrl,
  onPronounce,
  onViewDocument,
}: CurriculumCardProps) {
  const [showIrish, setShowIrish] = useState(false);

  const typeConfig = {
    learning_outcome: {
      icon: Target,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
      borderColor: "border-blue-200",
      label: "Learning Outcome",
    },
    strand: {
      icon: Layers,
      color: "text-orange-600",
      bgColor: "bg-orange-50",
      borderColor: "border-orange-200",
      label: "Strand",
    },
    unit: {
      icon: BookOpen,
      color: "text-green-600",
      bgColor: "bg-green-50",
      borderColor: "border-green-200",
      label: "Unit",
    },
    subject: {
      icon: BookOpen,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
      borderColor: "border-purple-200",
      label: "Subject",
    },
    topic: {
      icon: ChevronRight,
      color: "text-gray-600",
      bgColor: "bg-gray-50",
      borderColor: "border-gray-200",
      label: "Topic",
    },
  };

  const config = typeConfig[type];
  const IconComponent = config.icon;

  const levelLabels: Record<string, { label: string; color: string }> = {
    primary: { label: "Primary", color: "bg-yellow-100 text-yellow-800" },
    junior_cycle: { label: "Junior Cycle", color: "bg-blue-100 text-blue-800" },
    senior_cycle: { label: "Senior Cycle", color: "bg-purple-100 text-purple-800" },
  };

  const displayTitle = showIrish && titleGa ? titleGa : titleEn;
  const displayDescription = showIrish && descriptionGa ? descriptionGa : descriptionEn;

  return (
    <div
      className={`rounded-lg border ${config.borderColor} ${config.bgColor} shadow-sm overflow-hidden`}
      data-component-id={componentId}
    >
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 bg-white/50">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <div
              className={`w-10 h-10 rounded-lg flex items-center justify-center ${config.bgColor}`}
            >
              <IconComponent className={`h-5 w-5 ${config.color}`} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className={`text-xs px-2 py-0.5 rounded ${config.bgColor} ${config.color}`}>
                  {config.label}
                </span>
                {code && (
                  <span className="text-xs font-mono text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                    {code}
                  </span>
                )}
                {level && levelLabels[level] && (
                  <span
                    className={`text-xs px-2 py-0.5 rounded ${levelLabels[level].color}`}
                  >
                    {levelLabels[level].label}
                  </span>
                )}
              </div>
              <h3 className="font-medium text-gray-900 mt-1 truncate">
                {displayTitle}
              </h3>
              {showIrish && titleGa && (
                <p className="text-sm text-gray-500 truncate">{titleEn}</p>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-1">
            {/* Language toggle */}
            {titleGa && (
              <button
                onClick={() => setShowIrish(!showIrish)}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  showIrish
                    ? "bg-green-100 text-green-700"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
                title={showIrish ? "Show English" : "Show Irish"}
              >
                {showIrish ? "GA" : "EN"}
              </button>
            )}

            {/* Pronounce button */}
            {onPronounce && titleGa && (
              <button
                onClick={() => onPronounce(showIrish ? titleGa : titleEn)}
                className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                title="Pronounce"
              >
                <Volume2 className="h-4 w-4" />
              </button>
            )}

            {/* Dismiss button */}
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                title="Dismiss"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="px-4 py-3">
        <p className="text-gray-700 text-sm leading-relaxed">
          {displayDescription}
        </p>
        {showIrish && descriptionGa && (
          <p className="text-gray-500 text-sm mt-2 leading-relaxed">
            {descriptionEn}
          </p>
        )}

        {/* Key Skills */}
        {keySkills.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {keySkills.map((skill) => (
              <span
                key={skill}
                className="text-xs bg-white border border-gray-200 text-gray-600 px-2 py-0.5 rounded"
              >
                {skill}
              </span>
            ))}
          </div>
        )}

        {/* Subject badge */}
        {subject && (
          <div className="mt-3">
            <span className="text-xs text-gray-500">Subject: </span>
            <span className="text-xs font-medium text-gray-700">{subject}</span>
          </div>
        )}
      </div>

      {/* Footer with actions */}
      {(documentUrl || onViewDocument) && (
        <div className="px-4 py-2 border-t border-gray-200 bg-white/50">
          <button
            onClick={onViewDocument}
            className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800 transition-colors"
          >
            <ExternalLink className="h-4 w-4" />
            View full document
          </button>
        </div>
      )}
    </div>
  );
}

export default CurriculumCard;
