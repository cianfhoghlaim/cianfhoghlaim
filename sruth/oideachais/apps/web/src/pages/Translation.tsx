import { useState } from "react";
import { Languages, Check, X, RefreshCw, AlertCircle, Clock, CheckCircle } from "lucide-react";
import { toast } from "sonner";
import { cn } from "../lib/utils";

interface TranslationRequest {
  id: string;
  source_text: string;
  source_language: string;
  target_language: string;
  ai_translation: string;
  confidence: number;
  context: string;
  status: "pending" | "approved" | "rejected" | "revised";
  created_at: string;
}

const LANGUAGE_NAMES: Record<string, string> = {
  en: "English",
  ga: "Irish (Gaeilge)",
  cy: "Welsh (Cymraeg)",
  gd: "Scottish Gaelic (Gàidhlig)",
  gv: "Manx (Gaelg)",
};

// Mock translation data
const MOCK_TRANSLATIONS: TranslationRequest[] = [
  {
    id: "trans-001",
    source_text: "Students will be able to solve quadratic equations using the quadratic formula.",
    source_language: "en",
    target_language: "ga",
    ai_translation: "Beidh scoláirí in ann cothromóidí cearnógacha a réiteach ag úsáid an fhoirmle chearnógaigh.",
    confidence: 0.87,
    context: "Junior Cycle Mathematics - Algebra Strand",
    status: "pending",
    created_at: new Date().toISOString(),
  },
  {
    id: "trans-002",
    source_text: "Analyse the causes and consequences of World War I.",
    source_language: "en",
    target_language: "cy",
    ai_translation: "Dadansoddi achosion a chanlyniadau'r Rhyfel Byd Cyntaf.",
    confidence: 0.92,
    context: "GCSE History - Modern World",
    status: "pending",
    created_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: "trans-003",
    source_text: "Demonstrate understanding of photosynthesis and cellular respiration.",
    source_language: "en",
    target_language: "gd",
    ai_translation: "Seall tuigse air foto-synthesis agus analachadh ceallach.",
    confidence: 0.78,
    context: "Scottish Highers - Biology",
    status: "pending",
    created_at: new Date(Date.now() - 7200000).toISOString(),
  },
];

