import { anthropic } from "@ai-sdk/anthropic";
import { streamText } from "ai";
import type { ChatRequest } from "../../contracts/schemas.js";

/**
 * Handle AI chat streaming requests
 */
export async function handleChatStream(request: ChatRequest) {
  const { messages, model, temperature } = request;

  try {
    const result = streamText({
      model: anthropic(model),
      messages,
      temperature,
      maxTokens: 4096,
    });

    return result.toDataStreamResponse();
  } catch (error) {
    console.error("Chat stream error:", error);
    throw new Error(
      error instanceof Error ? error.message : "Failed to generate response"
    );
  }
}

/**
 * Handle AI chat with MCP tool calling
 */
export async function handleChatWithTools(request: ChatRequest) {
  const { messages, model, temperature } = request;

  try {
    // Define tools that can be called by the AI
    const tools = {
      add: {
        description: "Add two numbers together",
        parameters: {
          type: "object",
          properties: {
            a: { type: "number", description: "First number" },
            b: { type: "number", description: "Second number" },
          },
          required: ["a", "b"],
        },
        execute: async ({ a, b }: { a: number; b: number }) => {
          return { result: a + b };
        },
      },
      search: {
        description: "Search for information",
        parameters: {
          type: "object",
          properties: {
            query: { type: "string", description: "Search query" },
            limit: {
              type: "number",
              description: "Max results",
              default: 10,
            },
          },
          required: ["query"],
        },
        execute: async ({
          query,
          limit = 10,
        }: {
          query: string;
          limit?: number;
        }) => {
          // Simulated search
          return {
            results: Array.from({ length: Math.min(limit, 3) }, (_, i) => ({
              title: `Result ${i + 1} for "${query}"`,
              snippet: `Relevant content for ${query}`,
            })),
          };
        },
      },
    };

    const result = streamText({
      model: anthropic(model),
      messages,
      temperature,
      maxTokens: 4096,
      tools,
    });

    return result.toDataStreamResponse();
  } catch (error) {
    console.error("Chat with tools error:", error);
    throw new Error(
      error instanceof Error ? error.message : "Failed to generate response"
    );
  }
}
