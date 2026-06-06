/**
 * x402 Payment Middleware
 *
 * Server-side middleware for verifying and settling x402 payments.
 * Handles the 402 Payment Required flow for protected API routes.
 * Includes database tracking for payments and usage.
 */

import type { Address } from "viem";
import { DEFAULT_NETWORK, getNetworkByChainId, type NetworkConfig } from "./networks";
import { getFeaturePricing, type FeaturePricing } from "./pricing";
import {
  recordPayment,
  updatePaymentVerified,
  updatePaymentSettled,
  updatePaymentFailed,
  recordUsage,
  hasFreeTierRemaining,
  getDailyUsage,
} from "./payment-service";
import { getSession, getWalletAddress } from "../auth/server";

// Environment configuration
const PAYMENT_RECIPIENT = (process.env.PAYMENT_RECIPIENT ||
  "0x0000000000000000000000000000000000000000") as Address;
const FACILITATOR_URL =
  process.env.FACILITATOR_URL || "https://x402.org/facilitator";

/**
 * x402 Payment Required Response (v2 format)
 */
export interface PaymentRequiredResponse {
  x402Version: 2;
  error: string;
  resource: {
    url: string;
    description: string;
    mimeType: string;
  };
  accepts: PaymentRequirement[];
}

export interface PaymentRequirement {
  scheme: "exact";
  network: string; // CAIP-2 format
  amount: string; // atomic units
  asset: Address;
  payTo: Address;
  maxTimeoutSeconds: number;
  extra?: {
    name: string;
    version?: string;
  };
}

/**
 * x402 Payment Payload (from client)
 */
export interface PaymentPayload {
  x402Version: 2;
  resource: {
    url: string;
    description: string;
    mimeType: string;
  };
  accepted: PaymentRequirement;
  payload: {
    signature: string;
    authorization: {
      from: Address;
      to: Address;
      value: string;
      validAfter: string;
      validBefore: string;
      nonce: string;
    };
  };
}

/**
 * Facilitator verify response
 */
export interface VerifyResponse {
  isValid: boolean;
  invalidReason?: string;
  payer?: Address;
}

/**
 * Facilitator settle response
 */
export interface SettleResponse {
  success: boolean;
  transaction?: string;
  network?: string;
  payer?: Address;
  error?: string;
}

/**
 * Payment info passed to handlers
 */
export interface PaymentInfo {
  payer: Address | null;
  txHash: string | null;
  paid: boolean;
  paymentId?: string;
  userId?: string;
  walletAddress?: string;
}

/**
 * Build payment requirements for a feature
 */
export function buildPaymentRequirements(
  featureId: string,
  resourceUrl: string,
  network: NetworkConfig = DEFAULT_NETWORK
): PaymentRequirement[] {
  const pricing = getFeaturePricing(featureId);
  if (!pricing) {
    throw new Error(`Unknown feature: ${featureId}`);
  }

  return [
    {
      scheme: "exact",
      network: network.x402Network,
      amount: pricing.priceAtomic.toString(),
      asset: network.usdc,
      payTo: PAYMENT_RECIPIENT,
      maxTimeoutSeconds: 300,
      extra: {
        name: "USDC",
        version: "2",
      },
    },
  ];
}

/**
 * Create a 402 Payment Required response
 */
export function createPaymentRequiredResponse(
  featureId: string,
  resourceUrl: string,
  description: string,
  network: NetworkConfig = DEFAULT_NETWORK
): PaymentRequiredResponse {
  const requirements = buildPaymentRequirements(featureId, resourceUrl, network);

  return {
    x402Version: 2,
    error: "Payment required. Include PAYMENT-SIGNATURE header with signed payment.",
    resource: {
      url: resourceUrl,
      description,
      mimeType: "application/json",
    },
    accepts: requirements,
  };
}

/**
 * Verify a payment with the facilitator
 */
export async function verifyPayment(
  paymentPayload: PaymentPayload,
  requirements: PaymentRequirement[]
): Promise<VerifyResponse> {
  try {
    const response = await fetch(`${FACILITATOR_URL}/verify`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        paymentPayload,
        paymentRequirements: requirements[0],
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      return {
        isValid: false,
        invalidReason: `Facilitator error: ${error}`,
      };
    }

    return await response.json();
  } catch (error) {
    return {
      isValid: false,
      invalidReason: `Verification failed: ${error}`,
    };
  }
}

