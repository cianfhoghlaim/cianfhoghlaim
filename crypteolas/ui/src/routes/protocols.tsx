/**
 * Protocols page - DeFi protocol explorer with TVL, yields, and risk analysis
 */

import { createFileRoute, Link } from '@tanstack/react-router';
import { useState } from 'react';

export const Route = createFileRoute('/protocols')({
  component: ProtocolsPage,
});

interface Protocol {
  id: string;
  name: string;
  chain: string;
  tvl: number;
  tvlChange24h: number;
  category: string;
  apy?: number;
  riskScore: 'low' | 'medium' | 'high';
  auditStatus: 'audited' | 'pending' | 'unaudited';
}

// Sample protocol data (would come from API in production)
const SAMPLE_PROTOCOLS: Protocol[] = [
  {
    id: 'aave-v3',
    name: 'Aave V3',
    chain: 'Ethereum',
    tvl: 12_500_000_000,
    tvlChange24h: 2.5,
    category: 'Lending',
    apy: 4.2,
    riskScore: 'low',
    auditStatus: 'audited',
  },
  {
    id: 'uniswap-v3',
    name: 'Uniswap V3',
    chain: 'Ethereum',
    tvl: 8_200_000_000,
    tvlChange24h: -1.2,
    category: 'DEX',
    riskScore: 'low',
    auditStatus: 'audited',
  },
  {
    id: 'lido',
    name: 'Lido',
    chain: 'Ethereum',
    tvl: 22_000_000_000,
    tvlChange24h: 0.8,
    category: 'Liquid Staking',
    apy: 3.8,
    riskScore: 'low',
    auditStatus: 'audited',
  },
  {
    id: 'curve-finance',
    name: 'Curve Finance',
    chain: 'Ethereum',
    tvl: 4_500_000_000,
    tvlChange24h: -0.5,
    category: 'DEX',
    apy: 5.1,
    riskScore: 'medium',
    auditStatus: 'audited',
  },
  {
    id: 'gmx',
    name: 'GMX',
    chain: 'Arbitrum',
    tvl: 650_000_000,
    tvlChange24h: 3.2,
    category: 'Derivatives',
    apy: 12.5,
    riskScore: 'medium',
    auditStatus: 'audited',
  },
];

function ProtocolsPage() {
  const [filter, setFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'tvl' | 'apy' | 'change'>('tvl');

  const filteredProtocols = SAMPLE_PROTOCOLS
    .filter((p) => filter === 'all' || p.category.toLowerCase() === filter)
    .sort((a, b) => {
      if (sortBy === 'tvl') return b.tvl - a.tvl;
      if (sortBy === 'apy') return (b.apy || 0) - (a.apy || 0);
      return b.tvlChange24h - a.tvlChange24h;
    });

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
            <h1 className="text-lg font-semibold">Protocols</h1>
          </div>
          <nav className="flex gap-4">
            <Link to="/github" className="text-slate-400 hover:text-white">
              GitHub
            </Link>
            <Link to="/analytics" className="text-slate-400 hover:text-white">
              Analytics
            </Link>
          </nav>
        </div>
      </header>

      {/* Filters */}
      <section className="container mx-auto px-4 py-6">
        <div className="flex flex-wrap gap-4 items-center justify-between">
          <div className="flex gap-2">
            {['all', 'lending', 'dex', 'liquid staking', 'derivatives'].map((cat) => (
              <button
                key={cat}
                onClick={() => setFilter(cat)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filter === cat
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                }`}
              >
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </button>
            ))}
          </div>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'tvl' | 'apy' | 'change')}
            className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm"
          >
            <option value="tvl">Sort by TVL</option>
            <option value="apy">Sort by APY</option>
            <option value="change">Sort by 24h Change</option>
          </select>
        </div>
      </section>

      {/* Protocol List */}
      <section className="container mx-auto px-4 py-4">
        <div className="bg-slate-800/50 rounded-xl overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="text-left text-sm text-slate-400 border-b border-slate-700">
                <th className="px-6 py-4">Protocol</th>
                <th className="px-6 py-4">Chain</th>
                <th className="px-6 py-4">Category</th>
                <th className="px-6 py-4 text-right">TVL</th>
                <th className="px-6 py-4 text-right">24h Change</th>
                <th className="px-6 py-4 text-right">APY</th>
                <th className="px-6 py-4 text-center">Risk</th>
                <th className="px-6 py-4 text-center">Audit</th>
              </tr>
            </thead>
            <tbody>
              {filteredProtocols.map((protocol) => (
                <tr
                  key={protocol.id}
                  className="border-b border-slate-700/50 hover:bg-slate-700/30 cursor-pointer"
                >
                  <td className="px-6 py-4">
                    <div className="font-medium text-white">{protocol.name}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-slate-400">{protocol.chain}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 bg-slate-700 rounded text-sm">
                      {protocol.category}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right font-mono">
                    ${formatTVL(protocol.tvl)}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span
                      className={
                        protocol.tvlChange24h >= 0 ? 'text-emerald-400' : 'text-red-400'
                      }
                    >
                      {protocol.tvlChange24h >= 0 ? '+' : ''}
                      {protocol.tvlChange24h.toFixed(2)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right font-mono">
                    {protocol.apy ? `${protocol.apy.toFixed(1)}%` : '-'}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <RiskBadge risk={protocol.riskScore} />
                  </td>
                  <td className="px-6 py-4 text-center">
                    <AuditBadge status={protocol.auditStatus} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* AI Analysis Panel (placeholder) */}
      <section className="container mx-auto px-4 py-8">
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-indigo-300 mb-4">
            AI Protocol Analysis
          </h3>
          <p className="text-slate-400 mb-4">
            Ask questions about any protocol, compare yields, or analyze smart contract security.
          </p>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="e.g., Compare APY between Aave and Lido..."
              className="flex-1 bg-slate-900 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-500"
            />
            <button className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-lg font-medium transition-colors">
              Analyze
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}

function formatTVL(tvl: number): string {
  if (tvl >= 1_000_000_000) {
    return `${(tvl / 1_000_000_000).toFixed(2)}B`;
  }
  if (tvl >= 1_000_000) {
    return `${(tvl / 1_000_000).toFixed(2)}M`;
  }
  return tvl.toLocaleString();
}

function RiskBadge({ risk }: { risk: 'low' | 'medium' | 'high' }) {
  const colors = {
    low: 'bg-emerald-500/20 text-emerald-400',
    medium: 'bg-yellow-500/20 text-yellow-400',
    high: 'bg-red-500/20 text-red-400',
  };

  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${colors[risk]}`}>
      {risk.toUpperCase()}
    </span>
  );
}

function AuditBadge({ status }: { status: 'audited' | 'pending' | 'unaudited' }) {
  const colors = {
    audited: 'bg-emerald-500/20 text-emerald-400',
    pending: 'bg-yellow-500/20 text-yellow-400',
    unaudited: 'bg-red-500/20 text-red-400',
  };

  const icons = {
    audited: '✓',
    pending: '⋯',
    unaudited: '!',
  };

  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${colors[status]}`}>
      {icons[status]} {status}
    </span>
  );
}
