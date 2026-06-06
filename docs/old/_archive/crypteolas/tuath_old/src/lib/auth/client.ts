/**
 * Better Auth Client Configuration with SIWE
 *
 * Client-side auth utilities for Sign In With Ethereum
 */

import { createAuthClient } from "better-auth/client";
import { siweClient } from "better-auth/client/plugins";

// Create the auth client with SIWE plugin
export const authClient = createAuthClient({
  baseURL: typeof window !== "undefined" ? window.location.origin : "",
  plugins: [siweClient()],
});

// Export individual methods for convenience
export const {
  signIn,
  signOut,
  useSession,
  siwe: siweAuth,
} = authClient;

// Type exports
export type Session = typeof authClient.$Infer.Session;
export type User = typeof authClient.$Infer.User;
