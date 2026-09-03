import { useState, useCallback } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useMutation } from "convex/react";
import { api } from "@convex/_generated/api";
import { FileUpload } from "~/components/comparison/FileUpload";
import { ModelSelector } from "~/components/comparison/ModelSelector";
import { ArrowRight, Play, FileText } from "lucide-react";

export const Route = createFileRoute("/compare/")({
  component: ComparePage,
});

function ComparePage() {
  const navigate = useNavigate();
  const createTask = useMutation(api.tasks.create);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [outputFormat, setOutputFormat] = useState<"markdown" | "json" | "text">(
    "markdown"
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFileSelect = useCallback((file: File) => {
    setSelectedFile(file);
  }, []);

  const handleClearFile = useCallback(() => {
    setSelectedFile(null);
  }, []);

  const handleStartComparison = async () => {
    if (!selectedFile || selectedModels.length === 0) return;

    setIsSubmitting(true);
    try {
      // Create the task
      const taskId = await createTask({
        filename: selectedFile.name,
        fileSize: selectedFile.size,
        outputFormat,
        selectedModels,
      });

      // Navigate to the task page
      navigate({ to: "/compare/$taskId", params: { taskId } });
    } catch (error) {
      console.error("Failed to create comparison:", error);
      setIsSubmitting(false);
    }
  };

  const canSubmit = selectedFile && selectedModels.length > 0 && !isSubmitting;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          New Comparison
        </h1>
        <p className="mt-1 text-slate-600 dark:text-slate-400">
          Upload a PDF and select models to compare their OCR results side-by-side
        </p>
      </div>

      {/* Step 1: File Upload */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <div className="mb-4 flex items-center gap-2">
          <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-600 dark:bg-blue-900/50 dark:text-blue-400">
            1
          </span>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
            Upload PDF
          </h2>
        </div>
        <FileUpload
          onFileSelect={handleFileSelect}
          selectedFile={selectedFile}
          onClear={handleClearFile}
        />
      </div>

      {/* Step 2: Model Selection */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <div className="mb-4 flex items-center gap-2">
          <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-600 dark:bg-blue-900/50 dark:text-blue-400">
            2
          </span>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
            Select Models
          </h2>
        </div>
        <ModelSelector
          selectedModels={selectedModels}
          onSelectionChange={setSelectedModels}
          maxSelection={3}
        />
      </div>

      {/* Step 3: Output Format */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <div className="mb-4 flex items-center gap-2">
          <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-600 dark:bg-blue-900/50 dark:text-blue-400">
            3
          </span>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
            Output Format
          </h2>
        </div>
        <div className="flex gap-3">
          {(["markdown", "json", "text"] as const).map((format) => (
            <button
              key={format}
              onClick={() => setOutputFormat(format)}
              className={`flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition-all ${
                outputFormat === format
                  ? "border-blue-500 bg-blue-50 text-blue-700 dark:border-blue-400 dark:bg-blue-950/30 dark:text-blue-300"
                  : "border-slate-200 text-slate-600 hover:border-slate-300 dark:border-slate-700 dark:text-slate-400"
              }`}
            >
              <FileText className="h-4 w-4" />
              {format.charAt(0).toUpperCase() + format.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Summary & Submit */}
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-6 dark:border-slate-700 dark:bg-slate-800/50">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-slate-900 dark:text-white">
              Ready to Compare
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {selectedFile
                ? `${selectedFile.name} • ${selectedModels.length} model${selectedModels.length !== 1 ? "s" : ""} selected`
                : "Upload a PDF and select models to continue"}
            </p>
          </div>
          <button
            onClick={handleStartComparison}
            disabled={!canSubmit}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSubmitting ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Starting...
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                Start Comparison
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
