/**
 * GitHub Intelligence page - Analyze crypto protocol codebases
 */

import { createFileRoute, Link } from '@tanstack/react-router';
import { useState } from 'react';

export const Route = createFileRoute('/github')({
  component: GitHubPage,
});

interface Repository {
  id: string;
  name: string;
  fullName: string;
  stars: number;
  forks: number;
  language: string;
  lastCommit: string;
  commits30d: number;
  contributors: number;
  securityScore: number;
  openIssues: number;
}

// Sample repository data
const SAMPLE_REPOS: Repository[] = [
  {
    id: 'aave-v3-core',
    name: 'aave-v3-core',
    fullName: 'aave/aave-v3-core',
    stars: 845,
    forks: 523,
    language: 'Solidity',
    lastCommit: '2 days ago',
    commits30d: 45,
    contributors: 89,
    securityScore: 95,
    openIssues: 12,
  },
  {
    id: 'uniswap-v3-core',
    name: 'v3-core',
    fullName: 'Uniswap/v3-core',
    stars: 4200,
    forks: 2100,
    language: 'Solidity',
    lastCommit: '5 days ago',
    commits30d: 8,
    contributors: 45,
    securityScore: 98,
    openIssues: 34,
  },
  {
    id: 'lido-dao',
    name: 'lido-dao',
    fullName: 'lidofinance/lido-dao',
    stars: 320,
    forks: 180,
    language: 'Solidity',
    lastCommit: '1 day ago',
    commits30d: 62,
    contributors: 67,
    securityScore: 92,
    openIssues: 23,
  },
  {
    id: 'curve-contract',
    name: 'curve-contract',
    fullName: 'curvefi/curve-contract',
    stars: 1200,
    forks: 620,
    language: 'Vyper',
    lastCommit: '3 days ago',
    commits30d: 28,
    contributors: 34,
    securityScore: 88,
    openIssues: 8,
  },
];

function GitHubPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRepo, setSelectedRepo] = useState<Repository | null>(null);

  const filteredRepos = SAMPLE_REPOS.filter(
    (repo) =>
      repo.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      repo.fullName.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="bg-slate-800/50 border-b border-slate-700">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/" className="text-xl font-bold text-indigo-300">
              Crypteolas
            </Link>
            <span className="text-slate-500">/</span>
            <h1 className="text-lg font-semibold">GitHub Intelligence</h1>
          </div>
          <nav className="flex gap-4">
            <Link to="/protocols" className="text-slate-400 hover:text-white">
              Protocols
            </Link>
            <Link to="/analytics" className="text-slate-400 hover:text-white">
              Analytics
            </Link>
          </nav>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Repository List */}
          <div className="lg:col-span-2">
            {/* Search */}
            <div className="mb-6">
              <input
                type="text"
                placeholder="Search repositories..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500"
              />
            </div>

            {/* Repo Cards */}
            <div className="space-y-4">
              {filteredRepos.map((repo) => (
                <div
                  key={repo.id}
                  onClick={() => setSelectedRepo(repo)}
                  className={`bg-slate-800/50 border rounded-xl p-6 cursor-pointer transition-all ${
                    selectedRepo?.id === repo.id
                      ? 'border-indigo-500 bg-indigo-900/20'
                      : 'border-slate-700 hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="font-semibold text-white">{repo.fullName}</h3>
                      <span className="text-sm text-slate-400">{repo.language}</span>
                    </div>
                    <SecurityBadge score={repo.securityScore} />
                  </div>

                  <div className="grid grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-slate-400">Stars</div>
                      <div className="font-mono text-white">{repo.stars.toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-slate-400">Forks</div>
                      <div className="font-mono text-white">{repo.forks.toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-slate-400">Commits (30d)</div>
                      <div className="font-mono text-white">{repo.commits30d}</div>
                    </div>
                    <div>
                      <div className="text-slate-400">Contributors</div>
                      <div className="font-mono text-white">{repo.contributors}</div>
                    </div>
                  </div>

                  <div className="mt-4 flex items-center gap-4 text-xs text-slate-500">
                    <span>Last commit: {repo.lastCommit}</span>
                    <span>{repo.openIssues} open issues</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Analysis Panel */}
          <div className="lg:col-span-1">
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 sticky top-6">
              <h3 className="text-lg font-semibold text-violet-300 mb-4">
                Code Analysis
              </h3>

              {selectedRepo ? (
                <div className="space-y-6">
                  <div>
                    <h4 className="text-sm text-slate-400 mb-2">Selected Repository</h4>
                    <p className="font-medium">{selectedRepo.fullName}</p>
                  </div>

                  <div>
                    <h4 className="text-sm text-slate-400 mb-2">Security Score</h4>
                    <div className="flex items-center gap-3">
                      <div className="text-3xl font-bold text-emerald-400">
                        {selectedRepo.securityScore}
                      </div>
                      <div className="text-sm text-slate-400">/ 100</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm text-slate-400 mb-2">Quick Actions</h4>
                    <div className="space-y-2">
                      <button className="w-full px-4 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg text-sm transition-colors">
                        Run Security Audit
                      </button>
                      <button className="w-full px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm transition-colors">
                        Analyze Dependencies
                      </button>
                      <button className="w-full px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm transition-colors">
                        Compare with Fork
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <GitHubIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Select a repository to analyze</p>
                </div>
              )}
            </div>

            {/* AI Chat */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 mt-6">
              <h3 className="text-lg font-semibold text-violet-300 mb-4">
                AI Assistant
              </h3>
              <p className="text-sm text-slate-400 mb-4">
                Ask questions about code, security patterns, or developer activity.
              </p>
              <input
                type="text"
                placeholder="e.g., What vulnerabilities exist in this contract?"
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-4 py-3 text-sm text-white placeholder-slate-500"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function SecurityBadge({ score }: { score: number }) {
  const color =
    score >= 90
      ? 'bg-emerald-500/20 text-emerald-400'
      : score >= 70
      ? 'bg-yellow-500/20 text-yellow-400'
      : 'bg-red-500/20 text-red-400';

  return (
    <span className={`px-3 py-1 rounded-lg text-sm font-medium ${color}`}>
      {score}/100
    </span>
  );
}

function GitHubIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className={className}>
      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
    </svg>
  );
}
