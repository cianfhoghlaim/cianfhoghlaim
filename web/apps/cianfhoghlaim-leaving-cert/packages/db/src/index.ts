// @cianfhoghlaim/db — Drizzle ORM schema for the Cianfhoghlaim Leaving Cert
// (per the new app's D1 schema in the standalone deployment)
// Phase 1 T1.2 — packages/db scaffolding.

import { pgTable, serial, text, varchar, timestamp, integer } from "drizzle-orm/pg-core";

// The schema for the D1 / Postgres-backed metadata store
// (separate from the Convex `conic-leaving-cert` deployment).

export const userSessions = pgTable("user_sessions", {
  id: serial("id").primaryKey(),
  userId: varchar("user_id", { length: 64 }).notNull(),
  sessionToken: text("session_token").notNull().unique(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  expiresAt: timestamp("expires_at").notNull(),
});

export const oauthAccounts = pgTable("oauth_accounts", {
  id: serial("id").primaryKey(),
  userId: varchar("user_id", { length: 64 }).notNull(),
  provider: varchar("provider", { length: 32 }).notNull(), // github, google, pocket-id, siwe
  providerAccountId: text("provider_account_id").notNull(),
  accessToken: text("access_token"),
  refreshToken: text("refresh_token"),
  expiresAt: timestamp("expires_at"),
});

export const diagramCacheMetrics = pgTable("diagram_cache_metrics", {
  id: serial("id").primaryKey(),
  mode: varchar("mode", { length: 32 }).notNull(),
  subject: varchar("subject", { length: 32 }).notNull(),
  language: varchar("language", { length: 2 }).notNull(),
  renderMs: integer("render_ms").notNull(),
  cacheHit: integer("cache_hit").notNull(), // 0 = miss, 1 = hit
  renderedAt: timestamp("rendered_at").defaultNow().notNull(),
});