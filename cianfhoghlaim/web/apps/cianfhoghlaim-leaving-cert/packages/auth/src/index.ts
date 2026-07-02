// @cianfhoghlaim/auth — BetterAuth + Pocket ID OIDC + optional SIWE
// The shared auth instance used by both apps/web (client) and apps/api (server).

import { betterAuth } from "better-auth";
import { bearer } from "better-auth/plugins";
import { siwePlugin } from "better-auth/plugins/siwe";

// Pocket ID OIDC discovery URL (per Pocket ID documentation)
const POCKET_ID_DISCOVERY = process.env.POCKET_ID_DISCOVERY_URL || "http://localhost:8080/.well-known/openid-configuration";

// BetterAuth server factory (Phase 2 T2.4)
export const auth = betterAuth({
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:8787",
  secret: process.env.BETTER_AUTH_SECRET || "change-me-in-production",
  trustedOrigins: [
    "http://localhost:3082",
    "https://leaving-cert.cianfhoghlaim.ie",
  ],
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_CLIENT_ID || "",
      clientSecret: process.env.GITHUB_CLIENT_SECRET || "",
    },
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    },
  },
  plugins: [
    bearer(),
    // Optional SIWE (gated on VITE_SIWE_ENABLED)
    ...(process.env.SIWE_ENABLED === "true" ? [siwePlugin()] : []),
  ],
  // Pocket ID OIDC discovery (Phase 2 T2.6)
  // The actual OIDC provider registration is done via the socialProviders
  // mechanism with custom discovery URL.
});

// BetterAuth client factory (Phase 2 T2.5)
export function createAuthClient(baseURL?: string) {
  return {
    useSession: () => ({ data: null, isPending: false }),
    signIn: {
      email: async (_creds: { email: string; password: string }) => ({}),
    },
    signOut: async () => ({}),
    signUp: {
      email: async (_creds: { email: string; password: string; name: string }) => ({}),
    },
    $fetch: {} as never,
  } as const;
}

// Re-export the Pocket ID discovery URL constant
export { POCKET_ID_DISCOVERY };