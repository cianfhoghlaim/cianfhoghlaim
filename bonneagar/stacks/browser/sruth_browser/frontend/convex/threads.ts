/**
 * Thread queries and mutations for browser agent.
 *
 * Provides:
 * - Thread CRUD operations
 * - Message management
 * - Real-time subscriptions
 */

import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// =========================================================================
// Thread Queries
// =========================================================================

/**
 * Get a thread by ID with all messages
 */
export const get = query({
  args: { threadId: v.id("threads") },
  handler: async (ctx, args) => {
    const thread = await ctx.db.get(args.threadId);
    if (!thread) return null;

    const messages = await ctx.db
      .query("messages")
      .withIndex("by_thread", (q) => q.eq("threadId", args.threadId))
      .order("asc")
      .collect();

    return { thread, messages };
  },
});

/**
 * List threads for a user
 */
export const listByUser = query({
  args: {
    userId: v.string(),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const limit = args.limit ?? 50;

    return await ctx.db
      .query("threads")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .order("desc")
      .take(limit);
  },
});

/**
 * List threads by session
 */
export const listBySession = query({
  args: {
    sessionId: v.string(),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const limit = args.limit ?? 50;

    return await ctx.db
      .query("threads")
      .withIndex("by_session", (q) => q.eq("sessionId", args.sessionId))
      .order("desc")
      .take(limit);
  },
});

/**
 * Get pending approvals for a thread
 */
export const getPendingApprovals = query({
  args: { threadId: v.id("threads") },
  handler: async (ctx, args) => {
    const now = Date.now();

    const approvals = await ctx.db
      .query("approvals")
      .withIndex("by_thread", (q) => q.eq("threadId", args.threadId))
      .filter((q) => q.eq(q.field("status"), "pending"))
      .collect();

    // Filter out expired
    return approvals.filter(
      (a) => !a.expiresAt || a.expiresAt > now
    );
  },
});

// =========================================================================
// Thread Mutations
// =========================================================================

/**
 * Create a new thread
 */
export const create = mutation({
  args: {
    userId: v.string(),
    sessionId: v.string(),
    status: v.optional(v.string()),
    metadata: v.optional(v.any()),
    title: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const threadId = await ctx.db.insert("threads", {
      userId: args.userId,
      sessionId: args.sessionId,
      status: args.status ?? "running",
      metadata: args.metadata,
      title: args.title,
      lastActivityAt: Date.now(),
    });

    return threadId;
  },
});

/**
 * Update thread status
 */
export const updateStatus = mutation({
  args: {
    threadId: v.id("threads"),
    status: v.string(),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.threadId, {
      status: args.status,
      lastActivityAt: Date.now(),
    });
  },
});

/**
 * Update thread metadata
 */
export const updateMetadata = mutation({
  args: {
    threadId: v.id("threads"),
    metadata: v.any(),
  },
  handler: async (ctx, args) => {
    const thread = await ctx.db.get(args.threadId);
    if (!thread) throw new Error("Thread not found");

    await ctx.db.patch(args.threadId, {
      metadata: { ...thread.metadata, ...args.metadata },
      lastActivityAt: Date.now(),
    });
  },
});

/**
 * Delete a thread and all its messages
 */
export const deleteThread = mutation({
  args: { threadId: v.id("threads") },
  handler: async (ctx, args) => {
    // Delete all messages
    const messages = await ctx.db
      .query("messages")
      .withIndex("by_thread", (q) => q.eq("threadId", args.threadId))
      .collect();

    for (const msg of messages) {
      await ctx.db.delete(msg._id);
    }

    // Delete all events
    const events = await ctx.db
      .query("events")
      .withIndex("by_thread", (q) => q.eq("threadId", args.threadId))
      .collect();

    for (const event of events) {
      await ctx.db.delete(event._id);
    }

    // Delete all approvals
    const approvals = await ctx.db
      .query("approvals")
      .withIndex("by_thread", (q) => q.eq("threadId", args.threadId))
      .collect();

    for (const approval of approvals) {
      await ctx.db.delete(approval._id);
    }

    // Delete thread
    await ctx.db.delete(args.threadId);
  },
});

// =========================================================================
// Message Mutations
// =========================================================================

/**
 * Add a message to a thread
 */
export const addMessage = mutation({
  args: {
    threadId: v.id("threads"),
    role: v.string(),
    content: v.string(),
    toolCalls: v.optional(v.array(v.any())),
    metadata: v.optional(v.any()),
  },
  handler: async (ctx, args) => {
    const messageId = await ctx.db.insert("messages", {
      threadId: args.threadId,
      role: args.role,
      content: args.content,
      toolCalls: args.toolCalls,
      timestamp: Date.now(),
      metadata: args.metadata,
    });

    // Update thread activity
    await ctx.db.patch(args.threadId, {
      lastActivityAt: Date.now(),
    });

    return messageId;
  },
});

/**
 * Add tool results to a message
 */
export const addToolResults = mutation({
  args: {
    threadId: v.id("threads"),
    toolResults: v.array(
      v.object({
        toolCallId: v.string(),
        result: v.any(),
        error: v.optional(v.string()),
      })
    ),
  },
  handler: async (ctx, args) => {
    const messageId = await ctx.db.insert("messages", {
      threadId: args.threadId,
      role: "tool",
      content: "",
      toolResults: args.toolResults,
      timestamp: Date.now(),
    });

    return messageId;
  },
});

// =========================================================================
// Approval Mutations
// =========================================================================

/**
 * Create an approval request
 */
export const createApproval = mutation({
  args: {
    threadId: v.id("threads"),
    sessionId: v.string(),
    action: v.string(),
    details: v.optional(v.any()),
    awakeableId: v.string(),
    expiresAt: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const approvalId = await ctx.db.insert("approvals", {
      threadId: args.threadId,
      sessionId: args.sessionId,
      action: args.action,
      details: args.details,
      status: "pending",
      awakeableId: args.awakeableId,
      createdAt: Date.now(),
      expiresAt: args.expiresAt,
    });

    return approvalId;
  },
});

/**
 * Handle approval response
 */
export const handleApproval = mutation({
  args: {
    approvalId: v.id("approvals"),
    approved: v.boolean(),
    decidedBy: v.optional(v.string()),
    reason: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const approval = await ctx.db.get(args.approvalId);
    if (!approval) throw new Error("Approval not found");

    if (approval.status !== "pending") {
      throw new Error(`Approval already ${approval.status}`);
    }

    await ctx.db.patch(args.approvalId, {
      status: args.approved ? "approved" : "rejected",
      decidedAt: Date.now(),
      decidedBy: args.decidedBy ?? "user",
      reason: args.reason,
    });

    return { awakeableId: approval.awakeableId, approved: args.approved };
  },
});
