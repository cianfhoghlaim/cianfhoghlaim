/**
 * useProtocols - Data hook for DeFi protocol information
 *
 * Fetches protocol data from the Crypteolas API
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export interface Protocol {
  id: string;
  name: string;
  chain: string;
  tvl: number;
  tvlChange24h: number;
  tvlChange7d: number;
  category: string;
  apy?: number;
  riskScore: 'low' | 'medium' | 'high';
  auditStatus: 'audited' | 'pending' | 'unaudited';
  auditors?: string[];
  contracts: string[];
  website?: string;
  github?: string;
  documentation?: string;
}

export interface ProtocolDetails extends Protocol {
  description: string;
  tvlHistory: { date: string; tvl: number }[];
  topPools: { name: string; tvl: number; apy: number }[];
  securityIssues: { severity: string; description: string; resolved: boolean }[];
  governanceToken?: string;
  totalUsers: number;
  dailyActiveUsers: number;
}

interface UseProtocolsOptions {
  chain?: string;
  category?: string;
  sortBy?: 'tvl' | 'apy' | 'change';
  limit?: number;
}

const API_BASE = '/api/protocols';

async function fetchProtocols(options: UseProtocolsOptions = {}): Promise<Protocol[]> {
  const params = new URLSearchParams();
  if (options.chain) params.set('chain', options.chain);
  if (options.category) params.set('category', options.category);
  if (options.sortBy) params.set('sort_by', options.sortBy);
  if (options.limit) params.set('limit', options.limit.toString());

  const response = await fetch(`${API_BASE}?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch protocols: ${response.status}`);
  }

  const data = await response.json();
  return data.protocols;
}

async function fetchProtocolDetails(protocolId: string): Promise<ProtocolDetails> {
  const response = await fetch(`${API_BASE}/${protocolId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch protocol details: ${response.status}`);
  }
  return response.json();
}

async function searchProtocols(query: string): Promise<Protocol[]> {
  const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
  if (!response.ok) {
    throw new Error(`Search failed: ${response.status}`);
  }

  const data = await response.json();
  return data.results;
}

/**
 * Hook for fetching list of protocols
 */
export function useProtocols(options: UseProtocolsOptions = {}) {
  return useQuery({
    queryKey: ['protocols', options],
    queryFn: () => fetchProtocols(options),
    staleTime: 60_000, // 1 minute
    refetchInterval: 300_000, // 5 minutes
  });
}

/**
 * Hook for fetching detailed protocol information
 */
export function useProtocolDetails(protocolId: string | undefined) {
  return useQuery({
    queryKey: ['protocol', protocolId],
    queryFn: () => fetchProtocolDetails(protocolId!),
    enabled: !!protocolId,
    staleTime: 60_000,
  });
}

/**
 * Hook for searching protocols
 */
export function useProtocolSearch(query: string) {
  return useQuery({
    queryKey: ['protocol-search', query],
    queryFn: () => searchProtocols(query),
    enabled: query.length >= 2,
    staleTime: 30_000,
  });
}

/**
 * Hook for TVL data across all protocols
 */
export function useTotalTVL() {
  return useQuery({
    queryKey: ['total-tvl'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/stats/tvl`);
      if (!response.ok) throw new Error('Failed to fetch TVL');
      return response.json();
    },
    staleTime: 30_000,
    refetchInterval: 60_000,
  });
}

/**
 * Hook for TVL history data
 */
export function useTVLHistory(options: { days?: number; chain?: string } = {}) {
  const { days = 30, chain } = options;

  return useQuery({
    queryKey: ['tvl-history', days, chain],
    queryFn: async () => {
      const params = new URLSearchParams();
      params.set('days', days.toString());
      if (chain) params.set('chain', chain);

      const response = await fetch(`${API_BASE}/stats/tvl-history?${params}`);
      if (!response.ok) throw new Error('Failed to fetch TVL history');
      return response.json();
    },
    staleTime: 300_000, // 5 minutes
  });
}

/**
 * Hook for protocol risk analysis
 */
export function useProtocolRiskAnalysis(protocolId: string | undefined) {
  return useQuery({
    queryKey: ['protocol-risk', protocolId],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/${protocolId}/risk`);
      if (!response.ok) throw new Error('Failed to fetch risk analysis');
      return response.json();
    },
    enabled: !!protocolId,
    staleTime: 600_000, // 10 minutes
  });
}

/**
 * Hook for triggering AI analysis of a protocol
 */
export function useAnalyzeProtocol() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (protocolId: string) => {
      const response = await fetch(`${API_BASE}/${protocolId}/analyze`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Analysis failed');
      return response.json();
    },
    onSuccess: (_, protocolId) => {
      // Invalidate relevant queries after analysis
      queryClient.invalidateQueries({ queryKey: ['protocol', protocolId] });
      queryClient.invalidateQueries({ queryKey: ['protocol-risk', protocolId] });
    },
  });
}

/**
 * Hook for comparing multiple protocols
 */
export function useProtocolComparison(protocolIds: string[]) {
  return useQuery({
    queryKey: ['protocol-comparison', protocolIds],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ protocol_ids: protocolIds }),
      });
      if (!response.ok) throw new Error('Comparison failed');
      return response.json();
    },
    enabled: protocolIds.length >= 2,
    staleTime: 120_000,
  });
}

// Utility functions for formatting
export function formatTVL(tvl: number): string {
  if (tvl >= 1_000_000_000) {
    return `$${(tvl / 1_000_000_000).toFixed(2)}B`;
  }
  if (tvl >= 1_000_000) {
    return `$${(tvl / 1_000_000).toFixed(2)}M`;
  }
  if (tvl >= 1_000) {
    return `$${(tvl / 1_000).toFixed(2)}K`;
  }
  return `$${tvl.toFixed(2)}`;
}

export function formatChange(change: number): string {
  const prefix = change >= 0 ? '+' : '';
  return `${prefix}${change.toFixed(2)}%`;
}

export function getRiskColor(risk: 'low' | 'medium' | 'high'): string {
  switch (risk) {
    case 'low':
      return 'text-emerald-400';
    case 'medium':
      return 'text-yellow-400';
    case 'high':
      return 'text-red-400';
  }
}
