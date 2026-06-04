import { create } from "zustand";
import { persist } from "zustand/middleware";

interface Asset {
  symbol: string;
  name: string;
  balance: number;
  price: number;
  chain: string;
  contractAddress?: string;
}

interface PortfolioState {
  assets: Asset[];
  totalValue: number;
  selectedAsset: string | null;

  // Actions
  setAssets: (assets: Asset[]) => void;
  addAsset: (asset: Asset) => void;
  removeAsset: (symbol: string) => void;
  selectAsset: (symbol: string | null) => void;
  refreshPrices: () => Promise<void>;
}

export const usePortfolioStore = create<PortfolioState>()(
  persist(
    (set, get) => ({
      assets: [
        // Mock initial data
        { symbol: "ETH", name: "Ethereum", balance: 10, price: 3450, chain: "ethereum" },
        { symbol: "USDe", name: "Ethena USDe", balance: 25000, price: 0.9998, chain: "ethereum" },
        { symbol: "sUSDe", name: "Staked USDe", balance: 15000, price: 1.02, chain: "ethereum" },
        { symbol: "USDC", name: "USD Coin", balance: 10000, price: 1.0, chain: "ethereum" },
      ],
      totalValue: 0,
      selectedAsset: null,

      setAssets: (assets) => {
        const totalValue = assets.reduce(
          (sum, a) => sum + a.balance * a.price,
          0
        );
        set({ assets, totalValue });
      },

      addAsset: (asset) => {
        set((state) => {
          const assets = [...state.assets, asset];
          const totalValue = assets.reduce(
            (sum, a) => sum + a.balance * a.price,
            0
          );
          return { assets, totalValue };
        });
      },

      removeAsset: (symbol) => {
        set((state) => {
          const assets = state.assets.filter((a) => a.symbol !== symbol);
          const totalValue = assets.reduce(
            (sum, a) => sum + a.balance * a.price,
            0
          );
          return { assets, totalValue };
        });
      },

      selectAsset: (symbol) => set({ selectedAsset: symbol }),

      refreshPrices: async () => {
        // In production, fetch from CoinGecko or other price API
        const { assets } = get();

        // Mock price update
        const updatedAssets = assets.map((a) => ({
          ...a,
          price: a.price * (1 + (Math.random() - 0.5) * 0.02),
        }));

        const totalValue = updatedAssets.reduce(
          (sum, a) => sum + a.balance * a.price,
          0
        );

        set({ assets: updatedAssets, totalValue });
      },
    }),
    { name: "portfolio-storage" }
  )
);
