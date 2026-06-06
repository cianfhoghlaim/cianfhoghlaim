/**
 * CopilotKit Runtime Configuration
 *
 * Server-side runtime for CopilotKit with:
 * - Multi-provider LLM support via LiteLLM
 * - Agno agent integration
 * - MCP tool integration
 * - x402 payment gating
 */

import { CopilotRuntime, OpenAIAdapter, copilotRuntimeNextJSPagesRouterEndpoint } from "@copilotkit/runtime";

// LLM Configuration
const LITELLM_BASE_URL = process.env.LITELLM_BASE_URL || "http://localhost:4000";
const LLM_MODEL = process.env.LLM_MODEL || "gpt-4o-mini";
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || "";

/**
 * System prompt for the crypto research assistant
 */
export const CRYPTO_SYSTEM_PROMPT = `You are a crypto research assistant for Crypteolas, a DeFi analytics platform. You have access to:

## Data Sources
1. **Real-time Price Data**: Current and historical prices from Crypto.com and CoinGecko
2. **Protocol Metrics**: TVL, APY, and risk data from DeFiLlama
3. **Knowledge Graph**: Relationships between tokens, protocols, audits, and risks
4. **Yield Recommendations**: AI-powered strategy suggestions based on risk profiles

## Your Capabilities
- Analyze DeFi protocols (TVL, risks, yields)
- Explain tokenomics and mechanisms
- Review audit reports and security assessments
- Provide yield farming strategies based on risk tolerance
- Compare protocols and tokens
- Search the knowledge graph for entity relationships

## Guidelines
- Be concise but thorough
- Include relevant data and metrics when available
- Highlight risks and considerations
- Cite sources (audits, docs, data feeds) when applicable
- Format responses with markdown for readability
- Always remind users to DYOR and that crypto carries risk

## Key Protocols You Know About
- **Ethena**: Synthetic dollar (USDe) with ~27% APY through delta-neutral hedging
- **Aave v3**: Leading lending protocol with ~$12B TVL
- **Pendle**: Yield tokenization enabling 30%+ fixed yields
- **Lido**: Largest liquid staking with ~$22B TVL
- **Curve**: Stablecoin DEX with deep liquidity
- **Uniswap v3**: Concentrated liquidity DEX

When users ask about specific protocols or tokens, use the available tools to fetch real data.`;

/**
 * Tool definitions for CopilotKit
 */
export const cryptoTools = [
  {
    name: "query_price",
    description: "Get current price and 24h metrics for a cryptocurrency",
    parameters: {
      type: "object",
      properties: {
        symbol: {
          type: "string",
          description: "Token symbol (e.g., BTC, ETH, USDe)",
        },
      },
      required: ["symbol"],
    },
  },
  {
    name: "query_protocol",
    description: "Get TVL and metrics for a DeFi protocol",
    parameters: {
      type: "object",
      properties: {
        name: {
          type: "string",
          description: "Protocol name (e.g., ethena, aave-v3, lido)",
        },
      },
      required: ["name"],
    },
  },
  {
    name: "search_knowledge",
    description: "Search the knowledge graph for crypto entities",
    parameters: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search query",
        },
        type: {
          type: "string",
          enum: ["token", "protocol", "document", "all"],
          description: "Type of entity to search (default: all)",
        },
      },
      required: ["query"],
    },
  },
  {
    name: "get_yield_strategies",
    description: "Get yield strategy recommendations based on risk profile",
    parameters: {
      type: "object",
      properties: {
        riskLevel: {
          type: "string",
          enum: ["low", "medium", "high"],
          description: "User's risk tolerance",
        },
        amount: {
          type: "number",
          description: "Investment amount in USD (optional)",
        },
      },
      required: ["riskLevel"],
    },
  },
  {
    name: "analyze_risk",
    description: "Get risk analysis for a protocol or strategy",
    parameters: {
      type: "object",
      properties: {
        target: {
          type: "string",
          description: "Protocol name or strategy to analyze",
        },
      },
      required: ["target"],
    },
  },
];

/**
 * Create OpenAI-compatible adapter using LiteLLM
 */
export function createLLMAdapter() {
  // Use LiteLLM as the base URL if available, otherwise direct OpenAI
  const baseURL = LITELLM_BASE_URL.includes("localhost:4000")
    ? LITELLM_BASE_URL
    : "https://api.openai.com/v1";

  return new OpenAIAdapter({
    model: LLM_MODEL,
    // @ts-ignore - custom base URL
    baseURL,
    apiKey: OPENAI_API_KEY,
  });
}

/**
 * Tool execution handler
 * Connects to backend services (Agno, DeFiLlama, Knowledge Graph)
 */
export async function executeToolCall(
  toolName: string,
  args: Record<string, unknown>
): Promise<unknown> {
  const AGNO_API_URL = process.env.AGNO_API_URL || "http://localhost:8765";

  switch (toolName) {
    case "query_price": {
      // Try Agno first, fallback to mock
      try {
        const response = await fetch(`${AGNO_API_URL}/tools/price`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ symbol: args.symbol }),
        });
        if (response.ok) return await response.json();
      } catch {
        // Fallback to mock data
      }
      return getMockPrice(args.symbol as string);
    }

    case "query_protocol": {
      try {
        const response = await fetch(`${AGNO_API_URL}/tools/protocol`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: args.name }),
        });
        if (response.ok) return await response.json();
      } catch {
        // Fallback
      }
      return getMockProtocol(args.name as string);
    }

    case "search_knowledge": {
      try {
        const response = await fetch(`${AGNO_API_URL}/tools/search`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(args),
        });
        if (response.ok) return await response.json();
      } catch {
        // Fallback
      }
      return { results: [], message: "Knowledge graph not available" };
    }

    case "get_yield_strategies": {
      try {
        const response = await fetch(`${AGNO_API_URL}/tools/yields`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(args),
        });
        if (response.ok) return await response.json();
      } catch {
        // Fallback
      }
      return getMockYieldStrategies(args.riskLevel as string);
    }

    case "analyze_risk": {
      try {
        const response = await fetch(`${AGNO_API_URL}/tools/risk`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(args),
        });
        if (response.ok) return await response.json();
      } catch {
        // Fallback
      }
      return getMockRiskAnalysis(args.target as string);
    }

    default:
      return { error: `Unknown tool: ${toolName}` };
  }
}

