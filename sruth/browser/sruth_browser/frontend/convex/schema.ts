/**
 * Convex schema for browser agent thread/message persistence.
 *
 * Provides real-time sync for:
 * - Thread management (conversation sessions)
 * - Message history with tool calls
 * - Agent events for UI updates
 * - Workflow state tracking
 */

import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // =========================================================================
  // Threads - Conversation sessions
  // =========================================================================
  threads: defineTable({
    userId: v.string(),
    sessionId: v.string(),
    status: v.string(), // "running" | "completed" | "failed" | "paused"
    metadata: v.optional(v.any()),
    title: v.optional(v.string()),
    lastActivityAt: v.optional(v.number()),
  })
    .index("by_user", ["userId"])
    .index("by_session", ["sessionId"])
    .index("by_status", ["status"]),

  // =========================================================================
  // Messages - Thread message history
  // =========================================================================
  messages: defineTable({
    threadId: v.id("threads"),
    role: v.string(), // "user" | "assistant" | "tool" | "system"
    content: v.string(),
    toolCalls: v.optional(
      v.array(
        v.object({
          id: v.string(),
          name: v.string(),
          arguments: v.any(),
        })
      )
    ),
    toolResults: v.optional(
      v.array(
        v.object({
          toolCallId: v.string(),
          result: v.any(),
          error: v.optional(v.string()),
        })
      )
    ),
    timestamp: v.number(),
    metadata: v.optional(v.any()),
  }).index("by_thread", ["threadId"]),

  // =========================================================================
  // Events - Real-time agent events
  // =========================================================================
  events: defineTable({
    threadId: v.id("threads"),
    eventType: v.string(), // "RUN_STARTED" | "TEXT_DELTA" | "TOOL_CALL_START" | etc.
    data: v.any(),
    timestamp: v.number(),
    consumed: v.optional(v.boolean()),
  })
    .index("by_thread", ["threadId"])
    .index("by_thread_and_type", ["threadId", "eventType"]),

  // =========================================================================
  // Approvals - Human-in-the-loop requests
  // =========================================================================
  approvals: defineTable({
    threadId: v.id("threads"),
    sessionId: v.string(),
    action: v.string(),
    details: v.optional(v.any()),
    status: v.string(), // "pending" | "approved" | "rejected" | "expired"
    awakeableId: v.string(),
    createdAt: v.number(),
    expiresAt: v.optional(v.number()),
    decidedAt: v.optional(v.number()),
    decidedBy: v.optional(v.string()),
    reason: v.optional(v.string()),
  })
    .index("by_thread", ["threadId"])
    .index("by_session", ["sessionId"])
    .index("by_status", ["status"])
    .index("by_awakeable", ["awakeableId"]),

  // =========================================================================
  // Workflows - Durable workflow state
  // =========================================================================
  workflows: defineTable({
    name: v.string(),
    threadId: v.optional(v.id("threads")),
    status: v.string(), // "pending" | "running" | "completed" | "failed"
    args: v.any(),
    result: v.optional(v.any()),
    error: v.optional(v.string()),
    currentStep: v.optional(v.string()),
    steps: v.optional(
      v.array(
        v.object({
          name: v.string(),
          status: v.string(),
          startedAt: v.optional(v.number()),
          completedAt: v.optional(v.number()),
          result: v.optional(v.any()),
          error: v.optional(v.string()),
        })
      )
    ),
    startedAt: v.number(),
    completedAt: v.optional(v.number()),
  })
    .index("by_name", ["name"])
    .index("by_thread", ["threadId"])
    .index("by_status", ["status"]),

  // =========================================================================
  // Checkpoints - Pipeline checkpoints for resume
  // =========================================================================
  checkpoints: defineTable({
    workflowId: v.id("workflows"),
    stepName: v.string(),
    input: v.optional(v.any()),
    output: v.optional(v.any()),
    timestamp: v.number(),
  })
    .index("by_workflow", ["workflowId"])
    .index("by_workflow_and_step", ["workflowId", "stepName"]),

  // =========================================================================
  // Jobs - Workpool job queue
  // =========================================================================
  jobs: defineTable({
    type: v.string(), // "scrape" | "screenshot" | "extract"
    payload: v.any(),
    status: v.string(), // "pending" | "running" | "completed" | "failed"
    priority: v.optional(v.number()),
    attempts: v.optional(v.number()),
    maxAttempts: v.optional(v.number()),
    result: v.optional(v.any()),
    error: v.optional(v.string()),
    createdAt: v.number(),
    startedAt: v.optional(v.number()),
    completedAt: v.optional(v.number()),
    workerId: v.optional(v.string()),
  })
    .index("by_status", ["status"])
    .index("by_type", ["type"])
    .index("by_priority", ["priority"]),
});
