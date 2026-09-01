// apps/web/src/lib/orpc.ts — typed client for the @cianfhoghlaim/api router.
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T4.9.

import { createORPCClient } from "@orpc/client";
import { RPCLink } from "@orpc/client/fetch";
import type { AppRouter } from "@cianfhoghlaim/api-client";

// The RPC endpoint (Hono mounted at /rpc/*)
const RPC_URL = import.meta.env?.VITE_RPC_URL ?? "/rpc";

export const orpcLink = new RPCLink({
  url: `${RPC_URL}`,
  headers: () => ({
    "x-cianfhoghlaim-build": import.meta.env?.VITE_CIANFHLOGHLAIM_BUILD ?? "development",
  }),
});

export const client = createORPCClient<AppRouter>(orpcLink);

// Re-export the typed client
export type ORPCClient = typeof client;