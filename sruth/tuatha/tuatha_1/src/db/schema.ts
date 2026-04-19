/**
 * Drizzle ORM Database Schema for Crypteolas
 *
 * Includes:
 * - Better Auth tables (user, session, account, verification)
 * - SIWE/Web3 authentication extensions
 * - x402 payment tracking
 * - Usage metering
 * - Crypto analytics caching
 */

import {
  pgTable,
  text,
  timestamp,
  boolean,
  integer,
  decimal,
  jsonb,
  uuid,
  index,
  uniqueIndex,
} from "drizzle-orm/pg-core";
import { relations } from "drizzle-orm";

// ============================================================================
// BETTER AUTH CORE TABLES
// ============================================================================

export const user = pgTable("user", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  email: text("email").notNull().unique(),
  emailVerified: boolean("email_verified")
    .$defaultFn(() => false)
    .notNull(),
  image: text("image"),
  createdAt: timestamp("created_at")
    .$defaultFn(() => new Date())
    .notNull(),
  updatedAt: timestamp("updated_at")
    .$defaultFn(() => new Date())
    .notNull(),
  // Web3 extensions
  walletAddress: text("wallet_address").unique(),
  ensName: text("ens_name"),
  ensAvatar: text("ens_avatar"),
  chainId: integer("chain_id"),
});

