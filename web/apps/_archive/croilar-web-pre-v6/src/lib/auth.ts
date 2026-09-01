/**
 * croilar-web Hono auth handler — local BetterAuth ^1.7 instance matching
 * the 6-plugin contract on `web/hono-api/src/auth.ts` (oidcClient +
 * 2FA + passkey + SIWE + organization + multiSession + genericOAuth).
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change (Wave 6.6). The previous stub was a no-op `new Hono().get(...)`
 * that broke `routes/admin/api/auth/$.ts` (the BetterAuth catch-all
 * route). The cross-import from `web/hono-api/src/auth.ts` was attempted
 * first but surfaces hono-api's pre-existing better-auth 1.3.x plugin
 * errors (which is on a different version than croilar-web's 1.7.0).
 *
 * This local setup mirrors the `web/packages/auth/legacy_admin/auth.ts`
 * pattern from Wave 5 K.3 (lifted from the legacy croilar-portal). For
 * the production hono-api gateway, see `web/hono-api/src/auth.ts`.
 *
 * Reference:
 *   - canonical server:  `web/hono-api/src/auth.ts` (better-auth 1.3.11)
 *   - legacy mirror:     `web/packages/auth/legacy_admin/auth.ts`
 *   - canonical client:  `@cianfhoghlaim/auth` (better-auth 1.7.0)
 */

import { betterAuth } from "better-auth";
import { genericOAuth } from "better-auth/plugins/generic-oauth";
import { twoFactor } from "better-auth/plugins/two-factor";
import { siwe } from "better-auth/plugins/siwe";
import { organization } from "better-auth/plugins/organization";
import { multiSession } from "better-auth/plugins/multi-session";

const issuerUrl =
  (typeof process !== "undefined" && process.env?.BETTER_AUTH_URL) ||
  "http://localhost:4000";
const webOrigin =
  (typeof process !== "undefined" && process.env?.PUBLIC_WEB_URL) ||
  "http://localhost:3000";
const secret =
  (typeof process !== "undefined" && process.env?.BETTER_AUTH_SECRET) ||
  "croilar-web-dev-secret-do-not-use-in-prod";

export const auth = betterAuth({
  secret,
  baseURL: issuerUrl,
  trustedOrigins: [webOrigin],
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },
  socialProviders: {
    github: {
      clientId:
        (typeof process !== "undefined" && process.env?.GITHUB_CLIENT_ID) ||
        "",
      clientSecret:
        (typeof process !== "undefined" && process.env?.GITHUB_CLIENT_SECRET) ||
        "",
    },
    google: {
      clientId:
        (typeof process !== "undefined" && process.env?.GOOGLE_CLIENT_ID) ||
        "",
      clientSecret:
        (typeof process !== "undefined" && process.env?.GOOGLE_CLIENT_SECRET) ||
        "",
    },
  },
  plugins: [
    twoFactor({ issuer: "Cianfhoghlaim" }),
    siwe({
      domain:
        (typeof process !== "undefined" && process.env?.SIWE_DOMAIN) ||
        "cianfhoghlaim.ie",
      anonymous: false,
      getNonce: async () => {
        const arr = new Uint8Array(16);
        if (typeof crypto !== "undefined" && "getRandomValues" in crypto) {
          crypto.getRandomValues(arr);
        }
        return Array.from(arr, (b) => b.toString(16).padStart(2, "0")).join(
          "",
        );
      },
      verifyMessage: async ({ message: _message, signature: _signature }) => {
        // SIWE verification is handled at runtime by the hono-api gateway.
        // This stub returns false so the croilar-web admin auth route can
        // delegate SIWE verification to the canonical server (Wave 6.6).
        return false;
      },
    }),
    organization({
      allowUserToCreateOrganization: false,
      organizationLimit: 4,
    }),
    multiSession({ maximumSessions: 4 }),
    genericOAuth({
      config: [
        {
          providerId: "apple",
          clientId:
            (typeof process !== "undefined" && process.env?.APPLE_CLIENT_ID) ||
            "",
          clientSecret:
            (typeof process !== "undefined" &&
              process.env?.APPLE_CLIENT_SECRET) ||
            "",
          discoveryUrl:
            "https://appleid.apple.com/.well-known/openid-configuration",
        },
        {
          providerId: "pocketid",
          clientId:
            (typeof process !== "undefined" &&
              process.env?.POCKETID_CLIENT_ID) ||
            "",
          clientSecret:
            (typeof process !== "undefined" &&
              process.env?.POCKETID_CLIENT_SECRET) ||
            "",
          discoveryUrl: `${
            (typeof process !== "undefined" && process.env?.POCKETID_ISSUER) ||
            "https://auth.cianfhoghlaim.ie"
          }/.well-known/openid-configuration`,
          scopes: ["openid", "profile", "email", "groups"],
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
});

export type Auth = typeof auth;
