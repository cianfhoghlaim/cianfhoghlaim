// TODO: implement per-feature pricing config. For now, return a hard-coded
// placeholder so the pricing hook compiles.

export interface FeaturePrice {
  featureId: string;
  freePerDay: number;
  pricePerCall: string;
  asset: string;
}

export const PRICING_CONFIG: Record<string, FeaturePrice> = {
  copilot_chat: {
    featureId: "copilot_chat",
    freePerDay: 5,
    pricePerCall: "0.01",
    asset: "USDC",
  },
  yield_analytics: {
    featureId: "yield_analytics",
    freePerDay: 3,
    pricePerCall: "0.05",
    asset: "USDC",
  },
  risk_analysis: {
    featureId: "risk_analysis",
    freePerDay: 3,
    pricePerCall: "0.05",
    asset: "USDC",
  },
  knowledge_graph: {
    featureId: "knowledge_graph",
    freePerDay: 3,
    pricePerCall: "0.02",
    asset: "USDC",
  },
};
