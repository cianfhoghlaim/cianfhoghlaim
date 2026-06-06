/**
 * CopilotKit Actions for Crypto.com MCP Integration
 *
 * These actions allow the AI assistant to fetch real-time market data
 * from Crypto.com's MCP server.
 */

import {
  getPrice,
  getPrices,
  getMarketOverview,
  getTrending,
  comparePrices,
  formatPrice,
  formatMarketCap,
  type CryptoComTicker,
} from "./crypto-com";

/**
 * Action definitions for CopilotKit
 * Use with useCopilotAction hook in React components
 */
export const cryptoComActions = {
  /**
   * Get current price for a cryptocurrency
   */
  getPrice: {
    name: "getCryptoPrice",
    description:
      "Get the current price, 24h change, and volume for a cryptocurrency symbol (e.g., BTC, ETH, CRO)",
    parameters: [
      {
        name: "symbol",
        type: "string" as const,
        description: "The cryptocurrency symbol (e.g., BTC, ETH, SOL, CRO)",
        required: true,
      },
    ],
    handler: async ({ symbol }: { symbol: string }) => {
      const price = await getPrice(symbol);
      if (!price) {
        return { error: `Could not find price for ${symbol}` };
      }

      return {
        symbol: price.symbol,
        price: formatPrice(price.price),
        priceRaw: price.price,
        change24h: `${price.priceChangePercent24h > 0 ? "+" : ""}${price.priceChangePercent24h.toFixed(2)}%`,
        high24h: formatPrice(price.high24h),
        low24h: formatPrice(price.low24h),
        volume24h: formatMarketCap(price.volume24h),
      };
    },
  },

  /**
   * Get prices for multiple cryptocurrencies
   */
  getMultiplePrices: {
    name: "getMultipleCryptoPrices",
    description:
      "Get current prices for multiple cryptocurrency symbols at once",
    parameters: [
      {
        name: "symbols",
        type: "string[]" as const,
        description:
          "Array of cryptocurrency symbols (e.g., ['BTC', 'ETH', 'CRO'])",
        required: true,
      },
    ],
    handler: async ({ symbols }: { symbols: string[] }) => {
      const prices = await getPrices(symbols);

      return Object.entries(prices).map(([symbol, data]) => ({
        symbol,
        price: formatPrice(data.price),
        change24h: `${data.priceChangePercent24h > 0 ? "+" : ""}${data.priceChangePercent24h.toFixed(2)}%`,
      }));
    },
  },

  /**
   * Get market overview
   */
  getMarketOverview: {
    name: "getMarketOverview",
    description:
      "Get overall crypto market statistics including total market cap, volume, BTC dominance, and fear/greed index",
    parameters: [],
    handler: async () => {
      const overview = await getMarketOverview();
      if (!overview) {
        return { error: "Could not fetch market overview" };
      }

      const fearGreedLabel =
        overview.fearGreedIndex >= 80
          ? "Extreme Greed"
          : overview.fearGreedIndex >= 60
            ? "Greed"
            : overview.fearGreedIndex >= 40
              ? "Neutral"
              : overview.fearGreedIndex >= 20
                ? "Fear"
                : "Extreme Fear";

      return {
        totalMarketCap: formatMarketCap(overview.totalMarketCap),
        totalVolume24h: formatMarketCap(overview.totalVolume24h),
        btcDominance: `${overview.btcDominance.toFixed(1)}%`,
        ethDominance: `${overview.ethDominance.toFixed(1)}%`,
        fearGreedIndex: overview.fearGreedIndex,
        fearGreedLabel,
        trendingCoins: overview.trendingCoins,
      };
    },
  },

  /**
   * Get trending cryptocurrencies
   */
  getTrending: {
    name: "getTrendingCryptos",
    description: "Get the list of currently trending cryptocurrencies",
    parameters: [],
    handler: async () => {
      const trending = await getTrending();
      return { trending };
    },
  },

  /**
   * Compare two cryptocurrencies
   */
  compareCryptos: {
    name: "compareCryptos",
    description:
      "Compare the price and performance of two cryptocurrencies",
    parameters: [
      {
        name: "symbol1",
        type: "string" as const,
        description: "First cryptocurrency symbol",
        required: true,
      },
      {
        name: "symbol2",
        type: "string" as const,
        description: "Second cryptocurrency symbol",
        required: true,
      },
    ],
    handler: async ({
      symbol1,
      symbol2,
    }: {
      symbol1: string;
      symbol2: string;
    }) => {
      const [price1, price2] = await Promise.all([
        getPrice(symbol1),
        getPrice(symbol2),
      ]);

      if (!price1 || !price2) {
        return { error: "Could not fetch prices for comparison" };
      }

      const comparison = await comparePrices(symbol1, symbol2);

      return {
        [symbol1]: {
          price: formatPrice(price1.price),
          change24h: `${price1.priceChangePercent24h > 0 ? "+" : ""}${price1.priceChangePercent24h.toFixed(2)}%`,
        },
        [symbol2]: {
          price: formatPrice(price2.price),
          change24h: `${price2.priceChangePercent24h > 0 ? "+" : ""}${price2.priceChangePercent24h.toFixed(2)}%`,
        },
        ratio: comparison.ratio.toFixed(4),
        analysis: comparison.comparison,
      };
    },
  },
};

/**
 * Get all action definitions for registering with CopilotKit
 */
export function getCryptoComActionDefinitions() {
  return Object.values(cryptoComActions);
}

/**
 * System prompt addition for Crypto.com market data capabilities
 */
export const CRYPTO_COM_SYSTEM_PROMPT = `
You have access to real-time cryptocurrency market data through Crypto.com's API.

Available capabilities:
- Get current price, 24h change, high/low, and volume for any cryptocurrency
- Get prices for multiple cryptocurrencies at once
- Get market overview (total market cap, volume, BTC/ETH dominance, fear/greed index)
- Get trending cryptocurrencies
- Compare two cryptocurrencies

When users ask about crypto prices or market conditions, use these tools to provide
accurate, real-time data. Always include the source as "Crypto.com Market Data".

The data is provided free of charge through Crypto.com's MCP server.
`;
