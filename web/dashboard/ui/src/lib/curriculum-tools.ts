/**
 * Celtic Education Curriculum Tools - TanStack AI Tool Definitions
 *
 * Type-safe tool definitions using Zod schemas for:
 * - Curriculum search (hybrid, semantic, keyword)
 * - Learning outcome retrieval
 * - Subject information
 * - Document management
 */

import { toolDefinition } from "@tanstack/ai";
import { clientTools as createClientTools } from "@tanstack/ai-client";
import { z } from "zod";

// Common schemas
const educationLevelSchema = z.enum([
  "primary",
  "junior_cycle",
  "senior_cycle",
  "leaving_cert",
  "all",
]);

const nationSchema = z.enum([
  "ireland",
  "scotland",
  "wales",
  "england",
  "northern_ireland",
  "all",
]);

const languageSchema = z.enum(["en", "ga", "gd", "cy", "br", "gv", "kw"]);

const searchResultSchema = z.object({
  id: z.string(),
  title: z.string(),
  content: z.string(),
  source: z.string(),
  score: z.number(),
  metadata: z.object({
    subject: z.string().optional(),
    level: z.string().optional(),
    nation: z.string().optional(),
    language: z.string().optional(),
    documentType: z.string().optional(),
  }),
});

// ============================================================================
// Search Tools
// ============================================================================

/**
 * Hybrid search combining vector and keyword search
 */
export const hybridSearchToolDef = toolDefinition({
  name: "searchCurriculumHybrid",
  description:
    "Search curriculum documents using hybrid search (vector + keyword). Best for natural language queries about curriculum content, learning outcomes, or educational topics.",
  inputSchema: z.object({
    vectorQuery: z
      .string()
      .describe("Natural language query for semantic search"),
    keywordQuery: z
      .string()
      .optional()
      .describe("Optional keyword query for exact term matching"),
    topK: z.number().default(10).describe("Number of results to return"),
    vectorWeight: z
      .number()
      .default(0.7)
      .describe("Weight for vector search (0-1)"),
    keywordWeight: z
      .number()
      .default(0.3)
      .describe("Weight for keyword search (0-1)"),
    filters: z
      .object({
        level: educationLevelSchema.optional(),
        nation: nationSchema.optional(),
        subject: z.string().optional(),
        language: languageSchema.optional(),
      })
      .optional(),
  }),
  outputSchema: z.object({
    results: z.array(searchResultSchema),
    totalCount: z.number(),
    queryTime: z.number(),
  }),
});

export const hybridSearchServer = hybridSearchToolDef.server(async (args) => {
  // Proxy to MCP endpoint
  const response = await fetch("/api/mcp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: Date.now(),
      method: "tools/call",
      params: {
        name: "search-hybrid",
        arguments: {
          vector_query: args.vectorQuery,
          keyword_query: args.keywordQuery,
          top_k: args.topK,
          vector_weight: args.vectorWeight,
          keyword_weight: args.keywordWeight,
        },
      },
    }),
  });

  const data = await response.json();
  return data.result || { results: [], totalCount: 0, queryTime: 0 };
});

/**
 * Pure semantic search using embeddings
 */
export const semanticSearchToolDef = toolDefinition({
  name: "searchCurriculumSemantic",
  description:
    "Search curriculum documents using semantic similarity. Best for finding conceptually related content even if exact terms differ.",
  inputSchema: z.object({
    query: z.string().describe("Natural language query"),
    topK: z.number().default(10).describe("Number of results to return"),
    filters: z
      .object({
        level: educationLevelSchema.optional(),
        nation: nationSchema.optional(),
        subject: z.string().optional(),
      })
      .optional(),
  }),
  outputSchema: z.object({
    results: z.array(searchResultSchema),
    totalCount: z.number(),
  }),
});

export const semanticSearchServer = semanticSearchToolDef.server(
  async (args) => {
    const response = await fetch("/api/mcp", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: Date.now(),
        method: "tools/call",
        params: {
          name: "search-semantic",
          arguments: {
            query: args.query,
            top_k: args.topK,
          },
        },
      }),
    });

    const data = await response.json();
    return data.result || { results: [], totalCount: 0 };
  }
);

// ============================================================================
// Learning Outcome Tools
// ============================================================================

const learningOutcomeSchema = z.object({
  id: z.string(),
  code: z.string(),
  descriptionEn: z.string(),
  descriptionGa: z.string().optional(),
  subject: z.string(),
  strand: z.string().optional(),
  strandUnit: z.string().optional(),
  level: z.string(),
  keySkills: z.array(z.string()).optional(),
  difficultyLevel: z.number().optional(),
});

export const getLearningOutcomesToolDef = toolDefinition({
  name: "getLearningOutcomes",
  description:
    "Get learning outcomes for a specific subject and level. Returns curriculum learning outcomes with bilingual descriptions.",
  inputSchema: z.object({
    subject: z.string().describe("Subject code (e.g., 'mathematics', 'irish')"),
    level: educationLevelSchema.describe("Education level"),
    strand: z.string().optional().describe("Optional strand filter"),
  }),
  outputSchema: z.object({
    outcomes: z.array(learningOutcomeSchema),
    subject: z.string(),
    level: z.string(),
  }),
});

export const getLearningOutcomesServer = getLearningOutcomesToolDef.server(
  async (args) => {
    const response = await fetch(
      `/api/search/learning-outcomes?subject=${args.subject}&level=${args.level}${args.strand ? `&strand=${args.strand}` : ""}`
    );
    const data = await response.json();
    return data;
  }
);

