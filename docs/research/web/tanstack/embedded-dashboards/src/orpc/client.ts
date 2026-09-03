import { createORPCClient } from "@orpc/client";
import { RPCLink } from "@orpc/client/fetch";
import { createTanstackQueryUtils } from "@orpc/tanstack-query";
import type { Router } from "./router";

// Create the oRPC client for browser usage
const link = new RPCLink({
  url: typeof window !== "undefined"
    ? `${window.location.origin}/api/rpc`
    : "http://localhost:3000/api/rpc",
});

const client = createORPCClient<Router>(link);

// Create TanStack Query utilities for data fetching
export const orpc = createTanstackQueryUtils(client);

export { client };
