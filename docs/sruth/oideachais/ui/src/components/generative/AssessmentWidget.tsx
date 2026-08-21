/**
 * AssessmentWidget - Generative UI Component.
 *
 * Interactive practice questions for curriculum assessment.
 * Supports multiple question types: multiple choice, fill-in-blank, matching.
 */

import { useState, useCallback } from "react";
import {
  CheckCircle2,
  XCircle,
  HelpCircle,
  ChevronRight,
  RotateCcw,
  X,
  Lightbulb,
} from "lucide-react";

// ============================================================================
// Types
// ============================================================================

export type QuestionType = "multiple_choice" | "fill_blank" | "matching" | "true_false";

export interface QuestionOption {
  id: string;
  text: string;
  textGa?: string;
  isCorrect: boolean;
}

export interface Question {
  id: string;
  type: QuestionType;
  questionEn: string;
  questionGa?: string;
  options?: QuestionOption[];
  correctAnswer?: string;
  hint?: string;
  explanation?: string;
  points?: number;
}

export interface AssessmentWidgetProps {
  /** Unique ID from AG-UI event */
  componentId?: string;
  /** Callback to dismiss the widget */
  onDismiss?: () => void;

  /** Question to display */
  question: Question;
  /** Topic/subject context */
  topic?: string;
  /** Learning outcome code */
  learningOutcome?: string;
  /** Show Irish version */
  showIrish?: boolean;
  /** Callback when answer is submitted */
  onAnswer?: (questionId: string, answer: string, isCorrect: boolean) => void;
  /** Callback when user requests hint */
  onHintRequest?: (questionId: string) => void;
  /** Callback for next question */
  onNext?: () => void;
}

// ============================================================================
// Component
// ============================================================================

