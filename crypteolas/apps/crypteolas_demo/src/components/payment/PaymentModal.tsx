/**
 * Payment Modal Component
 *
 * Displays when a user needs to pay for a feature.
 * Shows pricing, network, and payment confirmation.
 */

import { useAccount, useChainId, useSwitchChain } from "wagmi";
import { useX402 } from "../../lib/x402/provider";
import { atomicToUsd } from "../../lib/x402/pricing";
import { Loader2, Wallet, ExternalLink, X, AlertCircle } from "lucide-react";

export function PaymentModal() {
  const { address, isConnected } = useAccount();
  const chainId = useChainId();
  const { switchChain, isPending: isSwitching } = useSwitchChain();

  const {
    pendingPayment,
    isPaymentModalOpen,
    isProcessing,
    cancelPayment,
    confirmPayment,
  } = useX402();

  if (!isPaymentModalOpen || !pendingPayment) {
    return null;
  }

  const { pricing, network, description } = pendingPayment;
  const isCorrectChain = chainId === network.chainId;
  const priceDisplay = atomicToUsd(pricing.priceAtomic);

  const handleSwitchChain = async () => {
    try {
      await switchChain({ chainId: network.chainId });
    } catch (error) {
      console.error("Failed to switch chain:", error);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={cancelPayment}
      />

      {/* Modal */}
      <div className="relative z-10 w-full max-w-md rounded-xl border bg-card p-6 shadow-xl">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Payment Required</h2>
          <button
            onClick={cancelPayment}
            className="rounded-full p-1 hover:bg-muted"
            disabled={isProcessing}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="space-y-4">
          {/* Feature info */}
          <div className="rounded-lg border bg-muted/50 p-4">
            <div className="text-sm text-muted-foreground">Feature</div>
            <div className="font-medium">{pricing.name}</div>
            <div className="mt-1 text-sm text-muted-foreground">
              {description}
            </div>
          </div>

          {/* Price */}
          <div className="flex items-center justify-between rounded-lg border p-4">
            <div>
              <div className="text-sm text-muted-foreground">Price</div>
              <div className="text-2xl font-bold">{priceDisplay}</div>
            </div>
            <div className="text-right">
              <div className="text-sm text-muted-foreground">Network</div>
              <div className="font-medium">{network.displayName}</div>
            </div>
          </div>

          {/* Wallet status */}
          {!isConnected ? (
            <div className="flex items-center gap-3 rounded-lg border border-yellow-500/50 bg-yellow-500/10 p-4">
              <AlertCircle className="h-5 w-5 text-yellow-500" />
              <div className="text-sm">
                Please connect your wallet to make a payment.
              </div>
            </div>
          ) : !isCorrectChain ? (
            <div className="rounded-lg border border-yellow-500/50 bg-yellow-500/10 p-4">
              <div className="mb-3 flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-yellow-500" />
                <span className="text-sm font-medium">Wrong Network</span>
              </div>
              <p className="mb-3 text-sm text-muted-foreground">
                Please switch to {network.displayName} to complete this payment.
              </p>
              <button
                onClick={handleSwitchChain}
                disabled={isSwitching}
                className="w-full rounded-lg bg-yellow-500 px-4 py-2 text-sm font-medium text-black hover:bg-yellow-400 disabled:opacity-50"
              >
                {isSwitching ? (
                  <span className="flex items-center justify-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Switching...
                  </span>
                ) : (
                  `Switch to ${network.displayName}`
                )}
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3 rounded-lg border border-green-500/50 bg-green-500/10 p-4">
              <Wallet className="h-5 w-5 text-green-500" />
              <div className="flex-1">
                <div className="text-sm font-medium">Connected</div>
                <div className="font-mono text-xs text-muted-foreground">
                  {address?.slice(0, 6)}...{address?.slice(-4)}
                </div>
              </div>
            </div>
          )}

          {/* Payment info */}
          <div className="rounded-lg border p-4 text-sm">
            <div className="mb-2 font-medium">Payment Details</div>
            <div className="space-y-1 text-muted-foreground">
              <div className="flex justify-between">
                <span>Token:</span>
                <span className="font-mono">USDC</span>
              </div>
              <div className="flex justify-between">
                <span>Network:</span>
                <span>{network.displayName}</span>
              </div>
              <div className="flex justify-between">
                <span>Protocol:</span>
                <span>x402 (EIP-3009)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="mt-6 flex gap-3">
          <button
            onClick={cancelPayment}
            disabled={isProcessing}
            className="flex-1 rounded-lg border px-4 py-2 text-sm font-medium hover:bg-muted disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={confirmPayment}
            disabled={!isConnected || !isCorrectChain || isProcessing}
            className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {isProcessing ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Processing...
              </span>
            ) : (
              `Pay ${priceDisplay}`
            )}
          </button>
        </div>

        {/* Footer links */}
        <div className="mt-4 flex justify-center gap-4 text-xs text-muted-foreground">
          <a
            href={network.explorerUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 hover:text-foreground"
          >
            <ExternalLink className="h-3 w-3" />
            Block Explorer
          </a>
          <a
            href="https://x402.org"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 hover:text-foreground"
          >
            <ExternalLink className="h-3 w-3" />
            x402 Protocol
          </a>
        </div>
      </div>
    </div>
  );
}
