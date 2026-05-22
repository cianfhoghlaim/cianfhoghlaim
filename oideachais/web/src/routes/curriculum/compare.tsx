import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { GitCompare, Search, Filter, ChevronDown, Check } from "lucide-react";
import { cn } from "../../lib/utils";

export const Route = createFileRoute("/curriculum/compare")({
  component: ComparePage,
});

type Nation = "ireland" | "england" | "scotland" | "wales" | "northern_ireland";

interface ComparisonResult {
  source_nation: Nation;
  target_nation: Nation;
  source_outcome: string;
  target_outcome: string;
  similarity_score: number;
  alignment_type: "exact" | "partial" | "related";
}

const NATIONS: { value: Nation; label: string; flag: string }[] = [
  { value: "ireland", label: "Ireland", flag: "IE" },
  { value: "england", label: "England", flag: "EN" },
  { value: "scotland", label: "Scotland", flag: "SC" },
  { value: "wales", label: "Wales", flag: "WA" },
  { value: "northern_ireland", label: "N. Ireland", flag: "NI" },
];

const SUBJECTS = [
  "Mathematics",
  "English",
  "Science",
  "History",
  "Geography",
  "Irish",
  "Welsh",
  "Scottish Gaelic",
  "French",
  "German",
];

const LEVELS = [
  { value: "lower_secondary", label: "Lower Secondary (JC/GCSE/Nat5)" },
  { value: "upper_secondary", label: "Upper Secondary (LC/A-Level/Higher)" },
];

// Mock comparison data
const MOCK_RESULTS: ComparisonResult[] = [
  {
    source_nation: "ireland",
    target_nation: "england",
    source_outcome: "Apply algebraic techniques to solve linear equations",
    target_outcome: "Solve linear equations in one variable",
    similarity_score: 0.92,
    alignment_type: "exact",
  },
  {
    source_nation: "ireland",
    target_nation: "scotland",
    source_outcome: "Apply algebraic techniques to solve linear equations",
    target_outcome: "Use algebraic methods to solve equations",
    similarity_score: 0.87,
    alignment_type: "partial",
  },
  {
    source_nation: "ireland",
    target_nation: "wales",
    source_outcome: "Apply algebraic techniques to solve linear equations",
    target_outcome: "Manipulate and solve algebraic expressions and equations",
    similarity_score: 0.85,
    alignment_type: "partial",
  },
];

function ComparePage() {
  const [selectedNations, setSelectedNations] = useState<Nation[]>(["ireland", "england"]);
  const [selectedSubject, setSelectedSubject] = useState("Mathematics");
  const [selectedLevel, setSelectedLevel] = useState("lower_secondary");
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState<ComparisonResult[]>(MOCK_RESULTS);
  const [isLoading, setIsLoading] = useState(false);

  const toggleNation = (nation: Nation) => {
    setSelectedNations((prev) =>
      prev.includes(nation)
        ? prev.filter((n) => n !== nation)
        : [...prev, nation]
    );
  };

  const handleCompare = async () => {
    if (selectedNations.length < 2) {
      return;
    }
    setIsLoading(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setResults(MOCK_RESULTS);
    setIsLoading(false);
  };

  const getAlignmentColor = (type: string) => {
    switch (type) {
      case "exact":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      case "partial":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
      case "related":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <GitCompare className="h-6 w-6" />
          Curriculum Comparison
        </h1>
        <p className="text-muted-foreground">
          Compare learning outcomes across different national curricula
        </p>
      </div>

      {/* Filters */}
      <div className="rounded-lg border bg-card p-6 space-y-4">
        <h2 className="font-semibold flex items-center gap-2">
          <Filter className="h-4 w-4" />
          Filters
        </h2>

        {/* Nation Selection */}
        <div>
          <label className="text-sm font-medium mb-2 block">
            Select Nations (minimum 2)
          </label>
          <div className="flex flex-wrap gap-2">
            {NATIONS.map((nation) => (
              <button
                key={nation.value}
                onClick={() => toggleNation(nation.value)}
                className={cn(
                  "inline-flex items-center gap-2 rounded-md border px-3 py-2 text-sm",
                  selectedNations.includes(nation.value)
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-input hover:bg-accent"
                )}
              >
                <span className="font-mono text-xs bg-muted px-1 rounded">
                  {nation.flag}
                </span>
                {nation.label}
                {selectedNations.includes(nation.value) && (
                  <Check className="h-4 w-4" />
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Subject and Level */}
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="text-sm font-medium mb-2 block">Subject</label>
            <div className="relative">
              <select
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
                className={cn(
                  "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm",
                  "focus:outline-none focus:ring-2 focus:ring-ring"
                )}
              >
                {SUBJECTS.map((subject) => (
                  <option key={subject} value={subject}>
                    {subject}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-3 h-4 w-4 opacity-50" />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">Level</label>
            <div className="relative">
              <select
                value={selectedLevel}
                onChange={(e) => setSelectedLevel(e.target.value)}
                className={cn(
                  "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm",
                  "focus:outline-none focus:ring-2 focus:ring-ring"
                )}
              >
                {LEVELS.map((level) => (
                  <option key={level.value} value={level.value}>
                    {level.label}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-3 h-4 w-4 opacity-50" />
            </div>
          </div>
        </div>

        {/* Search within results */}
        <div>
          <label className="text-sm font-medium mb-2 block">
            Search Learning Outcomes
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter by keyword..."
              className={cn(
                "flex h-10 w-full rounded-md border border-input bg-background pl-10 pr-3 py-2 text-sm",
                "placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              )}
            />
          </div>
        </div>

        <button
          onClick={handleCompare}
          disabled={selectedNations.length < 2 || isLoading}
          className={cn(
            "inline-flex items-center justify-center rounded-md text-sm font-medium",
            "bg-primary text-primary-foreground hover:bg-primary/90",
            "h-10 px-4 disabled:opacity-50 disabled:cursor-not-allowed"
          )}
        >
          {isLoading ? (
            <>Loading...</>
          ) : (
            <>
              <GitCompare className="mr-2 h-4 w-4" />
              Compare Curricula
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-4">
          <h2 className="font-semibold">
            Comparison Results ({results.length} alignments found)
          </h2>

          <div className="space-y-3">
            {results.map((result, idx) => (
              <div
                key={idx}
                className="rounded-lg border bg-card p-4 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs bg-muted px-2 py-1 rounded">
                      {NATIONS.find((n) => n.value === result.source_nation)?.flag}
                    </span>
                    <span className="text-muted-foreground">→</span>
                    <span className="font-mono text-xs bg-muted px-2 py-1 rounded">
                      {NATIONS.find((n) => n.value === result.target_nation)?.flag}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={cn(
                        "text-xs px-2 py-1 rounded-full",
                        getAlignmentColor(result.alignment_type)
                      )}
                    >
                      {result.alignment_type}
                    </span>
                    <span className="text-sm font-medium">
                      {Math.round(result.similarity_score * 100)}%
                    </span>
                  </div>
                </div>

                <div className="grid gap-3 md:grid-cols-2">
                  <div className="rounded-md bg-muted/50 p-3">
                    <div className="text-xs text-muted-foreground mb-1">
                      Source ({NATIONS.find((n) => n.value === result.source_nation)?.label})
                    </div>
                    <p className="text-sm">{result.source_outcome}</p>
                  </div>
                  <div className="rounded-md bg-muted/50 p-3">
                    <div className="text-xs text-muted-foreground mb-1">
                      Target ({NATIONS.find((n) => n.value === result.target_nation)?.label})
                    </div>
                    <p className="text-sm">{result.target_outcome}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
