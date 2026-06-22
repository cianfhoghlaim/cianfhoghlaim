// TODO: implement the x402 payment provider (React context + Wagmi hook).

import { createContext, useContext } from "react";
import type { NetworkConfig } from "./networks";

export interface X402ContextValue {
  network: NetworkConfig;
  setNetwork: (id: NetworkConfig["id"]) => void;
  isConnected: boolean;
  walletAddress: string | null;
}

export const X402Context = createContext<X402ContextValue | null>(null);

export function useX402(): X402ContextValue {
  const ctx = useContext(X402Context);
  if (!ctx) {
    throw new Error("useX402 must be used inside an <X402Provider>");
  }
  return ctx;
}
