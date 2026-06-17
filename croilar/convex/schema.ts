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

  // ── Web stack observability (croilar-devtools-hub) ────────────────────
  tanstackRoutes: defineTable({
    project: v.string(),
    route: v.string(),
    file: v.string(),
    isPublic: v.boolean(),
    isServer: v.boolean(),
    hasLoader: v.boolean(),
    hasAuth: v.boolean(),
    lines: v.number(),
    lastCommit: v.string(),
    lastCommitAt: v.number(),
  })
    .index("by_project", ["project"])
    .index("by_project_route", ["project", "route"]),

  convexFunctions: defineTable({
    project: v.string(),
    file: v.string(),
    name: v.string(),
    kind: v.union(
      v.literal("query"),
      v.literal("mutation"),
      v.literal("action"),
      v.literal("internalQuery"),
      v.literal("internalMutation"),
      v.literal("internalAction"),
    ),
    args: v.optional(v.string()),
    returns: v.optional(v.string()),
    lines: v.number(),
    lastCommit: v.string(),
  })
    .index("by_project_file", ["project", "file"])
    .index("by_project_name", ["project", "name"]),

  cloudflareResources: defineTable({
    project: v.string(),
    kind: v.union(
      v.literal("worker"),
      v.literal("pages"),
      v.literal("r2"),
      v.literal("kv"),
      v.literal("d1"),
      v.literal("durable_object"),
    ),
    name: v.string(),
    account: v.optional(v.string()),
    wranglerConfig: v.optional(v.string()),
    lastDeployed: v.optional(v.number()),
    version: v.optional(v.string()),
  }).index("by_project_kind", ["project", "kind"]),

  bamlSchemas: defineTable({
    project: v.string(),
    file: v.string(),
    classCount: v.number(),
    functionCount: v.number(),
    enumCount: v.number(),
    lastCompiled: v.optional(v.number()),
    clientVersion: v.optional(v.string()),
  }).index("by_project", ["project"]),

  testRuns: defineTable({
    project: v.string(),
    suite: v.string(),
    branch: v.string(),
    commit: v.string(),
    passed: v.number(),
    failed: v.number(),
    skipped: v.number(),
    durationMs: v.number(),
    startedAt: v.number(),
    finishedAt: v.number(),
    failureDetails: v.optional(v.string()),
  })
    .index("by_project_started", ["project", "startedAt"])
    .index("by_project_branch", ["project", "branch"]),

  convexFunctionCalls: defineTable({
    function: v.string(),
    kind: v.union(v.literal("query"), v.literal("mutation"), v.literal("action")),
    project: v.string(),
    args: v.optional(v.string()),
    durationMs: v.number(),
    ok: v.boolean(),
    error: v.optional(v.string()),
    calledAt: v.number(),
  })
    .index("by_function_calledAt", ["function", "calledAt"])
    .index("by_calledAt", ["calledAt"]),

  convexMetrics: defineTable({
    scope: v.string(),
    metric: v.string(),
    value: v.number(),
    window: v.string(),
    sampledAt: v.number(),
  }).index("by_scope_metric", ["scope", "metric", "sampledAt"]),

  marimoNotebooks: defineTable({
    project: v.string(),
    slug: v.string(),
    file: v.string(),
    title: v.string(),
    description: v.optional(v.string()),
    cellCount: v.number(),
    lastExported: v.optional(v.number()),
    wasmPath: v.optional(v.string()),
  })
    .index("by_project", ["project"])
    .index("by_slug", ["slug"]),

  glanceConfig: defineTable({
    version: v.number(),
    yaml: v.string(),
    pageCount: v.number(),
    widgetCount: v.number(),
    generatedAt: v.number(),
    generatedBy: v.string(),
  }).index("by_version", ["version"]),
});
