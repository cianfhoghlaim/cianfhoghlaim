import { FileText, ExternalLink, Star } from "lucide-react";

interface SearchResult {
  id: string;
  title: string;
  excerpt: string;
  documentType: string;
  educationLevel: string;
  subject: string;
  score: number;
  source: string;
  url?: string;
}

interface SearchResultsProps {
  query: string;
  results: SearchResult[];
  onSelect?: (documentId: string) => void;
}

export function SearchResults({ query, results, onSelect }: SearchResultsProps) {
  return (
    <div className="bg-white rounded-lg shadow divide-y">
      <div className="p-4 bg-gray-50 border-b">
        <h2 className="text-sm font-medium text-gray-700">
          {results.length} results for "{query}"
        </h2>
      </div>

      {results.map((result) => (
        <SearchResultCard
          key={result.id}
          result={result}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}

function SearchResultCard({
  result,
  onSelect,
}: {
  result: SearchResult;
  onSelect?: (documentId: string) => void;
}) {
  const documentTypeLabels: Record<string, { label: string; color: string }> = {
    curriculum_specification: {
      label: "Curriculum Specification",
      color: "bg-blue-100 text-blue-800",
    },
    examiner_report: {
      label: "Examiner Report",
      color: "bg-green-100 text-green-800",
    },
    marking_scheme: {
      label: "Marking Scheme",
      color: "bg-purple-100 text-purple-800",
    },
    guidelines: {
      label: "Guidelines",
      color: "bg-orange-100 text-orange-800",
    },
    other: {
      label: "Document",
      color: "bg-gray-100 text-gray-800",
    },
  };

  const levelLabels: Record<string, string> = {
    primary: "Primary",
    junior_cycle: "Junior Cycle",
    senior_cycle: "Senior Cycle",
    unknown: "",
  };

  const typeInfo = documentTypeLabels[result.documentType] || documentTypeLabels.other;
  const levelLabel = levelLabels[result.educationLevel] || result.educationLevel;

  return (
    <div className="p-4 hover:bg-gray-50 transition-colors">
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0">
          <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
            <FileText className="h-5 w-5 text-gray-500" />
          </div>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <button
                onClick={() => onSelect?.(result.id)}
                className="text-left group"
              >
                <h3 className="text-lg font-medium text-gray-900 group-hover:text-blue-600 transition-colors">
                  {result.title}
                </h3>
              </button>

              <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                {result.excerpt}
              </p>

              <div className="flex items-center gap-2 mt-2 flex-wrap">
                <span
                  className={`text-xs px-2 py-1 rounded-full font-medium ${typeInfo.color}`}
                >
                  {typeInfo.label}
                </span>

                {levelLabel && (
                  <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                    {levelLabel}
                  </span>
                )}

                {result.subject && result.subject !== "unknown" && (
                  <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded capitalize">
                    {result.subject.replace(/_/g, " ")}
                  </span>
                )}

                <span className="text-xs text-gray-400">
                  Source: {result.source}
                </span>
              </div>
            </div>

            <div className="flex flex-col items-end gap-2">
              <div className="flex items-center gap-1">
                <Star className="h-4 w-4 text-yellow-400 fill-current" />
                <span className="text-sm font-medium text-gray-700">
                  {(result.score * 100).toFixed(0)}%
                </span>
              </div>

              {result.url && (
                <a
                  href={result.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                >
                  View PDF
                  <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
