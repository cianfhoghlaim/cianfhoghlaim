/**
 * x402 Payment Service
 *
 * Database-backed payment tracking and usage management.
 * Integrates with Drizzle ORM for persistent storage.
 */

import { eq, and, sql } from "drizzle-orm";
import { db, payment, usageRecord, usageQuota, type NewPayment, type NewUsageRecord } from "../../db";
import type { Address } from "viem";
import { getFeaturePricing, type FeaturePricing } from "./pricing";

// ============================================================================
// PAYMENT RECORDING
// ============================================================================

export interface RecordPaymentParams {
  userId?: string;
  walletAddress: string;
  featureId: string;
  resourceUrl: string;
  amount: string;
  asset: string;
  network: string;
  txHash?: string;
  payerAddress: string;
  recipientAddress: string;
  status?: "pending" | "verified" | "settled" | "failed";
  metadata?: Record<string, unknown>;
}

/**
 * Record a new payment in the database
 */
export async function recordPayment(params: RecordPaymentParams) {
  const [newPayment] = await db
    .insert(payment)
    .values({
      userId: params.userId,
      walletAddress: params.walletAddress,
      featureId: params.featureId,
      resourceUrl: params.resourceUrl,
      amount: params.amount,
      asset: params.asset,
      network: params.network,
      txHash: params.txHash,
      payerAddress: params.payerAddress,
      recipientAddress: params.recipientAddress,
      status: params.status || "pending",
      metadata: params.metadata,
    })
    .returning();

  return newPayment;
}

/**
 * Update payment status after verification
 */
export async function updatePaymentVerified(paymentId: string) {
  const [updated] = await db
    .update(payment)
    .set({
      status: "verified",
      verifiedAt: new Date(),
      updatedAt: new Date(),
    })
    .where(eq(payment.id, paymentId))
    .returning();

  return updated;
}

/**
 * Update payment status after settlement
 */
export async function updatePaymentSettled(paymentId: string, txHash: string) {
  const [updated] = await db
    .update(payment)
    .set({
      status: "settled",
      txHash,
      settledAt: new Date(),
      updatedAt: new Date(),
    })
    .where(eq(payment.id, paymentId))
    .returning();

  return updated;
}

/**
 * Mark payment as failed
 */
export async function updatePaymentFailed(paymentId: string, reason: string) {
  const [updated] = await db
    .update(payment)
    .set({
      status: "failed",
      metadata: sql`jsonb_set(COALESCE(metadata, '{}'), '{failureReason}', ${JSON.stringify(reason)}::jsonb)`,
      updatedAt: new Date(),
    })
    .where(eq(payment.id, paymentId))
    .returning();

  return updated;
}

/**
 * Get payment by transaction hash
 */
export async function getPaymentByTxHash(txHash: string) {
  const [result] = await db
    .select()
    .from(payment)
    .where(eq(payment.txHash, txHash))
    .limit(1);

  return result;
}

/**
 * Get payments for a wallet address
 */
export async function getPaymentsByWallet(walletAddress: string, limit = 50) {
  return db
    .select()
    .from(payment)
    .where(eq(payment.walletAddress, walletAddress.toLowerCase()))
    .orderBy(sql`${payment.createdAt} DESC`)
    .limit(limit);
}

// ============================================================================
// USAGE TRACKING
// ============================================================================

/**
 * Get today's date string (YYYY-MM-DD)
 */
function getTodayString(): string {
  return new Date().toISOString().split("T")[0];
}

/**
 * Get current month string (YYYY-MM)
 */
function getCurrentMonthString(): string {
  const date = new Date();
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
}

/**
 * Record usage of a feature
 */
export async function recordUsage(params: {
  userId?: string;
  walletAddress?: string;
  featureId: string;
  paymentId?: string;
}) {
  const today = getTodayString();

  const [record] = await db
    .insert(usageRecord)
    .values({
      userId: params.userId,
      walletAddress: params.walletAddress?.toLowerCase(),
      featureId: params.featureId,
      date: today,
      paymentId: params.paymentId,
    })
    .returning();

  return record;
}

/**
 * Get daily usage count for a feature
 */
export async function getDailyUsage(params: {
  userId?: string;
  walletAddress?: string;
  featureId: string;
}): Promise<number> {
  const today = getTodayString();

  const conditions = [
    eq(usageRecord.featureId, params.featureId),
    eq(usageRecord.date, today),
  ];

  if (params.userId) {
    conditions.push(eq(usageRecord.userId, params.userId));
  } else if (params.walletAddress) {
    conditions.push(eq(usageRecord.walletAddress, params.walletAddress.toLowerCase()));
  }

  const result = await db
    .select({ count: sql<number>`count(*)::int` })
    .from(usageRecord)
    .where(and(...conditions));

  return result[0]?.count || 0;
}