/**
 * Settle a payment with the facilitator
 */
export async function settlePayment(
  paymentPayload: PaymentPayload,
  requirements: PaymentRequirement[]
): Promise<SettleResponse> {
  try {
    const response = await fetch(`${FACILITATOR_URL}/settle`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        paymentPayload,
        paymentRequirements: requirements[0],
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      return {
        success: false,
        error: `Settlement failed: ${error}`,
      };
    }

    return await response.json();
  } catch (error) {
    return {
      success: false,
      error: `Settlement error: ${error}`,
    };
  }
}

/**
 * Decode payment header from request
 */
export function decodePaymentHeader(
  headerValue: string | null
): PaymentPayload | null {
  if (!headerValue) return null;

  try {
    const decoded = atob(headerValue);
    return JSON.parse(decoded) as PaymentPayload;
  } catch {
    return null;
  }
}

/**
 * Encode settlement response for header
 */
export function encodeSettlementHeader(settlement: SettleResponse): string {
  return btoa(JSON.stringify(settlement));
}

/**
 * Middleware options
 */
export interface PaymentMiddlewareOptions {
  featureId: string;
  description: string;
  network?: NetworkConfig;
  // Enable database tracking (default: true)
  trackPayments?: boolean;
  // Enable usage tracking (default: true)
  trackUsage?: boolean;
  // Custom free tier check (overrides default DB check)
  checkUsage?: (walletAddress: string | null, userId: string | null) => Promise<boolean>;
}

/**
 * Create a payment-protected API handler wrapper with database tracking
 *
 * Usage:
 * ```ts
 * const handler = withPayment({
 *   featureId: "analytics_yield",
 *   description: "Yield strategy analysis",
 * }, async (request, paymentInfo) => {
 *   // Your handler logic
 *   return Response.json({ data: "..." });
 * });
 * ```
 */
