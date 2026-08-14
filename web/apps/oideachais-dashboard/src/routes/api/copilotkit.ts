/**
 * CopilotKit Runtime Endpoint
 * Provides AI-powered actions for OCR comparison analysis
 */
import { createAPIFileRoute } from "@tanstack/start/api";
import {
  CopilotRuntime,
  OpenAIAdapter,
  copilotRuntimeNextJSPagesRouterEndpoint,
} from "@copilotkit/runtime";

// Model recommendation action
const recommendModelAction = {
  name: "recommendModel",
  description:
    "Recommend the best OCR model based on document characteristics and requirements",
  parameters: [
    {
      name: "documentType",
      type: "string",
      description:
        "Type of document (pdf, image, scan, handwritten, typed, mixed)",
      required: true,
    },
    {
      name: "hasImages",
      type: "boolean",
      description: "Whether the document contains images",
      required: false,
    },
    {
      name: "hasTables",
      type: "boolean",
      description: "Whether the document contains tables",
      required: false,
    },
    {
      name: "language",
      type: "string",
      description: "Primary language of the document (e.g., English, Irish)",
      required: false,
    },
    {
      name: "prioritize",
      type: "string",
      description: "What to prioritize: speed, accuracy, or balanced",
      required: false,
    },
  ],
  handler: async (args: {
    documentType: string;
    hasImages?: boolean;
    hasTables?: boolean;
    language?: string;
    prioritize?: string;
  }) => {
    const { documentType, hasImages, hasTables, language, prioritize } = args;

    // Model recommendation logic based on capabilities
    const recommendations = [];

    // Irish language documents need specialized models
    if (language?.toLowerCase() === "irish" || language?.toLowerCase() === "ga") {
      recommendations.push({
        model: "qwen3-vl-30b",
        reason: "Best Irish language support with vision capabilities",
        score: 95,
      });
    }

    // Documents with tables
    if (hasTables) {
      recommendations.push({
        model: "dots-ocr",
        reason: "SOTA layout detection with excellent table recognition",
        score: 92,
      });
      recommendations.push({
        model: "olmocr-7b",
        reason: "Specialized for dense text and table extraction",
        score: 88,
      });
    }

    // Fast extraction priority
    if (prioritize === "speed") {
      recommendations.push({
        model: "pymupdf4llm",
        reason: "Fastest PDF text extraction, no ML overhead",
        score: 90,
      });
      recommendations.push({
        model: "paddleocr",
        reason: "Fast OCR with good accuracy balance",
        score: 85,
      });
    }

    // High accuracy priority
    if (prioritize === "accuracy") {
      recommendations.push({
        model: "marker",
        reason: "ML-based layout analysis with highest quality output",
        score: 94,
      });
      recommendations.push({
        model: "docling",
        reason: "IBM Document Intelligence for complex layouts",
        score: 91,
      });
    }

    // Image-heavy documents
    if (hasImages) {
      recommendations.push({
        model: "gemma-3-27b",
        reason: "Strong vision capabilities for mixed content",
        score: 87,
      });
    }

    // Default balanced recommendations
    if (recommendations.length === 0) {
      recommendations.push({
        model: "qwen3-vl-30b",
        reason: "Best overall accuracy for general documents",
        score: 90,
      });
      recommendations.push({
        model: "marker",
        reason: "High-quality layout preservation",
        score: 88,
      });
    }

    // Sort by score and return top 3
    return recommendations.sort((a, b) => b.score - a.score).slice(0, 3);
  },
};

