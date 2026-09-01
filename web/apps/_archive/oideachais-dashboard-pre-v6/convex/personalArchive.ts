/**
 * Convex actions + queries for the UoG personal-archive chat-over-my-archive
 * surface.
 *
 * Per the 2026-08-23-uog-personal-archive-tertiary-modules-v1 change
 * (WS10 — Convex + CopilotKit + Genie + ADK). The 5 public symbols
 * (1 action + 4 queries, plus the chatOverMyArchive action that
 * combines LLM + vector search) back the
 * `web/apps/cianfhoghlaim/components/AskMyArchive.tsx` CopilotKit
 * panel and the Genie `personal_archive_browser` tile.
 *
 * PERMANENT: this file moved from `web/apps/cianfhoghlaim/convex/` to
 * the umbrella at `web/apps/oideachais-dashboard/convex/` per the
 * 2026-08-24-wave-5-web-consolidation-v1 change K.2 + K.5. The umbrella
 * schema (`schema.ts`) declares the `archive_documents`,
 * `archive_chat_threads`, and `archive_chat_messages` tables that this
 * file queries.
 *
 * Convex v0.20+ syntax with `v` validators + `action` / `query` from
 * `./_generated/server`. The vector-search action calls the central
 * LanceDB endpoint; the chat action calls the user's preferred LLM
 * (LiteLLM proxy at /litellm/v1/chat/completions).
 */

import { v } from "convex/values";
import { action, query } from "./_generated/server";

// ---------------------------------------------------------------------------
// 1. chatOverMyArchive — the chat-with-my-archive action. Combines LLM
//    (LiteLLM proxy) + vector search (LanceDB) for grounded answers.
// ---------------------------------------------------------------------------

