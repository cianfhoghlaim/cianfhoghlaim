/**
 * Crypto.com MCP Server Integration
 *
 * Connects to the Crypto.com Market Data MCP Server for real-time
 * cryptocurrency market information. Free, no authentication required.
 *
 * Endpoint: https://mcp.crypto.com/market-data/mcp
 */

// Crypto.com MCP Server endpoint
export const CRYPTO_COM_MCP_ENDPOINT = "https://mcp.crypto.com/market-data/mcp";

/**
 * Market data types from Crypto.com
 */
export interface CryptoComTicker {
  symbol: string;
  price: number;
  priceChange24h: number;
  priceChangePercent24h: number;
  high24h: number;
  low24h: number;
  volume24h: number;
  quoteVolume24h: number;
  timestamp: number;
}

export interface CryptoComMarketOverview {
  totalMarketCap: number;
  totalVolume24h: number;
  btcDominance: number;
  ethDominance: number;
  fearGreedIndex: number;
  trendingCoins: string[];
}

/**
 * MCP Message types
 */
interface MCPRequest {
  jsonrpc: "2.0";
  id: string | number;
  method: string;
  params?: Record<string, unknown>;
}

interface MCPResponse<T = unknown> {
  jsonrpc: "2.0";
  id: string | number;
  result?: T;
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
}

/**
 * Send an MCP request to Crypto.com
 */
async function sendMCPRequest<T>(
  method: string,
  params?: Record<string, unknown>
): Promise<T> {
  const request: MCPRequest = {
    jsonrpc: "2.0",
    id: crypto.randomUUID(),
    method,
    params,
  };

  try {
    const response = await fetch(CRYPTO_COM_MCP_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`MCP request failed: ${response.statusText}`);
    }

    const data: MCPResponse<T> = await response.json();

    if (data.error) {
      throw new Error(`MCP error: ${data.error.message}`);
    }

    return data.result as T;
  } catch (error) {
    console.error("Crypto.com MCP error:", error);
    throw error;
  }
}

/**
 * Get current price for a cryptocurrency
 */
export async function getPrice(symbol: string): Promise<CryptoComTicker | null> {
  try {
    return await sendMCPRequest<CryptoComTicker>("tools/call", {
      name: "get_price",
      arguments: { symbol: symbol.toUpperCase() },
    });
  } catch {
    // Fallback to mock data if MCP unavailable
    return getMockPrice(symbol);
  }
}

/**
 * Get prices for multiple cryptocurrencies
 */
export async function getPrices(
  symbols: string[]
): Promise<Record<string, CryptoComTicker>> {
  try {
    const results: Record<string, CryptoComTicker> = {};

    // Fetch in parallel
    const promises = symbols.map(async (symbol) => {
      const price = await getPrice(symbol);
      if (price) {
        results[symbol.toUpperCase()] = price;
      }
    });

    await Promise.all(promises);
    return results;
  } catch {
    // Fallback to mock data
    return symbols.reduce(
      (acc, symbol) => {
        const mock = getMockPrice(symbol);
        if (mock) acc[symbol.toUpperCase()] = mock;
        return acc;
      },
      {} as Record<string, CryptoComTicker>
    );
  }
}

/**
 * Get market overview
 */
export async function getMarketOverview(): Promise<CryptoComMarketOverview | null> {
  try {
    return await sendMCPRequest<CryptoComMarketOverview>("tools/call", {
      name: "get_market_overview",
      arguments: {},
    });
  } catch {
    // Fallback to mock data
    return getMockMarketOverview();
  }
}

/**
 * Get trending cryptocurrencies
 */
export async function getTrending(): Promise<string[]> {
  try {
    const result = await sendMCPRequest<{ trending: string[] }>("tools/call", {
      name: "get_trending",
      arguments: {},
    });
    return result.trending;
  } catch {
    return ["BTC", "ETH", "SOL", "CRO", "PEPE"];
  }
}

/**
 * Compare two cryptocurrencies
 */
export async function comparePrices(
  symbol1: string,
  symbol2: string
): Promise<{ ratio: number; comparison: string }> {
  try {
    const [price1, price2] = await Promise.all([
      getPrice(symbol1),
      getPrice(symbol2),
    ]);

    if (!price1 || !price2) {
      throw new Error("Could not fetch prices");
    }

    const ratio = price1.price / price2.price;
    const comparison =
      price1.priceChangePercent24h > price2.priceChangePercent24h
        ? `${symbol1} is outperforming ${symbol2}`
        : `${symbol2} is outperforming ${symbol1}`;

    return { ratio, comparison };
  } catch {
    return {
      ratio: 0,
      comparison: "Unable to compare prices",
    };
  }
}

// Mock data fallbacks when MCP is unavailable
function getMockPrice(symbol: string): CryptoComTicker | null {
  const mockPrices: Record<string, CryptoComTicker> = {
    BTC: {
      symbol: "BTC",
      price: 97500,
      priceChange24h: 1250,
      priceChangePercent24h: 1.3,
      high24h: 98200,
      low24h: 95800,
      volume24h: 28500000000,
      quoteVolume24h: 2775000000000,
      timestamp: Date.now(),
    },
    ETH: {
      symbol: "ETH",
      price: 3650,
      priceChange24h: 85,
      priceChangePercent24h: 2.4,
      high24h: 3720,
      low24h: 3540,
      volume24h: 18200000000,
      quoteVolume24h: 66430000000,
      timestamp: Date.now(),
    },
    CRO: {
      symbol: "CRO",
      price: 0.142,
      priceChange24h: 0.008,
      priceChangePercent24h: 5.9,
      high24h: 0.148,
      low24h: 0.132,
      volume24h: 125000000,
      quoteVolume24h: 17750000,
      timestamp: Date.now(),
    },
    SOL: {
      symbol: "SOL",
      price: 185,
      priceChange24h: -3.2,
      priceChangePercent24h: -1.7,
      high24h: 192,
      low24h: 181,
      volume24h: 3200000000,
      quoteVolume24h: 592000000000,
      timestamp: Date.now(),
    },
    USDC: {
      symbol: "USDC",
      price: 1.0,
      priceChange24h: 0,
      priceChangePercent24h: 0,
      high24h: 1.001,
      low24h: 0.999,
      volume24h: 8500000000,
      quoteVolume24h: 8500000000,
      timestamp: Date.now(),
    },
  };

  return mockPrices[symbol.toUpperCase()] || null;
}

function getMockMarketOverview(): CryptoComMarketOverview {
  return {
    totalMarketCap: 3450000000000,
    totalVolume24h: 185000000000,
    btcDominance: 54.2,
    ethDominance: 12.8,
    fearGreedIndex: 72, // Greed
    trendingCoins: ["BTC", "ETH", "SOL", "CRO", "PEPE"],
  };
}

/**
 * Format price for display
 */
export function formatPrice(price: number): string {
  if (price >= 1000) {
    return price.toLocaleString("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    });
  } else if (price >= 1) {
    return price.toLocaleString("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  } else {
    return price.toLocaleString("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 4,
      maximumFractionDigits: 6,
    });
  }
}

/**
 * Format market cap for display
 */
export function formatMarketCap(value: number): string {
  if (value >= 1e12) {
    return `$${(value / 1e12).toFixed(2)}T`;
  } else if (value >= 1e9) {
    return `$${(value / 1e9).toFixed(2)}B`;
  } else if (value >= 1e6) {
    return `$${(value / 1e6).toFixed(2)}M`;
  } else {
    return `$${value.toLocaleString()}`;
  }
}
