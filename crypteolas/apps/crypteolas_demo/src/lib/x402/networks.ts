// TODO: implement multi-chain network configuration for the x402 payment
// gateway. Each entry describes a supported chain: its chain id, RPC URL,
// USDC contract address, and the facilitator URL.

export interface NetworkConfig {
  id: "cronos" | "base" | "ethereum" | "polygon";
  chainId: number;
  rpcUrl: string;
  usdcAddress: string;
  facilitatorUrl: string;
}

export const NETWORKS: Record<NetworkConfig["id"], NetworkConfig> = {
  cronos: {
    id: "cronos",
    chainId: 25,
    rpcUrl: "https://evm.cronos.org",
    usdcAddress: "0xc21223249CA28397B5925741f873A99B4B6D5A93",
    facilitatorUrl: "https://x402.org/facilitator",
  },
  base: {
    id: "base",
    chainId: 8453,
    rpcUrl: "https://mainnet.base.org",
    usdcAddress: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    facilitatorUrl: "https://x402.org/facilitator",
  },
  ethereum: {
    id: "ethereum",
    chainId: 1,
    rpcUrl: "https://eth.llamarpc.com",
    usdcAddress: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    facilitatorUrl: "https://x402.org/facilitator",
  },
  polygon: {
    id: "polygon",
    chainId: 137,
    rpcUrl: "https://polygon-rpc.com",
    usdcAddress: "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
    facilitatorUrl: "https://x402.org/facilitator",
  },
};

export const DEFAULT_PAYMENT_NETWORK: NetworkConfig["id"] = "cronos";
