import { createFileRoute } from "@tanstack/react-router";
import { useState, useMemo } from "react";
import {
  useCoAgent,
  useCopilotAction,
  useCopilotReadable,
  useRenderToolCall,
} from "@copilotkit/react-core";
import { Search, Filter, FileText, BookOpen, Loader2 } from "lucide-react";
import { SearchResults } from "~/components/search/SearchResults";
import { useDagsterSharedState } from "~/hooks/useDagsterSharedState";

export const Route = createFileRoute("/search")({
  component: SearchPage,
  validateSearch: (search: Record<string, unknown>) => ({
    query: (search.query as string) || "",
    type: (search.type as string) || "",
    level: (search.level as string) || "",
    subject: (search.subject as string) || "",
  }),
});

function SearchPage() {
  const { query, type, level, subject } = Route.useSearch();

  const [searchQuery, setSearchQuery] = useState(query);
  const [filters, setFilters] = useState({
    documentType: type,
    educationLevel: level,
    subject: subject,
  });
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Connect to the education assistant agent
  const { state, setState } = useCoAgent({
    name: "education_assistant",
    initialState: {
      lastQuery: "",
      searchResults: [] as SearchResult[],
      selectedDocument: null as string | null,
    },
  });

  // Get Dagster pipeline status for context
  const { state: dagsterState, isProcessing: dagsterProcessing } =
    useDagsterSharedState({ enableRealtime: true });

  // Prepare search context for CopilotKit
  const searchContext = useMemo(
    () => ({
      currentQuery: searchQuery,
      filters: {
        documentType: filters.documentType || "all",
        educationLevel: filters.educationLevel || "all",
        subject: filters.subject || "all",
      },
      resultCount: results.length,
      hasResults: results.length > 0,
      selectedDocument: state.selectedDocument,
      isSearching,
      topResults: results.slice(0, 3).map((r) => ({
        title: r.title,
        type: r.documentType,
        score: r.score,
      })),
    }),
    [searchQuery, filters, results, state.selectedDocument, isSearching]
  );

  // Register search context with CopilotKit
  useCopilotReadable({
    description:
      "Current search context including query, filters, and results. Use this to understand what the user is searching for and help them find relevant curriculum documents.",
    value: searchContext,
  });

  // Register selected document context
  useCopilotReadable({
    description:
      "Currently selected document details if any. Use this when the user asks about a specific document.",
    value: state.selectedDocument
      ? results.find((r) => r.id === state.selectedDocument) || null
      : null,
  });

  // Register filter options context
  useCopilotReadable({
    description:
      "Available filter options for curriculum search including document types, education levels, and subjects.",
    value: {
      documentTypes: [
        "curriculum_specification",
        "examiner_report",
        "marking_scheme",
        "guidelines",
      ],
      educationLevels: ["primary", "junior_cycle", "senior_cycle"],
      subjects: [
        "mathematics",
        "english",
        "irish",
        "science",
        "history",
        "geography",
      ],
    },
  });

  // Register render handler for curriculum_search tool
  useRenderToolCall({
    name: "curriculum_search",
    render: ({ args, result, status }) => {
      if (status === "executing") {
        return (
          <div className="animate-pulse flex space-x-4 p-4 bg-gray-50 rounded-lg">
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
        );
      }

      if (result?.results) {
        return (
          <SearchResults
            query={args.query}
            results={result.results}
            onSelect={(docId) => {
              setState((prev) => ({ ...prev, selectedDocument: docId }));
            }}
          />
        );
      }

      return null;
    },
  });

  // Register action for document viewing
  useCopilotAction({
    name: "viewDocument",
    description: "View a specific curriculum document",
    parameters: [
      {
        name: "documentId",
        type: "string",
        description: "The ID of the document to view",
        required: true,
      },
    ],
    handler: async ({ documentId }) => {
      window.location.href = `/documents/${documentId}`;
      return { success: true };
    },
  });

  // Register action for generating practice questions
  useCopilotAction({
    name: "generateQuestions",
    description:
      "Generate practice questions based on selected curriculum content or learning outcomes",
    parameters: [
      {
        name: "topic",
        type: "string",
        description: "The topic or learning outcome to generate questions for",
        required: true,
      },
      {
        name: "questionType",
        type: "string",
        description:
          "Type of questions: multiple_choice, short_answer, essay, cloze",
        required: false,
      },
      {
        name: "difficulty",
        type: "string",
        description: "Difficulty level: easy, medium, hard",
        required: false,
      },
      {
        name: "count",
        type: "number",
        description: "Number of questions to generate (1-10)",
        required: false,
      },
    ],
    handler: async ({ topic, questionType, difficulty, count }) => {
      const response = await fetch("/api/generate/questions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic,
          questionType: questionType || "multiple_choice",
          difficulty: difficulty || "medium",
          count: count || 5,
          subject: filters.subject,
          educationLevel: filters.educationLevel,
        }),
      });

      if (!response.ok) {
        return { error: "Failed to generate questions" };
      }

      const data = await response.json();
      return {
        success: true,
        questions: data.questions,
        message: `Generated ${data.questions.length} questions on ${topic}`,
      };
    },
  });

  // Register action for comparing documents
  useCopilotAction({
    name: "compareDocuments",
    description:
      "Cross-reference and compare two curriculum documents to find similarities and differences",
    parameters: [
      {
        name: "documentId1",
        type: "string",
        description: "First document ID to compare",
        required: true,
      },
      {
        name: "documentId2",
        type: "string",
        description: "Second document ID to compare",
        required: true,
      },
      {
        name: "aspectsToCompare",
        type: "string",
        description:
          "Aspects to compare: learning_outcomes, topics, assessment, skills",
        required: false,
      },
    ],
    handler: async ({ documentId1, documentId2, aspectsToCompare }) => {
      const response = await fetch("/api/documents/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          documentIds: [documentId1, documentId2],
          aspects: aspectsToCompare?.split(",") || ["learning_outcomes", "topics"],
        }),
      });

      if (!response.ok) {
        return { error: "Failed to compare documents" };
      }

      const data = await response.json();
      return {
        success: true,
        comparison: data.comparison,
        similarities: data.similarities,
        differences: data.differences,
      };
    },
  });

  // Register action for exporting content
  useCopilotAction({
    name: "exportContent",
    description:
      "Export search results or selected content as PDF or markdown",
    parameters: [
      {
        name: "format",
        type: "string",
        description: "Export format: pdf or markdown",
        required: true,
      },
      {
        name: "includeResults",
        type: "boolean",
        description: "Whether to include current search results",
        required: false,
      },
      {
        name: "documentIds",
        type: "string",
        description: "Comma-separated document IDs to export",
        required: false,
      },
    ],
    handler: async ({ format, includeResults, documentIds }) => {
      const idsToExport = documentIds
        ? documentIds.split(",")
        : includeResults
          ? results.map((r) => r.id)
          : [];

      if (idsToExport.length === 0) {
        return { error: "No documents selected for export" };
      }

      const response = await fetch("/api/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          format,
          documentIds: idsToExport,
          query: searchQuery,
        }),
      });

      if (!response.ok) {
        return { error: "Failed to export content" };
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `curriculum-export.${format === "pdf" ? "pdf" : "md"}`;
      a.click();

      return {
        success: true,
        message: `Exported ${idsToExport.length} documents as ${format}`,
      };
    },
  });

  // Register action for Irish language validation (Human-in-the-Loop)
  useCopilotAction({
    name: "validateIrishTranslation",
    description:
      "Request human validation for Irish language content to ensure accuracy",
    parameters: [
      {
        name: "contentToValidate",
        type: "string",
        description: "The Irish language content to validate",
        required: true,
      },
      {
        name: "validationType",
        type: "string",
        description:
          "Type of validation: grammar, translation, terminology, style",
        required: true,
      },
      {
        name: "context",
        type: "string",
        description: "Context for the validation (e.g., subject area, grade level)",
        required: false,
      },
    ],
    handler: async ({ contentToValidate, validationType, context }) => {
      // This triggers the HITL validation flow
      const response = await fetch("/api/validate/irish", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: contentToValidate,
          validationType,
          context: context || `${filters.subject} - ${filters.educationLevel}`,
        }),
      });

      if (!response.ok) {
        return { error: "Failed to submit for validation" };
      }

      const data = await response.json();
      return {
        success: true,
        validationId: data.validationId,
        status: "pending_review",
        message:
          "Content submitted for Irish language validation. You will be notified when review is complete.",
      };
    },
    // This action renders a UI component for HITL
    render: "You can use the /validate command to check Irish translations.",
  });

  // Register action for applying filters
  useCopilotAction({
    name: "applySearchFilters",
    description: "Apply filters to narrow down curriculum search results",
    parameters: [
      {
        name: "documentType",
        type: "string",
        description:
          "Document type filter: curriculum_specification, examiner_report, marking_scheme, guidelines",
        required: false,
      },
      {
        name: "educationLevel",
        type: "string",
        description:
          "Education level filter: primary, junior_cycle, senior_cycle",
        required: false,
      },
      {
        name: "subject",
        type: "string",
        description:
          "Subject filter: mathematics, english, irish, science, history, geography",
        required: false,
      },
    ],
    handler: async ({ documentType, educationLevel, subject }) => {
      const newFilters = {
        documentType: documentType || filters.documentType,
        educationLevel: educationLevel || filters.educationLevel,
        subject: subject || filters.subject,
      };
      setFilters(newFilters);

      // Trigger new search if we have a query
      if (searchQuery) {
        setIsSearching(true);
        try {
          const response = await fetch("/api/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: searchQuery, filters: newFilters }),
          });
          const data = await response.json();
          setResults(data.results || []);
        } finally {
          setIsSearching(false);
        }
      }

      return {
        success: true,
        appliedFilters: newFilters,
        message: "Filters applied successfully",
      };
    },
  });

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSearching(true);

    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: searchQuery,
          filters,
        }),
      });

      const data = await response.json();
      setResults(data.results || []);

      // Update agent state
      setState((prev) => ({
        ...prev,
        lastQuery: searchQuery,
        searchResults: data.results || [],
      }));
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search curriculum documents, syllabi, examiner reports..."
                className="w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <button
              type="submit"
              disabled={isSearching}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              {isSearching ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="h-4 w-4" />
                  Search
                </>
              )}
            </button>
          </div>

          {/* Filters */}
          <div className="flex gap-4 items-center">
            <Filter className="h-4 w-4 text-gray-400" />
            <select
              value={filters.documentType}
              onChange={(e) =>
                setFilters((f) => ({ ...f, documentType: e.target.value }))
              }
              className="border rounded-md px-3 py-2 text-sm"
            >
              <option value="">All Document Types</option>
              <option value="curriculum_specification">
                Curriculum Specification
              </option>
              <option value="examiner_report">Examiner Report</option>
              <option value="marking_scheme">Marking Scheme</option>
              <option value="guidelines">Guidelines</option>
            </select>

            <select
              value={filters.educationLevel}
              onChange={(e) =>
                setFilters((f) => ({ ...f, educationLevel: e.target.value }))
              }
              className="border rounded-md px-3 py-2 text-sm"
            >
              <option value="">All Levels</option>
              <option value="primary">Primary</option>
              <option value="junior_cycle">Junior Cycle</option>
              <option value="senior_cycle">Senior Cycle</option>
            </select>

            <select
              value={filters.subject}
              onChange={(e) =>
                setFilters((f) => ({ ...f, subject: e.target.value }))
              }
              className="border rounded-md px-3 py-2 text-sm"
            >
              <option value="">All Subjects</option>
              <option value="mathematics">Mathematics</option>
              <option value="english">English</option>
              <option value="irish">Irish / Gaeilge</option>
              <option value="science">Science</option>
              <option value="history">History</option>
              <option value="geography">Geography</option>
            </select>
          </div>
        </form>
      </div>

      {/* Results */}
      {results.length > 0 ? (
        <SearchResults
          query={searchQuery}
          results={results}
          onSelect={(docId) => {
            setState((prev) => ({ ...prev, selectedDocument: docId }));
          }}
        />
      ) : searchQuery && !isSearching ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No results found
          </h3>
          <p className="text-gray-500">
            Try adjusting your search terms or filters.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <BookOpen className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Search Irish Curriculum Resources
          </h3>
          <p className="text-gray-500 max-w-md mx-auto">
            Search across curriculum specifications, examiner reports, syllabi,
            and guidelines from the NCCA, SEC, and Department of Education.
          </p>
        </div>
      )}

      {/* Ask AI Section */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-100">
        <h3 className="text-lg font-medium text-blue-900 mb-2">
          Ask the Education Assistant
        </h3>
        <p className="text-blue-700 text-sm mb-4">
          Can't find what you're looking for? Ask our AI assistant for help
          navigating the curriculum.
        </p>
        <div className="flex gap-2 flex-wrap">
          <QuickQuestion text="What are the key skills in Junior Cycle?" />
          <QuickQuestion text="How is Irish assessed at Leaving Cert?" />
          <QuickQuestion text="What's new in the Primary Maths curriculum?" />
        </div>
      </div>
    </div>
  );
}

function QuickQuestion({ text }: { text: string }) {
  return (
    <button
      onClick={() => {
        // This would trigger the CopilotKit chat with the question
        const event = new CustomEvent("copilotkit:sendMessage", {
          detail: { message: text },
        });
        window.dispatchEvent(event);
      }}
      className="text-sm bg-white text-blue-700 px-3 py-1.5 rounded-full border border-blue-200 hover:bg-blue-50 transition-colors"
    >
      {text}
    </button>
  );
}

interface SearchResult {
  id: string;
  title: string;
  excerpt: string;
  documentType: string;
  educationLevel: string;
  subject: string;
  score: number;
  source: string;
}
