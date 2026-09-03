/**
 * SIWE (Sign-In With Ethereum) Connect Component
 *
 * Configurable wallet connect button for all Cianfhoghlaim platforms
 */

import { useState } from 'react';
import { cn } from '../../lib/cn';

export interface SIWETheme {
  /** Connected state background */
  connectedBg?: string;
  /** Connected state border */
  connectedBorder?: string;
  /** Connected state text */
  connectedText?: string;
  /** Status dot color */
  statusDot?: string;
  /** Button background */
  buttonBg?: string;
  /** Button hover background */
  buttonHover?: string;
  /** Button disabled background */
  buttonDisabled?: string;
  /** Button text color */
  buttonText?: string;
}

export interface SIWEConnectProps {
  /** Sign-in statement shown to user */
  statement?: string;
  /** API endpoint for nonce */
  nonceEndpoint?: string;
  /** API endpoint for verification */
  verifyEndpoint?: string;
  /** Default chain ID */
  chainId?: number;
  /** Theme configuration */
  theme?: SIWETheme;
  /** Called on successful connection */
  onConnect?: (address: string, sessionId: string) => void;
  /** Called on disconnect */
  onDisconnect?: () => void;
  /** Additional CSS classes */
  className?: string;
  /** Show chain badge */
  showChainBadge?: boolean;
}

const defaultTheme: SIWETheme = {
  connectedBg: 'bg-emerald-900/50',
  connectedBorder: 'border-emerald-700',
  connectedText: 'text-emerald-300',
  statusDot: 'bg-emerald-400',
  buttonBg: 'bg-indigo-600',
  buttonHover: 'hover:bg-indigo-500',
  buttonDisabled: 'disabled:bg-indigo-800',
  buttonText: 'text-white',
};

export function SIWEConnect({
  statement = 'Sign in with your Ethereum wallet',
  nonceEndpoint = '/api/auth/nonce',
  verifyEndpoint = '/api/auth/verify',
  chainId: defaultChainId,
  theme: customTheme,
  onConnect,
  onDisconnect,
  className = '',
  showChainBadge = true,
}: SIWEConnectProps) {
  const theme = { ...defaultTheme, ...customTheme };

  const [isConnecting, setIsConnecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [address, setAddress] = useState<string | null>(null);
  const [chainId, setChainId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleConnect = async () => {
    setIsConnecting(true);
    setError(null);

    try {
      if (typeof window === 'undefined' || !window.ethereum) {
        throw new Error('No wallet found. Please install MetaMask or another Web3 wallet.');
      }

      const accounts = (await window.ethereum.request({
        method: 'eth_requestAccounts',
      })) as string[];

      if (!accounts || accounts.length === 0) {
        throw new Error('No accounts found');
      }

      const userAddress = accounts[0];

      const chainIdHex = (await window.ethereum.request({
        method: 'eth_chainId',
      })) as string;
      const currentChainId = defaultChainId || parseInt(chainIdHex, 16);
      setChainId(currentChainId);

      const nonceResponse = await fetch(nonceEndpoint);
      const { nonce, expires_at } = await nonceResponse.json();

      const domain = window.location.host;
      const origin = window.location.origin;

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

      const signature = await window.ethereum.request({
        method: 'personal_sign',
        params: [message, userAddress],
      });

      const verifyResponse = await fetch(verifyEndpoint, {
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
      <div className={cn('flex items-center gap-3', className)}>
        <div
          className={cn(
            'flex items-center gap-2 px-3 py-2 rounded-lg border',
            theme.connectedBg,
            theme.connectedBorder
          )}
        >
          <div className={cn('w-2 h-2 rounded-full animate-pulse', theme.statusDot)} />
          <span className={cn('text-sm font-mono', theme.connectedText)}>
            {address.slice(0, 6)}...{address.slice(-4)}
          </span>
          {showChainBadge && chainId && <ChainBadge chainId={chainId} />}
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
        className={cn(
          'px-4 py-2 font-medium rounded-lg transition-colors flex items-center gap-2',
          theme.buttonBg,
          theme.buttonHover,
          theme.buttonDisabled,
          theme.buttonText
        )}
      >
        {isConnecting ? (
          <>
            <span
              className={cn(
                'w-4 h-4 border-2 border-t-transparent rounded-full animate-spin',
                theme.buttonText === 'text-white' ? 'border-white' : 'border-slate-900'
              )}
            />
            Connecting...
          </>
        ) : (
          <>
            <WalletIcon />
            Connect Wallet
          </>
        )}
      </button>
      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
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
    <span className={cn('px-1.5 py-0.5 text-xs text-white rounded', chain.color)}>
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