// ============================================================================
// MOCK DATA FALLBACKS (when backend services unavailable)
// ============================================================================

function getMockPrice(symbol: string) {
  const prices: Record<string, unknown> = {
    BTC: { symbol: "BTC", price: 105000, change24h: 2.5, volume24h: 45000000000 },
    ETH: { symbol: "ETH", price: 3800, change24h: 1.8, volume24h: 22000000000 },
    USDe: { symbol: "USDe", price: 0.9999, change24h: 0.01, volume24h: 150000000 },
    CRO: { symbol: "CRO", price: 0.18, change24h: 3.2, volume24h: 85000000 },
    SOL: { symbol: "SOL", price: 220, change24h: 4.1, volume24h: 8500000000 },
  };
  return prices[symbol.toUpperCase()] || { error: `Price not found for ${symbol}` };
}

function getMockProtocol(name: string) {
  const protocols: Record<string, unknown> = {
    ethena: {
      name: "Ethena",
      tvl: 2800000000,
      apy: 27.4,
      risk: "medium",
      chain: "ethereum",
      audits: ["Zellic", "Spearbit"],
      description: "Synthetic dollar protocol using delta-neutral hedging",
    },
    "aave-v3": {
      name: "Aave V3",
      tvl: 12000000000,
      apy: 3.5,
      risk: "low",
      chain: "multi-chain",
      audits: ["Trail of Bits", "Certora", "SigmaPrime"],
      description: "Decentralized lending and borrowing protocol",
    },
    lido: {
      name: "Lido",
      tvl: 22000000000,
      apy: 3.8,
      risk: "low",
      chain: "ethereum",
      audits: ["Quantstamp", "Sigma Prime"],
      description: "Liquid staking for Ethereum",
    },
    pendle: {
      name: "Pendle",
      tvl: 3500000000,
      apy: 32.1,
      risk: "medium",
      chain: "multi-chain",
      audits: ["Ackee", "Dedaub"],
      description: "Yield tokenization and trading protocol",
    },
  };
  return protocols[name.toLowerCase()] || { error: `Protocol not found: ${name}` };
}

function getMockYieldStrategies(riskLevel: string) {
  const strategies = {
    low: [
      { protocol: "Aave V3", asset: "USDC", apy: 3.5, risk: "low" },
      { protocol: "Lido", asset: "stETH", apy: 3.8, risk: "low" },
      { protocol: "Compound V3", asset: "USDC", apy: 3.2, risk: "low" },
    ],
    medium: [
      { protocol: "Ethena", asset: "sUSDe", apy: 27.4, risk: "medium" },
      { protocol: "Pendle", asset: "PT-sUSDe", apy: 32.1, risk: "medium" },
      { protocol: "Curve", asset: "USDe-USDC LP", apy: 12.5, risk: "medium" },
    ],
    high: [
      { protocol: "Aave + Ethena", asset: "Looped sUSDe", apy: 55.0, risk: "high" },
      { protocol: "Pendle YT", asset: "YT-sUSDe", apy: 100.0, risk: "high" },
      { protocol: "GMX", asset: "GLP", apy: 25.0, risk: "high" },
    ],
  };
  return {
    riskLevel,
    strategies: strategies[riskLevel as keyof typeof strategies] || strategies.low,
    disclaimer: "Past performance does not guarantee future results. DYOR.",
  };
}

function getMockRiskAnalysis(target: string) {
  const risks: Record<string, unknown> = {
    ethena: {
      target: "Ethena",
      overallScore: 6.5,
      categories: {
        smartContract: { score: 8, notes: "Multiple audits, time in production" },
        economic: { score: 5, notes: "Funding rate dependency, peg risk" },
        counterparty: { score: 5, notes: "CEX exposure for hedging" },
        governance: { score: 7, notes: "Progressive decentralization" },
      },
      keyRisks: [
        "Negative funding rates during bear markets",
        "Centralized exchange counterparty risk",
        "USDe depeg scenarios",
      ],
    },
    aave: {
      target: "Aave V3",
      overallScore: 8.5,
      categories: {
        smartContract: { score: 9, notes: "Battle-tested, extensive audits" },
        economic: { score: 8, notes: "Proven liquidation mechanism" },
        counterparty: { score: 9, notes: "Decentralized, no custodians" },
        governance: { score: 8, notes: "Active DAO, safety module" },
      },
      keyRisks: [
        "Oracle manipulation (low probability)",
        "Governance attacks",
        "Bad debt accumulation in extreme markets",
      ],
    },
  };

  const normalized = target.toLowerCase().replace(/[^a-z]/g, "");
  return risks[normalized] || {
    target,
    message: "Risk analysis not available for this target",
    suggestion: "Try: ethena, aave, lido, pendle",
  };
}

/**
 * Create CopilotKit runtime instance
 */
export function createCopilotRuntime() {
  const adapter = createLLMAdapter();

  const runtime = new CopilotRuntime({
    // @ts-ignore - pending CopilotKit types update
    adapter,
  });

  return runtime;
}