export const session = pgTable("session", {
  id: text("id").primaryKey(),
  expiresAt: timestamp("expires_at").notNull(),
  token: text("token").notNull().unique(),
  createdAt: timestamp("created_at").notNull(),
  updatedAt: timestamp("updated_at").notNull(),
  ipAddress: text("ip_address"),
  userAgent: text("user_agent"),
  userId: text("user_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
}, (table) => ({
  userIdx: index("session_user_idx").on(table.userId),
  tokenIdx: uniqueIndex("session_token_idx").on(table.token),
}));

export const account = pgTable("account", {
  id: text("id").primaryKey(),
  accountId: text("account_id").notNull(),
  providerId: text("provider_id").notNull(),
  userId: text("user_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  accessToken: text("access_token"),
  refreshToken: text("refresh_token"),
  idToken: text("id_token"),
  accessTokenExpiresAt: timestamp("access_token_expires_at"),
  refreshTokenExpiresAt: timestamp("refresh_token_expires_at"),
  scope: text("scope"),
  password: text("password"),
  createdAt: timestamp("created_at").notNull(),
  updatedAt: timestamp("updated_at").notNull(),
}, (table) => ({
  userIdx: index("account_user_idx").on(table.userId),
  providerIdx: index("account_provider_idx").on(table.providerId, table.accountId),
}));

export const verification = pgTable("verification", {
  id: text("id").primaryKey(),
  identifier: text("identifier").notNull(),
  value: text("value").notNull(),
  expiresAt: timestamp("expires_at").notNull(),
  createdAt: timestamp("created_at").$defaultFn(() => new Date()),
  updatedAt: timestamp("updated_at").$defaultFn(() => new Date()),
}, (table) => ({
  identifierIdx: index("verification_identifier_idx").on(table.identifier),
}));

// ============================================================================
// X402 PAYMENT TABLES
// ============================================================================

export const payment = pgTable("payment", {
  id: uuid("id").defaultRandom().primaryKey(),
  userId: text("user_id").references(() => user.id, { onDelete: "set null" }),
  walletAddress: text("wallet_address").notNull(),

  // Payment details
  featureId: text("feature_id").notNull(),
  resourceUrl: text("resource_url").notNull(),
  amount: decimal("amount", { precision: 18, scale: 6 }).notNull(),
  asset: text("asset").notNull(), // USDC address
  network: text("network").notNull(), // CAIP-2 format (e.g., "eip155:25" for Cronos)

  // Transaction details
  txHash: text("tx_hash").unique(),
  payerAddress: text("payer_address").notNull(),
  recipientAddress: text("recipient_address").notNull(),

  // Status
  status: text("status").notNull().default("pending"), // pending, verified, settled, failed
  verifiedAt: timestamp("verified_at"),
  settledAt: timestamp("settled_at"),

  // Metadata
  metadata: jsonb("metadata").$type<Record<string, unknown>>(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
}, (table) => ({
  userIdx: index("payment_user_idx").on(table.userId),
  walletIdx: index("payment_wallet_idx").on(table.walletAddress),
  txHashIdx: uniqueIndex("payment_tx_hash_idx").on(table.txHash),
  featureIdx: index("payment_feature_idx").on(table.featureId),
  statusIdx: index("payment_status_idx").on(table.status),
}));

// ============================================================================
// USAGE TRACKING TABLES
// ============================================================================

export const usageRecord = pgTable("usage_record", {
  id: uuid("id").defaultRandom().primaryKey(),
  userId: text("user_id").references(() => user.id, { onDelete: "cascade" }),
  walletAddress: text("wallet_address"),

  featureId: text("feature_id").notNull(),
  count: integer("count").notNull().default(1),

  // Daily tracking
  date: text("date").notNull(), // YYYY-MM-DD format

  // Payment reference (if paid)
  paymentId: uuid("payment_id").references(() => payment.id),

  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
}, (table) => ({
  userDateIdx: index("usage_user_date_idx").on(table.userId, table.date),
  walletDateIdx: index("usage_wallet_date_idx").on(table.walletAddress, table.date),
  featureDateIdx: index("usage_feature_date_idx").on(table.featureId, table.date),
}));

export const usageQuota = pgTable("usage_quota", {
  id: uuid("id").defaultRandom().primaryKey(),
  userId: text("user_id").references(() => user.id, { onDelete: "cascade" }),
  walletAddress: text("wallet_address"),

  featureId: text("feature_id").notNull(),

  // Quota details
  dailyLimit: integer("daily_limit").notNull(),
  monthlyLimit: integer("monthly_limit"),

  // Current usage
  dailyUsed: integer("daily_used").notNull().default(0),
  monthlyUsed: integer("monthly_used").notNull().default(0),

  // Reset tracking
  lastDailyReset: timestamp("last_daily_reset").defaultNow().notNull(),
  lastMonthlyReset: timestamp("last_monthly_reset").defaultNow().notNull(),

  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
}, (table) => ({
  userFeatureIdx: uniqueIndex("quota_user_feature_idx").on(table.userId, table.featureId),
  walletFeatureIdx: index("quota_wallet_feature_idx").on(table.walletAddress, table.featureId),
}));

// ============================================================================
// CHAT / CONVERSATION TABLES
// ============================================================================

export const conversation = pgTable("conversation", {
  id: uuid("id").defaultRandom().primaryKey(),
  userId: text("user_id").references(() => user.id, { onDelete: "cascade" }),
  walletAddress: text("wallet_address"),

  title: text("title"),

  // Metadata
  metadata: jsonb("metadata").$type<{
    model?: string;
    totalTokens?: number;
    totalCost?: number;
  }>(),

  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
}, (table) => ({
  userIdx: index("conversation_user_idx").on(table.userId),
  walletIdx: index("conversation_wallet_idx").on(table.walletAddress),
}));

export const message = pgTable("message", {
  id: uuid("id").defaultRandom().primaryKey(),
  conversationId: uuid("conversation_id")
    .notNull()
    .references(() => conversation.id, { onDelete: "cascade" }),

  role: text("role").notNull(), // user, assistant, system, tool
  content: text("content").notNull(),

  // Tool calls
  toolCalls: jsonb("tool_calls").$type<Array<{
    id: string;
    name: string;
    arguments: Record<string, unknown>;
  }>>(),
  toolCallId: text("tool_call_id"), // For tool response messages

  // Sources and citations
  sources: jsonb("sources").$type<Array<{
    title: string;
    type: string;
    url?: string;
  }>>(),

  // Token usage
  inputTokens: integer("input_tokens"),
  outputTokens: integer("output_tokens"),

  // Payment reference
  paymentId: uuid("payment_id").references(() => payment.id),

  createdAt: timestamp("created_at").defaultNow().notNull(),
}, (table) => ({
  conversationIdx: index("message_conversation_idx").on(table.conversationId),
  roleIdx: index("message_role_idx").on(table.role),
}));

// ============================================================================
// CRYPTO DATA CACHE TABLES
// ============================================================================

export const priceCache = pgTable("price_cache", {
  id: uuid("id").defaultRandom().primaryKey(),
  symbol: text("symbol").notNull(),
  price: decimal("price", { precision: 24, scale: 12 }).notNull(),
  priceChange24h: decimal("price_change_24h", { precision: 10, scale: 4 }),
  volume24h: decimal("volume_24h", { precision: 24, scale: 2 }),
  marketCap: decimal("market_cap", { precision: 24, scale: 2 }),

  source: text("source").notNull(), // coingecko, crypto_com, binance

  fetchedAt: timestamp("fetched_at").defaultNow().notNull(),
  expiresAt: timestamp("expires_at").notNull(),
}, (table) => ({
  symbolIdx: index("price_symbol_idx").on(table.symbol),
  sourceSymbolIdx: uniqueIndex("price_source_symbol_idx").on(table.source, table.symbol),
}));

export const protocolCache = pgTable("protocol_cache", {
  id: uuid("id").defaultRandom().primaryKey(),
  slug: text("slug").notNull().unique(),
  name: text("name").notNull(),

  tvl: decimal("tvl", { precision: 24, scale: 2 }),
  tvlChange24h: decimal("tvl_change_24h", { precision: 10, scale: 4 }),
  apy: decimal("apy", { precision: 10, scale: 4 }),

  chains: jsonb("chains").$type<string[]>(),
  category: text("category"),

  riskScore: decimal("risk_score", { precision: 4, scale: 2 }),
  auditStatus: text("audit_status"), // audited, partial, none

  metadata: jsonb("metadata").$type<Record<string, unknown>>(),

  source: text("source").notNull(), // defillama, custom
  fetchedAt: timestamp("fetched_at").defaultNow().notNull(),
  expiresAt: timestamp("expires_at").notNull(),
}, (table) => ({
  slugIdx: uniqueIndex("protocol_slug_idx").on(table.slug),
  categoryIdx: index("protocol_category_idx").on(table.category),
}));

// ============================================================================
// RELATIONS
// ============================================================================

export const userRelations = relations(user, ({ many }) => ({
  sessions: many(session),
  accounts: many(account),
  payments: many(payment),
  usageRecords: many(usageRecord),
  usageQuotas: many(usageQuota),
  conversations: many(conversation),
}));

export const sessionRelations = relations(session, ({ one }) => ({
  user: one(user, {
    fields: [session.userId],
    references: [user.id],
  }),
}));

export const accountRelations = relations(account, ({ one }) => ({
  user: one(user, {
    fields: [account.userId],
    references: [user.id],
  }),
}));

export const paymentRelations = relations(payment, ({ one, many }) => ({
  user: one(user, {
    fields: [payment.userId],
    references: [user.id],
  }),
  usageRecords: many(usageRecord),
  messages: many(message),
}));

export const usageRecordRelations = relations(usageRecord, ({ one }) => ({
  user: one(user, {
    fields: [usageRecord.userId],
    references: [user.id],
  }),
  payment: one(payment, {
    fields: [usageRecord.paymentId],
    references: [payment.id],
  }),
}));

export const usageQuotaRelations = relations(usageQuota, ({ one }) => ({
  user: one(user, {
    fields: [usageQuota.userId],
    references: [user.id],
  }),
}));

export const conversationRelations = relations(conversation, ({ one, many }) => ({
  user: one(user, {
    fields: [conversation.userId],
    references: [user.id],
  }),
  messages: many(message),
}));

export const messageRelations = relations(message, ({ one }) => ({
  conversation: one(conversation, {
    fields: [message.conversationId],
    references: [conversation.id],
  }),
  payment: one(payment, {
    fields: [message.paymentId],
    references: [payment.id],
  }),
}));

// ============================================================================
// TYPE EXPORTS
// ============================================================================

export type User = typeof user.$inferSelect;
export type NewUser = typeof user.$inferInsert;

export type Session = typeof session.$inferSelect;
export type NewSession = typeof session.$inferInsert;

export type Account = typeof account.$inferSelect;
export type NewAccount = typeof account.$inferInsert;

export type Verification = typeof verification.$inferSelect;
export type NewVerification = typeof verification.$inferInsert;

export type Payment = typeof payment.$inferSelect;
export type NewPayment = typeof payment.$inferInsert;

export type UsageRecord = typeof usageRecord.$inferSelect;
export type NewUsageRecord = typeof usageRecord.$inferInsert;

export type UsageQuota = typeof usageQuota.$inferSelect;
export type NewUsageQuota = typeof usageQuota.$inferInsert;

export type Conversation = typeof conversation.$inferSelect;
export type NewConversation = typeof conversation.$inferInsert;

export type Message = typeof message.$inferSelect;
export type NewMessage = typeof message.$inferInsert;

export type PriceCache = typeof priceCache.$inferSelect;
export type NewPriceCache = typeof priceCache.$inferInsert;

export type ProtocolCache = typeof protocolCache.$inferSelect;
export type NewProtocolCache = typeof protocolCache.$inferInsert;