// Result explanation action
const explainResultAction = {
  name: "explainResult",
  description:
    "Explain OCR output quality and highlight potential issues or improvements",
  parameters: [
    {
      name: "modelName",
      type: "string",
      description: "Name of the OCR model used",
      required: true,
    },
    {
      name: "resultSample",
      type: "string",
      description: "Sample of the OCR output (first 1000 chars)",
      required: true,
    },
    {
      name: "durationMs",
      type: "number",
      description: "Processing duration in milliseconds",
      required: false,
    },
    {
      name: "characterCount",
      type: "number",
      description: "Total character count of output",
      required: false,
    },
  ],
  handler: async (args: {
    modelName: string;
    resultSample: string;
    durationMs?: number;
    characterCount?: number;
  }) => {
    const { modelName, resultSample, durationMs, characterCount } = args;

    // Analyze the result for common issues
    const issues: string[] = [];
    const strengths: string[] = [];

    // Check for formatting preservation
    if (resultSample.includes("##") || resultSample.includes("**")) {
      strengths.push("Markdown formatting preserved");
    }

    // Check for table detection
    if (resultSample.includes("|") && resultSample.includes("-|-")) {
      strengths.push("Table structure detected and formatted");
    }

    // Check for potential OCR errors (common patterns)
    if (/[0O][0O]/.test(resultSample)) {
      issues.push("Possible 0/O confusion in text");
    }
    if (/[1lI][1lI]/.test(resultSample)) {
      issues.push("Possible 1/l/I confusion in text");
    }

    // Check for Irish language patterns (fada marks)
    const fadaPattern = /[áéíóúÁÉÍÓÚ]/g;
    const fadaCount = (resultSample.match(fadaPattern) || []).length;
    if (fadaCount > 0) {
      strengths.push(`Irish fada marks detected (${fadaCount} found)`);
    }

    // Performance analysis
    let performanceNote = "";
    if (durationMs) {
      if (durationMs < 1000) {
        performanceNote = "Excellent processing speed";
      } else if (durationMs < 5000) {
        performanceNote = "Good processing speed";
      } else if (durationMs < 15000) {
        performanceNote = "Moderate processing time";
      } else {
        performanceNote = "Slow processing - consider faster alternatives";
      }
    }

    return {
      modelName,
      qualityScore: issues.length === 0 ? "High" : issues.length < 3 ? "Medium" : "Low",
      strengths,
      issues,
      performanceNote,
      recommendation:
        issues.length > 2
          ? "Consider trying Marker or dots.ocr for better accuracy"
          : "Output quality appears good",
    };
  },
};

// Compare multiple results action
const compareResultsAction = {
  name: "compareResults",
  description: "Compare OCR outputs from multiple models and provide analysis",
  parameters: [
    {
      name: "results",
      type: "array",
      description: "Array of model results with name and sample",
      required: true,
    },
  ],
  handler: async (args: {
    results: Array<{ modelName: string; sample: string; durationMs?: number }>;
  }) => {
    const { results } = args;

    if (results.length < 2) {
      return { error: "Need at least 2 results to compare" };
    }

    // Calculate similarity between outputs
    const similarities: Array<{
      models: string[];
      similarity: number;
    }> = [];

    for (let i = 0; i < results.length; i++) {
      for (let j = i + 1; j < results.length; j++) {
        const a = results[i].sample.toLowerCase();
        const b = results[j].sample.toLowerCase();

        // Simple word overlap similarity
        const wordsA = new Set(a.split(/\s+/));
        const wordsB = new Set(b.split(/\s+/));
        const intersection = new Set([...wordsA].filter((x) => wordsB.has(x)));
        const union = new Set([...wordsA, ...wordsB]);
        const similarity = Math.round((intersection.size / union.size) * 100);

        similarities.push({
          models: [results[i].modelName, results[j].modelName],
          similarity,
        });
      }
    }

    // Find the fastest model
    const fastestResult = results
      .filter((r) => r.durationMs)
      .sort((a, b) => (a.durationMs || 0) - (b.durationMs || 0))[0];

    // Find the most verbose output (often correlates with completeness)
    const mostComplete = results.sort(
      (a, b) => b.sample.length - a.sample.length
    )[0];

    return {
      similarities,
      fastestModel: fastestResult?.modelName || "Unknown",
      mostCompleteModel: mostComplete?.modelName || "Unknown",
      recommendation:
        similarities[0]?.similarity > 90
          ? `High agreement (${similarities[0].similarity}%) between models - results are reliable`
          : `Moderate variation between models - review outputs manually for best result`,
    };
  },
};

// Create the CopilotKit runtime with actions
const runtime = new CopilotRuntime({
  actions: [recommendModelAction, explainResultAction, compareResultsAction],
});

// API Route handler
export const APIRoute = createAPIFileRoute("/api/copilotkit")({
  POST: async ({ request }) => {
    const openaiApiKey = process.env.OPENAI_API_KEY;

    if (!openaiApiKey) {
      return new Response(
        JSON.stringify({ error: "OPENAI_API_KEY not configured" }),
        {
          status: 500,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    const adapter = new OpenAIAdapter({ openaiApiKey });

    try {
      const body = await request.json();

      // Handle the CopilotKit runtime request
      const result = await runtime.process({
        ...body,
        adapter,
      });

      return new Response(JSON.stringify(result), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    } catch (error) {
      console.error("CopilotKit runtime error:", error);
      return new Response(
        JSON.stringify({
          error: error instanceof Error ? error.message : "Unknown error",
        }),
        {
          status: 500,
          headers: { "Content-Type": "application/json" },
        }
      );
    }
  },
});
