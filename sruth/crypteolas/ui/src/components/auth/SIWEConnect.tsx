/**
 * SIWE (Sign-In With Ethereum) Connect Component for Crypteolas
 *
 * Enables wallet connection for DeFi analytics and premium features
 */

import { useState } from 'react';

interface SIWEConnectProps {
  onConnect?: (address: string, sessionId: string) => void;
  onDisconnect?: () => void;
  className?: string;
}

export function SIWEConnect({ onConnect, onDisconnect, className = '' }: SIWEConnectProps) {
  const [isConnecting, setIsConnecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [address, setAddress] = useState<string | null>(null);
  const [chainId, setChainId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleConnect = async () => {
    setIsConnecting(true);
    setError(null);

    try {
      // Check if wallet is available
      if (typeof window === 'undefined' || !window.ethereum) {
        throw new Error('No wallet found. Please install MetaMask or another Web3 wallet.');
      }

      // Request account access
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts',
      }) as string[];

      if (!accounts || accounts.length === 0) {
        throw new Error('No accounts found');
      }

      const userAddress = accounts[0];

      // Get chain ID
      const chainIdHex = await window.ethereum.request({
        method: 'eth_chainId',
      }) as string;
      const currentChainId = parseInt(chainIdHex, 16);
      setChainId(currentChainId);

      // Get nonce from server
      const nonceResponse = await fetch('/api/auth/nonce');
      const { nonce, expires_at } = await nonceResponse.json();

      // Create SIWE message
      const domain = window.location.host;
      const origin = window.location.origin;
      const statement = 'Sign in to Crypteolas - DeFi Analytics & GitHub Intelligence';

      const message = createSiweMessage({
        domain,
        address: userAddress,
        statement,
        uri: origin,
        version: '1',
        chainId: currentChainId,
        nonce,
        issuedAt: new Date().toISOString(),
        expirationTime: expires_at,
      });

      // Sign message
      const signature = await window.ethereum.request({
        method: 'personal_sign',
        params: [message, userAddress],
      });

      // Verify with server
      const verifyResponse = await fetch('/api/auth/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, signature }),
      });

      const result = await verifyResponse.json();

      if (result.success) {
        setAddress(userAddress);
        setIsConnected(true);
        onConnect?.(userAddress, result.session_id);
      } else {
        throw new Error('Verification failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection failed');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleDisconnect = async () => {
    setAddress(null);
    setChainId(null);
    setIsConnected(false);
    onDisconnect?.();
  };

  if (isConnected && address) {
    return (
      <div className={`flex items-center gap-3 ${className}`}>
        <div className="flex items-center gap-2 px-3 py-2 bg-indigo-900/50 rounded-lg border border-indigo-700">
          <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
          <span className="text-indigo-300 text-sm font-mono">
            {address.slice(0, 6)}...{address.slice(-4)}
          </span>
          {chainId && (
            <ChainBadge chainId={chainId} />
          )}
        </div>
        <button
          onClick={handleDisconnect}
          className="px-3 py-2 text-sm text-slate-400 hover:text-white transition-colors"
        >
          Disconnect
        </button>
      </div>
    );
  }

  return (
    <div className={className}>
      <button
        onClick={handleConnect}
        disabled={isConnecting}
        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
      >
        {isConnecting ? (
          <>
            <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Connecting...
          </>
        ) : (
          <>
            <WalletIcon />
            Connect Wallet
          </>
        )}
      </button>
      {error && (
        <p className="mt-2 text-sm text-red-400">{error}</p>
      )}
    </div>
  );
}

function ChainBadge({ chainId }: { chainId: number }) {
  const chains: Record<number, { name: string; color: string }> = {
    1: { name: 'ETH', color: 'bg-blue-500' },
    42161: { name: 'ARB', color: 'bg-blue-400' },
    10: { name: 'OP', color: 'bg-red-500' },
    137: { name: 'MATIC', color: 'bg-purple-500' },
    8453: { name: 'BASE', color: 'bg-blue-600' },
    43114: { name: 'AVAX', color: 'bg-red-600' },
    56: { name: 'BNB', color: 'bg-yellow-500' },
  };

  const chain = chains[chainId] || { name: `${chainId}`, color: 'bg-slate-500' };

  return (
    <span className={`px-1.5 py-0.5 text-xs text-white rounded ${chain.color}`}>
      {chain.name}
    </span>
  );
}

function WalletIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
      />
    </svg>
  );
}

interface SiweMessageParams {
  domain: string;
  address: string;
  statement: string;
  uri: string;
  version: string;
  chainId: number;
  nonce: string;
  issuedAt: string;
  expirationTime: string;
}

function createSiweMessage(params: SiweMessageParams): string {
  return `${params.domain} wants you to sign in with your Ethereum account:
${params.address}

${params.statement}

URI: ${params.uri}
Version: ${params.version}
Chain ID: ${params.chainId}
Nonce: ${params.nonce}
Issued At: ${params.issuedAt}
Expiration Time: ${params.expirationTime}`;
}

// Type declaration for window.ethereum
declare global {
  interface Window {
    ethereum?: {
      request: (args: { method: string; params?: unknown[] }) => Promise<unknown>;
      on: (event: string, callback: (...args: unknown[]) => void) => void;
      removeListener: (event: string, callback: (...args: unknown[]) => void) => void;
    };
  }
}

export default SIWEConnect;
