import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { organization } from "better-auth/plugins";
import { db } from "./db/client";

const secret = process.env.BETTER_AUTH_SECRET;
if (!secret) {
  throw new Error("BETTER_AUTH_SECRET is required");
}

const issuerUrl = process.env.BETTER_AUTH_URL ?? "http://localhost:4000";
const webOrigin = process.env.PUBLIC_WEB_URL ?? "http://localhost:3000";

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
    organization({
      // The 4 orgs: aleyum, cianfhoghlaim, croilar-admin, croilar-collab
      // Created on first login via /api/auth/organization/create
      allowUserToCreateOrganization: false,
      organizationLimit: 4,
    }),
  ],
  advanced: {
    // CORS for the web app — Convex and the web app both need access
    crossSubDomainCookies: { enabled: true },
    defaultCookieAttributes: {
      sameSite: "lax",
      secure: issuerUrl.startsWith("https://"),
      httpOnly: true,
    },
  },
  // OIDC client for Convex: convex.croilar.cianfhoghlaim.ie
  // applicationID becomes the `aud` claim on JWTs
  oauth: {
    // Apps that can consume BetterAuth JWTs (audience)
    // Convex registers as one of these clients
    clientMetadata: {
      convex: { applicationID: "convex_backend", name: "Croilar Convex" },
      web: { applicationID: "croilar_web", name: "Croilar Web" },
    },
  },
});

export type Auth = typeof auth;
