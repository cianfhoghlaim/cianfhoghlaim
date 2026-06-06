/**
 * x402 Network Configuration
 *
 * Defines supported networks for x402 payments, with Cronos EVM as primary
 * for the hackathon, plus Base Sepolia as fallback (well-tested facilitator).
 */

import type { Address } from "viem";

export interface NetworkConfig {
  chainId: number;
  name: string;
  displayName: string;
  rpcUrl: string;
  explorerUrl: string;
  isTestnet: boolean;
  // x402 specific
  x402Network: string; // CAIP-2 format for x402 v2
  usdc: Address;
  facilitatorUrl: string;
}

// Cronos Testnet - Primary for hackathon
export const CRONOS_TESTNET: NetworkConfig = {
  chainId: 338,
  name: "cronos-testnet",
  displayName: "Cronos Testnet",
  rpcUrl: "https://evm-t3.cronos.org/",
  explorerUrl: "https://explorer.cronos.org/testnet/",
  isTestnet: true,
  x402Network: "eip155:338",
  // Note: USDC on Cronos testnet - update with actual address
  usdc: "0x87EFB3ec1576Dec8ED47e58B832bEdCd86eE186e" as Address,
  facilitatorUrl: "https://x402.org/facilitator", // May need custom facilitator for Cronos
};

// Cronos Mainnet
export const CRONOS_MAINNET: NetworkConfig = {
  chainId: 25,
  name: "cronos",
  displayName: "Cronos",
  rpcUrl: "https://evm.cronos.org/",
  explorerUrl: "https://explorer.cronos.org/",
  isTestnet: false,
  x402Network: "eip155:25",
  usdc: "0xc21223249CA28397B4B6541dfFaEcC539BfF0c59" as Address, // USDC on Cronos mainnet
  facilitatorUrl: "https://x402.org/facilitator",
};

// Base Sepolia - Fallback (well-tested x402 support)
export const BASE_SEPOLIA: NetworkConfig = {
  chainId: 84532,
  name: "base-sepolia",
  displayName: "Base Sepolia",
  rpcUrl: "https://sepolia.base.org",
  explorerUrl: "https://sepolia.basescan.org/",
  isTestnet: true,
  x402Network: "eip155:84532",
  usdc: "0x036CbD53842c5426634e7929541eC2318f3dCF7e" as Address,
  facilitatorUrl: "https://x402.org/facilitator",
};

// Base Mainnet
export const BASE_MAINNET: NetworkConfig = {
  chainId: 8453,
  name: "base",
  displayName: "Base",
  rpcUrl: "https://mainnet.base.org",
  explorerUrl: "https://basescan.org/",
  isTestnet: false,
  x402Network: "eip155:8453",
  usdc: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913" as Address,
  facilitatorUrl: "https://x402.org/facilitator",
};

// Network registry
export const NETWORKS: Record<string, NetworkConfig> = {
  "cronos-testnet": CRONOS_TESTNET,
  "cronos": CRONOS_MAINNET,
  "base-sepolia": BASE_SEPOLIA,
  "base": BASE_MAINNET,
};

// Get network by chain ID
export function getNetworkByChainId(chainId: number): NetworkConfig | undefined {
  return Object.values(NETWORKS).find((n) => n.chainId === chainId);
}

// Get network by x402 network string
export function getNetworkByX402(x402Network: string): NetworkConfig | undefined {
  return Object.values(NETWORKS).find((n) => n.x402Network === x402Network);
}

// Default network for the hackathon
export const DEFAULT_NETWORK = CRONOS_TESTNET;

// Supported testnet networks
export const TESTNET_NETWORKS = Object.values(NETWORKS).filter((n) => n.isTestnet);

// Supported mainnet networks
export const MAINNET_NETWORKS = Object.values(NETWORKS).filter((n) => !n.isTestnet);

// Viem chain definitions for Cronos (not in viem by default)
export const cronosTestnet = {
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
} as const;

export const cronos = {
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
  testnet: false,
} as const;
