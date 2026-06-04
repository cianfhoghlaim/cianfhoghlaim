/**
 * Pipeline Router
 *
 * oRPC procedures for interacting with FastAPI data pipelines.
 * Provides type-safe access to curriculum search, chat, and agent functionality.
 */

import { z } from "zod";
import { protectedProcedure, publicProcedure } from "../index";
import {
  getFastAPIClient,
  type ChatRequest,
  type SearchRequest,
} from "../clients/fastapi-client";

// =============================================================================
// Input Schemas
// =============================================================================

const chatInputSchema = z.object({
  message: z.string().min(1).max(10000),
  sessionId: z.string().optional(),
  language: z.enum(["en", "ga"]).default("en"),
  agents: z.array(z.string()).optional(),
});

const searchInputSchema = z.object({
  query: z.string().min(1).max(500),
  language: z.enum(["en", "ga"]).optional(),
  nation: z.enum(["ireland", "uk", "scotland", "wales"]).optional(),
  limit: z.number().min(1).max(100).default(10),
  offset: z.number().min(0).default(0),
});

const unifiedSearchInputSchema = searchInputSchema.extend({
  domains: z
    .array(z.enum(["curriculum", "folklore", "terminology"]))
    .optional(),
});

const sessionInputSchema = z.object({
  sessionId: z.string(),
});

// =============================================================================
// Pipeline Router
// =============================================================================

export const pipelineRouter = {
  /**
   * Check FastAPI health
   */
  health: publicProcedure.handler(async () => {
    const client = getFastAPIClient();
    const health = await client.health();
    return {
      status: health.status,
      timestamp: health.timestamp,
      services: Object.entries(health.services).map(([name, service]) => ({
        name,
        status: service.status,
        latencyMs: service.latency_ms,
      })),
    };
  }),

  /**
   * Send a chat message (non-streaming)
   */
  chat: protectedProcedure
    .input(chatInputSchema)
    .handler(async ({ input, context }) => {
      const client = getFastAPIClient();

      const request: ChatRequest = {
        message: input.message,
        session_id: input.sessionId,
        language: input.language,
        stream: false,
        agents: input.agents,
      };

      const response = await client.chat(request, context.session);

      return {
        message: response.message,
        sessionId: response.session_id,
        sources: response.sources?.map((s) => ({
          id: s.id,
          title: s.title,
          url: s.url,
          snippet: s.snippet,
          score: s.score,
        })),
        agentsUsed: response.agents_used,
      };
    }),

  /**
   * Search curriculum content
   */
  searchCurriculum: protectedProcedure
    .input(searchInputSchema)
    .handler(async ({ input, context }) => {
      const client = getFastAPIClient();

      const request: SearchRequest = {
        query: input.query,
        language: input.language,
        nation: input.nation,
        limit: input.limit,
        offset: input.offset,
      };

      const response = await client.searchCurriculum(request, context.session);

      return {
        results: response.results.map((r) => ({
          id: r.id,
          title: r.title,
          content: r.content,
          score: r.score,
          metadata: r.metadata,
        })),
        total: response.total,
        query: response.query,
      };
    }),

  /**
   * Search folklore collection
   */
  searchFolklore: protectedProcedure
    .input(searchInputSchema)
    .handler(async ({ input, context }) => {
      const client = getFastAPIClient();

      const request: SearchRequest = {
        query: input.query,
        language: input.language,
        nation: input.nation,
        limit: input.limit,
        offset: input.offset,
      };

      const response = await client.searchFolklore(request, context.session);

      return {
        results: response.results.map((r) => ({
          id: r.id,
          title: r.title,
          content: r.content,
          score: r.score,
          metadata: r.metadata,
        })),
        total: response.total,
        query: response.query,
      };
    }),

  /**
   * Search terminology database
   */
  searchTerminology: protectedProcedure
    .input(searchInputSchema)
    .handler(async ({ input, context }) => {
      const client = getFastAPIClient();

      const request: SearchRequest = {
        query: input.query,
        language: input.language,
        limit: input.limit,
        offset: input.offset,
      };

      const response = await client.searchTerminology(request, context.session);

      return {
        results: response.results.map((r) => ({
          id: r.id,
          title: r.title,
          content: r.content,
          score: r.score,
          metadata: r.metadata,
        })),
        total: response.total,
        query: response.query,
      };
    }),

  /**
   * Unified search across all domains
   */
  searchUnified: protectedProcedure
    .input(unifiedSearchInputSchema)
    .handler(async ({ input, context }) => {
      const client = getFastAPIClient();

      const response = await client.searchUnified(
        {
          query: input.query,
          language: input.language,
          nation: input.nation,
          limit: input.limit,
          offset: input.offset,
          domains: input.domains,
        },
        context.session
      );

      return {
        results: response.results.map((r) => ({
          id: r.id,
          title: r.title,
          content: r.content,
          score: r.score,
          metadata: r.metadata,
        })),
        total: response.total,
        query: response.query,
        facets: response.facets,
      };
    }),

  /**
   * Get chat session info
   */
  getSession: protectedProcedure
    .input(sessionInputSchema)
    .handler(async ({ input, context }) => {
      const client = getFastAPIClient();

      const session = await client.getSession(input.sessionId, context.session);

      return {
        sessionId: session.session_id,
        messages: session.messages.map((m) => ({
          id: m.id,
          role: m.role,
          content: m.content,
          toolCalls: m.tool_calls,
        })),
        createdAt: session.created_at,
      };
    }),

  /**
   * Clear a chat session
   */
  clearSession: protectedProcedure
    .input(sessionInputSchema)
    .handler(async ({ input, context }) => {
      const client = getFastAPIClient();
      await client.clearSession(input.sessionId, context.session);
      return { success: true };
    }),
};
