import { betterAuth } from "better-auth";
import { postgres } from "better-auth/db/postgres";
import { oidc } from "better-auth/oauth";

export const auth = betterAuth({
  database: postgres({
    url: process.env.DATABASE_URL!,
  }),
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },
  socialProviders: {
    // Configure PocketID as a custom OIDC provider
    // PocketID is a passkey-first OIDC provider running at auth.cianfhoghlaim.ie
    oidc({
      providerId: "pocketid",
      clientId: process.env.POCKETID_CLIENT_ID!,
      clientSecret: process.env.POCKETID_CLIENT_SECRET!,
      issuer: process.env.POCKETID_ISSUER || "https://auth.cianfhoghlaim.ie",
      redirectURI: `${process.env.AUTH_BASE_URL}/api/auth/callback/oidc`,
      scope: "openid email profile groups",
    }),
  },
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // 5 minutes
    },
  },
  advanced: {
    cookiePrefix: "cianfhoghlaim",
    crossSubDomainCookies: {
      enabled: false,
    },
  },
});

// Export session fetching helper for server-side
export const getSession = async (headers: Headers) => {
  return auth.api.getSession({
    headers,
  });
};
