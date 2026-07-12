/**
 * Payment hook for x402 micropayments
 */

import { useCallback, useState } from 'react';

interface PaymentState {
  isLoading: boolean;
  error: string | null;
  currentPayment: PaymentRequest | null;
  completedPayments: string[];
}

interface PaymentRequest {
  paymentId: string;
  resourceType: string;
  priceUsd: number;
  priceCrypto: number;
  token: string;
  receiverAddress: string;
  expiresAt: string;
}

interface PaymentActions {
  requestPayment: (resourceType: string, token?: string) => Promise<PaymentRequest>;
  submitPayment: (paymentId: string, txHash: string) => Promise<boolean>;
  checkFreeUsage: (resourceType: string, sessionId?: string) => Promise<boolean>;
  clearPayment: () => void;
}

export function usePayment(): PaymentState & PaymentActions {
  const [state, setState] = useState<PaymentState>({
    isLoading: false,
    error: null,
    currentPayment: null,
    completedPayments: [],
  });

  const requestPayment = useCallback(async (
    resourceType: string,
    token: string = 'USDC'
  ): Promise<PaymentRequest> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await fetch(`/api/payments/request/${resourceType}?token=${token}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to request payment');
      }

      const data = await response.json();

      const payment: PaymentRequest = {
        paymentId: data.payment_id,
        resourceType: data.resource_type,
        priceUsd: data.price_usd,
        priceCrypto: data.price_crypto,
        token: data.token,
        receiverAddress: data.receiver_address,
        expiresAt: data.expires_at,
      };

      setState(prev => ({
        ...prev,
        isLoading: false,
        currentPayment: payment,
      }));

      return payment;
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Payment request failed';
      setState(prev => ({ ...prev, isLoading: false, error }));
      throw err;
    }
  }, []);

  const submitPayment = useCallback(async (
    paymentId: string,
    txHash: string
  ): Promise<boolean> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await fetch('/api/payments/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          payment_id: paymentId,
          transaction_hash: txHash,
          token: state.currentPayment?.token || 'USDC',
          amount: state.currentPayment?.priceCrypto?.toString() || '0',
        }),
      });

      const result = await response.json();

      if (result.access_granted) {
        setState(prev => ({
          ...prev,
          isLoading: false,
          currentPayment: null,
          completedPayments: [...prev.completedPayments, paymentId],
        }));
        return true;
      } else {
        throw new Error(result.message || 'Payment verification failed');
      }
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Payment verification failed';
      setState(prev => ({ ...prev, isLoading: false, error }));
      return false;
    }
  }, [state.currentPayment]);

  const checkFreeUsage = useCallback(async (
    resourceType: string,
    sessionId?: string
  ): Promise<boolean> => {
    try {
      const response = await fetch(`/api/payments/usage/${resourceType}`, {
        headers: sessionId ? { 'X-Session-ID': sessionId } : {},
      });

      if (!response.ok) {
        return false;
      }

      const data = await response.json();
      return !data.requires_payment;
    } catch {
      return false;
    }
  }, []);

  const clearPayment = useCallback(() => {
    setState(prev => ({
      ...prev,
      currentPayment: null,
      error: null,
    }));
  }, []);

  return {
    ...state,
    requestPayment,
    submitPayment,
    checkFreeUsage,
    clearPayment,
  };
}

/**
 * Pricing configuration
 */
export const PRICING = {
  chat_message: {
    priceUsd: 0.01,
    freeDailyLimit: 5,
    description: 'AI chat message',
  },
  knowledge_search: {
    priceUsd: 0.02,
    freeDailyLimit: 3,
    description: 'Knowledge base search',
  },
  premium_quest: {
    priceUsd: 0.05,
    freeDailyLimit: 0,
    description: 'Premium quest access',
  },
  analytics: {
    priceUsd: 0.05,
    freeDailyLimit: 0,
    description: 'Learning analytics',
  },
} as const;

export type ResourceType = keyof typeof PRICING;

/**
 * Format price for display
 */
export function formatPrice(priceUsd: number): string {
  if (priceUsd < 0.01) {
    return `$${priceUsd.toFixed(4)}`;
  }
  return `$${priceUsd.toFixed(2)}`;
}

/**
 * Calculate crypto equivalent (simplified)
 */
export function calculateCryptoPrice(
  priceUsd: number,
  token: 'USDC' | 'ETH',
  ethPrice: number = 2500
): number {
  if (token === 'USDC') {
    return priceUsd;
  }
  return priceUsd / ethPrice;
}
