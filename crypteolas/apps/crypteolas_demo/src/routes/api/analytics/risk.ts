/**
 * Risk Analysis API Route (Paid)
 *
 * Provides liquidation risk modeling and de-peg probability analysis.
 * Protected by x402 payment - $0.05 per call.
 */

import { createAPIFileRoute } from "@tanstack/start/api";
import {
  createPaymentRequiredResponse,
  decodePaymentHeader,
  verifyPayment,
  settlePayment,
  buildPaymentRequirements,
  encodeSettlementHeader,
} from "../../../lib/x402/middleware";
import { DEFAULT_NETWORK } from "../../../lib/x402/networks";

// Mock risk analysis data
const RISK_ANALYSIS = {
  usde: {
    pegStability: {
      current: 0.9998,
      historicalLow: 0.9891,
      historicalHigh: 1.0012,
      deviation1d: 0.0002,
      deviation7d: 0.0008,
      deviation30d: 0.0015,
      depegProbability: 0.023, // 2.3% chance of >1% depeg in next 30 days
    },
    backingAnalysis: {
      totalCollateral: 2850000000,
      hedgeRatio: 0.998,
      collateralTypes: [
        { type: "stETH", percentage: 62, value: 1767000000 },
        { type: "WETH", percentage: 28, value: 798000000 },
        { type: "USDC", percentage: 10, value: 285000000 },
      ],
      exchanges: [
        { name: "Binance", percentage: 35, exposure: 997500000 },
        { name: "OKX", percentage: 28, exposure: 798000000 },
        { name: "Bybit", percentage: 22, exposure: 627000000 },
        { name: "Deribit", percentage: 15, exposure: 427500000 },
      ],
    },
    fundingRateRisk: {
      currentRate: 0.0234, // 2.34% annualized
      historicalAvg: 0.0189,
      volatility: 0.0156,
      negativeFundingProbability: 0.12, // 12% chance of negative funding
      breakEvenDays: 45, // Days of negative funding before reserve depletes
    },
    smartContractRisk: {
      audits: [
        { auditor: "Zellic", date: "2024-06-15", criticalIssues: 0 },
        { auditor: "Spearbit", date: "2024-07-01", criticalIssues: 0 },
      ],
      codeMaturity: "medium", // < 1 year
      upgradeability: true,
      multisigThreshold: "3/5",
    },
  },
  aaveLoop: {
    liquidationScenarios: [
      {
        scenario: "10% ETH drop",
        newHealthFactor: 1.28,
        liquidationRisk: "low",
        estimatedLoss: 0,
      },
      {
        scenario: "20% ETH drop",
        newHealthFactor: 1.14,
        liquidationRisk: "medium",
        estimatedLoss: 0,
      },
      {
        scenario: "30% ETH drop",
        newHealthFactor: 0.99,
        liquidationRisk: "high",
        estimatedLoss: 0.15, // 15% of collateral
      },
      {
        scenario: "USDe 5% depeg",
        newHealthFactor: 0.89,
        liquidationRisk: "critical",
        estimatedLoss: 0.42, // 42% of collateral
      },
    ],
    currentPosition: {
      healthFactor: 1.42,
      liquidationPrice: 2180, // ETH price for liquidation
      collateralValue: 100000,
      debtValue: 68000,
      leverage: 3.2,
    },
    recommendations: [
      {
        action: "Reduce leverage to 2.5x",
        impact: "Health factor increases to 1.65",
        priority: "medium",
      },
      {
        action: "Set up health factor alerts at 1.3",
        impact: "Early warning for deleveraging",
        priority: "high",
      },
      {
        action: "Maintain USDC buffer for emergency repay",
        impact: "Avoid forced liquidation",
        priority: "medium",
      },
    ],
  },
  protocolComparison: {
    protocols: [
      {
        name: "Ethena (sUSDe)",
        riskScore: 6.5,
        apy: 27.4,
        riskAdjustedReturn: 4.2, // Sharpe-like ratio
      },
      {
        name: "Aave v3 USDC",
        riskScore: 2.5,
        apy: 4.2,
        riskAdjustedReturn: 1.7,
      },
      {
        name: "Pendle PT-sUSDe",
        riskScore: 5.5,
        apy: 32.1,
        riskAdjustedReturn: 5.8,
      },
      {
        name: "Curve USDe-USDC",
        riskScore: 4.0,
        apy: 8.5,
        riskAdjustedReturn: 2.1,
      },
    ],
  },
};

const FEATURE_ID = "analytics_risk";
const RESOURCE_DESCRIPTION = "Liquidation risk modeling and de-peg probability analysis";

export const Route = createAPIFileRoute("/api/analytics/risk")({
  GET: async ({ request }) => {
    const url = new URL(request.url);
    const analysisType = url.searchParams.get("type") || "all";

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

    // Return risk analysis data
    let data;
    switch (analysisType) {
      case "usde":
        data = { usde: RISK_ANALYSIS.usde };
        break;
      case "aave":
        data = { aaveLoop: RISK_ANALYSIS.aaveLoop };
        break;
      case "comparison":
        data = { protocolComparison: RISK_ANALYSIS.protocolComparison };
        break;
      case "all":
      default:
        data = RISK_ANALYSIS;
    }

    return new Response(
      JSON.stringify({
        data,
        meta: {
          timestamp: new Date().toISOString(),
          source: "on-chain analysis + risk models",
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
