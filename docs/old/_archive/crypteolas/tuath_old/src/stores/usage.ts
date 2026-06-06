/**
 * Usage Tracking Store
 *
 * Tracks daily usage per feature for the free tier limits.
 * Persists to localStorage, keyed by wallet address.
 * Resets at midnight UTC.
 */

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { getFreeTierLimits, type FeaturePricing } from "../lib/x402/pricing";

export interface UsageRecord {
  featureId: string;
  timestamp: number;
  paid: boolean;
  txHash?: string;
}

export interface DailyUsage {
  [featureId: string]: number;
}

export interface PaymentRecord {
  featureId: string;
  amount: string; // atomic USDC
  network: string;
  txHash: string;
  timestamp: number;
}

interface UsageState {
  // Current wallet address
  walletAddress: string | null;
  // Today's usage counts per feature
  dailyUsage: DailyUsage;
  // Date string for reset check (YYYY-MM-DD UTC)
  usageDate: string;
  // Payment history
  payments: PaymentRecord[];
  // Total spent (atomic USDC)
  totalSpent: bigint;

  // Actions
  setWallet: (address: string | null) => void;
  incrementUsage: (featureId: string) => void;
  recordPayment: (payment: Omit<PaymentRecord, "timestamp">) => void;
  getUsageCount: (featureId: string) => number;
  getRemainingFree: (featureId: string) => number;
  needsPayment: (featureId: string) => boolean;
  resetIfNewDay: () => void;
  clearUsage: () => void;
}

// Get current UTC date string
function getUtcDateString(): string {
  return new Date().toISOString().split("T")[0];
}

// Custom serializer for BigInt
const storage = createJSONStorage<UsageState>(() => localStorage, {
  reviver: (key, value) => {
    if (key === "totalSpent" && typeof value === "string") {
      return BigInt(value);
    }
    return value;
  },
  replacer: (key, value) => {
    if (key === "totalSpent" && typeof value === "bigint") {
      return value.toString();
    }
    return value;
  },
});

export const useUsageStore = create<UsageState>()(
  persist(
    (set, get) => ({
      walletAddress: null,
      dailyUsage: {},
      usageDate: getUtcDateString(),
      payments: [],
      totalSpent: BigInt(0),

      setWallet: (address) => {
        set({ walletAddress: address });
        // Reset usage when wallet changes
        if (address !== get().walletAddress) {
          get().resetIfNewDay();
        }
      },

      incrementUsage: (featureId) => {
        get().resetIfNewDay();
        set((state) => ({
          dailyUsage: {
            ...state.dailyUsage,
            [featureId]: (state.dailyUsage[featureId] || 0) + 1,
          },
        }));
      },

      recordPayment: (payment) => {
        const record: PaymentRecord = {
          ...payment,
          timestamp: Date.now(),
        };
        set((state) => ({
          payments: [...state.payments, record],
          totalSpent: state.totalSpent + BigInt(payment.amount),
        }));
        // Also increment usage
        get().incrementUsage(payment.featureId);
      },

      getUsageCount: (featureId) => {
        get().resetIfNewDay();
        return get().dailyUsage[featureId] || 0;
      },

      getRemainingFree: (featureId) => {
        const limits = getFreeTierLimits();
        const limit = limits[featureId] || 0;
        const used = get().getUsageCount(featureId);
        return Math.max(0, limit - used);
      },

      needsPayment: (featureId) => {
        return get().getRemainingFree(featureId) <= 0;
      },

      resetIfNewDay: () => {
        const today = getUtcDateString();
        if (get().usageDate !== today) {
          set({
            dailyUsage: {},
            usageDate: today,
          });
        }
      },

      clearUsage: () => {
        set({
          dailyUsage: {},
          usageDate: getUtcDateString(),
        });
      },
    }),
    {
      name: "crypteolas-usage",
      storage,
      partialize: (state) => ({
        walletAddress: state.walletAddress,
        dailyUsage: state.dailyUsage,
        usageDate: state.usageDate,
        payments: state.payments,
        totalSpent: state.totalSpent,
      }),
    }
  )
);

// Selector hooks for convenience
export const useWalletAddress = () => useUsageStore((s) => s.walletAddress);
export const useDailyUsage = () => useUsageStore((s) => s.dailyUsage);
export const usePayments = () => useUsageStore((s) => s.payments);
export const useTotalSpent = () => useUsageStore((s) => s.totalSpent);