/**
 * Check if user has remaining free usage
 */
export async function hasFreeTierRemaining(params: {
  userId?: string;
  walletAddress?: string;
  featureId: string;
}): Promise<{ hasRemaining: boolean; used: number; limit: number }> {
  const pricing = getFeaturePricing(params.featureId);
  const freeLimit = pricing?.freeLimit || 0;

  if (freeLimit === 0) {
    return { hasRemaining: false, used: 0, limit: 0 };
  }

  const used = await getDailyUsage(params);

  return {
    hasRemaining: used < freeLimit,
    used,
    limit: freeLimit,
  };
}

/**
 * Get usage summary for a user/wallet
 */
export async function getUsageSummary(params: {
  userId?: string;
  walletAddress?: string;
}) {
  const today = getTodayString();

  const conditions = [];
  if (params.userId) {
    conditions.push(eq(usageRecord.userId, params.userId));
  } else if (params.walletAddress) {
    conditions.push(eq(usageRecord.walletAddress, params.walletAddress.toLowerCase()));
  }

  conditions.push(eq(usageRecord.date, today));

  const result = await db
    .select({
      featureId: usageRecord.featureId,
      count: sql<number>`count(*)::int`,
    })
    .from(usageRecord)
    .where(and(...conditions))
    .groupBy(usageRecord.featureId);

  // Enrich with pricing info
  return result.map((r) => {
    const pricing = getFeaturePricing(r.featureId);
    return {
      featureId: r.featureId,
      used: r.count,
      freeLimit: pricing?.freeLimit || 0,
      remaining: Math.max(0, (pricing?.freeLimit || 0) - r.count),
      priceUsd: pricing?.priceUsd,
    };
  });
}

// ============================================================================
// QUOTA MANAGEMENT (Optional, for more complex limits)
// ============================================================================

/**
 * Initialize or get quota for a user/feature
 */
export async function getOrCreateQuota(params: {
  userId?: string;
  walletAddress?: string;
  featureId: string;
}) {
  const pricing = getFeaturePricing(params.featureId);

  // Try to find existing quota
  const conditions = [eq(usageQuota.featureId, params.featureId)];
  if (params.userId) {
    conditions.push(eq(usageQuota.userId, params.userId));
  }

  const [existing] = await db
    .select()
    .from(usageQuota)
    .where(and(...conditions))
    .limit(1);

  if (existing) {
    // Reset daily quota if needed
    const lastReset = existing.lastDailyReset;
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (lastReset < today) {
      const [updated] = await db
        .update(usageQuota)
        .set({
          dailyUsed: 0,
          lastDailyReset: today,
          updatedAt: new Date(),
        })
        .where(eq(usageQuota.id, existing.id))
        .returning();

      return updated;
    }

    return existing;
  }

  // Create new quota
  const [newQuota] = await db
    .insert(usageQuota)
    .values({
      userId: params.userId,
      walletAddress: params.walletAddress?.toLowerCase(),
      featureId: params.featureId,
      dailyLimit: pricing?.freeLimit || 0,
    })
    .returning();

  return newQuota;
}

// ============================================================================
// ANALYTICS HELPERS
// ============================================================================

/**
 * Get total revenue for a time period
 */
export async function getRevenueStats(startDate: Date, endDate: Date) {
  const result = await db
    .select({
      totalPayments: sql<number>`count(*)::int`,
      totalRevenue: sql<string>`sum(amount::numeric)`,
      uniquePayers: sql<number>`count(distinct payer_address)::int`,
    })
    .from(payment)
    .where(
      and(
        eq(payment.status, "settled"),
        sql`${payment.settledAt} >= ${startDate}`,
        sql`${payment.settledAt} <= ${endDate}`
      )
    );

  return result[0];
}

/**
 * Get feature usage breakdown
 */
export async function getFeatureUsageStats(startDate: Date, endDate: Date) {
  const startDateStr = startDate.toISOString().split("T")[0];
  const endDateStr = endDate.toISOString().split("T")[0];

  return db
    .select({
      featureId: usageRecord.featureId,
      totalUsage: sql<number>`count(*)::int`,
      paidUsage: sql<number>`count(payment_id)::int`,
      freeUsage: sql<number>`count(*) - count(payment_id)::int`,
    })
    .from(usageRecord)
    .where(
      and(
        sql`${usageRecord.date} >= ${startDateStr}`,
        sql`${usageRecord.date} <= ${endDateStr}`
      )
    )
    .groupBy(usageRecord.featureId);
}
