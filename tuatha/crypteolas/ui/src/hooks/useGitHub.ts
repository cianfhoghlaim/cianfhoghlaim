/**
 * useGitHub - Data hook for GitHub intelligence
 *
 * Fetches GitHub repository analysis data from the Crypteolas API
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export interface Repository {
  id: string;
  name: string;
  fullName: string;
  description?: string;
  stars: number;
  forks: number;
  watchers: number;
  language: string;
  languages: { name: string; percentage: number }[];
  lastCommit: string;
  commits30d: number;
  contributors: number;
  securityScore: number;
  openIssues: number;
  license?: string;
  topics: string[];
  protocol?: string;
}

export interface RepositoryDetails extends Repository {
  readme?: string;
  securityAnalysis: SecurityAnalysis;
  codeMetrics: CodeMetrics;
  contributorActivity: ContributorActivity[];
  commitHistory: { date: string; commits: number }[];
  dependencyGraph: DependencyNode[];
}

export interface SecurityAnalysis {
  score: number;
  vulnerabilities: Vulnerability[];
  auditFindings: AuditFinding[];
  codeSmells: CodeSmell[];
  lastScan: string;
}

export interface Vulnerability {
  id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  description: string;
  location: string;
  recommendation: string;
  cwe?: string;
}

export interface AuditFinding {
  auditor: string;
  date: string;
  severity: string;
  finding: string;
  status: 'fixed' | 'acknowledged' | 'open';
}

export interface CodeSmell {
  type: string;
  location: string;
  description: string;
  impact: string;
}

export interface CodeMetrics {
  linesOfCode: number;
  complexity: number;
  testCoverage?: number;
  documentation: number;
  contractCount: number;
  functionCount: number;
}

export interface ContributorActivity {
  username: string;
  avatar?: string;
  commits: number;
  additions: number;
  deletions: number;
  lastActive: string;
}

export interface DependencyNode {
  name: string;
  version: string;
  type: 'npm' | 'cargo' | 'pip' | 'foundry';
  hasVulnerabilities: boolean;
  children?: DependencyNode[];
}

interface UseGitHubOptions {
  language?: string;
  sortBy?: 'stars' | 'activity' | 'security';
  limit?: number;
  protocol?: string;
}

const API_BASE = '/api/github';

async function fetchRepositories(options: UseGitHubOptions = {}): Promise<Repository[]> {
  const params = new URLSearchParams();
  if (options.language) params.set('language', options.language);
  if (options.sortBy) params.set('sort_by', options.sortBy);
  if (options.limit) params.set('limit', options.limit.toString());
  if (options.protocol) params.set('protocol', options.protocol);

  const response = await fetch(`${API_BASE}/repos?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch repositories: ${response.status}`);
  }

  const data = await response.json();
  return data.repositories;
}

async function fetchRepositoryDetails(repoId: string): Promise<RepositoryDetails> {
  const response = await fetch(`${API_BASE}/repos/${encodeURIComponent(repoId)}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch repository details: ${response.status}`);
  }
  return response.json();
}

async function searchRepositories(query: string): Promise<Repository[]> {
  const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
  if (!response.ok) {
    throw new Error(`Search failed: ${response.status}`);
  }

  const data = await response.json();
  return data.results;
}

/**
 * Hook for fetching list of repositories
 */
export function useRepositories(options: UseGitHubOptions = {}) {
  return useQuery({
    queryKey: ['repositories', options],
    queryFn: () => fetchRepositories(options),
    staleTime: 300_000, // 5 minutes
  });
}

/**
 * Hook for fetching detailed repository information
 */
export function useRepositoryDetails(repoId: string | undefined) {
  return useQuery({
    queryKey: ['repository', repoId],
    queryFn: () => fetchRepositoryDetails(repoId!),
    enabled: !!repoId,
    staleTime: 300_000,
  });
}

/**
 * Hook for searching repositories
 */
export function useRepositorySearch(query: string) {
  return useQuery({
    queryKey: ['repository-search', query],
    queryFn: () => searchRepositories(query),
    enabled: query.length >= 2,
    staleTime: 60_000,
  });
}

/**
 * Hook for security scan of a repository
 */