export default function TranslationPage() {
  const [translations, setTranslations] = useState<TranslationRequest[]>(MOCK_TRANSLATIONS);
  const [selectedTranslation, setSelectedTranslation] = useState<TranslationRequest | null>(null);
  const [editedTranslation, setEditedTranslation] = useState("");
  const [filter, setFilter] = useState<"all" | "pending" | "approved" | "rejected">("pending");

  const filteredTranslations = translations.filter(
    (t) => filter === "all" || t.status === filter
  );

  const handleSelect = (translation: TranslationRequest) => {
    setSelectedTranslation(translation);
    setEditedTranslation(translation.ai_translation);
  };

  const handleApprove = () => {
    if (!selectedTranslation) return;

    setTranslations((prev) =>
      prev.map((t) =>
        t.id === selectedTranslation.id
          ? { ...t, status: "approved" as const, ai_translation: editedTranslation }
          : t
      )
    );
    toast.success("Translation approved");
    setSelectedTranslation(null);
  };

  const handleReject = () => {
    if (!selectedTranslation) return;

    setTranslations((prev) =>
      prev.map((t) =>
        t.id === selectedTranslation.id ? { ...t, status: "rejected" as const } : t
      )
    );
    toast.info("Translation rejected - will be queued for re-translation");
    setSelectedTranslation(null);
  };

  const handleRetranslate = () => {
    if (!selectedTranslation) return;
    toast.info("Requesting new translation...");
    // Would trigger new AI translation here
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return "text-green-600";
    if (confidence >= 0.8) return "text-yellow-600";
    return "text-red-600";
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "approved":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "rejected":
        return <X className="h-4 w-4 text-red-600" />;
      case "revised":
        return <RefreshCw className="h-4 w-4 text-blue-600" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-600" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Languages className="h-6 w-6" />
          Translation Review
        </h1>
        <p className="text-muted-foreground">
          Review and approve AI translations for Celtic languages
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Pending", count: translations.filter((t) => t.status === "pending").length, status: "pending" },
          { label: "Approved", count: translations.filter((t) => t.status === "approved").length, status: "approved" },
          { label: "Rejected", count: translations.filter((t) => t.status === "rejected").length, status: "rejected" },
          { label: "Total", count: translations.length, status: "all" },
        ].map((stat) => (
          <button
            key={stat.label}
            onClick={() => setFilter(stat.status as typeof filter)}
            className={cn(
              "rounded-lg border p-4 text-center transition-colors",
              filter === stat.status
                ? "border-primary bg-primary/5"
                : "hover:bg-muted"
            )}
          >
            <div className="text-2xl font-bold">{stat.count}</div>
            <div className="text-sm text-muted-foreground">{stat.label}</div>
          </button>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Translation List */}
        <div className="space-y-4">
          <h2 className="font-semibold">Translation Queue</h2>
          <div className="space-y-2">
            {filteredTranslations.length === 0 ? (
              <div className="rounded-lg border bg-muted/50 p-8 text-center">
                <Languages className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
                <p className="text-muted-foreground">No translations to review</p>
              </div>
            ) : (
              filteredTranslations.map((translation) => (
                <button
                  key={translation.id}
                  onClick={() => handleSelect(translation)}
                  className={cn(
                    "w-full text-left rounded-lg border p-4 transition-colors",
                    selectedTranslation?.id === translation.id
                      ? "border-primary bg-primary/5"
                      : "hover:bg-muted"
                  )}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs bg-muted px-2 py-0.5 rounded">
                          {LANGUAGE_NAMES[translation.source_language]} →{" "}
                          {LANGUAGE_NAMES[translation.target_language]}
                        </span>
                        {getStatusIcon(translation.status)}
                      </div>
                      <p className="text-sm line-clamp-2">{translation.source_text}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {translation.context}
                      </p>
                    </div>
                    <div
                      className={cn(
                        "text-sm font-medium",
                        getConfidenceColor(translation.confidence)
                      )}
                    >
                      {Math.round(translation.confidence * 100)}%
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Review Panel */}
        <div className="space-y-4">
          <h2 className="font-semibold">Review Panel</h2>
          {selectedTranslation ? (
            <div className="rounded-lg border bg-card p-6 space-y-4">
              {/* Source */}
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Source ({LANGUAGE_NAMES[selectedTranslation.source_language]})
                </label>
                <p className="mt-1 p-3 rounded-md bg-muted">
                  {selectedTranslation.source_text}
                </p>
              </div>

              {/* Context */}
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Context
                </label>
                <p className="mt-1 text-sm">{selectedTranslation.context}</p>
              </div>

              {/* AI Translation (editable) */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-sm font-medium text-muted-foreground">
                    AI Translation ({LANGUAGE_NAMES[selectedTranslation.target_language]})
                  </label>
                  <span
                    className={cn(
                      "text-sm",
                      getConfidenceColor(selectedTranslation.confidence)
                    )}
                  >
                    Confidence: {Math.round(selectedTranslation.confidence * 100)}%
                  </span>
                </div>
                <textarea
                  value={editedTranslation}
                  onChange={(e) => setEditedTranslation(e.target.value)}
                  rows={4}
                  className={cn(
                    "w-full rounded-md border border-input bg-background px-3 py-2 text-sm",
                    "focus:outline-none focus:ring-2 focus:ring-ring"
                  )}
                />
              </div>

              {/* Confidence Warning */}
              {selectedTranslation.confidence < 0.8 && (
                <div className="flex items-start gap-2 rounded-md bg-yellow-50 dark:bg-yellow-900/20 p-3">
                  <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0" />
                  <div className="text-sm">
                    <p className="font-medium text-yellow-800 dark:text-yellow-200">
                      Low Confidence Translation
                    </p>
                    <p className="text-yellow-700 dark:text-yellow-300">
                      This translation has a confidence score below 80%. Please review carefully.
                    </p>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2 pt-2">
                <button
                  onClick={handleApprove}
                  className={cn(
                    "flex-1 inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium",
                    "bg-green-600 text-white hover:bg-green-700",
                    "h-10 px-4"
                  )}
                >
                  <Check className="h-4 w-4" />
                  Approve
                </button>
                <button
                  onClick={handleReject}
                  className={cn(
                    "flex-1 inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium",
                    "bg-red-600 text-white hover:bg-red-700",
                    "h-10 px-4"
                  )}
                >
                  <X className="h-4 w-4" />
                  Reject
                </button>
                <button
                  onClick={handleRetranslate}
                  className={cn(
                    "inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium",
                    "border border-input bg-background hover:bg-accent",
                    "h-10 px-4"
                  )}
                >
                  <RefreshCw className="h-4 w-4" />
                </button>
              </div>
            </div>
          ) : (
            <div className="rounded-lg border bg-muted/50 p-8 text-center">
              <Languages className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
              <p className="text-muted-foreground">
                Select a translation from the queue to review
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
