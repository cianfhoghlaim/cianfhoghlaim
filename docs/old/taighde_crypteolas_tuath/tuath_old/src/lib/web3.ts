import { createConfig, http } from "wagmi";
import { mainnet, polygon, arbitrum, base, baseSepolia } from "wagmi/chains";
import type { Chain } from "wagmi/chains";

// Cronos chain definitions (not in wagmi by default)
export const cronos: Chain = {
  id: 25,
  name: "Cronos",
  nativeCurrency: {
    decimals: 18,
    name: "CRO",
    symbol: "CRO",
  },
  rpcUrls: {
    default: { http: ["https://evm.cronos.org/"] },
  },
  blockExplorers: {
    default: {
      name: "Cronos Explorer",
      url: "https://explorer.cronos.org",
    },
  },
};

export const cronosTestnet: Chain = {
  id: 338,
  name: "Cronos Testnet",
  nativeCurrency: {
    decimals: 18,
    name: "Test CRO",
    symbol: "TCRO",
  },
  rpcUrls: {
    default: { http: ["https://evm-t3.cronos.org/"] },
  },
  blockExplorers: {
    default: {
      name: "Cronos Explorer",
      url: "https://explorer.cronos.org/testnet",
    },
  },
  testnet: true,
};

// Wagmi configuration for multi-chain support
// Including Cronos for hackathon + Base Sepolia for x402 testing
export const wagmiConfig = createConfig({
  chains: [mainnet, polygon, arbitrum, base, baseSepolia, cronos, cronosTestnet],
  transports: {
    [mainnet.id]: http(),
    [polygon.id]: http(),
    [arbitrum.id]: http(),
    [base.id]: http(),
    [baseSepolia.id]: http(),
    [cronos.id]: http(),
    [cronosTestnet.id]: http(),
  },
});

// Chain metadata for UI
export const chainMetadata: Record<number, { name: string; icon: string; color: string }> = {
  [mainnet.id]: {
    name: "Ethereum",
    icon: "eth",
    color: "#627eea",
  },
  [polygon.id]: {
    name: "Polygon",
    icon: "matic",
    color: "#8247e5",
  },
  [arbitrum.id]: {
    name: "Arbitrum",
    icon: "arb",
    color: "#28a0f0",
  },
  [base.id]: {
    name: "Base",
    icon: "base",
    color: "#0052ff",
  },
  [baseSepolia.id]: {
    name: "Base Sepolia",
    icon: "base",
    color: "#0052ff",
  },
  [cronos.id]: {
    name: "Cronos",
    icon: "cro",
    color: "#002D74",
  },
  [cronosTestnet.id]: {
    name: "Cronos Testnet",
    icon: "cro",
    color: "#002D74",
  },
};

// Common token addresses
export const tokens = {
  USDe: {
    [mainnet.id]: "0x4c9EDD5852cd905f086C759E8383e09bff1E68B3",
  },
  sUSDe: {
    [mainnet.id]: "0x9D39A5DE30e57443BfF2A8307A4256c8797A3497",
  },
  USDC: {
    [mainnet.id]: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    [polygon.id]: "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
    [arbitrum.id]: "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
    [base.id]: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    [baseSepolia.id]: "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
    [cronos.id]: "0xc21223249CA28397B4B6541dfFaEcC539BfF0c59",
    [cronosTestnet.id]: "0x87EFB3ec1576Dec8ED47e58B832bEdCd86eE186e", // Test USDC
  },
  WETH: {
    [mainnet.id]: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    [polygon.id]: "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
    [arbitrum.id]: "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
  },
  WCRO: {
    [cronos.id]: "0x5C7F8A570d578ED84E63fdFA7b1eE72dEae1AE23",
    [cronosTestnet.id]: "0x6a3173618859C7cd40fAF6921b5E9eB6A76f1fD4",
  },
};
