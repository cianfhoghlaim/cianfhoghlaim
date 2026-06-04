/**
 * Authentication hook for SIWE in Crypteolas
 *
 * Manages wallet connection state and session for DeFi analytics
 */

import { useCallback, useEffect, useState } from 'react';

interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  address: string | null;
  chainId: number | null;
  sessionId: string | null;
  tier: 'free' | 'pro' | 'enterprise';
  apiCallsRemaining: number;
  analysesRemaining: number;
}

interface AuthActions {
  connect: () => Promise<void>;
  disconnect: () => Promise<void>;
  refreshSession: () => Promise<void>;
  switchChain: (chainId: number) => Promise<void>;
}

const STORAGE_KEY = 'crypteolas_session';

// Supported chains for Crypteolas
const SUPPORTED_CHAINS = [
  1,     // Ethereum
  42161, // Arbitrum
  10,    // Optimism
  137,   // Polygon
  8453,  // Base
  43114, // Avalanche
];

export function useAuth(): AuthState & AuthActions {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    address: null,
    chainId: null,
    sessionId: null,
    tier: 'free',
    apiCallsRemaining: 100,
    analysesRemaining: 5,
  });

  // Load session from storage on mount
  useEffect(() => {
    const loadSession = async () => {
      try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
          const { sessionId, address } = JSON.parse(stored);
          if (sessionId) {
            // Verify session is still valid
            const response = await fetch(`/api/auth/session/${sessionId}`);
            if (response.ok) {
              const session = await response.json();
              setState({
                isAuthenticated: true,
                isLoading: false,
                address: session.address,
                chainId: session.chain_id,
                sessionId,
                tier: session.tier || 'free',
                apiCallsRemaining: session.api_calls_remaining ?? 100,
                analysesRemaining: session.analyses_remaining ?? 5,
              });
              return;
            }
          }
        }
      } catch (err) {
        console.error('Failed to load session:', err);
      }
      setState((prev) => ({ ...prev, isLoading: false }));
    };

    loadSession();
  }, []);

  // Listen for chain changes
  useEffect(() => {
    if (typeof window === 'undefined' || !window.ethereum) return;

    const handleChainChanged = (chainIdHex: string) => {
      const newChainId = parseInt(chainIdHex, 16);
      setState((prev) => ({ ...prev, chainId: newChainId }));
    };

    const handleAccountsChanged = (accounts: string[]) => {
      if (accounts.length === 0) {
        // User disconnected
        disconnect();
      } else if (accounts[0] !== state.address) {
        // User switched accounts
        setState((prev) => ({ ...prev, address: accounts[0] }));
      }
    };

    window.ethereum.on('chainChanged', handleChainChanged as (...args: unknown[]) => void);
    window.ethereum.on('accountsChanged', handleAccountsChanged as (...args: unknown[]) => void);

    return () => {
      window.ethereum?.removeListener('chainChanged', handleChainChanged as (...args: unknown[]) => void);
      window.ethereum?.removeListener('accountsChanged', handleAccountsChanged as (...args: unknown[]) => void);
    };
  }, [state.address]);

  const connect = useCallback(async () => {
    if (typeof window === 'undefined' || !window.ethereum) {
      throw new Error('No wallet found');
    }

    setState((prev) => ({ ...prev, isLoading: true }));

    try {
      // Request accounts
      const accounts = (await window.ethereum.request({
        method: 'eth_requestAccounts',
      })) as string[];

      if (!accounts || accounts.length === 0) {
        throw new Error('No accounts found');
      }

      const userAddress = accounts[0];

      // Get chain ID
      const chainIdHex = (await window.ethereum.request({
        method: 'eth_chainId',
      })) as string;
      const currentChainId = parseInt(chainIdHex, 16);

      // Get nonce
      const nonceResponse = await fetch('/api/auth/nonce');
      const { nonce, expires_at } = await nonceResponse.json();

      // Create SIWE message
      const domain = window.location.host;
      const origin = window.location.origin;
      const message = `${domain} wants you to sign in with your Ethereum account:
${userAddress}

Sign in to Crypteolas - DeFi Analytics & GitHub Intelligence

URI: ${origin}
Version: 1
Chain ID: ${currentChainId}
Nonce: ${nonce}
Issued At: ${new Date().toISOString()}
Expiration Time: ${expires_at}`;

      // Sign message
      const signature = await window.ethereum.request({
        method: 'personal_sign',
        params: [message, userAddress],
      });

      // Verify
      const verifyResponse = await fetch('/api/auth/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, signature }),
      });

      const result = await verifyResponse.json();

      if (result.success) {
        // Store session
        localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({
            sessionId: result.session_id,
            address: result.address,
          })
        );

        setState({
          isAuthenticated: true,
          isLoading: false,
          address: result.address,
          chainId: currentChainId,
          sessionId: result.session_id,
          tier: result.tier || 'free',
          apiCallsRemaining: result.api_calls_remaining ?? 100,
          analysesRemaining: result.analyses_remaining ?? 5,
        });
      } else {
        throw new Error('Verification failed');
      }
    } catch (err) {
      setState((prev) => ({ ...prev, isLoading: false }));
      throw err;
    }
  }, []);

  const disconnect = useCallback(async () => {
    if (state.sessionId) {
      try {
        await fetch(`/api/auth/logout/${state.sessionId}`, {
          method: 'POST',
        });
      } catch (err) {
        console.error('Logout request failed:', err);
      }
    }

    localStorage.removeItem(STORAGE_KEY);

    setState({
      isAuthenticated: false,
      isLoading: false,
      address: null,
      chainId: null,
      sessionId: null,
      tier: 'free',
      apiCallsRemaining: 100,
      analysesRemaining: 5,
    });
  }, [state.sessionId]);

  const refreshSession = useCallback(async () => {
    if (!state.sessionId) return;

    try {
      const response = await fetch(`/api/auth/session/${state.sessionId}`);
      if (response.ok) {
        const session = await response.json();
        setState((prev) => ({
          ...prev,
          tier: session.tier || prev.tier,
          apiCallsRemaining: session.api_calls_remaining ?? prev.apiCallsRemaining,
          analysesRemaining: session.analyses_remaining ?? prev.analysesRemaining,
        }));
      } else {
        // Session expired
        await disconnect();
      }
    } catch (err) {
      console.error('Failed to refresh session:', err);
    }
  }, [state.sessionId, disconnect]);

  const switchChain = useCallback(async (chainId: number) => {
    if (typeof window === 'undefined' || !window.ethereum) {
      throw new Error('No wallet found');
    }

    if (!SUPPORTED_CHAINS.includes(chainId)) {
      throw new Error(`Chain ${chainId} is not supported`);
    }

    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: `0x${chainId.toString(16)}` }],
      });
    } catch (err: unknown) {
      // Chain not added, try to add it
      if ((err as { code?: number })?.code === 4902) {
        // Would need chain config to add it
        throw new Error('Please add this network to your wallet first');
      }
      throw err;
    }
  }, []);

  return {
    ...state,
    connect,
    disconnect,
    refreshSession,
    switchChain,
  };
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

export default useAuth;