// ============================================================================
// Subject Tools
// ============================================================================

const subjectSchema = z.object({
  code: z.string(),
  nameEn: z.string(),
  nameGa: z.string().optional(),
  level: z.string(),
  syllabusUrl: z.string().optional(),
  strandCount: z.number().optional(),
  outcomeCount: z.number().optional(),
});

export const getSubjectsToolDef = toolDefinition({
  name: "getSubjects",
  description:
    "Get all subjects for a specific education level. Returns subject codes and names with bilingual support.",
  inputSchema: z.object({
    level: educationLevelSchema.describe("Education level"),
    nation: nationSchema.default("ireland").describe("Nation/curriculum"),
  }),
  outputSchema: z.object({
    subjects: z.array(subjectSchema),
    level: z.string(),
    nation: z.string(),
  }),
});

export const getSubjectsServer = getSubjectsToolDef.server(async (args) => {
  const response = await fetch(
    `/api/search/subjects?level=${args.level}&nation=${args.nation}`
  );
  const data = await response.json();
  return data;
});

// ============================================================================
// Translation Tools
// ============================================================================

export const translateContentToolDef = toolDefinition({
  name: "translateContent",
  description:
    "Translate educational content between Celtic languages and English. Preserves educational terminology.",
  inputSchema: z.object({
    text: z.string().describe("Text to translate"),
    sourceLanguage: languageSchema.describe("Source language code"),
    targetLanguage: languageSchema.describe("Target language code"),
    preserveTerminology: z
      .boolean()
      .default(true)
      .describe("Preserve educational terms"),
  }),
  outputSchema: z.object({
    translation: z.string(),
    sourceLanguage: z.string(),
    targetLanguage: z.string(),
    confidence: z.number(),
    terminologyNotes: z.array(z.string()).optional(),
  }),
});

export const translateContentServer = translateContentToolDef.server(
  async (args) => {
    const response = await fetch("/api/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(args),
    });
    const data = await response.json();
    return data;
  }
);

// ============================================================================
// Document Tools (with approval)
// ============================================================================

export const downloadDocumentToolDef = toolDefinition({
  name: "downloadDocument",
  description:
    "Download a curriculum document (PDF, syllabus, etc.). Requires approval for large downloads.",
  inputSchema: z.object({
    documentId: z.string().describe("Document ID to download"),
    format: z.enum(["pdf", "html", "markdown"]).default("pdf"),
  }),
  outputSchema: z.object({
    success: z.boolean(),
    downloadUrl: z.string().optional(),
    fileName: z.string().optional(),
    fileSize: z.number().optional(),
    error: z.string().optional(),
  }),
  needsApproval: true, // Requires user approval
});

export const downloadDocumentServer = downloadDocumentToolDef.server(
  async (args) => {
    // This would connect to the backend document service
    return {
      success: true,
      downloadUrl: `/api/documents/${args.documentId}?format=${args.format}`,
      fileName: `document-${args.documentId}.${args.format}`,
      fileSize: 0,
    };
  }
);

export const downloadDocumentClient = downloadDocumentToolDef.client(
  async (args) => {
    // Client-side download handling
    const url = `/api/documents/${args.documentId}?format=${args.format}`;
    window.open(url, "_blank");
    return {
      success: true,
      downloadUrl: url,
      fileName: `document-${args.documentId}.${args.format}`,
      fileSize: 0,
    };
  }
);

// ============================================================================
// Visualization Tools (client-side)
// ============================================================================

export const displayCurriculumVisualizationToolDef = toolDefinition({
  name: "displayCurriculumVisualization",
  description:
    "Display an interactive curriculum visualization in the UI. This tool MUST be used when showing curriculum structure or learning pathways.",
  inputSchema: z.object({
    subject: z.string().describe("Subject to visualize"),
    level: educationLevelSchema.describe("Education level"),
    visualizationType: z
      .enum(["tree", "graph", "timeline", "sankey"])
      .default("tree"),
  }),
  outputSchema: z.object({
    visualizationId: z.string(),
    subject: z.string(),
    level: z.string(),
  }),
});

export const displayCurriculumVisualizationClient =
  displayCurriculumVisualizationToolDef.client(async (args) => {
    // Client renders the visualization component
    return {
      visualizationId: `viz-${Date.now()}`,
      subject: args.subject,
      level: args.level,
    };
  });

// ============================================================================
// Export Server and Client Tools
// ============================================================================

/**
 * Server tools - used by the backend/agent
 */
export const serverTools = [
  hybridSearchServer,
  semanticSearchServer,
  getLearningOutcomesServer,
  getSubjectsServer,
  translateContentServer,
  downloadDocumentServer,
  displayCurriculumVisualizationToolDef, // Definition only for client rendering
];

/**
 * Client tools - used by the frontend
 */
export const clientTools = createClientTools(
  downloadDocumentClient,
  displayCurriculumVisualizationClient
);

/**
 * All tool definitions (for documentation/schema export)
 */
export const toolDefinitions = [
  hybridSearchToolDef,
  semanticSearchToolDef,
  getLearningOutcomesToolDef,
  getSubjectsToolDef,
  translateContentToolDef,
  downloadDocumentToolDef,
  displayCurriculumVisualizationToolDef,
];
