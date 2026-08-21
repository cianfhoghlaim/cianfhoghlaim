/**
 * Authentication hook for SIWE
 */

import { useCallback, useEffect, useState } from 'react';

interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  address: string | null;
  playerId: string | null;
  sessionId: string | null;
  freeMessagesRemaining: number;
  freeSearchesRemaining: number;
}

interface AuthActions {
  connect: () => Promise<void>;
  disconnect: () => Promise<void>;
  refreshSession: () => Promise<void>;
}

const STORAGE_KEY = 'tuath_session';

export function useAuth(): AuthState & AuthActions {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    address: null,
    playerId: null,
    sessionId: null,
    freeMessagesRemaining: 5,
    freeSearchesRemaining: 3,
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
                playerId: session.player_id,
                sessionId,
                freeMessagesRemaining: session.free_messages_remaining,
                freeSearchesRemaining: session.free_searches_remaining,
              });
              return;
            }
          }
        }
      } catch (err) {
        console.error('Failed to load session:', err);
      }
      setState(prev => ({ ...prev, isLoading: false }));
    };

    loadSession();
  }, []);

  const connect = useCallback(async () => {
    if (typeof window === 'undefined' || !window.ethereum) {
      throw new Error('No wallet found');
    }

    setState(prev => ({ ...prev, isLoading: true }));

    try {
      // Request accounts
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts',
      }) as string[];

      if (!accounts || accounts.length === 0) {
        throw new Error('No accounts found');
      }

      const userAddress = accounts[0];

      // Get nonce
      const nonceResponse = await fetch('/api/auth/nonce');
      const { nonce, expires_at } = await nonceResponse.json();

      // Create SIWE message
      const domain = window.location.host;
      const origin = window.location.origin;
      const message = `${domain} wants you to sign in with your Ethereum account:
${userAddress}

Sign in to Tuath - Celtic Educational MMO

URI: ${origin}
Version: 1
Chain ID: 1
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
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
          sessionId: result.session_id,
          address: result.address,
        }));

        setState({
          isAuthenticated: true,
          isLoading: false,
          address: result.address,
          playerId: result.player_id,
          sessionId: result.session_id,
          freeMessagesRemaining: 5,
          freeSearchesRemaining: 3,
        });
      } else {
        throw new Error('Verification failed');
      }
    } catch (err) {
      setState(prev => ({ ...prev, isLoading: false }));
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
      playerId: null,
      sessionId: null,
      freeMessagesRemaining: 5,
      freeSearchesRemaining: 3,
    });
  }, [state.sessionId]);

  const refreshSession = useCallback(async () => {
    if (!state.sessionId) return;

    try {
      const response = await fetch(`/api/auth/session/${state.sessionId}`);
      if (response.ok) {
        const session = await response.json();
        setState(prev => ({
          ...prev,
          freeMessagesRemaining: session.free_messages_remaining,
          freeSearchesRemaining: session.free_searches_remaining,
        }));
      } else {
        // Session expired
        await disconnect();
      }
    } catch (err) {
      console.error('Failed to refresh session:', err);
    }
  }, [state.sessionId, disconnect]);

  return {
    ...state,
    connect,
    disconnect,
    refreshSession,
  };
}

// Type declaration for window.ethereum
declare global {
  interface Window {
    ethereum?: {
      request: (args: { method: string; params?: unknown[] }) => Promise<unknown>;
    };
  }
}
