/**
 * Event queries and mutations for real-time UI updates.
 *
 * Events provide real-time streaming from the browser agent
 * to connected frontend clients.
 */

import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// =========================================================================
// Event Queries
// =========================================================================

/**
 * Subscribe to events for a thread
 *
 * This query automatically updates when new events are published,
 * providing real-time streaming to the frontend.
 */
export const subscribe = query({
  args: {
    threadId: v.id("threads"),
    limit: v.optional(v.number()),
    afterTimestamp: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const limit = args.limit ?? 100;

    let query = ctx.db
      .query("events")
      .withIndex("by_thread", (q) => q.eq("threadId", args.threadId));

    if (args.afterTimestamp) {
      query = query.filter((q) =>
        q.gt(q.field("timestamp"), args.afterTimestamp)
      );
    }

    return await query.order("asc").take(limit);
  },
});

/**
 * Get latest event for a thread
 */
export const getLatest = query({
  args: { threadId: v.id("threads") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("events")
      .withIndex("by_thread", (q) => q.eq("threadId", args.threadId))
      .order("desc")
      .first();
  },
});

/**
 * Get events by type
 */
export const getByType = query({
  args: {
    threadId: v.id("threads"),
    eventType: v.string(),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const limit = args.limit ?? 50;

    return await ctx.db
      .query("events")
      .withIndex("by_thread_and_type", (q) =>
        q.eq("threadId", args.threadId).eq("eventType", args.eventType)
      )
      .order("desc")
      .take(limit);
  },
});

// =========================================================================
// Event Mutations
// =========================================================================

/**
 * Publish an event to a thread
 *
 * Called by the Python backend to stream events to the frontend.
 */
export const publish = mutation({
  args: {
    threadId: v.id("threads"),
    eventType: v.string(),
    data: v.any(),
    timestamp: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const eventId = await ctx.db.insert("events", {
      threadId: args.threadId,
      eventType: args.eventType,
      data: args.data,
      timestamp: args.timestamp ?? Date.now(),
      consumed: false,
    });

    // Update thread activity
    await ctx.db.patch(args.threadId, {
      lastActivityAt: Date.now(),
    });

    return eventId;
  },
});

/**
 * Publish multiple events at once
 */
export const publishBatch = mutation({
  args: {
    threadId: v.id("threads"),
    events: v.array(
      v.object({
        eventType: v.string(),
        data: v.any(),
        timestamp: v.optional(v.number()),
      })
    ),
  },
  handler: async (ctx, args) => {
    const now = Date.now();
    const eventIds: string[] = [];

    for (const event of args.events) {
      const eventId = await ctx.db.insert("events", {
        threadId: args.threadId,
        eventType: event.eventType,
        data: event.data,
        timestamp: event.timestamp ?? now,
        consumed: false,
      });
      eventIds.push(eventId);
    }

    // Update thread activity
    await ctx.db.patch(args.threadId, {
      lastActivityAt: now,
    });

    return eventIds;
  },
});

/**
 * Mark events as consumed
 */
export const markConsumed = mutation({
  args: {
    eventIds: v.array(v.id("events")),
  },
  handler: async (ctx, args) => {
    for (const eventId of args.eventIds) {
      await ctx.db.patch(eventId, { consumed: true });
    }
  },
});

/**
 * Clean up old events
 *
 * Called periodically to remove events older than a threshold.
 */
export const cleanup = mutation({
  args: {
    threadId: v.id("threads"),
    olderThanMs: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const threshold = Date.now() - (args.olderThanMs ?? 24 * 60 * 60 * 1000); // 24h default

    const oldEvents = await ctx.db
      .query("events")
      .withIndex("by_thread", (q) => q.eq("threadId", args.threadId))
      .filter((q) => q.lt(q.field("timestamp"), threshold))
      .collect();

    for (const event of oldEvents) {
      await ctx.db.delete(event._id);
    }

    return { deleted: oldEvents.length };
  },
});
