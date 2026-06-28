// TODO: implement the typed data-fetching hooks used by the React
// dashboard. Each hook wraps a TanStack Query call to a backend endpoint.

import { useQuery } from "@tanstack/react-query";

export interface TokenPrice {
  id: string;
  symbol: string;
  usd: number;
  change24h: number;
}

export function useTokenPrices(tokenIds: string[]) {
  return useQuery<TokenPrice[]>({
    queryKey: ["tokenPrices", tokenIds],
    queryFn: async () => {
      throw new Error("useTokenPrices: not yet implemented");
    },
  });
}

export interface ProtocolTVL {
  id: string;
  name: string;
  tvlUsd: number;
  change24h: number;
}

export function useProtocols(protocolIds: string[]) {
  return useQuery<ProtocolTVL[]>({
    queryKey: ["protocols", protocolIds],
    queryFn: async () => {
      throw new Error("useProtocols: not yet implemented");
    },
  });
}
