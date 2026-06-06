/**
 * X402 Payment Provider
 *
 * React context for managing x402 payments on the frontend.
 * Integrates with wagmi wallet and the usage store.
 */

import React, { createContext, useContext, useCallback, useState, useEffect } from "react";
import { useAccount, useSignTypedData, useChainId, useSwitchChain } from "wagmi";
import type { Address } from "viem";
import { useUsageStore } from "../../stores/usage";
import {
  DEFAULT_NETWORK,
  getNetworkByChainId,
  type NetworkConfig,
} from "./networks";
import {
  getFeaturePricing,
  atomicToUsd,
  type FeaturePricing,
} from "./pricing";

// EIP-3009 domain for USDC transferWithAuthorization
const EIP3009_DOMAIN = {
  name: "USD Coin",
  version: "2",
} as const;

// EIP-3009 types
const EIP3009_TYPES = {
  TransferWithAuthorization: [
    { name: "from", type: "address" },
    { name: "to", type: "address" },
    { name: "value", type: "uint256" },
    { name: "validAfter", type: "uint256" },
    { name: "validBefore", type: "uint256" },
    { name: "nonce", type: "bytes32" },
  ],
} as const;

export interface PaymentRequest {
  featureId: string;
  resourceUrl: string;
  description: string;
  onSuccess?: (txHash: string) => void;
  onError?: (error: string) => void;
}

export interface PendingPayment {
  featureId: string;
  pricing: FeaturePricing;
  resourceUrl: string;
  description: string;
  network: NetworkConfig;
  onSuccess?: (txHash: string) => void;
  onError?: (error: string) => void;
}

interface X402ContextValue {
  // Current network
  network: NetworkConfig;
  setNetwork: (network: NetworkConfig) => void;

  // Payment state
  pendingPayment: PendingPayment | null;
  isPaymentModalOpen: boolean;
  isProcessing: boolean;

  // Actions
  requestPayment: (request: PaymentRequest) => void;
  cancelPayment: () => void;
  confirmPayment: () => Promise<void>;

  // Payment signing (for direct API calls)
  signPayment: (
    featureId: string,
    resourceUrl: string,
    recipientAddress: Address
  ) => Promise<string | null>;

  // Usage helpers
  needsPayment: (featureId: string) => boolean;
  getRemainingFree: (featureId: string) => number;
}

const X402Context = createContext<X402ContextValue | null>(null);

