import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  personas: defineTable({
    slug: v.string(),
    displayName: v.string(),
    themeMode: v.union(v.literal("dark"), v.literal("light")),
    accentColor: v.string(),
    dataSources: v.array(v.string()),
    isActive: v.boolean(),
  }).index("by_slug", ["slug"]),

  organizations: defineTable({
    slug: v.string(),
    name: v.string(),
    isPublic: v.boolean(),
    createdAt: v.number(),
  }).index("by_slug", ["slug"]),

  memberships: defineTable({
    orgId: v.id("organizations"),
    userId: v.string(),
    role: v.union(v.literal("owner"), v.literal("admin"), v.literal("member"), v.literal("viewer")),
    invitedAt: v.number(),
  })
    .index("by_org", ["orgId"])
    .index("by_user", ["userId"])
    .index("by_user_org", ["userId", "orgId"]),

  portfolioPages: defineTable({
    personaSlug: v.string(),
    route: v.string(),
    title: v.object({ en: v.string(), ga: v.string() }),
    sections: v.array(v.object({
      id: v.string(),
      type: v.string(),
      order: v.number(),
      dataSource: v.string(),
      config: v.optional(v.any()),
    })),
    updatedAt: v.number(),
  }).index("by_persona_route", ["personaSlug", "route"]),

  cvEntries: defineTable({
    personaSlug: v.string(),
    type: v.union(
      v.literal("education"), v.literal("award"),
      v.literal("publication"), v.literal("reference"), v.literal("experience"),
    ),
    title: v.string(),
    institution: v.optional(v.string()),
    date: v.string(),
    description: v.object({ en: v.string(), ga: v.optional(v.string()) }),
    url: v.optional(v.string()),
    extractedAt: v.number(),
  })
    .index("by_persona_type", ["personaSlug", "type"])
    .index("by_persona_date", ["personaSlug", "date"]),

  musicEntries: defineTable({
    personaSlug: v.string(),
    source: v.union(v.literal("spotify"), v.literal("soundcloud")),
    externalId: v.string(),
    title: v.string(),
    artist: v.string(),
    url: v.string(),
    playCount: v.optional(v.number()),
    syncedAt: v.number(),
  }).index("by_persona_source", ["personaSlug", "source"]),

  githubRepos: defineTable({
    personaSlug: v.string(),
    repoName: v.string(),
    description: v.optional(v.string()),
    language: v.optional(v.string()),
    stars: v.number(),
    forks: v.number(),
    url: v.string(),
    syncedAt: v.number(),
  }).index("by_persona", ["personaSlug"]),

  contactSubmissions: defineTable({
    personaSlug: v.string(),
    name: v.string(),
    email: v.string(),
    message: v.string(),
    createdAt: v.number(),
    isRead: v.boolean(),
  }).index("by_persona", ["personaSlug"]),

  invites: defineTable({
    orgId: v.id("organizations"),
    email: v.string(),
    role: v.string(),
    code: v.string(),
    status: v.union(v.literal("pending"), v.literal("accepted"), v.literal("expired")),
    createdAt: v.number(),
    expiresAt: v.number(),
  })
    .index("by_code", ["code"])
    .index("by_org", ["orgId"]),
});
