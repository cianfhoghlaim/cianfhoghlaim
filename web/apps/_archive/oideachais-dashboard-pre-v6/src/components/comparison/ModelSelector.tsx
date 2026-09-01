import { useQuery } from "convex/react";
import { api } from "@convex/_generated/api";
import { Check, AlertCircle, Cpu, Zap, FileText } from "lucide-react";
import { cn } from "~/lib/utils";

interface ModelSelectorProps {
  selectedModels: string[];
  onSelectionChange: (models: string[]) => void;
  maxSelection?: number;
}

export function ModelSelector({
  selectedModels,
  onSelectionChange,
  maxSelection = 3,
}: ModelSelectorProps) {
  const models = useQuery(api.models.list);

  const handleToggle = (modelName: string) => {
    if (selectedModels.includes(modelName)) {
      onSelectionChange(selectedModels.filter((m) => m !== modelName));
    } else if (selectedModels.length < maxSelection) {
      onSelectionChange([...selectedModels, modelName]);
    }
  };

  const getProviderIcon = (provider: string) => {
    switch (provider) {
      case "llama-swap":
      case "mlx-omni-server":
      case "vllm":
        return <Cpu className="h-4 w-4" />;
      case "library":
        return <Zap className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  const getProviderLabel = (provider: string) => {
    const labels: Record<string, string> = {
      "llama-swap": "GGUF",
      "mlx-omni-server": "MLX",
      vllm: "vLLM",
      paddle: "API",
      docling: "API",
      unstract: "API",
      library: "Local",
    };
    return labels[provider] || provider;
  };

  if (!models) {
    return (
      <div className="animate-pulse space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 rounded-lg bg-slate-100 dark:bg-slate-800" />
        ))}
      </div>
    );
  }

  // Group models by provider type
  const groupedModels = {
    "Vision Models": models.filter((m) =>
      ["llama-swap"].includes(m.provider)
    ),
    "OCR Models": models.filter((m) =>
      ["mlx-omni-server", "vllm"].includes(m.provider)
    ),
    "Platform Services": models.filter((m) =>
      ["paddle", "docling", "unstract"].includes(m.provider)
    ),
    "Python Libraries": models.filter((m) => m.provider === "library"),
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Select up to {maxSelection} models to compare
        </p>
        <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
          {selectedModels.length}/{maxSelection} selected
        </p>
      </div>

      {Object.entries(groupedModels).map(([group, groupModels]) => (
        <div key={group}>
          <h3 className="mb-3 text-sm font-semibold text-slate-500 uppercase tracking-wide dark:text-slate-400">
            {group}
          </h3>
          <div className="grid gap-2 sm:grid-cols-2">
            {groupModels.map((model) => {
              const isSelected = selectedModels.includes(model.name);
              const isDisabled =
                !model.isAvailable ||
                (!isSelected && selectedModels.length >= maxSelection);

              return (
                <button
                  key={model.name}
                  onClick={() => handleToggle(model.name)}
                  disabled={isDisabled}
                  className={cn(
                    "flex items-center gap-3 rounded-lg border p-3 text-left transition-all",
                    isSelected
                      ? "border-blue-500 bg-blue-50 ring-1 ring-blue-500 dark:border-blue-400 dark:bg-blue-950/30"
                      : "border-slate-200 hover:border-slate-300 dark:border-slate-700 dark:hover:border-slate-600",
                    isDisabled && !isSelected && "cursor-not-allowed opacity-50"
                  )}
                >
                  <div
                    className={cn(
                      "flex h-8 w-8 items-center justify-center rounded-lg",
                      isSelected
                        ? "bg-blue-100 text-blue-600 dark:bg-blue-900/50 dark:text-blue-400"
                        : "bg-slate-100 text-slate-400 dark:bg-slate-800"
                    )}
                  >
                    {isSelected ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      getProviderIcon(model.provider)
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-medium text-slate-900 dark:text-white truncate">
                        {model.displayName}
                      </p>
                      {!model.isAvailable && (
                        <AlertCircle className="h-4 w-4 text-amber-500 flex-shrink-0" />
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                      <span className="rounded bg-slate-100 px-1.5 py-0.5 dark:bg-slate-800">
                        {getProviderLabel(model.provider)}
                      </span>
                      {model.vramRequirement && (
                        <span>{model.vramRequirement}</span>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
