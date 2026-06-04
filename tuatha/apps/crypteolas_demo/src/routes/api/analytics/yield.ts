/**
 * Yield Analysis API Route (Paid)
 *
 * Provides detailed sUSDe/USDe yield strategy analysis.
 * Protected by x402 payment - $0.05 per call.
 */

import { createAPIFileRoute } from "@tanstack/start/api";
import {
  withPayment,
  createPaymentRequiredResponse,
  decodePaymentHeader,
  verifyPayment,
  settlePayment,
  buildPaymentRequirements,
  encodeSettlementHeader,
} from "../../../lib/x402/middleware";
import { DEFAULT_NETWORK } from "../../../lib/x402/networks";

// Mock yield data - would come from on-chain data + calculations
const YIELD_STRATEGIES = {
  sUSDe: {
    protocol: "Ethena",
    currentApy: 27.4,
    apyHistory: [
      { date: "2024-11-01", apy: 25.2 },
      { date: "2024-11-08", apy: 28.1 },
      { date: "2024-11-15", apy: 26.8 },
      { date: "2024-11-22", apy: 27.4 },
    ],
    riskFactors: {
      fundingRateRisk: "high",
      smartContractRisk: "medium",
      counterpartyRisk: "medium-high",
      liquidityRisk: "low",
    },
    yieldBreakdown: {
      stakingRewards: 4.2,
      fundingRate: 23.2,
      total: 27.4,
    },
    metrics: {
      tvl: 2800000000,
      utilizationRate: 0.89,
      avgHoldingPeriod: "14 days",
    },
  },
  "pendle-pt-sUSDe": {
    protocol: "Pendle",
    currentApy: 32.1,
    maturityDate: "2025-03-27",
    impliedApy: 32.1,
    riskFactors: {
      durationRisk: "medium",
      smartContractRisk: "medium",
      redemptionRisk: "low",
    },
    yieldBreakdown: {
      discount: 32.1,
      total: 32.1,
    },
    metrics: {
      tvl: 180000000,
      liquidity: 45000000,
      daysToMaturity: 135,
    },
  },
  "aave-sUSDe-loop": {
    protocol: "Aave v3",
    currentApy: 48.5,
    leverage: 3.2,
    liquidationThreshold: 0.825,
    healthFactor: 1.42,
    riskFactors: {
      liquidationRisk: "high",
      smartContractRisk: "low",
      oracleRisk: "medium",
      depegRisk: "medium",
    },
    yieldBreakdown: {
      baseYield: 27.4,
      leverageMultiplier: 1.77,
      borrowCost: -5.8,
      total: 48.5,
    },
    metrics: {
      maxLeverage: 5.0,
      optimalLeverage: 3.0,
      borrowRate: 5.9,
    },
  },
};

const FEATURE_ID = "analytics_yield";
const RESOURCE_DESCRIPTION = "sUSDe/USDe yield strategy analysis with risk metrics";

export const Route = createAPIFileRoute("/api/analytics/yield")({
  GET: async ({ request }) => {
    const url = new URL(request.url);
    const strategy = url.searchParams.get("strategy") || "all";

    // Check for payment header
    const paymentHeader =
      request.headers.get("PAYMENT-SIGNATURE") ||
      request.headers.get("X-PAYMENT");

    if (!paymentHeader) {
      // Return 402 Payment Required
      const paymentRequired = createPaymentRequiredResponse(
        FEATURE_ID,
        request.url,
        RESOURCE_DESCRIPTION,
        DEFAULT_NETWORK
      );

      return new Response(JSON.stringify(paymentRequired), {
        status: 402,
        headers: {
          "Content-Type": "application/json",
          "PAYMENT-REQUIRED": btoa(JSON.stringify(paymentRequired)),
        },
      });
    }

    // Decode and verify payment
    const paymentPayload = decodePaymentHeader(paymentHeader);
    if (!paymentPayload) {
      return new Response(
        JSON.stringify({ error: "Invalid payment header" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const requirements = buildPaymentRequirements(
      FEATURE_ID,
      request.url,
      DEFAULT_NETWORK
    );

    // Verify payment
    const verification = await verifyPayment(paymentPayload, requirements);
    if (!verification.isValid) {
      const paymentRequired = createPaymentRequiredResponse(
        FEATURE_ID,
        request.url,
        RESOURCE_DESCRIPTION,
        DEFAULT_NETWORK
      );
      paymentRequired.error = verification.invalidReason || "Payment verification failed";

      return new Response(JSON.stringify(paymentRequired), {
        status: 402,
        headers: {
          "Content-Type": "application/json",
        },
      });
    }

    // Settle payment
    const settlement = await settlePayment(paymentPayload, requirements);
    if (!settlement.success) {
      return new Response(
        JSON.stringify({ error: settlement.error || "Payment settlement failed" }),
        { status: 402, headers: { "Content-Type": "application/json" } }
      );
    }

    // Return yield analysis data
    let data;
    if (strategy === "all") {
      data = YIELD_STRATEGIES;
    } else {
      data = YIELD_STRATEGIES[strategy as keyof typeof YIELD_STRATEGIES];
      if (!data) {
        return new Response(
          JSON.stringify({ error: `Unknown strategy: ${strategy}` }),
          { status: 404, headers: { "Content-Type": "application/json" } }
        );
      }
    }

    return new Response(
      JSON.stringify({
        data,
        meta: {
          timestamp: new Date().toISOString(),
          source: "on-chain + defillama",
          paid: true,
          payer: verification.payer,
          txHash: settlement.transaction,
        },
      }),
      {
        headers: {
          "Content-Type": "application/json",
          "PAYMENT-RESPONSE": encodeSettlementHeader(settlement),
        },
      }
    );
  },
});