export function X402Provider({ children }: { children: React.ReactNode }) {
  const { address, isConnected } = useAccount();
  const chainId = useChainId();
  const { switchChain } = useSwitchChain();
  const { signTypedDataAsync } = useSignTypedData();

  const usageStore = useUsageStore();

  const [network, setNetwork] = useState<NetworkConfig>(DEFAULT_NETWORK);
  const [pendingPayment, setPendingPayment] = useState<PendingPayment | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Sync wallet address with usage store
  useEffect(() => {
    usageStore.setWallet(address || null);
  }, [address]);

  // Check if current chain matches target network
  const isCorrectChain = chainId === network.chainId;

  // Generate random nonce for EIP-3009
  const generateNonce = (): `0x${string}` => {
    const bytes = new Uint8Array(32);
    crypto.getRandomValues(bytes);
    return `0x${Array.from(bytes)
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("")}` as `0x${string}`;
  };

  // Sign a payment using EIP-3009 transferWithAuthorization
  const signPayment = useCallback(
    async (
      featureId: string,
      resourceUrl: string,
      recipientAddress: Address
    ): Promise<string | null> => {
      if (!address || !isConnected) {
        console.error("Wallet not connected");
        return null;
      }

      const pricing = getFeaturePricing(featureId);
      if (!pricing) {
        console.error(`Unknown feature: ${featureId}`);
        return null;
      }

      // Switch chain if needed
      if (!isCorrectChain) {
        try {
          await switchChain({ chainId: network.chainId });
        } catch (e) {
          console.error("Failed to switch chain:", e);
          return null;
        }
      }

      const now = Math.floor(Date.now() / 1000);
      const validAfter = now - 60; // Valid from 1 minute ago
      const validBefore = now + 300; // Valid for 5 minutes
      const nonce = generateNonce();

      try {
        // Sign EIP-712 typed data
        const signature = await signTypedDataAsync({
          domain: {
            ...EIP3009_DOMAIN,
            chainId: network.chainId,
            verifyingContract: network.usdc,
          },
          types: EIP3009_TYPES,
          primaryType: "TransferWithAuthorization",
          message: {
            from: address,
            to: recipientAddress,
            value: pricing.priceAtomic,
            validAfter: BigInt(validAfter),
            validBefore: BigInt(validBefore),
            nonce,
          },
        });

        // Build payment payload
        const paymentPayload = {
          x402Version: 2,
          resource: {
            url: resourceUrl,
            description: pricing.description,
            mimeType: "application/json",
          },
          accepted: {
            scheme: "exact" as const,
            network: network.x402Network,
            amount: pricing.priceAtomic.toString(),
            asset: network.usdc,
            payTo: recipientAddress,
            maxTimeoutSeconds: 300,
            extra: {
              name: "USDC",
              version: "2",
            },
          },
          payload: {
            signature,
            authorization: {
              from: address,
              to: recipientAddress,
              value: pricing.priceAtomic.toString(),
              validAfter: validAfter.toString(),
              validBefore: validBefore.toString(),
              nonce,
            },
          },
        };

        // Encode for header
        return btoa(JSON.stringify(paymentPayload));
      } catch (error) {
        console.error("Failed to sign payment:", error);
        return null;
      }
    },
    [address, isConnected, isCorrectChain, network, signTypedDataAsync, switchChain]
  );

  // Request a payment (opens modal)
  const requestPayment = useCallback(
    (request: PaymentRequest) => {
      const pricing = getFeaturePricing(request.featureId);
      if (!pricing) {
        request.onError?.(`Unknown feature: ${request.featureId}`);
        return;
      }

      setPendingPayment({
        featureId: request.featureId,
        pricing,
        resourceUrl: request.resourceUrl,
        description: request.description,
        network,
        onSuccess: request.onSuccess,
        onError: request.onError,
      });
    },
    [network]
  );

  // Cancel pending payment
  const cancelPayment = useCallback(() => {
    if (pendingPayment?.onError) {
      pendingPayment.onError("Payment cancelled");
    }
    setPendingPayment(null);
  }, [pendingPayment]);

  // Confirm and process payment
  const confirmPayment = useCallback(async () => {
    if (!pendingPayment || !address) return;

    setIsProcessing(true);

    try {
      // Get recipient address from environment or use default
      const recipient = (process.env.NEXT_PUBLIC_PAYMENT_RECIPIENT ||
        "0x0000000000000000000000000000000000000000") as Address;

      const paymentHeader = await signPayment(
        pendingPayment.featureId,
        pendingPayment.resourceUrl,
        recipient
      );

      if (!paymentHeader) {
        throw new Error("Failed to sign payment");
      }

      // Make the API request with payment header
      const response = await fetch(pendingPayment.resourceUrl, {
        headers: {
          "PAYMENT-SIGNATURE": paymentHeader,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Payment failed");
      }

      // Get settlement info from response
      const settlementHeader =
        response.headers.get("PAYMENT-RESPONSE") ||
        response.headers.get("X-PAYMENT-RESPONSE");

      let txHash = "";
      if (settlementHeader) {
        try {
          const settlement = JSON.parse(atob(settlementHeader));
          txHash = settlement.transaction || "";
        } catch {}
      }

      // Record payment in usage store
      usageStore.recordPayment({
        featureId: pendingPayment.featureId,
        amount: pendingPayment.pricing.priceAtomic.toString(),
        network: pendingPayment.network.name,
        txHash,
      });

      pendingPayment.onSuccess?.(txHash);
      setPendingPayment(null);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Payment failed";
      pendingPayment.onError?.(message);
    } finally {
      setIsProcessing(false);
    }
  }, [pendingPayment, address, signPayment, usageStore]);

  // Usage helpers
  const needsPayment = useCallback(
    (featureId: string) => usageStore.needsPayment(featureId),
    [usageStore]
  );

  const getRemainingFree = useCallback(
    (featureId: string) => usageStore.getRemainingFree(featureId),
    [usageStore]
  );

  const value: X402ContextValue = {
    network,
    setNetwork,
    pendingPayment,
    isPaymentModalOpen: pendingPayment !== null,
    isProcessing,
    requestPayment,
    cancelPayment,
    confirmPayment,
    signPayment,
    needsPayment,
    getRemainingFree,
  };

  return <X402Context.Provider value={value}>{children}</X402Context.Provider>;
}

export function useX402() {
  const context = useContext(X402Context);
  if (!context) {
    throw new Error("useX402 must be used within an X402Provider");
  }
  return context;
}

// Hook for making paid API calls
export function usePaidFetch() {
  const { signPayment, needsPayment } = useX402();
  const usageStore = useUsageStore();

  const paidFetch = useCallback(
    async (
      featureId: string,
      url: string,
      options: RequestInit = {}
    ): Promise<Response> => {
      // Check if payment is needed
      if (!needsPayment(featureId)) {
        // Free tier - just make the request and increment usage
        const response = await fetch(url, options);
        if (response.ok) {
          usageStore.incrementUsage(featureId);
        }
        return response;
      }

      // Payment needed - sign and include in request
      const recipient = (process.env.NEXT_PUBLIC_PAYMENT_RECIPIENT ||
        "0x0000000000000000000000000000000000000000") as Address;

      const paymentHeader = await signPayment(featureId, url, recipient);
      if (!paymentHeader) {
        throw new Error("Failed to sign payment");
      }

      const headers = new Headers(options.headers);
      headers.set("PAYMENT-SIGNATURE", paymentHeader);

      return fetch(url, {
        ...options,
        headers,
      });
    },
    [signPayment, needsPayment, usageStore]
  );

  return paidFetch;
}