export function withPayment<T>(
  options: PaymentMiddlewareOptions,
  handler: (request: Request, paymentInfo: PaymentInfo) => Promise<Response>
): (request: Request) => Promise<Response> {
  const trackPayments = options.trackPayments !== false;
  const trackUsage = options.trackUsage !== false;

  return async (request: Request): Promise<Response> => {
    const network = options.network || DEFAULT_NETWORK;
    const resourceUrl = request.url;

    // Try to get session info
    let userId: string | undefined;
    let walletAddress: string | undefined;

    try {
      const sessionData = await getSession(request);
      userId = sessionData?.user?.id;
      walletAddress = sessionData?.user?.walletAddress || undefined;
    } catch {
      // No session, continue with wallet from header
    }

    // Fallback to header wallet
    if (!walletAddress) {
      walletAddress = request.headers.get("X-Wallet-Address") || undefined;
    }

    // Check for payment header (v2: PAYMENT-SIGNATURE, v1: X-PAYMENT)
    const paymentHeader =
      request.headers.get("PAYMENT-SIGNATURE") ||
      request.headers.get("X-PAYMENT");

    // If no payment, check if free tier allows access
    if (!paymentHeader) {
      let hasFreeAccess = false;

      if (options.checkUsage) {
        // Custom usage check
        hasFreeAccess = await options.checkUsage(walletAddress || null, userId || null);
      } else if (trackUsage && (walletAddress || userId)) {
        // Default database check
        const freeTierStatus = await hasFreeTierRemaining({
          userId,
          walletAddress,
          featureId: options.featureId,
        });
        hasFreeAccess = freeTierStatus.hasRemaining;
      }

      if (hasFreeAccess) {
        // Record free usage
        if (trackUsage && (walletAddress || userId)) {
          await recordUsage({
            userId,
            walletAddress,
            featureId: options.featureId,
          });
        }

        // Allow free access
        return handler(request, {
          payer: null,
          txHash: null,
          paid: false,
          userId,
          walletAddress,
        });
      }

      // Return 402 Payment Required
      const paymentRequired = createPaymentRequiredResponse(
        options.featureId,
        resourceUrl,
        options.description,
        network
      );

      return new Response(JSON.stringify(paymentRequired), {
        status: 402,
        headers: {
          "Content-Type": "application/json",
          "PAYMENT-REQUIRED": btoa(JSON.stringify(paymentRequired)),
        },
      });
    }

    // Decode payment payload
    const paymentPayload = decodePaymentHeader(paymentHeader);
    if (!paymentPayload) {
      return new Response(
        JSON.stringify({ error: "Invalid payment header" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const requirements = buildPaymentRequirements(
      options.featureId,
      resourceUrl,
      network
    );

    // Record pending payment
    let paymentRecord: { id: string } | undefined;
    if (trackPayments) {
      const pricing = getFeaturePricing(options.featureId);
      paymentRecord = await recordPayment({
        userId,
        walletAddress: paymentPayload.payload.authorization.from,
        featureId: options.featureId,
        resourceUrl,
        amount: pricing?.priceUsd?.toString() || "0",
        asset: requirements[0].asset,
        network: requirements[0].network,
        payerAddress: paymentPayload.payload.authorization.from,
        recipientAddress: requirements[0].payTo,
        status: "pending",
      });
    }

    // Verify payment
    const verification = await verifyPayment(paymentPayload, requirements);
    if (!verification.isValid) {
      // Update payment status
      if (trackPayments && paymentRecord) {
        await updatePaymentFailed(paymentRecord.id, verification.invalidReason || "Verification failed");
      }

      const paymentRequired = createPaymentRequiredResponse(
        options.featureId,
        resourceUrl,
        options.description,
        network
      );
      paymentRequired.error = verification.invalidReason || "Payment verification failed";

      return new Response(JSON.stringify(paymentRequired), {
        status: 402,
        headers: {
          "Content-Type": "application/json",
          "PAYMENT-REQUIRED": btoa(JSON.stringify(paymentRequired)),
        },
      });
    }

    // Update payment as verified
    if (trackPayments && paymentRecord) {
      await updatePaymentVerified(paymentRecord.id);
    }

    // Settle payment
    const settlement = await settlePayment(paymentPayload, requirements);
    if (!settlement.success) {
      if (trackPayments && paymentRecord) {
        await updatePaymentFailed(paymentRecord.id, settlement.error || "Settlement failed");
      }

      return new Response(
        JSON.stringify({ error: settlement.error || "Payment settlement failed" }),
        { status: 402, headers: { "Content-Type": "application/json" } }
      );
    }

    // Update payment as settled
    if (trackPayments && paymentRecord && settlement.transaction) {
      await updatePaymentSettled(paymentRecord.id, settlement.transaction);
    }

    // Record paid usage
    if (trackUsage) {
      await recordUsage({
        userId,
        walletAddress: verification.payer || walletAddress,
        featureId: options.featureId,
        paymentId: paymentRecord?.id,
      });
    }

    // Call the actual handler
    const response = await handler(request, {
      payer: verification.payer || null,
      txHash: settlement.transaction || null,
      paid: true,
      paymentId: paymentRecord?.id,
      userId,
      walletAddress: verification.payer || walletAddress,
    });

    // Add settlement info to response headers
    const headers = new Headers(response.headers);
    headers.set("PAYMENT-RESPONSE", encodeSettlementHeader(settlement));
    headers.set("X-PAYMENT-RESPONSE", encodeSettlementHeader(settlement));

    return new Response(response.body, {
      status: response.status,
      headers,
    });
  };
}

/**
 * Create a usage checker using database
 */
export function createDbUsageChecker(
  featureId: string
): (walletAddress: string | null, userId: string | null) => Promise<boolean> {
  return async (walletAddress, userId) => {
    if (!walletAddress && !userId) return false;

    const result = await hasFreeTierRemaining({
      userId: userId || undefined,
      walletAddress: walletAddress || undefined,
      featureId,
    });

    return result.hasRemaining;
  };
}

/**
 * Simple in-memory usage check (for backwards compatibility)
 */
export function createUsageChecker(
  featureId: string,
  getUsage: (wallet: string | null) => Promise<number>
): (wallet: string | null) => Promise<boolean> {
  const pricing = getFeaturePricing(featureId);
  const freeLimit = pricing?.freeLimit || 0;

  return async (wallet: string | null): Promise<boolean> => {
    if (freeLimit === 0) return false;
    const currentUsage = await getUsage(wallet);
    return currentUsage < freeLimit;
  };
}
