import { useState, useCallback } from "react";
import { Upload, FileText, X, CheckCircle } from "lucide-react";
import { cn } from "~/lib/utils";

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  onClear: () => void;
}

export function FileUpload({
  onFileSelect,
  selectedFile,
  onClear,
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const files = e.dataTransfer.files;
      if (files.length > 0 && files[0].type === "application/pdf") {
        onFileSelect(files[0]);
      }
    },
    [onFileSelect]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (files && files.length > 0 && files[0].type === "application/pdf") {
        onFileSelect(files[0]);
      }
    },
    [onFileSelect]
  );

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={cn(
        "relative rounded-xl border-2 border-dashed p-8 transition-all duration-200",
        isDragging
          ? "border-blue-500 bg-blue-50 dark:bg-blue-950/20"
          : selectedFile
            ? "border-green-400 bg-green-50 dark:border-green-600 dark:bg-green-950/20"
            : "border-slate-300 hover:border-slate-400 dark:border-slate-600 dark:hover:border-slate-500"
      )}
    >
      <input
        type="file"
        accept="application/pdf"
        onChange={handleFileInput}
        className="absolute inset-0 cursor-pointer opacity-0"
        disabled={!!selectedFile}
      />

      {selectedFile ? (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-100 dark:bg-green-900/30">
              <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="font-medium text-slate-900 dark:text-white">
                {selectedFile.name}
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {formatFileSize(selectedFile.size)}
              </p>
            </div>
          </div>
          <button
            onClick={(e) => {
              e.preventDefault();
              onClear();
            }}
            className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-700"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center text-center">
          <div
            className={cn(
              "mb-4 flex h-14 w-14 items-center justify-center rounded-xl",
              isDragging
                ? "bg-blue-100 dark:bg-blue-900/30"
                : "bg-slate-100 dark:bg-slate-800"
            )}
          >
            {isDragging ? (
              <FileText className="h-7 w-7 text-blue-500" />
            ) : (
              <Upload className="h-7 w-7 text-slate-400" />
            )}
          </div>
          <p className="mb-1 font-medium text-slate-700 dark:text-slate-300">
            {isDragging ? "Drop your PDF here" : "Drop PDF here or click to upload"}
          </p>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            PDF files only, up to 50MB
          </p>
        </div>
      )}
    </div>
  );
}
