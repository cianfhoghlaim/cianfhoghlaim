import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { genericOAuth } from "better-auth/plugins/generic-oauth";
import { twoFactor } from "better-auth/plugins/two-factor";
import { passkey } from "better-auth/plugins/passkey";
import { siwe } from "better-auth/plugins/siwe";
import { oidcClient } from "better-auth/plugins/oidc-client";
import { organization } from "better-auth/plugins/organization";
import { multiSession } from "better-auth/plugins/multi-session";
import { db } from "./db/client";

const secret = process.env.BETTER_AUTH_SECRET;
if (!secret) {
  throw new Error("BETTER_AUTH_SECRET is required");
}

const issuerUrl = process.env.BETTER_AUTH_URL ?? "http://localhost:4000";
const webOrigin = process.env.PUBLIC_WEB_URL ?? "http://localhost:3000";

/**
 * BetterAuth ^1.7 server-side config — used by the Hono API gateway.
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change (Wave 6.6). Plugin set:
 *   - oidcClient               — OAuth client against the Pocket ID OIDC provider
 *   - twoFactor                — TOTP 2FA (apps).
 *   - passkey                  — WebAuthn passkeys (Passwordless).
 *   - siwe                     — Sign-In With Ethereum (crypteolas + tuatha).
 *   - organization             — the 4 orgs (aleyum, cianfhoghlaim, croilar-admin,
 *                                croilar-collab).
 *   - multiSession             — per-org session isolation.
 *   - genericOAuth             — SIWE + OIDC adapters.
 *
 * Reference:
 *   - skill:                  .agents/skills/better-auth/SKILL.md
 *   - canonical BetterAuth:    web/packages/auth/src/index.ts
 *   - BetterAuth ^1.7 release: https://www.better-auth.com/
 */
export const auth = betterAuth({
  database: drizzleAdapter(db, { provider: "pg" }),
  secret,
  baseURL: issuerUrl,
  trustedOrigins: [webOrigin],
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_CLIENT_ID ?? "",
      clientSecret: process.env.GITHUB_CLIENT_SECRET ?? "",
    },
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID ?? "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET ?? "",
    },
  },
  plugins: [
    oidcClient({
      // The client id registered with the Pocket ID OIDC provider
      clientId: process.env.POCKETID_CLIENT_ID ?? "cianfhoghlaim-web",
    }),
    twoFactor({
      issuer: "Cianfhoghlaim",
    }),
    passkey({
      rpName: "Cianfhoghlaim",
      rpID: process.env.PASSKEY_RP_ID ?? "cianfhoghlaim.ie",
      origin: issuerUrl,
    }),
    siwe({
      // Crypteolas + Tuatha use SIWE; the SiweMessage nonce + verify
      // are handled by the plugin via the canonical wallet interface.
      anonymous: false,
    }),
    organization({
      allowUserToCreateOrganization: false,
      organizationLimit: 4,
    }),
    multiSession({
      // The 4 orgs above live in separate sessions
      maximumSessions: 4,
    }),
    genericOAuth({
      // Generic OAuth client for additional providers (Apple, Microsoft).
      config: [
        {
          providerId: "apple",
          clientId: process.env.APPLE_CLIENT_ID ?? "",
          clientSecret: process.env.APPLE_CLIENT_SECRET ?? "",
          discoveryUrl: "https://appleid.apple.com/.well-known/openid-configuration",
        },
      ],
    }),
  ],
  advanced: {
    crossSubDomainCookies: { enabled: true },
    defaultCookieAttributes: {
      sameSite: "lax",
      secure: issuerUrl.startsWith("https://"),
      httpOnly: true,
    },
  },
  oauth: {
    clientMetadata: {
      convex: { applicationID: "convex_backend", name: "Croilar Convex" },
      web: { applicationID: "croilar_web", name: "Croilar Web" },
    },
  },
});

export type Auth = typeof auth;