export const chatOverMyArchive = action({
  args: {
    thread_id: v.string(),
    user_message: v.string(),
    module_code: v.optional(v.string()),
  },
  handler: async (
    ctx,
    { thread_id, user_message, module_code }
  ) => {
    const liteUrl =
      process.env.LITELLM_PROXY_URL ?? "http://litellm:4000/v1/chat/completions";
    const lanceUrl =
      process.env.CIANFHOGHLAIM_LANCEDB_URL ?? "http://lakehouse-lance-namespace:8182";

    // 1. Vector-search the personal-archive LanceDB tables.
    const searchPayload = {
      query: user_message,
      tables: [
        "personal_archive_artefacts",
        "personal_archive_questions",
        "personal_archive_topics",
        "personal_archive_lecture_notes",
      ],
      module_code: module_code ?? null,
      limit: 6,
    };
    let hits: Array<Record<string, unknown>> = [];
    try {
      const resp = await fetch(`${lanceUrl}/v1/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(searchPayload),
      });
      if (resp.ok) {
        const json = (await resp.json()) as { hits?: Array<Record<string, unknown>> };
        hits = json.hits ?? [];
      }
    } catch (_e) {
      hits = [];
    }

    // 2. Build the prompt with the retrieved context.
    const contextBlock = hits
      .slice(0, 6)
      .map((h, i) => `[${i + 1}] ${JSON.stringify(h).slice(0, 800)}`)
      .join("\n");

    const messages = [
      {
        role: "system",
        content:
          "You are the UoG personal-archive assistant. " +
          "Ground every answer in the retrieved personal-archive context " +
          "(artefacts, questions, topics, lecture notes from " +
          "`leabharlann/ollscoil_na_gaillimhe/`). If the context is empty, " +
          "say so and ask the user to ingest more material via the " +
          "personal-archive Dagster pipeline.",
      },
      {
        role: "user",
        content:
          `Question: ${user_message}\n\n` +
          `Retrieved context (${hits.length} hits):\n${contextBlock}`,
      },
    ];

    let assistant = "";
    try {
      const resp = await fetch(liteUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: process.env.PERSONAL_ARCHIVE_LLM_MODEL ?? "gpt-4o-mini",
          messages,
          temperature: 0.2,
        }),
      });
      if (resp.ok) {
        const json = (await resp.json()) as {
          choices?: Array<{ message?: { content?: string } }>;
        };
        assistant = json.choices?.[0]?.message?.content ?? "";
      }
    } catch (_e) {
      assistant = "";
    }

    return {
      thread_id,
      assistant_message: assistant,
      hits,
      module_code: module_code ?? null,
    };
  },
});

// ---------------------------------------------------------------------------
// 2. getModuleDossier — the full per-module dossier (artefacts + questions
//    + topics + reading list + code cells + transcript rows).
// ---------------------------------------------------------------------------

export const getModuleDossier = query({
  args: { module_code: v.string() },
  handler: async (ctx, { module_code }) => {
    const artefacts = await ctx.db
      .query("personal_archive_artefacts")
      .withIndex("by_module_code", (q: any) => q.eq("module_code", module_code))
      .collect();
    const questions = await ctx.db
      .query("personal_archive_questions")
      .withIndex("by_module_code", (q: any) => q.eq("module_code", module_code))
      .collect();
    const topics = await ctx.db
      .query("personal_archive_topics")
      .withIndex("by_module_code", (q: any) => q.eq("module_code", module_code))
      .collect();
    const readingList = await ctx.db
      .query("personal_archive_reading_lists")
      .withIndex("by_module_code", (q: any) => q.eq("module_code", module_code))
      .collect();
    const codeCells = await ctx.db
      .query("personal_archive_code_cells")
      .withIndex("by_module_code", (q: any) => q.eq("module_code", module_code))
      .collect();
    const transcripts = await ctx.db
      .query("student_transcripts")
      .withIndex("by_module_code", (q: any) => q.eq("module_code", module_code))
      .collect();
    return {
      module_code,
      artefact_count: artefacts.length,
      question_count: questions.length,
      topic_count: topics.length,
      reading_list_count: readingList.length,
      code_cell_count: codeCells.length,
      transcript_row_count: transcripts.length,
      artefacts,
      questions,
      topics,
      reading_list: readingList,
      code_cells: codeCells,
      transcripts,
    };
  },
});

// ---------------------------------------------------------------------------
// 3. getQuestionsForTopic — every question whose expected_topic matches
//    `topic_name` (cross-module).
// ---------------------------------------------------------------------------

export const getQuestionsForTopic = query({
  args: { topic_name: v.string() },
  handler: async (ctx, { topic_name }) => {
    const all = await ctx.db.query("personal_archive_questions").collect();
    return all.filter((q: any) => q.expected_topic === topic_name);
  },
});

// ---------------------------------------------------------------------------
// 4. getMyAnswerForQuestion — the `my_answer_text` column for one question.
// ---------------------------------------------------------------------------

export const getMyAnswerForQuestion = query({
  args: { question_id: v.string() },
  handler: async (ctx, { question_id }) => {
    return await ctx.db
      .query("personal_archive_questions")
      .withIndex("by_question_id", (q: any) => q.eq("question_id", question_id))
      .first();
  },
});

// ---------------------------------------------------------------------------
// 5. searchSimilarQuestions — semantic search over the
//    `personal_archive_questions` LanceDB table (the F-granularity
//    "what past-paper Q is similar to X" surface).
// ---------------------------------------------------------------------------

export const searchSimilarQuestions = action({
  args: {
    question_text: v.string(),
    limit: v.optional(v.number()),
  },
  handler: async (
    ctx,
    { question_text, limit }
  ) => {
    const lanceUrl =
      process.env.CIANFHOGHLAIM_LANCEDB_URL ?? "http://lakehouse-lance-namespace:8182";
    try {
      const resp = await fetch(`${lanceUrl}/v1/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: question_text,
          tables: ["personal_archive_questions"],
          limit: limit ?? 5,
        }),
      });
      if (!resp.ok) {
        return { hits: [], error: `lance ${resp.status}` };
      }
      const json = (await resp.json()) as { hits?: Array<Record<string, unknown>> };
      return { hits: json.hits ?? [] };
    } catch (e) {
      return { hits: [], error: String(e) };
    }
  },
});
