/**
 * x402 Pricing Configuration
 *
 * Defines pricing tiers and per-feature costs for the hybrid
 * free tier + pay-per-call model.
 */

export interface FeaturePricing {
  id: string;
  name: string;
  description: string;
  // Free tier limits (per day, 0 = no free access)
  freeLimit: number;
  // Price per call in USD (as string for precision)
  priceUsd: string;
  // Price in atomic units (6 decimals for USDC)
  priceAtomic: bigint;
  // Category for grouping
  category: "chat" | "analytics" | "knowledge" | "models";
}

// Convert USD string to atomic USDC (6 decimals)
export function usdToAtomic(usd: string): bigint {
  const [whole, decimal = ""] = usd.replace("$", "").split(".");
  const paddedDecimal = decimal.padEnd(6, "0").slice(0, 6);
  return BigInt(whole + paddedDecimal);
}

// Convert atomic to display USD
export function atomicToUsd(atomic: bigint): string {
  const str = atomic.toString().padStart(7, "0");
  const whole = str.slice(0, -6) || "0";
  const decimal = str.slice(-6);
  return `$${whole}.${decimal}`;
}

// Feature pricing definitions
export const FEATURE_PRICING: Record<string, FeaturePricing> = {
  // Chat features
  chat_message: {
    id: "chat_message",
    name: "Chat Message",
    description: "Send a message to the AI assistant",
    freeLimit: 5, // 5 free messages per day
    priceUsd: "$0.01",
    priceAtomic: usdToAtomic("0.01"),
    category: "chat",
  },

  // Knowledge graph features
  knowledge_search: {
    id: "knowledge_search",
    name: "Knowledge Search",
    description: "Search the crypto protocol knowledge graph",
    freeLimit: 3, // 3 free searches per day
    priceUsd: "$0.02",
    priceAtomic: usdToAtomic("0.02"),
    category: "knowledge",
  },
  knowledge_entity: {
    id: "knowledge_entity",
    name: "Entity Details",
    description: "Get detailed entity relationships from knowledge graph",
    freeLimit: 2,
    priceUsd: "$0.03",
    priceAtomic: usdToAtomic("0.03"),
    category: "knowledge",
  },

  // Analytics features
  analytics_protocol: {
    id: "analytics_protocol",
    name: "Protocol Analytics",
    description: "Detailed protocol analysis (TVL, APY, risk)",
    freeLimit: 0, // No free access
    priceUsd: "$0.05",
    priceAtomic: usdToAtomic("0.05"),
    category: "analytics",
  },
  analytics_yield: {
    id: "analytics_yield",
    name: "Yield Analysis",
    description: "sUSDe/USDe yield strategy analysis",
    freeLimit: 0,
    priceUsd: "$0.05",
    priceAtomic: usdToAtomic("0.05"),
    category: "analytics",
  },
  analytics_risk: {
    id: "analytics_risk",
    name: "Risk Modeling",
    description: "Liquidation risk and de-peg probability analysis",
    freeLimit: 0,
    priceUsd: "$0.05",
    priceAtomic: usdToAtomic("0.05"),
    category: "analytics",
  },

  // Model inference features
  model_inference: {
    id: "model_inference",
    name: "Finetuned Model",
    description: "Query crypto-specialized finetuned model",
    freeLimit: 0,
    priceUsd: "$0.10",
    priceAtomic: usdToAtomic("0.10"),
    category: "models",
  },
};

// Get pricing by feature ID
export function getFeaturePricing(featureId: string): FeaturePricing | undefined {
  return FEATURE_PRICING[featureId];
}

// Get all features by category
export function getFeaturesByCategory(category: FeaturePricing["category"]): FeaturePricing[] {
  return Object.values(FEATURE_PRICING).filter((f) => f.category === category);
}

// Check if a feature has free tier access
export function hasFreeTier(featureId: string): boolean {
  const pricing = FEATURE_PRICING[featureId];
  return pricing ? pricing.freeLimit > 0 : false;
}

// Daily limits summary for display
export interface FreeTierSummary {
  chat: { used: number; limit: number };
  knowledge: { used: number; limit: number };
  analytics: { used: number; limit: number };
  models: { used: number; limit: number };
}

export function getFreeTierLimits(): Record<string, number> {
  return {
    chat_message: FEATURE_PRICING.chat_message.freeLimit,
    knowledge_search: FEATURE_PRICING.knowledge_search.freeLimit,
    knowledge_entity: FEATURE_PRICING.knowledge_entity.freeLimit,
    analytics_protocol: FEATURE_PRICING.analytics_protocol.freeLimit,
    analytics_yield: FEATURE_PRICING.analytics_yield.freeLimit,
    analytics_risk: FEATURE_PRICING.analytics_risk.freeLimit,
    model_inference: FEATURE_PRICING.model_inference.freeLimit,
  };
}

// Calculate total cost for multiple features
export function calculateTotalCost(features: { id: string; count: number }[]): bigint {
  return features.reduce((total, { id, count }) => {
    const pricing = FEATURE_PRICING[id];
    if (!pricing) return total;
    return total + pricing.priceAtomic * BigInt(count);
  }, BigInt(0));
}