export function AssessmentWidget({
  componentId,
  onDismiss,
  question,
  topic,
  learningOutcome,
  showIrish = false,
  onAnswer,
  onHintRequest,
  onNext,
}: AssessmentWidgetProps) {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [showHint, setShowHint] = useState(false);
  const [fillBlankAnswer, setFillBlankAnswer] = useState("");

  const questionText = showIrish && question.questionGa
    ? question.questionGa
    : question.questionEn;

  const handleSelectOption = useCallback((optionId: string) => {
    if (!isSubmitted) {
      setSelectedAnswer(optionId);
    }
  }, [isSubmitted]);

  const handleSubmit = useCallback(() => {
    if (!selectedAnswer && question.type !== "fill_blank") return;
    if (question.type === "fill_blank" && !fillBlankAnswer) return;

    let correct = false;
    const answer = question.type === "fill_blank" ? fillBlankAnswer : selectedAnswer;

    if (question.type === "multiple_choice" || question.type === "true_false") {
      const selectedOption = question.options?.find((o) => o.id === selectedAnswer);
      correct = selectedOption?.isCorrect ?? false;
    } else if (question.type === "fill_blank") {
      correct = fillBlankAnswer.toLowerCase().trim() ===
        (question.correctAnswer?.toLowerCase().trim() ?? "");
    }

    setIsCorrect(correct);
    setIsSubmitted(true);
    onAnswer?.(question.id, answer!, correct);
  }, [selectedAnswer, fillBlankAnswer, question, onAnswer]);

  const handleReset = useCallback(() => {
    setSelectedAnswer(null);
    setIsSubmitted(false);
    setIsCorrect(null);
    setShowHint(false);
    setFillBlankAnswer("");
  }, []);

  const handleShowHint = useCallback(() => {
    setShowHint(true);
    onHintRequest?.(question.id);
  }, [question.id, onHintRequest]);

  return (
    <div
      className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden"
      data-component-id={componentId}
    >
      {/* Header */}
      <div className="px-4 py-3 border-b bg-gradient-to-r from-indigo-50 to-purple-50">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
              <HelpCircle className="h-5 w-5 text-indigo-600" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs px-2 py-0.5 rounded bg-indigo-100 text-indigo-700">
                  Practice Question
                </span>
                {question.points && (
                  <span className="text-xs text-gray-500">
                    {question.points} points
                  </span>
                )}
              </div>
              {topic && (
                <p className="text-xs text-gray-500 mt-1">{topic}</p>
              )}
              {learningOutcome && (
                <p className="text-xs font-mono text-gray-400 mt-0.5">
                  {learningOutcome}
                </p>
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

      {/* Question */}
      <div className="px-4 py-4">
        <p className="text-gray-800 font-medium">{questionText}</p>
        {showIrish && question.questionGa && (
          <p className="text-sm text-gray-500 mt-1">{question.questionEn}</p>
        )}
      </div>

      {/* Answer Area */}
      <div className="px-4 pb-4">
        {/* Multiple Choice / True-False */}
        {(question.type === "multiple_choice" || question.type === "true_false") &&
          question.options && (
            <div className="space-y-2">
              {question.options.map((option) => {
                const isSelected = selectedAnswer === option.id;
                const showResult = isSubmitted && isSelected;

                return (
                  <button
                    key={option.id}
                    onClick={() => handleSelectOption(option.id)}
                    disabled={isSubmitted}
                    className={`w-full p-3 rounded-lg border text-left transition-all ${
                      isSubmitted
                        ? isSelected
                          ? option.isCorrect
                            ? "border-green-500 bg-green-50"
                            : "border-red-500 bg-red-50"
                          : option.isCorrect
                          ? "border-green-300 bg-green-50/50"
                          : "border-gray-200 bg-gray-50"
                        : isSelected
                        ? "border-indigo-500 bg-indigo-50"
                        : "border-gray-200 hover:border-indigo-300 hover:bg-indigo-50/50"
                    } ${isSubmitted ? "cursor-default" : "cursor-pointer"}`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                          isSubmitted && option.isCorrect
                            ? "border-green-500 bg-green-500"
                            : isSubmitted && isSelected && !option.isCorrect
                            ? "border-red-500 bg-red-500"
                            : isSelected
                            ? "border-indigo-500 bg-indigo-500"
                            : "border-gray-300"
                        }`}
                      >
                        {showResult && (
                          option.isCorrect ? (
                            <CheckCircle2 className="h-3 w-3 text-white" />
                          ) : (
                            <XCircle className="h-3 w-3 text-white" />
                          )
                        )}
                      </div>
                      <span className="text-sm text-gray-700">
                        {showIrish && option.textGa ? option.textGa : option.text}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          )}

        {/* Fill in the Blank */}
        {question.type === "fill_blank" && (
          <div>
            <input
              type="text"
              value={fillBlankAnswer}
              onChange={(e) => setFillBlankAnswer(e.target.value)}
              disabled={isSubmitted}
              placeholder="Type your answer..."
              className={`w-full px-4 py-3 rounded-lg border text-sm transition-colors ${
                isSubmitted
                  ? isCorrect
                    ? "border-green-500 bg-green-50"
                    : "border-red-500 bg-red-50"
                  : "border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200"
              }`}
            />
            {isSubmitted && !isCorrect && question.correctAnswer && (
              <p className="text-sm text-green-600 mt-2">
                Correct answer: <strong>{question.correctAnswer}</strong>
              </p>
            )}
          </div>
        )}
      </div>

      {/* Hint */}
      {question.hint && !isSubmitted && (
        <div className="px-4 pb-3">
          {showHint ? (
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <div className="flex items-start gap-2">
                <Lightbulb className="h-4 w-4 text-amber-600 mt-0.5" />
                <p className="text-sm text-amber-800">{question.hint}</p>
              </div>
            </div>
          ) : (
            <button
              onClick={handleShowHint}
              className="text-sm text-amber-600 hover:text-amber-700 flex items-center gap-1"
            >
              <Lightbulb className="h-4 w-4" />
              Show hint
            </button>
          )}
        </div>
      )}

      {/* Explanation (after submission) */}
      {isSubmitted && question.explanation && (
        <div className="px-4 pb-4">
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">{question.explanation}</p>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="px-4 py-3 border-t bg-gray-50 flex items-center justify-between">
        {!isSubmitted ? (
          <>
            <button
              onClick={handleReset}
              className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
            >
              <RotateCcw className="h-4 w-4" />
              Reset
            </button>
            <button
              onClick={handleSubmit}
              disabled={!selectedAnswer && !fillBlankAnswer}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedAnswer || fillBlankAnswer
                  ? "bg-indigo-600 text-white hover:bg-indigo-700"
                  : "bg-gray-200 text-gray-400 cursor-not-allowed"
              }`}
            >
              Submit Answer
            </button>
          </>
        ) : (
          <>
            <div className="flex items-center gap-2">
              {isCorrect ? (
                <>
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  <span className="text-sm font-medium text-green-700">
                    Correct!
                  </span>
                </>
              ) : (
                <>
                  <XCircle className="h-5 w-5 text-red-600" />
                  <span className="text-sm font-medium text-red-700">
                    Incorrect
                  </span>
                </>
              )}
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleReset}
                className="px-3 py-2 text-sm text-gray-600 hover:text-gray-800"
              >
                Try Again
              </button>
              {onNext && (
                <button
                  onClick={onNext}
                  className="px-4 py-2 rounded-lg text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-700 flex items-center gap-1"
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default AssessmentWidget;