export function useSecurityScan(repoId: string | undefined) {
  return useQuery({
    queryKey: ['security-scan', repoId],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/repos/${encodeURIComponent(repoId!)}/security`);
      if (!response.ok) throw new Error('Failed to fetch security scan');
      return response.json() as Promise<SecurityAnalysis>;
    },
    enabled: !!repoId,
    staleTime: 600_000, // 10 minutes
  });
}

/**
 * Hook for triggering a new security scan
 */
export function useTriggerSecurityScan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (repoId: string) => {
      const response = await fetch(`${API_BASE}/repos/${encodeURIComponent(repoId)}/scan`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Scan failed');
      return response.json();
    },
    onSuccess: (_, repoId) => {
      queryClient.invalidateQueries({ queryKey: ['security-scan', repoId] });
      queryClient.invalidateQueries({ queryKey: ['repository', repoId] });
    },
  });
}

/**
 * Hook for comparing two repositories
 */
export function useRepositoryComparison(repoIds: [string, string] | undefined) {
  return useQuery({
    queryKey: ['repository-comparison', repoIds],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_ids: repoIds }),
      });
      if (!response.ok) throw new Error('Comparison failed');
      return response.json();
    },
    enabled: !!repoIds && repoIds.length === 2,
    staleTime: 300_000,
  });
}

/**
 * Hook for smart contract analysis
 */
export function useContractAnalysis(repoId: string | undefined, contractPath?: string) {
  return useQuery({
    queryKey: ['contract-analysis', repoId, contractPath],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (contractPath) params.set('path', contractPath);

      const response = await fetch(
        `${API_BASE}/repos/${encodeURIComponent(repoId!)}/contracts?${params}`
      );
      if (!response.ok) throw new Error('Contract analysis failed');
      return response.json();
    },
    enabled: !!repoId,
    staleTime: 600_000,
  });
}

/**
 * Hook for dependency analysis
 */
export function useDependencyAnalysis(repoId: string | undefined) {
  return useQuery({
    queryKey: ['dependencies', repoId],
    queryFn: async () => {
      const response = await fetch(
        `${API_BASE}/repos/${encodeURIComponent(repoId!)}/dependencies`
      );
      if (!response.ok) throw new Error('Dependency analysis failed');
      return response.json() as Promise<DependencyNode[]>;
    },
    enabled: !!repoId,
    staleTime: 600_000,
  });
}

/**
 * Hook for commit activity
 */
export function useCommitActivity(repoId: string | undefined, days: number = 30) {
  return useQuery({
    queryKey: ['commit-activity', repoId, days],
    queryFn: async () => {
      const response = await fetch(
        `${API_BASE}/repos/${encodeURIComponent(repoId!)}/commits?days=${days}`
      );
      if (!response.ok) throw new Error('Failed to fetch commit activity');
      return response.json();
    },
    enabled: !!repoId,
    staleTime: 300_000,
  });
}

/**
 * Hook for contributor analysis
 */
export function useContributors(repoId: string | undefined) {
  return useQuery({
    queryKey: ['contributors', repoId],
    queryFn: async () => {
      const response = await fetch(
        `${API_BASE}/repos/${encodeURIComponent(repoId!)}/contributors`
      );
      if (!response.ok) throw new Error('Failed to fetch contributors');
      return response.json() as Promise<ContributorActivity[]>;
    },
    enabled: !!repoId,
    staleTime: 600_000,
  });
}

// Utility functions
export function getSecurityScoreColor(score: number): string {
  if (score >= 90) return 'text-emerald-400';
  if (score >= 70) return 'text-yellow-400';
  if (score >= 50) return 'text-orange-400';
  return 'text-red-400';
}

export function getSeverityColor(severity: 'critical' | 'high' | 'medium' | 'low'): string {
  switch (severity) {
    case 'critical':
      return 'text-red-500 bg-red-500/20';
    case 'high':
      return 'text-orange-400 bg-orange-500/20';
    case 'medium':
      return 'text-yellow-400 bg-yellow-500/20';
    case 'low':
      return 'text-blue-400 bg-blue-500/20';
  }
}

export function formatNumber(num: number): string {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toString();
}

export function timeAgo(date: string): string {
  const now = new Date();
  const past = new Date(date);
  const diffMs = now.getTime() - past.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'today';
  if (diffDays === 1) return 'yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
  return `${Math.floor(diffDays / 365)} years ago`;
}
