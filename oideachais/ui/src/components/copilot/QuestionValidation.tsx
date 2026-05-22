/**
 * Human-in-the-Loop (HITL) Validation Component for CopilotKit.
 *
 * Provides validation UI for:
 * - Irish language translations
 * - Curriculum alignment verification
 * - Difficulty level assessment
 */

import { useState, useCallback } from "react";
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Languages,
  BookOpen,
  BarChart2,
  ChevronDown,
  ChevronUp,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
} from "lucide-react";

// ============================================================================
// Types
// ============================================================================

export type ValidationType =
  | "irish_language"
  | "curriculum_alignment"
  | "difficulty"
  | "content_accuracy";

export type ValidationStatus = "pending" | "approved" | "rejected" | "revised";

export interface ValidationItem {
  id: string;
  type: ValidationType;
  originalContent: string;
  generatedContent: string;
  context?: {
    subject?: string;
    educationLevel?: string;
    learningOutcome?: string;
    strandUnit?: string;
  };
  metadata?: Record<string, unknown>;
}

export interface ValidationResult {
  itemId: string;
  status: ValidationStatus;
  feedback?: string;
  corrections?: string;
  timestamp: string;
  validatorId?: string;
}

export interface QuestionValidationProps {
  item: ValidationItem;
  onValidate: (result: ValidationResult) => void;
  onSkip?: () => void;
  isLoading?: boolean;
}

// ============================================================================
// Validation Type Configuration
// ============================================================================

const validationTypeConfig: Record<
  ValidationType,
  {
    label: string;
    icon: typeof Languages;
    description: string;
    color: string;
    criteria: string[];
  }
> = {
  irish_language: {
    label: "Irish Language",
    icon: Languages,
    description: "Verify Irish translation accuracy and natural phrasing",
    color: "bg-green-100 text-green-800",
    criteria: [
      "Grammar is correct (including mutations)",
      "Natural phrasing (not literal translation)",
      "Appropriate dialect/register",
      "Technical terms are correctly translated",
      "Spelling follows standard Irish",
    ],
  },
  curriculum_alignment: {
    label: "Curriculum Alignment",
    icon: BookOpen,
    description: "Verify content aligns with learning outcomes",
    color: "bg-blue-100 text-blue-800",
    criteria: [
      "Addresses the specified learning outcome",
      "Appropriate for the education level",
      "Covers required skills/knowledge",
      "Matches strand unit context",
      "Follows curriculum specification guidelines",
    ],
  },
  difficulty: {
    label: "Difficulty Level",
    icon: BarChart2,
    description: "Assess question difficulty appropriateness",
    color: "bg-purple-100 text-purple-800",
    criteria: [
      "Matches intended difficulty level",
      "Cognitive demand is appropriate",
      "Prerequisites are reasonable",
      "Time allocation is realistic",
      "Accessible to target audience",
    ],
  },
  content_accuracy: {
    label: "Content Accuracy",
    icon: CheckCircle,
    description: "Verify factual accuracy of generated content",
    color: "bg-orange-100 text-orange-800",
    criteria: [
      "Facts are accurate and up-to-date",
      "No misleading information",
      "Sources are credible",
      "Examples are appropriate",
      "No contradictions with curriculum",
    ],
  },
};

// ============================================================================
// Main Component
// ============================================================================

