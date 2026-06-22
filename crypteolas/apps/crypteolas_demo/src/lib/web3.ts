// TODO: implement the shared Web3 helpers (Wagmi config, ENS resolution,
// chain helpers, wallet-connect modal wrappers).

import type { Config } from "wagmi";
import { mainnet, base, cronos, polygon } from "wagmi/chains";

export const wagmiConfig: Config = {
  chains: [mainnet, base, cronos, polygon],
  connectors: [],
  transports: {
    [mainnet.id]: undefined,
    [base.id]: undefined,
    [cronos.id]: undefined,
    [polygon.id]: undefined,
  },
} as unknown as Config;

export async function resolveEnsName(address: string): Promise<string | null> {
  return null;
}

export async function resolveEnsAvatar(address: string): Promise<string | null> {
  return null;
}
