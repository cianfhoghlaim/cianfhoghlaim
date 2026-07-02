// apps/web/src/lib/auth-client.ts — BetterAuth client for the Cianfhoghlaim OS.
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T2.5.

import { createAuthClient } from "better-auth/react";

const AUTH_URL = import.meta.env?.VITE_AUTH_URL ?? "http://localhost:8787/api/auth";

export const authClient = createAuthClient({
  baseURL: AUTH_URL,
  plugins: [
    // Optional SIWE plugin (gated on VITE_SIWE_ENABLED=true)
    ...(import.meta.env?.VITE_SIWE_ENABLED === "true"
      ? [require("better-auth/plugins/siwe/react")]
      : []),
  ],
});

export const {
  useSession,
  signIn,
  signOut,
  signUp,
} = authClient;