export function QuestionValidation({
  item,
  onValidate,
  onSkip,
  isLoading = false,
}: QuestionValidationProps) {
  const [status, setStatus] = useState<ValidationStatus>("pending");
  const [feedback, setFeedback] = useState("");
  const [corrections, setCorrections] = useState("");
  const [showCriteria, setShowCriteria] = useState(true);
  const [criteriaChecked, setCriteriaChecked] = useState<Record<number, boolean>>({});

  const config = validationTypeConfig[item.type];
  const IconComponent = config.icon;

  const handleSubmit = useCallback(
    (finalStatus: ValidationStatus) => {
      const result: ValidationResult = {
        itemId: item.id,
        status: finalStatus,
        feedback: feedback || undefined,
        corrections: corrections || undefined,
        timestamp: new Date().toISOString(),
      };
      onValidate(result);
    },
    [item.id, feedback, corrections, onValidate]
  );

  const allCriteriaChecked =
    config.criteria.length > 0 &&
    config.criteria.every((_, i) => criteriaChecked[i]);

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className={`px-4 py-3 ${config.color} border-b`}>
        <div className="flex items-center gap-2">
          <IconComponent className="h-5 w-5" />
          <span className="font-medium">{config.label} Validation</span>
        </div>
        <p className="text-sm opacity-80 mt-1">{config.description}</p>
      </div>

      {/* Context */}
      {item.context && (
        <div className="px-4 py-3 bg-gray-50 border-b text-sm">
          <div className="flex flex-wrap gap-4">
            {item.context.subject && (
              <span className="text-gray-600">
                <strong>Subject:</strong> {item.context.subject}
              </span>
            )}
            {item.context.educationLevel && (
              <span className="text-gray-600">
                <strong>Level:</strong>{" "}
                {item.context.educationLevel.replace(/_/g, " ")}
              </span>
            )}
            {item.context.learningOutcome && (
              <span className="text-gray-600">
                <strong>LO:</strong> {item.context.learningOutcome}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Content Comparison */}
      <div className="p-4 space-y-4">
        {/* Original Content */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            Original Content
          </h4>
          <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-800 whitespace-pre-wrap">
            {item.originalContent}
          </div>
        </div>

        {/* Generated Content */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            Generated Content
          </h4>
          <div className="bg-blue-50 rounded-lg p-3 text-sm text-gray-800 whitespace-pre-wrap border border-blue-200">
            {item.generatedContent}
          </div>
        </div>
      </div>

      {/* Validation Criteria */}
      <div className="border-t">
        <button
          onClick={() => setShowCriteria(!showCriteria)}
          className="w-full px-4 py-3 flex items-center justify-between text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          <span>Validation Criteria</span>
          {showCriteria ? (
            <ChevronUp className="h-4 w-4" />
          ) : (
            <ChevronDown className="h-4 w-4" />
          )}
        </button>

        {showCriteria && (
          <div className="px-4 pb-4 space-y-2">
            {config.criteria.map((criterion, index) => (
              <label
                key={index}
                className="flex items-start gap-3 p-2 rounded hover:bg-gray-50 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={criteriaChecked[index] || false}
                  onChange={(e) =>
                    setCriteriaChecked((prev) => ({
                      ...prev,
                      [index]: e.target.checked,
                    }))
                  }
                  className="mt-0.5 h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">{criterion}</span>
              </label>
            ))}
          </div>
        )}
      </div>

      {/* Feedback Section */}
      <div className="border-t p-4 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <MessageSquare className="h-4 w-4 inline mr-1" />
            Feedback (optional)
          </label>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Provide feedback on the generated content..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={3}
          />
        </div>

        {status === "revised" && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <AlertTriangle className="h-4 w-4 inline mr-1 text-yellow-500" />
              Corrections
            </label>
            <textarea
              value={corrections}
              onChange={(e) => setCorrections(e.target.value)}
              placeholder="Provide the corrected version..."
              className="w-full px-3 py-2 border border-yellow-300 rounded-lg text-sm focus:ring-2 focus:ring-yellow-500 focus:border-transparent resize-none bg-yellow-50"
              rows={4}
            />
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="border-t p-4 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {onSkip && (
              <button
                onClick={onSkip}
                disabled={isLoading}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
              >
                Skip
              </button>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setStatus("revised");
              }}
              disabled={isLoading}
              className="px-4 py-2 text-sm bg-yellow-100 text-yellow-800 hover:bg-yellow-200 rounded-lg transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <AlertTriangle className="h-4 w-4" />
              Needs Revision
            </button>

            <button
              onClick={() => handleSubmit("rejected")}
              disabled={isLoading}
              className="px-4 py-2 text-sm bg-red-100 text-red-800 hover:bg-red-200 rounded-lg transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <ThumbsDown className="h-4 w-4" />
              Reject
            </button>

            <button
              onClick={() => handleSubmit(status === "revised" ? "revised" : "approved")}
              disabled={isLoading || (status !== "revised" && !allCriteriaChecked)}
              className="px-4 py-2 text-sm bg-green-600 text-white hover:bg-green-700 rounded-lg transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {status === "revised" ? (
                <>
                  <CheckCircle className="h-4 w-4" />
                  Submit Revision
                </>
              ) : (
                <>
                  <ThumbsUp className="h-4 w-4" />
                  Approve
                </>
              )}
            </button>
          </div>
        </div>

        {!allCriteriaChecked && status !== "revised" && (
          <p className="text-xs text-gray-500 mt-2 text-right">
            Check all criteria to approve
          </p>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// Validation Queue Component
// ============================================================================

export interface ValidationQueueProps {
  items: ValidationItem[];
  onValidate: (result: ValidationResult) => void;
  onComplete?: () => void;
}

export function ValidationQueue({
  items,
  onValidate,
  onComplete,
}: ValidationQueueProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [results, setResults] = useState<ValidationResult[]>([]);

  const handleValidate = useCallback(
    (result: ValidationResult) => {
      setResults((prev) => [...prev, result]);
      onValidate(result);

      if (currentIndex < items.length - 1) {
        setCurrentIndex((prev) => prev + 1);
      } else {
        onComplete?.();
      }
    },
    [currentIndex, items.length, onValidate, onComplete]
  );

  const handleSkip = useCallback(() => {
    if (currentIndex < items.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    }
  }, [currentIndex, items.length]);

  if (items.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900">All Done!</h3>
        <p className="text-gray-500 mt-2">No items pending validation.</p>
      </div>
    );
  }

  const currentItem = items[currentIndex];

  return (
    <div className="space-y-4">
      {/* Progress */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            Validation Progress
          </span>
          <span className="text-sm text-gray-500">
            {currentIndex + 1} of {items.length}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{
              width: `${((currentIndex + 1) / items.length) * 100}%`,
            }}
          />
        </div>
        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <CheckCircle className="h-3 w-3 text-green-500" />
            {results.filter((r) => r.status === "approved").length} approved
          </span>
          <span className="flex items-center gap-1">
            <XCircle className="h-3 w-3 text-red-500" />
            {results.filter((r) => r.status === "rejected").length} rejected
          </span>
          <span className="flex items-center gap-1">
            <AlertTriangle className="h-3 w-3 text-yellow-500" />
            {results.filter((r) => r.status === "revised").length} revised
          </span>
        </div>
      </div>

      {/* Current Item */}
      <QuestionValidation
        key={currentItem.id}
        item={currentItem}
        onValidate={handleValidate}
        onSkip={handleSkip}
      />
    </div>
  );
}

// ============================================================================
// Irish Language Specific Validation
// ============================================================================

export interface IrishTranslationValidationProps {
  englishText: string;
  irishText: string;
  context?: {
    subject?: string;
    educationLevel?: string;
    technicalDomain?: string;
  };
  onValidate: (result: ValidationResult & { suggestedTranslation?: string }) => void;
}

export function IrishTranslationValidation({
  englishText,
  irishText,
  context,
  onValidate,
}: IrishTranslationValidationProps) {
  const [suggestedTranslation, setSuggestedTranslation] = useState("");

  const item: ValidationItem = {
    id: `irish-${Date.now()}`,
    type: "irish_language",
    originalContent: englishText,
    generatedContent: irishText,
    context: context
      ? {
          subject: context.subject,
          educationLevel: context.educationLevel,
        }
      : undefined,
    metadata: {
      technicalDomain: context?.technicalDomain,
    },
  };

  const handleValidate = (result: ValidationResult) => {
    onValidate({
      ...result,
      suggestedTranslation: suggestedTranslation || undefined,
    });
  };

  return (
    <div className="space-y-4">
      <QuestionValidation item={item} onValidate={handleValidate} />

      {/* Additional Irish-specific field */}
      <div className="bg-white rounded-lg shadow p-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <Languages className="h-4 w-4 inline mr-1" />
          Suggested Translation (optional)
        </label>
        <textarea
          value={suggestedTranslation}
          onChange={(e) => setSuggestedTranslation(e.target.value)}
          placeholder="If the translation needs correction, provide your suggested version in Irish..."
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
          rows={3}
          dir="ltr"
          lang="ga"
        />
        <p className="text-xs text-gray-500 mt-1">
          Include séimhiú (lenition) and urú (eclipsis) as needed
        </p>
      </div>
    </div>
  );
}

export default QuestionValidation;
