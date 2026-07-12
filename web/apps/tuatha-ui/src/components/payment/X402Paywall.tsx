/**
 * x402 Payment Paywall Component
 *
 * Shows payment requirement and handles micropayment flow
 */

import { useState } from 'react';

interface PaymentRequirement {
  resourceType: string;
  priceUsd: number;
  priceCrypto: number;
  token: string;
  receiverAddress: string;
  paymentId: string;
  expiresAt: string;
}

interface X402PaywallProps {
  paymentRequired: PaymentRequirement;
  onPaymentComplete?: (paymentId: string) => void;
  onClose?: () => void;
  children?: React.ReactNode;
}

export function X402Paywall({
  paymentRequired,
  onPaymentComplete,
  onClose,
  children,
}: X402PaywallProps) {
  const [isPaying, setIsPaying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [txHash, setTxHash] = useState<string | null>(null);

  const handlePayment = async () => {
    setIsPaying(true);
    setError(null);

    try {
      if (typeof window === 'undefined' || !window.ethereum) {
        throw new Error('No wallet connected');
      }

      // Get current account
      const accounts = await window.ethereum.request({
        method: 'eth_accounts',
      }) as string[];

      if (!accounts || accounts.length === 0) {
        throw new Error('Please connect your wallet first');
      }

      const fromAddress = accounts[0];

      // For USDC, we'd need to call the token contract
      // For simplicity, this example uses native ETH
      if (paymentRequired.token === 'ETH') {
        // Convert to wei
        const valueInWei = BigInt(Math.floor(paymentRequired.priceCrypto * 1e18));

        const tx = await window.ethereum.request({
          method: 'eth_sendTransaction',
          params: [{
            from: fromAddress,
            to: paymentRequired.receiverAddress,
            value: '0x' + valueInWei.toString(16),
          }],
        });

        setTxHash(tx as string);

        // Verify payment with server
        const verifyResponse = await fetch('/api/payments/verify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            payment_id: paymentRequired.paymentId,
            transaction_hash: tx,
            token: paymentRequired.token,
            amount: paymentRequired.priceCrypto.toString(),
          }),
        });

        const result = await verifyResponse.json();

        if (result.access_granted) {
          onPaymentComplete?.(paymentRequired.paymentId);
        } else {
          throw new Error(result.message || 'Payment verification failed');
        }
      } else {
        // For USDC, would need ERC-20 transfer
        throw new Error('USDC payments not yet implemented in demo');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Payment failed');
    } finally {
      setIsPaying(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-xl border border-amber-500/50 max-w-md w-full p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-amber-300">Payment Required</h3>
          {onClose && (
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white text-2xl"
            >
              ×
            </button>
          )}
        </div>

        {/* Content */}
        {children && (
          <div className="mb-4 text-slate-300">
            {children}
          </div>
        )}

        {/* Price */}
        <div className="bg-slate-700/50 rounded-lg p-4 mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-slate-400">Resource:</span>
            <span className="text-white capitalize">
              {paymentRequired.resourceType.replace(/_/g, ' ')}
            </span>
          </div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-slate-400">Price:</span>
            <span className="text-amber-300 font-bold">
              ${paymentRequired.priceUsd.toFixed(2)} USD
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-slate-400">Pay with:</span>
            <span className="text-emerald-300">
              {paymentRequired.priceCrypto.toFixed(6)} {paymentRequired.token}
            </span>
          </div>
        </div>

        {/* Payment Info */}
        <div className="text-sm text-slate-400 mb-4">
          <p>Payment will be sent to:</p>
          <p className="font-mono text-xs text-slate-500 break-all mt-1">
            {paymentRequired.receiverAddress}
          </p>
        </div>

        {/* Transaction Hash */}
        {txHash && (
          <div className="bg-emerald-900/30 border border-emerald-700 rounded p-3 mb-4">
            <p className="text-emerald-300 text-sm">Transaction submitted!</p>
            <p className="font-mono text-xs text-emerald-400 break-all mt-1">
              {txHash}
            </p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded p-3 mb-4">
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={handlePayment}
            disabled={isPaying}
            className="flex-1 py-3 bg-amber-500 hover:bg-amber-400 disabled:bg-amber-700 text-slate-900 font-bold rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            {isPaying ? (
              <>
                <span className="w-4 h-4 border-2 border-slate-900 border-t-transparent rounded-full animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <PaymentIcon />
                Pay Now
              </>
            )}
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
            >
              Cancel
            </button>
          )}
        </div>

        {/* Protocol Badge */}
        <div className="mt-4 text-center">
          <span className="text-xs text-slate-500">
            Powered by x402 Micropayments
          </span>
        </div>
      </div>
    </div>
  );
}

function PaymentIcon() {
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

/**
 * Hook to check if payment is required for a resource
 */
export function usePaymentCheck(resourceType: string) {
  const [isChecking, setIsChecking] = useState(false);
  const [paymentRequired, setPaymentRequired] = useState<PaymentRequirement | null>(null);

  const checkPayment = async (sessionId?: string) => {
    setIsChecking(true);
    try {
      const response = await fetch(`/api/payments/usage/${resourceType}`, {
        headers: sessionId ? { 'X-Session-ID': sessionId } : {},
      });
      const data = await response.json();

      if (data.requires_payment) {
        // Get payment request
        const paymentResponse = await fetch(`/api/payments/request/${resourceType}`, {
          method: 'POST',
        });
        const paymentData = await paymentResponse.json();
        setPaymentRequired({
          resourceType: paymentData.resource_type,
          priceUsd: paymentData.price_usd,
          priceCrypto: paymentData.price_crypto,
          token: paymentData.token,
          receiverAddress: paymentData.receiver_address,
          paymentId: paymentData.payment_id,
          expiresAt: paymentData.expires_at,
        });
      } else {
        setPaymentRequired(null);
      }
    } catch (err) {
      console.error('Payment check failed:', err);
    } finally {
      setIsChecking(false);
    }
  };

  return { isChecking, paymentRequired, checkPayment, clearPayment: () => setPaymentRequired(null) };
}
