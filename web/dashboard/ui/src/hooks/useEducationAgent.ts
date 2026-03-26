import { useCoAgent, useCopilotAction } from "@copilotkit/react-core";
import { useState, useCallback } from "react";

/**
 * Custom hook for education agent interactions.
 *
 * Provides:
 * - Agent state management
 * - Search actions
 * - Document viewing
 * - Q&A capabilities
 */

interface AgentState {
  lastQuery: string;
  searchResults: SearchResult[];
  selectedDocument: string | null;
  conversationHistory: ConversationMessage[];
}

interface SearchResult {
  id: string;
  title: string;
  excerpt: string;
  documentType: string;
  educationLevel: string;
  subject: string;
  score: number;
}

interface ConversationMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export function useEducationAgent() {
  const [isProcessing, setIsProcessing] = useState(false);

  // Connect to the education assistant agent
  const { state, setState, run } = useCoAgent<AgentState>({
    name: "education_assistant",
    initialState: {
      lastQuery: "",
      searchResults: [],
      selectedDocument: null,
      conversationHistory: [],
    },
  });

  // Register curriculum search action
  useCopilotAction({
    name: "searchCurriculum",
    description: "Search Irish curriculum documents",
    parameters: [
      {
        name: "query",
        type: "string",
        description: "Search query",
        required: true,
      },
      {
        name: "subject",
        type: "string",
        description: "Subject filter (e.g., Mathematics, Irish, English)",
        required: false,
      },
      {
        name: "level",
        type: "string",
        description: "Education level (primary, junior_cycle, senior_cycle)",
        required: false,
      },
      {
        name: "documentType",
        type: "string",
        description:
          "Document type (curriculum_specification, examiner_report, marking_scheme)",
        required: false,
      },
    ],
    handler: async ({ query, subject, level, documentType }) => {
      setIsProcessing(true);
      try {
        const response = await fetch("/api/search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query,
            filters: {
              subject,
              educationLevel: level,
              documentType,
            },
          }),
        });

        const data = await response.json();

        setState((prev) => ({
          ...prev,
          lastQuery: query,
          searchResults: data.results || [],
        }));

        return {
          success: true,
          resultCount: data.results?.length || 0,
          results: data.results,
        };
      } finally {
        setIsProcessing(false);
      }
    },
  });

  // Register document Q&A action
  useCopilotAction({
    name: "askQuestion",
    description: "Ask a question about Irish curriculum content",
    parameters: [
      {
        name: "question",
        type: "string",
        description: "Question to answer",
        required: true,
      },
    ],
    handler: async ({ question }) => {
      setIsProcessing(true);
      try {
        // First search for relevant content
        const searchResponse = await fetch("/api/search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query: question,
            topK: 5,
          }),
        });

        const searchData = await searchResponse.json();

        // Build context from search results
        const context = searchData.results
          ?.map((r: SearchResult) => `${r.title}: ${r.excerpt}`)
          .join("\n\n");

        // Add to conversation history
        setState((prev) => ({
          ...prev,
          conversationHistory: [
            ...prev.conversationHistory,
            {
              role: "user" as const,
              content: question,
              timestamp: new Date(),
            },
          ],
        }));

        return {
          success: true,
          context,
          sources: searchData.results?.map((r: SearchResult) => ({
            title: r.title,
            id: r.id,
          })),
        };
      } finally {
        setIsProcessing(false);
      }
    },
  });

  // Register document viewing action
  useCopilotAction({
    name: "viewDocument",
    description: "View a specific curriculum document",
    parameters: [
      {
        name: "documentId",
        type: "string",
        description: "Document ID to view",
        required: true,
      },
    ],
    handler: async ({ documentId }) => {
      setState((prev) => ({
        ...prev,
        selectedDocument: documentId,
      }));

      // Navigate to document view
      window.location.href = `/documents/${documentId}`;

      return { success: true, documentId };
    },
  });

  // Search helper
  const search = useCallback(
    async (query: string, filters?: Record<string, string>) => {
      if (run) {
        await run(`Search curriculum documents for: ${query}`, {
          query,
          ...filters,
        });
      }
    },
    [run]
  );

  // Clear results helper
  const clearResults = useCallback(() => {
    setState((prev) => ({
      ...prev,
      searchResults: [],
      lastQuery: "",
    }));
  }, [setState]);

  return {
    state,
    isProcessing,
    search,
    clearResults,
    setSelectedDocument: (docId: string | null) => {
      setState((prev) => ({ ...prev, selectedDocument: docId }));
    },
  };
}
